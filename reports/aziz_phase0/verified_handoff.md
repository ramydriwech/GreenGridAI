# GreenGrid AI — Aziz: Evaluation 1 handoff (verified executed v3)

**Source:** `notebooks/02_exploration_meteo_eco2mix_aziz.ipynb` uploaded 1 Nov 2026. All listed figures and metrics come from the notebook's stored outputs, not independently rerun API requests.

## What works
- 8 French cities, hourly ERA5 observations for 2024: **70,272 city-hour records**.
- RTE data: **35,136 exported records**, aggregated to **8,784 UTC hours**.
- Joined RTE + eight-city weather data: **8,784 hours**, with **8,783 non-null pairs** for the main scatterplots.
- Exploratory correlations: temperature versus demand **r = −0.575**; mean eight-city wind versus generation-based CO2 intensity **r = −0.007**.
- Seasonal relationships vary: January **−0.604**; June **+0.641**; July **+0.720**; August **+0.714**.
- Wind versus actual wind electricity generation **r = +0.861**; wind generation versus RTE production-based carbon intensity **r = +0.022**.
- Archived weather fixed-lead pilot, Paris 1–7 Oct 2024, 168 hourly pairs: temperature MAE **0.950 °C**, RMSE **1.193 °C**; 100m wind MAE **4.138 km/h**, RMSE **5.197 km/h**. (Comparison target is ERA5 reanalysis, not direct instrument readings.)

## Data quality — the key point for the jury
- Unique UTC RTE timestamps: **35,132** vs **35,136** expected 15-min positions.
- Four duplicated 15-min timestamps: **2024-03-31 01:00–01:45 UTC** (four extra rows).
- Four missing 15-min positions: **2024-10-27 00:00–00:45 UTC** (one entire hour).
- Non-null realized measurements at **:00** and **:30**, null at **:15** and **:45**; the 17,568 null rows are consistent with half-hour actual measurements on a quarter-hour timestamp grid, not 50% loss of observations.
- Before training, check duplicated records for consistency; deduplicate with a documented rule; retain the missing hour as NA and exclude it from target-scored metrics or apply an explicitly justified strategy. Never hide the exception.

## Suggested slides
1. Research question: Can available day-ahead weather forecasts improve France's **generation-based** carbon intensity predictions? Distinguish the target from marginal/consumption-based intensity.
2. Data provenance and data quality: 8 cities, RTE + ERA5, 8,784 hourly points, precise DST-related anomalies.
3. Seasonal demand relationship: include `03_temperature_vs_consumption_by_season.png`, highlight that month changes the relationship.
4. Wind mechanism and honest limits: include `05_wind_generation_diagnostics.png`; explain that correlation is not causal and a full electricity-mix model is needed.
5. Forecast leakage avoidance: include `04_historical_forecast_vs_ERA5.png` and define what information is available at prediction time.

## Critical caveats
- ERA5 at the target time is retrospective reanalysis: unsuitable as a future input to a day-ahead forecast unless labeled as an oracle upper-bound scenario.
- `previous_day1` fixed-lead forecast values do not constitute one consistent daily issue-time forecast for all 24 future hours; design the actual prediction protocol before training.
- Eight-city weather is an unweighted exploratory proxy, not representative national meteorology.
- One week in Paris does not establish historical forecast performance for France and all seasons.
- No trained ML model, deployment, generalization, causal estimate, or emission-saving experiment has been demonstrated in Phase 0.
- 2025 remains the proposed locked test year and was not queried by the notebook.

## Next coordination steps with Ramy
1. Share five figures and this note.
2. Agree on exact target, horizon, issued-time assumptions, and training/validation/test protocol with the supervisors.
3. Decide how historical weather forecast availability will change the 2019–2023/2024/2025 split.
4. Prepare first-evaluation slides and practice explaining leakage, seasonality, quality anomalies, and why correlation is not causation.
