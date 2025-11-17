# FAIR Monte Carlo Risk Analysis - Quick Start

## ✅ Fixed Issues
- ✅ UTF-8 encoding added (fixes euro symbol errors)
- ✅ requirements.txt included
- ✅ updated requirements.txt to include web dashboard dependencies

## 📦 Installation

### 1. Make sure you have Python 3.7+

```bash
python3 --version
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Run the example

```bash
python3 fair_monte_carlo.py
```

Or if that doesn't work:
Try run it in a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
```bash
venv\Scripts\activate     # Windows
```

That's it! You should see results printed and files generated.

## 📁 What You Get

After running, you'll have:
- **PNG file**: Risk analysis visualization (4 charts)
- **CSV file**: Raw simulation data (10,000 rows)
- **JSON file**: Summary statistics

## 🎯 Create Your Own Analysis

### Option 1: Use the Template

Edit `custom_scenario_template.py` and change these sections:
- Lines 28-33: Client information
- Lines 42-49: Threat Event Frequency
- Lines 64-79: Vulnerability calculation
- Lines 98-107: Primary losses
- Lines 130-142: Secondary losses

Then run:
```bash
python3 custom_scenario_template.py
```

### Option 2: Write Your Own Script

Create a file called `my_analysis.py`:

```python
# -*- coding: utf-8 -*-
from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution

# Create simulation
sim = FAIRMonteCarloSimulation(n_simulations=10000)

# Define threat frequency (attempts per year)
tef = FAIRDistribution(
    dist_type='pert',
    min_val=100,
    mode_val=500,
    max_val=2000
)

# Define vulnerability (probability of success: 0-1)
vulnerability = 0.015  # 1.5%

# Define primary loss (direct costs in euros)
primary_loss = FAIRDistribution(
    dist_type='lognormal',
    min_val=20000,
    mode_val=80000,
    max_val=300000
)

# Define secondary loss (indirect costs)
secondary_loss = FAIRDistribution(
    dist_type='lognormal',
    min_val=10000,
    mode_val=50000,
    max_val=200000
)

# Run simulation
stats = sim.run_simulation(
    tef_dist=tef,
    vuln_prob=vulnerability,
    primary_loss_dist=primary_loss,
    secondary_loss_dist=secondary_loss,
    secondary_loss_prob=0.4  # 40% chance of secondary losses
)

# Display results
sim.print_results(stats, currency="€")

# Generate visualization
sim.plot_results(stats, currency="€", save_path="my_risk_analysis.png")

# Export data
sim.export_results(stats, "My Risk Scenario", "my_results.csv")
```

Run it:
```bash
python3 my_analysis.py
```

## 📚 Documentation

- **FAIR_Monte_Carlo_Guide.md**: Complete methodology guide
- **FAIR_Parameter_Reference.md**: Industry benchmarks and ready-to-use values

## 🔧 Troubleshooting

**"No module named 'numpy'"**
```bash
pip3 install numpy pandas matplotlib scipy
```

**"Permission denied"**
```bash
pip3 install --user numpy pandas matplotlib scipy
```

**Still having issues?**
Try creating a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python3 fair_monte_carlo.py
```

## 💡 Pro Tips

1. **Start with the example**: Run `fair_monte_carlo.py` first to see how it works
2. **Use the reference guide**: `FAIR_Parameter_Reference.md` has pre-calculated values for common scenarios
3. **Iterate**: Run multiple scenarios (before/after controls) to show ROI
4. **Export for clients**: The PNG charts are ready for PowerPoint/Google Slides

## 🎓 Understanding the Outputs

- **Mean ALE**: Average expected annual loss (use for budgeting)
- **Median ALE**: Typical loss year (often lower than mean)
- **95th Percentile**: Use for "worst case" planning and insurance coverage
- **Loss Event Frequency**: Expected number of incidents per year

## 📧 Questions?

Refer to the comprehensive guide: `FAIR_Monte_Carlo_Guide.md`

---

**Version**: 1.0  
**For**: BARE Cybersecurity vCISO engagements  
**Created**: November 2025
