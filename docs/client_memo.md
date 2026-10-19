# Client memo: why subscribers switch operators, and where to focus first

**To:** Head of Customer Retention
**From:** Pranali Sawant, data analyst
**Date:** October 2026
**Basis:** TRAI monthly portability data (June 2025 to August 2026) and about 12,000 public Play Store reviews of the My Jio, Airtel Thanks, Vi and BSNL apps (2 August to 8 October 2026).

## The problem
About 15 million subscribers a month ask to port their number to another operator, and the volume is steady: 13.58 to 16.12 million over 15 months, averaging about 15.1 million. The question is what customers are unhappy about, and where retention effort should go first.

## What we found
1. **App sentiment splits into two groups.** Average ratings are 2.44 for Airtel and 2.24 for BSNL, against 4.02 for Jio and 4.25 for Vi. 62.8% (Airtel) and 67.5% (BSNL) of reviews give 1 or 2 stars, against 20.8% (Jio) and 14.8% (Vi).
2. **The main complaint differs by operator.** Network quality is the largest theme for Airtel (about 38% of its complaints), Jio (about 49%) and Vi (about 37%). For BSNL it is app problems (about 67%).
3. **Switching is persistent, not spiking.** Monthly portability requests stayed within a narrow band. The low was June 2025 and the high was December 2025 (16.12 million); the latest month, August 2026, was 15.83 million.

## Recommendations (hypotheses to test, not conclusions)
1. **Airtel, Jio, Vi:** treat network experience as the first retention priority. Check the complaint themes against internal network-quality and customer-care data to find where the problems are concentrated.
2. **BSNL:** fix the app first. In the reviews read during labelling, recurring problems were login and OTP failures, plan and validity details not showing, and recharges charged but not reflected.
3. **Track two numbers every month:** the share of 1-2 star reviews, and the share of network complaints, and compare them with your own operator-level port-out data.

## How confident we are
- **The theme classifier is about 71% accurate** on 100 fresh labelled reviews (95% range 61% to 79%). The labels were assigned with AI assistance and spot-checked. Network and App themes are the most reliable; Customer Support is unreliable and is not used. App complaints are probably undercounted. Exact percentages move with the rules, but the ranking of the largest theme per operator held under both rule versions tested.
- **Reviews are a self-selected sample** of app users, in English only, and cover different periods per operator (Jio and Vi about 9 days, Airtel 24, BSNL 68), so compare shares, not counts.
- **Portability requests are a proxy** for switching, not total churn. The reviews and the TRAI data overlap only in August 2026, so this analysis cannot show that complaints explain switching.

## What I would check next
1. Label more reviews, especially Customer Support, and re-test on a third fresh sample.
2. Collect reviews monthly so they overlap the TRAI series for longer.
3. Add operator-wise subscriber movement from TRAI and compare it with each operator's complaint themes.
4. Validate the themes against internal ticket data.
