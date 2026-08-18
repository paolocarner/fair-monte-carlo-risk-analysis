#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAIR Monte Carlo Simulation Tool
Based on Factor Analysis of Information Risk (FAIR) methodology

Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)
LEF = Threat Event Frequency (TEF) × Vulnerability (Vuln)
"""

import os

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Optional
import json

# Configuration constants
PERT_LAMBDA_PARAMETER = 4  # Shape parameter for PERT distribution
LOGNORMAL_SIGMA_DIVISOR = 4  # Divisor for lognormal sigma estimation
MIN_POSITIVE_VALUE = 1e-10  # Minimum value to prevent log(0) errors


def derive_tef_from_contact(cf_min: float, cf_mode: float, cf_max: float,
                             poa: float) -> tuple:
    """
    Derive Threat Event Frequency (TEF) distribution parameters from Contact
    Frequency (CF) and Probability of Action (PoA), per the Open Group O-RT
    Standard v3.0.1, Section 4.3.1:

        TEF = Contact Frequency (CF) x Probability of Action (PoA)

    CF is a count of contacts/year (e.g. "3,000 malicious emails reaching the
    org per year"), NOT a percentage -- per O-RT Section 2.4 / Table 1, Contact
    Frequency's unit of measure is events per unit time. PoA is the probability,
    once contact occurs, that the threat agent acts (O-RT Section 2.13) and is
    a fraction in [0, 1].

    Mathematically, if CF ~ PERT(cf_min, cf_mode, cf_max) and TEF = CF * poa
    for a constant poa, then TEF ~ PERT(poa*cf_min, poa*cf_mode, poa*cf_max).
    This holds because the PERT shape parameters (alpha, beta) depend only on
    the ratios (mode-min)/(max-min) and (max-mode)/(max-min), which are
    invariant under positive linear scaling of all three inputs -- so scaling
    every parameter by the same positive constant scales the resulting
    distribution by that constant. This lets the simulation engine keep
    treating TEF as a single PERT-sampled input with no changes to
    FAIRMonteCarloSimulation.run_simulation() itself.

    Parameters:
    -----------
    cf_min, cf_mode, cf_max: Contact Frequency distribution parameters
        (contacts per year; must satisfy cf_min <= cf_mode <= cf_max).
    poa: Probability of Action, in [0, 1].

    Returns:
    --------
    (tef_min, tef_mode, tef_max) tuple, suitable for
    FAIRDistribution('pert', tef_min, tef_mode, tef_max).
    """
    if not (0.0 <= poa <= 1.0):
        raise ValueError(f"poa must be between 0 and 1, got {poa}")
    if not (cf_min <= cf_mode <= cf_max):
        raise ValueError(
            f"Contact Frequency requires cf_min <= cf_mode <= cf_max, "
            f"got min={cf_min}, mode={cf_mode}, max={cf_max}"
        )
    return cf_min * poa, cf_mode * poa, cf_max * poa


@dataclass
class FAIRDistribution:
    """Represents a probability distribution for FAIR parameters"""
    dist_type: str  # 'pert', 'lognormal', 'uniform', 'triangular'
    min_val: float
    mode_val: float = None
    max_val: float = None
    mean: float = None
    std: float = None

    def __post_init__(self):
        valid_types = {'pert', 'lognormal', 'uniform', 'triangular'}
        if self.dist_type not in valid_types:
            raise ValueError(
                f"Unknown distribution type: '{self.dist_type}'. "
                f"Must be one of: {sorted(valid_types)}"
            )
        if self.dist_type in ('pert', 'triangular'):
            if self.mode_val is None:
                raise ValueError(f"{self.dist_type} distribution requires mode_val")
            if self.max_val is None:
                raise ValueError(f"{self.dist_type} distribution requires max_val")
        if self.dist_type == 'uniform' and self.max_val is None:
            raise ValueError("uniform distribution requires max_val")
        if self.dist_type == 'lognormal' and self.mean is None and self.std is None:
            if self.mode_val is None or self.max_val is None:
                raise ValueError(
                    "lognormal distribution requires either (mean, std) "
                    "or (min_val, mode_val, max_val)"
                )

    def sample(self, size: int) -> np.ndarray:
        """Generate random samples from the distribution"""
        if self.dist_type == 'pert':
            if not (self.min_val <= self.mode_val <= self.max_val):
                raise ValueError(
                    f"PERT distribution requires min_val <= mode_val <= max_val, "
                    f"got min={self.min_val}, mode={self.mode_val}, max={self.max_val}"
                )
            lambda_param = PERT_LAMBDA_PARAMETER
            if self.max_val == self.min_val:
                return np.full(size, self.min_val)
            alpha = 1 + lambda_param * (self.mode_val - self.min_val) / (self.max_val - self.min_val)
            beta = 1 + lambda_param * (self.max_val - self.mode_val) / (self.max_val - self.min_val)
            beta_samples = np.random.beta(alpha, beta, size)
            return self.min_val + beta_samples * (self.max_val - self.min_val)

        elif self.dist_type == 'lognormal':
            if self.mean is not None and self.std is not None:
                if self.mean <= 0:
                    raise ValueError(f"Lognormal distribution requires positive mean, got {self.mean}")
                if self.std <= 0:
                    raise ValueError(f"Lognormal distribution requires positive std, got {self.std}")
                variance = self.std ** 2
                mu = np.log(self.mean ** 2 / np.sqrt(variance + self.mean ** 2))
                sigma = np.sqrt(np.log(1 + variance / (self.mean ** 2)))
                return np.random.lognormal(mu, sigma, size)
            else:
                min_val_safe = max(self.min_val, MIN_POSITIVE_VALUE)
                mode_val_safe = max(self.mode_val, MIN_POSITIVE_VALUE)
                max_val_safe = max(self.max_val, MIN_POSITIVE_VALUE)
                if min_val_safe >= max_val_safe:
                    raise ValueError(
                        f"Lognormal distribution requires min_val < max_val, "
                        f"got min={self.min_val}, max={self.max_val}"
                    )
                mu = np.log(mode_val_safe)
                sigma = (np.log(max_val_safe) - np.log(min_val_safe)) / LOGNORMAL_SIGMA_DIVISOR
                return np.random.lognormal(mu, sigma, size)

        elif self.dist_type == 'uniform':
            if self.min_val >= self.max_val:
                raise ValueError(
                    f"Uniform distribution requires min_val < max_val, "
                    f"got min={self.min_val}, max={self.max_val}"
                )
            return np.random.uniform(self.min_val, self.max_val, size)

        elif self.dist_type == 'triangular':
            if not (self.min_val <= self.mode_val <= self.max_val):
                raise ValueError(
                    f"Triangular distribution requires min_val <= mode_val <= max_val, "
                    f"got min={self.min_val}, mode={self.mode_val}, max={self.max_val}"
                )
            return np.random.triangular(self.min_val, self.mode_val, self.max_val, size)


class FAIRMonteCarloSimulation:
    """FAIR-based Monte Carlo simulation engine"""

    def __init__(self, n_simulations: int = 10000, random_seed: Optional[int] = None):
        self.n_simulations = n_simulations
        self.random_seed = random_seed
        self.results = None

    def run_simulation(self,
                       tef_dist: FAIRDistribution,
                       vuln_prob: float,
                       primary_loss_dist: FAIRDistribution,
                       secondary_loss_dist: FAIRDistribution = None,
                       secondary_loss_prob: float = 0.0) -> Dict:
        """
        Run FAIR Monte Carlo simulation

        Parameters:
        -----------
        tef_dist: Distribution for Threat Event Frequency (events per year)
        vuln_prob: Probability of vulnerability (0-1)
        primary_loss_dist: Distribution for Primary Loss Magnitude (€)
        secondary_loss_dist: Distribution for Secondary Loss Magnitude (€)
        secondary_loss_prob: Probability that secondary losses occur (0-1)

        Returns:
        --------
        Dictionary with simulation results and statistics
        """
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

        # Sample Threat Event Frequency and compute Loss Event Frequency
        tef_samples = tef_dist.sample(self.n_simulations)
        lef_samples = tef_samples * vuln_prob

        # Number of actual loss events per simulation (Poisson-distributed)
        actual_events = np.random.poisson(lef_samples)

        # --- Vectorized loss calculation ---
        # Instead of looping over simulations, sample all events at once
        # and aggregate per-simulation using np.bincount (O(n) vs O(n*k))
        total_events = int(np.sum(actual_events))
        annual_losses = np.zeros(self.n_simulations)

        if total_events > 0:
            all_primary = primary_loss_dist.sample(total_events)

            if secondary_loss_dist is not None and secondary_loss_prob > 0:
                all_secondary = secondary_loss_dist.sample(total_events)
                has_secondary = np.random.random(total_events) < secondary_loss_prob
                all_loss = all_primary + np.where(has_secondary, all_secondary, 0.0)
            else:
                all_loss = all_primary

            # Map each sampled event back to its simulation index
            sim_indices = np.repeat(np.arange(self.n_simulations), actual_events)
            annual_losses = np.bincount(sim_indices, weights=all_loss, minlength=self.n_simulations)

        self.results = {
            'annual_losses': annual_losses,
            'lef_samples': lef_samples,
            'actual_events': actual_events,
            'tef_samples': tef_samples
        }

        return self._calculate_statistics(annual_losses, lef_samples)

    def _calculate_statistics(self, annual_losses: np.ndarray, lef_samples: np.ndarray) -> Dict:
        """Calculate key statistics from simulation results"""
        non_zero_losses = annual_losses[annual_losses > 0]

        stats = {
            'ale_mean': np.mean(annual_losses),
            'ale_median': np.median(annual_losses),
            'ale_std': np.std(annual_losses),
            'ale_min': np.min(annual_losses),
            'ale_max': np.max(annual_losses),
            'percentiles': {
                '10th': np.percentile(annual_losses, 10),
                '25th': np.percentile(annual_losses, 25),
                '50th': np.percentile(annual_losses, 50),
                '75th': np.percentile(annual_losses, 75),
                '90th': np.percentile(annual_losses, 90),
                '95th': np.percentile(annual_losses, 95),
                '99th': np.percentile(annual_losses, 99)
            },
            'lef_mean': np.mean(lef_samples),
            'lef_median': np.median(lef_samples),
            'probability_of_loss': len(non_zero_losses) / len(annual_losses),
            'mean_loss_given_event': np.mean(non_zero_losses) if len(non_zero_losses) > 0 else 0
        }

        return stats

    def print_results(self, stats: Dict, currency: str = "€"):
        """Print formatted simulation results"""
        print("\n" + "="*60)
        print("FAIR MONTE CARLO SIMULATION RESULTS")
        print("="*60)
        print(f"\nNumber of simulations: {self.n_simulations:,}")

        print(f"\n📊 ANNUAL LOSS EXPECTANCY (ALE)")
        print(f"Mean ALE:          {currency}{stats['ale_mean']:,.2f}")
        print(f"Median ALE:        {currency}{stats['ale_median']:,.2f}")
        print(f"Std Deviation:     {currency}{stats['ale_std']:,.2f}")

        print(f"\n📈 PERCENTILES")
        for pct, val in stats['percentiles'].items():
            print(f"{pct:>5} percentile:  {currency}{val:,.2f}")

        print(f"\n🎯 LOSS EVENT FREQUENCY")
        print(f"Mean LEF:          {stats['lef_mean']:.4f} events/year")
        print(f"Median LEF:        {stats['lef_median']:.4f} events/year")

        print(f"\n💡 KEY INSIGHTS")
        print(f"Probability of at least one loss event: {stats['probability_of_loss']*100:.1f}%")
        if stats['mean_loss_given_event'] > 0:
            print(f"Mean loss given an event occurs:        {currency}{stats['mean_loss_given_event']:,.2f}")

        print("\n" + "="*60 + "\n")

    def plot_results(self, stats: Dict, currency: str = "€", save_path: str = None):
        """Generate visualization of simulation results (CLI use; requires matplotlib)"""
        import matplotlib.pyplot as plt  # lazy import — not needed by the dashboard

        if self.results is None:
            raise ValueError("No simulation results available. Run simulation first.")

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('FAIR Monte Carlo Simulation Results', fontsize=16, fontweight='bold')

        annual_losses = self.results['annual_losses']
        lef_samples = self.results['lef_samples']

        # 1. Annual Loss Distribution
        ax1 = axes[0, 0]
        ax1.hist(annual_losses, bins=50, edgecolor='black', alpha=0.7, color='#2E86AB')
        ax1.axvline(stats['ale_mean'], color='red', linestyle='--', linewidth=2,
                    label=f'Mean: {currency}{stats["ale_mean"]:,.0f}')
        ax1.axvline(stats['ale_median'], color='orange', linestyle='--', linewidth=2,
                    label=f'Median: {currency}{stats["ale_median"]:,.0f}')
        ax1.set_xlabel(f'Annual Loss ({currency})', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Distribution of Annual Losses', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Cumulative Distribution (Exceedance Curve)
        ax2 = axes[0, 1]
        sorted_losses = np.sort(annual_losses)
        exceedance_prob = 1 - np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
        ax2.plot(sorted_losses, exceedance_prob * 100, linewidth=2, color='#A23B72')
        ax2.set_xlabel(f'Annual Loss ({currency})', fontsize=11)
        ax2.set_ylabel('Probability of Exceedance (%)', fontsize=11)
        ax2.set_title('Loss Exceedance Curve', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        for pct in [95, 99]:
            pct_val = stats['percentiles'][f'{pct}th']
            ax2.axvline(pct_val, color='red', linestyle=':', alpha=0.5)
            ax2.text(pct_val, 50, f'{pct}th', rotation=90, va='center', fontsize=9)

        # 3. Loss Event Frequency Distribution
        ax3 = axes[1, 0]
        ax3.hist(lef_samples, bins=50, edgecolor='black', alpha=0.7, color='#F18F01')
        ax3.axvline(stats['lef_mean'], color='red', linestyle='--', linewidth=2,
                    label=f'Mean: {stats["lef_mean"]:.3f}')
        ax3.set_xlabel('Loss Event Frequency (events/year)', fontsize=11)
        ax3.set_ylabel('Frequency', fontsize=11)
        ax3.set_title('Distribution of Loss Event Frequency', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Box plot summary
        ax4 = axes[1, 1]
        ax4.boxplot([annual_losses], vert=True, patch_artist=True,
                    showmeans=True, meanline=True,
                    boxprops=dict(facecolor='#06A77D', alpha=0.7),
                    meanprops=dict(color='red', linewidth=2),
                    medianprops=dict(color='orange', linewidth=2))
        ax4.set_ylabel(f'Annual Loss ({currency})', fontsize=11)
        ax4.set_title('Annual Loss Distribution Summary', fontsize=12, fontweight='bold')
        ax4.set_xticklabels(['ALE'])
        ax4.grid(True, alpha=0.3, axis='y')
        textstr = (
            f'Mean: {currency}{stats["ale_mean"]:,.0f}\n'
            f'Median: {currency}{stats["ale_median"]:,.0f}\n'
            f'95th: {currency}{stats["percentiles"]["95th"]:,.0f}\n'
            f'99th: {currency}{stats["percentiles"]["99th"]:,.0f}'
        )
        ax4.text(0.98, 0.97, textstr, transform=ax4.transAxes, fontsize=10,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")

        plt.show()

    def export_results(self, stats: Dict, scenario_name: str,
                       filename: str, output_dir: str = ".") -> Dict[str, str]:
        """
        Export results to JSON and CSV.

        Parameters:
        -----------
        stats: Statistics dict from run_simulation()
        scenario_name: Human-readable name for the scenario
        filename: Base CSV filename (e.g. 'results.csv')
        output_dir: Directory to write files into (default: current directory)

        Returns:
        --------
        Dict with keys 'json' and 'csv' containing the written file paths.
        """
        os.makedirs(output_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(filename))[0]
        json_path = os.path.join(output_dir, base + '.json')
        csv_path = os.path.join(output_dir, base + '.csv')

        json_data = {
            'scenario_name': scenario_name,
            'n_simulations': self.n_simulations,
            'statistics': stats
        }
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"Statistics exported to: {json_path}")

        written = {'json': json_path}

        if self.results is not None:
            df = pd.DataFrame({
                'annual_loss': self.results['annual_losses'],
                'loss_event_frequency': self.results['lef_samples'],
                'threat_event_frequency': self.results['tef_samples'],
                'actual_events': self.results['actual_events']
            })
            df.to_csv(csv_path, index=False)
            print(f"Raw simulation data exported to: {csv_path}")
            written['csv'] = csv_path

        return written


def example_ransomware_scenario():
    """Example: Ransomware attack scenario for SMB"""
    print("\n🔐 EXAMPLE SCENARIO: Ransomware Attack on EU SMB")
    print("="*60)

    sim = FAIRMonteCarloSimulation(n_simulations=10000)

    tef = FAIRDistribution(dist_type='pert', min_val=100, mode_val=300, max_val=1000)
    vulnerability = 0.02

    primary_loss = FAIRDistribution(dist_type='lognormal', min_val=10000, mode_val=50000, max_val=200000)
    secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=5000, mode_val=25000, max_val=150000)

    stats = sim.run_simulation(
        tef_dist=tef,
        vuln_prob=vulnerability,
        primary_loss_dist=primary_loss,
        secondary_loss_dist=secondary_loss,
        secondary_loss_prob=0.4
    )

    sim.print_results(stats, currency="€")
    sim.plot_results(stats, currency="€", save_path="ransomware_risk_analysis.png")
    sim.export_results(stats, "Ransomware Attack", "ransomware_simulation_results.csv")


if __name__ == "__main__":
    example_ransomware_scenario()

    print("\n" + "="*60)
    print("To create your own scenario, use the following structure:")
    print("="*60)
    print("""
from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution

# Create simulation
sim = FAIRMonteCarloSimulation(n_simulations=10000)

# Define your parameters
tef = FAIRDistribution(dist_type='pert', min_val=X, mode_val=Y, max_val=Z)
vulnerability = 0.XX  # Probability 0-1

primary_loss = FAIRDistribution(dist_type='lognormal', min_val=X, mode_val=Y, max_val=Z)
secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=X, mode_val=Y, max_val=Z)

# Run simulation
stats = sim.run_simulation(
    tef_dist=tef,
    vuln_prob=vulnerability,
    primary_loss_dist=primary_loss,
    secondary_loss_dist=secondary_loss,
    secondary_loss_prob=0.X
)

# View results
sim.print_results(stats, currency="€")
sim.plot_results(stats, currency="€")
    """)
