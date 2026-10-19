#!/usr/bin/env python3
"""Educational FaceVitals Phase-0 RGB-TRACE benchmark (NOT a video/clinical benchmark).

Synthetic, temporally sampled RGB ROI means only. Implements simplified overlap-add
POS and CHROM projections, GREEN, and a deliberately simple PCA comparator.
Nothing in this script estimates SpO2 or BP or validates a specific skin tone.

Run: python src/benchmark.py --out results --figures figures --trials 35 --seed 2027
Input adapter: python src/benchmark.py --input-csv path.csv --fps 30 --out results/custom
CSV input columns: r,g,b (0-1), optionally timestamp_s; --reference-bpm reference value.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import time
import json
import math
import platform
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, periodogram

METHODS = ("GREEN", "CHROM", "POS", "PCA")
SCENARIOS = ("controlled", "low_light_proxy", "motion_artifact", "color_illumination", "10fps_trace", "weak_pulse_proxy")
FMIN, FMAX = 0.7, 3.0


def simulate_rgb(hr_bpm: float, fps: float, duration: float, rng: np.random.Generator,
                 scenario: str) -> tuple[np.ndarray, float, dict]:
    """Generate illustrative ROI mean RGB traces. No facial frames, lux or labels."""
    if scenario not in SCENARIOS:
        raise ValueError(scenario)
    nominal_fps = 30.0
    t = np.arange(int(duration * nominal_fps)) / nominal_fps
    base = np.array([0.55, 0.43, 0.35], dtype=float)
    pulse_strength = 0.0058
    illum = 1.0
    read_noise = 0.0008
    motion_strength = 0.0005
    flicker_strength = 0.0004
    if scenario == "low_light_proxy":
        illum = 0.15  # synthetic gain, NOT a physical lux calibration
        read_noise = 0.0021
    elif scenario == "motion_artifact":
        motion_strength = 0.014
    elif scenario == "color_illumination":
        flicker_strength = 0.012
    elif scenario == "weak_pulse_proxy":
        pulse_strength *= 0.17  # NOT a skin-tone simulator
    freq = hr_bpm / 60.0
    pulse = np.sin(2 * np.pi * freq * t + 0.27) + 0.15 * np.sin(4 * np.pi * freq * t + 0.6)
    rgb = base[None, :] * illum
    rgb = np.broadcast_to(rgb, (len(t), 3)).copy()
    # Different channel blood volume signature; sign in reflectance is irrelevant for HR.
    rgb += (pulse_strength * illum) * pulse[:, None] * np.array([0.63, 1.0, 0.32])[None, :]
    # Slow shared intensity changes + a weak artifact inside the physiological band.
    drift = (0.010 * np.sin(2 * np.pi * 0.19 * t + 1.2) +
             motion_strength * np.sin(2 * np.pi * float(rng.uniform(.85, 2.3)) * t + 1))
    rgb += (illum * drift[:, None]) * np.array([1.05, 1.0, .94])[None, :]
    rgb += (illum * flicker_strength * np.sin(2 * np.pi * float(rng.uniform(.75, 2.4)) * t + .8))[:, None] * np.array([.35, 1.15, -.28])[None, :]
    # Photon noise grows as sqrt(signal); read noise remains absolute.
    shot_sigma = 0.00055 * np.sqrt(np.maximum(rgb, 1.e-5))
    rgb += rng.normal(0, read_noise, size=rgb.shape) + rng.normal(size=rgb.shape) * shot_sigma
    rgb = np.clip(rgb, 0.001, 0.999)
    fps_out = 10.0 if scenario == "10fps_trace" else nominal_fps
    if fps_out == 10.0:
        rgb = rgb[::3]  # temporal downsampling only, not image compression/resizing
    return rgb, fps_out, {"relative_light_gain": illum, "pulse_amplitude": pulse_strength,
                          "read_noise_sigma": read_noise, "motion_artifact_amplitude": motion_strength,
                          "color_illumination_amplitude": flicker_strength}


def bandpass(x: np.ndarray, fps: float) -> np.ndarray:
    x = np.asarray(x, float)
    if len(x) < int(fps * 4):
        raise ValueError("At least 4 s of valid signal is necessary")
    high = min(FMAX, .45 * fps)  # strictly below Nyquist, actual band 0.7-3 at >= 10fps
    sos = butter(3, [FMIN, high], btype="bandpass", fs=fps, output="sos")
    return sosfiltfilt(sos, x - np.mean(x))


def _ola(rgb: np.ndarray, fps: float, method: str) -> np.ndarray:
    n = len(rgb)
    length = max(8, round(1.6 * fps))
    step = max(1, length // 4)
    out, weights = np.zeros(n), np.zeros(n)
    starts = sorted(set(list(range(0, n - length + 1, step)) + [max(0, n-length)]))
    taper = np.hanning(length) + 1e-4
    for start in starts:
        clip = rgb[start:start + length]
        normalized = clip / np.maximum(clip.mean(axis=0), 1e-8) - 1.0
        r, g, b = normalized.T
        if method == "POS":
            s1, s2 = g - b, g + b - 2 * r
            h = s1 + (np.std(s1) / max(np.std(s2), 1e-8)) * s2
        elif method == "CHROM":
            s1, s2 = 3 * r - 2 * g, 1.5 * r + g - 1.5 * b
            h = s1 - (np.std(s1) / max(np.std(s2), 1e-8)) * s2
        else:
            raise ValueError(method)
        h -= h.mean()
        out[start:start + length] += h * taper
        weights[start:start + length] += taper
    return out / np.maximum(weights, 1e-8)


def extract(rgb: np.ndarray, fps: float, method: str) -> np.ndarray:
    if rgb.ndim != 2 or rgb.shape[1] != 3:
        raise ValueError("Input must be Nx3 RGB ROI means")
    if not np.all(np.isfinite(rgb)) or np.any(rgb <= 0):
        raise ValueError("RGB must be finite and >0")
    if method == "GREEN":
        h = rgb[:, 1] / np.mean(rgb[:, 1]) - 1
    elif method in ("POS", "CHROM"):
        h = _ola(rgb, fps, method)
    elif method == "PCA":
        x = rgb / rgb.mean(axis=0) - 1
        x = x - np.mean(x, axis=0)
        _, _, vh = np.linalg.svd(x, full_matrices=False)
        # A deliberately simple PCA-1; signal vs artifact is NOT identifiable in PCA alone.
        h = x @ vh[0]
    else:
        raise ValueError(method)
    return bandpass(h, fps)


def estimate_hr(sig: np.ndarray, fps: float) -> tuple[float, float]:
    """Hann periodogram; local parabolic interpolation for HR estimate.

    Quality metric is relative peak prominence and is NOT a confidence probability.
    """
    nfft = max(2048, int(2 ** math.ceil(math.log2(len(sig)))))
    hz, psd = periodogram(sig, fs=fps, window="hann", nfft=nfft, detrend="constant")
    valid = (hz >= FMIN) & (hz <= FMAX)
    inds = np.flatnonzero(valid)
    if not len(inds):
        return float("nan"), float("nan")
    k = int(inds[np.argmax(psd[valid])])
    peak = hz[k]
    if 1 <= k < len(hz)-1 and min(psd[k-1], psd[k], psd[k+1]) > 1e-20:
        # Quadratic interpolation in log PSD: better numeric peak localization,
        # but zero-padding does not create additional information.
        v = np.log(np.maximum(psd[k-1:k+2], 1e-20))
        denom = v[0] - 2*v[1] + v[2]
        if abs(denom) > 1e-12:
            delta = float(np.clip(0.5*(v[0] - v[2])/denom, -.5, .5))
            peak += delta * (hz[1] - hz[0])
    prominence = float(psd[k] / max(float(np.median(psd[valid])), 1e-16))
    return 60 * float(peak), prominence


def calculate_summary(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scenario, method), g in raw.groupby(["scenario", "method"], sort=True):
        ok = g["predicted_bpm"].notna()
        errs = g.loc[ok, "predicted_bpm"].to_numpy() - g.loc[ok, "reference_bpm"].to_numpy()
        gt = g.loc[ok, "reference_bpm"].to_numpy()
        pred = g.loc[ok, "predicted_bpm"].to_numpy()
        if len(gt) >= 3 and np.std(gt) > 0 and np.std(pred) > 0:
            pearson = float(np.corrcoef(gt, pred)[0, 1])
        else:
            pearson = float("nan")
        bias = float(np.mean(errs)) if len(errs) else np.nan
        sd = float(np.std(errs, ddof=1)) if len(errs) > 1 else np.nan
        failures = int(np.sum(~ok) + np.sum(np.abs(errs) > 5.0))
        rows.append({"scenario": scenario, "method": method, "n_total": len(g),
            "n_valid": int(np.sum(ok)), "n_failed_gt5_or_missing": failures,
            "failure_rate_gt5_pct": 100 * failures / len(g),
            "mae_bpm": float(np.mean(np.abs(errs))) if len(errs) else np.nan,
            "rmse_bpm": float(np.sqrt(np.mean(errs**2))) if len(errs) else np.nan,
            "pearson_r": pearson, "ba_bias_bpm": bias,
            "ba_loa_low_bpm": bias - 1.96 * sd, "ba_loa_high_bpm": bias + 1.96 * sd,
            "mean_processing_ms_per_trace": float(g["processing_ms"].mean()),
            "evidence_type": "SYNTHETIC_RGB_TRACE_ONLY"})
    return pd.DataFrame(rows).sort_values(["scenario", "mae_bpm"])


def run_synthetic(out: Path, figures: Path, trials: int, seed: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    records = []
    for scene in SCENARIOS:
        for trial in range(trials):
            hr = float(rng.uniform(52, 138))
            trace, fps, details = simulate_rgb(hr, 30, 22, rng, scene)
            for method in METHODS:
                start = time.perf_counter()
                try:
                    sig = extract(trace, fps, method)
                    estimated, quality = estimate_hr(sig, fps)
                    status = "ok" if np.isfinite(estimated) else "invalid"
                except (ValueError, FloatingPointError, np.linalg.LinAlgError):
                    estimated, quality, status = np.nan, np.nan, "invalid"
                milliseconds = 1000 * (time.perf_counter() - start)
                records.append({"synthetic_clip_id": f"synth_{scene}_{trial:03d}",
                    "scenario": scene, "trial": trial, "seed": seed, "method": method,
                    "reference_bpm": hr, "predicted_bpm": estimated,
                    "absolute_error_bpm": abs(hr - estimated), "failed_gt5_or_missing":
                    bool(not np.isfinite(estimated) or abs(hr - estimated) > 5),
                    "quality_peak_to_median_psd": quality, "sampling_fps": fps,
                    "duration_s": len(trace)/fps, "processing_ms": milliseconds,
                    "status": status, "evidence_type": "SYNTHETIC_RGB_TRACE_ONLY", **details})
    raw = pd.DataFrame(records)
    summary = calculate_summary(raw)
    raw.to_csv(out / "synthetic_predictions.csv", index=False, float_format="%.6f")
    summary.to_csv(out / "synthetic_summary.csv", index=False, float_format="%.6f")
    info = {"seed": seed, "trials_per_scenario": trials, "n_synthetic_clips": trials*len(SCENARIOS),
        "n_predictions": len(raw), "algorithms": list(METHODS), "scenarios": list(SCENARIOS),
        "dataset_origin": "simulation_only; generated RGB means; no real videos, subjects, lux, SpO2 or BP",
        "failure_rule": "abs(predicted_bpm-reference_bpm)>5 OR missing",
        "computer_platform": platform.platform(), "python": platform.python_version(),
        "numpy": np.__version__, "pandas": pd.__version__}
    (out / "manifest.json").write_text(json.dumps(info, indent=2) + "\n")
    plot_results(raw, summary, figures, seed)
    print(summary[["scenario", "method", "n_total", "mae_bpm", "failure_rate_gt5_pct"]].to_string(index=False))


def plot_results(raw: pd.DataFrame, summ: pd.DataFrame, figures: Path, seed: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    # Accuracy matrix, title explicitly describes artificial evidence.
    view = summ.pivot(index="scenario", columns="method", values="mae_bpm").reindex(SCENARIOS)
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(view.values, cmap="viridis_r", aspect="auto")
    ax.set_xticks(range(len(view.columns)), labels=view.columns)
    ax.set_yticks(range(len(view.index)), labels=view.index)
    for i in range(len(view.index)):
        for j in range(len(view.columns)):
            ax.text(j, i, f"{view.values[i,j]:.1f}", ha="center", va="center", color="white" if view.values[i,j]>15 else "black", fontsize=9)
    fig.colorbar(im, ax=ax, label="MAE (bpm)")
    ax.set_title("Illustrative synthetic RGB-trace test: HR MAE (NOT clinical/video performance)")
    fig.tight_layout(); fig.savefig(figures / "synthetic_mae_heatmap.png", dpi=175); plt.close(fig)
    # Three-stage teaching visual.
    fig, ax = plt.subplots(figsize=(12, 3.0))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3); ax.axis("off")
    stages = [(0.1, "RGB video", "(not implemented)"), (2.55, "Skin ROIs", "(not implemented)"),
              (5.05, "RGB traces", "(simulated here)"), (7.52, "POS/CHROM", "+ filtering"),
              (10, "HR estimate", "+ metrics")]
    for i, (x, a, b) in enumerate(stages):
        p = FancyBboxPatch((x, 0.72), 1.85, 1.56, boxstyle="round,pad=.12",
                           facecolor="#eaf3f9", edgecolor="#3a6b83", linewidth=1.2)
        ax.add_patch(p); ax.text(x + .925, 1.61, a, ha="center", fontsize=10, weight="bold")
        ax.text(x + .925, 1.23, b, ha="center", fontsize=8)
        if i < len(stages)-1:
            ax.annotate("", xy=(x+2.35, 1.51), xytext=(x+1.98,1.51),
                        arrowprops=dict(arrowstyle="->", lw=2, color="#345a73"))
    ax.set_title("Full rPPG pipeline and the actual boundary of this prototype", fontsize=12)
    fig.tight_layout(); fig.savefig(figures / "pipeline_diagram.png", dpi=180); plt.close(fig)
    rng = np.random.default_rng(seed)
    example, fps, _ = simulate_rgb(78, 30, 22, rng, "motion_artifact")
    fig, axs = plt.subplots(2, 1, figsize=(10, 5.8), sharex=True)
    ts = np.arange(len(example))/fps
    for j, name in enumerate(("R", "G", "B")):
        axs[0].plot(ts, (example[:,j]/np.mean(example[:,j])-1)*100, alpha=.7, label=name, lw=.8)
    axs[0].set_ylabel("Relative channel change (%)"); axs[0].legend(ncol=3, frameon=False)
    for method in ("GREEN", "CHROM", "POS"):
        sig = extract(example, fps, method)
        sig /= max(np.std(sig), 1e-12)
        est, _ = estimate_hr(sig, fps)
        axs[1].plot(ts, sig, label=f"{method} ({est:.1f} bpm)", alpha=.75, lw=.9)
    axs[1].set_xlabel("Time (seconds)"); axs[1].set_ylabel("Normalized extracted pulse (a.u.)")
    axs[1].legend(frameon=False, ncol=3)
    fig.suptitle("Synthetic example: 78 bpm with periodic artifact (not a subject)")
    fig.tight_layout(); fig.savefig(figures / "synthetic_trace_example.png", dpi=175); plt.close(fig)


def run_csv(input_csv: Path, fps: float, reference_bpm: float | None, out: Path):
    if not input_csv.exists():
        raise FileNotFoundError(input_csv)
    df = pd.read_csv(input_csv)
    if not set(("r", "g", "b")).issubset(df.columns):
        raise ValueError("Input CSV needs columns r,g,b; optionally timestamp_s")
    if "timestamp_s" in df:
        t = df.timestamp_s.to_numpy(dtype=float)
        if not np.all(np.diff(t)>0):
            raise ValueError("timestamps must increase")
        intervals = np.diff(t)
        if np.max(np.abs(intervals-np.median(intervals))) > .1 * np.median(intervals):
            raise ValueError("frame times irregular by >10%: resample before benchmark")
        fps = float(1 / np.median(intervals))
    trace = df[["r", "g", "b"]].to_numpy(float)
    out.mkdir(exist_ok=True, parents=True)
    rows = []
    for method in METHODS:
        start = time.perf_counter()
        sig = extract(trace, fps, method)
        hr, q = estimate_hr(sig, fps)
        pd.DataFrame({"timestamp_s": np.arange(len(sig))/fps, "processed_signal": sig}).to_csv(out / f"trace_{method}.csv", index=False)
        rows.append({"method": method, "estimated_hr_bpm": hr, "reference_hr_bpm": reference_bpm,
                     "absolute_error_bpm": abs(hr - reference_bpm) if reference_bpm is not None else None,
                     "quality_peak_to_median_psd": q, "processing_ms": 1000 * (time.perf_counter()-start),
                     "evidence_type": "EXTERNAL_RGB_TRACE_UNVERIFIED"})
    pd.DataFrame(rows).to_csv(out / "external_trace_estimates.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trials", type=int, default=35)
    p.add_argument("--seed", type=int, default=2027)
    p.add_argument("--out", type=Path, default=Path("results"))
    p.add_argument("--figures", type=Path, default=Path("figures"))
    p.add_argument("--input-csv", type=Path)
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--reference-bpm", type=float)
    args = p.parse_args()
    if args.input_csv:
        run_csv(args.input_csv, args.fps, args.reference_bpm, args.out)
    else:
        if args.trials < 3:
            raise ValueError("--trials must be >= 3 for meaningful aggregate summaries")
        run_synthetic(args.out, args.figures, args.trials, args.seed)

if __name__ == "__main__":
    main()
