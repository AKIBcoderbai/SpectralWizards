import unittest, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
from benchmark import extract, estimate_hr, simulate_rgb, calculate_summary

class BenchmarkTests(unittest.TestCase):
    def test_clean_synthetic_pulse(self):
        fps=30
        rng=np.random.default_rng(24)
        rgb, fps, _ = simulate_rgb(75,fps,25,rng,"controlled")
        for method in ["GREEN", "POS", "CHROM"]:
            predicted,_=estimate_hr(extract(rgb,fps,method),fps)
            self.assertLess(abs(predicted-75),5,f"{method} result: {predicted:.2f}")
    def test_bandedge_resampling(self):
        rng=np.random.default_rng(27)
        rgb,fps,_=simulate_rgb(90,30,22,rng,"10fps_trace")
        self.assertEqual(fps,10)
        for method in ("GREEN","POS","CHROM","PCA"):
            val,_=estimate_hr(extract(rgb,fps,method),fps)
            self.assertTrue(np.isfinite(val))
            self.assertTrue(42<=val<=180)
    def test_invalid_input(self):
        rgb=np.zeros((400,3))
        with self.assertRaises(ValueError): extract(rgb,30,"POS")
    def test_reproducibility(self):
        a,af,ap=simulate_rgb(78,30,22,np.random.default_rng(2027),"motion_artifact")
        b,bf,bp=simulate_rgb(78,30,22,np.random.default_rng(2027),"motion_artifact")
        self.assertTrue(np.array_equal(a,b))
        self.assertEqual(ap,bp)

if __name__ == '__main__': unittest.main()
