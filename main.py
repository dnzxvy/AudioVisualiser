import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from matplotlib.animation import FuncAnimation
filename = r"C:\Users\ntuka\Downloads\protected instrumental.mp3"
y, sr = librosa.load(filename, sr=None, mono=True)

# run beat tracker

tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
print(type(tempo), tempo)
tempo_value = tempo[0]

print('Estimated tempo: {:.2f} beats per minute'.format(tempo_value))

# convert the frame indicies of beat events into timestamps

beat_times = librosa.frames_to_time(beat_frames, sr=sr)

print(beat_times)
fig, ax = plt.subplots()

librosa.display.waveshow(y, sr=sr, ax=ax)
ax.set(title='Envelope view, stereo')

plt.show()

# Seperating sound into chunks(frames)

samples_per_frame = 2048
hop_size = samples_per_frame // 2
samples_total = len(y)
samples_wrote = 0


#rms track amplitude
rms = librosa.feature.rms(y=y, frame_length=samples_per_frame, hop_length=hop_size)[0]


# Frequency bands in Hz
bands = {
    "bass": (20, 250),
    "low_mids": (250, 500),
    "mids": (500, 2000),
    "high_mids": (2000, 6000),
    "treble": (6000, 20000)
}
frame_idx = 0
fft_magnitudes = []
while samples_wrote < samples_total:
    if samples_per_frame > (samples_total - samples_wrote):
        samples_per_frame = samples_total - samples_wrote

    #get current frame
    block = y[samples_wrote : samples_wrote + samples_per_frame]
    fft_result = np.fft.rfft(block)
    magnitude = np.abs(fft_result)
    fft_magnitudes.append(magnitude)
    samples_wrote += hop_size
    frame_idx += 1

    print(magnitude[:10])

# Animated matplotlib figure
fig, ax = plt.subplots(figsize=(8,6))
plt.axis('off')
bar_colors = ['red', 'orange', 'green', 'blue', 'purple']
bars = ax.bar(range(len(bands)), [0]*len(bands), color=bar_colors)
circle = plt.Circle((2, 5), 0, color='yellow', alpha=0.5)
ax.add_patch(circle)
ax.set_xlim(-1, len(bands))
ax.set_ylim(-1, 10)

# Animation Function
def update(frame):
    magnitude = fft_magnitudes[frame]
    band_values = []

    # Mapping frequency Bands

    for band_name, (f_low, f_high) in bands.items():
        start_bin = int(np.floor(f_low * samples_per_frame / sr))
        end_bin = min(int(np.ceil(f_high * samples_per_frame / sr)), len(magnitude)-1)
        # converts frequency in Hz to fft bin indices. because fft
        # is indexed via bins. np.floor ensures the start bin is rounded down
        # np.ceil ensures end bin covers upper limit. E.g Bass bin:
        #f_low = 20Hz, f_high = 250hz, spf = 2048, sr (sample rate) = 44100
        # start_bin = np.floor(20 x 2048/44100) = 0. end_bin = np.ceil
        #(250 x 2048/44100) = 12. this was derived from fft bin index formula
        band_values.append(np.mean(magnitude[start_bin+1]) * 10)

        # Update bars
        for bar, value in zip(bars, band_values):
            bar.set_height(value)
        circle.radius = rms[frame]*50
        return bars, circle


        # takes all fft magnitudes in the specific bin range and compute average
        #then stores in dictionary for that frequency band name.



        print(band_values)
    amplitude_rms_value = rms[frame_idx]
    print(f"RMS: {amplitude_rms_value:.4f}, Bands: {band_values}")
ani = FuncAnimation(fig, update, frames=len(rms), interval=30, blit=False)
plt.show()



