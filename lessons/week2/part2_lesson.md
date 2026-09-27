# Week 2 Part 2: Slowly Changing Dimensions (SCD), Surrogate Keys & Unknown Members

---

## 📌 Module Overview
This module explores advanced dimensional modeling techniques: managing historical attribute changes with **Slowly Changing Dimensions (SCD Types 1, 2, and 3)**, establishing robust **Surrogate Key** strategies while avoiding concurrency race conditions (`SELECT MAX(sk) + 1`), and handling **Unknown Members** and late-arriving dimensions.

---

## ⏳ 1. Slowly Changing Dimension (SCD) Design Patterns

In operational source systems, master data changes (e.g., a customer changes their residential city from Bengaluru to Mumbai). Data warehouses must decide whether to overwrite, track full history, or retain previous values.

```
                                  SCD PATTERN SELECTION
                                             |
         +-----------------------------------+-----------------------------------+
         |                                   |                                   |
         v                                   v                                   v
  +--------------+                    +--------------+                    +--------------+
  |  SCD TYPE 1  |                    |  SCD TYPE 2  |                    |  SCD TYPE 3  |
  |  (Overwrite) |                    |  (History)   |                    | (Add Column) |
  +--------------+                    +--------------+                    +--------------+
  No historical record               Full audit history                   Previous value
  saved. Corrects typos.             via version & dates.                 column maintained.
```

### 1. SCD Type 1: Overwrite (No History)
- **Mechanism**: Replaces old attribute directly in place (`UPDATE dim_customer SET city = 'Mumbai' WHERE customer_id = 801;`).
- **Use Case**: Correcting typos in names, emails, or phone numbers where history is irrelevant.
- **Pros**: Simple DDL; dimension row count remains constant.
- **Cons**: Erases past historical context for past orders.

### 2. SCD Type 2: Full Historical Tracking (Gold Standard)
- **Mechanism**: Inserts a new dimension row with a new surrogate key (`customer_sk`), sets the previous row's `expiry_date = current_date` and `is_current = 0`, and sets the new row's `is_current = 1` and `effective_date = current_date`.
- **Use Case**: Relocation, customer address changes, tier updates (Silver -> Gold loyalty tier) where past facts must preserve historical location context.

#### SCD Type 2 Dimension Table Schema:
```sql
CREATE TABLE dim_customer (
    customer_sk INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique Surrogate Key
    customer_id INTEGER NOT NULL,                  -- Natural Business Key
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    city TEXT NOT NULL,
    effective_date TEXT NOT NULL,                  -- Range start (YYYY-MM-DD)
    expiry_date TEXT,                              -- Range end (NULL if active)
    is_current INTEGER DEFAULT 1,                  -- Active flag (1 = Active, 0 = Expired)
    version INTEGER DEFAULT 1                      -- Sequential version counter
);
```

### 3. SCD Type 3: Previous Value Column
- **Mechanism**: Adds a dedicated column (e.g., `previous_city`, `previous_category`) to store the immediate prior state while overwriting the current state.
- **Use Case**: Comparing current vs prior product category classification.

---

## 🔑 2. Surrogate Key Strategies & The MAX+1 Concurrency Hazard

### Why Use Surrogate Keys?
A **Surrogate Key (`SK`)** is an artificial integer or hash key managed entirely by the data warehouse. It decouples the warehouse from operational natural business keys (`customer_id`) because:
1. Natural keys are re-used or updated in source DBs.
2. SCD Type 2 requires multiple dimension rows for a single `customer_id`.

```
                        SURREGATE KEY VS NATURAL KEY
                        
   customer_sk (Surrogate Key) | customer_id (Natural) | city      | is_current
   ----------------------------+-----------------------+-----------+-----------
   1001                        | CUST_802              | Bengaluru | 0
   1002                        | CUST_802              | Mumbai    | 1
```

### ⚠️ The `SELECT MAX(sk) + 1` Concurrency Hazard
In multi-threaded or distributed pipelines (Spark, Airflow parallel workers), computing surrogate keys via:

$$\text{Next SK} = \text{SELECT MAX(customer\_sk) + 1 FROM dim\_customer;}$$

causes a **Race Condition**. Two parallel threads execute `SELECT MAX` at the exact same instant, receive the same SK value, and fail with `PRIMARY KEY UNIQUE CONSTRAINT VIOLATION` or silently overwrite each other!

#### Safe Alternatives:
1. **Database `AUTOINCREMENT` / `IDENTITY`**: Native database engine sequence generator.
2. **Deterministic Hash Keys**: Generating MD5 or SHA-256 string hashes:
   $$\text{customer\_sk} = \text{SHA256}(\text{customer\_id} + \text{"\_"} + \text{effective\_date})$$

---

## ❓ 3. Unknown Members & Late-Arriving Dimensions

### Unknown Member Pattern (`sk = -1`)
During fact loading, an incoming order may reference a `customer_id` or `store_id` that does not yet exist in the dimension table due to ingestion lag.
- **Solution**: Never drop fact rows or insert `NULL` foreign keys. Instead, assign `customer_sk = -1`, referencing a default pre-populated **Unknown Member** row (`'Unknown Customer'`).

### Late-Arriving Dimensions
When dimension records arrive hours after the facts:
1. Fact rows initially pointing to `sk = -1` are updated once the dimension record arrives.
2. Or the dimension record is inserted with backdated `effective_date`.
