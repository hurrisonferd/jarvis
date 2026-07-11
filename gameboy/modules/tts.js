// ── TTS Module ──────────────────────────────────────────────────────────────
// Fleet voice auto-read using Web Speech API

const voiceMap = {
  'LILITH': { pitch: 1.1, rate: 0.95 },
  'AYRE': { pitch: 0.95, rate: 0.90 },
  'JARVIS': { pitch: 0.85, rate: 0.92 },
  'THOR': { pitch: 0.9, rate: 0.88 },
  'NEO': { pitch: 1.15, rate: 0.95 },
  'EREBUS': { pitch: 0.75, rate: 0.85 },
  'VIRGIL': { pitch: 1.05, rate: 0.92 },
  'SHAKA': { pitch: 1.0, rate: 0.92 },
  'EDISON': { pitch: 0.95, rate: 0.90 },
  'PYTHAGORAS': { pitch: 1.0, rate: 0.88 },
  'ATLAS': { pitch: 0.9, rate: 0.85 },
  'YORK': { pitch: 1.05, rate: 0.92 }
};

function coordinatorSpeak(nodeName, text) {
  if (!window.speechSynthesis || !text) return;
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(String(text).slice(0, 400));
    const voices = window.speechSynthesis.getVoices().filter(v => v.lang.startsWith('en'));
    const settings = voiceMap[nodeName] || { pitch: 1.0, rate: 0.95 };
    const v = voices[Math.floor(settings.pitch * 10) % voices.length];
    if (v) u.voice = v;
    u.rate = settings.rate;
    u.pitch = settings.pitch;
    u.volume = 1;
    window.speechSynthesis.speak(u);
  } catch (e) {
    console.log('[TTS] Error:', e);
  }
}

function fleetAutoSpeak(sender, text) {
  if (!fleetVoiceOn || !text) return;
  coordinatorSpeak(sender, text);
}

function speakToggle() {
  voiceOn = !voiceOn;
  if (!voiceOn && window.speechSynthesis) window.speechSynthesis.cancel();
  draw();
}

function speakListen() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert('Voice needs Chrome/Edge'); return; }
  if (voiceListening) {
    try { _jarvisRecog && _jarvisRecog.stop(); } catch (e) {}
    voiceListening = false;
    draw();
    return;
  }
  _jarvisRecog = new SR();
  _jarvisRecog.lang = 'en-US';
  _jarvisRecog.interimResults = false;
  _jarvisRecog.maxAlternatives = 1;
  voiceListening = true;
  draw();
  _jarvisRecog.onresult = (e) => {
    const t = e.results[0][0].transcript;
    const inp = document.getElementById('speak-input');
    if (inp) inp.value = t;
    speakHistory.push({ from: 'raven', text: t, ts: Date.now() });
    voiceListening = false;
    draw();
    if (t.trim()) speakSend();
  };
  _jarvisRecog.onerror = () => { voiceListening = false; draw(); };
  _jarvisRecog.onend = () => { voiceListening = false; draw(); };
  try { _jarvisRecog.start(); } catch (e) { voiceListening = false; draw(); }
}

function fleetVoiceToggle() {
  fleetVoiceOn = !fleetVoiceOn;
  if (!fleetVoiceOn && window.speechSynthesis) window.speechSynthesis.cancel();
  draw();
}

function fleetMicListen() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert('Voice needs Chrome/Edge'); return; }
  if (fleetMicOn) {
    try { _fleetMicRecog && _fleetMicRecog.stop(); } catch (e) {}
    fleetMicOn = false;
    draw();
    return;
  }
  _fleetMicRecog = new SR();
  _fleetMicRecog.lang = 'en-US';
  _fleetMicRecog.interimResults = false;
  _fleetMicRecog.maxAlternatives = 1;
  fleetMicOn = true;
  draw();
  _fleetMicRecog.onresult = (e) => {
    const t = e.results[0][0].transcript;
    fleetInput = t;
    fleetMicOn = false;
    draw();
    if (t.trim()) fleetSend();
  };
  _fleetMicRecog.onerror = () => { fleetMicOn = false; draw(); };
  _fleetMicRecog.onend = () => { fleetMicOn = false; draw(); };
  try { _fleetMicRecog.start(); } catch (e) { fleetMicOn = false; draw(); }
}

// Preload voices
if (window.speechSynthesis) {
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}
