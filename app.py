import os
import logging

import numpy as np
import pandas as pd
import joblib
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

BASE_YEAR = 2023

HISTORY_SQL = """
SELECT
    CAST(d.year AS INT)  AS year,
    CAST(d.month AS INT) AS month,
    p.category,
    CAST(SUM(f.quantity) AS INT) AS total_quantity,
    SUM(f.quantity) FILTER (WHERE f.promo_id IS NOT NULL)::float
        / NULLIF(SUM(f.quantity), 0)     AS promo_share,
    SUM(f.discount_amount)::float
        / NULLIF(SUM(f.gross_amount), 0) AS discount_rate
FROM gold.fact_sales f
JOIN gold.dim_date     d ON f.date_key   = d.date_key
JOIN gold.dim_products p ON f.product_id = p.product_id
WHERE f.source_system = 'batch'
GROUP BY d.year, d.month, p.category
ORDER BY p.category, d.year, d.month;
"""

model = None
feature_cols = None
engine = None
hist = None

HISTORY_CSV = os.path.join("data", "history.csv")


def load_model():
    global model, feature_cols
    model_path = os.path.join("models", "xgboost_demand_forecast.pkl")
    if not os.path.exists(model_path):
        model_path = os.path.join("notebooks", "xgboost_demand_forecast.pkl")
    features_path = os.path.join("models", "feature_columns.pkl")
    if not os.path.exists(features_path):
        features_path = os.path.join("notebooks", "feature_columns.pkl")

    model = joblib.load(model_path)
    feature_cols = list(joblib.load(features_path))
    logger.info(f"Model loaded from {model_path} ({len(feature_cols)} features)")


def load_history():
    global engine, hist

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        load_dotenv(dotenv_path=os.path.join("src", ".env"))
        db_url = os.getenv("DATABASE_URL")

    df = None
    if db_url:
        try:
            if engine is None:
                engine = create_engine(db_url)
            df = pd.read_sql(HISTORY_SQL, engine)
            logger.info(f"History loaded from database: {df.shape[0]} rows")
        except Exception as e:
            logger.warning(f"Database unavailable ({e}); falling back to {HISTORY_CSV}")

    if df is None:
        df = pd.read_csv(HISTORY_CSV)
        logger.info(f"History loaded from snapshot: {df.shape[0]} rows")

    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str))
    df = df.sort_values(["category", "date"]).reset_index(drop=True)
    df[["promo_share", "discount_rate"]] = df[["promo_share", "discount_rate"]].fillna(0)
    hist = df
    logger.info(f"History ready: {df.shape[0]} rows, {df['category'].nunique()} categories")


try:
    load_model()
except Exception as e:
    logger.error(f"Could not load model: {e}")

try:
    load_history()
except Exception as e:
    logger.error(f"Could not load history: {e}")


def categories():
    if hist is None:
        return []
    return sorted(hist["category"].unique().tolist())


def forecast_category(category, horizon):
    s = hist[hist["category"] == category].sort_values("date")
    if s.empty:
        return []

    qty = list(s["total_quantity"].astype(float).values)
    last_date = s["date"].max()
    cal = (s.assign(m=s["date"].dt.month)
             .groupby("m")[["promo_share", "discount_rate"]].last())

    out = []
    for h in range(1, horizon + 1):
        nd = last_date + pd.DateOffset(months=h)
        m = nd.month
        feat = {
            "month": m,
            "lag_1": qty[-1], "lag_2": qty[-2], "lag_3": qty[-3],
            "lag_12": qty[-12] if len(qty) >= 12 else float(np.mean(qty)),
            "rolling_3": float(np.mean(qty[-3:])), "rolling_6": float(np.mean(qty[-6:])),
            "month_sin": float(np.sin(2 * np.pi * m / 12)),
            "month_cos": float(np.cos(2 * np.pi * m / 12)),
            "time_index": (nd.year - BASE_YEAR) * 12 + (m - 1),
            "promo_share": float(cal["promo_share"].get(m, 0.0)),
            "discount_rate": float(cal["discount_rate"].get(m, 0.0)),
        }
        row = {c: 0 for c in feature_cols}
        for k, v in feat.items():
            if k in row:
                row[k] = v
        cd = f"category_{category}"
        if cd in row:
            row[cd] = 1

        pred = float(model.predict(pd.DataFrame([row])[feature_cols])[0])
        qty.append(pred)
        out.append({"date": nd.strftime("%Y-%m-%d"), "category": category,
                    "forecast": round(max(pred, 0.0), 1)})
    return out


def recent_actuals(category, n=6):
    s = hist[hist["category"] == category].sort_values("date").tail(n)
    return [{"date": d.strftime("%Y-%m-%d"), "actual": int(q)}
            for d, q in zip(s["date"], s["total_quantity"])]


@app.route("/")
def index():
    return render_template("index.html", categories=categories())


@app.route("/predict", methods=["POST"])
def predict():
    if model is None or hist is None:
        return jsonify({"error": "Model or history not loaded"}), 503
    try:
        data = request.get_json(silent=True) or {}
        category = data.get("category")
        if category not in categories():
            return jsonify({"error": f"Unknown category: {category}"}), 400
        horizon = max(1, min(int(data.get("horizon", 6)), 12))

        return jsonify({
            "category": category,
            "horizon": horizon,
            "recent_actuals": recent_actuals(category),
            "forecasts": forecast_category(category, horizon),
        })
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/model_info", methods=["GET"])
def model_info():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 404
    importances = sorted(
        zip(feature_cols, [float(x) for x in model.feature_importances_]),
        key=lambda kv: kv[1], reverse=True,
    )[:10]
    return jsonify({
        "model_type": type(model).__name__,
        "features_count": len(feature_cols),
        "top_features": [{"feature": f, "importance": round(v, 4)} for f, v in importances],
        "categories": categories(),
        "model_loaded": True,
        "status": "ready",
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "history_loaded": hist is not None,
    })


@app.route("/refresh", methods=["GET"])
def refresh():
    try:
        load_history()
        return jsonify({"status": "refreshed", "rows": int(hist.shape[0])})
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)