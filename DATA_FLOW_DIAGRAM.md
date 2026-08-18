# Data Flow Diagram: Where Statistics Go

Visual guide showing how statistics flow through the FAIR Monte Carlo tool.

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (External)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Verizon DBIR  │  📊 ENISA Reports  │  📊 Insurance Claims │
│  📊 Sophos Data   │  📊 IBM Studies    │  📊 GDPR Tracker    │
│  📊 Your Logs     │  📊 Pen Tests      │  📊 Past Incidents  │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              DOCUMENTATION (Parameter Reference)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  docs/FAIR_Parameter_Reference.md                              │
│  - Industry benchmarks by size                                 │
│  - Vulnerability rates by maturity                             │
│  - Loss magnitudes with breakdowns                             │
│  - Citations and sources                                       │
│                                                                 │
└────────────────────┬────────────────────┬───────────────────────┘
                     │                    │
                     ↓                    ↓
┌──────────────────────────────┐  ┌─────────────────────────────┐
│   DASHBOARD PRESETS          │  │  COMMAND-LINE EXAMPLES      │
│   presets.json                │  │  fair_monte_carlo.py        │
│   (loaded by fair_dashboard.py)│ │  example_ransomware()       │
├──────────────────────────────┤  ├─────────────────────────────┤
│                              │  │                             │
│  "Ransomware Attack": {      │  │  tef = FAIRDistribution(    │
│    "cf_min": 1000,          │  │    min_val=100,             │
│    "cf_mode": 3000,         │  │    mode_val=300,            │
│    "cf_max": 10000,         │  │    max_val=1000             │
│    "poa": 0.1,              │  │  )   # TEF entered directly │
│    "vulnerability": 0.0013, │  │                             │
│    "primary_min": 20000,    │  │  vulnerability = 0.02       │
│    "primary_mode": 75000,   │  │  primary_loss = ...         │
│    ...                      │  │  secondary_loss = ...       │
│  }                          │  │                             │
│  ↓ derive_tef_from_contact()│  │  (estimates TEF directly,   │
│  TEF = cf × poa             │  │  skipping the CF/PoA split) │
│                              │  │                             │
└──────────┬───────────────────┘  └────────┬────────────────────┘
           │                               │
           │                               │
           └───────────┬───────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│              USER INPUT (Dashboard or Script)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Option A: Select Preset                                       │
│  ┌──────────────────────┐                                      │
│  │ Load Preset Scenario │                                      │
│  │ [Ransomware Attack ▼]│  ← User selects                     │
│  └──────────────────────┘                                      │
│                                                                 │
│  Option B: Manual Entry                                        │
│  ┌─────────────────────────────────┐                           │
│  │ Threat Frequency:               │                           │
│  │ Min:  [100]  Mode: [300]       │  ← User enters            │
│  │ Max:  [1000]                   │                           │
│  │                                 │                           │
│  │ Vulnerability: ●──────          │  ← User adjusts slider   │
│  │               0%      100%      │                           │
│  └─────────────────────────────────┘                           │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│           SIMULATION ENGINE (fair_monte_carlo.py)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  class FAIRMonteCarloSimulation:                               │
│                                                                 │
│  1. Create Distributions                                       │
│     ┌──────────────────────────────────────┐                   │
│     │ TEF Distribution (PERT)              │                   │
│     │ • Min: 100, Mode: 300, Max: 1000    │                   │
│     │ • Generates random samples           │                   │
│     └──────────────────────────────────────┘                   │
│                                                                 │
│  2. Calculate Vulnerability                                    │
│     ┌──────────────────────────────────────┐                   │
│     │ Total Vuln = Contact × Action × Rate│                   │
│     │ 0.25 × 0.10 × 0.35 = 0.00875 (0.875%)                  │
│     └──────────────────────────────────────┘                   │
│                                                                 │
│  3. Calculate Loss Event Frequency                             │
│     ┌──────────────────────────────────────┐                   │
│     │ LEF = TEF × Vulnerability            │                   │
│     │ 300 × 0.00875 = 2.6 events/year     │                   │
│     └──────────────────────────────────────┘                   │
│                                                                 │
│  4. Run Monte Carlo (10,000 iterations)                        │
│     ┌──────────────────────────────────────┐                   │
│     │ For each iteration:                  │                   │
│     │  • Sample TEF                        │                   │
│     │  • Calculate LEF                     │                   │
│     │  • Determine actual events (Poisson) │                   │
│     │  • Sample loss magnitudes            │                   │
│     │  • Sum annual loss                   │                   │
│     └──────────────────────────────────────┘                   │
│                                                                 │
│  5. Calculate Statistics                                       │
│     ┌──────────────────────────────────────┐                   │
│     │ • Mean ALE                           │                   │
│     │ • Median ALE                         │                   │
│     │ • Percentiles (10th, 25th, ..., 99th)│                   │
│     │ • Standard deviation                 │                   │
│     │ • Probability of loss                │                   │
│     └──────────────────────────────────────┘                   │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT / RESULTS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Visual Dashboard                                            │
│  ┌─────────────────────────────────────────┐                   │
│  │ Mean ALE: €618,000                      │                   │
│  │ Median:   €554,000                      │                   │
│  │ 95th %:   €1,340,000                    │                   │
│  │ LEF:      7.7 events/year               │                   │
│  │                                         │                   │
│  │ [Interactive Charts]                    │                   │
│  │ • Distribution histogram                │                   │
│  │ • Exceedance curve                      │                   │
│  │ • Percentile bars                       │                   │
│  │ • LEF analysis                          │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  💾 Export Files                                                │
│  ┌─────────────────────────────────────────┐                   │
│  │ • JSON: Complete statistics             │                   │
│  │ • CSV:  All 10,000 iterations          │                   │
│  │ • TXT:  Executive summary              │                   │
│  │ • PNG:  Charts for reports             │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📍 Detailed: Where Each Statistic Is Used

### Threat Event Frequency (TEF)

```
DATA SOURCE                  LOCATION IN CODE                USE
─────────────────────────────────────────────────────────────────
Sophos Report 2024     →    fair_dashboard.py          →    User sees
"100-1000 attempts/yr"       load_preset()                  in dropdown
                             line 103
                             
                       →    FAIRDistribution()         →    Monte Carlo
                             creates PERT dist              samples from
                             
                       →    10,000 iterations          →    Statistics
                             each samples TEF               calculated
```

### Vulnerability Rate

```
DATA SOURCE                  LOCATION IN CODE                USE
─────────────────────────────────────────────────────────────────
Verizon DBIR 2024      →    fair_dashboard.py          →    User adjusts
"25% contact rate"           load_preset()                  with sliders
"10% action rate"            lines 104-106
"35% vuln rate"              
                       →    Multiplied together        →    Total: 0.875%
                             0.25 × 0.10 × 0.35
                             
                       →    Used in LEF calc           →    LEF = TEF × Vuln
                             every iteration
```

### Loss Magnitudes

```
DATA SOURCE                  LOCATION IN CODE                USE
─────────────────────────────────────────────────────────────────
IBM Breach Report      →    fair_dashboard.py          →    User sees
"€20k-350k range"            load_preset()                  preset values
                             lines 105-107
                             
Coalition Claims       →    FAIRDistribution()         →    Lognormal
"Most ~€75k"                 creates lognormal dist         distribution
                             
                       →    Sampled per event          →    Total loss
                             in Monte Carlo                 calculated
```

## 🔄 Update Flow

```
NEW RESEARCH PUBLISHED
         ↓
Read the Report
         ↓
Extract Parameters
         ↓
┌────────────────────────┐
│ Update Location        │
├────────────────────────┤
│ 1. fair_dashboard.py   │ ← Change preset values
│    load_preset()       │
│                        │
│ 2. docs/Reference.md   │ ← Update documentation
│                        │
│ 3. CHANGELOG.md        │ ← Document the change
└────────────────────────┘
         ↓
Test with Dashboard
         ↓
Verify Results Reasonable
         ↓
Commit & Push
         ↓
COMMUNITY BENEFITS
```

## 📊 Statistics Flow by File

### fair_dashboard.py
```
┌──────────────────────────────────────┐
│ Line 100: load_preset() function    │ ← STATISTICS STORED HERE
├──────────────────────────────────────┤
│ Lines 100-142: Preset dictionary    │
│  ├─ Ransomware Attack               │
│  ├─ Data Breach (GDPR)              │
│  ├─ Business Email Compromise       │
│  ├─ DDoS Attack                     │
│  └─ Insider Threat                  │
└──────────────┬───────────────────────┘
               │
               ↓ (passed to)
┌──────────────────────────────────────┐
│ Lines 200-250: Parameter inputs     │ ← USER INTERFACE
├──────────────────────────────────────┤
│  • TEF sliders                      │
│  • Vulnerability sliders            │
│  • Loss magnitude inputs            │
└──────────────┬───────────────────────┘
               │
               ↓ (passed to)
┌──────────────────────────────────────┐
│ Lines 280-320: Run simulation       │ ← SIMULATION CALL
├──────────────────────────────────────┤
│  sim.run_simulation(                │
│    tef_dist=tef,                    │
│    vuln_prob=total_vulnerability,   │
│    primary_loss_dist=primary_loss,  │
│    ...                              │
│  )                                  │
└──────────────┬───────────────────────┘
               │
               ↓ (returns)
┌──────────────────────────────────────┐
│ Lines 350-600: Display results      │ ← OUTPUT
├──────────────────────────────────────┤
│  • Key metrics                      │
│  • Interactive charts               │
│  • Risk recommendations             │
│  • Export buttons                   │
└──────────────────────────────────────┘
```

### fair_monte_carlo.py
```
┌──────────────────────────────────────┐
│ Lines 1-100: FAIRDistribution class │ ← DISTRIBUTION CREATION
├──────────────────────────────────────┤
│  • PERT distribution                │
│  • Lognormal distribution           │
│  • Uniform distribution             │
│  • Triangular distribution          │
└──────────────┬───────────────────────┘
               │
               ↓ (used by)
┌──────────────────────────────────────┐
│ Lines 110-250: Simulation class     │ ← MONTE CARLO ENGINE
├──────────────────────────────────────┤
│  • run_simulation()                 │
│    ├─ Sample distributions          │
│    ├─ Calculate LEF                 │
│    ├─ Determine events (Poisson)    │
│    ├─ Sample loss magnitudes        │
│    └─ Aggregate annual loss         │
│                                     │
│  • calculate_statistics()           │
│    ├─ Mean, median, std dev         │
│    ├─ Percentiles                   │
│    └─ Probability metrics           │
└──────────────┬───────────────────────┘
               │
               ↓ (generates)
┌──────────────────────────────────────┐
│ Lines 360-400: Example scenario     │ ← DEMONSTRATION
├──────────────────────────────────────┤
│  • Shows how to use the engine      │
│  • Contains sample parameters       │
│  • Prints results                   │
│  • Generates charts                 │
└──────────────────────────────────────┘
```

### docs/FAIR_Parameter_Reference.md
```
┌──────────────────────────────────────┐
│ Industry Benchmarks Section         │ ← REFERENCE DATA
├──────────────────────────────────────┤
│  • TEF by company size              │
│  • Vulnerability rates              │
│  • Loss magnitude ranges            │
│  • Industry modifiers               │
│  • Data source citations            │
└──────────────┬───────────────────────┘
               │
               ↓ (referenced by)
┌──────────────────────────────────────┐
│ Preset Values in Dashboard          │ ← PRACTICAL USE
├──────────────────────────────────────┤
│  "Based on Reference.md table X"    │
└──────────────────────────────────────┘
```

## 🎯 Quick Lookup: "I need to update X"

```
WHAT TO UPDATE              WHERE TO GO              LINE NUMBERS
────────────────────────────────────────────────────────────────
Ransomware frequency        fair_dashboard.py        103
Data breach frequency       fair_dashboard.py        110
BEC frequency              fair_dashboard.py        117
DDoS frequency             fair_dashboard.py        124
Insider frequency          fair_dashboard.py        131

Vulnerability rates        fair_dashboard.py        104-106, etc.
Loss magnitudes           fair_dashboard.py        105-107, etc.
Secondary loss prob       fair_dashboard.py        107, etc.

Benchmark tables          docs/Reference.md        Throughout
Data source citations     docs/Reference.md        Throughout

Example code              fair_monte_carlo.py      360-400
```

## 🔍 Tracing a Statistic

**Example: "Where does '300 ransomware attempts' come from?"**

```
1. RESEARCH SOURCE
   ↓
   Sophos State of Ransomware 2024
   Page 23: "Small businesses report median of 300 ransomware attempts/year"
   
2. DOCUMENTED IN
   ↓
   docs/FAIR_Parameter_Reference.md
   Table: "Ransomware Attempts by Company Size"
   
3. CODED IN
   ↓
   fair_dashboard.py, line 103
   "tef_mode": 300,  # Sophos 2024, p.23
   
4. USED IN
   ↓
   FAIRDistribution() creates PERT distribution
   
5. SAMPLED IN
   ↓
   Monte Carlo simulation (10,000 times)
   
6. RESULTS IN
   ↓
   Mean LEF, ALE calculations
   
7. DISPLAYED AS
   ↓
   "Expected 7.7 loss events per year"
   "Mean ALE: €618,000"
```

## 🎓 Understanding the Flow

**Key Insight:** Statistics flow from research → documentation → code → simulation → results

**Transparency:** Every number can be traced back to a source

**Updateability:** Change in one place propagates through the tool

**Reproducibility:** Same inputs = same outputs (with optional random seed)

---

**Need to update statistics?** Follow the flow backwards:
1. Find the statistic in the output
2. Trace it to the simulation
3. Find it in the code
4. Update with proper documentation
5. Test and verify

**Questions?** See UPDATING_STATISTICS_GUIDE.md for detailed instructions!
