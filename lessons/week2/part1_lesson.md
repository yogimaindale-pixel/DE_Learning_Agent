# Week 2 Part 1: Dimensional Modeling, Star Schemas, Join Strategies & Window Functions

---

## 📌 Module Overview
This module covers analytical data modeling using Ralph Kimball's **Star and Snowflake Schema** methodology, declaring fact grain, categorizing Fact Table types (Transaction, Periodic Snapshot, Accumulating Snapshot), mastering join strategies and anti-patterns, and executing advanced SQL aggregation and window functions.

---

## ⭐ 1. Star Schema vs Snowflake Schema Architecture

Modern data warehousing structures analytical models to separate **measurable numerical metrics (Facts)** from **descriptive contextual attributes (Dimensions)**.

```
                           STAR SCHEMA
                      +-------------------+
                      |   dim_customer    |
                      +-------------------+
                               |
+-----------------+   +-------------------+   +-----------------+
|    dim_store    |---|  fact_order_item  |---|   dim_product   |
+-----------------+   +-------------------+   +-----------------+
                               |
                      +-------------------+
                      |     dim_date      |
                      +-------------------+
```

### Key Differences Matrix

| Dimension | Star Schema | Snowflake Schema |
| :--- | :--- | :--- |
| **Normalization** | Denormalized (Dimensions are single flat tables) | Normalized (Dimensions broken into sub-dimension lookup tables) |
| **Join Complexity** | Simple 1-level joins (`Fact -> Dimension`) | Multi-level hierarchical joins (`Fact -> Dim -> Sub-Dim`) |
| **Query Performance** | **Fastest** (Fewer table joins) | Slower (Requires complex recursive joins) |
| **Storage Overhead** | Slightly higher redundant attribute storage | Minimum storage footprint |
| **Best Practice** | **Standard for Data Warehouses & Marts** | Niche cases with extreme dimension hierarchy depth |

---

## 📊 2. Declaring Grain & Fact Table Types

### Declaring the Grain (Rule #1 of Kimball Data Modeling)
Before writing any DDL or transformation logic, you must explicitly state what a single row in the fact table represents.
- **Example**: *"One row in `fact_order_item` represents a single line item purchased by a customer in a specific order at a specific store on a specific date."*

### The Three Core Fact Table Types

```
1. TRANSACTION FACT TABLE
   [Fact ID] [Order ID] [Customer SK] [Product SK] [Quantity] [Net Amount]
   Grain: 1 row per individual business transaction line.

2. PERIODIC SNAPSHOT FACT TABLE
   [Snapshot ID] [Date Key] [Store SK] [Total Orders] [Gross Sales] [AOV]
   Grain: 1 row per fixed time interval (e.g., end-of-day summary per store).

3. ACCUMULATING SNAPSHOT FACT TABLE
   [Delivery ID] [Order ID] [Placed TS] [Assigned TS] [Picked TS] [Delivered TS]
   Grain: 1 row per process lifecycle, updating timestamps as milestones occur.
```

---

## 🔗 3. SQL Join Strategies & Anti-Patterns

### Join Types Overview
- **INNER JOIN**: Returns rows only when keys match in both tables.
- **LEFT OUTER JOIN**: Returns all rows from left table, with matching right table rows (or NULLs).
- **FULL OUTER JOIN**: Returns all rows when there is a match in either table.
- **CROSS JOIN**: Produces Cartesian product ($M \times N$ rows).

### Dangerous Anti-Pattern: Fan-Out Double Counting
When joining a Fact table to an un-deduplicated Dimension table (1-to-Many instead of 1-to-1), fact metrics duplicate unexpectedly.

```sql
-- DANGEROUS: If dim_customer has 2 historical versions for customer_id 801,
-- joining on customer_id causes total_price to be SUMMED TWICE!
SELECT 
    f.order_id, 
    SUM(f.total_price) AS incorrect_revenue -- DOUBLE COUNTED!
FROM fact_order_item f
JOIN dim_customer c ON f.customer_id = c.customer_id; -- Wrong key! Should join on customer_sk!
```

---

## 🪟 4. Advanced Window Functions & Ranking Queries

Window functions perform calculations across a set of table rows related to the current row without collapsing rows into a single summary output.

```
+---------------------------------------------------------------------------------------+
| WINDOW FUNCTION SYNTAX                                                                |
| FUNCTION() OVER (PARTITION BY category ORDER BY spend DESC)                          |
+---------------------------------------------------------------------------------------+
```

### Core Analytical Window Functions
1. **`ROW_NUMBER()`**: Unique sequential integer assigned per row (1, 2, 3, 4).
2. **`RANK()`**: Rank with gaps for tied values (1, 2, 2, 4).
3. **`DENSE_RANK()`**: Rank without gaps for tied values (1, 2, 2, 3).
4. **`LAG(col, offset)`**: Accesses value from previous row in the partition (e.g., previous order date).
5. **`LEAD(col, offset)`**: Accesses value from upcoming row in the partition.
6. **`NTILE(n)`**: Divides rows into $N$ equal bucket quartiles/percentiles.
7. **`SUM(col) OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN ...)`**: Running total sum.

#### Practical SQL Example (Customer RFM Analysis):
```sql
SELECT 
    customer_id,
    city,
    total_spend,
    ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spend DESC) AS city_spend_row,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) AS overall_dense_rank,
    LAG(total_spend, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prior_order_spend
FROM customer_orders_summary;
```
