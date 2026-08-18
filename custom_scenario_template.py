#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAIR Risk Analysis Template for BARE Cybersecurity Clients

Use this template to quickly set up custom risk scenarios for your vCISO engagements.
Simply fill in the parameters based on client interviews and industry data.
"""

from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution, derive_tef_from_contact

def run_custom_scenario():
    """
    Custom Risk Scenario Template
    
    INSTRUCTIONS:
    1. Fill in the CLIENT_INFO section
    2. Adjust RISK_SCENARIO parameters based on client context
    3. Run the script to generate results
    4. Use outputs for client presentations and documentation
    """
    
    # =================================================================
    # CLIENT INFORMATION
    # =================================================================
    CLIENT_NAME = "Your Client Name"
    RISK_SCENARIO_NAME = "Data Breach via Phishing"
    COMPANY_SIZE = "SMB"  # SMB, Mid-market, Enterprise
    ANNUAL_REVENUE = 5_000_000  # in euros
    INDUSTRY = "Professional Services"  # e.g., Healthcare, Financial, Manufacturing
    REGULATORY_FRAMEWORK = "GDPR"  # GDPR, NIS2, DORA, ISO 27001, etc.
    
    print(f"\n{'='*70}")
    print(f"FAIR RISK ANALYSIS FOR: {CLIENT_NAME}")
    print(f"Scenario: {RISK_SCENARIO_NAME}")
    print(f"Industry: {INDUSTRY} | Size: {COMPANY_SIZE} | Revenue: €{ANNUAL_REVENUE:,}")
    print(f"Regulatory Context: {REGULATORY_FRAMEWORK}")
    print(f"{'='*70}\n")
    
    # =================================================================
    # CONTACT FREQUENCY (CF) & PROBABILITY OF ACTION (PoA)
    # =================================================================
    # Per the Open Group O-RT Standard v3.0.1, Section 4.3.1:
    #     Threat Event Frequency (TEF) = Contact Frequency (CF) x Probability of Action (PoA)
    #
    # Contact Frequency is a COUNT of contacts/year (e.g. malicious emails
    # reaching the org) -- NOT a percentage. Probability of Action is the
    # probability that, once contact occurs, the threat agent actually acts.
    # Question: How many times per year does a threat agent contact this
    # organization, and what fraction of those contacts turn into a real
    # attempt?
    # Sources: Email gateway logs, SIEM data, industry reports, expert judgment

    # Example: Phishing emails targeting this organization
    cf_min = 3_750      # Conservative estimate (minimum contacts/year)
    cf_mode = 10_000    # Most likely (typical contacts/year)
    cf_max = 25_000     # Worst case (maximum contacts/year)

    # Probability of Action: fraction of contacts that are acted upon
    # Example: 8% of employees click phishing links
    probability_of_action = 0.08  # 8% click

    tef_min, tef_mode, tef_max = derive_tef_from_contact(
        cf_min, cf_mode, cf_max, probability_of_action
    )

    tef = FAIRDistribution(
        dist_type='pert',
        min_val=tef_min,
        mode_val=tef_mode,
        max_val=tef_max
    )

    print(f"📧 Contact Frequency (CF) & Threat Event Frequency (TEF)")
    print(f"   Contact Frequency:  {cf_min:,} / {cf_mode:,} / {cf_max:,} contacts/year (min/mode/max)")
    print(f"   Probability of Action: {probability_of_action*100:.1f}%")
    print(f"   → Derived TEF: {tef_min:,.1f} / {tef_mode:,.1f} / {tef_max:,.1f} attempts/year\n")

    # =================================================================
    # VULNERABILITY
    # =================================================================
    # Question: Once a threat event occurs (already counted in TEF above),
    # what's the probability it succeeds and becomes a loss event?
    # Per O-RT Section 4.3.2: Vulnerability = P(Threat Capability > Resistance
    # Strength). This is a SINGLE probability applied directly to TEF --
    # it must NOT be re-multiplied by Contact Frequency or Probability of
    # Action again, since those are already fully accounted for in TEF above.
    # (An earlier version of this template made exactly that mistake --
    # see the project's CHANGELOG.md for the writeup.)
    #
    # Example: of the ~800/year phishing attempts that get through and are
    # acted upon (TEF), a small fraction still result in a real compromise
    # despite EDR, backups, and other controls.
    total_vulnerability = 0.00017  # 0.017% -- see CHANGELOG.md / PRESET_METHODOLOGY.md
                                    # for how this order of magnitude was derived; validate
                                    # against real client control effectiveness data.

    print(f"🎯 Vulnerability")
    print(f"   Vulnerability: {total_vulnerability*100:.4f}% (probability a threat event becomes a loss event)")
    print(f"   → Expected loss events: ~{tef_mode * total_vulnerability:.2f}/year\n")
    
    # =================================================================
    # PRIMARY LOSS MAGNITUDE
    # =================================================================
    # Question: What are the direct costs when an incident occurs?
    # Include: Incident response, forensics, recovery, downtime, ransom
    
    # Cost components to consider:
    # - Incident response team: €10,000-50,000
    # - Digital forensics: €5,000-30,000
    # - System recovery/rebuild: €10,000-100,000
    # - Downtime costs: (Revenue/day × days down)
    # - Data recovery: €5,000-50,000
    # - Legal/PR: €5,000-100,000
    
    primary_min = 25_000    # Minimum direct costs
    primary_mode = 80_000   # Typical direct costs
    primary_max = 300_000   # Maximum direct costs
    
    primary_loss = FAIRDistribution(
        dist_type='lognormal',  # Right-skewed: most incidents cheaper, few very expensive
        min_val=primary_min,
        mode_val=primary_mode,
        max_val=primary_max
    )
    
    print(f"💰 Primary Loss (Direct Costs)")
    print(f"   Min: €{primary_min:,}")
    print(f"   Mode: €{primary_mode:,}")
    print(f"   Max: €{primary_max:,}\n")
    
    # =================================================================
    # SECONDARY LOSS MAGNITUDE
    # =================================================================
    # Question: What are the indirect costs?
    # Include: Regulatory fines, reputation damage, customer churn, legal
    
    # Cost components to consider:
    # - GDPR fines: Up to 4% annual revenue (€200k for €5M revenue)
    # - Customer churn: (# customers lost × customer LTV)
    # - Reputation damage: Lost deals, delayed sales
    # - Legal costs: €10,000-200,000
    # - Insurance premium increases
    # - Competitive disadvantage
    
    secondary_min = 10_000     # Minimum indirect costs
    secondary_mode = 50_000    # Typical indirect costs
    secondary_max = 200_000    # Maximum indirect costs (e.g., with regulatory fine)
    
    # Probability that secondary losses occur
    # Not every incident leads to regulatory fines or major reputation damage
    secondary_probability = 0.30  # 30% of incidents have secondary losses
    
    secondary_loss = FAIRDistribution(
        dist_type='lognormal',
        min_val=secondary_min,
        mode_val=secondary_mode,
        max_val=secondary_max
    )
    
    print(f"📉 Secondary Loss (Indirect Costs)")
    print(f"   Min: €{secondary_min:,}")
    print(f"   Mode: €{secondary_mode:,}")
    print(f"   Max: €{secondary_max:,}")
    print(f"   Probability of occurrence: {secondary_probability*100:.0f}%\n")
    
    # =================================================================
    # RUN SIMULATION
    # =================================================================
    print(f"🔄 Running Monte Carlo simulation with 10,000 iterations...\n")
    
    sim = FAIRMonteCarloSimulation(n_simulations=10000)
    
    stats = sim.run_simulation(
        tef_dist=tef,
        vuln_prob=total_vulnerability,
        primary_loss_dist=primary_loss,
        secondary_loss_dist=secondary_loss,
        secondary_loss_prob=secondary_probability
    )
    
    # =================================================================
    # DISPLAY AND SAVE RESULTS
    # =================================================================
    sim.print_results(stats, currency="€")
    
    # Calculate as percentage of revenue
    ale_pct_revenue = (stats['ale_mean'] / ANNUAL_REVENUE) * 100
    ale_95_pct_revenue = (stats['percentiles']['95th'] / ANNUAL_REVENUE) * 100
    
    print(f"📊 BUSINESS CONTEXT")
    print(f"Annual Revenue: €{ANNUAL_REVENUE:,}")
    print(f"Mean ALE as % of revenue: {ale_pct_revenue:.2f}%")
    print(f"95th percentile as % of revenue: {ale_95_pct_revenue:.2f}%\n")
    
    # Risk appetite check
    if ale_pct_revenue > 1.0:
        print(f"⚠️  WARNING: Risk exceeds typical SMB risk appetite (>1% of revenue)")
        print(f"   → Recommend immediate risk treatment\n")
    elif ale_pct_revenue > 0.5:
        print(f"⚡ MODERATE RISK: Within acceptable range but warrants attention")
        print(f"   → Consider cost-effective controls\n")
    else:
        print(f"✅ ACCEPTABLE RISK: Below typical SMB risk appetite")
        print(f"   → May accept risk or implement low-cost controls\n")
    
    # Save outputs with client name
    safe_client_name = CLIENT_NAME.replace(" ", "_").lower()
    safe_scenario_name = RISK_SCENARIO_NAME.replace(" ", "_").lower()
    
    filename_base = f"{safe_client_name}_{safe_scenario_name}"

    try:
        sim.plot_results(
            stats,
            currency="€",
            save_path=f"{filename_base}_analysis.png"
        )
        print(f"✅ Plot saved: {filename_base}_analysis.png\n")
    except Exception as e:
        print(f"⚠️ Could not save plot: {e}\n")

    try:
        sim.export_results(
            stats,
            f"{CLIENT_NAME} - {RISK_SCENARIO_NAME}",
            f"{filename_base}_results.csv"
        )
        print(f"✅ Results exported\n")
    except Exception as e:
        print(f"⚠️ Could not export results: {e}\n")
    
    # =================================================================
    # RECOMMENDATIONS TEMPLATE
    # =================================================================
    print(f"\n{'='*70}")
    print(f"RECOMMENDATIONS FOR CLIENT")
    print(f"{'='*70}\n")
    
    print(f"Based on this analysis, here are potential risk treatment options:\n")
    
    print(f"1️⃣  AVOID THE RISK")
    print(f"   - Discontinue high-risk activities")
    print(f"   - Block certain attack vectors entirely")
    print(f"   - Estimated cost reduction: N/A\n")
    
    print(f"2️⃣  REDUCE THE RISK")
    print(f"   Option A: Email Security Gateway + User Training")
    print(f"   - Reduce vulnerability by an estimated 75% (to ~{total_vulnerability*0.25*100:.4f}%)")
    print(f"   - Estimated annual cost: €15,000-25,000")
    print(f"   - Estimated ALE reduction: ~75% (€{stats['ale_mean']*0.75:,.0f})")
    print(f"   - Net benefit: €{(stats['ale_mean']*0.75 - 20000):,.0f}/year")
    print(f"   - ROSI: {((stats['ale_mean']*0.75 - 20000)/20000)*100:.0f}%\n")
    
    print(f"   Option B: EDR/MDR + Enhanced Detection")
    print(f"   - Reduce loss magnitude by detecting breaches faster")
    print(f"   - Estimated annual cost: €30,000-50,000")
    print(f"   - Estimated ALE reduction: ~60% (€{stats['ale_mean']*0.60:,.0f})")
    print(f"   - Net benefit: €{(stats['ale_mean']*0.60 - 40000):,.0f}/year")
    print(f"   - ROSI: {((stats['ale_mean']*0.60 - 40000)/40000)*100:.0f}%\n")
    
    print(f"3️⃣  TRANSFER THE RISK")
    print(f"   - Cyber insurance coverage")
    print(f"   - Recommended coverage: €{stats['percentiles']['95th']:,.0f} (95th percentile)")
    print(f"   - Estimated premium: €{stats['percentiles']['95th']*0.03:,.0f}-{stats['percentiles']['95th']*0.05:,.0f}/year (3-5% of coverage)")
    print(f"   - Recommended deductible: €{stats['ale_median']:,.0f} (median ALE)\n")
    
    print(f"4️⃣  ACCEPT THE RISK")
    print(f"   - Acknowledge and monitor risk")
    print(f"   - Appropriate if ALE < 0.5% of revenue")
    print(f"   - Current: {ale_pct_revenue:.2f}% of revenue")
    print(f"   - Reserve fund recommendation: €{stats['percentiles']['90th']:,.0f} (90th percentile)\n")
    
    print(f"{'='*70}\n")
    
    # Create summary for client presentation
    print(f"📋 EXECUTIVE SUMMARY (for client deck):")
    print(f"""
The organization faces an estimated annual loss expectancy of €{stats['ale_mean']:,.0f} 
from {RISK_SCENARIO_NAME}. This represents {ale_pct_revenue:.2f}% of annual revenue.

There is a {stats['probability_of_loss']*100:.0f}% probability of experiencing at least 
one incident per year. In 5% of scenarios, annual losses could exceed €{stats['percentiles']['95th']:,.0f}.

Recommended actions: [Choose most appropriate treatment option(s) above]
Implementation timeline: [Define based on risk urgency]
Budget required: [Based on selected option(s)]
Expected risk reduction: [Based on selected option(s)]
""")
    
    print(f"\n✅ Analysis complete! Files saved:")
    print(f"   - {filename_base}_analysis.png")
    print(f"   - {filename_base}_results.csv")
    print(f"   - {filename_base}_results.json\n")


if __name__ == "__main__":
    run_custom_scenario()
