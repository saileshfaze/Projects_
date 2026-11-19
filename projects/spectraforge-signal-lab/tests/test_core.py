import math
import pytest
from spectraforge.core import fft, hann, spectrum, dominant_peaks, generate_signal, detect_anomalies

def test_fft_impulse(): assert fft([1, 0, 0, 0]) == [1, 1, 1, 1]
def test_fft_dc(): assert fft([2, 2, 2, 2]) == [8, 0, 0, 0]
def test_fft_invalid():
    with pytest.raises(ValueError): fft([1, 2, 3])
def test_fft_empty():
    with pytest.raises(ValueError): fft([])
def test_hann_edges():
    v = hann(8); assert abs(v[0]) < 1e-12 and abs(v[-1]) < 1e-12
def test_hann_invalid():
    with pytest.raises(ValueError): hann(1)
def test_peak_frequency():
    signal = generate_signal(256, 256, [(20, 2)], seed=1)
    peak = dominant_peaks(signal, 256)[0]
    assert peak.frequency_hz == 20
    assert abs(peak.amplitude - 2) < .02
def test_rectangular_amplitude():
    signal = generate_signal(128, 128, [(10, 1.5)])
    peak = dominant_peaks(signal, 128, window="rectangular")[0]
    assert peak.frequency_hz == 10 and abs(peak.amplitude - 1.5) < 1e-9
def test_deterministic(): assert generate_signal(32, 64, [(4, 1)], .1, 42) == generate_signal(32, 64, [(4, 1)], .1, 42)
def test_different_seeds(): assert generate_signal(32, 64, [], .1, 1) != generate_signal(32, 64, [], .1, 2)
def test_nyquist():
    with pytest.raises(ValueError): generate_signal(32, 64, [(32, 1)])
def test_negative_noise():
    with pytest.raises(ValueError): generate_signal(32, 64, [], -1)
def test_spectrum_nonfinite():
    with pytest.raises(ValueError): spectrum([float("nan"), 1, 2, 3], 4)
def test_bad_window():
    with pytest.raises(ValueError): spectrum([1, 2, 3, 4], 4, "unknown")
def test_bad_rate():
    with pytest.raises(ValueError): spectrum([1, 2, 3, 4], 0)
def test_bad_length():
    with pytest.raises(ValueError): spectrum([1, 2, 3], 4)
def test_bad_count():
    with pytest.raises(ValueError): dominant_peaks([1, 2, 3, 4], 4, 0)
def test_anomaly(): assert 20 in detect_anomalies([0.0] * 20 + [10.0], window=8)
def test_no_anomaly(): assert detect_anomalies([0.0] * 50) == []
def test_anomaly_bad_window():
    with pytest.raises(ValueError): detect_anomalies([1, 2, 3], 1)
def test_anomaly_bad_threshold():
    with pytest.raises(ValueError): detect_anomalies([1, 2, 3], 2, 0)
def test_dc_spectrum(): assert spectrum([3.0] * 8, 8, "rectangular")[0].amplitude == 3
