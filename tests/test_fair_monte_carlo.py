"""
Unit tests for fair_monte_carlo.py

Run with:  pytest tests/ -v
"""
import json
import os

import numpy as np
import pytest

from fair_monte_carlo import (
    LOGNORMAL_SIGMA_DIVISOR,
    PERT_LAMBDA_PARAMETER,
    FAIRDistribution,
    FAIRMonteCarloSimulation,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEED = 42


def make_tef(min_val=10, mode_val=30, max_val=100):
    return FAIRDistribution(dist_type="pert", min_val=min_val, mode_val=mode_val, max_val=max_val)


def make_primary(min_val=1_000, mode_val=5_000, max_val=20_000):
    return FAIRDistribution(dist_type="lognormal", min_val=min_val, mode_val=mode_val, max_val=max_val)


def make_secondary(min_val=500, mode_val=2_000, max_val=10_000):
    return FAIRDistribution(dist_type="lognormal", min_val=min_val, mode_val=mode_val, max_val=max_val)


# ---------------------------------------------------------------------------
# FAIRDistribution — validation (__post_init__)
# ---------------------------------------------------------------------------

class TestFAIRDistributionValidation:

    def test_invalid_dist_type_raises(self):
        with pytest.raises(ValueError, match="Unknown distribution type"):
            FAIRDistribution(dist_type="gaussian", min_val=1)

    def test_pert_missing_mode_raises(self):
        with pytest.raises(ValueError, match="mode_val"):
            FAIRDistribution(dist_type="pert", min_val=1, max_val=10)

    def test_pert_missing_max_raises(self):
        with pytest.raises(ValueError, match="max_val"):
            FAIRDistribution(dist_type="pert", min_val=1, mode_val=5)

    def test_triangular_missing_mode_raises(self):
        with pytest.raises(ValueError, match="mode_val"):
            FAIRDistribution(dist_type="triangular", min_val=1, max_val=10)

    def test_uniform_missing_max_raises(self):
        with pytest.raises(ValueError, match="max_val"):
            FAIRDistribution(dist_type="uniform", min_val=1)

    def test_lognormal_missing_params_raises(self):
        # Neither (mean, std) nor (min, mode, max) provided
        with pytest.raises(ValueError, match="lognormal"):
            FAIRDistribution(dist_type="lognormal", min_val=1)

    def test_valid_pert_no_exception(self):
        FAIRDistribution(dist_type="pert", min_val=1, mode_val=5, max_val=10)

    def test_valid_lognormal_with_mean_std_no_exception(self):
        FAIRDistribution(dist_type="lognormal", min_val=0, mean=5_000.0, std=2_000.0)

    def test_valid_lognormal_with_min_mode_max_no_exception(self):
        FAIRDistribution(dist_type="lognormal", min_val=1_000, mode_val=5_000, max_val=20_000)

    def test_valid_uniform_no_exception(self):
        FAIRDistribution(dist_type="uniform", min_val=1, max_val=10)

    def test_valid_triangular_no_exception(self):
        FAIRDistribution(dist_type="triangular", min_val=1, mode_val=5, max_val=10)


# ---------------------------------------------------------------------------
# FAIRDistribution — sampling
# ---------------------------------------------------------------------------

class TestFAIRDistributionSampling:

    SIZE = 5_000

    def test_pert_samples_within_bounds(self):
        dist = FAIRDistribution(dist_type="pert", min_val=10, mode_val=30, max_val=100)
        samples = dist.sample(self.SIZE)
        assert samples.shape == (self.SIZE,)
        assert np.all(samples >= 10)
        assert np.all(samples <= 100)

    def test_pert_degenerate_returns_constant(self):
        """When min == max == mode, sample should be a constant."""
        dist = FAIRDistribution(dist_type="pert", min_val=50, mode_val=50, max_val=50)
        samples = dist.sample(100)
        assert np.all(samples == 50)

    def test_pert_mode_ordering_error(self):
        dist = FAIRDistribution(dist_type="pert", min_val=10, mode_val=5, max_val=100)
        with pytest.raises(ValueError, match="min_val <= mode_val <= max_val"):
            dist.sample(10)

    def test_lognormal_min_mode_max_all_positive(self):
        dist = make_primary()
        samples = dist.sample(self.SIZE)
        assert samples.shape == (self.SIZE,)
        assert np.all(samples > 0)

    def test_lognormal_mean_std_all_positive(self):
        dist = FAIRDistribution(dist_type="lognormal", min_val=0, mean=10_000.0, std=3_000.0)
        samples = dist.sample(self.SIZE)
        assert np.all(samples > 0)

    def test_lognormal_bad_mean_raises(self):
        dist = FAIRDistribution(dist_type="lognormal", min_val=0, mean=-1.0, std=1.0)
        with pytest.raises(ValueError, match="positive mean"):
            dist.sample(10)

    def test_lognormal_bad_std_raises(self):
        dist = FAIRDistribution(dist_type="lognormal", min_val=0, mean=1.0, std=-1.0)
        with pytest.raises(ValueError, match="positive std"):
            dist.sample(10)

    def test_lognormal_min_equals_max_raises(self):
        dist = FAIRDistribution(dist_type="lognormal", min_val=5_000, mode_val=5_000, max_val=5_000)
        with pytest.raises(ValueError, match="min_val < max_val"):
            dist.sample(10)

    def test_uniform_samples_within_bounds(self):
        dist = FAIRDistribution(dist_type="uniform", min_val=0, max_val=100)
        samples = dist.sample(self.SIZE)
        assert samples.shape == (self.SIZE,)
        assert np.all(samples >= 0)
        assert np.all(samples <= 100)

    def test_uniform_min_equals_max_raises(self):
        dist = FAIRDistribution(dist_type="uniform", min_val=5, max_val=5)
        with pytest.raises(ValueError, match="min_val < max_val"):
            dist.sample(10)

    def test_triangular_samples_within_bounds(self):
        dist = FAIRDistribution(dist_type="triangular", min_val=10, mode_val=40, max_val=100)
        samples = dist.sample(self.SIZE)
        assert samples.shape == (self.SIZE,)
        assert np.all(samples >= 10)
        assert np.all(samples <= 100)

    def test_triangular_mode_ordering_error(self):
        dist = FAIRDistribution(dist_type="triangular", min_val=50, mode_val=10, max_val=100)
        with pytest.raises(ValueError, match="min_val <= mode_val <= max_val"):
            dist.sample(10)

    def test_sample_size_zero(self):
        dist = make_primary()
        samples = dist.sample(0)
        assert samples.shape == (0,)


# ---------------------------------------------------------------------------
# FAIRMonteCarloSimulation
# ---------------------------------------------------------------------------

class TestFAIRMonteCarloSimulation:

    N = 5_000  # keep tests fast

    # --- reproducibility ---

    def test_reproducibility_with_seed(self):
        tef = make_tef()
        primary = make_primary()

        sim1 = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats1 = sim1.run_simulation(tef, 0.1, primary)

        sim2 = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats2 = sim2.run_simulation(tef, 0.1, primary)

        assert stats1["ale_mean"] == stats2["ale_mean"]
        assert stats1["ale_median"] == stats2["ale_median"]

    def test_different_seeds_differ(self):
        tef = make_tef()
        primary = make_primary()

        sim1 = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=1)
        stats1 = sim1.run_simulation(tef, 0.1, primary)

        sim2 = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=2)
        stats2 = sim2.run_simulation(tef, 0.1, primary)

        # Extremely unlikely to match exactly with different seeds
        assert stats1["ale_mean"] != stats2["ale_mean"]

    # --- zero vulnerability ---

    def test_zero_vulnerability_zero_ale(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, vuln_prob=0.0, primary_loss_dist=primary)
        assert stats["ale_mean"] == 0.0
        assert stats["ale_median"] == 0.0
        assert stats["probability_of_loss"] == 0.0

    # --- results structure ---

    def test_results_dict_keys(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)

        required_keys = {
            "ale_mean", "ale_median", "ale_std", "ale_min", "ale_max",
            "lef_mean", "lef_median", "probability_of_loss",
            "mean_loss_given_event", "percentiles",
        }
        assert required_keys.issubset(stats.keys())

    def test_percentiles_keys(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)
        expected_pct_keys = {"10th", "25th", "50th", "75th", "90th", "95th", "99th"}
        assert expected_pct_keys == set(stats["percentiles"].keys())

    def test_internal_results_arrays(self):
        """After run_simulation(), sim.results should hold arrays of correct length."""
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        sim.run_simulation(tef, 0.1, primary)

        assert sim.results["annual_losses"].shape == (self.N,)
        assert sim.results["lef_samples"].shape == (self.N,)
        assert sim.results["tef_samples"].shape == (self.N,)
        assert sim.results["actual_events"].shape == (self.N,)

    # --- statistical properties ---

    def test_percentiles_ordered(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)

        p = stats["percentiles"]
        assert p["10th"] <= p["25th"] <= p["50th"] <= p["75th"] <= p["90th"] <= p["95th"] <= p["99th"]

    def test_annual_losses_non_negative(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        sim.run_simulation(tef, 0.1, primary)
        assert np.all(sim.results["annual_losses"] >= 0)

    def test_secondary_losses_increase_ale(self):
        """ALE with secondary losses should be >= ALE without (on average)."""
        tef = make_tef()
        primary = make_primary()
        secondary = make_secondary()

        sim_no_sec = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats_no_sec = sim_no_sec.run_simulation(tef, 0.5, primary)

        sim_with_sec = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats_with_sec = sim_with_sec.run_simulation(tef, 0.5, primary, secondary, 0.5)

        assert stats_with_sec["ale_mean"] >= stats_no_sec["ale_mean"]

    def test_higher_vulnerability_increases_ale(self):
        """Doubling vulnerability should produce a higher mean ALE."""
        tef = make_tef()
        primary = make_primary()

        sim_low = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats_low = sim_low.run_simulation(tef, vuln_prob=0.05, primary_loss_dist=primary)

        sim_high = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats_high = sim_high.run_simulation(tef, vuln_prob=0.50, primary_loss_dist=primary)

        assert stats_high["ale_mean"] > stats_low["ale_mean"]

    def test_probability_of_loss_in_range(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)
        assert 0.0 <= stats["probability_of_loss"] <= 1.0

    def test_mean_loss_given_event_positive_when_losses_exist(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.5, primary)
        # With vuln=0.5 and reasonable TEF, there should be some losses
        if stats["probability_of_loss"] > 0:
            assert stats["mean_loss_given_event"] > 0

    def test_ale_mean_approx_median_below_mean(self):
        """For right-skewed distributions, median <= mean."""
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=20_000, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.5, primary)
        assert stats["ale_median"] <= stats["ale_mean"]

    # --- no secondary (secondary_loss_dist=None) ---

    def test_no_secondary_dist_runs_fine(self):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)  # no secondary args
        assert stats["ale_mean"] >= 0

    # --- export_results ---

    def test_export_results_returns_paths(self, tmp_path):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)

        paths = sim.export_results(
            stats,
            scenario_name="Test Scenario",
            filename="test_output.csv",
            output_dir=str(tmp_path),
        )
        assert "json" in paths
        assert "csv" in paths
        assert os.path.isfile(paths["json"])
        assert os.path.isfile(paths["csv"])

    def test_export_results_json_content(self, tmp_path):
        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)

        paths = sim.export_results(
            stats,
            scenario_name="JSON Test",
            filename="out.csv",
            output_dir=str(tmp_path),
        )
        with open(paths["json"]) as f:
            data = json.load(f)
        assert data["scenario_name"] == "JSON Test"
        assert data["n_simulations"] == self.N
        assert "statistics" in data
        assert "ale_mean" in data["statistics"]

    def test_export_results_csv_row_count(self, tmp_path):
        import pandas as pd

        tef = make_tef()
        primary = make_primary()
        sim = FAIRMonteCarloSimulation(n_simulations=self.N, random_seed=SEED)
        stats = sim.run_simulation(tef, 0.1, primary)

        paths = sim.export_results(
            stats,
            scenario_name="CSV Test",
            filename="out.csv",
            output_dir=str(tmp_path),
        )
        df = pd.read_csv(paths["csv"])
        assert len(df) == self.N
        assert "annual_loss" in df.columns
        assert "loss_event_frequency" in df.columns

    def test_export_results_without_run_no_csv(self, tmp_path):
        """If results is None (simulation never run), no CSV should be written."""
        sim = FAIRMonteCarloSimulation(n_simulations=self.N)
        dummy_stats = {
            "ale_mean": 0, "ale_median": 0, "ale_std": 0, "ale_min": 0, "ale_max": 0,
            "lef_mean": 0, "lef_median": 0, "probability_of_loss": 0,
            "mean_loss_given_event": 0, "percentiles": {}
        }
        paths = sim.export_results(
            dummy_stats,
            scenario_name="No-run test",
            filename="norun.csv",
            output_dir=str(tmp_path),
        )
        assert "json" in paths
        assert "csv" not in paths


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------

class TestConstants:

    def test_pert_lambda_positive(self):
        assert PERT_LAMBDA_PARAMETER > 0

    def test_lognormal_sigma_divisor_positive(self):
        assert LOGNORMAL_SIGMA_DIVISOR > 0
