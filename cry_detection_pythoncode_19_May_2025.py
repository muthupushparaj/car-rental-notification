
import os
import csv
import numpy as np
import soundfile as sf
import scipy.signal as signal

# Configuration (flatness filter removed)
FRAME_SIZE = 1024
HOP_SIZE = 512
BASE_TEO_THRESHOLD = 0.0015
#BASE_TEO_THRESHOLD = 0.0008
BASE_ZCR_THRESHOLD = 0.15
PITCH_MIN = 200
PITCH_MAX = 1000
SMOOTH_ALPHA = 0.6
PITCH_VARIANCE_WINDOW = 5
PITCH_VARIANCE_THRESHOLD = 15
MIN_CONSECUTIVE_FRAMES = 4

def compute_teager_energy(frame):
    return np.mean(frame[1:-1]**2 - frame[:-2]*frame[2:]) * 20

def compute_pitch_autocorrelation(frame, sr):
    min_lag = sr // PITCH_MAX
    max_lag = sr // PITCH_MIN
    best_lag = -1
    max_corr = 0
    for lag in range(min_lag, max_lag):
        corr = np.sum(frame[:-lag] * frame[lag:])
        if corr > max_corr:
            max_corr = corr
            best_lag = lag
    return sr / best_lag if best_lag > 0 else 0

def compute_zcr(frame):
    return np.mean(np.abs(np.diff(np.sign(frame)))) / 2

# Cry Detection
def detect_cries(file_path):
    y, sr = sf.read(file_path)
    if y.ndim > 1:
        y = y[:, 0]
    y = np.append(y[0], y[1:] - 0.97 * y[:-1])
    y = y / np.max(np.abs(y))
    sos = signal.butter(4, [300, 1300], btype='bandpass', fs=sr, output='sos')
    y_filtered = signal.sosfilt(sos, y)

    cry_flags = []
    smoothed_teo = 0
    pitch_window = []

    for i in range(0, len(y_filtered) - FRAME_SIZE, HOP_SIZE):
        frame = y_filtered[i:i + FRAME_SIZE]
        teo = compute_teager_energy(frame)
        zcr = compute_zcr(frame)
        pitch = compute_pitch_autocorrelation(frame, sr)
        smoothed_teo = teo if i == 0 else SMOOTH_ALPHA * teo + (1 - SMOOTH_ALPHA) * smoothed_teo

        pitch_window.append(pitch)
        if len(pitch_window) > PITCH_VARIANCE_WINDOW:
            pitch_window.pop(0)

        pitch_variance = np.std(pitch_window)

        is_cry = (
            smoothed_teo > BASE_TEO_THRESHOLD and
            zcr < BASE_ZCR_THRESHOLD and
            PITCH_MIN < pitch < PITCH_MAX and
            pitch_variance > PITCH_VARIANCE_THRESHOLD
        )

        cry_flags.append(1 if is_cry else 0)

    detected_times = []
    sr_step = HOP_SIZE / sr
    for idx in range(len(cry_flags)):
        if cry_flags[idx] == 1:
            count = sum(cry_flags[idx:idx + MIN_CONSECUTIVE_FRAMES])
            if count >= MIN_CONSECUTIVE_FRAMES:
                detected_times.append(round(idx * sr_step, 2))

    return detected_times

# Process labeled folders and write results to CSV
categories = [
    "Cry-Noise-NoMusic",
    "Cry-NoNoise-Music",
    "Cry-NoNoise-NoMusic",
    "NoCry-Noise-NoMusic",
    "NoCry-NoNoise-Music"
]

results = []
for folder in categories:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.lower().endswith(".ogg"):
            fpath = os.path.join(folder, fname)
            try:
                timestamps = detect_cries(fpath)
                results.append({
                    "Folder": folder,
                    "File": fname,
                    "Cry Detected": "Yes" if timestamps else "No",
                    "Timestamps": ", ".join(str(t) for t in timestamps)
                })
            except Exception as e:
                results.append({
                    "Folder": folder,
                    "File": fname,
                    "Cry Detected": "Error",
                    "Timestamps": str(e)
                })

# Write CSV
csv_path = "cry_detection_results.csv"
with open(csv_path, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["Folder", "File", "Cry Detected", "Timestamps"])
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {csv_path}")
