# Task 4 — Insights and Recommendations (Mobile Banking App Reviews)

## 1. Executive Summary

This report analyzes customer reviews for mobile banking apps using **ratings**, **sentiment labels/scores**, and **themes** (`theme_primary`).
It identifies **drivers** of positive experience and **pain points** behind negative sentiment for each bank, compares banks, and proposes actionable improvements.

**Dataset size:** 1,786 reviews (PostgreSQL).


## 2. Cross-bank comparison (KPIs)

| bank_name   |   n_reviews |   avg_rating |   neg_share |   pos_share |
|:------------|------------:|-------------:|------------:|------------:|
| BOA         |         599 |      3.24207 |    0.562604 |    0.434057 |
| DASHEN      |         599 |      4.04841 |    0.323873 |    0.674457 |
| CBE         |         588 |      4.04252 |    0.35034  |    0.641156 |


## 3. Visualizations

- `figures/sentiment_by_bank.png` — Sentiment distribution by bank
- `figures/rating_distribution.png` — Rating distribution by bank
- `figures/negative_trend_monthly.png` — Monthly negative sentiment share
- `figures/top_negative_keywords_overall.png` — Top complaint keywords


## 4. Bank-level insights and recommendations


### BOA

#### Drivers (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind   |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-------|
| BOA         | OTHER           | 544 |           0.90818   |       3.375  |       0.466912 |       0.529412 | DRIVER |
| BOA         | STABILITY_BUGS  |  39 |           0.0651085 |       1.4359 |       0        |       1        | DRIVER |

Evidence snippets for **OTHER**:
- "This is the best app; many features are awesome, but it should work without the need to turn off the developer options. I'm tired of having to constantly switch the developer opti…"
- "Nice to meet you my proud bank in Ethiopia.. I'm a member of this bank, i need to solve my problem of international receiving money for me from my online digital working service's…"

Evidence snippets for **STABILITY_BUGS**:
- "This app is a joke. It crashes more than it works, takes forever to load, and half the features are just decorative at this point. Can’t log in, can’t transfer money, can’t even c…"
- "most of bank apps in Ethiopia are linked with ethiopian phone number, I live in US permanently so when I open BoA account, I told them where I live and to link it with email addre…"

#### Pain points (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind       |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-----------|
| BOA         | OTHER           | 544 |           0.90818   |       3.375  |       0.466912 |       0.529412 | PAIN_POINT |
| BOA         | STABILITY_BUGS  |  39 |           0.0651085 |       1.4359 |       0        |       1        | PAIN_POINT |

Evidence snippets for **OTHER**:
- "I will give only one star, because it faced with multiple of problems. 1. The app is not as fast as the other banks App, for e.g like CBE 2. The App asks repeatedly to switch off …"
- "Very unprofessional and mischievous bank in my opinion. I have had several occasions but recently I used Abyssinia Card to withdraw money and it was deducted from my account but d…"

Evidence snippets for **STABILITY_BUGS**:
- "This app is a joke. It crashes more than it works, takes forever to load, and half the features are just decorative at this point. Can’t log in, can’t transfer money, can’t even c…"
- "most of bank apps in Ethiopia are linked with ethiopian phone number, I live in US permanently so when I open BoA account, I told them where I live and to link it with email addre…"

#### Recommendations (2+)

1. Stability program: crash analytics, staged rollouts, automated regression testing, and rollback for faulty releases.
2. Add in-app support: FAQs + guided troubleshooting for login/transfer issues, with escalation (ticket/chat) when unresolved.

Additional keywords figure: `figures/top_negative_keywords_boa.png`

### CBE

#### Drivers (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind   |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-------|
| CBE         | OTHER           | 548 |           0.931973  |      4.11314 |       0.671533 |       0.319343 | DRIVER |
| CBE         | STABILITY_BUGS  |  16 |           0.0272109 |      2.25    |       0        |       1        | DRIVER |

Evidence snippets for **OTHER**:
- "The application is generally very good and reliable. It offers smooth operations and better functionality compared to many similar apps. However, after the recent update, the keyb…"
- "Hello guys. The frequently updating is very essential for mobile banking. But please learn many experiences from Dashen Mobile Banking Supper app how much safe, efficient and user…"

Evidence snippets for **STABILITY_BUGS**:
- "this is absolute trash why because it's not Woking most time the servers are down even though I'm using 4g data Internet they steal not working they use to work with out even data…"
- "since the application updated, i couldn't use the it properly . now it stucked and loading but not working I was even trying to contact thru online help/chat box on the app, but n…"

#### Pain points (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind       |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-----------|
| CBE         | OTHER           | 548 |           0.931973  |      4.11314 |       0.671533 |       0.319343 | PAIN_POINT |
| CBE         | STABILITY_BUGS  |  16 |           0.0272109 |      2.25    |       0        |       1        | PAIN_POINT |

Evidence snippets for **OTHER**:
- "To the Commercial Bank of Ethiopia (CBE), I am writing to express my concern regarding the recent update to the CBE Mobile Banking application. Since the update, the application h…"
- "Seriously, what’s going on with this app? The "Pay to Beneficiary" option is completely disabled for Android users, yet iOS users get full access without restrictions. Why are And…"

Evidence snippets for **STABILITY_BUGS**:
- "this is absolute trash why because it's not Woking most time the servers are down even though I'm using 4g data Internet they steal not working they use to work with out even data…"
- "since the application updated, i couldn't use the it properly . now it stucked and loading but not working I was even trying to contact thru online help/chat box on the app, but n…"

#### Recommendations (2+)

1. Stability program: crash analytics, staged rollouts, automated regression testing, and rollback for faulty releases.
2. Add in-app support: FAQs + guided troubleshooting for login/transfer issues, with escalation (ticket/chat) when unresolved.

Additional keywords figure: `figures/top_negative_keywords_cbe.png`

### DASHEN

#### Drivers (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind   |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-------|
| DASHEN      | OTHER           | 533 |            0.889816 |      4.09944 |       0.690432 |       0.307692 | DRIVER |
| DASHEN      | UX_UI           |  40 |            0.066778 |      4.525   |       0.85     |       0.15     | DRIVER |

Evidence snippets for **OTHER**:
- "Dashen Super App is a game-changer! It’s fast, user-friendly, and packed with features that make everyday banking and transactions super convenient. I love how everything I need f…"
- "The best of best is now arrived **Empowering Your Financial Freedom** "Experience seamless banking at your fingertips with Dashen Bank. Empowering your financial freedom, anytime,…"

Evidence snippets for **UX_UI**:
- "i can't recommend the Dashen Super App enough! This app is truly a game changer for anyone looking for a seamless and efficient way to manage their daily life. It combines multipl…"
- "The Dashen supperapp is a revolutionary advancement in digital banking, combining exceptional usability, an intuitive interface and a seamless user experience. among its standout …"

#### Pain points (2+)

| bank_name   | theme_primary   |   n |   share_within_bank |   avg_rating |   pct_positive |   pct_negative | kind       |
|:------------|:----------------|----:|--------------------:|-------------:|---------------:|---------------:|:-----------|
| DASHEN      | OTHER           | 533 |            0.889816 |      4.09944 |       0.690432 |       0.307692 | PAIN_POINT |
| DASHEN      | UX_UI           |  40 |            0.066778 |      4.525   |       0.85     |       0.15     | PAIN_POINT |

Evidence snippets for **OTHER**:
- "I am very disappointed with the Dashin Bank Super App. The app does not allow me to withdraw 50 birr or can't transfer money and even I can't use it to buy airtime. This makes me …"
- "This might be the worst banking app I've ever used I dont know why kind of bug it is but suddenly the apps stops working it says "Temporarily unavailable" for a simple feature lik…"

Evidence snippets for **UX_UI**:
- "would most likely rate it even less but it does have it's perks. But for the most part the whole app is filled with bugs and it stops being responsive almost everytime. Besides so…"
- "The UI/UX appears well-designed, but it has some critical issues that need attention, such as the inability to display full transaction histories and the presence of numerous mini…"

#### Recommendations (2+)

1. UX simplification: reduce steps for common actions, improve navigation labels, and add contextual help around failures.
2. Add in-app support: FAQs + guided troubleshooting for login/transfer issues, with escalation (ticket/chat) when unresolved.

Additional keywords figure: `figures/top_negative_keywords_dashen.png`


## 5. Ethics and limitations

- **Review selection bias:** Reviewers are self-selected; negative experiences are often overrepresented.
- **Event/release bias:** A single outage or app release can spike negative reviews temporarily.
- **Platform bias:** Store reviews may not represent all customers or device/network contexts.
- **Language + NLP limitations:** Mixed language, spelling variation, and short texts reduce sentiment/theme accuracy.
- **Attribution caution:** Themes reflect user perception and should be validated with operational logs.