# Frequently Asked Questions: Statistics & Data Sources

## 📊 About the Data

### Q1: Where do the default statistics come from?

**A:** The preset scenarios are calibrated using multiple authoritative sources:

**Threat Frequency:**
- Verizon Data Breach Investigations Report (DBIR) 2024/2025
- ENISA Threat Landscape Report 2024
- Sophos State of Ransomware 2024
- Coalition Cyber Insurance claims data

**Vulnerability Rates:**
- Verizon DBIR (attack success rates)
- KnowBe4 Phishing Benchmarking Report
- SANS Security Awareness Report

**Loss Magnitudes:**
- IBM Cost of Data Breach Report 2024
- Ponemon Institute breach cost studies
- EU GDPR Enforcement Tracker (actual fines)
- Coalition/Allianz cyber insurance claims

All sources are documented in `docs/FAIR_Parameter_Reference.md` with specific citations.

---

### Q2: How often are the statistics updated?

**A:** Currently:
- **Major updates**: Annually (when new DBIR/ENISA reports are released)
- **Minor updates**: Quarterly (new incident data or regulatory changes)
- **Ad-hoc updates**: When significant threat landscape changes occur

We recommend users check for updates quarterly and review the CHANGELOG.md for changes.

---

### Q3: Are these statistics specific to my country/region?

**A:** The default presets are calibrated for **European SMBs** (Small and Medium Businesses) because:
- I'm based in the Netherlands and work primarily with EU clients
- EU has unique regulatory context (GDPR, NIS2, DORA)
- EU threat landscape differs from US/APAC

**However**, the methodology is universal. You can:
- Adjust parameters for your region (see UPDATING_STATISTICS_GUIDE.md)
- Use local data sources (national CERTs, regional ISACs)
- Create regional presets (e.g., "Ransomware Attack - US")

---

### Q4: What if I don't have data for my specific industry?

**A:** Use this approach:

**Step 1: Start with the closest preset**
- Healthcare → Use general "Data Breach" as baseline
- Manufacturing → Use "Ransomware Attack" as baseline
- Retail → Use "Business Email Compromise" as baseline

**Step 2: Apply industry modifiers**
See the "Industry-Specific Modifiers" section in `docs/FAIR_Parameter_Reference.md`:
- Healthcare: +30% TEF, +40% primary loss (patient safety)
- Financial: +50% TEF (attractive target), -30% vulnerability (better controls)
- Manufacturing: -20% TEF, +30% vulnerability (legacy systems)

**Step 3: Refine over time**
As you gather industry-specific data, update the parameters.

---

### Q5: Can I use my own company's historical data?

**A:** Absolutely! That's the gold standard. Here's how:

**If you have incident logs:**
```python
# Count your actual incidents from past 3 years
# Example: 8 ransomware attempts in 3 years

# Calculate TEF
actual_tef = 8 / 3  # = 2.67 events/year

# Use this for your parameters
"tef_min": 1,     # Some years had 1
"tef_mode": 3,    # Most typical
"tef_max": 6,     # Worst year extrapolated
```

**If you have cost data:**
```python
# You had 2 incidents that cost €45k and €120k

"primary_min": 40000,   # Lower bound
"primary_mode": 45000,  # Your smaller incident
"primary_max": 120000,  # Your larger incident
```

**Pro tip:** Combine your data with industry benchmarks:
- Use your frequency data (you know your exposure)
- Use industry cost data (small sample size)

---

### Q6: Why are the ranges so wide (e.g., 100-1000)?

**A:** Because risk is inherently uncertain! Wide ranges reflect:

1. **Real variability**: Some organizations face 100 attempts, others 1000
2. **Unknown factors**: Attacker behavior changes
3. **Control differences**: Good email filtering vs. poor
4. **Temporal changes**: Q4 often busier than Q2

The PERT distribution handles this by:
- Focusing on the mode (most likely: 300)
- Allowing for tail events (min: 100, max: 1000)
- Producing realistic probability distributions

**This is a feature, not a bug.** Single-point estimates hide uncertainty!

---

### Q7: How accurate are these estimates?

**A:** FAIR provides **order-of-magnitude accuracy** (±50%), not precision.

**What this means:**
- ✅ Accurate enough for investment decisions ($50k vs. $500k control)
- ✅ Accurate enough for insurance coverage (€500k vs. €5M)
- ✅ Accurate enough for risk acceptance thresholds
- ❌ Not accurate enough to budget to the nearest €1,000
- ❌ Not accurate enough to predict specific incident dates

**Why this is okay:**
- 80% accuracy beats 0% quantification (heat maps)
- Directionally correct beats precisely wrong
- Comparative analysis works fine (before/after controls)

**Academic support:**
Hubbard's "How to Measure Anything in Cybersecurity Risk" shows that even rough quantification improves decisions by 40-60% vs. qualitative methods.

---

## 🔄 Updating & Customization

### Q8: Can I create my own preset scenarios?

**A:** Yes! See "Method 3: Add a New Preset Scenario" in UPDATING_STATISTICS_GUIDE.md

Basic steps:
1. Add to the `load_preset()` dictionary in `fair_dashboard.py`
2. Add to the dropdown menu
3. Document your data sources
4. Test thoroughly

**Contributions welcome!** If you create a well-documented preset, consider contributing it back to the project.

---

### Q9: How do I adjust for company size?

**A:** The presets assume **small businesses (€2-10M revenue)**. Adjust using these multipliers:

**Micro (€0-2M revenue):**
- TEF: ×0.5 (less attractive target)
- Vulnerability: ×1.2 (fewer controls)
- Primary loss: ×0.6 (smaller scale)
- Secondary loss: ×0.4 (smaller fines, less reputation impact)

**Medium (€10-50M revenue):**
- TEF: ×1.5 (more attractive target)
- Vulnerability: ×0.8 (more mature controls)
- Primary loss: ×2.0 (larger scale)
- Secondary loss: ×2.5 (bigger fines, more reputation impact)

**Example:**
```python
# Small business baseline
"tef_mode": 300,

# Adjusted for medium business
"tef_mode": 450,  # 300 × 1.5
```

---

### Q10: Should I use the presets or create custom scenarios?

**A:** Depends on your use case:

**Use presets when:**
- Quick baseline assessment needed
- Client has typical risk profile
- No historical data available
- Early discovery phase

**Create custom when:**
- You have client-specific data
- Unique industry (e.g., critical infrastructure)
- High-stakes decision (>€500k investment)
- Regulatory requirement for tailored assessment

**Pro tip:** Start with preset, then customize as you learn more about the client.

---

### Q11: Can I modify the vulnerability calculation?

**A:** Vulnerability is now a single, directly-set value (see `CHANGELOG.md` — the earlier three-factor multiplication documented below was a real bug and has been removed):

**Current model:**
```python
tef_min, tef_mode, tef_max = derive_tef_from_contact(cf_min, cf_mode, cf_max, poa)
# LEF = TEF × Vulnerability, where Vulnerability is set directly — it is
# NOT re-multiplied by Contact Frequency or Probability of Action, since
# both are already fully accounted for in the derived TEF above.
```

**Setting Vulnerability directly:**
```python
# In custom_scenario_template.py
total_vulnerability = 0.0016  # Your direct estimate — see CHANGELOG.md /
                                # PRESET_METHODOLOGY.md for how preset values
                                # were derived; validate against your own data.

stats = sim.run_simulation(
    tef_dist=tef,
    vuln_prob=total_vulnerability,  # Use direct value
    ...
)
```

**When to use direct:**
- You have penetration test results (5% of tests succeeded)
- Historical data (15 successful attacks in 1,000 attempts)
- Research data specific to your scenario

**When to use three-factor:**
- Need to model control improvements at each stage
- Want to show impact of email filtering, training, EDR separately
- Communicating to non-technical stakeholders

---

## 🎯 Methodology Questions

### Q12: Why PERT distribution for frequency?

**A:** PERT (Program Evaluation and Review Technique) distribution is ideal for expert estimates because:

1. **Uses three points** (min, mode, max) - natural for SME interviews
2. **Mode-focused** - emphasizes most likely value
3. **Handles asymmetry** - mode doesn't need to be in middle
4. **Well-understood** - widely used in project management

**Alternative:** Use lognormal if you have mean and standard deviation from research.

---

### Q13: Why lognormal distribution for losses?

**A:** Financial losses are lognormally distributed because:

1. **Right-skewed** - Most incidents cheap, few very expensive
2. **Cannot be negative** - Losses are always ≥ 0
3. **Multiplicative** - Costs compound (downtime × hourly rate × days)
4. **Empirically validated** - IBM, Ponemon data shows this pattern

**Visual:**
```
Frequency
    ▲
    │  ███
    │  █████
    │  ███████
    │  █████████
    │  ███████████
    │  █████████████
    └──────────────────► Loss Amount
    Low        High
```

Most losses are small, tail extends to very large losses.

---

### Q14: What's the difference between TEF and LEF?

**A:** Common confusion! Here's the distinction:

**TEF (Threat Event Frequency):**
- How often threats occur (attempts)
- Example: 300 phishing emails/year
- **All attempts, whether successful or not**

**LEF (Loss Event Frequency):**
- How often losses occur (successful attacks)
- Example: 300 × 0.01 = 3 successful breaches/year
- **Only successful attempts that cause loss**

**Formula:**
```
LEF = TEF × Vulnerability

Example:
- TEF: 300 phishing attempts/year
- Vulnerability: 0.01 (1%)
- LEF: 3 successful breaches/year
```

The tool calculates LEF automatically from your TEF and vulnerability inputs.

---

### Q15: Why use Poisson sampling for actual events?

**A:** Because events are discrete and random in time:

**Without Poisson:**
- If LEF = 2.5, we'd always get 2.5 events (impossible!)

**With Poisson:**
- If LEF = 2.5, we might get 0, 1, 2, 3, 4, 5... events
- Probability follows real-world randomness
- Some years: 0 events (lucky!)
- Some years: 5 events (unlucky!)

This captures the **uncertainty in timing** that makes insurance valuable.

---

## 💰 Financial Questions

### Q16: How do I convert risk to budget?

**A:** Use the **mean ALE** for budget planning:

**Example:**
- Mean ALE: €450,000
- Budget for controls: 10-20% of ALE
- Budget range: €45,000-€90,000/year

**Rationale:**
- If controls reduce risk by 50%, you save €225k
- Spending €90k to save €225k = 150% ROSI
- This is the "risk-driven budget" approach

**Compare to traditional:**
- Traditional: "Industry average is 3-5% of IT budget"
- Risk-driven: "We face €450k risk, so we invest proportionally"

---

### Q17: Should I use mean or median ALE?

**A:** Depends on your audience:

**Use Mean:**
- Budget planning (accounts for tail risk)
- Insurance limit decisions
- Multi-year aggregation
- Technical risk managers

**Use Median:**
- "Typical year" conversations
- Board presentations (less scary)
- Risk acceptance discussions
- Non-technical stakeholders

**Use 95th percentile:**
- Risk appetite thresholds
- Worst-case planning
- Capital reserve requirements
- Conservative budgeting

**Example conversation:**
"In a typical year (median), we expect €300k in losses. On average (mean), it's €450k because of occasional severe incidents. There's a 5% chance (95th percentile) losses exceed €1.2M, which is why we need insurance."

---

### Q18: How do I compare ROI of different controls?

**A:** Run "before" and "after" scenarios:

**Step 1: Baseline (no control)**
```python
vulnerability_before = 0.02  # 2%
# Run simulation → Mean ALE: €600,000
```

**Step 2: With Control A (Email security + training)**
```python
vulnerability_after = 0.006  # 0.6% (70% reduction)
control_cost = 25000  # €25k/year
# Run simulation → Mean ALE: €180,000
```

**Step 3: Calculate ROSI**
```python
ale_reduction = 600000 - 180000  # €420,000
net_benefit = ale_reduction - control_cost  # €395,000
rosi = net_benefit / control_cost  # 15.8 = 1,580%
```

**Step 4: Repeat for Control B and compare**

This gives you objective comparison of security investments.

---

## 🛡️ Compliance & Reporting

### Q19: Can I use this for ISO 27001 / SOC 2 compliance?

**A:** Yes! Here's how:

**ISO 27001 (Risk Assessment):**
- ✅ Meets requirement for "systematic approach"
- ✅ Provides documented methodology
- ✅ Produces quantitative risk statements
- ✅ Supports risk treatment decisions
- ✅ Auditor-friendly (reproducible, transparent)

**SOC 2 (Risk Management):**
- ✅ Demonstrates risk-based approach
- ✅ Quantifies control effectiveness
- ✅ Documents assumptions and sources
- ✅ Shows ongoing risk monitoring

**NIS2 / DORA (EU Financial Services):**
- ✅ Quantifies incident impact
- ✅ Supports resilience planning
- ✅ Documents risk-based approach
- ✅ EU-specific regulatory context

**Export the reports** (JSON, CSV, TXT) for audit evidence.

---

### Q20: How do I explain Monte Carlo to executives?

**A:** Use this analogy:

**Bad explanation:**
"We run 10,000 iterations sampling from PERT and lognormal distributions using NumPy's random number generator..."

**Good explanation:**
"Think of weather forecasting. Instead of saying 'it will rain exactly 1.2 inches,' they run thousands of simulations and say '70% chance of 1-2 inches, 20% chance of 2-3 inches.'

We do the same with cyber risk:
- Run 10,000 'what if' scenarios
- Each scenario slightly different (varying attack frequency, costs)
- Get a range of outcomes with probabilities
- '80% of the time, losses are under €800k. But 5% of the time, they exceed €1.5M.'

This helps us plan for both typical and worst-case scenarios."

**Follow-up if they ask "How do we know the numbers are right?"**
"We base them on data from thousands of real companies:
- Verizon analyzes 20,000+ breaches annually
- IBM studies 600+ organizations
- EU regulators publish all GDPR fines

So instead of guessing, we're using the collective experience of the industry."

---

## 🤝 Contributing & Community

### Q21: Can I contribute updated statistics?

**A:** Yes please! Here's how:

1. **Fork the repository** on GitHub
2. **Update parameters** with proper documentation:
   - Add comments with sources
   - Include page numbers and sample sizes
   - Explain your methodology
3. **Test the changes** - verify results are reasonable
4. **Submit pull request** with clear description
5. **Engage in review discussion**

See CONTRIBUTING.md for detailed guidelines.

---

### Q22: Can I use this tool commercially?

**A:** Yes! The MIT License allows:
- ✅ Commercial use (charge clients for risk assessments)
- ✅ Modification (customize for your needs)
- ✅ Distribution (share with clients, colleagues)
- ✅ Private use (internal risk management)

**Only requirement:** Keep the license and copyright notice.

**Attribution appreciated:**
"Risk quantification performed using FAIR Monte Carlo Analysis Tool by Paolo Carner / BARE Cybersecurity"

---

### Q23: Where can I get help or report issues?

**A:** Multiple options:

**For bugs or feature requests:**
- GitHub Issues: [Your repo URL]/issues
- Provide: OS, Python version, error message, steps to reproduce

**For methodology questions:**
- Read: docs/FAIR_Monte_Carlo_Guide.md
- Read: docs/FAIR_Parameter_Reference.md
- Read: This FAQ

**For general discussion:**
- GitHub Discussions: [Your repo URL]/discussions
- LinkedIn: Connect with Paolo Carner
- Email: paolo@barecybersecurity.com (for sensitive questions)

**For professional services:**
- BARE Cybersecurity: https://paolocarner.com
- I'm available for vCISO engagements, training, custom tool development

---

### Q24: Will this tool always be free?

**A:** Yes, the core tool will remain open source and free forever.

**Why?**
- Enterprise risk platforms cost €50k+
- SMBs deserve access to quantitative risk analysis
- Community contributions improve the tool for everyone
- Open source increases trust and transparency

**Potential future offerings** (not decided):
- Hosted/cloud version (convenience, no installation)
- Professional training workshops
- Custom scenario development services
- Integration with commercial GRC platforms

But the core GitHub version will always be free and open source.

---

### Q25: Can I request a new preset scenario?

**A:** Absolutely! Open a GitHub Issue with:

**Title:** "New Preset Request: [Scenario Name]"

**Body:**
```markdown
**Scenario**: Supply Chain Attack
**Use case**: Manufacturing and critical infrastructure
**Why needed**: Supply chain is increasingly targeted but not covered by current presets
**Data sources available**: 
- ENISA Supply Chain report
- CISA Supply Chain guidance
- [Your research/experience]

**Willingness to contribute**: [Yes/No/With help]
```

I'll either:
- Create it if I have the data
- Collaborate with you to develop it
- Guide you through creating it yourself (and I'll review)

---

## 📚 Learning More

### Q26: I'm new to FAIR. Where should I start?

**Learning path:**

**Week 1: Understanding FAIR**
1. Read: Part 1 of my blog series
2. Read: FAIR Institute "Introduction to FAIR"
3. Watch: FAIR Institute YouTube tutorials

**Week 2: Using the Tool**
1. Read: Dashboard_Quick_Start.md
2. Run: Pre-built scenarios in the dashboard
3. Experiment: Adjust sliders, see impact

**Week 3: Customization**
1. Read: FAIR_Parameter_Reference.md
2. Try: custom_scenario_template.py
3. Practice: Model a real risk from your organization

**Week 4: Mastery**
1. Read: FAIR methodology guide (full)
2. Study: Data source reports (Verizon DBIR, etc.)
3. Create: Your own preset scenarios

**Resources:**
- FAIR Institute: https://www.fairinstitute.org/
- Book: "Measuring and Managing Information Risk" (Freund & Jones)
- My blog: https://paolocarner.com/blog/

---

### Q27: Are there online courses on FAIR?

**A:** Yes! Options:

**Free:**
- FAIR Institute resources (free membership)
- YouTube: "Introduction to FAIR Risk Analysis"
- My blog series (3-part practical guide)

**Paid:**
- FAIR Institute training ($1,500-3,000)
- Cybrary FAIR course ($200-500)
- LinkedIn Learning: "Cybersecurity Risk Management"

**Best value:** FAIR Institute Open Group (free) + hands-on practice with this tool

---

## 🎯 Still Have Questions?

**Check these resources:**
1. Read: `docs/FAIR_Monte_Carlo_Guide.md` (methodology)
2. Read: `docs/FAIR_Parameter_Reference.md` (benchmarks)
3. Read: `UPDATING_STATISTICS_GUIDE.md` (detailed update process)
4. Open: GitHub Issue (for bug reports, feature requests)
5. Email: paolo@barecybersecurity.com (for sensitive questions)

**The tool is designed to be transparent and understandable. If something is unclear, that's a bug - please let me know so I can improve the documentation!**

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Questions not answered here?** Open a GitHub Issue with the label "documentation" and I'll add it to the FAQ!
