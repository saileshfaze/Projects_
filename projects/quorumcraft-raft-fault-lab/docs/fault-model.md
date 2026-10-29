# Fault model

Supported: packet delay in a configured positive integer interval; seeded independent packet loss; symmetric link partitions between two node sets; node crash and restart; in-flight packets dropped if a link is blocked or endpoint inactive at delivery.

Unsupported: Byzantine or malicious nodes, packet duplication, packet reordering beyond delay, corrupted payloads, disk persistence, resource starvation, dynamic membership, asymmetric partitions, external network interfaces, clock drift and wall-clock scheduling.

A partitioned minority may retain a stale leader role, but cannot commit new entries without majority acknowledgments. Once healed, a higher-term AppendEntries causes that node to step down. A crash preserves simulated persistent state in memory, so it is not a durability test.
