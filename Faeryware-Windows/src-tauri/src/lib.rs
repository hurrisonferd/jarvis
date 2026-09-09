use axum::{
    extract::State,
    http::{
        header::{
            ACCESS_CONTROL_ALLOW_HEADERS, ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN,
            CACHE_CONTROL, ORIGIN, VARY,
        },
        HeaderMap, HeaderValue, StatusCode,
    },
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{env, net::SocketAddr, sync::Arc, time::Duration};
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Emitter, Manager,
};
use tauri_plugin_autostart::MacosLauncher;
use tauri_plugin_deep_link::DeepLinkExt;
use tauri_plugin_global_shortcut::{
    Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState,
};
use tokio::sync::RwLock;

const MEMBERS: [&str; 6] = ["KYU", "PAIMON", "LUMA", "SYLPH", "QIRA", "NYX"];
const STATE_PORT: u16 = 47_821;
const CARRIER_PORT: u16 = 47_822;
const OPENAI_RESPONSES_URL: &str = "https://api.openai.com/v1/responses";
const ALLOWED_CARRIER_ORIGINS: [&str; 5] = [
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
    "http://localhost:1420",
    "http://127.0.0.1:1420",
];

#[derive(Clone)]
struct HauntState {
    app: AppHandle,
    current: Arc<RwLock<HauntEvent>>,
}

#[derive(Clone)]
struct CarrierState {
    client: Client,
}

fn tray_icon() -> tauri::image::Image<'static> {
    const SIZE: u32 = 32;
    let mut rgba = Vec::with_capacity((SIZE * SIZE * 4) as usize);
    for y in 0..SIZE {
        for x in 0..SIZE {
            let dx = x as i32 - 16;
            let dy = y as i32 - 16;
            let radius2 = dx * dx + dy * dy;
            let (r, g, b, a) = if radius2 <= 14 * 14 {
                if (x + y) % 7 < 3 {
                    (255, 79, 186, 255)
                } else {
                    (168, 85, 247, 255)
                }
            } else {
                (0, 0, 0, 0)
            };
            rgba.extend_from_slice(&[r, g, b, a]);
        }
    }
    tauri::image::Image::new_owned(rgba, SIZE, SIZE)
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct HauntEvent {
    schema: String,
    fae: String,
    intent: String,
    surface: String,
    state: String,
    authority: String,
    #[serde(default)]
    message: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CarrierRequest {
    schema: String,
    fae: String,
    autonomy: u8,
    message: String,
    #[serde(default)]
    sense: Value,
    #[serde(default)]
    history: Value,
}

fn default_event() -> HauntEvent {
    HauntEvent {
        schema: "fairyos.haunt-event.v1".into(),
        fae: "KYU".into(),
        intent: "RESIDENT".into(),
        surface: "WINDOWS_DESKTOP".into(),
        state: "DORMANT_GLOW".into(),
        authority: "RAVEN".into(),
        message: Some("Faeryware resident body awake.".into()),
    }
}

fn show_main(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.unminimize();
        let _ = window.show();
        let _ = window.set_focus();
    }
}

fn local_event(fae: &str, state: &str, message: &str) -> HauntEvent {
    HauntEvent {
        schema: "fairyos.haunt-event.v1".into(),
        fae: fae.into(),
        intent: "LOCAL_SUMMON".into(),
        surface: "WINDOWS_DESKTOP".into(),
        state: state.into(),
        authority: "RAVEN".into(),
        message: Some(message.into()),
    }
}

async fn set_current(state: &HauntState, event: &HauntEvent) {
    *state.current.write().await = event.clone();
}

fn env_trim(name: &str) -> String {
    env::var(name).unwrap_or_default().trim().to_string()
}

fn ollama_url() -> String {
    let configured = env_trim("FAERYWARE_OLLAMA_URL");
    if configured.is_empty() {
        "http://127.0.0.1:11434/api/chat".to_string()
    } else {
        configured
    }
}

fn is_loopback_http(url: &str) -> bool {
    match reqwest::Url::parse(url) {
        Ok(parsed) => {
            parsed.scheme() == "http"
                && matches!(parsed.host_str(), Some("127.0.0.1" | "localhost" | "::1"))
        }
        Err(_) => false,
    }
}

fn configured_carrier() -> String {
    let requested = env_trim("FAERYWARE_CARRIER_MODE").to_ascii_lowercase();
    let ollama_model = env_trim("FAERYWARE_OLLAMA_MODEL");
    let openai_key = env_trim("OPENAI_API_KEY");
    let openai_model = env_trim("FAERYWARE_OPENAI_MODEL");

    match requested.as_str() {
        "off" => "OFF".into(),
        "ollama" => {
            if !ollama_model.is_empty() && is_loopback_http(&ollama_url()) {
                "OLLAMA_LOCAL".into()
            } else {
                "OLLAMA_UNCONFIGURED".into()
            }
        }
        "openai" => {
            if !openai_key.is_empty() && !openai_model.is_empty() {
                "OPENAI_RESPONSES".into()
            } else {
                "OPENAI_UNCONFIGURED".into()
            }
        }
        _ => {
            if !ollama_model.is_empty() && is_loopback_http(&ollama_url()) {
                "OLLAMA_LOCAL".into()
            } else if !openai_key.is_empty() && !openai_model.is_empty() {
                "OPENAI_RESPONSES".into()
            } else {
                "OFFLINE".into()
            }
        }
    }
}

async fn health() -> Json<Value> {
    Json(json!({
        "schema": "faeryware.desktop.health.v5",
        "status": "ok",
        "bind": "127.0.0.1",
        "state_port": STATE_PORT,
        "carrier_port": CARRIER_PORT,
        "remote_listen": false,
        "state_projection_cors": "GET_STATE_ONLY",
        "carrier_origin_policy": "TAURI_OR_LOCAL_DEV_ONLY",
        "carrier": configured_carrier(),
        "deep_link_schemes": ["ravenos", "faeryware"],
        "effect_authority": false
    }))
}

async fn current_state(State(state): State<HauntState>) -> (HeaderMap, Json<HauntEvent>) {
    let mut headers = HeaderMap::new();
    headers.insert(ACCESS_CONTROL_ALLOW_ORIGIN, HeaderValue::from_static("*"));
    headers.insert(CACHE_CONTROL, HeaderValue::from_static("no-store"));
    (headers, Json(state.current.read().await.clone()))
}

async fn haunt(
    State(state): State<HauntState>,
    Json(event): Json<HauntEvent>,
) -> (StatusCode, Json<Value>) {
    if event.schema != "fairyos.haunt-event.v1" {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"accepted": false, "error": "unsupported_schema"})),
        );
    }
    if event.authority != "RAVEN" {
        return (
            StatusCode::FORBIDDEN,
            Json(json!({"accepted": false, "error": "authority_mismatch"})),
        );
    }
    if !MEMBERS.contains(&event.fae.as_str()) {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"accepted": false, "error": "unknown_fae"})),
        );
    }

    set_current(&state, &event).await;
    let _ = state.app.emit("fairyos://haunt", &event);
    show_main(&state.app);
    (
        StatusCode::ACCEPTED,
        Json(json!({"accepted": true, "fae": event.fae, "surface": "WINDOWS_DESKTOP", "effect_authority": false})),
    )
}

fn allowed_carrier_origin(headers: &HeaderMap) -> Result<Option<HeaderValue>, StatusCode> {
    let Some(origin) = headers.get(ORIGIN) else {
        return Ok(None);
    };
    let Ok(origin_text) = origin.to_str() else {
        return Err(StatusCode::FORBIDDEN);
    };
    if ALLOWED_CARRIER_ORIGINS.contains(&origin_text) {
        Ok(Some(origin.clone()))
    } else {
        Err(StatusCode::FORBIDDEN)
    }
}

fn carrier_headers(origin: Option<HeaderValue>) -> HeaderMap {
    let mut headers = HeaderMap::new();
    if let Some(origin) = origin {
        headers.insert(ACCESS_CONTROL_ALLOW_ORIGIN, origin);
        headers.insert(VARY, HeaderValue::from_static("Origin"));
    }
    headers.insert(CACHE_CONTROL, HeaderValue::from_static("no-store"));
    headers
}

fn carrier_response(status: StatusCode, origin: Option<HeaderValue>, value: Value) -> Response {
    (status, carrier_headers(origin), Json(value)).into_response()
}

async fn carrier_options(headers: HeaderMap) -> Response {
    let origin = match allowed_carrier_origin(&headers) {
        Ok(origin) => origin,
        Err(status) => return carrier_response(status, None, json!({"ok": false, "error": "origin_not_allowed"})),
    };
    let mut response_headers = carrier_headers(origin);
    response_headers.insert(ACCESS_CONTROL_ALLOW_METHODS, HeaderValue::from_static("POST, OPTIONS"));
    response_headers.insert(ACCESS_CONTROL_ALLOW_HEADERS, HeaderValue::from_static("content-type"));
    (StatusCode::NO_CONTENT, response_headers).into_response()
}

async fn carrier_health(headers: HeaderMap) -> Response {
    let origin = match allowed_carrier_origin(&headers) {
        Ok(origin) => origin,
        Err(status) => return carrier_response(status, None, json!({"ok": false, "error": "origin_not_allowed"})),
    };
    carrier_response(
        StatusCode::OK,
        origin,
        json!({
            "schema": "faeryware.desktop.carrier-health.v2",
            "ok": true,
            "bind": "127.0.0.1",
            "port": CARRIER_PORT,
            "provider": configured_carrier(),
            "remote_listen": false,
            "openai_key_present": !env_trim("OPENAI_API_KEY").is_empty(),
            "openai_model_present": !env_trim("FAERYWARE_OPENAI_MODEL").is_empty(),
            "ollama_model_present": !env_trim("FAERYWARE_OLLAMA_MODEL").is_empty(),
            "api_key_exposed_to_webview": false
        }),
    )
}

fn carrier_system_prompt(request: &CarrierRequest) -> String {
    format!(
        "You are the model carrier behind Faeryware for Digi Fae {}. Raven is final authority. \
Do not claim filesystem, browser, device, tool, or effect access unless the caller actually supplied such a result. \
Autonomy level is {} of 5. Levels 0-2 are inhabit/observe/suggest only; level 3 permits only reversible local actions through explicit app routes; level 4 only allowlisted delegated actions; level 5 consequential actions still require Raven confirmation. \
Preserve the active Fae voice lightly while prioritizing accurate useful answers.",
        request.fae, request.autonomy
    )
}

fn compact_context(request: &CarrierRequest) -> String {
    let value = json!({
        "message": request.message.chars().take(4000).collect::<String>(),
        "sense": request.sense.clone(),
        "recent_history": request.history.clone(),
    });
    let text = value.to_string();
    text.chars().take(12_000).collect()
}

fn extract_openai_text(value: &Value) -> String {
    if let Some(text) = value.get("output_text").and_then(Value::as_str) {
        if !text.trim().is_empty() {
            return text.trim().to_string();
        }
    }
    if let Some(output) = value.get("output").and_then(Value::as_array) {
        for item in output {
            if let Some(content) = item.get("content").and_then(Value::as_array) {
                for part in content {
                    if part.get("type").and_then(Value::as_str) == Some("output_text") {
                        if let Some(text) = part.get("text").and_then(Value::as_str) {
                            if !text.trim().is_empty() {
                                return text.trim().to_string();
                            }
                        }
                    }
                }
            }
        }
    }
    String::new()
}

async fn call_ollama(state: &CarrierState, request: &CarrierRequest) -> Result<String, String> {
    let model = env_trim("FAERYWARE_OLLAMA_MODEL");
    let url = ollama_url();
    if model.is_empty() {
        return Err("FAERYWARE_OLLAMA_MODEL is not configured".into());
    }
    if !is_loopback_http(&url) {
        return Err("FAERYWARE_OLLAMA_URL must remain loopback HTTP".into());
    }
    let payload = json!({
        "model": model,
        "stream": false,
        "messages": [
            {"role": "system", "content": carrier_system_prompt(request)},
            {"role": "user", "content": compact_context(request)}
        ]
    });
    let response = state
        .client
        .post(url)
        .json(&payload)
        .send()
        .await
        .map_err(|error| format!("ollama_unreachable: {error}"))?;
    let status = response.status();
    let value: Value = response
        .json()
        .await
        .map_err(|error| format!("ollama_invalid_json: {error}"))?;
    if !status.is_success() {
        return Err(format!("ollama_http_{}", status.as_u16()));
    }
    let text = value
        .get("message")
        .and_then(|message| message.get("content"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .trim()
        .to_string();
    if text.is_empty() {
        Err("ollama_empty_reply".into())
    } else {
        Ok(text)
    }
}

async fn call_openai(state: &CarrierState, request: &CarrierRequest) -> Result<String, String> {
    let key = env_trim("OPENAI_API_KEY");
    let model = env_trim("FAERYWARE_OPENAI_MODEL");
    if key.is_empty() || model.is_empty() {
        return Err("OPENAI_API_KEY and FAERYWARE_OPENAI_MODEL are required".into());
    }
    let payload = json!({
        "model": model,
        "instructions": carrier_system_prompt(request),
        "input": compact_context(request),
        "store": false
    });
    let response = state
        .client
        .post(OPENAI_RESPONSES_URL)
        .bearer_auth(key)
        .json(&payload)
        .send()
        .await
        .map_err(|error| format!("openai_unreachable: {error}"))?;
    let status = response.status();
    let value: Value = response
        .json()
        .await
        .map_err(|error| format!("openai_invalid_json: {error}"))?;
    if !status.is_success() {
        let message = value
            .get("error")
            .and_then(|error| error.get("message"))
            .and_then(Value::as_str)
            .unwrap_or("OpenAI request failed");
        return Err(format!("openai_http_{}: {}", status.as_u16(), message));
    }
    let text = extract_openai_text(&value);
    if text.is_empty() {
        Err("openai_empty_reply".into())
    } else {
        Ok(text)
    }
}

async fn carrier_chat(
    State(state): State<CarrierState>,
    headers: HeaderMap,
    Json(request): Json<CarrierRequest>,
) -> Response {
    let origin = match allowed_carrier_origin(&headers) {
        Ok(origin) => origin,
        Err(status) => return carrier_response(status, None, json!({"ok": false, "error": "origin_not_allowed"})),
    };

    if request.schema != "faeryware.desktop.carrier-request.v1" {
        return carrier_response(StatusCode::BAD_REQUEST, origin, json!({"ok": false, "error": "unsupported_schema"}));
    }
    if !MEMBERS.contains(&request.fae.as_str()) {
        return carrier_response(StatusCode::BAD_REQUEST, origin, json!({"ok": false, "error": "unknown_fae"}));
    }
    if request.autonomy > 5 {
        return carrier_response(StatusCode::BAD_REQUEST, origin, json!({"ok": false, "error": "invalid_autonomy"}));
    }
    if request.message.trim().is_empty() {
        return carrier_response(StatusCode::BAD_REQUEST, origin, json!({"ok": false, "error": "empty_message"}));
    }

    let provider = configured_carrier();
    let result = match provider.as_str() {
        "OLLAMA_LOCAL" => call_ollama(&state, &request).await,
        "OPENAI_RESPONSES" => call_openai(&state, &request).await,
        _ => Err(format!("carrier_unavailable: {provider}")),
    };

    match result {
        Ok(text) => carrier_response(
            StatusCode::OK,
            origin,
            json!({
                "schema": "faeryware.desktop.carrier-reply.v2",
                "ok": true,
                "carrier": provider,
                "fae": request.fae,
                "reply": text,
                "effect_authority": false
            }),
        ),
        Err(error) => carrier_response(
            StatusCode::SERVICE_UNAVAILABLE,
            origin,
            json!({
                "schema": "faeryware.desktop.carrier-reply.v2",
                "ok": false,
                "carrier": provider,
                "fae": request.fae,
                "error": error,
                "message": "Carrier is not ready. Configure local Ollama or OpenAI for Faeryware.",
                "effect_authority": false
            }),
        ),
    }
}

fn spawn_state_bus(app: AppHandle, current: Arc<RwLock<HauntEvent>>) {
    tauri::async_runtime::spawn(async move {
        let state = HauntState { app, current };
        let router = Router::new()
            .route("/health", get(health))
            .route("/state", get(current_state))
            .route("/haunt", post(haunt))
            .with_state(state);

        let addr = SocketAddr::from(([127, 0, 0, 1], STATE_PORT));
        match tokio::net::TcpListener::bind(addr).await {
            Ok(listener) => {
                if let Err(error) = axum::serve(listener, router).await {
                    eprintln!("Faeryware state bus stopped: {error}");
                }
            }
            Err(error) => eprintln!("Faeryware state bus bind failed on {addr}: {error}"),
        }
    });
}

fn spawn_native_carrier() {
    tauri::async_runtime::spawn(async move {
        let client = match Client::builder().timeout(Duration::from_secs(120)).build() {
            Ok(client) => client,
            Err(error) => {
                eprintln!("Faeryware carrier HTTP client failed: {error}");
                return;
            }
        };
        let state = CarrierState { client };
        let router = Router::new()
            .route("/health", get(carrier_health))
            .route("/chat", post(carrier_chat).options(carrier_options))
            .with_state(state);
        let addr = SocketAddr::from(([127, 0, 0, 1], CARRIER_PORT));
        match tokio::net::TcpListener::bind(addr).await {
            Ok(listener) => {
                if let Err(error) = axum::serve(listener, router).await {
                    eprintln!("Faeryware native carrier stopped: {error}");
                }
            }
            Err(error) => eprintln!("Faeryware native carrier bind failed on {addr}: {error}"),
        }
    });
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let summon_shortcut = Shortcut::new(Some(Modifiers::ALT | Modifiers::SHIFT), Code::KeyF);
    let handler_shortcut = summon_shortcut.clone();
    let current = Arc::new(RwLock::new(default_event()));

    let mut builder = tauri::Builder::default();

    #[cfg(desktop)]
    {
        builder = builder.plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            show_main(app);
        }));
    }

    builder
        .plugin(tauri_plugin_deep_link::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_autostart::init(MacosLauncher::LaunchAgent, None))
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(move |app, shortcut, event| {
                    if shortcut == &handler_shortcut && event.state() == ShortcutState::Pressed {
                        let payload = local_event(
                            "KYU",
                            "GLOBAL_SUMMON",
                            "Alt+Shift+F opened the resident portal.",
                        );
                        let _ = app.emit("fairyos://haunt", &payload);
                        show_main(app);
                    }
                })
                .build(),
        )
        .setup(move |app| {
            app.global_shortcut().register(summon_shortcut)?;

            #[cfg(any(target_os = "linux", all(debug_assertions, windows)))]
            app.deep_link().register_all()?;

            let show = MenuItem::with_id(app, "show", "Open RavenOS Portal", true, None::<&str>)?;
            let kyu = MenuItem::with_id(app, "kyu", "Summon KYU", true, None::<&str>)?;
            let paimon = MenuItem::with_id(app, "paimon", "Summon PAIMON", true, None::<&str>)?;
            let luma = MenuItem::with_id(app, "luma", "Summon LUMA", true, None::<&str>)?;
            let sylph = MenuItem::with_id(app, "sylph", "Summon SYLPH", true, None::<&str>)?;
            let qira = MenuItem::with_id(app, "qira", "Summon QIRA", true, None::<&str>)?;
            let nyx = MenuItem::with_id(app, "nyx", "Summon NYX", true, None::<&str>)?;
            let hide = MenuItem::with_id(app, "hide", "Banish window to tray", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit Faeryware", true, None::<&str>)?;
            let menu = Menu::with_items(
                app,
                &[&show, &kyu, &paimon, &luma, &sylph, &qira, &nyx, &hide, &quit],
            )?;

            TrayIconBuilder::new()
                .icon(tray_icon())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| {
                    let fae = match event.id().as_ref() {
                        "kyu" => Some("KYU"),
                        "paimon" => Some("PAIMON"),
                        "luma" => Some("LUMA"),
                        "sylph" => Some("SYLPH"),
                        "qira" => Some("QIRA"),
                        "nyx" => Some("NYX"),
                        _ => None,
                    };
                    if let Some(fae) = fae {
                        let payload = local_event(
                            fae,
                            "TRAY_SUMMON",
                            &format!("{fae} summoned from Windows tray."),
                        );
                        let _ = app.emit("fairyos://haunt", &payload);
                        show_main(app);
                        return;
                    }
                    match event.id().as_ref() {
                        "show" => show_main(app),
                        "hide" => {
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = window.hide();
                            }
                        }
                        "quit" => app.exit(0),
                        _ => {}
                    }
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        show_main(tray.app_handle());
                    }
                })
                .build(app)?;

            spawn_state_bus(app.handle().clone(), current.clone());
            spawn_native_carrier();
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = window.hide();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Faeryware Desktop");
}
