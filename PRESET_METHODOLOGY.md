# Preset Methodology (schema v2)

This document explains how the Contact Frequency (CF), Probability of
Action (PoA), and Vulnerability values in `presets.json` were derived for
the schema v2 fix (see `CHANGELOG.md`). It exists so a future maintainer
editing these values understands the reasoning rather than guessing, and so
users of the tool understand the limits of these numbers before relying on
them in a client engagement.

## The problem this solved

Earlier versions collected Threat Event Frequency (TEF) directly as a
min/mode/max distribution, then separately asked for a "Contact Frequency
(%)", "Probability of Action (%)", and "Vulnerability Rate (%)", and
multiplied all three together as `total_vulnerability`, which was then
multiplied again by TEF. This double-counted contact and action — TEF
already represents "attempts specifically against this org," which per the
Open Group O-RT Standard v3.0.1 §4.3.1 already equals `Contact Frequency ×
Probability of Action`. Re-applying a contact/action discount on top of an
already-complete TEF crushed the resulting Loss Event Frequency (LEF) to
artificially low values.

## Step 1: Recovering Contact Frequency without changing TEF

The old `tef_min`/`tef_mode`/`tef_max` values in each preset were reasonably
calibrated (they matched the worked examples throughout the docs and the
tool's own published demo output). To avoid discarding that calibration
work, Contact Frequency was **reverse-derived** so that `CF × PoA` exactly
reproduces the old TEF distribution:

```
CF_min  = old_tef_min  / PoA
CF_mode = old_tef_mode / PoA
CF_max  = old_tef_max  / PoA
```

using the old `vuln_action` value as PoA (it was already correctly defined
as "Probability of Action" in the original design — only its *application*
was wrong, not its definition). This was verified programmatically: for
every preset, `CF × PoA` reconstructs the original TEF min/mode/max to
within rounding.

## Step 2: Vulnerability could not simply be carried over

The obvious next step — reusing the old `vuln_rate` value as the new,
standalone Vulnerability — was tried and rejected. Because Vulnerability is
no longer discounted by contact/action a second time, reusing (e.g.)
Ransomware's old `vuln_rate = 0.35` directly would imply:

```
LEF_mean ≈ TEF_mean × 0.35 ≈ 383 × 0.35 ≈ 134 loss events/year
```

— i.e. over a hundred successful ransomware compromises per year for a
single SMB, which is not defensible. The old `vuln_rate` values were
evidently calibrated by the original author with the (mistaken)
expectation that two more multiplicative discounts would stack on top of
them; removing those discounts exposes that `vuln_rate` alone was too high
to serve as a standalone Vulnerability estimate.

## Step 3: Re-deriving Vulnerability against a plausible target

Vulnerability was instead solved for directly, by picking a **plausible
mean annual count of real loss events** for a mid-size EU SMB with baseline
security controls, and solving:

```
Vulnerability = target_LEF_mean / TEF_mean
```

where `TEF_mean = (TEF_min + 4×TEF_mode + TEF_max) / 6` (the standard PERT
mean).

| Scenario | Target LEF mean (events/yr) |
|---|---|
| Ransomware Attack | 0.5 |
| Data Breach (GDPR) | 0.3 |
| Business Email Compromise | 0.7 |
| DDoS Attack | 3.0 |
| Insider Threat | 0.2 |
| Zero-Day Exploit | 0.1 |
| Physical Theft of Device | 0.5 |
| Critical System Outage | 1.5 |
| Supply Chain Compromise | 0.1 |
| _default | 0.4 |

**These targets are reasoned, order-of-magnitude judgment calls — not
sourced statistics.** They were chosen to be plausible for a mid-size EU
SMB with baseline controls (e.g. "a meaningful chance of one successful
ransomware incident every ~2 years," not "a handful of confirmed
compromises every week"). They have not been validated against a specific
dataset (Verizon DBIR, ENISA, insurer claims data, etc.). Before using
these presets in an actual client engagement:

1. Replace the target LEF assumption with real data where you have it
   (client logs, insurer loss data, industry reports for their specific
   sector and size band).
2. Adjust Contact Frequency and Probability of Action independently if you
   have real contact-volume data (e.g. actual phishing simulation
   click-through rates), rather than relying on the reverse-derived CF
   values above.
3. Treat Vulnerability as the parameter most worth defending with a
   specific source (pen test results, MFA/EDR coverage data) — it's the
   single biggest lever on the final LEF/ALE numbers.

## Worked example: Ransomware Attack

| Value | Old (buggy) | New (schema v2) |
|---|---|---|
| TEF (min/mode/max) | 100 / 300 / 1,000 *(entered directly)* | 100.0 / 300.0 / 1,000.0 *(derived, numerically unchanged)* |
| Contact Frequency (min/mode/max) | n/a — was a % slider (25%) | 1,000 / 3,000 / 10,000 contacts/yr |
| Probability of Action | 0.10 (%, but re-multiplied into the vulnerability calc rather than used to derive TEF) | 0.10 |
| Vulnerability as applied (`vuln_prob` passed to the engine) | 0.00875 (`0.25 × 0.10 × 0.35`) | 0.0013 |
| Resulting LEF mean | ~3.3/yr | ~0.5/yr (target) |
| Resulting ALE mean | ~€388K | ~€58K |

Note the *old* LEF/ALE above are not the same as the numbers in this
project's published `ransomware_simulation_results.json` demo artifact
(~7.6/yr, ~€620K) — that artifact was generated by
`fair_monte_carlo.py`'s standalone `example_ransomware_scenario()`
function, which always used a single directly-specified
`vulnerability = 0.02` and was never affected by this bug. The table above
compares the dashboard preset's old (buggy) and new (fixed) behavior for
the same TEF calibration, not that unrelated example.

Both the old and new ALE numbers are internally consistent with their
respective (different) models — the point of this table is to show that
the *old* number was not "more correct" simply because it was previously
published; it was the output of a model that double-counted contact and
action.
