# Assumptions and limitations

- Input is short (<=120 seconds), local integer PCM WAV; compressed formats are out of scope.
- The default sample rate for synthetic audio is 16 kHz. Other supported rates are linearly interpolated for fingerprinting.
- Audio clips may be copyrighted or private. The included WAV fixtures are generated mathematically and contain no human recordings.
- No supervised training, real-world accuracy claim, or forensic validation has been performed.
- Alignment votes indicate a possible match, not identity, originality, or authorship.
- Quiet recordings, dense noise, pitch shifts, speed changes, codec artifacts, and stereo phase cancellation can degrade results.
- No production performance SLA; SQLite is intended for small local collections.
- The spectrogram visualization is a derived log-mel heatmap, not a spectrographic measurement standard.
