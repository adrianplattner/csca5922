# Craigslist Cars & Trucks Price Prediction Plan

## 1. Objectives
- Predict vehicle listing `price` using available structured features.
- Identify the most influential attributes that drive price variation.
- Build a reproducible pipeline that supports feature engineering, model training, and evaluation.

## 2. Data Understanding
- **Source**: `vehicles.csv` from the Kaggle Craigslist Cars & Trucks dataset.
- **Target Variable**: `price` (numeric).
- **Candidate Features**: `year`, `manufacturer`, `model`, `condition`, `cylinders`, `fuel`, `odometer`, `title_status`, `transmission`, `drive`, `size`, `type`, `paint_color`, `state`, `region`, `lat`, `long`, `posting_date`, `description` text, and derived attributes.
- **Initial Checks**:
  - Load with `pandas`, inspect dtypes, unique counts, and missingness.
  - Verify duplicates by `id`/`url`/`vin`; decide deduplication strategy.
  - Assess outliers in `price`, `year`, `odometer`, and geolocation.

## 3. Data Cleaning Strategy
1. **Missing Data**
   - Quantify missingness per column.
   - Impute numeric fields (`year`, `odometer`) using domain-aware methods (median imputation by manufacturer/type) or flag as "unknown" categories.
   - For categorical variables, create explicit `Unknown` category when imputation is inappropriate.
2. **Outliers & Validity Constraints**
   - Filter prices outside a reasonable band (e.g., `$500`–`$200,000`).
   - Clip `year` to plausible vehicle production years (e.g., `1990–2024`).
   - Remove entries with `odometer <= 0` or extreme values after log-transform diagnostics.
3. **Text Normalization**
   - Lowercase, remove punctuation, and optionally lemmatize `description` for NLP features.
4. **Temporal Handling**
   - Parse `posting_date` to datetime and extract components (`posting_year`, `posting_month`).

## 4. Feature Engineering
- **Numeric Features**:
  - Car age: `posting_year - year`.
  - Price per mile: `price / odometer` for diagnostics (not as feature to avoid leakage) and categorize into bins.
  - Odometer log-transform to reduce skew (`log1p`).
- **Categorical Encoding**:
  - Frequency encode high-cardinality fields (`model`, `region`).
  - One-hot encode manageable categories (`fuel`, `condition`, `drive`, `type`, `transmission`, `title_status`).
  - Group rare manufacturers/types into `Other` to avoid sparse columns.
- **Geospatial Features**:
  - Convert `lat/long` to state-level aggregates; optionally cluster coordinates (e.g., KMeans for region embeddings).
  - Incorporate external cost-of-living or regional price indices if available.
- **Text Features**:
  - TF-IDF vectors on `description` (limit to top `1–5k` n-grams) or extract keyword flags (e.g., `"salvage"`, `"like new"`).
- **Interaction Terms**:
  - Combine `manufacturer` × `type`, `drive` × `fuel`, and age × condition to capture heterogeneous effects.

## 5. Modeling Approach
1. **Baseline Models**
   - Linear Regression / Lasso (with standardized numeric features and encoded categories).
   - Random Forest Regressor for non-linear benchmark.
2. **Gradient Boosted Trees**
   - XGBoost or LightGBM with hyperparameter tuning via cross-validation.
3. **Regularization & Feature Selection**
   - Use L1 (Lasso) for sparsity in high-dimensional design matrices.
   - Evaluate permutation importance for tree-based models to highlight key drivers.
4. **Text Integration Options**
   - Build separate pipelines with and without TF-IDF to gauge incremental benefit.
   - Consider dimension reduction (SVD) on TF-IDF to limit feature explosion.

## 6. Evaluation Strategy
- Split data into train/validation/test (e.g., 70/15/15) with stratification on `state` or price deciles to maintain distribution.
- Primary metrics: Root Mean Squared Error (RMSE) and Mean Absolute Error (MAE).
- Secondary checks: R², error distribution across price buckets, calibration plots.
- Perform k-fold cross-validation (e.g., 5-fold) for robust generalization estimates.
- Track experiment results in a structured format (e.g., MLflow, spreadsheet).

## 7. Model Diagnostics & Interpretability
- Analyze feature importances, partial dependence plots, and SHAP values for top models.
- Slice performance by key categories (manufacturer, state, vehicle type) to detect bias or underperformance.
- Inspect residuals vs. predictions to detect heteroscedasticity or systematic errors.

## 8. Deployment Considerations
- Package preprocessing and model steps into a `scikit-learn` `Pipeline` for reproducibility.
- Serialize best model (e.g., `joblib`) and document inference requirements.
- Provide data schema expectations and preprocessing steps for future scoring.

## 9. Next Steps
1. Acquire dataset locally and run initial profiling notebook (e.g., `pandas-profiling`, `ydata-profiling`).
2. Implement data cleaning scripts/notebooks following the outlined strategy.
3. Train and evaluate baseline models; iterate with feature enhancements.
4. Summarize findings and model performance in a report or dashboard.

