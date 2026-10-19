# 03 | Reproducible benchmark protocol for real videos

## Study questions

- Q1: On real videos, which of GREEN, POS, CHROM, ICA and PBV best estimates **HR** under controlled conditions?
- Q2: Which degrades least under C1 low light, C4 low resolution, C5 reduced bandwidth/FPS, and C7 occlusion?
- Q3: Does **worst-group** HR error increase across objectively documented pigmentation strata, age bands or camera conditions?
- Q4: Is an uncertainty/quality gate capable of preventing confident wrong HR estimates without rejecting every hard sample?
- Q5 (later): Can SpO2 / systolic+diastolic BP be estimated with defensible calibration and subject-independent testing?

## 1. Before any model is trained or tuned

Create a reproducible sample manifest containing: `dataset_id, subject_id, clip_id, video_path, camera_model, frame_rate, timestamps, reference_type, reference_file, skin_tone_method, age_band, condition, measured_lux, video_bitrate, resolution, consent_license_status`. Unknown fields should be null, not invented. Securely store identifiable face videos and share only data permitted by licenses/consent.

Define **participant-disjoint splits**. A person's recordings MUST NOT appear across train/validation/test, and neighboring overlapping windows of the same person must not leak across splits. If testing camera generalization, hold out **entire cameras**. For robustness claims, evaluate the shift from baseline on matched subjects when possible, and report condition sample sizes. Calibrate thresholds/models only on training/validation, never the final test.

## 2. Input and face/ROI preprocessing

1. Decode exact frame timestamps, keep dropped-frame indicators; do not assume perfect constant FPS.
2. Detect *all* faces; select target ID and track across time (C3), measure identity-switch rate.
3. Extract forehead, left cheek, right cheek masks from landmarks; exclude hair, sclera, specular reflections and occlusions.
4. Average robust RGB over each skin mask per time step; store 3 traces and mean skin-pixel coverage.
5. Compute method output per ROI and optionally aggregate using **a score evaluated without reference HR** (e.g., spectral peak stability, patch consistency). Report any abstentions.
6. Process windows of 20--30 s to establish an initial baseline. Vary duration as a controlled ablation (e.g., 10/20/30 s).
7. Pass the *same* HR estimator and passband (for example 0.7--3 Hz) to every method. Publish latency after warm-up and memory per device.

## 3. Baseline & stress tests

| Test | Grounded competition target | Real experiment | Current synthetic prototype |
|---|---|---|---|
| Controlled | ≥300 lux, ≥30 fps, HD, 40--60 cm, frontal | measured setup + reference ECG/PPG | simulates clean RGB traces **only** |
| C1 low light | ≤50 lux | measure lux at face plane and capture real camera noise/exposure settings | low `relative_light_gain`; **not lux-calibrated** |
| C2 skin tone | multi-tone and dermatological variation | obtain consented Fitzpatrick/ITA metadata and stratify | **not implemented**; weak-pulse proxy is not skin tone |
| C3 multi-person | persistent one-target tracking | staged multi-face videos, identity-switch count | **not implemented** |
| C4 low resolution | VGA ≤640×480, QVGA ≤320×240 | decode genuine reduced-resolution frames before face detection | **not implemented** |
| C5 bandwidth/FPS | ≤500 kbps, ≤10 fps | re-encode actual videos at target bitrate/FPS, decode and rerun end-to-end | resamples RGB *traces* to 10 fps only |
| C6 age | 60--70+ | age-stratified real data incl. older participants | **not implemented** |
| C7 occlusion | ≥40% lower face | mask actual images and verify ROI fallbacks | **not implemented** |

Do not try to "pass" the low-light task by multiplying post-extraction RGB means and claiming actual 50 lux behavior. Real cameras change shutter, gain, noise distribution and compression under weak light. Similarly, pixel downsampling after ROI averaging cannot evaluate face detector failure or changing number of pixels in the ROI.

## 4. Error metric formulas (HR in bpm)

For N paired clip predictions, `e_i = pred_i - truth_i`.

- `MAE = mean(|e_i|)`: typical absolute error.
- `RMSE = sqrt(mean(e_i²))`: outlier-sensitive error.
- `Pearson r = corr(pred, truth)`: agreement in co-variation, **not** a bias-free accuracy metric.
- `Bland--Altman bias = mean(e)`; approximate 95% limits of agreement = `bias ± 1.96*std(e, ddof=1)` when distributional assumptions permit.
- `failure_5bpm = 1(|e_i| > 5 OR invalid)`: user-defined operational measure, *not specified as the competition threshold*.
- `coverage = number_valid / number_total` and `selective MAE` for quality/abstention models; distinguish failure rate from abstention rate.

Use a separate paired bootstrap **resampled by subject, not by overlapping clip**, for 95% confidence intervals. Stratify sample sizes and report missingness. A claim of "skin-tone fairness" should also quantify the worst group and uncertainty intervals; ITA and Fitzpatrick are not equivalent concepts, and neither should be assigned merely by eyeballing a single rendered frame.

## 5. Multi-output metrics in later rounds

- **SpO2:** MAE and RMSE in **percentage points**, Bland-Altman limits, signed bias, accuracy at clinically relevant lower saturations, device/illumination generalization; do not equate narrow healthy-label prediction with reliable hypoxemia estimation.
- **BP:** separate SBP and DBP bias/MAE/RMSE in **mmHg**, cuff reference details, repeat-measure variability, calibration status, per-subject trajectories, independent subjects, and agreement plots.
- Report reference-device sampling, averaging time, recording delay, possible label synchronization issues. No substitution of hypothetical/noisy synthetic SpO2/BP labels for clinical ground truth.

## 6. Statistical comparison and literature reports

For the same held-out clips, report *paired* per-clip errors and difference distributions (e.g. POS minus GREEN). Use subject-wise bootstrap CIs; if statistical testing, pre-specify a paired test and account for multiple comparisons. Include at least one failure-case gallery with permission, raw RGB plots, frequency spectra and face-mask coverage. Avoid selecting the method by test-set tuning.

## 7. Recommended output table

Store one row per `{dataset_id, subject_id, clip_id, window_start_s, condition, method}` with:

`reference_bpm, predicted_bpm, absolute_error_bpm, failed_gt5_or_missing, quality, output_valid, roi_coverage, n_frames, actual_fps, measured_lux, bitrate_kbps, resolution, demographic_stratum, processing_ms, platform, code_version, split, reference_device, calibration_state`.

Create a `summary.csv` grouped by method × condition × subgroup, showing `N, MAE, RMSE, failure_% (defined threshold), Pearson, Bland-Altman bias/limits, coverage, time_ms` and the test protocol/version. This is compatible with judging metrics but **not the complete required competition file schema**; export official `.mat`/video/reference structures after organizers confirm details.
