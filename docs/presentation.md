---
title: "University of Colorado Boulder"
subtitle: "CSCA5622 · Predicting Car Prices"
author: "Adrian Gomez"
theme: simple
---

# Predicting Car Prices

### CSCA5622 · University of Colorado Boulder

**Author:** Adrian Gomez\n\n**Contact:** Adrian.Gomez-1@colorado.edu

---

# What Problem Do We Solve?

- Used-car prices fluctuate across regions, seasons, and listing sites, making it hard to know a fair value.
- Buyers risk overpaying for a vehicle, while sellers risk leaving money on the table.
- A predictive model provides a market-grounded reference price, helping both parties negotiate confidently.
- Accurate price estimates streamline buy/sell decisions and reduce the time spent searching listings.

---

# Modeling Pipeline

- Filter listings to top 50 models, valid price range (USD $1k–$40k), and complete records for year/manufacturer/model/fuel.
- Features: vehicle year (numeric) plus manufacturer, model, and fuel encoded via one-hot vectors.
- 70/30 train–test split; evaluate with RMSE and R^2 to balance error magnitude and explained variance.
- Persist pre-processing metadata (feature order, allowed categories) alongside the model for reproducibility.

---

# Algorithms Evaluated

- **Linear Regression** baseline to gauge linear signal strength.
- **Ridge Regression (RidgeCV)** with cross-validated $\alpha$ to stabilize coefficients.
- **AdaBoost Regressor** to capture boosted tree interactions.
- **Random Forest Regressor** (300 estimators, tuned splits) delivered the most stable test RMSE/R^2 and powers the app.

---

# Application Method

- Flask service loads the persisted random forest bundle and preprocessing metadata.
- Dependent dropdowns enforce valid manufacturer → model → year combinations from the training data.
- Incoming requests are one-hot encoded using the saved feature layout before inference.
- Endpoint returns price predictions in real time, keeping results consistent with the trained pipeline.

---

# Model Performance


| Model | Train RMSE (USD) | Test RMSE (USD) | Test R^2 |
| --- | --- | --- | --- |
| Linear Regression | 6,369 | 6,346 | 0.59 |
| RidgeCV | 6,369 | 6,346 | 0.59 |
| AdaBoost Regressor | 7,521 | 7,498 | 0.43 |
| Random Forest Regressor | **4,144** | **4,232** | **0.82** |

- Random forest improves test RMSE by ~33% compared to the linear family models.
- Ridge regression mirrors the baseline, confirming modest linear signal without strong regularization gains.
- Tree ensembles without tuning (AdaBoost) underperform, while random forest generalizes best and powers the app.
