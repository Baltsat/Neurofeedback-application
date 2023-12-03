import numpy as np
from scipy.signal import welch

def process_eeg_data(eeg_data):
    # Define sampling rate and frequencies for alpha and beta waves
    sampling_rate = 256  # This is an example value; adjust based on your device's specs
    alpha_band = (8, 13)
    beta_band = (13, 30)

    # Apply Welch's method to estimate power spectral density
    freqs, psd = welch(eeg_data, sampling_rate, nperseg=4*sampling_rate)

    # Find power in alpha and beta bands
    alpha_power = psd[np.logical_and(freqs >= alpha_band[0], freqs <= alpha_band[1])].mean()
    beta_power = psd[np.logical_and(freqs >= beta_band[0], freqs <= beta_band[1])].mean()

    return alpha_power, beta_power




