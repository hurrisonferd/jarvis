"""
Sound Manager for Space Invaders Game
Manages all game sounds using pygame.mixer with synthesized waveforms.
"""

import pygame
import numpy as np
from typing import Optional
import threading


class SoundManager:
    """Manages all game audio including sound effects and background music."""
    
    def __init__(self):
        """Initialize pygame.mixer and prepare sound buffers."""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Volume controls (0.0 to 1.0)
        self._master_volume = 1.0
        self._sfx_volume = 0.7
        self._music_volume = 0.5
        
        # Sound effect volumes (individual per-sound scaling)
        self._sfx_scales = {
            'player_shoot': 1.0,
            'enemy_explode': 1.0,
            'player_hit': 1.0,
            'enemy_shoot': 0.8,
            'wave_complete': 1.0,
            'game_over': 1.0,
        }
        
        # Pre-generated sounds
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._music_channel: Optional[pygame.mixer.Channel] = None
        
        # Generate all sound effects
        self._generate_all_sounds()
        
        # Background music state
        self._music_playing = False
        self._music_thread: Optional[threading.Thread] = None
    
    def _generate_all_sounds(self) -> None:
        """Generate all sound effect buffers."""
        self._sounds['player_shoot'] = self._generate_player_shoot()
        self._sounds['enemy_explode'] = self._generate_enemy_explode()
        self._sounds['player_hit'] = self._generate_player_hit()
        self._sounds['enemy_shoot'] = self._generate_enemy_shoot()
        self._sounds['wave_complete'] = self._generate_wave_complete()
        self._sounds['game_over'] = self._generate_game_over()
    
    def _generate_player_shoot(self) -> pygame.mixer.Sound:
        """
        Generate a short 'pew' sound - high frequency laser.
        Creates a quick frequency sweep from high to low.
        """
        sample_rate = 44100
        duration = 0.1  # 100ms
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Frequency sweep: start high, sweep down quickly
        freq_start = 1200
        freq_end = 400
        freq = np.linspace(freq_start, freq_end, len(t))
        
        # Generate wave with exponential decay
        wave = np.sin(2 * np.pi * freq * t)
        
        # Add slight harmonics for richness
        wave += 0.3 * np.sin(4 * np.pi * freq * t)
        
        # Apply exponential decay envelope
        envelope = np.exp(-t * 25)
        wave = wave * envelope
        
        # Convert to 16-bit audio
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_enemy_explode(self) -> pygame.mixer.Sound:
        """
        Generate explosion sound - noise burst with low frequency rumble.
        """
        sample_rate = 44100
        duration = 0.4  # 400ms
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # White noise for the crack
        np.random.seed(42)
        noise = np.random.uniform(-1, 1, len(t))
        
        # Low frequency rumble
        rumble_freq = 60
        rumble = np.sin(2 * np.pi * rumble_freq * t)
        
        # Combine noise and rumble
        wave = 0.6 * noise + 0.4 * rumble
        
        # Add some crackle
        wave += 0.2 * np.random.uniform(-1, 1, len(t))
        
        # Apply decay envelope - sharp attack, gradual decay
        envelope = np.exp(-t * 8)
        wave = wave * envelope
        
        # Add sub-bass thump
        sub_t = t[:len(t)//4]
        sub_wave = np.sin(2 * np.pi * 30 * sub_t)
        sub_envelope = np.exp(-sub_t * 20)
        sub_wave = sub_wave * sub_envelope * 0.5
        wave[:len(sub_wave)] += sub_wave
        
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_player_hit(self) -> pygame.mixer.Sound:
        """
        Generate impact sound - low thud with mid-frequency crack.
        """
        sample_rate = 44100
        duration = 0.25  # 250ms
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Low frequency impact
        impact_freq = 80
        wave = np.sin(2 * np.pi * impact_freq * t)
        
        # Add mid-frequency crunch
        crunch_freq = 300
        wave += 0.5 * np.sin(2 * np.pi * crunch_freq * t)
        
        # White noise burst
        noise = np.random.uniform(-1, 1, len(t))
        wave += 0.3 * noise
        
        # Sharp decay envelope
        envelope = np.exp(-t * 15)
        wave = wave * envelope
        
        # Add initial impact thump
        thump = np.sin(2 * np.pi * 40 * t[:len(t)//8])
        thump *= np.exp(-t[:len(t)//8] * 50)
        wave[:len(thump)] += thump * 0.8
        
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_enemy_shoot(self) -> pygame.mixer.Sound:
        """
        Generate enemy 'pew' - deeper, more menacing than player shoot.
        """
        sample_rate = 44100
        duration = 0.12  # 120ms
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Lower starting frequency for more menacing sound
        freq_start = 800
        freq_end = 250
        freq = np.linspace(freq_start, freq_end, len(t))
        
        wave = np.sin(2 * np.pi * freq * t)
        
        # Add some square wave character
        wave += 0.2 * np.sign(np.sin(2 * np.pi * freq * t))
        
        # Faster decay for punchier sound
        envelope = np.exp(-t * 30)
        wave = wave * envelope
        
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_wave_complete(self) -> pygame.mixer.Sound:
        """
        Generate victory fanfare - ascending arpeggio.
        """
        sample_rate = 44100
        
        # Notes for a simple victory fanfare (C5, E5, G5, C6)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_duration = 0.15
        pause_duration = 0.05
        
        all_samples = []
        
        for freq in notes:
            t = np.linspace(0, note_duration, int(sample_rate * note_duration), False)
            wave = np.sin(2 * np.pi * freq * t)
            
            # Add harmonics for richer sound
            wave += 0.3 * np.sin(4 * np.pi * freq * t)
            wave += 0.1 * np.sin(6 * np.pi * freq * t)
            
            # Envelope with attack and sustain
            attack = np.exp(t[:len(t)//10] * 20) / np.exp(0)
            sustain = np.ones(len(t) - len(t)//10)
            envelope = np.concatenate([attack, sustain])
            
            # Decay at the end
            decay = np.exp(-(t - note_duration + 0.05) * 10)
            decay = np.clip(decay, 0, 1)
            envelope = envelope * decay
            
            wave = wave * envelope
            all_samples.extend(wave)
            
            # Add pause between notes
            pause_samples = np.zeros(int(sample_rate * pause_duration))
            all_samples.extend(pause_samples)
        
        # Add a final chord
        chord_duration = 0.4
        t = np.linspace(0, chord_duration, int(sample_rate * chord_duration), False)
        chord = np.zeros(len(t))
        for freq in notes:
            chord += np.sin(2 * np.pi * freq * t)
        chord = chord / len(notes)  # Normalize chord
        chord *= np.exp(-t * 3)  # Decay
        all_samples.extend(chord)
        
        wave = np.array(all_samples)
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_game_over(self) -> pygame.mixer.Sound:
        """
        Generate sad trombone 'wah-wah-wah-waaah' sound.
        """
        sample_rate = 44100
        
        # Notes descending (B4, A4, G4, E4) - classic sad trombone
        notes = [493.88, 440.00, 392.00, 329.63]
        note_duration = 0.35
        
        all_samples = []
        
        for i, freq in enumerate(notes):
            t = np.linspace(0, note_duration, int(sample_rate * note_duration), False)
            
            # Create 'wah' effect with frequency modulation
            wah_rate = 6 if i < 3 else 2  # Faster for first three, slow for last
            wah_depth = 30 if i < 3 else 50
            
            wah_mod = wah_depth * np.sin(2 * np.pi * wah_rate * t)
            modulated_freq = freq + wah_mod
            
            wave = np.sin(2 * np.pi * modulated_freq * t)
            
            # Add brass-like harmonics
            wave += 0.4 * np.sin(4 * np.pi * modulated_freq * t)
            wave += 0.15 * np.sin(6 * np.pi * modulated_freq * t)
            
            # Different envelopes for each note
            if i < 3:
                # Short notes with quick attack
                envelope = np.exp(-t * 5)
                attack = 1 - np.exp(-t * 30)
                envelope = envelope * attack
            else:
                # Long final note with slow decay
                envelope = np.exp(-t * 2)
                attack = 1 - np.exp(-t * 10)
                envelope = envelope * attack
            
            wave = wave * envelope
            all_samples.extend(wave)
            
            # Small pause between notes
            if i < 3:
                pause_samples = np.zeros(int(sample_rate * 0.05))
                all_samples.extend(pause_samples)
        
        wave = np.array(all_samples)
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _generate_background_music(self) -> pygame.mixer.Sound:
        """
        Generate looping synth melody for gameplay.
        Creates a simple but engaging 8-bar loop.
        """
        sample_rate = 44100
        bpm = 120
        beat_duration = 60 / bpm
        bar_duration = beat_duration * 4
        
        # 8 bars total
        total_duration = bar_duration * 8
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave = np.zeros(len(t))
        
        # Bass pattern (simple root notes)
        bass_notes = [
            (0, 65.41),      # C2
            (1, 65.41),      # C2
            (2, 87.31),      # F2
            (3, 87.31),      # F2
            (4, 73.42),      # D2
            (5, 73.42),      # D2
            (6, 65.41),      # C2
            (7, 65.41),      # C2
        ]
        
        # Lead melody pattern
        melody_notes = [
            (0, 261.63, 0.5),   # C4, eighth note
            (0.5, 329.63, 0.5), # E4
            (1, 392.00, 1.0),   # G4
            (2, 349.23, 0.5),   # F4
            (2.5, 392.00, 0.5), # G4
            (3, 440.00, 1.0),   # A4
            (4, 293.66, 0.5),   # D4
            (4.5, 349.63, 0.5), # F4
            (5, 392.00, 1.0),   # G4
            (6, 261.63, 2.0),   # C4, half note
        ]
        
        # Percussion pattern (hi-hat on off-beats)
        hihat_beats = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
        
        # Generate bass
        for bar, freq in bass_notes:
            start_time = bar * bar_duration
            end_time = start_time + bar_duration * 0.9
            mask = (t >= start_time) & (t < end_time)
            
            bass_t = t[mask] - start_time
            bass_wave = np.sin(2 * np.pi * freq * bass_t)
            bass_wave += 0.3 * np.sin(4 * np.pi * freq * bass_t)
            
            # Bass envelope
            attack = np.exp(bass_t * 10)
            decay = np.exp(-bass_t * 2)
            envelope = np.minimum(attack, 1) * decay
            bass_wave *= envelope * 0.6
            
            wave[mask] += bass_wave
        
        # Generate melody
        for start_beat, freq, note_length in melody_notes:
            start_time = start_beat * beat_duration
            end_time = start_time + note_length * beat_duration
            mask = (t >= start_time) & (t < end_time)
            
            melody_t = t[mask] - start_time
            melody_wave = np.sin(2 * np.pi * freq * melody_t)
            melody_wave += 0.25 * np.sin(4 * np.pi * freq * melody_t)
            melody_wave += 0.1 * np.sin(6 * np.pi * freq * melody_t)
            
            # Melody envelope
            attack = np.exp(melody_t * 15)
            sustain_level = 0.7
            release_start = note_length * beat_duration * 0.7
            release = np.exp(-(melody_t - release_start) * 8)
            release = np.maximum(release, sustain_level)
            envelope = np.minimum(attack, 1) * release
            melody_wave *= envelope * 0.4
            
            wave[mask] += melody_wave
        
        # Generate hi-hat
        for beat_time in hihat_beats:
            start_time = beat_time * beat_duration
            end_time = start_time + 0.05
            mask = (t >= start_time) & (t < end_time)
            
            hihat = np.random.uniform(-1, 1, np.sum(mask))
            hihat *= np.exp(-(t[mask] - start_time) * 100)
            wave[mask] += hihat * 0.15
        
        # Add subtle pad for atmosphere
        pad_freqs = [130.81, 196.00]  # C3, G3
        for freq in pad_freqs:
            pad_wave = np.sin(2 * np.pi * freq * t)
            pad_wave *= 0.05  # Very subtle
            wave += pad_wave
        
        audio = self._normalize_audio(wave)
        return pygame.mixer.Sound(buffer=audio)
    
    def _normalize_audio(self, wave: np.ndarray) -> np.ndarray:
        """Convert float audio to 16-bit stereo array."""
        # Clip to prevent overflow
        wave = np.clip(wave, -1, 1)
        
        # Convert to 16-bit
        audio = (wave * 32767).astype(np.int16)
        
        # Make stereo (duplicate to both channels)
        audio_stereo = np.column_stack((audio, audio))
        
        return audio_stereo
    
    def _calculate_volume(self, sound_name: str) -> float:
        """Calculate final volume for a sound based on all volume settings."""
        scale = self._sfx_scales.get(sound_name, 1.0)
        return self._master_volume * self._sfx_volume * scale
    
    def play_sfx(self, sound_name: str) -> None:
        """Play a sound effect by name."""
        if sound_name not in self._sounds:
            print(f"Warning: Sound '{sound_name}' not found")
            return
        
        sound = self._sounds[sound_name]
        volume = self._calculate_volume(sound_name)
        sound.set_volume(volume)
        sound.play()
    
    def play_player_shoot(self) -> None:
        """Play player shooting sound."""
        self.play_sfx('player_shoot')
    
    def play_enemy_explode(self) -> None:
        """Play enemy explosion sound."""
        self.play_sfx('enemy_explode')
    
    def play_player_hit(self) -> None:
        """Play player hit sound."""
        self.play_sfx('player_hit')
    
    def play_enemy_shoot(self) -> None:
        """Play enemy shooting sound."""
        self.play_sfx('enemy_shoot')
    
    def play_wave_complete(self) -> None:
        """Play wave complete fanfare."""
        self.play_sfx('wave_complete')
    
    def play_game_over(self) -> None:
        """Play game over sound."""
        self.play_sfx('game_over')
    
    def play_music(self) -> None:
        """Start background music loop."""
        if self._music_playing:
            return
        
        self._music_playing = True
        self._music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self._music_thread.start()
    
    def _music_loop(self) -> None:
        """Internal music loop - generates and plays music repeatedly."""
        while self._music_playing:
            music = self._generate_background_music()
            music.set_volume(self._master_volume * self._music_volume)
            
            # Get channel 0 for music
            channel = pygame.mixer.Channel(0)
            channel.play(music, loops=-1)  # -1 = loop forever
            
            # Wait for music to finish (shouldn't happen with loops=-1)
            while channel.get_busy() and self._music_playing:
                pygame.time.wait(100)
    
    def stop_music(self) -> None:
        """Stop background music."""
        self._music_playing = False
        if self._music_thread and self._music_thread.is_alive():
            self._music_thread.join(timeout=1.0)
        
        # Stop the mixer channel
        channel = pygame.mixer.Channel(0)
        channel.stop()
    
    def pause_music(self) -> None:
        """Pause background music."""
        channel = pygame.mixer.Channel(0)
        channel.pause()
    
    def resume_music(self) -> None:
        """Resume background music."""
        channel = pygame.mixer.Channel(0)
        channel.unpause()
    
    @property
    def master_volume(self) -> float:
        """Get master volume (0.0 to 1.0)."""
        return self._master_volume
    
    @master_volume.setter
    def master_volume(self, value: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self._master_volume = max(0.0, min(1.0, value))
    
    @property
    def sfx_volume(self) -> float:
        """Get SFX volume (0.0 to 1.0)."""
        return self._sfx_volume
    
    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        """Set SFX volume (0.0 to 1.0)."""
        self._sfx_volume = max(0.0, min(1.0, value))
    
    @property
    def music_volume(self) -> float:
        """Get music volume (0.0 to 1.0)."""
        return self._music_volume
    
    @music_volume.setter
    def music_volume(self, value: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self._music_volume = max(0.0, min(1.0, value))
        # Update currently playing music
        if self._music_playing:
            channel = pygame.mixer.Channel(0)
            if channel.get_busy():
                channel.set_volume(self._master_volume * self._music_volume)
    
    def set_volume(self, master: Optional[float] = None,
                   sfx: Optional[float] = None,
                   music: Optional[float] = None) -> None:
        """Set multiple volume levels at once."""
        if master is not None:
            self.master_volume = master
        if sfx is not None:
            self.sfx_volume = sfx
        if music is not None:
            self.music_volume = music
    
    def get_volume_settings(self) -> dict[str, float]:
        """Get all volume settings as a dictionary."""
        return {
            'master': self._master_volume,
            'sfx': self._sfx_volume,
            'music': self._music_volume
        }
    
    def shutdown(self) -> None:
        """Clean shutdown of sound manager."""
        self.stop_music()
        pygame.mixer.quit()


# Standalone test
if __name__ == "__main__":
    print("Initializing Sound Manager...")
    sm = SoundManager()
    
    print("\nVolume Settings:", sm.get_volume_settings())
    
    print("\nTesting all sound effects...")
    
    print("  Playing player_shoot...")
    sm.play_player_shoot()
    pygame.time.wait(200)
    
    print("  Playing enemy_explode...")
    sm.play_enemy_explode()
    pygame.time.wait(500)
    
    print("  Playing player_hit...")
    sm.play_player_hit()
    pygame.time.wait(300)
    
    print("  Playing enemy_shoot...")
    sm.play_enemy_shoot()
    pygame.time.wait(200)
    
    print("  Playing wave_complete...")
    sm.play_wave_complete()
    pygame.time.wait(1500)
    
    print("  Playing game_over...")
    sm.play_game_over()
    pygame.time.wait(2500)
    
    print("\nTesting volume controls...")
    sm.master_volume = 0.5
    sm.sfx_volume = 0.8
    print(f"  Volume settings: {sm.get_volume_settings()}")
    
    print("\nTesting background music...")
    sm.music_volume = 0.3
    sm.play_music()
    print("  Music started. Playing for 3 seconds...")
    pygame.time.wait(3000)
    
    print("\nPausing music...")
    sm.pause_music()
    pygame.time.wait(1000)
    
    print("Resuming music...")
    sm.resume_music()
    pygame.time.wait(1000)
    
    print("\nStopping music...")
    sm.stop_music()
    
    print("\nShutting down...")
    sm.shutdown()
    
    print("\n✅ All tests passed!")