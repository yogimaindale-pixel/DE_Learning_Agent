# Week 2 Part 1: Dimensional Modeling & Analytics SQL

## Objectives
- Master Star vs Snowflake schemas, Fact tables, and Dimension granularity.
- Implement Fact Table Types: Transaction, Periodic Snapshot, Accumulating Snapshot.
- Identify and resolve join anti-patterns (double counting / fan-out).
- Master advanced SQL window functions: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `NTILE`, and running `SUM OVER`.
- Case studies: Puma India, BigBasket, Nykaa, Amazon India.

## 1. Dimensional Modeling Basics

### Grain First
Always define the business grain before creating tables:
- `fact_order_item`: One row per item per order.
- `fact_daily_sales_snapshot`: One row per store per calendar day.
- `fact_delivery_lifecycle`: One row per delivery order tracking milestone timestamps.

### Fact Table Types
1. **Transaction Fact**: Captures discrete atomic events (e.g. order item purchased).
2. **Periodic Snapshot Fact**: Summarizes periodic status (e.g. daily inventory or daily store sales).
3. **Accumulating Snapshot Fact**: Tracks milestones in a workflow lifecycle (e.g. Order Placed -> Assigned -> Picked -> Delivered).

---

## 2. Advanced Window Functions

```sql
-- Top product per category using ROW_NUMBER
WITH RankedProducts AS (
    SELECT 
        category,
        product_name,
        SUM(net_amount) as total_sales,
        ROW_NUMBER() OVER(PARTITION BY category ORDER BY SUM(net_amount) DESC) as rnk
    FROM fact_order_item f
    JOIN dim_product p ON f.product_sk = p.product_sk
    GROUP BY category, product_name
)
SELECT * FROM RankedProducts WHERE rnk = 1;
```
