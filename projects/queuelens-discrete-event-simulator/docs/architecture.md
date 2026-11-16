# Architecture

Validate a scenario, sort arrivals by `(arrival,id)`, and process a heap of server completion events before each new arrival. A bounded FIFO waiting room accepts jobs when all servers are busy. Departures dispatch the next waiting job immediately. Event order is deterministic: departures precede arrivals at the same timestamp; simultaneous completions sort by server ID. Server busy-time and job timing are derived from the event log.
