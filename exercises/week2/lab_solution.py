"""
Week 2 Hands-on Lab Solution: Dimensional Modeling & SCD Type 2
Reference solution for Week 2 exercises.
"""
import pandas as pd

def calculate_customer_rfm_ranks(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Customer RFM Ranks using aggregation and window ranking."""
    rfm = orders_df.groupby("customer_id").agg(
        frequency=("order_id", "count"),
        monetary=("total_amount", "sum"),
        recency_latest_date=("order_date", "max")
    ).reset_index()
    
    rfm["monetary_rank"] = rfm["monetary"].rank(ascending=False, method="dense").astype(int)
    return rfm

def apply_scd_type2_update(current_dim_df: pd.DataFrame, change_event: dict) -> pd.DataFrame:
    """Apply SCD Type 2 versioning for a dimension record."""
    cust_id = change_event["customer_id"]
    eff_date = change_event["effective_date"]
    new_city = change_event["city"]
    
    df = current_dim_df.copy()
    
    # Locate current active record
    mask = (df["customer_id"] == cust_id) & (df["is_current"] == 1)
    if mask.any():
        df.loc[mask, "is_current"] = 0
        df.loc[mask, "expiry_date"] = eff_date
        old_ver = df.loc[mask, "version"].values[0]
        old_sk = df.loc[mask, "customer_sk"].values[0]
        
        # New record
        new_row = df.loc[mask].iloc[0].to_dict()
        new_row["customer_sk"] = old_sk * 10 + old_ver + 1
        new_row["city"] = new_city
        new_row["effective_date"] = eff_date
        new_row["expiry_date"] = None
        new_row["is_current"] = 1
        new_row["version"] = old_ver + 1
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
    return df
