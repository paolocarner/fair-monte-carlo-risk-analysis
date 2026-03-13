# -*- coding: utf-8 -*-
"""
FAIR Monte Carlo - Interactive Risk Analysis Dashboard

A web-based interactive tool for running FAIR risk assessments with real-time visualization.
Perfect for client presentations and scenario modeling.

To run: streamlit run fair_dashboard.py
"""

import os
import json

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FAIR Risk Analysis Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'sim' not in st.session_state:
    st.session_state.sim = None
# Persist custom risk-threshold values across profile switches
if 'custom_thresholds' not in st.session_state:
    st.session_state.custom_thresholds = {'low': 0.5, 'moderate': 1.0}

# ---------------------------------------------------------------------------
# Preset loader (cached so JSON is only read once)
# ---------------------------------------------------------------------------
@st.cache_data
def load_all_presets() -> dict:
    presets_path = os.path.join(os.path.dirname(__file__), 'presets.json')
    with open(presets_path) as f:
        return json.load(f)

PRESETS = load_all_presets()
PRESET_NAMES = [k for k in PRESETS if not k.startswith('_')]


def load_preset(scenario: str) -> dict:
    return PRESETS.get(scenario, PRESETS['_default'])


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
def validate_inputs(tef_min, tef_mode, tef_max,
                    primary_min, primary_mode, primary_max,
                    secondary_min, secondary_mode, secondary_max) -> list[str]:
    errors = []
    if not (tef_min <= tef_mode <= tef_max):
        errors.append(
            f"TEF: min ({tef_min:,}) must be ≤ mode ({tef_mode:,}) ≤ max ({tef_max:,})"
        )
    if not (primary_min <= primary_mode <= primary_max):
        errors.append(
            f"Primary Loss: min ({primary_min:,}) must be ≤ mode ({primary_mode:,}) ≤ max ({primary_max:,})"
        )
    if not (secondary_min <= secondary_mode <= secondary_max):
        errors.append(
            f"Secondary Loss: min ({secondary_min:,}) must be ≤ mode ({secondary_mode:,}) ≤ max ({secondary_max:,})"
        )
    return errors


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="main-header">🛡️ FAIR Risk Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown("**Interactive Monte Carlo Simulation for Cybersecurity Risk Quantification**")
st.markdown("---")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("bare_logo.png"):
        st.image("bare_logo.png", width=150)
    st.header("⚙️ Configuration")

    scenario_preset = st.selectbox(
        "📋 Load Preset Scenario",
        ["Custom"] + PRESET_NAMES,
        help="Load pre-configured risk scenarios. Select 'Custom' to define your own parameters."
    )

    st.markdown("---")

    # Client information
    st.subheader("👤 Client Information")
    client_name = st.text_input(
        "Client Name",
        value="Example Company",
        help="Used for report generation and documentation."
    )
    annual_revenue = st.number_input(
        "Annual Revenue (€)",
        min_value=100_000,
        max_value=1_000_000_000,
        value=5_000_000,
        step=100_000,
        format="%d",
        help="Used to calculate risk as a percentage of revenue and determine risk appetite thresholds."
    )
    industry = st.selectbox(
        "Industry",
        ["Professional Services", "Financial Services", "Healthcare",
         "E-commerce", "Manufacturing", "Technology", "Other"],
        help="Helps contextualise risk tolerance and industry-specific benchmarking."
    )

    st.markdown("---")

    # Simulation settings
    st.subheader("🔧 Simulation Settings")
    n_simulations = st.select_slider(
        "Number of Simulations",
        options=[1000, 5000, 10000, 20000, 50000],
        value=10000,
        help="Higher values give more accurate results but take longer. 10,000 is a good default."
    )

    currency = st.selectbox(
        "Currency",
        ["€", "$", "£", "CHF"],
        index=0,
        help="Currency symbol used throughout reports and visualisations."
    )

    use_seed = st.checkbox(
        "Fix random seed (reproducibility)",
        value=False,
        help="When enabled, the same parameters will always produce identical results."
    )
    random_seed = None
    if use_seed:
        random_seed = st.number_input(
            "Random seed",
            min_value=0,
            max_value=99999,
            value=42,
            step=1,
            help="Integer seed for NumPy's random number generator."
        )

    st.markdown("---")

    # Risk tolerance
    st.subheader("🎚️ Risk Tolerance Settings")

    risk_profile = st.selectbox(
        "Risk Appetite Profile",
        ["Conservative", "Moderate", "Aggressive", "Custom"],
        index=1,
        help="Conservative: financial services. Moderate: most orgs. Aggressive: startups."
    )

    PROFILE_DEFAULTS = {
        "Conservative": (0.2, 0.5),
        "Moderate":     (0.5, 1.0),
        "Aggressive":   (1.0, 2.0),
    }

    if risk_profile == "Custom":
        default_low = st.session_state.custom_thresholds['low']
        default_moderate = st.session_state.custom_thresholds['moderate']
    else:
        default_low, default_moderate = PROFILE_DEFAULTS[risk_profile]

    col_risk1, col_risk2 = st.columns(2)
    with col_risk1:
        low_threshold = st.number_input(
            "Low Risk (%)",
            min_value=0.01,
            max_value=10.0,
            value=default_low,
            step=0.1,
            disabled=(risk_profile != "Custom"),
            help="ALE below this % of revenue is LOW RISK."
        )
    with col_risk2:
        moderate_threshold = st.number_input(
            "Moderate Risk (%)",
            min_value=0.01,
            max_value=10.0,
            value=default_moderate,
            step=0.1,
            disabled=(risk_profile != "Custom"),
            help="ALE above this % of revenue is HIGH RISK."
        )

    # Persist custom values so they survive profile switches
    if risk_profile == "Custom":
        st.session_state.custom_thresholds = {
            'low': low_threshold,
            'moderate': moderate_threshold
        }

    st.session_state.risk_thresholds = {
        'low': low_threshold,
        'moderate': moderate_threshold,
        'profile': risk_profile
    }

    with st.expander("📊 Your Risk Tolerance Summary"):
        st.markdown(f"""
        **Profile:** {risk_profile}

        **Risk Levels (as % of annual revenue):**
        - 🟢 **Low Risk (Acceptable):** < {low_threshold}%
        - 🟡 **Moderate Risk:** {low_threshold}% – {moderate_threshold}%
        - 🔴 **High Risk:** > {moderate_threshold}%

        **For your organisation ({currency}{annual_revenue:,}):**
        - 🟢 Low Risk: < {currency}{annual_revenue * low_threshold / 100:,.0f}
        - 🟡 Moderate Risk: {currency}{annual_revenue * low_threshold / 100:,.0f} – {currency}{annual_revenue * moderate_threshold / 100:,.0f}
        - 🔴 High Risk: > {currency}{annual_revenue * moderate_threshold / 100:,.0f}
        """)

# ---------------------------------------------------------------------------
# Load preset values
# ---------------------------------------------------------------------------
preset_values = load_preset(scenario_preset if scenario_preset != "Custom" else "_default")

# ---------------------------------------------------------------------------
# Main content — parameters
# ---------------------------------------------------------------------------
st.header("📊 Risk Scenario Parameters")
st.info(
    "💡 **FAIR factors are grouped by source:** "
    "🌍 **External factors** depend on the threat landscape. "
    "🏢 **Internal factors** depend on your organisation's posture and costs."
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌍 External Factors (Threat Landscape)")
    with st.container(border=True):
        st.markdown("**🎯 Contact Frequency**")
        st.caption("Industry-wide threat activity — NOT organisation-specific")

        vuln_contact = st.slider(
            "Contact Frequency (%)",
            min_value=0.0,
            max_value=100.0,
            value=preset_values["vuln_contact"] * 100,
            step=1.0,
            help=(
                "Contact Frequency (CF): The probable frequency that a threat agent will "
                "come into contact with your asset. Based on industry-wide data."
            )
        ) / 100

        st.caption(f"📊 Industry benchmark: {vuln_contact*100:.1f}% contact rate")

    st.markdown("---")

    st.markdown("### 🏢 Internal Factors (Your Organisation)")

    with st.container(border=True):
        st.markdown("**🎯 Threat Event Frequency (TEF)**")
        st.caption("How many times per year are YOU specifically targeted?")

        col_tef1, col_tef2 = st.columns(2)
        with col_tef1:
            tef_min = st.number_input(
                "Minimum attempts/year",
                min_value=1, max_value=100_000,
                value=preset_values["tef_min"], step=10,
                help="Minimum probable frequency of threat events per year."
            )
            tef_mode = st.number_input(
                "Most likely attempts/year",
                min_value=1, max_value=100_000,
                value=preset_values["tef_mode"], step=10,
                help="Most likely (mode) frequency of threat events per year."
            )
        with col_tef2:
            tef_max = st.number_input(
                "Maximum attempts/year",
                min_value=1, max_value=100_000,
                value=preset_values["tef_max"], step=10,
                help="Maximum probable frequency of threat events per year."
            )
            st.markdown("")
            vuln_action = st.slider(
                "Probability of Action (%)",
                min_value=0.0, max_value=100.0,
                value=preset_values["vuln_action"] * 100, step=1.0,
                help=(
                    "Probability of Action (PoA): Once contact occurs, the probability "
                    "that the threat agent will act. Scales industry data to your specific threat level."
                ),
                key="poa_slider"
            ) / 100

        st.caption(
            f"📈 TEF = CF × PoA = {vuln_contact*100:.1f}% × {vuln_action*100:.1f}% "
            f"(Your specific threat level)"
        )

    with st.container(border=True):
        st.markdown("**🔓 Vulnerability (Your Controls)**")
        st.caption("How effective are YOUR security controls?")

        vuln_rate = st.slider(
            "Vulnerability Rate (%)",
            min_value=0.0, max_value=100.0,
            value=preset_values["vuln_rate"] * 100, step=1.0,
            help=(
                "Vulnerability: Probability that a threat event results in a loss event. "
                "Inverse of your controls' effectiveness."
            )
        ) / 100

with col2:
    st.markdown("### 💸 Loss Magnitude (Your Organisation)")

    with st.container(border=True):
        st.markdown("**💰 Primary Loss Magnitude**")
        st.caption("Direct costs when an incident occurs")

        primary_min = st.number_input(
            "Minimum primary loss",
            min_value=100, max_value=10_000_000,
            value=preset_values["primary_min"], step=1000,
            help="Minimum direct loss (ransom payment, immediate response costs, hardware replacement)."
        )
        primary_mode = st.number_input(
            "Most likely primary loss",
            min_value=100, max_value=10_000_000,
            value=preset_values["primary_mode"], step=1000,
            help="Most likely (mode) direct cost per incident."
        )
        primary_max = st.number_input(
            "Maximum primary loss",
            min_value=100, max_value=10_000_000,
            value=preset_values["primary_max"], step=1000,
            help="Maximum probable direct cost in a worst-case incident."
        )

    with st.container(border=True):
        st.markdown("**📉 Secondary Loss Magnitude**")
        st.caption("Indirect costs (fines, reputation, legal, etc.)")

        secondary_min = st.number_input(
            "Minimum secondary loss",
            min_value=0, max_value=10_000_000,
            value=preset_values["secondary_min"], step=1000,
            help="Minimum indirect losses (fines, lawsuits, reputational damage)."
        )
        secondary_mode = st.number_input(
            "Most likely secondary loss",
            min_value=0, max_value=10_000_000,
            value=preset_values["secondary_mode"], step=1000,
            help="Most likely (mode) indirect cost following an incident."
        )
        secondary_max = st.number_input(
            "Maximum secondary loss",
            min_value=0, max_value=10_000_000,
            value=preset_values["secondary_max"], step=1000,
            help="Maximum probable indirect cost including worst-case regulatory penalties."
        )

        secondary_prob = st.slider(
            "Probability of Secondary Losses (%)",
            min_value=0.0, max_value=100.0,
            value=preset_values["secondary_prob"] * 100, step=5.0,
            help=(
                "Secondary Loss Event Frequency: Probability that a primary event "
                "also triggers secondary losses (e.g., regulatory fines)."
            )
        ) / 100

# ---------------------------------------------------------------------------
# Derived values (computed outside the column blocks to be safely in scope)
# ---------------------------------------------------------------------------
total_vulnerability = vuln_contact * vuln_action * vuln_rate

col_v1, col_v2 = st.columns(2)
with col_v1:
    st.metric(
        "Total Vulnerability",
        f"{total_vulnerability*100:.3f}%",
        help="Combined probability of a successful attack: Contact × Action × Vulnerability."
    )
with col_v2:
    expected_lef = tef_mode * total_vulnerability
    st.metric(
        "Expected Loss Events/Year",
        f"{expected_lef:.2f}",
        help="Loss Event Frequency (LEF) = TEF × Vulnerability."
    )

# ---------------------------------------------------------------------------
# Validation + Run button
# ---------------------------------------------------------------------------
st.markdown("---")

validation_errors = validate_inputs(
    tef_min, tef_mode, tef_max,
    primary_min, primary_mode, primary_max,
    secondary_min, secondary_mode, secondary_max
)

if validation_errors:
    for err in validation_errors:
        st.error(f"❌ {err}")

col_button1, col_button2, col_button3 = st.columns([1, 1, 1])
with col_button2:
    run_button = st.button(
        "🚀 Run Simulation",
        type="primary",
        disabled=bool(validation_errors)
    )

if run_button:
    with st.spinner('Running Monte Carlo simulation…'):
        try:
            tef = FAIRDistribution(
                dist_type='pert',
                min_val=tef_min, mode_val=tef_mode, max_val=tef_max
            )
            primary_loss = FAIRDistribution(
                dist_type='lognormal',
                min_val=primary_min, mode_val=primary_mode, max_val=primary_max
            )
            secondary_loss = FAIRDistribution(
                dist_type='lognormal',
                min_val=secondary_min, mode_val=secondary_mode, max_val=secondary_max
            )

            sim = FAIRMonteCarloSimulation(
                n_simulations=n_simulations,
                random_seed=random_seed
            )
            stats = sim.run_simulation(
                tef_dist=tef,
                vuln_prob=total_vulnerability,
                primary_loss_dist=primary_loss,
                secondary_loss_dist=secondary_loss,
                secondary_loss_prob=secondary_prob
            )

            st.session_state.simulation_run = True
            st.session_state.stats = stats
            st.session_state.sim = sim
            st.success("✅ Simulation complete!")

        except ValueError as e:
            st.error(f"❌ **Simulation Error**: {e}")
            st.info("Please check your input parameters and ensure they are valid.")
        except Exception as e:
            st.error(f"❌ **Unexpected Error**: {e}")
            st.info("An unexpected error occurred. Please try again.")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if st.session_state.simulation_run and st.session_state.stats:
    stats = st.session_state.stats
    sim = st.session_state.sim
    annual_losses = sim.results['annual_losses']

    st.markdown("---")
    st.header("📈 Simulation Results")

    st.subheader("🎯 Key Risk Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mean ALE",
            f"{currency}{stats['ale_mean']:,.0f}",
            delta=f"{(stats['ale_mean']/annual_revenue)*100:.2f}% of revenue",
            help="Mean expected annual loss from this risk scenario."
        )
    with col2:
        st.metric(
            "Median ALE",
            f"{currency}{stats['ale_median']:,.0f}",
            help="Middle value of the annual loss distribution — more representative than mean for skewed distributions."
        )
    with col3:
        st.metric(
            "95th Percentile",
            f"{currency}{stats['percentiles']['95th']:,.0f}",
            help="Loss value exceeded only 5% of the time. Useful for insurance coverage decisions."
        )
    with col4:
        st.metric(
            "Loss Event Frequency",
            f"{stats['lef_mean']:.2f}/year",
            help="Expected number of successful loss events per year."
        )

    # Risk appetite indicator
    ale_pct_revenue = (stats['ale_mean'] / annual_revenue) * 100
    thresholds = st.session_state.get('risk_thresholds', {'low': 0.5, 'moderate': 1.0, 'profile': 'Moderate'})
    low_t = thresholds['low']
    moderate_t = thresholds['moderate']

    if ale_pct_revenue > moderate_t:
        st.error(f"🔴 **HIGH RISK**: Mean ALE is {ale_pct_revenue:.2f}% of revenue (>{moderate_t}%). Immediate risk treatment recommended.")
    elif ale_pct_revenue > low_t:
        st.warning(f"🟡 **MODERATE RISK**: Mean ALE is {ale_pct_revenue:.2f}% of revenue ({low_t}%–{moderate_t}%). Consider cost-effective controls.")
    else:
        st.success(f"🟢 **LOW RISK (ACCEPTABLE)**: Mean ALE is {ale_pct_revenue:.2f}% of revenue (<{low_t}%). May accept or implement low-cost controls.")

    st.markdown("---")

    # ---------------------------------------------------------------------------
    # Visualisations
    # ---------------------------------------------------------------------------
    st.subheader("📊 Interactive Visualisations")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribution", "📈 Exceedance Curve", "🎲 Percentiles", "📉 LEF Analysis"])

    with tab1:
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=annual_losses, nbinsx=50, name='Annual Loss',
            marker_color='#2E86AB', opacity=0.7
        ))
        fig_dist.add_vline(
            x=stats['ale_mean'], line_dash="dash", line_color="red",
            annotation_text=f"Mean: {currency}{stats['ale_mean']:,.0f}",
            annotation_position="top right"
        )
        fig_dist.add_vline(
            x=stats['ale_median'], line_dash="dash", line_color="orange",
            annotation_text=f"Median: {currency}{stats['ale_median']:,.0f}",
            annotation_position="top left"
        )
        low_threshold_value = annual_revenue * low_t / 100
        moderate_threshold_value = annual_revenue * moderate_t / 100
        fig_dist.add_vline(
            x=low_threshold_value, line_dash="dot", line_color="green", opacity=0.7,
            annotation_text=f"Low Risk: {currency}{low_threshold_value:,.0f}",
            annotation_position="bottom left"
        )
        fig_dist.add_vline(
            x=moderate_threshold_value, line_dash="dot", line_color="red", opacity=0.7,
            annotation_text=f"High Risk: {currency}{moderate_threshold_value:,.0f}",
            annotation_position="bottom right"
        )
        fig_dist.update_layout(
            title="Distribution of Annual Losses (with Risk Tolerance Thresholds)",
            xaxis_title=f"Annual Loss ({currency})",
            yaxis_title="Frequency",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.caption(
            f"🟢 Green line: Low risk threshold ({low_t}% of revenue) | "
            f"🔴 Red line: High risk threshold ({moderate_t}% of revenue)"
        )

    with tab2:
        sorted_losses = np.sort(annual_losses)
        exceedance_prob = 1 - np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)

        fig_exceed = go.Figure()
        fig_exceed.add_trace(go.Scatter(
            x=sorted_losses, y=exceedance_prob * 100,
            mode='lines', name='Exceedance Probability',
            line=dict(color='#A23B72', width=3),
            fill='tozeroy', fillcolor='rgba(162, 59, 114, 0.1)'
        ))
        for pct in [95, 99]:
            pct_val = stats['percentiles'][f'{pct}th']
            fig_exceed.add_vline(
                x=pct_val, line_dash="dot", line_color="red", opacity=0.5,
                annotation_text=f"{pct}th: {currency}{pct_val:,.0f}",
                annotation_position="top"
            )
        fig_exceed.update_layout(
            title="Loss Exceedance Curve",
            xaxis_title=f"Annual Loss ({currency})",
            yaxis_title="Probability of Exceedance (%)",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_exceed, use_container_width=True)
        st.info("💡 **Interpretation**: Shows the probability that annual losses will exceed a given amount. Use the 95th percentile for insurance coverage decisions.")

    with tab3:
        pct_keys = ['10th', '25th', '50th', '75th', '90th', '95th', '99th']
        pct_values = [stats['percentiles'][p] for p in pct_keys]

        fig_pct = go.Figure()
        fig_pct.add_trace(go.Bar(
            x=pct_keys, y=pct_values,
            marker_color=['#06A77D', '#06A77D', '#2E86AB', '#2E86AB', '#F18F01', '#A23B72', '#DC143C'],
            text=[f"{currency}{v:,.0f}" for v in pct_values],
            textposition='outside'
        ))
        fig_pct.update_layout(
            title="Loss Distribution by Percentile",
            xaxis_title="Percentile",
            yaxis_title=f"Annual Loss ({currency})",
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_pct, use_container_width=True)

        st.subheader("📋 Detailed Percentiles")
        pct_table = pd.DataFrame({
            'Percentile': ['10th', '25th', '50th (Median)', '75th', '90th', '95th', '99th'],
            'Annual Loss': [f"{currency}{stats['percentiles'][p]:,.2f}" for p in pct_keys],
            '% of Revenue': [f"{(stats['percentiles'][p]/annual_revenue)*100:.2f}%" for p in pct_keys]
        })
        st.dataframe(pct_table, hide_index=True)

    with tab4:
        lef_samples = sim.results['lef_samples']

        fig_lef = go.Figure()
        fig_lef.add_trace(go.Histogram(
            x=lef_samples, nbinsx=50, name='Loss Event Frequency',
            marker_color='#F18F01', opacity=0.7
        ))
        fig_lef.add_vline(
            x=stats['lef_mean'], line_dash="dash", line_color="red",
            annotation_text=f"Mean: {stats['lef_mean']:.3f}",
            annotation_position="top right"
        )
        fig_lef.update_layout(
            title="Distribution of Loss Event Frequency",
            xaxis_title="Loss Events per Year",
            yaxis_title="Frequency",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_lef, use_container_width=True)
        st.metric(
            "Probability of at least one loss event",
            f"{stats['probability_of_loss']*100:.1f}%",
            help="Probability that at least one successful loss event occurs during the year."
        )

    st.markdown("---")

    # ---------------------------------------------------------------------------
    # Risk treatment recommendations
    # ---------------------------------------------------------------------------
    st.header("💡 Risk Treatment Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛡️ Control Investment Analysis")

        control_reduction = st.slider(
            "Estimated Risk Reduction from Controls (%)",
            min_value=0, max_value=95, value=70, step=5,
            help="Expected % reduction in ALE from implementing security controls."
        )
        control_cost = st.number_input(
            f"Annual Control Cost ({currency})",
            min_value=0, max_value=1_000_000, value=25_000, step=1000,
            help="Total annual cost of implementing and maintaining the control."
        )

        ale_reduction = stats['ale_mean'] * (control_reduction / 100)
        net_benefit = ale_reduction - control_cost
        rosi = (net_benefit / control_cost * 100) if control_cost > 0 else 0

        st.metric("ALE Reduction", f"{currency}{ale_reduction:,.0f}",
                  help="Expected annual reduction in losses from this control.")
        st.metric("Net Benefit", f"{currency}{net_benefit:,.0f}",
                  help="ALE Reduction minus Control Cost.")
        st.metric("ROSI", f"{rosi:.0f}%",
                  help="Return on Security Investment = (Net Benefit / Control Cost) × 100.")

        if rosi > 100:
            st.success(f"✅ **Excellent Investment**: ROSI of {rosi:.0f}% indicates strong value.")
        elif rosi > 0:
            st.info(f"💡 **Positive ROI**: ROSI of {rosi:.0f}% — consider implementation.")
        else:
            st.warning(f"⚠️ **Negative ROI**: ROSI of {rosi:.0f}% — may not be cost-effective.")

    with col2:
        st.subheader("🏥 Insurance Recommendation")

        st.write("**Recommended Coverage Limits:**")
        st.write(f"- Minimum Coverage: {currency}{stats['percentiles']['90th']:,.0f} (90th percentile)")
        st.write(f"- Recommended Coverage: {currency}{stats['percentiles']['95th']:,.0f} (95th percentile)")
        st.write(f"- Conservative Coverage: {currency}{stats['percentiles']['99th']:,.0f} (99th percentile)")
        st.write(f"\n**Suggested Deductible:** {currency}{stats['ale_median']:,.0f} (median ALE)")

        coverage_95 = stats['percentiles']['95th']
        premium_low = coverage_95 * 0.03
        premium_high = coverage_95 * 0.05
        st.write(f"\n**Estimated Annual Premium:** {currency}{premium_low:,.0f} – {currency}{premium_high:,.0f}")
        st.caption("(Typically 3–5% of coverage amount for SMBs)")
        st.info(
            "💡 **Tip**: Coverage at the 95th percentile protects against worst-case scenarios "
            "while keeping premiums reasonable. Align the deductible with your risk appetite."
        )

    st.markdown("---")

    # ---------------------------------------------------------------------------
    # Export
    # ---------------------------------------------------------------------------
    st.header("💾 Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        export_data = {
            "client_name": client_name,
            "scenario": scenario_preset,
            "annual_revenue": annual_revenue,
            "industry": industry,
            "simulation_parameters": {
                "n_simulations": n_simulations,
                "random_seed": random_seed,
                "tef": {"min": tef_min, "mode": tef_mode, "max": tef_max},
                "vulnerability": total_vulnerability,
                "primary_loss": {"min": primary_min, "mode": primary_mode, "max": primary_max},
                "secondary_loss": {"min": secondary_min, "mode": secondary_mode, "max": secondary_max},
                "secondary_probability": secondary_prob
            },
            "results": stats
        }
        json_str = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"{client_name.replace(' ', '_')}_fair_analysis.json",
            mime="application/json",
            help="Full analysis results in JSON format."
        )

    with col2:
        raw_data_df = pd.DataFrame({
            'annual_loss': sim.results['annual_losses'],
            'loss_event_frequency': sim.results['lef_samples'],
            'threat_event_frequency': sim.results['tef_samples'],
            'actual_events': sim.results['actual_events']
        })
        csv = raw_data_df.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV",
            data=csv,
            file_name=f"{client_name.replace(' ', '_')}_simulation_data.csv",
            mime="text/csv",
            help="Raw Monte Carlo iteration data for analysis in Excel or other tools."
        )

    with col3:
        seed_line = f"Random Seed: {random_seed}" if random_seed is not None else "Random Seed: none (non-reproducible)"
        report = f"""FAIR RISK ANALYSIS REPORT
{'='*60}

Client: {client_name}
Industry: {industry}
Annual Revenue: {currency}{annual_revenue:,}
Scenario: {scenario_preset}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

RISK METRICS
{'='*60}
Mean ALE: {currency}{stats['ale_mean']:,.2f}
Median ALE: {currency}{stats['ale_median']:,.2f}
Standard Deviation: {currency}{stats['ale_std']:,.2f}
ALE as % of Revenue: {ale_pct_revenue:.2f}%

PERCENTILES
{'='*60}
10th Percentile: {currency}{stats['percentiles']['10th']:,.2f}
25th Percentile: {currency}{stats['percentiles']['25th']:,.2f}
50th Percentile: {currency}{stats['percentiles']['50th']:,.2f}
75th Percentile: {currency}{stats['percentiles']['75th']:,.2f}
90th Percentile: {currency}{stats['percentiles']['90th']:,.2f}
95th Percentile: {currency}{stats['percentiles']['95th']:,.2f}
99th Percentile: {currency}{stats['percentiles']['99th']:,.2f}

LOSS EVENT FREQUENCY
{'='*60}
Mean LEF: {stats['lef_mean']:.4f} events/year
Median LEF: {stats['lef_median']:.4f} events/year
Probability of Loss: {stats['probability_of_loss']*100:.1f}%

SIMULATION PARAMETERS
{'='*60}
Number of Simulations: {n_simulations:,}
{seed_line}
Threat Event Frequency: {tef_min}–{tef_mode}–{tef_max}
Vulnerability: {total_vulnerability*100:.3f}%
Primary Loss Range: {currency}{primary_min:,} – {currency}{primary_max:,}
Secondary Loss Range: {currency}{secondary_min:,} – {currency}{secondary_max:,}
Secondary Loss Probability: {secondary_prob*100:.1f}%

Generated by BARE Cybersecurity FAIR Analysis Tool
"""
        st.download_button(
            label="📝 Download Report",
            data=report,
            file_name=f"{client_name.replace(' ', '_')}_fair_report.txt",
            mime="text/plain",
            help="Formatted text report for documentation and presentation."
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p><strong>FAIR Monte Carlo Risk Analysis Dashboard</strong></p>
        <p>Created for BARE Cybersecurity | Version 1.1</p>
        <p>Based on Factor Analysis of Information Risk (FAIR) methodology</p>
    </div>
    """, unsafe_allow_html=True)
