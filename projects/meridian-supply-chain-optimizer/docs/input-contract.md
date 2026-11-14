# JSON contract

`supply`: object mapping warehouse identifiers to nonnegative integer units.
`demand`: object mapping store identifiers to nonnegative integer units.
`routes`: list of `{source,destination,capacity,unit_cost}` with unique endpoints and nonnegative integer capacities/costs. Identifiers must exist in the corresponding supply/demand maps. Output records shipped quantities and unmet demand by store. All quantities are synthetic.
