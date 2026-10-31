# Architecture

Pipeline: SQL text → lexer/parser → typed AST → catalog validation → access-path selection → left-deep dynamic-programming optimizer → physical plan → optional reference executor → explain/DOT/JSON.

DP states are subsets of aliases; each state keeps the lowest estimated-cost left-deep plan. States expand by adding one relation connected by an equijoin unless cross joins are enabled. Physical alternatives are nested loop, hash, and modeled indexed nested loop. A fixed input-order nested-loop baseline is used to check result equivalence.

The executor materializes Python dictionaries; hash join builds a temporary hash table and modeled indexed nested-loop is executed as nested loops. This separation deliberately exposes the difference between estimated plan cost and actual Python execution.
