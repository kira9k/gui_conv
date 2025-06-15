import numpy as np
from scipy import signal as sig


def z_score_normalize(signal: np.ndarray) -> np.ndarray:
    """
    Z-нормализация сигнала: (x - mean) / std
    :param signal: исходный сигнал
    :return: нормализованный сигнал
    """
    mean_val = np.mean(signal)
    std_val = np.std(signal)
    normalized_signal = (signal - mean_val) / std_val
    return normalized_signal


def min_max_normalize(signal: np.ndarray) -> np.ndarray:
    """
    Нормализация сигнала по min-max: (x - min) / (max - min)
    :param signal: исходный сигнал
    :return: нормализованный сигнал
    """
    min_val = np.min(signal)
    max_val = np.max(signal)
    normalized_signal = (signal - min_val) / (max_val - min_val)
    return normalized_signal


def calculate_conv(
    N: tuple,
    S: np.ndarray,
    t0: float,
    M: int,
    spectr,
    y_col: str,
    x_min: float,
    x_max: float,
    force_W: float = None,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """
    Вычисляет координаты X_i, Y_i для траектории по сигналу S и спектру.
    :param N: кортеж коэффициентов (Nx, Ny)
    :param S: сигнал (numpy array)
    :param t0: начальное время
    :param M: количество периодов
    :param spectr: DataFrame спектра
    :param y_col: имя столбца спектра
    :param x_min: минимальная частота
    :param x_max: максимальная частота
    :param force_W: если задано — использовать эту частоту вместо поиска по спектру
    :return: X_i, Y_i, W, t_end
    """
    # --- Проверка входных данных ---
    if spectr is None:
        raise ValueError("Спектр не загружен (None)")
    if y_col not in spectr.columns:
        raise ValueError(f"Столбец '{y_col}' не найден в спектре")

    Nx, Ny = N
    A = []
    W_peaks = sig.find_peaks(spectr[y_col][int(x_min):int(x_max)])[0]
    for i in W_peaks:
        A.append(spectr[y_col][int(x_min):int(x_max):1][i])
    if force_W is not None:
        W = float(force_W)
    else:
        W = np.where(spectr[y_col] == max(A))[0][0]
    t0_index = int(t0 / 0.00004)
    t_end = np.round(t0 + M * 2 * np.pi / W, 6)
    t_end_index = int(t_end / 0.00004)
    t = np.arange(t0, t_end, 0.00004)
    if t_end_index - t0_index != t.shape[0]:
        t_end_index += 1
    Sm = max(abs(S[t0:t.shape[0]]))
    X_i = 0.5 * (
        Nx * S[t0_index:t_end_index] * np.cos(2 * np.pi * W * t) / Sm + Nx)
    Y_i = 0.5 * (
        Ny * S[t0_index:t_end_index] * np.sin(2 * np.pi * W * t) / Sm + Ny)
    return X_i, Y_i, W, t_end


def modulate_signal(spectr,
                    y_col: str = "СКЗ, мВ",
                    x_min: float = 0,
                    x_max: float = 12500) -> np.ndarray:
    """
    Модулирует сигнал на основе спектра.
    :param spectr: DataFrame спектра
    :param y_col: имя столбца спектра
    :param x_min: минимальная частота
    :param x_max: максимальная частота
    :return: numpy array смоделированного сигнала
    """
    x_min = int(x_min)
    x_max = int(x_max)
    modul_signal = []
    A = []
    W = sig.find_peaks(spectr[y_col][x_min:x_max])[0]
    phi_0_list = []
    for i in W:
        phi_0 = np.random.normal(0, np.pi * 2)
        phi_0_list.append(phi_0)
        A.append(spectr[y_col][x_min:x_max:1][i])
    A = np.array(A)
    W = np.array(W)
    denominator = np.sum(A)
    # Генерируем белый шум на каждом шаге t с амплитудой A0
    A0 = spectr[y_col][x_min:x_max:1].mean() * 0.01
    for t in np.arange(0, 6, 0.00004):
        noise = np.random.normal(0, A0)  # белый шум с амплитудой A0
        numerator = np.sum(
            A[1:] * np.sin(W[1:] * 2 * np.pi * t + phi_0_list[1:]))  #+ noise
        modul_signal.append(numerator / denominator)
    return np.array(modul_signal)
