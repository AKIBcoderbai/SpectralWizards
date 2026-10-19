# 02 | Algorithm selection, evidence and dataset access

**Research status as of 19 October 2026.** This matrix is a *methodological triage*, not a pooled meta-analysis and not a set of established per-algorithm failure rates.

## Method comparison: where each approach can shine

| Method | Principle | Strengths | Main potential failure mechanisms | Edge feasibility | Phase-1 role |
|---|---|---|---|---|---|
| GREEN | green ROI mean + temporal filtering | transparent; extremely fast; useful check of camera/ROI | pulse-like motion, flicker, specular changes | Excellent | must-have control |
| CHROM | normalized RGB chrominance projections with adaptive scaling | interpretable; attempts illumination/motion suppression | illumination spectrum and camera RGB response mismatch; unstable short-window SD | Excellent | primary baseline |
| POS | standardized color projection orthogonal to skin direction | good low-compute candidate; unsupervised; easy per-ROI | tiny pulse amplitude; changing skin reflection; heavy motion | Excellent | **primary starting baseline** |
| ICA | independent source separation in RGB | flexible nuisance mixing | independence violated; output component selection may track artifacts | Good | second-stage baseline |
| PCA | largest RGB variance or selected PCs | easy dimension reduction | largest component can be motion rather than pulse | Excellent | diagnostic comparator, not PCA-1 as best method |
| PBV | estimated blood-volume color signature | physiology-inspired projection | model mismatch under varied light/camera/skin | Excellent | ablation candidate |
| LGI / SSR | invariant/spatial color subspace methods | may exploit pixel structure and nuisance subspaces | ROI quality, illumination, insufficient skin pixels | Good | advanced classical |
| DeepPhys | CNN learned from appearance + changes | can learn spatial attention under representative training | bias, compression generalization, labels needed | Moderate | deep baseline |
| PhysNet | spatiotemporal learned waveform | captures nonlinear time/space cues | heavy deployment; high-data needs | Lower | GPU reference |
| TS-CAN / EfficientPhys | efficiency-oriented neural signal estimation | potentially useful on edge | inference cost still needs hardware testing; out-of-domain shift | Moderate/Good | later edge candidate |
| PhysFormer | temporal/spatial attention | expressive representation | compute/data cost, skin-tone & camera domain shift | Lower | aspirational higher-capacity reference |

**Recommendation:** Begin with **GREEN, POS and CHROM**, with consistent face/ROI preprocessing, same HR-band filter and fixed evaluation clips. After real-video ground truth is acquired, add ICA/PBV, patch-level aggregation and a model from rPPG-Toolbox. No method is an unconditional "best" across conditions; even the apparently best one in the synthetic CSV may lose on authentic videos.

The `src/benchmark.py` prototype implements GREEN, CHROM, POS and PCA-1 on *synthetic ROI RGB traces*. It does not implement any of the deep methods, ICA, PBV, LGI or SSR.

## Why we are not copying "failure rates" out of papers

A defensible method-to-method error comparison must use the **same actual clips, reference-signal synchronization, skin ROI, test splits, HR-estimator configuration and failure definition**. Different papers often use different datasets and metrics (MAE, RMSE, correlation, signal-to-noise ratio, fraction with errors >5 bpm). Even if paper A reports 2 bpm MAE and paper B reports 5 bpm MAE, that alone does not prove A's algorithm is better.

### Literature-grounded benchmark references

- **Wang et al., 2017, POS mathematical foundations:** https://pubmed.ncbi.nlm.nih.gov/28113245/
- **de Haan & Jeanne, 2013, CHROM:** https://pubmed.ncbi.nlm.nih.gov/23744659/
- **pyVHR:** cross-dataset workflows for GREEN, ICA, PCA, CHROM, POS, SSR, LGI, PBV, OMIT; https://github.com/phuselab/pyVHR
- **rPPG-Toolbox:** public reference implementations and training/evaluation workflows; https://github.com/ubicomplab/rPPG-Toolbox
- **AiPEX-Lab diversity/bias study:** real videos from India and Sierra Leone, published method-comparison CSV, source code and methodology; https://github.com/AiPEX-Lab/rppg_biases ; associated paper https://doi.org/10.1038/s41746-021-00462-z . The paper reports variability and bias under its *own protocol*; do not mislabel this as a generic per-method failure percentage.
- **RGB-only SpO2 critical review (2026):** https://www.mdpi.com/2079-9292/15/15/3477
- **AHA cuffless BP scientific statement:** https://professional.heart.org/en/science-news/cuffless-devices-for-the-measurement-of-blood-pressure

## Dataset ranking and what is actually measured

| Dataset/source | Best use | Critical caution | Access |
|---|---|---|---|
| **Organizer's 2027 clinical dataset** | direct challenge alignment, three-vital validation if labels match | requires copyright/legal agreement; obtain acquisition metadata | email Dr. Vijay Jeyakumar (copy competition list) |
| **AiPEX-Lab rppg_biases** | subgroup and cross-condition *HR* comparisons; multiple facial ROI clips | publicly provided means/videos should be checked for timing, actual pixel availability and ground-truth format | GitHub repository |
| **UBFC-rPPG** | foundational real-video HR + PPG test | Dataset 1/2 labels differ; not a definitive BP or hypoxemia benchmark | public dataset page |
| **PURE** | movement and controlled recording HR baseline | verify availability/usage terms and exact reference-signal format | request authors / public routes where permitted |
| **VIPL-HR** | broader devices/lighting and pulse labels; investigate SpO2 availability per session | changing hardware & capture conditions require subject/device splits | published dataset site |
| **COHFACE** | illumination and real PPG/respiration comparison | limited cohort; older camera | dataset owners/site |
| **BP4D+** | extensive subject-diverse facial video and physiological/cuff pressure-wave modalities | not an interchangeable clinical SpO2/ECG/PPG ground truth; must inspect labels and synchronization | faculty-led license request |
| **BP4D++** | more age diversity including participants through 70; physiology and video | large, access-restricted; ascertain which BP labels and reference techniques actually provided | inquiry to Dr. Lijun Yin |
| **BU-3DFE** | static 3D expression/face geometry only | **not suitable as a core HR/rPPG dataset** because static expression models lack synchronized pulse video/reference | not a priority |
| **Camera Vitals website** | discovery index of datasets, tools and papers | **not itself a dataset** | https://cameravitals.github.io/datasets.html |

**Important correction to dataset search:** The Binghamton page is titled "3D Facial Expression Database" but covers *several* different datasets. Request **BP4D+ or BP4D++**, not BU-3DFE, for relevant physiology; the site says students cannot individually receive BP4D+ and asks a **faculty supervisor** to request data and sign institutional agreements. The site also describes a substantial external-drive transfer for BP4D+. **Ask whether a smaller authorized subset is available** before planning transfer.

## Competition specification notes

- Official source: https://signalprocessingsociety.org/sites/default/files/2026-10/2027-SP-Cup-Official-Document-FaceVitals.pdf
- Round 1: HR under controlled and uncontrolled conditions; at least two robustness constraints addressed and justified.
- Round 2: HR + SpO2 with pulse oximeter reference.
- Final phase: HR + SpO2 + systolic/diastolic BP, clinically benchmarked and live demonstration.
- Stress requirements include ≤50 lux; sub-HD down to QVGA; ≤500 kbps and ≤10 fps; ages 60–70+; partial lower-face masking; multi-person selection; Fitzpatrick/skin-condition generalization.
- Official output convention includes `.mat` payloads, paired RGB video, reference and processed CSV; metadata include light, age, skin type, camera FPS, distance, constraints.

**Documentation inconsistencies to clarify with organizers:** The technical document describes *three rounds* but also lists directory `/Round4_FullSystem_Clinical/`; the general uploaded Terms & Conditions lists **six** equally weighted final judging criteria, while an SPS web page currently displays **five**. Follow the challenge-specific instructions and request written clarification rather than guessing submission folder names or scoring weights.
