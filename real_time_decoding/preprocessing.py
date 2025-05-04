from scipy import signal
import numpy as np

def butter_highpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high')
    return signal.filtfilt(b, a, data)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low')
    return signal.filtfilt(b, a, data)

def butter_notch_filter(data, notch_freq, fs, order=4):
    nyq = 0.5 * fs
    low = (notch_freq - 1) / nyq
    high = (notch_freq + 1) / nyq
    b, a = signal.butter(order, [low, high], btype='bandstop')
    return signal.filtfilt(b, a, data)

def apply_eeg_preprocessing(eeg_chunk, fs=250, hp_cutoff=1, lp_cutoff=10, notch_freqs=[50, 60]):
    eeg = eeg_chunk.copy()
    eeg -= np.mean(eeg, axis=0)
    for ch in range(eeg.shape[1]):
        eeg[:, ch] = butter_highpass_filter(eeg[:, ch], hp_cutoff, fs)
        eeg[:, ch] = butter_lowpass_filter(eeg[:, ch], lp_cutoff, fs)
        for nf in notch_freqs:
            eeg[:, ch] = butter_notch_filter(eeg[:, ch], nf, fs)
    return eeg