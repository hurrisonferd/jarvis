use axum::{http::{header::{ACCESS_CONTROL_ALLOW_ORIGIN, CACHE_CONTROL}, HeaderMap, HeaderValue}, routing::get, Json, Router};
use serde::Serialize;
use serde_json::{json, Value};
use std::{net::SocketAddr, sync::{Arc, RwLock}, thread, time::{Duration, SystemTime, UNIX_EPOCH}};

const SENSE_PORT: u16 = 47_823;

#[derive(Clone, Debug, Default, Serialize)]
struct FocusRect { left: i32, top: i32, right: i32, bottom: i32 }

#[derive(Clone, Debug, Default, Serialize)]
struct FocusedElement { name: String, control_type: String, rect: FocusRect }

#[derive(Clone, Debug, Serialize)]
struct SenseSnapshot {
    schema: &'static str,
    supported: bool,
    observed_ms: u128,
    focused: Option<FocusedElement>,
    audio_peak: f32,
    uia_available: bool,
    audio_meter_available: bool,
    read_only: bool,
    screen_capture: bool,
    keylogging: bool,
    effect_authority: bool,
}

impl Default for SenseSnapshot {
    fn default() -> Self {
        Self { schema: "faeryware.desktop.sense-hub.v1", supported: cfg!(windows), observed_ms: now_ms(), focused: None, audio_peak: 0.0, uia_available: false, audio_meter_available: false, read_only: true, screen_capture: false, keylogging: false, effect_authority: false }
    }
}

type Shared = Arc<RwLock<SenseSnapshot>>;

fn now_ms() -> u128 { SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_millis() }

async fn sense(axum::extract::State(state): axum::extract::State<Shared>) -> (HeaderMap, Json<Value>) {
    let snapshot = state.read().map(|value| value.clone()).unwrap_or_default();
    let mut headers = HeaderMap::new();
    headers.insert(ACCESS_CONTROL_ALLOW_ORIGIN, HeaderValue::from_static("*"));
    headers.insert(CACHE_CONTROL, HeaderValue::from_static("no-store"));
    (headers, Json(json!(snapshot)))
}

#[cfg(windows)]
fn sensor_loop(shared: Shared) {
    use uiautomation::UIAutomation;
    use wasapi::{DeviceEnumerator, Direction};

    let _ = wasapi::initialize_mta().ok();
    let automation = UIAutomation::new_direct().ok();
    let meter = DeviceEnumerator::new().ok().and_then(|enumerator| enumerator.get_default_device(&Direction::Render).ok()).and_then(|device| device.get_audiometerinformation().ok());

    loop {
        let focused = automation.as_ref().and_then(|automation| {
            let element = automation.get_focused_element().ok()?;
            let rect = element.get_bounding_rectangle().ok()?;
            Some(FocusedElement {
                name: element.get_name().unwrap_or_default().chars().take(120).collect(),
                control_type: element.get_localized_control_type().unwrap_or_else(|_| "unknown".into()).chars().take(80).collect(),
                rect: FocusRect { left: rect.get_left(), top: rect.get_top(), right: rect.get_right(), bottom: rect.get_bottom() },
            })
        });
        let audio_peak = meter.as_ref().and_then(|meter| meter.get_peak_value().ok()).unwrap_or(0.0).clamp(0.0, 1.0);
        if let Ok(mut state) = shared.write() {
            state.supported = true;
            state.observed_ms = now_ms();
            state.focused = focused;
            state.audio_peak = audio_peak;
            state.uia_available = automation.is_some();
            state.audio_meter_available = meter.is_some();
        }
        thread::sleep(Duration::from_millis(80));
    }
}

#[cfg(not(windows))]
fn sensor_loop(shared: Shared) {
    if let Ok(mut state) = shared.write() { state.supported = false; state.observed_ms = now_ms(); }
}

pub fn spawn() {
    let shared = Arc::new(RwLock::new(SenseSnapshot::default()));
    let sensor_state = shared.clone();
    thread::Builder::new().name("faeryware-sense-worker".into()).spawn(move || sensor_loop(sensor_state)).ok();
    thread::Builder::new().name("faeryware-sense-http".into()).spawn(move || {
        let runtime = match tokio::runtime::Builder::new_current_thread().enable_all().build() {
            Ok(runtime) => runtime,
            Err(error) => { eprintln!("Faeryware sense runtime failed: {error}"); return; }
        };
        runtime.block_on(async move {
            let router = Router::new().route("/sense", get(sense)).with_state(shared);
            let addr = SocketAddr::from(([127, 0, 0, 1], SENSE_PORT));
            match tokio::net::TcpListener::bind(addr).await {
                Ok(listener) => { if let Err(error) = axum::serve(listener, router).await { eprintln!("Faeryware sense hub stopped: {error}"); } }
                Err(error) => eprintln!("Faeryware sense hub bind failed on {addr}: {error}"),
            }
        });
    }).ok();
}
