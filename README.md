HC Panter Spring Cup 2026 – Tournament Model
Problem
This project models a 14‑team youth hockey tournament that originally had only raw standings and a manual bracket. Small sample sizes (6 group games per team) make naive goal averages unstable, and there was no way to quantify each team’s true attacking and defensive strength or their chances of reaching each finishing place. This repo provides a reproducible probabilistic model and an automatically generated, analysis‑ready Excel workbook.

Model
Poisson goal model calibrated on all completed match results, deriving per‑team attack strength and defensive weakness, normalised to each group’s scoring environment.

Bayesian-style shrinkage on attack/defence ratings so that extreme records over a handful of games are pulled toward the group mean instead of producing unrealistic win probabilities.

Direct RSI and Bridge RSI factors to adjust same‑group and cross‑group matchups using performance versus quality‑matched opponents.

Full Monte Carlo engine (100,000 simulations) for group and knockout stages, applying the official tiebreak ladder in the correct order: head‑to‑head points → head‑to‑head goal difference → head‑to‑head goals for → overall goal difference → overall goals for → dice. Multi‑team ties are resolved by rerunning the ladder on only the tied teams.

Outputs
Running the pipeline produces an Excel file HC_Panter_Spring_Cup_2026_v5.xlsx in the output/ folder with:

Colour‑coded Group A & B standings with W/D/L, GF/GA, GD, points, and games left.

Match‑by‑match predictions with Poisson λ values, win/draw/loss probabilities, and RSI type (Direct vs Bridge).

A Bridge RSI matrix showing cross‑group strength adjustments for every A vs B pairing.

Knockout and placement game predictions with KO win probabilities.

Group position probabilities (P(1st)–P(7th) for each team).

A full 14‑place tournament finish matrix, with every finishing position column validated to sum to 100%.

How to run
Install dependencies:

bash
pip install -r requirements.txt
Update the completed and remaining match lists in the data script if new results are available.

Run the pipeline (scripts can be run in order or combined into a single driver):

bash
python 01_data_and_shrinkage_model.py
python 02_global_quality_scores.py
python 03_bridge_rsi_function.py
python 04_full_prediction_with_rsi.py
python 05_monte_carlo_simulation.py
python 06_build_dataframes_for_excel.py
python 07_write_and_style_excel.py

Open output/HC_Panter_Spring_Cup_2026_v5.xlsx to explore the results.
