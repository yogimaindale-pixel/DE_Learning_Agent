# Week 2 Part 2: Slowly Changing Dimensions (SCD) & Surrogate Keys

## Objectives
- Master Slowly Changing Dimension patterns: SCD Type 1, Type 2, and Type 3.
- Evaluate surrogate key strategies and demonstrate `MAX+1` concurrency hazards.
- Handle late-arriving dimensions and unknown members (`customer_sk = -1`).
- Capstone: Lenskart prescription analytics star schema design.

## 1. Slowly Changing Dimensions (SCD)

| SCD Pattern | Mechanism | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Type 1** | Overwrite existing attribute | Simple, zero extra storage | Loss of historical state |
| **Type 2** | Expire old version (`is_current=0`), insert new version (`is_current=1`) | Preserves full history | Table growth, requires surrogate keys |
| **Type 3** | Add `previous_column` | Tracks recent 1 change | Cannot track 3+ changes |

---

## 2. Surrogate Keys & Concurrency Risk

### Why `MAX(sk) + 1` fails under concurrency
In multi-threaded pipelines, Thread A and Thread B execute `SELECT MAX(sk) + 1` simultaneously. Both receive the value `100` and attempt to insert key `101`, causing primary key collision exceptions.

### Safe Alternatives
- Database `AUTOINCREMENT` / `IDENTITY` columns.
- Deterministic Hash Surrogate Keys: `SHA256(business_key + effective_date)`.
- `dim_date` Integer Key convention: `YYYYMMDD` (e.g. `20240601`).

---

## 3. Lenskart Prescription Analytics Star Schema
Lenskart tracks customer prescriptions (`sphere_left`, `sphere_right`, `lens_type`). By modeling prescription parameters as a dedicated dimension (`dim_prescription`), order item facts can analyze lens sales trends by vision correction strength.
