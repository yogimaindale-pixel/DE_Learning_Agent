"""
Week 2 Hands-on Lab Starter: Dimensional Modeling & SCD Type 2
Instructions: Fill in the TODO sections to implement Star Schema joins and SCD Type 2 history updates.
"""

def calculate_customer_rfm_ranks(orders_df):
    """
    TODO 1: Calculate Customer Recency, Frequency, and Monetary (RFM) ranks using window functions.
    Expects columns: customer_id, order_date, total_amount
    """
    # TODO: Calculate Frequency (COUNT of orders) and Monetary (SUM of total_amount) per customer.
    # TODO: Rank customers by Monetary value using ROW_NUMBER() or rank() in pandas.
    pass

def apply_scd_type2_update(current_dim_df, change_event):
    """
    TODO 2: Given a customer address change event, expire the current record and create a new version.
    """
    # TODO: Expire current row (is_current=0, expiry_date=change_event['effective_date'])
    # TODO: Append new row (is_current=1, version=old_version+1, effective_date=change_event['effective_date'])
    pass
