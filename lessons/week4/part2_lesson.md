# Week 4 Part 2: Automated Data Quality, PII Privacy Vaults, DPDP/GDPR Compliance & Query Profiling

---

## 📌 Module Overview
This module covers advanced enterprise architecture controls: automated **Data Quality as Code** (Great Expectations / Soda Core), building a **PII Vault Architecture for DPDP Act & GDPR Compliance**, executing **SQL Query Profiling (`EXPLAIN QUERY PLAN`)**, and applying lakehouse performance optimizations (**Partitioning, Z-Ordering, Materialized Summaries**).

---

## 🛡️ 1. Automated Data Quality Gates

Data quality validation must occur automatically before publishing data to Gold analytical layers.

```
+------------------+      +-----------------------+      +-----------------------+
| Silver Dataset   | ---> | Automated Quality Gate| ---> | Gold Published Layer  |
| (Cleansed Rows)  |      | (Great Expectations)  |      | (Analytical Views)    |
+------------------+      +-----------------------+      +-----------------------+
                                      |
                                      v (Validation Failure)
                          +-----------------------+
                          | Halt Gold Publish &   |
                          | Alert Data Team       |
                          +-----------------------+
```

### Core Declarative Quality Assertions
- `expect_column_values_to_not_be_null(column="customer_id")`
- `expect_column_values_to_be_unique(column="customer_sk")`
- `expect_column_values_to_be_between(column="net_amount", min_value=0)`
- `expect_table_row_count_to_be_between(min_value=1)`

---

## 🔒 2. PII Privacy Vault Pattern & Compliance (DPDP Act / GDPR)

Under data protection laws (**Digital Personal Data Protection Act - DPDP India**, **GDPR Europe**), enterprises must protect Personal Identifiable Information (PII) like names, email addresses, phone numbers, and government IDs.

```
                           PII MASKING VAULT PATTERN
                           
   BRONZE LAYER (Restricted Access)
   [customer_id: 801] [email: rahul.varma@domain.com] [phone: +919876543210]
                                     |
                                     v
   SILVER LAYER (Masked & Tokenized)
   [customer_token: SHA256(801)] [email: ra***@domain.com] [phone: +91XXXXXX3210]
                                     |
                                     v
   GOLD LAYER (100% Free of Direct PII)
   [state: 'MH'] [total_orders: 14] [gross_revenue: 28400.00]
```

### Anonymization & Pseudonymization Techniques
1. **Masking**: Replacing sensitive string characters (`rahul@domain.com` $\rightarrow$ `ra***@domain.com`).
2. **Deterministic Salted Tokenization**: Hashing natural keys using SHA-256 with a secret pepper salt:
   $$\text{token} = \text{SHA256}(\text{customer\_id} + \text{"\_"} + \text{SECRET\_PEPPER})$$
3. **Column Encryption**: Encrypting sensitive columns at rest using AES-256 symmetric keys.

---

## ⚡ 3. SQL Query Profiling & Performance Tuning

### Profiling Queries with `EXPLAIN QUERY PLAN`
Before deploying analytical SQL queries to production, inspect execution cost and index usage using `EXPLAIN QUERY PLAN`.

```sql
EXPLAIN QUERY PLAN
SELECT f.order_id, c.first_name, f.net_amount
FROM fact_order_item f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
WHERE c.state = 'KA';
```

#### Understanding Output Diagnostics:
- ❌ **`SCAN TABLE fact_order_item`**: Indicates a Full Table Scan (slow, high I/O cost).
- ✅ **`SEARCH TABLE dim_customer USING COVERING INDEX idx_cust_state`**: Indicates efficient B-Tree Index lookup.

### Lakehouse Performance Optimizations
1. **Partitioning**: Grouping data on disk into directory sub-folders based on high-cardinality date or region keys (`/year=2026/month=09/`).
2. **Z-Ordering**: Multi-dimensional clustering algorithm that co-locating related data across multiple columns in Parquet files.
3. **Materialized Summary Views**: Pre-computing and persisting heavy aggregations (e.g., daily sales per store) to serve BI dashboards instantly.
