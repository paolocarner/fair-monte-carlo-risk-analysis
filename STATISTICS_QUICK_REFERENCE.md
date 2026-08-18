# Statistics Quick Reference Card

**Quick answers to: "Where are the statistics and how do I update them?"**

## 📍 3 Places Statistics Live

### 1. Preset Data (`presets.json`)

```json
"Ransomware Attack": {
    "cf_min": 1000,            # ← HERE: Contact Frequency min (contacts/yr)
    "cf_mode": 3000,           # ← HERE: Contact Frequency most likely
    "cf_max": 10000,           # ← HERE: Contact Frequency max
    "poa": 0.1,                # ← HERE: Probability of Action
    "vulnerability": 0.0013,   # ← HERE: Vulnerability (direct, applied to derived TEF)
    "primary_min": 20000,     # ← HERE: Min direct loss €
    "primary_mode": 75000,    # ← HERE: Most likely direct loss €
    "primary_max": 350000,    # ← HERE: Max direct loss €
    "secondary_min": 10000,   # ← HERE: Min indirect loss €
    "secondary_mode": 40000,  # ← HERE: Most likely indirect loss €
    "secondary_max": 200000,  # ← HERE: Max indirect loss €
    "secondary_prob": 0.35    # ← HERE: Chance of indirect loss
}
```

TEF is no longer stored directly — the dashboard derives it as `TEF = CF × PoA`
(see `fair_monte_carlo.py`'s `derive_tef_from_contact()`) and applies
`vulnerability` directly to that derived TEF. See `CHANGELOG.md` for why
the old `vuln_contact`/`vuln_action`/`vuln_rate` three-way split was removed.

**To update**: Edit `presets.json`, save, restart dashboard

### 2. Documentation (`docs/FAIR_Parameter_Reference.md`)
**Full file** - Detailed tables with sources

Contains:
- Industry benchmarks by company size
- Vulnerability rates by control maturity  
- Loss magnitude breakdowns
- Data source citations

**To update**: Edit the markdown tables

### 3. Example Code (`fair_monte_carlo.py`)
**Lines 360-400** - The `example_ransomware_scenario()` function

Shows how to use the values in code

**To update**: Modify the example values

---

## 🔄 How to Update in 5 Steps

### Step 1: Find the Right File
```bash
# For dashboard presets:
open fair_dashboard.py  # Mac
nano fair_dashboard.py  # Linux
notepad fair_dashboard.py  # Windows
```

### Step 2: Locate the Function
Search for: `def load_preset(scenario):`

You'll see around line 100

### Step 3: Edit the Values
```python
# OLD
"tef_mode": 300,

# NEW  
"tef_mode": 450,  # Updated: Sophos 2025 report
```

### Step 4: Add a Comment
```python
"tef_mode": 450,  # Updated 2025-01-15: Sophos 2025, 50% increase
```

### Step 5: Test It
```bash
streamlit run fair_dashboard.py
# Select the preset you changed
# Verify it loads correctly
```

---

## 📊 What Each Parameter Means

| Parameter | What It Is | Example Value | Typical Range |
|-----------|-----------|---------------|---------------|
| `cf_min` | Minimum contacts/year | 1,000 | 10-100,000 |
| `cf_mode` | Most likely contacts/year | 3,000 | 50-500,000 |
| `cf_max` | Maximum contacts/year | 10,000 | 100-1,000,000 |
| `poa` | Probability of Action | 0.10 (10%) | 0.01-1.00 |
| `vulnerability` | P(threat event → loss event) | 0.0013 (0.13%) | 0.0001-0.40 |
| `primary_min` | Min direct cost € | 20,000 | 5k-50k |
| `primary_mode` | Typical direct cost € | 75,000 | 20k-200k |
| `primary_max` | Max direct cost € | 350,000 | 100k-1M |
| `secondary_min` | Min indirect cost € | 10,000 | 0-50k |
| `secondary_mode` | Typical indirect cost € | 40,000 | 10k-200k |
| `secondary_max` | Max indirect cost € | 200,000 | 50k-1M |
| `secondary_prob` | Chance of indirect loss | 0.35 (35%) | 0.20-0.70 |

---

## 📚 Where Numbers Come From

### Threat Frequency (TEF)
- **Verizon DBIR** - Annual data breach report
- **Sophos** - Ransomware state reports  
- **ENISA** - EU threat landscape
- **Your logs** - Firewall, email gateway, SIEM

### Vulnerability Rates
- **Verizon DBIR** - Success rates by attack type
- **KnowBe4** - Phishing click rates
- **Your tests** - Pen test, red team results
- **Industry averages** - Based on control maturity

### Loss Amounts
- **IBM** - Cost of Data Breach report
- **Ponemon** - Breach cost studies
- **Coalition** - Cyber insurance claims
- **GDPR Tracker** - Actual fines levied
- **Your data** - Past incident costs

---

## 🚨 Common Mistakes to Avoid

❌ **Using attack success rate for TEF**
- TEF = all attempts (successful or not)
- Vulnerability = probability of success

❌ **Mixing up vulnerability components**
- Contact Frequency, Probability of Action, and Vulnerability are three separate O-RT factors
- TEF = Contact Frequency × Probability of Action
- Vulnerability is then applied directly to TEF: LEF = TEF × Vulnerability
- Do **not** multiply Vulnerability by Contact Frequency or Probability of Action again — they're already accounted for in TEF (this was a real bug in earlier versions; see `CHANGELOG.md`)

❌ **Loss magnitudes > annual revenue**
- Primary loss should be < 30% of revenue
- If higher, you need insurance or acceptance

❌ **Forgetting to cite sources**
- Always add comments with sources
- Include date and page numbers

❌ **Not testing after updates**
- Always run the simulation
- Verify results are reasonable

---

## ✅ Quick Validation Checks

After updating, ask:

**TEF Check:**
- [ ] Is this realistic for this company size?
- [ ] Is the mode between min and max?
- [ ] Do I have a source for this number?

**Vulnerability Check:**
- [ ] Is total < 10% (0.10)?
- [ ] Does it account for controls?
- [ ] Contact × Action × Rate = Total?

**Loss Check:**
- [ ] Is mode closer to min than max?
- [ ] Is max loss < annual revenue?
- [ ] Do costs include all components?

**Source Check:**
- [ ] Did I add a comment with source?
- [ ] Is the source recent (<2 years)?
- [ ] Can I point to the page number?

---

## 🎯 Most Common Updates

### Quarterly: Check for New Reports
- Verizon DBIR (March/April)
- ENISA Threat Landscape (Annual)
- Sophos Ransomware (Annual)

### Annually: Full Parameter Review
- Review all TEF values
- Update loss magnitudes for inflation
- Adjust vulnerability for new controls

### As Needed: Event-Driven
- Major new threat emerges
- Significant control improvement (e.g., MFA mandate)
- Regulatory change (e.g., GDPR fine increase)

---

## 📞 Need Help?

**For understanding parameters:**
Read: `docs/FAIR_Parameter_Reference.md`

**For detailed update process:**
Read: `UPDATING_STATISTICS_GUIDE.md`

**For adding new scenarios:**
See: "Method 3: Add a New Preset" in full guide

**For data sources:**
See: "Data Sources to Monitor" in full guide

---

## 🎓 Example: Quick Update

**Scenario**: New report shows ransomware attempts increased 50%

```python
# 1. Open file
nano fair_dashboard.py

# 2. Find the preset (line ~102)
"Ransomware Attack": {

# 3. Update TEF values
    "tef_min": 150,   # Was: 100
    "tef_mode": 450,  # Was: 300 - Updated: Sophos 2025
    "tef_max": 1500,  # Was: 1000

# 4. Save and test
# 5. Document in CHANGELOG.md
```

**Time required**: 5 minutes

---

**Remember**: It's better to use imperfect data with sources than perfect guesses without documentation!
