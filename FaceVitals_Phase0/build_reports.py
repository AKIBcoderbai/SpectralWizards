"""Build descriptive Markdown reports from synthetic simulation outputs."""
from pathlib import Path
import pandas as pd
base=Path(__file__).parent
s=pd.read_csv(base/'results/synthetic_summary.csv')
r=pd.read_csv(base/'results/synthetic_predictions.csv')
scenes={
'controlled':'Clean color traces with modest nuisance intensity drift',
'low_light_proxy':'Weak overall intensity and fixed absolute read noise; not measured lux',
'motion_artifact':'Periodic shared RGB nuisance at a cardiac-band frequency; not actual head movement',
'color_illumination':'Chromatic periodic flicker injected into RGB; not real illumination spectrum',
'10fps_trace':'Decimate sampled RGB means to 10 fps; not video bitrate/compression',
'weak_pulse_proxy':'Reduce synthetic pulse amplitude only; not a skin-tone simulator'}
lines=["# 07 | First results: synthetic RGB-trace benchmark", "",
       "**WARNING: illustrative simulations only. None of these percentages measure clinical or real-video performance.**", "",
       f"Generated {r['synthetic_clip_id'].nunique()} artificial traces, evaluated by {r['method'].nunique()} algorithms = **{len(r)} estimates**. ",
       "Each scenario has 35 independent artificial traces with randomized HR (52–138 bpm). One output per method per artificial trace. Reproducible random seed: 2027.", "",
       "## Metrics table", "",
       "The failure definition is `abs(est-true)>5 bpm OR missing`; MAE/RMSE are in bpm. Correlation and limits of agreement are also recorded in the CSV.", "",
       "| Scenario | Method | MAE (bpm) | RMSE (bpm) | Failure >5 bpm / missing | n |",
       "|:--|:--|--:|--:|--:|--:|"]
for scene in scenes:
    ss=s[s.scenario==scene].sort_values('mae_bpm')
    for row in ss.itertuples():
        lines.append(f'| {scene} | {row.method} | {row.mae_bpm:.2f} | {row.rmse_bpm:.2f} | {row.failure_rate_gt5_pct:.1f}% | {int(row.n_total)} |')
lines += ["", "## Why these outcomes appear", "",
    "**Controlled and 10 fps trace:** Strong artificial pulse with little in-band interference is easy for most spectral estimators. Downsampling a perfectly aligned pre-aggregated trace is *not* the same as feeding a poor 10 fps smartphone video into a face detector.", "",
    "**Motion-artifact scenario:** The injected shared-intensity sinusoid is designed to be suppressible by normalized color projections. This benefits POS/CHROM under this *particular* artifact construction and exposes GREEN/PCA-1 to nuisance dominance. It does not prove real movement immunity.", "",
    "**Low-light proxy:** The chosen absolute read-noise floor makes two-window color projections relatively unstable while the relatively stronger green pulse can remain visible. This is a *model effect*, not evidence that GREEN generally wins at 50 lux. Real cameras alter their exposure, gain, compression and temporal sampling.", "",
    "**Color illumination:** Periodic chromatic interference falls inside the HR passband and defeats all tested methods frequently. Peak power may be large even when the predicted HR is wrong: spectral peak-to-median PSD is **not calibrated confidence**.", "",
    "**Weak-pulse proxy:** This tests a deliberately smaller optical modulation, not pigmentation, Fitzpatrick classification, melanin absorption or any demographic attribute. It cannot support skin-tone fairness claims.", "",
    "## Technical limitations", "",
    "- Simplified, short-window CHROM/POS overlap-add variants; not exact original authors' implementation.",
    "- No facial video decoding, face detection, ROI segmentation, real frame-drop motion, physical luminance or bitrate modeling.",
    "- The model uses one artificial pulse shape across conditions; deliberately simple and **not calibrated** to human skin optics or real camera response.",
    "- PCA-1 is not a full pulse-aware PCA selector; algorithms were not tuned or learned using human data.",
    "- Per-condition sample size 35; no inferential real-population uncertainty analysis.",
    "- A changing heart rate/arrhythmia is not simulated. No physiological SpO2/BP predictions were made.",
    "", "## Full reproducibility", "",
    "`src/benchmark.py`, `tests/test_benchmark.py`, `results/manifest.json`, `results/synthetic_predictions.csv` and `results/synthetic_summary.csv` contain the complete generative assumptions, code, individual predictions and aggregations. Timing columns reflect only processing an RGB trace, **not end-to-end camera FPS**.",
    "", "## Figures", "",
    "![Pipeline, highlighting absent image-processing stages](../figures/pipeline_diagram.png)", "",
    "![Synthetic MAE heatmap](../figures/synthetic_mae_heatmap.png)", "",
    "![Artificial RGB traces and extracted channels](../figures/synthetic_trace_example.png)", "",
    "Next required evidence: real RGB video with synchronized ground truth, well-documented consent/licensing and participant-held-out evaluation."
]
(base/'docs/07_synthetic_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('wrote interpretation',len(lines),'lines')
