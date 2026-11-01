# Algorithm notes

1. Decode bounded PCM WAV to mono floating point in [-1, 1].
2. Resample linearly to 16 kHz for fingerprint extraction (simple and deterministic, not high-fidelity resampling).
3. Compute 1024-sample Hann-windowed STFT frames with hop 256 (16 ms).
4. For each interior frame select up to four local frequency maxima above the frame's 90th percentile and a fixed noise floor.
5. Pair each peak with up to four following peaks separated by 1–12 frames.
6. Hash `(frequency_bin_a, frequency_bin_b, delta_frames)` to 64-bit BLAKE2s hex codes.
7. Index `(clip_id, code, frame)` and retrieve all candidate rows for codes in the query.
8. Vote on `reference_frame - query_frame`. Rank by the largest aligned vote bucket.

The `confidence` output is `aligned_votes / number_of_query_landmarks`; it is **not a probability** and may exceed one when duplicate hash occurrences vote multiple times. `offset_seconds` uses 16 kHz and a 256-sample hop. Exact WAV duplicates are detected separately with SHA-256.

Complexity is approximately O(T F log F) for the STFT plus O(P·fanout) fingerprinting, where P is the number of selected peaks. The naive SQLite inverted-index search can grow large for very common hash codes; production systems would impose posting-list limits, rarity weighting, and robust index sharding.
