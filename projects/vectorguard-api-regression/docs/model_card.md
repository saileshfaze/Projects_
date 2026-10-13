# Drift signal card

## Default lexical score

Token and adjacent-token-bigram cosine similarity. It is deterministic, offline, and cheap. It does **not** understand semantic equivalence; paraphrases, word order, multilingual content, short strings and high-frequency boilerplate can produce misleading results. A 0.55 threshold is illustrative, not calibrated.

## Numeric signals

PSI compares smoothed proportions across baseline quantile bins. KS distance measures maximum separation of empirical cumulative distributions. Both are descriptive signals; neither is a p-value or a guaranteed detection threshold. Test on representative, adequately sized baseline/candidate samples.

## Optional embedding adapter

`app/semantic.py` supports a locally installed sentence-transformer model if `pip install -e '.[ml]'` is used and a local model directory is explicitly provided. No model weights are included. The default HTTP evaluation path uses lexical scoring only. Before production, validate candidate models on task-specific, consented evaluation sets and document licenses and error rates.
