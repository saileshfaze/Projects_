import json
import pytest
from resonance.report import spectrogram_svg, feature_report
from resonance.waveio import decode_wav

def test_svg(melody):
    svg=spectrogram_svg(decode_wav(melody))
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert svg.endswith("</svg>") and "<rect" in svg

def test_svg_deterministic(melody):
    audio=decode_wav(melody)
    assert spectrogram_svg(audio)==spectrogram_svg(audio)

def test_small_canvas(melody):
    with pytest.raises(ValueError): spectrogram_svg(decode_wav(melody), 20)

def test_json_report(melody):
    report=json.loads(feature_report(decode_wav(melody)))
    assert report["features"]["rms"]>0
