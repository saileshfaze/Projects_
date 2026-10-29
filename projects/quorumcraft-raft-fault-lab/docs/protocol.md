# Protocol walkthrough

1. A follower starts an election when its seeded deadline expires. It increments its term, votes for itself and sends `vote_request` with last-log term and index.
2. A follower grants a vote only if the candidate's term is current, the follower has not voted for someone else and the candidate log is at least as up to date.
3. A candidate with a majority becomes leader and initializes each follower's `next_index` and `match_index`.
4. The leader sends `append_request` messages with `(prev_index, prev_term)`, a suffix of entries and its commit index. Followers reject mismatching prefixes and truncate conflicting uncommitted suffixes.
5. Successful replies advance the leader's match index. The leader advances its commit index only for entries from its own term replicated on a majority; earlier entries may be committed as part of that prefix.
6. Each node applies committed commands in order, deduplicating request identifiers. Followers learn commit progress through subsequent AppendEntries messages.
7. Higher-term messages cause a node to step down. Partitions can leave a stale leader unable to commit, while a majority elects a replacement.

**Non-goals:** snapshot installation, membership changes, read leases, pre-vote, production RPC retries and durable disk protocols. No formal verification or production consensus guarantees are claimed.
