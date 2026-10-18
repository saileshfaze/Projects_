# Optimization and uncertainty model

## Feasibility

A route begins at the depot at vehicle shift start. For each job, road-adjusted distance is `1.35 × haversine_km`. Travel time is `ceil(60 × adjusted_km / speed_kmh)`. Service begins at the later of arrival and earliest time. If service start exceeds the job's latest time, the candidate route is infeasible. After service, the vehicle must return to the depot by shift end and within max route distance. Total job demand must not exceed capacity.

## Construction

Jobs are ordered by descending priority, then ascending latest service time and ID. For each job, every insertion position in every vehicle's current route is evaluated. The minimum **incremental cost** feasible move is chosen. Jobs without any feasible insertion are explicitly reported as unserved. This greedy method can miss feasible assignments; that limitation is intentional and documented.

## Local improvement

Up to five best-improvement inter-vehicle relocate passes are attempted. Each move removes one served job from its current vehicle and inserts it into another route. Only strictly cost-reducing feasible moves are applied. The method never intentionally removes a served job.

## Baseline

The first-fit baseline processes input-order jobs and appends each to the first vehicle whose route remains feasible. Comparing costs is meaningful only when both plans serve the same number of jobs.

## Monte Carlo

For each seeded trial, demand is multiplied by a uniform random factor in `[1-demand_jitter, 1+demand_jitter]`, and each vehicle's speed by a factor in `[1-speed_jitter, 1+speed_jitter]`. **Assignments and visit order stay fixed**. Feasibility rate is the proportion of trials satisfying every route. Cost percentiles exclude infeasible trials and must not be interpreted as unconditional expected operating cost.

This is a pedagogical uncertainty model, not calibrated forecast confidence.
