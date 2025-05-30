import numpy as np
from scipy import signal as sig


def z_score_normalize(signal):

    mean_val = np.mean(signal)
    std_val = np.std(signal)
    normalized_signal = (signal - mean_val) / std_val
    return normalized_signal


def min_max_normalize(signal):
    min_val = np.min(signal)
    max_val = np.max(signal)
    normalized_signal = (signal - min_val) / (max_val - min_val)
    return normalized_signal


def calculate_conv(
    N: tuple,
    S,
    t0: float,
    M: int,
    spectr,
    y_col,
    x_min,
    x_max,
):
    Nx, Ny = N
    A = []
    W = sig.find_peaks(spectr[y_col][int(x_min):int(x_max)])[0]
    for i in W:
        A.append(spectr[y_col][int(x_min):int(x_max):1][i])
    W = np.where(spectr[y_col] == max(A))[0][0]
    t_end = t0 + M * 2 * np.pi / W
    t = np.arange(t0, t_end, 0.00004)
    Sm = max(abs(S[t0:t.shape[0]]))
    X_i = 0.5 * (Nx * S[t0:t.shape[0]] * np.cos(2 * np.pi * W * t) / Sm + Nx)
    Y_i = 0.5 * (Ny * S[t0:t.shape[0]] * np.sin(2 * np.pi * W * t) / Sm + Ny)
    return X_i, Y_i, W, t_end


def modulate_signal(spectr, y_col="СКЗ, мВ", x_min=0, x_max=12500):
    x_min = int(x_min)
    x_max = int(x_max)
    modul_signal = []
    A = []
    phi_0 = np.random.normal(0, np.pi * 2)
    W = sig.find_peaks(spectr[y_col][x_min:x_max])[0]
    for i in W:
        A.append(spectr[y_col][x_min:x_max:1][i])
    A = np.array(A)
    W = np.array(W)
    noise = spectr[y_col][x_min:x_max:1].max() * 0.1
    denominator = np.sum(A)
    for t in np.arange(0, 6, 0.00004):  #signal['Время,с']:
        numerator = np.sum(
            A[1:] * np.sin(W[1:] * 2 * np.pi * t + phi_0)) + noise
        modul_signal.append(numerator / denominator)
    return np.array(modul_signal)
