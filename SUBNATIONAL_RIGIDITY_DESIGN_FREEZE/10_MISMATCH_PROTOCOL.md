# 10 — Mismatch protocol (frozen)

Baseline crop geography fixed at unit level (baseline shares). Climate at unit
centroid from NASA POWER monthly (T2M, PRECTOTCORR; cached under
data/raw/power_subnat/). Growing-season months per crop from MIRCA2000
condensed crop calendars for the unit's country (national calendar proxy —
documented limitation for large countries).

Primary: mismatch_T = mean over calendar crops of |Delta T| between
baseline-window and endline-window growing-season means (deg C).
Secondary: mismatch_P = |Delta log(precip)|.
Dominant-crop variant (sensitivity): restrict calendar to baseline argmax crop.
Coverage threshold: unit enters sample only if POWER series retrieved AND
MIRCA calendar exists for its country (frozen preregistered rule; no
leakage — endline outcomes never touch exposure construction).
