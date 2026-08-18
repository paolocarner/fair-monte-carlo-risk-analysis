# FAIR Quick Reference Card: Parameter Values for EU SMBs

## Typical Parameter Ranges by Company Size

### Micro Enterprise (1-9 employees, €0-2M revenue)
- **Risk Appetite**: 0.3-0.8% of revenue
- **Insurance Coverage**: €50k-250k
- **Incident Response Budget**: €5k-20k

### Small Business (10-49 employees, €2-10M revenue)
- **Risk Appetite**: 0.4-1.0% of revenue
- **Insurance Coverage**: €250k-1M
- **Incident Response Budget**: €10k-50k

### Medium Business (50-249 employees, €10-50M revenue)
- **Risk Appetite**: 0.3-0.8% of revenue
- **Insurance Coverage**: €1M-5M
- **Incident Response Budget**: €25k-150k

---

## Threat Event Frequency (TEF) - Industry Benchmarks

### Phishing/Social Engineering
| Company Size | Min/Year | Mode/Year | Max/Year | Source |
|-------------|----------|-----------|----------|--------|
| Micro | 100 | 300 | 800 | Verizon DBIR 2024 |
| Small | 300 | 1,000 | 3,000 | Verizon DBIR 2024 |
| Medium | 1,000 | 3,000 | 10,000 | Verizon DBIR 2024 |

### Ransomware Attempts
| Company Size | Min/Year | Mode/Year | Max/Year | Source |
|-------------|----------|-----------|----------|--------|
| Micro | 50 | 150 | 500 | Sophos State of Ransomware |
| Small | 100 | 300 | 1,000 | Sophos State of Ransomware |
| Medium | 300 | 800 | 2,000 | Sophos State of Ransomware |

### DDoS Attacks
| Company Size | Min/Year | Mode/Year | Max/Year | Source |
|-------------|----------|-----------|----------|--------|
| All E-commerce | 10 | 30 | 100 | Cloudflare Reports |
| Financial Services | 20 | 60 | 200 | Cloudflare Reports |
| Other | 5 | 15 | 50 | Cloudflare Reports |

### Web Application Attacks
| Company Size | Min/Year | Mode/Year | Max/Year | Source |
|-------------|----------|-----------|----------|--------|
| Any w/ Web Apps | 500 | 2,000 | 10,000 | OWASP/Akamai |

### Insider Threats
| Company Size | Min/Year | Mode/Year | Max/Year | Source |
|-------------|----------|-----------|----------|--------|
| Micro | 1 | 3 | 10 | Verizon DBIR 2024 |
| Small | 2 | 8 | 25 | Verizon DBIR 2024 |
| Medium | 5 | 20 | 60 | Verizon DBIR 2024 |

---

## Vulnerability Rates by Control Maturity

Per the corrected model (see `CHANGELOG.md`), **Contact Frequency (CF) is
external and does not change with your controls** — it's industry-wide
threat volume, a count. What controls actually change is **Probability of
Action (PoA)** and **Vulnerability**: better filtering/training reduces how
often a contact turns into a real attempt (PoA), and better technical
controls (MFA, EDR, backups) reduce how often an attempt succeeds
(Vulnerability). The tables below hold CF fixed and vary PoA/Vulnerability
by maturity tier.

### Phishing → Credential Theft (illustrative CF: 3,000 contacts/year)

#### No Controls
- Probability of Action: 0.20 (20% click — no filtering, no training)
- Vulnerability: 0.05 (5% of clicks lead to compromise — no MFA)
- **Effective loss events/year ≈ 3,000 × 0.20 × 0.05 = 30**

#### Basic Controls (email filtering + basic training)
- Probability of Action: 0.12 (filtering + training reduce click-through)
- Vulnerability: 0.01 (1% — some MFA coverage)
- **Effective loss events/year ≈ 3,000 × 0.12 × 0.01 = 3.6**

#### Mature Controls (filtering + training + MFA + EDR)
- Probability of Action: 0.08 (well-trained workforce)
- Vulnerability: 0.0013 (MFA + EDR block most compromises even after a click)
- **Effective loss events/year ≈ 3,000 × 0.08 × 0.0013 ≈ 0.31**

### Ransomware Vulnerability (illustrative CF: 3,000 contacts/year)

#### No Controls
- Probability of Action: 0.20
- Vulnerability: 0.05 (no backups/EDR — a successful click usually means full compromise)
- **Effective loss events/year ≈ 3,000 × 0.20 × 0.05 = 30**

#### Basic Controls (AV + backups)
- Probability of Action: 0.15
- Vulnerability: 0.01
- **Effective loss events/year ≈ 3,000 × 0.15 × 0.01 = 4.5**

#### Mature Controls (EDR + backups + segmentation)
- Probability of Action: 0.10
- Vulnerability: 0.0013
- **Effective loss events/year ≈ 3,000 × 0.10 × 0.0013 ≈ 0.39**

All figures above are illustrative order-of-magnitude estimates, not
sourced statistics — validate against real client control-effectiveness
data (pen test results, phishing simulation click rates, MFA coverage,
EDR alert data) before use in a client engagement. See
`PRESET_METHODOLOGY.md` for how the shipped preset values were derived.

---

## Loss Magnitude: Primary Costs (Direct)

### Ransomware Incident
| Company Size | Min (€) | Mode (€) | Max (€) | Components |
|-------------|---------|----------|---------|------------|
| Micro | 5,000 | 20,000 | 80,000 | Ransom, recovery, downtime |
| Small | 15,000 | 60,000 | 250,000 | + IR team, forensics |
| Medium | 50,000 | 200,000 | 1,000,000 | + full rebuild, extended downtime |

**Breakdown:**
- Ransom payment: €5k-500k (if paid; avg €70k for SMBs)
- Incident response: €10k-100k
- Digital forensics: €5k-50k
- System recovery: €10k-200k
- Data recovery: €5k-100k
- Downtime: €1k-10k per day × days

### Data Breach (GDPR)
| Company Size | Min (€) | Mode (€) | Max (€) | Components |
|-------------|---------|----------|---------|------------|
| Micro | 3,000 | 15,000 | 60,000 | Notification, legal, basic IR |
| Small | 10,000 | 50,000 | 200,000 | + forensics, credit monitoring |
| Medium | 30,000 | 150,000 | 800,000 | + comprehensive response |

**Breakdown:**
- Incident investigation: €5k-80k
- Legal fees: €5k-100k
- Notification costs: €2k-50k
- Credit monitoring: €10-30 per affected individual
- PR/crisis management: €10k-100k

### Business Email Compromise (BEC)
| Company Size | Min (€) | Mode (€) | Max (€) | Components |
|-------------|---------|----------|---------|------------|
| Micro | 3,000 | 15,000 | 80,000 | Wire transfer loss |
| Small | 5,000 | 35,000 | 200,000 | Larger transfers |
| Medium | 10,000 | 80,000 | 500,000 | High-value targets |

**Breakdown:**
- Wire transfer loss: €5k-500k (FBI IC3: avg €120k)
- Recovery attempts: €2k-20k
- Investigation: €3k-30k

### DDoS Attack
| Company Size | Min (€) | Mode (€) | Max (€) | Components |
|-------------|---------|----------|---------|------------|
| E-commerce | 2,000 | 15,000 | 100,000 | Lost revenue + mitigation |
| SaaS | 3,000 | 20,000 | 150,000 | Customer impact + SLA |
| Other | 1,000 | 8,000 | 50,000 | Downtime + response |

**Breakdown:**
- Lost revenue: (Revenue per hour × hours down)
- Mitigation service: €5k-50k per incident
- Customer compensation: €1k-30k
- Emergency response: €2k-20k

### Insider Threat/Data Theft
| Company Size | Min (€) | Mode (€) | Max (€) | Components |
|-------------|---------|----------|---------|------------|
| Micro | 5,000 | 25,000 | 100,000 | Investigation, IP loss |
| Small | 10,000 | 60,000 | 300,000 | + legal action |
| Medium | 30,000 | 150,000 | 1,000,000 | + competitive impact |

---

## Loss Magnitude: Secondary Costs (Indirect)

### Regulatory Fines (EU)

#### GDPR Fines (up to 4% annual revenue or €20M)
| Severity | Micro (€2M rev) | Small (€10M rev) | Medium (€50M rev) |
|----------|-----------------|------------------|-------------------|
| Minor | €5,000 | €25,000 | €125,000 |
| Moderate | €20,000 | €100,000 | €500,000 |
| Severe | €50,000 | €250,000 | €1,250,000 |

**Historical averages** (GDPR fine tracker):
- SMBs: €10k-100k (majority under €50k)
- First-time offenders: Lower end
- Repeat/negligent: Upper end

#### NIS2 Penalties
- Essential entities: Up to €10M or 2% revenue
- Important entities: Up to €7M or 1.4% revenue

### Customer Churn
| Industry | Churn Rate After Breach | Avg Customer LTV | Impact |
|----------|------------------------|------------------|---------|
| Financial Services | 15-30% | €5,000-20,000 | High |
| Healthcare | 10-20% | €3,000-10,000 | Medium-High |
| Retail | 5-15% | €500-2,000 | Medium |
| B2B SaaS | 10-25% | €10,000-50,000 | Very High |
| Professional Services | 5-15% | €5,000-30,000 | Medium |

**Calculation**: (Customer count × Churn rate × Customer LTV)

### Reputation Damage (Lost Business)
| Breach Severity | Revenue Impact (Next 12 months) | Duration |
|----------------|--------------------------------|----------|
| Minor (not public) | 0-2% revenue loss | 3-6 months |
| Moderate (public) | 2-5% revenue loss | 6-12 months |
| Severe (major breach) | 5-15% revenue loss | 12-24 months |

### Other Secondary Costs
- Insurance premium increases: 10-50% for 3 years
- Stock price impact (if public): 5-15% drop avg
- Legal settlements: €10k-500k
- Competitive disadvantage: 2-8% lost deals
- Executive time: 100-500 hours @ €200-500/hr

### Probability of Secondary Losses

| Incident Type | Chance of Regulatory Fine | Chance of Major Reputation Impact | Chance of Customer Churn |
|---------------|--------------------------|----------------------------------|-------------------------|
| Ransomware | 10-30% | 40-60% | 30-50% |
| Data Breach | 30-60% | 60-80% | 40-70% |
| BEC | 5-10% | 10-30% | 5-15% |
| DDoS | 5-15% | 30-50% | 20-40% |
| Insider Threat | 20-40% | 40-60% | 20-40% |

---

## Industry-Specific Modifiers

### Healthcare (GDPR + sector-specific)
- **Higher TEF**: +30% (attractive target)
- **Higher Vulnerability**: +20% (legacy systems)
- **Higher Primary Loss**: +40% (patient safety costs)
- **Higher Secondary**: +50% (regulatory scrutiny)

### Financial Services (GDPR + DORA + PSD2)
- **Higher TEF**: +50% (very attractive target)
- **Lower Vulnerability**: -30% (better controls)
- **Higher Secondary**: +60% (trust critical)

### Professional Services
- **Average TEF**: baseline
- **Average Vulnerability**: baseline
- **Lower Primary**: -20% (faster recovery)
- **Moderate Secondary**: +10%

### E-commerce/Retail
- **Higher TEF**: +20% (public-facing)
- **Higher Vulnerability**: +10% (web apps)
- **Moderate Primary**: baseline
- **Higher Secondary**: +30% (customer impact)

### Manufacturing/Industrial
- **Lower TEF**: -20% (less targeted)
- **Higher Vulnerability**: +30% (OT/legacy)
- **Variable Primary**: depends on downtime impact
- **Moderate Secondary**: baseline

---

## Control Effectiveness: Typical Risk Reduction

### Email Security & Training
- **TEF Reduction**: 0% (doesn't reduce attempts)
- **Vulnerability Reduction**: 70-85%
- **Loss Magnitude**: 0% (doesn't reduce impact)
- **Overall Risk Reduction**: 70-85%
- **Annual Cost**: €5k-25k for SMBs

### Endpoint Detection & Response (EDR/MDR)
- **TEF Reduction**: 0%
- **Vulnerability Reduction**: 40-60%
- **Loss Magnitude Reduction**: 30-50% (faster detection)
- **Overall Risk Reduction**: 60-80%
- **Annual Cost**: €15k-60k for SMBs

### MFA (Multi-Factor Authentication)
- **TEF Reduction**: 0%
- **Vulnerability Reduction**: 80-95% (credential-based)
- **Loss Magnitude**: 0%
- **Overall Risk Reduction**: 80-95% for credential threats
- **Annual Cost**: €3k-15k for SMBs

### Backup & Recovery Solution
- **TEF Reduction**: 0%
- **Vulnerability Reduction**: 0%
- **Loss Magnitude Reduction**: 60-80% (ransomware)
- **Overall Risk Reduction**: 60-80% (ransomware only)
- **Annual Cost**: €5k-30k for SMBs

### Cyber Insurance
- **Risk Reduction**: 0% (transfer only)
- **Financial Impact**: Transfers 70-90% after deductible
- **Annual Cost**: 2-5% of coverage amount
- **Typical Coverage**: €500k-5M for SMBs

### Network Segmentation
- **TEF Reduction**: 0%
- **Vulnerability Reduction**: 20-40%
- **Loss Magnitude Reduction**: 40-60% (limits spread)
- **Overall Risk Reduction**: 50-75%
- **Implementation Cost**: €20k-100k (one-time)

---

## Recommended Simulation Parameters by Scenario

### 1. Phishing → Credential Theft → Data Breach

```python
# TEF: Email phishing attempts
tef = FAIRDistribution('pert', min_val=500, mode_val=1500, max_val=4000)

# Vulnerability: Email reaches inbox × User clicks × Leads to breach
vulnerability = 0.30 * 0.08 * 0.25  # = 0.006 (0.6%)

# Primary: Investigation, notification, recovery
primary = FAIRDistribution('lognormal', min_val=15000, mode_val=65000, max_val=250000)

# Secondary: GDPR fine, customer churn, reputation
secondary = FAIRDistribution('lognormal', min_val=20000, mode_val=80000, max_val=400000)
secondary_prob = 0.50
```

### 2. Ransomware via Phishing

```python
tef = FAIRDistribution('pert', min_val=200, mode_val=600, max_val=1500)
vulnerability = 0.25 * 0.10 * 0.35  # = 0.00875 (0.875%)
primary = FAIRDistribution('lognormal', min_val=20000, mode_val=75000, max_val=350000)
secondary = FAIRDistribution('lognormal', min_val=10000, mode_val=40000, max_val=200000)
secondary_prob = 0.35
```

### 3. Business Email Compromise

```python
tef = FAIRDistribution('pert', min_val=300, mode_val=800, max_val=2000)
vulnerability = 0.40 * 0.05 * 0.30  # = 0.006 (0.6%)
primary = FAIRDistribution('lognormal', min_val=8000, mode_val=40000, max_val=200000)
secondary = FAIRDistribution('lognormal', min_val=3000, mode_val=15000, max_val=75000)
secondary_prob = 0.25
```

### 4. DDoS Attack (E-commerce)

```python
tef = FAIRDistribution('pert', min_val=15, mode_val=40, max_val=120)
vulnerability = 0.50 * 0.35  # = 0.175 (17.5%)
primary = FAIRDistribution('lognormal', min_val=5000, mode_val=25000, max_val=120000)
secondary = FAIRDistribution('lognormal', min_val=3000, mode_val=18000, max_val=80000)
secondary_prob = 0.50
```

### 5. Insider Threat - Malicious

```python
tef = FAIRDistribution('pert', min_val=3, mode_val=10, max_val=30)
vulnerability = 0.60 * 0.15  # = 0.09 (9%)
primary = FAIRDistribution('lognormal', min_val=15000, mode_val=80000, max_val=400000)
secondary = FAIRDistribution('lognormal', min_val=20000, mode_val=100000, max_val=600000)
secondary_prob = 0.60
```

---

## Data Sources for Parameters

### Threat Intelligence
- **Verizon DBIR**: Annual data breach report (TEF, vulnerability stats)
- **IBM X-Force**: Threat intelligence report
- **Microsoft Security Intelligence**: Volume 25+
- **ENISA Threat Landscape**: EU-specific threats
- **Sophos Threat Report**: SMB-focused

### Loss Data
- **IBM Cost of Data Breach**: Annual report (€4.88M avg in 2024, €165 per record)
- **Ponemon Cost Studies**: Various breach types
- **NetDiligence Claims Database**: Cyber insurance claims
- **Advisen Cyber Loss Database**: Historical losses

### Regulatory
- **GDPR Enforcement Tracker**: Historical fine data
- **Privacy Affairs**: Fine database
- **DLA Piper GDPR Fines**: Tracker service

### Insurance
- **Coalition Cyber Claims Report**: Annual claims analysis
- **Beazley Breach Insights**: Trends in cyber claims
- **Munich Re Cyber Risk**: Industry analysis

---

## Quick Decision Matrix

| Mean ALE as % Revenue | Risk Level | Typical Action |
|----------------------|------------|----------------|
| < 0.3% | Low | Accept or minimal controls |
| 0.3% - 0.6% | Moderate-Low | Basic controls, consider insurance |
| 0.6% - 1.0% | Moderate | Invest in controls, get insurance |
| 1.0% - 2.0% | High | Priority investment, insurance required |
| > 2.0% | Critical | Immediate action, comprehensive program |

| 95th Percentile | Insurance Coverage Recommendation |
|-----------------|----------------------------------|
| < €100k | Consider €250k-500k policy |
| €100k - €500k | Get €500k-1M policy |
| €500k - €1M | Get €1M-2M policy |
| > €1M | Get €2M-5M policy |

---

## Validation Checks

After running simulation, verify:

1. **Sanity Check**: Does Mean ALE seem reasonable?
   - Compare to industry benchmarks (0.3-0.6% revenue typical)
   - Check against insurance quotes (should align)

2. **LEF Check**: Expected loss events per year
   - Should be between 0.1 and 20 for most SMB scenarios
   - If > 50, check TEF and vulnerability (might be too high)

3. **Loss Magnitude Check**: 
   - Ensure max loss < annual revenue (unless catastrophic)
   - Check mode is between min and max (not at extremes)

4. **Distribution Shape**:
   - ALE should be right-skewed (median < mean)
   - 90th/95th should be 2-5× median

---

## Common Mistakes to Avoid

❌ **Using single-point estimates** instead of distributions
✅ Use full PERT or lognormal distributions

❌ **Overestimating vulnerability** (using "gut feel" vs. data)
✅ Ground Vulnerability in real control-effectiveness data (pen tests, phishing simulation results, MFA/EDR coverage) — and apply it directly to TEF, not multiplied by Contact Frequency or Probability of Action again (those are already accounted for in TEF; see `CHANGELOG.md`)

❌ **Ignoring secondary losses** or using same distribution as primary
✅ Model separately with lower probability of occurrence

❌ **Using normal distributions** for loss magnitudes
✅ Use lognormal (reflects real-world skew)

❌ **Not considering control maturity** in vulnerability
✅ Adjust vulnerability based on actual security posture

❌ **Forgetting to annualize** costs (e.g., using one-time costs)
✅ Ensure all values represent annual expectations

❌ **Setting TEF too low** (only counting successful attacks)
✅ TEF = all attempts, vulnerability = success rate

---

**Last Updated**: November 2025  
**Version**: 1.0 for BARE Cybersecurity  
**For**: EU SMB vCISO engagements

*Note: These values are guidelines based on industry research and should be adjusted for specific client contexts.*
