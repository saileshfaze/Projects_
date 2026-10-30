# Continuous-time separation mathematics

For each pair of overlapping flight-plan segments, let `p` be their initial relative
horizontal position in metres and `v` their relative horizontal velocity in metres/second.
The squared separation at local time `u` is `||p + u v||²`. The conflict condition is
`||p + u v||² < (H · 1852)²`, where H is the horizontal threshold in nautical miles.
Expand to `a u² + b u + c < 0` with `a=v·v`, `b=2 p·v`, and
`c=p·p-(H·1852)²`. For nonzero relative velocity, solve roots with the discriminant;
clamp the open interval between roots to the overlapping segment interval.

Vertical separation uses `|z + u vz| < V · 0.3048` for threshold V in feet. This
is a linear interval inequality. Intersect the two time windows; a positive-length
intersection is a conflict. Adjacent windows are merged per pair. The reported closest
horizontal approach is the constrained minimizer `clip(-p·v/(v·v), entry, exit)`.

**Important:** The minimum horizontal distance is calculated *inside* the detected conflict
window, not necessarily at the minimum 3D distance. Time is in seconds from a synthetic
scenario origin, not an absolute UTC timestamp. Equal-to-threshold points alone do not
count as positive-duration conflicts.
