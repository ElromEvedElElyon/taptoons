#!/usr/bin/env python3
"""
TapToons v3.0 — Programmatic Sound Effects Generator
=====================================================
Generates all game SFX, background music, and UI sounds
using pure Python (wave + struct). No external dependencies.

Output: sounds.json with base64-encoded WAV data URIs.

Sample Rate: 22050 Hz | Bit Depth: 16-bit | Channels: Mono
Style: Crisp, punchy, retro-modern (Celeste / Shovel Knight quality)
"""

import wave
import struct
import math
import random
import base64
import json
import io
import os

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
SAMPLE_RATE = 22050
MAX_AMP = 32767
TWO_PI = 2.0 * math.pi

# Musical note frequencies (A4 = 440Hz)
NOTES = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
    'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
    'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51,
}


# ──────────────────────────────────────────────
# Oscillators
# ──────────────────────────────────────────────
def sine(phase):
    """Pure sine wave."""
    return math.sin(phase)


def square(phase):
    """Square wave with slight bandwidth limiting for less harsh clipping."""
    s = math.sin(phase)
    # Soft clipping for a warmer square
    return max(-1.0, min(1.0, s * 4.0))


def hard_square(phase):
    """True hard square wave for authentic chiptune."""
    return 1.0 if math.sin(phase) >= 0 else -1.0


def triangle(phase):
    """Triangle wave — smooth, warm bass tone."""
    p = (phase % TWO_PI) / TWO_PI
    if p < 0.25:
        return 4.0 * p
    elif p < 0.75:
        return 2.0 - 4.0 * p
    else:
        return -4.0 + 4.0 * p


def sawtooth(phase):
    """Sawtooth wave — buzzy, aggressive."""
    p = (phase % TWO_PI) / TWO_PI
    return 2.0 * p - 1.0


def noise():
    """White noise sample."""
    return random.uniform(-1.0, 1.0)


def pulse(phase, duty=0.25):
    """Pulse wave with variable duty cycle — NES-style."""
    p = (phase % TWO_PI) / TWO_PI
    return 1.0 if p < duty else -1.0


# ──────────────────────────────────────────────
# Envelope Generators
# ──────────────────────────────────────────────
def adsr_envelope(t, duration, attack=0.01, decay=0.05, sustain_level=0.7, release=0.05):
    """Standard ADSR envelope."""
    release_start = duration - release
    if t < attack:
        return t / attack if attack > 0 else 1.0
    elif t < attack + decay:
        d = (t - attack) / decay if decay > 0 else 0
        return 1.0 - (1.0 - sustain_level) * d
    elif t < release_start:
        return sustain_level
    elif t < duration:
        r = (t - release_start) / release if release > 0 else 0
        return sustain_level * (1.0 - r)
    return 0.0


def quick_decay(t, duration, power=2.0):
    """Quick exponential decay — good for percussive sounds."""
    progress = t / duration
    return max(0.0, (1.0 - progress) ** power)


def linear_fade(t, duration):
    """Simple linear fade out."""
    return max(0.0, 1.0 - t / duration)


# ──────────────────────────────────────────────
# Utility: Frequency interpolation
# ──────────────────────────────────────────────
def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t


def exp_interp(a, b, t):
    """Exponential interpolation — more natural pitch sweeps."""
    if a <= 0:
        a = 1.0
    if b <= 0:
        b = 1.0
    return a * ((b / a) ** t)


# ──────────────────────────────────────────────
# WAV Builder
# ──────────────────────────────────────────────
def samples_to_wav(samples):
    """Convert list of float samples [-1, 1] to WAV bytes."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        packed = b''
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            packed += struct.pack('<h', int(clamped * MAX_AMP))
        wf.writeframes(packed)
    return buf.getvalue()


def wav_to_data_uri(wav_bytes):
    """Convert WAV bytes to base64 data URI."""
    b64 = base64.b64encode(wav_bytes).decode('ascii')
    return f"data:audio/wav;base64,{b64}"


def generate_samples(duration, generator_fn):
    """Generate samples for a given duration using a generator function.
    generator_fn(t, i, total) -> float sample value
    """
    total = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total):
        t = i / SAMPLE_RATE
        samples.append(generator_fn(t, i, total))
    return samples


def mix_tracks(*tracks):
    """Mix multiple sample tracks together. Normalizes if clipping."""
    if not tracks:
        return []
    length = max(len(t) for t in tracks)
    mixed = [0.0] * length
    for track in tracks:
        for i in range(len(track)):
            mixed[i] += track[i]
    # Normalize to prevent clipping
    peak = max(abs(s) for s in mixed) if mixed else 1.0
    if peak > 1.0:
        mixed = [s / peak for s in mixed]
    return mixed


def apply_volume(samples, vol):
    """Scale samples by volume factor."""
    return [s * vol for s in samples]


def apply_lowpass(samples, cutoff_freq):
    """Simple one-pole lowpass filter."""
    rc = 1.0 / (TWO_PI * cutoff_freq)
    dt = 1.0 / SAMPLE_RATE
    alpha = dt / (rc + dt)
    out = [0.0] * len(samples)
    out[0] = samples[0] * alpha
    for i in range(1, len(samples)):
        out[i] = out[i - 1] + alpha * (samples[i] - out[i - 1])
    return out


def apply_highpass(samples, cutoff_freq):
    """Simple one-pole highpass filter."""
    rc = 1.0 / (TWO_PI * cutoff_freq)
    dt = 1.0 / SAMPLE_RATE
    alpha = rc / (rc + dt)
    out = [0.0] * len(samples)
    out[0] = samples[0]
    for i in range(1, len(samples)):
        out[i] = alpha * (out[i - 1] + samples[i] - samples[i - 1])
    return out


def apply_distortion(samples, amount=2.0):
    """Soft clipping distortion."""
    return [math.tanh(s * amount) for s in samples]


def apply_reverb(samples, delay_ms=40, decay=0.3, taps=3):
    """Simple multi-tap delay reverb."""
    out = list(samples)
    for tap in range(1, taps + 1):
        delay_samples = int(SAMPLE_RATE * delay_ms * tap / 1000.0)
        tap_decay = decay ** tap
        for i in range(delay_samples, len(out)):
            out[i] += samples[i - delay_samples] * tap_decay
    # Normalize
    peak = max(abs(s) for s in out) if out else 1.0
    if peak > 1.0:
        out = [s / peak for s in out]
    return out


# ──────────────────────────────────────────────
# GAME SFX
# ──────────────────────────────────────────────

def gen_jump():
    """Short upward sweep, 100ms, sine 200Hz->800Hz. Punchy platformer jump."""
    duration = 0.10

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(200, 800, progress)
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 1.5)
        # Add a subtle 2nd harmonic for body
        sig = sine(phase) * 0.8 + sine(phase * 2.0) * 0.2
        return sig * env * 0.85

    return generate_samples(duration, gen)


def gen_double_jump():
    """Higher sweep, 80ms, 400Hz->1200Hz with slight vibrato."""
    duration = 0.08

    def gen(t, i, total):
        progress = t / duration
        base_freq = exp_interp(400, 1200, progress)
        # Vibrato: 30Hz modulation, depth increases
        vibrato = math.sin(TWO_PI * 30 * t) * 40 * progress
        freq = base_freq + vibrato
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 1.3)
        sig = sine(phase) * 0.7 + sine(phase * 1.5) * 0.3
        return sig * env * 0.85

    return generate_samples(duration, gen)


def gen_land():
    """Quick thud, 60ms, 150Hz->50Hz with noise layer."""
    duration = 0.06

    def gen(t, i, total):
        progress = t / duration
        freq = lerp(150, 50, progress)
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 3.0)
        # Thud: low sine + filtered noise
        thud = sine(phase) * 0.6
        n = noise() * 0.4 * quick_decay(t, duration, 5.0)
        return (thud + n) * env * 0.9

    return generate_samples(duration, gen)


def gen_coin_collect():
    """Classic ascending ding, 150ms, 800Hz->1600Hz, bright and sparkly."""
    duration = 0.15

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(800, 1600, min(progress * 2.0, 1.0))
        phase = TWO_PI * freq * t
        env = adsr_envelope(t, duration, attack=0.003, decay=0.02, sustain_level=0.5, release=0.08)
        # Bright sine + harmonic sparkle
        sig = sine(phase) * 0.6 + sine(phase * 2.0) * 0.25 + sine(phase * 3.0) * 0.15
        return sig * env * 0.8

    return generate_samples(duration, gen)


def gen_ring_collect():
    """Metallic ring, 200ms, 1000Hz with harmonics. Shimmery."""
    duration = 0.20

    def gen(t, i, total):
        freq = 1000.0
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 1.8)
        # Metallic: inharmonic overtones
        sig = (sine(phase) * 0.35 +
               sine(phase * 2.76) * 0.25 +
               sine(phase * 4.07) * 0.15 +
               sine(phase * 5.54) * 0.10 +
               sine(phase * 6.91) * 0.08 +
               sine(phase * 8.23) * 0.07)
        # Slight shimmer via AM
        shimmer = 0.8 + 0.2 * math.sin(TWO_PI * 15 * t)
        return sig * env * shimmer * 0.85

    return generate_samples(duration, gen)


def gen_enemy_stomp():
    """Satisfying pop, 100ms, 300Hz->100Hz square wave."""
    duration = 0.10

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(300, 100, progress)
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 2.5)
        # Square pop with noise transient
        transient = noise() * 0.6 * quick_decay(t, 0.01, 4.0) if t < 0.01 else 0.0
        sig = square(phase) * 0.5 + transient
        return sig * env * 0.8

    return generate_samples(duration, gen)


def gen_hurt():
    """Descending buzz, 300ms, 500Hz->100Hz saw wave."""
    duration = 0.30

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(500, 100, progress)
        phase = TWO_PI * freq * t
        env = adsr_envelope(t, duration, attack=0.005, decay=0.05, sustain_level=0.6, release=0.15)
        # Buzzy sawtooth + distortion feel
        sig = sawtooth(phase) * 0.5 + square(phase * 0.5) * 0.3
        # Tremolo for "pain" feel
        trem = 0.7 + 0.3 * math.sin(TWO_PI * 12 * t)
        return sig * env * trem * 0.75

    return generate_samples(duration, gen)


def gen_death():
    """Dramatic descend, 500ms, 600Hz->50Hz with tremolo."""
    duration = 0.50

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(600, 50, progress)
        phase = TWO_PI * freq * t
        env = adsr_envelope(t, duration, attack=0.01, decay=0.1, sustain_level=0.5, release=0.25)
        # Rich descending tone
        sig = (sawtooth(phase) * 0.35 +
               square(phase) * 0.25 +
               sine(phase * 0.5) * 0.2 +
               noise() * 0.05 * progress)
        # Increasing tremolo for drama
        trem_speed = lerp(6, 20, progress)
        trem = 0.6 + 0.4 * math.sin(TWO_PI * trem_speed * t)
        return sig * env * trem * 0.8

    return generate_samples(duration, gen)


def gen_speed_boost():
    """Whoosh with rising pitch, 400ms, noise + 200Hz->600Hz."""
    duration = 0.40

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(200, 600, progress)
        phase = TWO_PI * freq * t
        # Envelope: quick attack, sustained, quick fade
        env = adsr_envelope(t, duration, attack=0.02, decay=0.05, sustain_level=0.7, release=0.15)
        # Tonal sweep
        tonal = sine(phase) * 0.4 + triangle(phase * 2.0) * 0.2
        # Noise whoosh — bandpassed feel via mixing
        n = noise() * 0.35 * (0.5 + 0.5 * math.sin(TWO_PI * freq * 0.001 * t))
        return (tonal + n) * env * 0.8

    return generate_samples(duration, gen)


def gen_power_up():
    """Ascending arpeggio, 500ms, C-E-G-C notes. Triumphant."""
    duration = 0.50
    notes_seq = [NOTES['C5'], NOTES['E5'], NOTES['G5'], NOTES['C6']]
    note_dur = duration / len(notes_seq)

    def gen(t, i, total):
        note_idx = min(int(t / note_dur), len(notes_seq) - 1)
        local_t = t - note_idx * note_dur
        freq = notes_seq[note_idx]
        phase = TWO_PI * freq * t
        # Each note has its own quick envelope
        note_env = adsr_envelope(local_t, note_dur, attack=0.005, decay=0.03, sustain_level=0.7, release=0.04)
        # Overall envelope
        overall = adsr_envelope(t, duration, attack=0.005, decay=0.02, sustain_level=0.85, release=0.08)
        # Bright chiptune square
        sig = pulse(phase, 0.25) * 0.5 + sine(phase * 2) * 0.3 + sine(phase) * 0.2
        return sig * note_env * overall * 0.75

    return generate_samples(duration, gen)


def gen_checkpoint():
    """Bright fanfare, 300ms, ascending chord."""
    duration = 0.30
    # Quick 3-note ascending: C5 -> E5 -> G5 (as chord builds)

    def gen(t, i, total):
        progress = t / duration
        env = adsr_envelope(t, duration, attack=0.008, decay=0.04, sustain_level=0.6, release=0.1)

        sig = 0.0
        # Note 1: C5 — plays whole time
        sig += sine(TWO_PI * NOTES['C5'] * t) * 0.3
        # Note 2: E5 — enters at 30%
        if progress > 0.3:
            local_env = min((progress - 0.3) / 0.1, 1.0)
            sig += sine(TWO_PI * NOTES['E5'] * t) * 0.25 * local_env
        # Note 3: G5 — enters at 55%
        if progress > 0.55:
            local_env = min((progress - 0.55) / 0.1, 1.0)
            sig += sine(TWO_PI * NOTES['G5'] * t) * 0.25 * local_env
        # Sparkle on top
        sig += sine(TWO_PI * NOTES['C6'] * t) * 0.1 * max(0, progress - 0.7) / 0.3

        return sig * env * 0.9

    return generate_samples(duration, gen)


def gen_game_over():
    """Sad descend, 800ms, 400Hz->80Hz slow."""
    duration = 0.80

    def gen(t, i, total):
        progress = t / duration
        freq = exp_interp(400, 80, progress)
        phase = TWO_PI * freq * t
        env = adsr_envelope(t, duration, attack=0.02, decay=0.15, sustain_level=0.4, release=0.35)
        # Sad tone: slightly detuned pair
        sig = (triangle(phase) * 0.4 +
               triangle(phase * 1.005) * 0.3 +  # slight detune for sadness
               sine(phase * 0.5) * 0.2)
        # Slow tremolo
        trem = 0.7 + 0.3 * math.sin(TWO_PI * 4 * t)
        return sig * env * trem * 0.8

    return generate_samples(duration, gen)


def gen_menu_select():
    """Quick click, 30ms, 1000Hz square."""
    duration = 0.03

    def gen(t, i, total):
        phase = TWO_PI * 1000 * t
        env = quick_decay(t, duration, 2.0)
        sig = hard_square(phase) * 0.4 + sine(phase) * 0.3
        return sig * env * 0.7

    return generate_samples(duration, gen)


def gen_menu_hover():
    """Soft tick, 20ms, 800Hz sine."""
    duration = 0.02

    def gen(t, i, total):
        phase = TWO_PI * 800 * t
        env = quick_decay(t, duration, 1.5)
        sig = sine(phase) * 0.6 + sine(phase * 2) * 0.15
        return sig * env * 0.6

    return generate_samples(duration, gen)


# ──────────────────────────────────────────────
# UI SOUNDS
# ──────────────────────────────────────────────

def gen_button_tap():
    """Quick blip, 40ms. Satisfying button press."""
    duration = 0.04

    def gen(t, i, total):
        progress = t / duration
        freq = lerp(1200, 900, progress)
        phase = TWO_PI * freq * t
        env = quick_decay(t, duration, 2.5)
        sig = sine(phase) * 0.5 + hard_square(phase) * 0.2
        return sig * env * 0.7

    return generate_samples(duration, gen)


def gen_tab_switch():
    """Soft whoosh, 100ms."""
    duration = 0.10

    def gen(t, i, total):
        progress = t / duration
        freq = lerp(600, 400, progress)
        phase = TWO_PI * freq * t
        env = adsr_envelope(t, duration, attack=0.01, decay=0.02, sustain_level=0.4, release=0.05)
        tonal = sine(phase) * 0.3
        n = noise() * 0.25 * env
        return (tonal + n) * env * 0.6

    return generate_samples(duration, gen)


def gen_unlock():
    """Triumphant jingle, 600ms. Ascending bright arpeggio."""
    duration = 0.60
    # C5, E5, G5, C6, E6 — fast ascending, then ring
    note_freqs = [NOTES['C5'], NOTES['E5'], NOTES['G5'], NOTES['C6'], NOTES['E6']]
    arp_time = 0.35  # arpeggio takes 350ms
    ring_time = duration - arp_time

    def gen(t, i, total):
        sig = 0.0
        overall_env = adsr_envelope(t, duration, attack=0.005, decay=0.05, sustain_level=0.6, release=0.2)

        if t < arp_time:
            # Arpeggio phase
            note_dur = arp_time / len(note_freqs)
            note_idx = min(int(t / note_dur), len(note_freqs) - 1)
            local_t = t - note_idx * note_dur
            freq = note_freqs[note_idx]
            note_env = adsr_envelope(local_t, note_dur, attack=0.003, decay=0.02, sustain_level=0.6, release=0.02)
            phase = TWO_PI * freq * t
            sig = (pulse(phase, 0.25) * 0.4 + sine(phase * 2) * 0.2) * note_env
        else:
            # Ring/shimmer phase — hold final chord
            ring_t = t - arp_time
            ring_env = quick_decay(ring_t, ring_time, 1.5)
            # Play top 3 notes as chord
            for nf in note_freqs[-3:]:
                sig += sine(TWO_PI * nf * t) * 0.2 * ring_env
            # Sparkle
            sig += sine(TWO_PI * note_freqs[-1] * 2 * t) * 0.08 * ring_env

        return sig * overall_env * 0.85

    return generate_samples(duration, gen)


def gen_shake():
    """Rattle sound, 200ms. Quick bursts of noise."""
    duration = 0.20

    def gen(t, i, total):
        progress = t / duration
        env = adsr_envelope(t, duration, attack=0.005, decay=0.03, sustain_level=0.5, release=0.08)
        # Rattle: amplitude-modulated noise at ~40Hz
        rattle_mod = abs(math.sin(TWO_PI * 40 * t))
        # Add some tonal component for body
        tonal = sine(TWO_PI * 200 * t) * 0.15
        n = noise() * rattle_mod * 0.55
        return (n + tonal) * env * 0.75

    return generate_samples(duration, gen)


# ──────────────────────────────────────────────
# BACKGROUND MUSIC — 8-bit Chiptune Loop
# ──────────────────────────────────────────────

def gen_bgm_main():
    """
    8-second chiptune loop at ~140 BPM.
    Square wave melody + triangle bass + noise drums.
    Key of C major, energetic and catchy.
    """
    duration = 8.0  # 8 seconds
    bpm = 140
    beat_dur = 60.0 / bpm  # ~0.4286 seconds per beat
    sixteenth = beat_dur / 4.0

    total_samples = int(SAMPLE_RATE * duration)

    # ── Melody (square/pulse wave) ──
    # 32 sixteenth notes = 2 bars of 4/4
    # Using a catchy, Mega Man-inspired melody in C major
    melody_pattern = [
        # Bar 1: Energetic ascending phrase
        ('C5', 2), ('E5', 2), ('G5', 2), ('A5', 1), ('G5', 1),
        ('E5', 2), ('D5', 1), ('C5', 1), ('D5', 2), ('E5', 2),
        # Bar 2: Response phrase
        ('G5', 2), ('A5', 2), ('G5', 1), ('E5', 1), ('D5', 2),
        ('C5', 2), ('E5', 2), ('G5', 1), ('E5', 1), ('C5', 2),
        # Bar 3: Bridge / variation
        ('F5', 2), ('A5', 2), ('G5', 2), ('F5', 1), ('E5', 1),
        ('D5', 2), ('F5', 2), ('E5', 2), ('D5', 1), ('C5', 1),
        # Bar 4: Resolution
        ('E5', 2), ('G5', 2), ('C6', 3), ('B5', 1),
        ('A5', 2), ('G5', 2), ('E5', 2), ('C5', 2),
    ]

    # ── Bass (triangle wave) ──
    # Root notes following chord progression, one per beat
    # C - C - Am - Am - F - F - G - G  (classic platformer progression)
    bass_pattern = [
        # Bar 1: C major
        ('C3', 4), ('C3', 4), ('C3', 4), ('C3', 4),
        # Bar 2: A minor
        ('A3', 4), ('A3', 4), ('A3', 4), ('A3', 4),
        # Bar 3: F major
        ('F3', 4), ('F3', 4), ('F3', 4), ('F3', 4),
        # Bar 4: G major -> back to C
        ('G3', 4), ('G3', 4), ('G3', 4), ('G3', 4),
    ]

    # ── Drums (noise) ──
    # Kick on 1,3 | Snare on 2,4 | Hi-hat on every 8th
    # Per beat (4 sixteenths): K=kick, S=snare, H=hihat, .=rest
    # Pattern per bar (16 sixteenths):
    # K.H. S.H. K.H. S.H.
    drum_pattern = [
        'K', '.', 'H', '.',  # Beat 1
        'S', '.', 'H', '.',  # Beat 2
        'K', '.', 'H', '.',  # Beat 3
        'S', '.', 'H', '.',  # Beat 4
    ] * 4  # 4 bars

    # ── Build melody track ──
    melody_samples = [0.0] * total_samples
    pos = 0  # position in sixteenths
    phase_acc = 0.0
    prev_freq = 0.0

    for note_name, length in melody_pattern:
        start_time = pos * sixteenth
        end_time = (pos + length) * sixteenth
        start_i = int(start_time * SAMPLE_RATE)
        end_i = min(int(end_time * SAMPLE_RATE), total_samples)
        freq = NOTES.get(note_name, 440.0)
        note_duration = (end_time - start_time)

        for idx in range(start_i, end_i):
            t = (idx - start_i) / SAMPLE_RATE
            local_progress = t / note_duration if note_duration > 0 else 0
            # Note envelope
            env = adsr_envelope(t, note_duration, attack=0.005, decay=0.02, sustain_level=0.65, release=0.015)
            phase = TWO_PI * freq * (idx / SAMPLE_RATE)
            # 25% pulse for that NES lead sound
            sig = pulse(phase, 0.25) * 0.45
            # Add slight chorus with detuned oscillator
            sig += pulse(phase * 1.003, 0.25) * 0.15
            melody_samples[idx] = sig * env

        pos += length

    # ── Build bass track ──
    bass_samples = [0.0] * total_samples
    pos = 0

    for note_name, length in bass_pattern:
        start_time = pos * sixteenth
        end_time = (pos + length) * sixteenth
        start_i = int(start_time * SAMPLE_RATE)
        end_i = min(int(end_time * SAMPLE_RATE), total_samples)
        freq = NOTES.get(note_name, 130.81)
        note_duration = end_time - start_time

        for idx in range(start_i, end_i):
            t = (idx - start_i) / SAMPLE_RATE
            env = adsr_envelope(t, note_duration, attack=0.008, decay=0.04, sustain_level=0.55, release=0.03)
            phase = TWO_PI * freq * (idx / SAMPLE_RATE)
            sig = triangle(phase) * 0.55
            bass_samples[idx] = sig * env

        pos += length

    # ── Build drum track ──
    drum_samples = [0.0] * total_samples

    for step_idx, hit in enumerate(drum_pattern):
        if hit == '.':
            continue
        start_time = step_idx * sixteenth
        start_i = int(start_time * SAMPLE_RATE)

        if hit == 'K':
            # Kick: low sine sweep 150->50Hz, 80ms
            kick_dur = 0.08
            end_i = min(start_i + int(kick_dur * SAMPLE_RATE), total_samples)
            for idx in range(start_i, end_i):
                t = (idx - start_i) / SAMPLE_RATE
                prog = t / kick_dur
                freq = lerp(150, 50, prog)
                env = quick_decay(t, kick_dur, 3.0)
                phase = TWO_PI * freq * t
                drum_samples[idx] += sine(phase) * 0.55 * env

        elif hit == 'S':
            # Snare: noise + tone at 200Hz, 80ms
            snare_dur = 0.08
            end_i = min(start_i + int(snare_dur * SAMPLE_RATE), total_samples)
            for idx in range(start_i, end_i):
                t = (idx - start_i) / SAMPLE_RATE
                env_n = quick_decay(t, snare_dur, 2.0)
                env_t = quick_decay(t, snare_dur, 4.0)
                phase = TWO_PI * 200 * t
                sig = noise() * 0.35 * env_n + triangle(phase) * 0.2 * env_t
                drum_samples[idx] += sig

        elif hit == 'H':
            # Hi-hat: filtered noise, 30ms
            hh_dur = 0.03
            end_i = min(start_i + int(hh_dur * SAMPLE_RATE), total_samples)
            for idx in range(start_i, end_i):
                t = (idx - start_i) / SAMPLE_RATE
                env = quick_decay(t, hh_dur, 3.5)
                drum_samples[idx] += noise() * 0.18 * env

    # ── Add harmony/chord pad (subtle) ──
    harmony_samples = [0.0] * total_samples
    # Chord progression: C, Am, F, G — each 2 beats (8 sixteenths)
    chords = [
        ([NOTES['C4'], NOTES['E4'], NOTES['G4']], 16),   # C major - bar 1
        ([NOTES['A3'], NOTES['C4'], NOTES['E4']], 16),   # A minor - bar 2
        ([NOTES['F3'], NOTES['A3'], NOTES['C4']], 16),   # F major - bar 3
        ([NOTES['G3'], NOTES['B3'], NOTES['D4']], 16),   # G major - bar 4
    ]

    pos = 0
    for chord_notes, length in chords:
        start_time = pos * sixteenth
        end_time = (pos + length) * sixteenth
        start_i = int(start_time * SAMPLE_RATE)
        end_i = min(int(end_time * SAMPLE_RATE), total_samples)
        note_duration = end_time - start_time

        for idx in range(start_i, end_i):
            t = (idx - start_i) / SAMPLE_RATE
            env = adsr_envelope(t, note_duration, attack=0.05, decay=0.1, sustain_level=0.3, release=0.08)
            sig = 0.0
            for cn in chord_notes:
                phase = TWO_PI * cn * (idx / SAMPLE_RATE)
                sig += pulse(phase, 0.125) * 0.08  # Very quiet 12.5% pulse
            harmony_samples[idx] = sig * env

        pos += length

    # ── Mix all tracks ──
    mixed = mix_tracks(
        apply_volume(melody_samples, 0.55),
        apply_volume(bass_samples, 0.50),
        apply_volume(drum_samples, 0.60),
        apply_volume(harmony_samples, 0.35),
    )

    # Apply subtle lowpass to soften harsh edges
    mixed = apply_lowpass(mixed, 8000)

    # Final master volume
    mixed = apply_volume(mixed, 0.85)

    return mixed


# ──────────────────────────────────────────────
# MAIN — Generate All Sounds
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TapToons v3.0 — Sound Effects Generator")
    print("  Sample Rate: 22050Hz | 16-bit | Mono")
    print("=" * 60)

    sounds = {}

    # ── Game SFX ──
    sfx_generators = {
        'jump': gen_jump,
        'double_jump': gen_double_jump,
        'land': gen_land,
        'coin_collect': gen_coin_collect,
        'ring_collect': gen_ring_collect,
        'enemy_stomp': gen_enemy_stomp,
        'hurt': gen_hurt,
        'death': gen_death,
        'speed_boost': gen_speed_boost,
        'power_up': gen_power_up,
        'checkpoint': gen_checkpoint,
        'game_over': gen_game_over,
        'menu_select': gen_menu_select,
        'menu_hover': gen_menu_hover,
    }

    print("\n[1/3] Generating Game SFX...")
    for name, gen_fn in sfx_generators.items():
        print(f"  -> {name}...", end=" ", flush=True)
        samples = gen_fn()
        # Apply subtle reverb to most sounds
        if name not in ('menu_select', 'menu_hover', 'land'):
            samples = apply_reverb(samples, delay_ms=25, decay=0.2, taps=2)
        wav_bytes = samples_to_wav(samples)
        sounds[name] = wav_to_data_uri(wav_bytes)
        kb = len(wav_bytes) / 1024
        print(f"OK ({len(samples)} samples, {kb:.1f}KB)")

    # ── UI Sounds ──
    ui_generators = {
        'button_tap': gen_button_tap,
        'tab_switch': gen_tab_switch,
        'unlock': gen_unlock,
        'shake': gen_shake,
    }

    print("\n[2/3] Generating UI Sounds...")
    for name, gen_fn in ui_generators.items():
        print(f"  -> {name}...", end=" ", flush=True)
        samples = gen_fn()
        if name == 'unlock':
            samples = apply_reverb(samples, delay_ms=35, decay=0.25, taps=3)
        wav_bytes = samples_to_wav(samples)
        sounds[name] = wav_to_data_uri(wav_bytes)
        kb = len(wav_bytes) / 1024
        print(f"OK ({len(samples)} samples, {kb:.1f}KB)")

    # ── Background Music ──
    print("\n[3/3] Generating Background Music (8-bit chiptune, 8 seconds)...")
    print("  -> bgm_main... (this takes a moment)", flush=True)
    samples = gen_bgm_main()
    wav_bytes = samples_to_wav(samples)
    sounds['bgm_main'] = wav_to_data_uri(wav_bytes)
    kb = len(wav_bytes) / 1024
    print(f"  -> bgm_main OK ({len(samples)} samples, {kb:.1f}KB)")

    # ── Write JSON ──
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds.json')
    print(f"\nWriting {len(sounds)} sounds to {output_path}...")

    output = {
        '_meta': {
            'generator': 'TapToons v3.0 Sound Generator',
            'sample_rate': SAMPLE_RATE,
            'bit_depth': 16,
            'channels': 1,
            'format': 'base64 WAV data URI',
            'total_sounds': len(sounds),
            'categories': {
                'game_sfx': list(sfx_generators.keys()),
                'ui': list(ui_generators.keys()),
                'music': ['bgm_main'],
            }
        },
        'sounds': sounds,
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    total_size = os.path.getsize(output_path)
    print(f"\nDone! {total_size / 1024:.1f}KB total ({total_size / (1024 * 1024):.2f}MB)")
    print(f"Sounds: {len(sounds)}")
    print("\n" + "=" * 60)
    print("  All sounds generated successfully!")
    print("  Usage in JS:")
    print("    const data = await fetch('sounds.json').then(r => r.json());")
    print("    const audio = new Audio(data.sounds.jump);")
    print("    audio.play();")
    print("=" * 60)


if __name__ == '__main__':
    main()
