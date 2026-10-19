# FaceVitals | IEEE SP Cup 2027 | Research starter kit (Phase 0)

**Prepared 19 October 2026. Research and educational prototype; no medical claims.**

## Read these in order

1. [`docs/01_algorithm_tutorial.md`](docs/01_algorithm_tutorial.md): a from-scratch explanation of remote photoplethysmography, GREEN, CHROM, POS, ICA/PCA, deep models, SpO2 and BP.
2. [`docs/02_method_and_dataset_review.md`](docs/02_method_and_dataset_review.md): literature-grounded comparison and practical data-acquisition choices.
3. [`docs/03_experiment_protocol.md`](docs/03_experiment_protocol.md): how to evaluate a real video benchmark without leakage.
4. [`docs/07_synthetic_results.md`](docs/07_synthetic_results.md), [`results/synthetic_summary.csv`](results/synthetic_summary.csv) and [`figures/synthetic_mae_heatmap.png`](figures/synthetic_mae_heatmap.png): **SIMULATION ONLY**, not actual camera/demographic/clinical performance.
5. [`docs/04_research_roadmap.md`](docs/04_research_roadmap.md): novelty hypotheses and project priorities.
6. [`docs/05_dataset_request_emails.md`](docs/05_dataset_request_emails.md): ready-to-personalize drafts, *not sent*.
7. [`docs/06_competition_checklist.md`](docs/06_competition_checklist.md): registration and deliverable requirements.

## What was actually implemented?

**Implemented:** an RGB-*trace* generator (synthetic framewise mean R/G/B values), four computational baselines (GREEN, windowed POS, windowed CHROM, PCA-1), common filtering and frequency-domain HR estimation, controlled stress conditions, structured CSV output, MAE/RMSE/Pearson/Bland-Altman statistics, a >5 bpm failure definition, a saved run manifest, a 10 fps trace experiment and four unit tests.

**Not implemented in the synthetic benchmark:** video processing and facial-region extraction (the separate `src/video_to_rgb.py` provides only an optional, unvalidated OpenCV Haar proof-of-concept). **Not implemented in the project as a validated system:** accurate face landmarks, persistent multi-face identity tracking, clinically meaningful skin masks, real lux/noise calibration, video compression or actual low-resolution robustness evaluation, trained neural networks, real subject fairness evaluation, authorized dataset benchmarks, SpO2 models, BP models, clinical or on-device validation. The synthetic `weak_pulse_proxy` test **is not a skin-tone experiment**. `10fps_trace` **is not proof of compressed-video performance**. `low_light_proxy` **is not a measured 50-lux test**.

## Reproduce the simulation

```bash
cd FaceVitals_Phase0
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/benchmark.py --trials 35 --seed 2027 --out results --figures figures
```

The script is deterministic for the generated signal and HR results at a specified seed. Processing timings are machine-dependent. The output fields explicitly identify synthetic evidence.

### Apply the same estimators to your own RGB ROI time series

Prepare a CSV with columns `r,g,b` containing **mean skin-region RGB intensity per frame** (positive values, consistent with the camera's processing), and optionally `timestamp_s`:

```bash
python src/benchmark.py --input-csv data/example_roi_trace.csv --fps 30 --reference-bpm 75 --out results/own_trace
```

This is **not** an end-to-end video pipeline. If `timestamp_s` values are present, the tool infers sampling rate from them and rejects strongly irregular sampling (>10% interval deviation). Derive the reference HR from synchronized clinical ground truth and document the alignment/window definition. If the signal has changing HR, use an aligned windowed reference rather than a single whole-video value.

## Evidence quality and error reports

The percentage called a **failure rate** is explicitly defined as `100 × (|predicted HR − reference HR| > 5 bpm OR no valid prediction) / number of clips`. This is **our operational threshold**, not an official competition pass/fail metric. All CSV errors are computed on *artificial signals*, not human participants. There is no single well-defined published failure rate for each algorithm independent of dataset, acquisition setup, estimator settings and failure threshold.

## Primary sources

- Official 2027 FaceVitals technical specification: https://signalprocessingsociety.org/sites/default/files/2026-10/2027-SP-Cup-Official-Document-FaceVitals.pdf
- IEEE SPS competition page: https://signalprocessingsociety.org/community-involvement/signal-processing-cup
- Algorithmic Principles of Remote PPG (POS): https://pubmed.ncbi.nlm.nih.gov/28113245/
- CHROM: https://pubmed.ncbi.nlm.nih.gov/23744659/
- Reference baseline implementations: https://github.com/ubicomplab/rPPG-Toolbox and https://github.com/phuselab/pyVHR
- Published diverse real-video study: https://github.com/AiPEX-Lab/rppg_biases
- BP4D+ access conditions: https://www.cs.binghamton.edu/~lijun/Research/3DFE/3DFE_Analysis.html
- Camera Vitals public dataset index: https://cameravitals.github.io/datasets.html

We should prioritize authorized organizer / public dataset access, then measure on *real video* before choosing the final algorithm. 

### Optional proof-of-concept extraction from a licensed real video

```bash
python src/video_to_rgb.py --video PATH_TO_AUTHORIZED_VIDEO.mp4 --out results/own_video_rgb.csv
```

This OpenCV Haar baseline extracts approximate forehead and cheek rectangles, writes the three average channels, and retains missing detections as NaN. **It does not provide landmark-accurate skin ROI segmentation, multi-person identity assurance, ethical clearance or synchronized ground truth**. Only on a single clear face with valid, regularly sampled traces should you then pass that CSV to `src/benchmark.py`; otherwise improve the detector and gap-handling first. An unverified reference HR must never be invented. See `templates/real_video_manifest_template.csv` and `templates/reference_signal_template.csv` for the required upcoming data inventory.
