from __future__ import annotations

import numpy as np
import pandas as pd

RANDOM_STATE = 42


def build_customer_month_dataset(
    transactions: pd.DataFrame,
    kyc_profiles: pd.DataFrame,
    merchants: pd.DataFrame,
    geo_behavior: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Build customer-month AML features and weak labels.

    Weak label rule: suspicious_label = 1 when at least three AML rules fire
    in the same customer-month.

    Missing values are preserved as informative whenever possible. Numeric
    values are not blindly imputed; tree boosting can handle missing numeric
    values. Categorical missing values should be explicitly encoded later as
    __MISSING__ by the modeling pipeline.
    """
    tx = transactions.copy()
    kyc = kyc_profiles.copy()
    merchants = merchants.copy()
    geo = geo_behavior.copy()

    tx["timestamp"] = pd.to_datetime(tx["timestamp"], errors="coerce")
    tx["month"] = tx["timestamp"].dt.to_period("M").astype(str)
    tx = tx.merge(
        merchants[["merchant_id", "mcc_risk", "merchant_high_risk_flag", "merchant_chargeback_ratio_90d", "owner_customer_id"]],
        left_on="receiver_id",
        right_on="merchant_id",
        how="left",
    )

    out = tx[tx["sender_id"].astype(str).str.startswith("C")].copy()
    out["customer_id"] = out["sender_id"]
    out["direction"] = "out"
    out["counterparty_id"] = out["receiver_id"]
    out["signed_amount"] = -out["amount_brl"]

    inc = tx[tx["receiver_id"].astype(str).str.startswith("C")].copy()
    inc["customer_id"] = inc["receiver_id"]
    inc["direction"] = "in"
    inc["counterparty_id"] = inc["sender_id"]
    inc["signed_amount"] = inc["amount_brl"]

    p = pd.concat([out, inc], ignore_index=True)

    flags = {
        "is_sent": p["direction"].eq("out"),
        "is_received": p["direction"].eq("in"),
        "is_pix": p["transaction_type"].eq("PIX"),
        "is_card": p["transaction_type"].eq("Card"),
        "is_wire": p["transaction_type"].eq("Wire"),
        "is_cash_out": p["direction"].eq("out") & p["pix_flow"].eq("cash_out"),
        "is_cash_in": p["direction"].eq("in") & p["pix_flow"].eq("cash_in"),
        "is_cross_border": p["cross_border"].eq("Yes"),
        "is_high_risk_receiver_country": p["country_risk_receiver"].eq("High"),
        "is_high_risk_any_country": p[["country_risk_geo", "country_risk_ip", "country_risk_sender", "country_risk_receiver"]].eq("High").any(axis=1),
        "is_sanctions_tx": p["sanctions_screening_hit"].eq("Yes"),
        "is_high_value_50k": p["amount_brl"].ge(50000),
        "is_ecom_no_3ds": p["transaction_type"].eq("Card") & p["capture_method"].eq("E-commerce") & p["auth_3ds"].eq("No"),
        "is_mcc_high_risk": p["mcc_risk"].eq("High"),
        "is_merchant_high_risk": p["merchant_high_risk_flag"].eq("Yes"),
        "is_ip_anomaly": p["ip_anomaly"].eq("Yes"),
        "is_device_rooted": p["device_rooted"].eq("Yes"),
        "is_round_100": (p["amount_brl"] >= 1000) & (np.isclose(p["amount_brl"] % 100, 0, atol=0.01)),
        "is_round_1000": (p["amount_brl"] >= 1000) & (np.isclose(p["amount_brl"] % 1000, 0, atol=0.01)),
    }
    for name, cond in flags.items():
        p[name] = cond.fillna(False).astype(int)

    d = p.groupby(["customer_id", "month"]).agg(
        tx_count=("transaction_id", "count"),
        total_amount=("amount_brl", "sum"),
        avg_amount=("amount_brl", "mean"),
        median_amount=("amount_brl", "median"),
        std_amount=("amount_brl", "std"),
        max_amount=("amount_brl", "max"),
        net_flow=("signed_amount", "sum"),
        sent_count=("is_sent", "sum"),
        received_count=("is_received", "sum"),
        pix_count=("is_pix", "sum"),
        card_count=("is_card", "sum"),
        wire_count=("is_wire", "sum"),
        cash_out_count=("is_cash_out", "sum"),
        cash_in_count=("is_cash_in", "sum"),
        cross_border_count=("is_cross_border", "sum"),
        high_risk_receiver_country_count=("is_high_risk_receiver_country", "sum"),
        high_risk_any_country_count=("is_high_risk_any_country", "sum"),
        sanctions_tx_count=("is_sanctions_tx", "sum"),
        high_value_50k_count=("is_high_value_50k", "sum"),
        ecom_no_3ds_count=("is_ecom_no_3ds", "sum"),
        mcc_high_risk_count=("is_mcc_high_risk", "sum"),
        merchant_high_risk_count=("is_merchant_high_risk", "sum"),
        ip_anomaly_count=("is_ip_anomaly", "sum"),
        device_rooted_count=("is_device_rooted", "sum"),
        round_100_count=("is_round_100", "sum"),
        round_1000_count=("is_round_1000", "sum"),
        unique_counterparties=("counterparty_id", "nunique"),
    ).reset_index()

    idx = d.set_index(["customer_id", "month"]).index
    d["cash_in_total"] = p[p["is_cash_in"].eq(1)].groupby(["customer_id", "month"])["amount_brl"].sum().reindex(idx).fillna(0).values
    d["cash_out_total"] = p[p["is_cash_out"].eq(1)].groupby(["customer_id", "month"])["amount_brl"].sum().reindex(idx).fillna(0).values
    d["pass_through_ratio"] = np.where(d["total_amount"] > 0, np.abs(d["net_flow"]) / d["total_amount"], np.nan)
    d["pix_share"] = d["pix_count"] / d["tx_count"]
    d["card_share"] = d["card_count"] / d["tx_count"]
    d["wire_share"] = d["wire_count"] / d["tx_count"]
    d["cross_border_share"] = d["cross_border_count"] / d["tx_count"]
    d["mcc_high_risk_share"] = d["mcc_high_risk_count"] / d["tx_count"]
    d["merchant_high_risk_share"] = d["merchant_high_risk_count"] / d["tx_count"]
    d["device_rooted_share"] = d["device_rooted_count"] / d["tx_count"]

    d = d.merge(kyc, on="customer_id", how="left")
    d = d.merge(geo.add_prefix("geo_"), left_on="customer_id", right_on="geo_sender_id", how="left")

    d["period_end"] = pd.to_datetime(d["month"]) + pd.offsets.MonthEnd(0)
    d["date_of_birth"] = pd.to_datetime(d["date_of_birth"], errors="coerce")
    d["registration_date"] = pd.to_datetime(d["registration_date"], errors="coerce")
    d["age"] = ((d["period_end"] - d["date_of_birth"]).dt.days / 365.25).clip(lower=0)
    d["months_since_registration"] = ((d["period_end"] - d["registration_date"]).dt.days / 30.44).clip(lower=0)

    occ_med = d.groupby(["month", "declared_occupation"])["total_amount"].transform("median")
    occ_mean = d.groupby(["month", "declared_occupation"])["total_amount"].transform("mean")
    occ_std = d.groupby(["month", "declared_occupation"])["total_amount"].transform("std")
    d["occupation_month_median_total"] = occ_med
    d["ratio_to_occupation_median_total"] = d["total_amount"] / occ_med.replace(0, np.nan)
    d["zscore_vs_occupation_total"] = (d["total_amount"] - occ_mean) / occ_std.replace(0, np.nan)

    risk_factor = d["risk_rating"].map({"Low": 2.0, "Medium": 1.5, "High": 1.0}).fillna(2.0)
    out_profile_threshold = np.maximum(d["annual_income_brl"].fillna(0) * risk_factor, 20000)

    rules = {
        "r_out_of_profile": d["total_amount"].ge(out_profile_threshold) & d["tx_count"].ge(5),
        "r_pep_activity": d["pep"].eq("Yes") & d["total_amount"].ge(10000),
        "r_sanctions_customer": d["sanctions_list_hit"].eq("Yes"),
        "r_tx_sanctions": d["sanctions_tx_count"].gt(0),
        "r_high_risk_country": d["high_risk_any_country_count"].gt(0),
        "r_cross_border_high_risk": d["cross_border_count"].gt(0) & d["high_risk_any_country_count"].gt(0),
        "r_high_value_50k": d["high_value_50k_count"].gt(0),
        "r_ecom_no_3ds": d["ecom_no_3ds_count"].ge(2),
        "r_mcc_high_risk_concentration": d["mcc_high_risk_count"].ge(3) & d["mcc_high_risk_share"].ge(0.50),
        "r_merchant_high_risk_concentration": d["merchant_high_risk_count"].ge(3) & d["merchant_high_risk_share"].ge(0.40),
        "r_ip_anomaly": d["ip_anomaly_count"].gt(0),
        "r_device_rooted_recurrent": d["device_rooted_count"].ge(2),
        "r_round_values": d["round_100_count"].ge(10),
        "r_many_counterparties": d["unique_counterparties"].ge(25),
        "r_pass_through": d["cash_in_total"].gt(0) & d["cash_out_total"].gt(0) & d["pass_through_ratio"].le(0.20) & d["total_amount"].ge(20000),
        "r_velocity_pass_through": d["cash_out_count"].ge(60) & d["cash_in_count"].ge(9) & d["round_100_count"].ge(10),
        "r_geo_velocity": d["geo_tx_per_day"].ge(1.0),
        "r_high_risk_volume": d["risk_rating"].eq("High") & d["total_amount"].ge(50000),
    }
    rule_cols = []
    for name, cond in rules.items():
        d[name] = cond.fillna(False).astype(int)
        rule_cols.append(name)

    d["rule_count"] = d[rule_cols].sum(axis=1)
    d["suspicious_label"] = d["rule_count"].ge(3).astype(int)
    d["entity_type_model"] = np.where(d["cpf_cnpj"].astype(str).str.len().eq(14), "PJ", "PF")
    return d, rule_cols
