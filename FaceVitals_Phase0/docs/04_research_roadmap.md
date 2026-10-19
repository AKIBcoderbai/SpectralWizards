# 04 | Engineering roadmap and candidate research contribution

## Priorities and decision gates

| Time/order | Concrete deliverable | Gate |
|---|---|---|
| **Now, before 25 Oct 2026** | finish team formation, 3 active SPS undergraduate memberships, supervisor eligibility, signed terms, registration; email organizer for clinical dataset agreement | registration accepted + documented membership |
| Week 1 | read algorithms + download licensed/public real HR benchmark; synchronized video/PPG loader | first valid paired subject examples |
| Week 2 | video detector + forehead/cheek ROI; GREEN/POS/CHROM in common harness | correct waveform and manual spot checks |
| Weeks 3--4 | test controlled C1/C4/C5 + build per-condition statistics and clips gallery | reproducible participant-disjoint HR table |
| Weeks 4--5 | selective / adaptive fusion prototype + ablation against fixed POS/CHROM | credible improvement on held-out subject/condition split |
| By 30 Nov 2026 | Round-1 technical IEEE-format report, code, video/CSV/.mat package per official naming, at least two constraints | pre-submission audit |
| Round 2 | clinical SpO2 labels, cross-device/low-saturation tests, documented calibration | genuine joint HR/SpO2 validation |
| Final phase | SBP + DBP labels, clinical protocol, offline/live on-device version | no overstated medical claim |

## Candidate novelty: Quality-Calibrated Multi-ROI Color Projection (QC-MRCP)

**A research hypothesis, not a validated invention or claim of novelty against all literature.**

Instead of selecting POS or CHROM globally, process several separate skin patches: forehead, left cheek, right cheek, possible periocular exposed skin if occluded. For each patch, compute candidate pulse traces `GREEN`, `POS`, `CHROM`, optionally `PBV`. Score each independently using observable *input-only* features:

- stability of dominant frequency over adjacent windows;
- amplitude/SNR of candidate HR peak relative to other frequencies;
- agreement among spatially separate ROIs (not merely agreement among algorithms sharing the same contaminated input);
- target track stability and skin-mask coverage;
- saturation, clip/dark-pixel fraction, motion magnitude and exposure changes.

Then estimate a fused pulse/HR using weights such as `w_{roi,method} = softmax(quality / temperature)` and a robust consensus rather than always trusting the peak of the loudest signal. Critically: **frequency agreement among several patches can also be caused by global flicker or whole-head motion**; independently measure the nuisance features and reject low-quality outputs. A high quality number is not a calibrated confidence probability until tested against ground truth.

### Proposed experiments

A. Fixed ROI + GREEN vs fixed ROI + POS vs fixed ROI + CHROM.
B. Add adaptive ROI/patch aggregation without algorithm fusion.
C. Add adaptive method fusion with weights from pre-defined non-reference features.
D. Add explicit quality gate / abstention; plot risk-coverage curve and false-confidence rate.
E. Re-evaluate C1, C4, C5 and C7 as *real-video* stress, holding subjects/cameras out.
F. Ablate each feature, fix compute budget, and report paired bootstrap 95% CIs.

**What would support the hypothesis?** Lower worst-condition errors than fixed methods **at similar coverage**, honest improvements in false-confidence, improved subject/device generalization and sustained real-time throughput on an edge device. If it only improves a synthetic trace simulator, it remains a toy result.

## Other possible contributions (ranked)

1. **Robustness/uncertainty first:** edge-friendly POS/CHROM + multi-patch confidence and explicit abstention. Strong fit to constraints, lower compute and better interpretability.
2. **Camera-invariant color correction:** estimate nuisance exposure/white balance trends from non-skin background or reference patches *if available*. Check that this does not require unrealistic controlled calibration targets.
3. **Cross-device calibration study for SpO2:** compare fixed global RGB ratio, camera-conditioned and physiology-regularized regressors. Require broad clinical SpO2 values and confirm license/ground truth; prioritize *truthful feasibility bounds* over optimistic estimates.
4. **BP uncertainty and personalization:** if permitted by rules and user workflow, test population model against a separate **cuff-calibrated** model, with prospective recalibration and real BP-change evaluation. Do not claim absolute BP from pulse rate alone.

## Immediate fork in the road

The decision with the most value is **dataset availability**. Ask the organizers for the official clinical dataset now, while downloading a legitimate real-video HR dataset for Round 1. Do not delay the baseline until you get BP4D+; it is licensed, very large and not necessarily the exact pulse-ox ground truth needed for SpO2.
