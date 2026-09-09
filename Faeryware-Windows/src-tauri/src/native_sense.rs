use serde::Serialize;
use std::{
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, RwLock,
    },
    time::{Duration, SystemTime, UNIX_EPOCH},
};

#[derive(Clone, Debug, Serialize)]
pub struct UiLandmark {
    pub left: i32,
    pub top: i32,
    pub right: i32,
    pub bottom: i32,
    pub name: String,
    pub control_type: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct NativeSenseSnapshot {
    pub schema: String,
    pub audio_peak: f32,
    pub audio_available: bool,
    pub ui_perching_enabled: bool,
    pub landmark: Option<UiLandmark>,
    pub observed_unix_ms: u128,
    pub raw_audio_recorded: bool,
    pub screen_capture: bool,
    pub keylogging: bool,
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}

pub fn fresh_snapshot() -> NativeSenseSnapshot {
    NativeSenseSnapshot {
        schema: "faeryware.desktop.native-sense.v1".into(),
        audio_peak: 0.0,
        audio_available: false,
        ui_perching_enabled: false,
        landmark: None,
        observed_unix_ms: now_ms(),
        raw_audio_recorded: false,
        screen_capture: false,
        keylogging: false,
    }
}

#[cfg(windows)]
fn spawn_ui_landmark_sensor(
    snapshot: Arc<RwLock<NativeSenseSnapshot>>,
    ui_perching_enabled: Arc<AtomicBool>,
) {
    std::thread::Builder::new()
        .name("faeryware-uia-sense".into())
        .spawn(move || {
            use uiautomation::UIAutomation;

            let own_pid = std::process::id() as i32;
            let automation = UIAutomation::new().ok();

            loop {
                let enabled = ui_perching_enabled.load(Ordering::Relaxed);
                let landmark = if enabled {
                    automation
                        .as_ref()
                        .and_then(|automation| automation.get_focused_element().ok())
                        .and_then(|element| {
                            if element.get_process_id().ok() == Some(own_pid) {
                                return None;
                            }
                            let rect = element.get_bounding_rectangle().ok()?;
                            let width = rect.get_width();
                            let height = rect.get_height();
                            if width <= 1 || height <= 1 {
                                return None;
                            }
                            Some(UiLandmark {
                                left: rect.get_left(),
                                top: rect.get_top(),
                                right: rect.get_right(),
                                bottom: rect.get_bottom(),
                                name: element
                                    .get_name()
                                    .unwrap_or_default()
                                    .chars()
                                    .take(120)
                                    .collect(),
                                control_type: element
                                    .get_localized_control_type()
                                    .unwrap_or_else(|_| "control".into())
                                    .chars()
                                    .take(64)
                                    .collect(),
                            })
                        })
                } else {
                    None
                };

                if let Ok(mut state) = snapshot.write() {
                    state.ui_perching_enabled = enabled;
                    state.landmark = landmark;
                    state.observed_unix_ms = now_ms();
                }
                std::thread::sleep(Duration::from_millis(if enabled { 160 } else { 450 }));
            }
        })
        .ok();
}

#[cfg(windows)]
fn spawn_audio_peak_sensor(snapshot: Arc<RwLock<NativeSenseSnapshot>>) {
    std::thread::Builder::new()
        .name("faeryware-audio-meter".into())
        .spawn(move || {
            use windows::Win32::{
                Media::Audio::{
                    eMultimedia, eRender, Endpoints::IAudioMeterInformation, IMMDeviceEnumerator,
                    MMDeviceEnumerator,
                },
                System::Com::{CoCreateInstance, CoInitializeEx, CLSCTX_ALL, COINIT_MULTITHREADED},
            };

            let _ = unsafe { CoInitializeEx(None, COINIT_MULTITHREADED) };
            let mut meter: Option<IAudioMeterInformation> = None;
            let mut retry_at = std::time::Instant::now();

            loop {
                if meter.is_none() && std::time::Instant::now() >= retry_at {
                    meter = (|| -> windows::core::Result<IAudioMeterInformation> {
                        let enumerator: IMMDeviceEnumerator = unsafe {
                            CoCreateInstance(&MMDeviceEnumerator, None, CLSCTX_ALL)?
                        };
                        let device = unsafe {
                            enumerator.GetDefaultAudioEndpoint(eRender, eMultimedia)?
                        };
                        unsafe { device.Activate::<IAudioMeterInformation>(CLSCTX_ALL, None) }
                    })()
                    .ok();
                    retry_at = std::time::Instant::now() + Duration::from_secs(2);
                }

                let peak = meter
                    .as_ref()
                    .and_then(|meter| unsafe { meter.GetPeakValue().ok() });

                if peak.is_none() && meter.is_some() {
                    meter = None;
                    retry_at = std::time::Instant::now() + Duration::from_millis(750);
                }

                if let Ok(mut state) = snapshot.write() {
                    state.audio_peak = peak.unwrap_or(0.0).clamp(0.0, 1.0);
                    state.audio_available = peak.is_some();
                    state.observed_unix_ms = now_ms();
                }
                std::thread::sleep(Duration::from_millis(64));
            }
        })
        .ok();
}

#[cfg(windows)]
pub fn spawn_native_sensors(
    snapshot: Arc<RwLock<NativeSenseSnapshot>>,
    ui_perching_enabled: Arc<AtomicBool>,
) {
    spawn_ui_landmark_sensor(snapshot.clone(), ui_perching_enabled);
    spawn_audio_peak_sensor(snapshot);
}

#[cfg(not(windows))]
pub fn spawn_native_sensors(
    snapshot: Arc<RwLock<NativeSenseSnapshot>>,
    ui_perching_enabled: Arc<AtomicBool>,
) {
    std::thread::Builder::new()
        .name("faeryware-sense-stub".into())
        .spawn(move || loop {
            if let Ok(mut state) = snapshot.write() {
                state.ui_perching_enabled = ui_perching_enabled.load(Ordering::Relaxed);
                state.observed_unix_ms = now_ms();
            }
            std::thread::sleep(Duration::from_millis(500));
        })
        .ok();
}
