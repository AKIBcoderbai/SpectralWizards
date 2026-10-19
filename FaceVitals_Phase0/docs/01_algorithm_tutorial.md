# 01 | A beginner-to-researcher guide to rPPG algorithms

**Goal:** understand how facial video can reveal heart rate, why competing algorithms behave differently, and why SpO2 and BP need more than a pulse peak.

## 1. What the camera actually measures

A conventional photoplethysmograph (PPG) uses a light source and detector to measure blood-related variation in transmitted or reflected light. Remote PPG (rPPG) observes tiny, time-varying color changes of skin under illumination, using a camera instead of contacting the skin. Each heartbeat changes blood volume near the surface; hemoglobin absorption and tissue scattering slightly change the reflected radiance. The camera converts it to R, G and B electrical/image signals.

At a single region of interest (ROI) such as a forehead or cheek, define for frame *t*:

`r[t] = mean red value over valid skin pixels`, `g[t] = mean green`, `b[t] = mean blue`.

A useful schematic observation model is:

`RGB[t] = static skin color + cardiac modulation[t] + illumination[t] + motion/reflection artifacts[t] + camera noise[t]`.

This is a **conceptual additive approximation**, not a full optical forward model. A more physical starting point is that pixel intensity integrates light-source spectrum × tissue reflectance × camera spectral sensitivity across wavelengths, with additional camera processing (exposure, white balance, compression, nonlinear gamma). For this reason ordinary JPEG/video RGB channels are **not** calibrated wavelengths.

**The difficult part:** pulse color variations may be far smaller than apparent variation caused by changing pose, light, exposure or motion. Extracting a periodic peak does not prove that it is the heart: fluorescent flicker, movement or cyclic camera corrections can have a similar frequency.

## 2. The complete processing chain

```text
RGB VIDEO (timestamps, frames per second)
    |
    v
Find faces; designate + track target across frames
    |
    v
Find landmarks + skin-mask forehead and cheeks; exclude hair, eyes, mask
    |
    v
Compute robust RGB mean/median per region, per frame
    |
    v
Normalize slow color changes; combine color channels (GREEN/CHROM/POS/etc.)
    |
    v
Remove trend + band-pass pulse frequencies (example 0.7--3.0 Hz)
    |
    v
Get pulse spectral peak and/or interbeat spacing
    |
    v
HR = 60 x pulse_frequency_Hz; add quality / abstention gates
    |
    v
Compare to synchronized clinical reference; stratify failure by condition
```

The 0.7--3.0 Hz passband is approximately **42--180 bpm**. Frequency 1.25 Hz means `1.25 cycles/s × 60 s/min = 75 bpm`. **A passband is a design decision**: it can exclude bradycardia or tachycardia outside its bounds, and will alias or distort with insufficient frame rate. The official specification calls for **at least 30 fps** for the controlled baseline and includes a **10 fps** stress case (a 6 fps Nyquist floor covers 3 Hz in theory, but this does not guarantee acceptable accuracy).

### Why normalize by channel mean?

Suppose facial pixels of one ROI average `(R,G,B)=(110,84,70)` and a pulse varies green intensity by 0.4. The raw green variation is tiny relative to 84. A normalized green trace `g_norm[t] = g[t] / mean(g) - 1` measures *relative* deviations and is more comparable across cameras/subjects. However normalization does **not** remove every changing lighting artifact or create missing photometric information.

### What does a band-pass filter do?

An idealized sine wave at 1.2 Hz passes a 0.7--3.0 Hz bandpass. Slow brightness drift at 0.1 Hz is attenuated; high-frequency sensor noise is attenuated. But periodic head movement at 1.2 Hz passes **as well**, which is why color projection, tracking and robust spatial aggregation matter as much as filtering.

### How HR is estimated from the spectrum

An FFT or periodogram decomposes the extracted time series into candidate frequencies. Find the strongest reliable peak `f_peak` inside the allowed HR band; estimate `HR = 60 f_peak`. Prefer a Hann window, enough duration, reproducible frequency interpolation, and a mechanism to detect dominant motion harmonics. A 20-second observation contains approximately 0.05 Hz *independent* frequency spacing (`1/T`), equivalent to 3 bpm; zero-padding smooths the displayed periodogram but does not add new independent data. Longer windows stabilize spectral estimates but reduce responsiveness to changing HR.

## 3. GREEN -- the easiest baseline

1. Detect visible skin and compute the mean green-channel time series.
2. Divide by its temporal mean; remove baseline/trend.
3. Band-pass and find the strongest HR-band spectral peak.

Why green? Under many visible illumination conditions, the green channel has a comparatively strong pulsatile contrast. **Advantages:** trivial computation, interpretable, little tuning. **Weakness:** any illumination/motion artifact in green can overwhelm the pulse. A pure green method is valuable as a control; do not assume it should win.

## 4. CHROM -- exploit chrominance rather than brightness

Reference: de Haan & Jeanne (2013), *Robust pulse rate from chrominance-based rPPG*, DOI 10.1109/TBME.2013.2266196.

Given temporally normalized channels `r,g,b` within a short window, form:

`X = 3r − 2g`

`Y = 1.5r + g − 1.5b`

`alpha = std(X) / std(Y)`

`pulse_CHROM = X − alpha·Y`

The **idea** is to construct chrominance combinations where certain common illumination changes are suppressed, then scale them to balance nuisance contributions. Recalculate window statistics while moving along the video and overlap-add short window estimates. It is *not* simply selecting red and blue channels like a physical two-wavelength pulse oximeter.

**Advantages:** interpretable, no training labels, often handles motion/illumination variability better than GREEN. **Weakness:** depends on assumptions about light/color response and skin reflection; some illumination spectra break those assumptions. RGB values should be temporally well aligned, and short segments can produce unstable `std` ratios.

## 5. POS -- orthogonal projection to skin-tone direction

Reference: Wang et al. (2017), *Algorithmic Principles of Remote PPG*, DOI 10.1109/TBME.2016.2609282.

Again let `(r,g,b)` be normalized RGB within a short window, and compute:

`S1 = g − b`

`S2 = g + b − 2r`

`alpha = std(S1) / std(S2)`

`pulse_POS = S1 + alpha·S2`.

The projection is designed to isolate pulsatile color variation away from the dominant skin-color/intensity direction. Standard POS operates on overlapping short windows (e.g., 1.6 seconds) followed by temporal combination/postprocessing. In words: **look at how green differs from blue and how combined green/blue differs from red; blend those views adaptively**.

**Advantages:** inexpensive, unsupervised, a strong primary real-video baseline. **Weakness:** vulnerable when the skin-color assumptions fail, reflectance signal is small, motion changes the color balance, or artifacts have a pulse-like spectral peak.

**The implementation supplied here** is a teaching-oriented 1.6-second Hann-overlap-add adaptation with 25%-length hop and a common Butterworth filter; it is not a bitwise reproduction of the POS or CHROM authors' exact reference implementations. Before publication, validate against official implementations in rPPG-Toolbox/pyVHR.

## 6. ICA and PCA -- separating mixtures

**PCA (principal component analysis)** looks for directions in RGB space with maximum variance. It rotates the 3-channel observations into mutually orthogonal principal axes. Example: if head motion produces far more RGB variance than heartbeat, the **first** principal component might represent motion, not pulse. Selecting PCA-1 is therefore a deliberately weak comparator, not a state-of-the-art PCA implementation.

**ICA (independent component analysis)** assumes observations are mixtures of statistically independent underlying sources; it seeks combinations that are maximally non-Gaussian/independent. A component might resemble heartbeat, while another resembles illumination. In practice (i) independence assumptions are approximate, (ii) multiple artifacts can dominate, and (iii) one must select the *pulse-like* component without cheating by looking at reference HR.

We implemented **PCA-1**, not ICA. Real-data experiments should add a properly specified ICA baseline with component selection based only on allowed input/features.

## 7. PBV, LGI, SSR and neural approaches

- **PBV (blood-volume-pulse signature):** combines color channels using expected pulsatile relative amplitude; beneficial when its modeled optical signature is valid; errors arise under different lighting/cameras.
- **LGI (local group invariance):** removes nuisance variation through an estimated low-dimensional color subspace and invariant representation; needs careful ROI preprocessing.
- **SSR (spatial subspace rotation):** analyzes how the local skin-pixel color subspace changes over time; can use spatial pixel variation that framewise RGB means discard.
- **DeepPhys:** learns a physiological signal using image appearance + frame differences and learned attention; train/test leakage and changing camera pipelines matter.
- **PhysNet:** spatiotemporal video model learns waveform directly from video clips; typically heavier and label-dependent.
- **TS-CAN / EfficientPhys:** architectures emphasizing computational efficiency for physiological measurement; potentially more suitable to edge deployment than large 3-D models, subject to measured device latency/power.
- **PhysFormer:** attention-based temporal and spatial modeling; can be performant but is not an automatic edge/fairness solution.

Neural methods need data-quality checks, matching input representation, licensing and **subject-disjoint, device-disjoint evaluations**. Comparing a pretrained model evaluated on its training subjects to a new unsupervised baseline is not scientifically valid.

## 8. What exactly is a "failure rate"?

First define a test *unit*: a 20-second clip, fixed-person HR label, synchronized reference. Then define a threshold, for example `failure = |estimated HR - reference HR| > 5 bpm` or missing/invalid estimate. Across `N` clips, `failure_rate = number_failed / N` (×100 for percent). Separately report **MAE**, **RMSE**, **Pearson r**, **Bland-Altman bias** and limits (`mean difference ±1.96 × sample SD`) and *number of predictions rejected*. Always retain results by condition and demographic group; reporting only the pooled mean can hide systematic harm. The official challenge lists MAE, RMSE, Pearson and Bland-Altman; our >5 bpm threshold is an additional engineering measure.

There is no scientifically transferable figure such as "POS has a 12% failure rate" without specifying dataset, population, pre-processing, video quality, HR range, thresholds and ground truth. A published result on one dataset cannot be silently used as another dataset's benchmark.

## 9. Why SpO2 is a separate science problem

Classical pulse oximeters measure **red and near-infrared wavelengths** with known spectral responses, using a calibrated AC/DC intensity ratio. A conceptual ratio-of-ratios is:

`R = (AC_red/DC_red) / (AC_IR/DC_IR)`.

The clinical device maps `R` to SpO2 through a calibrated relationship, typically including empirical human calibration. **Ordinary RGB videos do not contain a dedicated infrared channel**, and RGB spectral responses/white balance change with device/illumination. One may attempt **calibrated RGB-ratio regression**, or a jointly learned feature network using actual clinical SpO2 labels, but the model must prove performance on genuinely varied oxygen saturations, skin tones and previously unseen cameras. Ordinary datasets of healthy subjects at 97--100% oxygenation may support a trivial near-constant predictor; such performance does not demonstrate hypoxemia detection.

Do not report SpO2 as clinically accurate without cross-device, low-saturation, agreement and calibration validation. Source: *RGB-Only rPPG for Contactless SpO2 Estimation: A Critical Review* (2026), https://www.mdpi.com/2079-9292/15/15/3477 .

## 10. Why BP is not simply HR plus a formula

BP varies with peripheral resistance, arterial compliance, cardiac output, posture, physiological state and other factors that **cannot be uniquely determined from HR**. One possible research pathway is to extract waveform-shape features (systolic upstroke duration, notch/shape proxies, width, variability), combine them with video-derived and validated covariates, and train systolic and diastolic regressors against properly synchronized **cuff/reference BP labels**. Assess individual calibration vs calibration-free methods separately. A model that learns a person's average pressure can appear strong without tracking BP changes, so use within-person change tests as well as subject-disjoint validation.

A single RGB-derived pulse trace is not a measured pulse-transit time (PTT); don't label it PTT unless two actual timing locations and a validated temporal reference are available. Clinical BP claims require dedicated validation. The American Heart Association cautions that cuffless BP estimates can be calibration-dependent and are not yet interchangeable with standard diagnosis/management measures: https://professional.heart.org/en/science-news/cuffless-devices-for-the-measurement-of-blood-pressure .

## 11. Worked mini-example: interpreting agreement

Suppose four synchronized clips have reference HR `[60, 80, 100, 120]` bpm, while a method gives `[61, 78, 106, 119]` bpm. Errors (prediction minus reference) are `[1, -2, 6, -1]` bpm. MAE is `(1+2+6+1)/4 = 2.5` bpm, despite **one failure** under the >5 bpm rule (25%). RMSE = `sqrt((1+4+36+1)/4) ≈ 3.24` bpm. These summarize different aspects: MAE typical absolute magnitude; RMSE sensitivity to outliers; failure rate risk of large errors. Report all three rather than just an attractive MAE.

## 12. First real-video task after this package

On authorized UBFC-rPPG, PURE, organizer, or AiPEX videos, implement: video timestamp loading, target-face detection, forehead/cheek ROI selection, skin-pixel mean extraction, GREEN/POS/CHROM, reference synchronization and a reproducible evaluation. Freeze that protocol **before** testing novel additions. The generated prototype does **not** yet execute this step.
