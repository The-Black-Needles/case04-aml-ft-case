from __future__ import annotations

import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, matthews_corrcoef, confusion_matrix
from xgboost import XGBClassifier

RANDOM_STATE = 42


def temporal_split(df: pd.DataFrame, validation_start_month: str = "2025-09") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split customer-month data temporally to avoid future leakage."""
    train = df[df["month"] < validation_start_month].copy()
    valid = df[df["month"] >= validation_start_month].copy()
    return train, valid


def get_feature_columns(df: pd.DataFrame, rule_cols: list[str]) -> tuple[list[str], list[str]]:
    """Return categorical and numeric feature columns, excluding label leakage."""
    id_cols = ["customer_id", "month", "full_name", "cpf_cnpj", "period_end", "date_of_birth", "registration_date", "geo_sender_id"]
    leakage_cols = ["suspicious_label", "rule_count"] + rule_cols
    exclude = set(id_cols + leakage_cols + ["sender_id", "merchant_id", "owner_customer_id"])
    candidates = [c for c in df.columns if c not in exclude]
    cat_cols = [c for c in candidates if df[c].dtype == "object" and c != "entity_type_model"]
    num_cols = [c for c in candidates if c not in cat_cols and not np.issubdtype(df[c].dtype, np.datetime64)]
    return cat_cols, num_cols


def fit_xgboost_pf(df: pd.DataFrame, rule_cols: list[str]) -> Pipeline:
    """Fit an XGBoost model for PF customer-month scoring."""
    pf = df[df["entity_type_model"].eq("PF")].copy()
    train, _ = temporal_split(pf)
    cat_cols, num_cols = get_feature_columns(pf, rule_cols)
    for col in cat_cols:
        train[col] = train[col].fillna("__MISSING__").astype(str)
    X_train = train[cat_cols + num_cols]
    y_train = train["suspicious_label"].astype(int)
    pos = int(y_train.sum())
    neg = int(len(y_train) - pos)
    scale_pos_weight = neg / max(pos, 1)
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=True), cat_cols),
            ("num", "passthrough", num_cols),
        ]
    )
    model = XGBClassifier(
        n_estimators=250,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=5,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=4,
        scale_pos_weight=scale_pos_weight,
    )
    pipe = Pipeline([("preprocess", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)
    return pipe
