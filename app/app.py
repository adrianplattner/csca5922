"""Flask application for Craigslist price prediction."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, List

import pandas as pd
from flask import Flask, jsonify, render_template, request


def _load_artifacts() -> dict:
    """Load the persisted random forest model and preprocessing metadata."""
    artifact_path = Path(__file__).resolve().parent.parent / "models" / "random_forest_regressor.pkl"
    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {artifact_path}. "
            "Run the training/persistence step before starting the web app."
        )

    with artifact_path.open("rb") as fh:
        artifacts = pickle.load(fh)

    # Normalize numpy integer types for downstream JSON serialization
    manufacturer_model_map: Dict[str, List[str]] = {
        manufacturer: sorted(models) for manufacturer, models in artifacts["manufacturer_model_map"].items()
    }
    year_options: Dict[str, Dict[str, List[int]]] = {}
    for (manufacturer, model), years in artifacts["model_year_map"].items():
        year_options.setdefault(manufacturer, {})[model] = [int(y) for y in years]

    categorical_options = {
        key: sorted(values) for key, values in artifacts["categorical_options"].items()
    }

    artifacts["manufacturer_model_map"] = manufacturer_model_map
    artifacts["year_options"] = year_options
    artifacts["categorical_options"] = categorical_options

    return artifacts


ARTIFACTS = _load_artifacts()
MODEL = ARTIFACTS["model"]
FEATURE_COLUMNS = ARTIFACTS["feature_columns"]
CATEGORICAL_COLUMNS = ARTIFACTS["categorical_columns"]
MANUFACTURER_MODEL_MAP = ARTIFACTS["manufacturer_model_map"]
YEAR_OPTIONS = ARTIFACTS["year_options"]
CATEGORICAL_OPTIONS = ARTIFACTS["categorical_options"]
PRICE_BOUNDS = ARTIFACTS["price_bounds"]


def _preprocess_payload(payload: dict) -> pd.DataFrame:
    """Transform a single prediction payload into the design matrix expected by the model."""
    try:
        manufacturer = payload["manufacturer"]
        model = payload["model"]
        fuel = payload["fuel"]
        year = int(payload["year"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid payload; ensure manufacturer, model, fuel, and year are provided.") from exc

    if manufacturer not in MANUFACTURER_MODEL_MAP:
        raise ValueError(f"Unknown manufacturer '{manufacturer}'.")
    if model not in MANUFACTURER_MODEL_MAP[manufacturer]:
        raise ValueError(f"Model '{model}' is not available for manufacturer '{manufacturer}'.")
    if fuel not in CATEGORICAL_OPTIONS["fuel"]:
        raise ValueError(f"Unknown fuel type '{fuel}'.")
    if model not in YEAR_OPTIONS.get(manufacturer, {}) or year not in YEAR_OPTIONS[manufacturer][model]:
        raise ValueError(f"Year '{year}' is not available for {manufacturer} {model}.")

    row = pd.DataFrame(
        [
            {
                "year": year,
                "model": model,
                "manufacturer": manufacturer,
                "fuel": fuel,
            }
        ]
    )
    row = pd.get_dummies(row, columns=CATEGORICAL_COLUMNS, drop_first=True, dtype="int64")
    row = row.reindex(columns=FEATURE_COLUMNS, fill_value=0)
    return row


def create_app() -> Flask:
    """Application factory for the price prediction web app."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        manufacturer_list = sorted(MANUFACTURER_MODEL_MAP.keys())
        return render_template(
            "index.html",
            manufacturer_options=manufacturer_list,
            manufacturer_model_map=MANUFACTURER_MODEL_MAP,
            year_options=YEAR_OPTIONS,
            fuel_options=CATEGORICAL_OPTIONS["fuel"],
            price_bounds=PRICE_BOUNDS,
        )

    @app.route("/api/models/<manufacturer>")
    def get_models(manufacturer: str):
        models = MANUFACTURER_MODEL_MAP.get(manufacturer)
        if models is None:
            return jsonify({"error": f"Manufacturer '{manufacturer}' not found."}), 404
        return jsonify({"models": models})

    @app.route("/api/years/<manufacturer>/<model>")
    def get_years(manufacturer: str, model: str):
        years = YEAR_OPTIONS.get(manufacturer, {}).get(model)
        if years is None:
            return jsonify({"error": f"No year data for {manufacturer} {model}."}), 404
        return jsonify({"years": years})

    @app.route("/api/predict", methods=["POST"])
    def predict():
        try:
            payload = request.get_json(force=True)
            features = _preprocess_payload(payload)
            prediction = float(MODEL.predict(features)[0])
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # pragma: no cover - defensive
            return jsonify({"error": f"Unexpected error: {exc}"}), 500

        return jsonify(
            {
                "predicted_price": round(prediction, 2),
                "currency": "USD",
            }
        )

    return app


app = create_app()
