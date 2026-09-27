# Week 4 Part 2: Data Quality, Privacy, & Performance Optimization

## Objectives
- Automate Data Quality as Code checks.
- Implement the PII Vault pattern and DPDP Act / GDPR compliance principles.
- Profile queries using `EXPLAIN QUERY PLAN` and optimize indexes.
- Materialize performance summary views.

## 1. PII Vault Pattern & Privacy Compliance

To comply with India's DPDP Act and GDPR:
1. **Bronze Raw**: Restricted access; contains raw payload with audit trails.
2. **Silver Cleaned**: Direct PII (`email`, `phone`) masked or tokenized (`c***i@example.com`, `******3210`); SHA-256 hash stored for identity resolution.
3. **Gold Curated**: Aggregated financial metrics completely free of direct individual PII.

---

## 2. Query Optimization & Indexes

Using `EXPLAIN QUERY PLAN` in SQLite:
- **Unindexed Scan**: `SCAN TABLE silver_orders` (Reads O(N) rows).
- **Indexed Search**: `SEARCH TABLE silver_orders USING INDEX idx_silver_orders_cust (customer_id=?)` (O(log N) lookup).
