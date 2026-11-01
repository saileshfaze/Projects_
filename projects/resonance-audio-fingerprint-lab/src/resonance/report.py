"""Deterministic text/HTML-safe SVG spectrogram and summary reports."""
from __future__ import annotations
from html import escape
import json
import numpy as np
from .dsp import log_mel, extract_features
from .waveio import Audio


def spectrogram_svg(audio: Audio, width: int = 900, height: int = 340) -> str:
    if width < 100 or height < 100:
        raise ValueError("canvas too small")
    mel = log_mel(audio.samples, audio.sample_rate)
    if not len(mel):
        raise ValueError("empty audio")
    # Subsample for bounded output size, retaining original mel-band order.
    mel = mel[::max(1, int(np.ceil(len(mel) / 160)))]
    maxval = max(float(np.max(mel)), 1e-9)
    plotw, ploth = width-100, height-70
    cells = []
    for ti, row in enumerate(mel):
        for band, value in enumerate(row):
            q = max(0, min(255, round(255*float(value)/maxval)))
            x = 65 + ti*plotw/len(mel)
            y = 20 + (len(row)-band-1)*ploth/len(row)
            cells.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{plotw/len(mel)+0.15:.2f}" height="{ploth/len(row)+0.15:.2f}" fill="rgb({q//3},{q//2},{q})"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<rect width="100%" height="100%" fill="#111827"/>'
            + "".join(cells) + '<text x="65" y="' + str(height-14) + '" fill="#ddd" font-size="13">Time →</text>'
            + '<text x="8" y="20" fill="#ddd" font-size="12">Mel bands ↑</text></svg>')


def feature_report(audio: Audio, label: str = "synthetic") -> str:
    return json.dumps({"label": label, "features": extract_features(audio).to_dict()}, indent=2, sort_keys=True)
