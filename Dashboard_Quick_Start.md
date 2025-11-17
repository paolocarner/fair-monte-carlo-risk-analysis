# 🎨 Interactive FAIR Dashboard - Quick Start Guide

## What You Get

A beautiful, **web-based interactive dashboard** that runs in your browser! Perfect for:
- 👥 **Client presentations** - adjust parameters live during meetings
- 🎯 **Scenario modeling** - instantly see impact of changing controls
- 📊 **Professional visualizations** - interactive charts with Plotly
- 💾 **Easy exports** - JSON, CSV, and text reports with one click

## 🚀 Installation

### Step 1: Install Extra Packages

You need to install Streamlit and Plotly (on top of the packages you already have):

```bash
pip3 install streamlit plotly
```

### Step 2: Launch the Dashboard

```bash
streamlit run fair_dashboard.py
```

Or if that doesn't work:
Try run it in a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or

venv\Scripts\activate     # Windows
```

That's it! Your browser will automatically open to the dashboard at `http://localhost:8501`

## 🎯 Features

### 📋 Preset Scenarios
Choose from ready-to-use scenarios:
- Ransomware Attack
- Data Breach (GDPR)
- Business Email Compromise
- DDoS Attack
- Insider Threat
- Custom (build your own)

### ⚙️ Interactive Parameters
Adjust everything with sliders and inputs:
- **Threat Event Frequency** (min, mode, max)
- **Vulnerability Components** (contact, action, vulnerability)
- **Loss Magnitudes** (primary and secondary)
- **Secondary Loss Probability**

See the impact **immediately** as you adjust!

### 📊 Live Visualizations
Four interactive chart types:
1. **Distribution Chart** - histogram of annual losses
2. **Exceedance Curve** - probability of exceeding any loss amount
3. **Percentiles View** - bar chart and detailed table
4. **LEF Analysis** - loss event frequency distribution

### 💡 Automatic Recommendations
The dashboard provides:
- **Risk appetite assessment** (high/moderate/acceptable)
- **Control investment analysis** with ROSI calculation
- **Insurance recommendations** with coverage amounts
- **Treatment options** based on your scenario

### 💾 One-Click Exports
Download your results in multiple formats:
- **JSON** - complete simulation data
- **CSV** - raw simulation results for further analysis
- **TXT Report** - formatted executive summary

## 🎬 How to Use

### Basic Workflow

1. **Launch**: `streamlit run fair_dashboard.py`

2. **Configure** (Left Sidebar):
   - Enter client name and revenue
   - Select industry
   - Choose a preset scenario or use "Custom"

3. **Adjust Parameters** (Main Area):
   - Fine-tune threat frequency
   - Adjust vulnerability sliders
   - Set loss magnitude ranges

4. **Run Simulation**:
   - Click the big "🚀 Run Simulation" button
   - Wait a few seconds (you'll see progress)

5. **Analyze Results**:
   - Review key metrics at the top
   - Explore interactive charts in tabs
   - Check risk treatment recommendations

6. **Export**:
   - Download JSON/CSV/Report for client deliverables
   - Take screenshots for presentations

### Advanced: Compare Scenarios

**Before/After Analysis:**

1. Run simulation with **current state** (no controls)
2. Note the Mean ALE
3. Adjust vulnerability sliders to reflect **with controls**
4. Run simulation again
5. Compare the two ALEs to show control effectiveness!

**Example:**
- Before: Vulnerability = 2% → Mean ALE = €600k
- After: Vulnerability = 0.3% → Mean ALE = €90k
- **Risk Reduction**: 85% (€510k savings)
- **If control costs €50k/year → ROSI = 920%**

## 🎨 Dashboard Sections Explained

### Key Metrics Row
- **Mean ALE**: Use for budget planning
- **Median ALE**: Typical year
- **95th Percentile**: For insurance coverage
- **LEF**: How often incidents occur

### Risk Appetite Indicator
- 🟢 **Green (< 0.5% revenue)**: Acceptable risk
- 🟡 **Yellow (0.5-1% revenue)**: Moderate risk
- 🔴 **Red (> 1% revenue)**: High risk - immediate action needed

### Distribution Tab
Shows the full probability distribution of annual losses with mean and median marked.

### Exceedance Curve Tab
Critical for insurance decisions! Shows probability of exceeding any loss amount. Use 95th percentile for coverage.

### Percentiles Tab
Bar chart and detailed table of all key percentiles. Great for board presentations.

### LEF Analysis Tab
Shows how often loss events occur. Helps prioritize prevention controls.

### Recommendations Section
- **Control Investment**: Calculate ROSI for proposed security investments
- **Insurance**: Recommended coverage amounts and estimated premiums

## 💼 Client Presentation Tips

### During a vCISO Meeting

1. **Start with a preset** that matches their main concern
2. **Run the baseline** to show current risk
3. **Ask client**: "What if we reduce phishing clicks from 8% to 3%?"
4. **Adjust the slider live** and re-run
5. **Show the difference**: "That's €400k in reduced risk!"
6. **Calculate ROSI**: "For a €30k investment in training"
7. **Export the report** and send it to them after the meeting

### For Board Presentations

1. Use **95th percentile** - boards care about worst-case
2. Show **% of revenue** - more meaningful than absolute numbers
3. Keep it on **Percentiles Tab** - clean bar chart
4. Use **preset scenarios** - credible and well-researched
5. Export **TXT report** for the board pack

### For Budget Justification

1. Run **"current state"** scenario
2. Show Mean ALE: "We're exposed to €X per year"
3. Adjust for **"with proposed controls"**
4. Calculate savings: "This control reduces risk by €Y"
5. Show ROSI: "That's a Z% return on investment"

## 🔧 Customization

### Change the Logo
Edit line 62 in `fair_dashboard.py`:
```python
st.image("your_logo.png", use_container_width=True)
```

### Add Your Own Presets
Edit the `load_preset()` function around line 80 to add company-specific scenarios.

### Adjust Default Revenue
Change line 52:
```python
value=5000000,  # Change to your typical client size
```

## 🌐 Sharing with Clients

### Option 1: Screen Share (Easiest)
- Launch dashboard locally
- Share your screen in Zoom/Teams
- Adjust parameters live based on discussion

### Option 2: Deploy Online (Advanced)
You can deploy to Streamlit Cloud for free:

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

Now clients can access it via a URL.

### Option 3: Export and Email
- Run the simulation
- Export all three formats (JSON, CSV, TXT)
- Attach to email with executive summary

## 🎓 Pro Tips

1. **Save Common Scenarios**: Take screenshots of parameter settings for your typical clients

2. **Use During Discovery**: Run quick analysis during client discovery calls to show value immediately

3. **Prepare Presets**: Before client meetings, customize the presets to match their industry

4. **Compare Multiple Risks**: Run 3-5 scenarios (ransomware, phishing, BEC, etc.) and show combined exposure

5. **Show Control Layers**: Demonstrate how multiple controls work together by adjusting vulnerability step-by-step

6. **Print the Exceedance Curve**: Boards and C-suite love this chart - very intuitive

## 📱 Mobile/Tablet View

Streamlit dashboards work on tablets! Great for:
- Walking around during workshops
- Quick demos on the go
- Client site visits

## ⌨️ Keyboard Shortcuts

While dashboard is focused:
- `R` - Rerun the app (refresh)
- `C` - Clear cache
- `Ctrl/Cmd + K` - Command palette

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
```bash
pip3 install streamlit plotly
```

**Dashboard won't open automatically**
- Manually go to: http://localhost:8501
- Or use the "External URL" shown in terminal

**Simulation takes too long**
- Reduce number of simulations in sidebar (try 5,000)
- It's a slider on the left side

**Plots not loading**
- Check that plotly is installed: `pip3 show plotly`
- Reinstall if needed: `pip3 install --upgrade plotly`

**Port already in use**
- Another Streamlit app is running
- Kill it: `pkill -f streamlit`
- Or use a different port: `streamlit run fair_dashboard.py --server.port 8502`

## 🔄 Updates and Maintenance

To update the dashboard in the future:
```bash
pip3 install --upgrade streamlit plotly
```

To check current versions:
```bash
streamlit --version
pip3 show plotly
```

## 📖 Example Session

Here's a complete workflow:

```bash
# 1. Navigate to project
cd ~/fair-monte-carlo

# 2. Launch dashboard
streamlit run fair_dashboard.py

# Browser opens automatically...

# 3. In the sidebar:
#    - Client Name: "TechCorp BV"
#    - Annual Revenue: €8,000,000
#    - Industry: Technology
#    - Preset: Ransomware Attack

# 4. In main area:
#    - Review default parameters
#    - Maybe adjust vulnerability down if they have good controls
#    - Click "🚀 Run Simulation"

# 5. Review results:
#    - Mean ALE: €620,000 (7.8% of revenue - HIGH RISK!)
#    - 95th percentile: €1.3M
#    - Probability of incident: 99%

# 6. Show what controls could do:
#    - Set "Control Investment Analysis" to 75% reduction
#    - Cost: €50,000
#    - ROSI: 830%! 

# 7. Export:
#    - Download all three files
#    - Send to client
```

## 🎉 You're Ready!

The interactive dashboard makes FAIR analysis accessible and engaging. Clients love seeing the numbers change in real-time as you discuss different scenarios.

**Quick Start Command:**
```bash
streamlit run fair_dashboard.py
```

Enjoy your new interactive risk analysis tool! 🛡️

---

**Questions?** Check the main `FAIR_Monte_Carlo_Guide.md` for methodology details.

**Need help with a specific scenario?** Refer to `FAIR_Parameter_Reference.md` for industry benchmarks.
