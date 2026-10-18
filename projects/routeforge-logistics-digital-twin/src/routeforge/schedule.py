"""Constraint-aware route evaluator. Time windows constrain service start."""
from .domain import Problem, Vehicle
from .geometry import haversine_km, travel_minutes

def evaluate_route(problem: Problem, vehicle: Vehicle, job_ids: list[str]) -> dict | None:
    jobs = {job.id: job for job in problem.jobs}
    if len(set(job_ids)) != len(job_ids) or any(j not in jobs for j in job_ids):
        raise ValueError("Unknown or duplicated job in route")
    if not job_ids:
        return {"vehicle_id": vehicle.id, "jobs": [], "stops": [], "load": 0.0,
                "distance_km": 0.0, "duration_min": 0, "cost": 0.0, "emissions_kg": 0.0}
    load = sum(jobs[j].demand for j in job_ids)
    if load > vehicle.capacity + 1e-9:
        return None
    t = vehicle.shift_start
    lat, lon = problem.depot.lat, problem.depot.lon
    km_total = 0.0
    stops = []
    for job_id in job_ids:
        job = jobs[job_id]
        km = haversine_km(lat, lon, job.lat, job.lon)
        km_total += km * 1.35
        arrival = t + travel_minutes(km, vehicle.speed_kmh)
        start = max(arrival, job.earliest)
        if start > job.latest:
            return None
        t = start + job.service_min
        stops.append({"job_id": job.id, "arrival_min": arrival,
                      "service_start_min": start, "depart_min": t})
        lat, lon = job.lat, job.lon
    home_km = haversine_km(lat, lon, problem.depot.lat, problem.depot.lon)
    km_total += home_km * 1.35
    t += travel_minutes(home_km, vehicle.speed_kmh)
    if t > vehicle.shift_end or km_total > vehicle.max_km + 1e-9:
        return None
    return {"vehicle_id": vehicle.id, "jobs": list(job_ids), "stops": stops,
            "load": round(load, 3), "distance_km": round(km_total, 3),
            "duration_min": t - vehicle.shift_start,
            "cost": round(vehicle.fixed_cost + km_total * vehicle.cost_per_km, 2),
            "emissions_kg": round(km_total * vehicle.emissions_g_per_km / 1000, 3)}
