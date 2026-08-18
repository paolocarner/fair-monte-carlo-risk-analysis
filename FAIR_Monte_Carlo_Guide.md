# FAIR Monte Carlo Simulation Guide

## Overview

This tool implements the **Factor Analysis of Information Risk (FAIR)** methodology using Monte Carlo simulations to provide probabilistic risk quantification. It's designed specifically for cybersecurity risk analysis for European SMBs.

## Core FAIR Concepts

### Risk Formula
```
Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)
```

### Loss Event Frequency (LEF)
```
LEF = Threat Event Frequency (TEF) × Vulnerability (Vuln)
TEF = Contact Frequency (CF) × Probability of Action (PoA)
```

Where (per the Open Group O-RT Standard v3.0.1):
- **Contact Frequency (CF)**: How often a threat agent contacts your asset, per year. A **count** (e.g. "3,000 malicious emails/year"), NOT a percentage.
- **Probability of Action (PoA)**: Once contact occurs, the probability the threat agent acts. A percentage (0-100%).
- **TEF**: CF × PoA — how often a threat *actually attempts* to act against your asset. This tool computes TEF from CF and PoA automatically; you don't multiply them yourself.
- **Vulnerability**: The probability a threat event (already counted in TEF) becomes a loss event — i.e. that the threat agent's capability exceeds your controls' resistance strength. A single percentage, applied on top of TEF — it is *not* multiplied by Contact Frequency or Probability of Action again, since those are already fully accounted for in TEF.

### Loss Magnitude (LM)
```
LM = Primary Loss + Secondary Loss
```

- **Primary Loss**: Direct costs (recovery, ransom, system replacement, downtime)
- **Secondary Loss**: Indirect costs (reputation damage, customer churn, regulatory fines, legal costs)

---

## Quick Start

### 1. Basic Usage

```python
from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution

# Create simulation with 10,000 iterations
sim = FAIRMonteCarloSimulation(n_simulations=10000)

# Define Threat Event Frequency (attempts per year)
tef = FAIRDistribution(
    dist_type='pert',
    min_val=100,    # Minimum attempts
    mode_val=300,   # Most likely attempts
    max_val=1000    # Maximum attempts
)

# Define vulnerability (probability of success)
vulnerability = 0.02  # 2% of attempts succeed

# Define Primary Loss (direct costs in €)
primary_loss = FAIRDistribution(
    dist_type='lognormal',
    min_val=10000,
    mode_val=50000,
    max_val=200000
)

# Define Secondary Loss (indirect costs in €)
secondary_loss = FAIRDistribution(
    dist_type='lognormal',
    min_val=5000,
    mode_val=25000,
    max_val=150000
)

# Run simulation
stats = sim.run_simulation(
    tef_dist=tef,
    vuln_prob=vulnerability,
    primary_loss_dist=primary_loss,
    secondary_loss_dist=secondary_loss,
    secondary_loss_prob=0.4  # 40% chance secondary losses occur
)

# Display results
sim.print_results(stats, currency="€")
sim.plot_results(stats, currency="€", save_path="risk_analysis.png")
sim.export_results(stats, "My Scenario", "results.csv")
```

---

## Distribution Types

### 1. PERT Distribution
**Best for**: Frequencies, probabilities with expert estimates
```python
FAIRDistribution(
    dist_type='pert',
    min_val=100,    # Minimum value
    mode_val=300,   # Most likely value
    max_val=1000    # Maximum value
)
```
- Smooth, realistic distribution
- Mode doesn't need to be in middle
- Good for modeling expert judgment

### 2. Lognormal Distribution
**Best for**: Loss magnitudes (financial impacts)
```python
FAIRDistribution(
    dist_type='lognormal',
    min_val=10000,
    mode_val=50000,
    max_val=200000
)
```
- Realistic for costs (right-skewed)
- Most losses are small, few are large
- Industry standard for financial modeling

### 3. Uniform Distribution
**Best for**: Complete uncertainty
```python
FAIRDistribution(
    dist_type='uniform',
    min_val=100,
    max_val=1000
)
```

### 4. Triangular Distribution
**Best for**: Simple three-point estimates
```python
FAIRDistribution(
    dist_type='triangular',
    min_val=100,
    mode_val=300,
    max_val=1000
)
```

---

## Practical Scenarios for SMBs

### Scenario 1: Data Breach (GDPR Violation)

```python
sim = FAIRMonteCarloSimulation(n_simulations=10000)

# Threat Event Frequency: attempts specifically against this org per year
# (this example estimates TEF directly rather than decomposing into CF x PoA
# -- both are valid per the O-RT Standard; decompose when you have separate
# contact-volume and action-rate data, estimate TEF directly otherwise)
tef = FAIRDistribution(dist_type='pert', min_val=50, mode_val=150, max_val=500)

# Vulnerability: probability one of those attempts succeeds and becomes a
# loss event, applied directly on top of TEF -- NOT a product of sub-factors
# that are already baked into TEF (see CHANGELOG.md for why that double-counts).
# Illustrative estimate -- validate against real control-effectiveness data.
vulnerability = 0.0016  # ~0.16%

# Primary: Incident response, forensics, notification, credit monitoring
primary_loss = FAIRDistribution(dist_type='lognormal', min_val=15000, mode_val=75000, max_val=300000)

# Secondary: GDPR fines, reputation, customer churn
secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=20000, mode_val=100000, max_val=500000)

stats = sim.run_simulation(tef, vulnerability, primary_loss, secondary_loss, secondary_loss_prob=0.5)
```

### Scenario 2: Business Email Compromise (BEC)

```python
# Threat Event Frequency: phishing/BEC attempts against this org per year
tef = FAIRDistribution(dist_type='pert', min_val=200, mode_val=500, max_val=1200)

# Vulnerability: probability an attempt succeeds (email reaches inbox,
# employee acts, transfer completes) -- a single estimate applied on top
# of TEF, not multiplied from separate contact/action/rate factors.
vulnerability = 0.0011  # ~0.11%

# Primary: Wire transfer losses, recovery costs
primary_loss = FAIRDistribution(dist_type='lognormal', min_val=5000, mode_val=30000, max_val=150000)

# Secondary: Bank fees, legal, reputation
secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=2000, mode_val=10000, max_val=50000)

stats = sim.run_simulation(tef, vulnerability, primary_loss, secondary_loss, secondary_loss_prob=0.3)
```

### Scenario 3: DDoS Attack

```python
# Threat Event Frequency: DDoS attempts on web services per year
tef = FAIRDistribution(dist_type='pert', min_val=10, mode_val=30, max_val=100)

# Vulnerability: probability an attempt overwhelms capacity and causes a
# measurable business-impacting outage, despite mitigation already in place.
vulnerability = 0.078  # ~7.8% -- higher than the other examples because DDoS
                        # attempts are comparatively easy to launch and mitigation
                        # doesn't always fully absorb them

# Primary: Downtime revenue loss, mitigation service costs
primary_loss = FAIRDistribution(dist_type='lognormal', min_val=3000, mode_val=15000, max_val=80000)

# Secondary: Customer satisfaction, SLA penalties
secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=1000, mode_val=8000, max_val=40000)

stats = sim.run_simulation(tef, vulnerability, primary_loss, secondary_loss, secondary_loss_prob=0.6)
```

---

## Estimating Parameters

### Contact Frequency (CF) & Probability of Action (PoA) → TEF

**Sources for CF estimates:**
1. **Vendor reports**: Verizon DBIR, IBM X-Force, Microsoft Security Intelligence
2. **Your data**: Firewall logs, email gateway, SIEM alerts
3. **Industry peers**: Information sharing groups (ISACs)
4. **Expert judgment**: SME interviews

**Example for ransomware (phishing vector):**
- Check email gateway: 50-200 malicious emails/month reaching the org (before any filtering the user acts on)
- Annualize: 600-2,400 contacts/year → this is **Contact Frequency**, use PERT with min=750, mode=1,200, max=2,400
- Estimate what fraction of those contacts get acted upon (opened/clicked): e.g. 8% → **Probability of Action = 0.08**
- The tool computes **TEF = CF × PoA** for you — you don't need to multiply these yourself, and you don't enter TEF directly when working at this level of detail. (If you'd rather estimate TEF directly without decomposing into CF/PoA, that's also a methodologically valid shortcut per the O-RT Standard — this tool's dashboard currently expects the CF/PoA breakdown; enter CF = your TEF estimate and PoA = 100% if you want TEF taken at face value.)

### Vulnerability Estimation

Vulnerability is the probability that a threat event — one that's already been counted in TEF above — succeeds and becomes a loss event (i.e. that the threat agent's capability exceeds your controls' resistance strength). Per the O-RT Standard, there are two valid ways to estimate it:

1. **Directly**, as a single probability: "of the attempts that get through and are acted upon, what fraction actually result in a real compromise despite our controls (EDR, backups, segmentation, etc.)?" This is usually a small number — often well under 1% for an org with reasonable controls, since TEF already represents fully-formed attack *attempts*, not raw contact volume.
2. **From Threat Capability vs. Resistance Strength**, comparing the attacker's estimated capability percentile against your controls' resistance percentile.

**Important:** Vulnerability is applied directly on top of TEF (`LEF = TEF × Vulnerability`). It must **not** be built by re-multiplying Contact Frequency or Probability of Action into it — those are already fully baked into TEF. Doing so double-counts the same discount and silently crushes your loss-event frequency to an unrealistically low number (this was a real bug in earlier versions of this tool — see `CHANGELOG.md`).

### Loss Magnitude

**Primary Loss Components:**
- Incident response: €10,000-50,000
- Forensics: €5,000-30,000
- System recovery: €5,000-100,000
- Downtime: (Revenue per hour × hours down)
- Data recovery: €10,000-200,000

**Secondary Loss Components:**
- Regulatory fines: €0-500,000 (GDPR up to 4% revenue)
- Customer churn: (Customer LTV × churn rate)
- Reputation: Lost deals, delayed sales
- Legal: €10,000-200,000
- Insurance premium increases

**For SMBs (€1-10M revenue):**
- Use industry benchmarks
- Scale to your company size
- Consider your specific regulatory exposure

---

## Interpreting Results

### Key Metrics

1. **Mean ALE** (Annual Loss Expectancy)
   - Average expected loss per year
   - Use for budget planning

2. **Median ALE**
   - Middle value (50th percentile)
   - Often lower than mean due to outliers
   - More "typical" loss

3. **95th Percentile**
   - Value exceeded only 5% of the time
   - Good for risk appetite decisions
   - "Worst case" planning

4. **99th Percentile**
   - Value exceeded only 1% of the time
   - Extreme scenarios
   - Board-level risk discussions

5. **Loss Event Frequency**
   - Expected number of loss events per year
   - Helps prioritize controls

### Using Results for Decisions

**Security Investment ROI:**
```
If ALE = €500,000 and control costs €100,000/year
ROSI = (ALE Reduction - Control Cost) / Control Cost

If control reduces ALE by 50%:
ROSI = (€250,000 - €100,000) / €100,000 = 150%
```

**Risk Acceptance:**
- Compare 95th percentile to risk appetite
- If 95th < appetite → Consider accepting risk
- If 95th > appetite → Invest in controls

**Insurance Decisions:**
- Use 90th-99th percentile for coverage limits
- Compare premium to ALE reduction
- Evaluate deductible based on median

---

## Output Files

The simulation generates:

1. **JSON file**: Statistics summary
2. **CSV file**: Raw simulation data (10,000 rows)
3. **PNG file**: Four-panel visualization:
   - Annual loss distribution
   - Loss exceedance curve
   - Loss event frequency
   - Box plot summary

---

## Best Practices

1. **Calibration**: Run with known historical incidents to validate
2. **Sensitivity Analysis**: Vary parameters to see impact
3. **Ranges**: Use wide ranges when uncertain (conservative)
4. **Documentation**: Keep records of assumptions and sources
5. **Updates**: Refresh quarterly or after major changes
6. **Validation**: Have another expert review parameters
7. **Communication**: Use percentiles for non-technical audiences

---

## Integration with BARE Services

### For vCISO Engagements
- Run simulations for client's top 3-5 risks
- Use results in board presentations
- Support budget justification
- Track ALE changes over time

### For Compliance (ISO 27001, SOC 2)
- Document risk assessment methodology
- Show quantitative approach to risk
- Support risk treatment decisions
- Demonstrate continuous improvement

### For NIS2/DORA
- Quantify incident costs for resilience planning
- Support recovery time objective (RTO) decisions
- Justify BC/DR investments
- Document risk-based approach

---

## Common Questions

**Q: How accurate are these estimates?**
A: FAIR provides order-of-magnitude accuracy (±50%). The goal is better decision-making, not precision.

**Q: What if I don't have enough data?**
A: Start with wide ranges and expert judgment. Refine over time as you gather data.

**Q: How often should I run simulations?**
A: Quarterly for active risks, annually for stable risks, and whenever major changes occur.

**Q: Can I combine multiple scenarios?**
A: Yes! Run each separately, then add the ALE values. The tool can be extended for portfolio analysis.

**Q: What about controls?**
A: Model "before" and "after" scenarios to show control effectiveness and ROI.

---

## References

- **FAIR Institute**: https://www.fairinstitute.org/
- **FAIR Book**: "Measuring and Managing Information Risk: A FAIR Approach" by Jack Freund and Jack Jones
- **OpenFAIR**: Open source risk analysis tools
- **ENISA**: EU cybersecurity agency threat landscape reports
- **Verizon DBIR**: Annual data breach investigations report

---

## Support

For questions about implementing FAIR Monte Carlo for your BARE Cybersecurity clients, the tool is fully customizable and ready to use for:
- Client risk assessments
- Board presentations
- Security budget justification
- Compliance documentation
- Service pricing models

The tool outputs professional visualizations and detailed statistics suitable for executive audiences.
