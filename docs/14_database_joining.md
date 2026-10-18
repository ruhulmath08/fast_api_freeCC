# Database joining

1. [Overview](#1-overview)
2. [Simple database schema](#2-simple-database-schema)
3. [Types of JOINs](#3-types-of-joins)
4. [Comparison of JOIN types](#4-comparison-of-join-types)
5. [Common pitfalls](#5-common-pitfalls)

---

## 1. Overview

In a relational database, data is organized into tables consisting of rows and columns. Related information is often
distributed across multiple tables to reduce data duplication and maintain data integrity.

A **SQL JOIN** is an operation that combines rows from two or more tables based on a specified relationship or
condition. JOINs allow developers to retrieve related information without unnecessarily duplicating data across tables.

**Example:**

Consider an application that stores employee information and department information in separate tables. The `employees`
table stores employee details, while the `departments` table stores department details. Instead of storing the
department name repeatedly for every employee, the employee record can reference a department using its ID.

```sql
SELECT
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
INNER JOIN departments AS d
    ON e.department_id = d.department_id;
```

This query combines the two tables using their related `department_id` values.

---

## 2. Simple database schema

Throughout this document, the following tables will be used to demonstrate the different types of JOINs.

`**employees` table:\*\*

| employee_id | name  | department_id |
| ----------- | ----- | ------------- |
| 1           | Rahim | 101           |
| 2           | Karim | 102           |
| 3           | Sumon | 103           |
| 4           | Hasan | NULL          |

`**departments` table:\*\*

| department_id | name            |
| ------------- | --------------- |
| 101           | Engineering     |
| 102           | Human Resources |
| 104           | Finance         |

**Understanding the relationship between the tables:**

1. Rahim belongs to Engineering.
2. Karim belongs to Human Resources.
3. Sumon references department ID `103`, which does not exist in the `departments` table.
4. Hasan has no assigned department.
5. Finance exists as a department but has no matching employees.

These records allow us to examine how different JOIN types handle matching and non-matching rows.

> **Note:** This example assumes that `department_id` identifies a unique department. In a production database, it would
> normally be the primary key of `departments` and a foreign key in `employees`. The sample data illustrates unmatched
> references, which a properly enforced foreign key would ordinarily prevent.

---

## 3. Types of JOINs

There are several types of JOINs in SQL, each with its own purpose and behavior. The most common types are:

3.1. [INNER JOIN](#31-inner-join)
3.2. [LEFT JOIN (LEFT OUTER JOIN)](#32-left-join-left-outer-join)
3.3. [RIGHT JOIN (RIGHT OUTER JOIN)](#33-right-join-right-outer-join)
3.4. [FULL OUTER JOIN](#34-full-outer-join)
3.5. [CROSS JOIN](#35-cross-join)
3.6. [SELF JOIN](#36-self-join)

### 3.1 INNER JOIN

An `INNER JOIN` returns only rows that satisfy the JOIN condition in both tables. Rows without a matching record in the
other table are excluded.

**Syntax:**

```sql
SELECT columns
FROM table_a AS a
INNER JOIN table_b AS b
    ON a.common_column = b.common_column;
```

**Example:**

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
INNER JOIN departments AS d
    ON e.department_id = d.department_id;
```

**Result:**

| employee_id | employee_name | department_name |
| ----------- | ------------- | --------------- |
| 1           | Rahim         | Engineering     |
| 2           | Karim         | Human Resources |

**Explanation:**

- Only Rahim and Karim have a `department_id` that matches a record in the `departments` table.
- Sumon is excluded because `department_id` `103` has no matching department.
- Hasan is excluded because his `department_id` is `NULL`.
- Finance is also excluded because no employee references `department_id` `104`.

**Common use cases:**

- Retrieving orders with matching customers.
- Retrieving employees with valid department records.
- Retrieving products associated with existing categories.
- Retrieving transactions associated with valid accounts.

**Important considerations:**

`JOIN` and `INNER JOIN` are equivalent in standard SQL usage.

```sql
SELECT
    e.name,
    d.name AS department_name
FROM employees AS e
JOIN departments AS d
    ON e.department_id = d.department_id;
```

The query produces the same result as the `INNER JOIN` example.

---

### 3.2 LEFT JOIN (LEFT OUTER JOIN)

A `LEFT JOIN` returns all rows from the left table (`table_a`), along with matching rows from the right table
(`table_b`). If there is no match, the result contains `NULL` values for the right table columns.

**Syntax:**

```sql
SELECT columns
FROM table_a AS a
LEFT JOIN table_b AS b
    ON a.common_column = b.common_column;
```

**Example:**

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
LEFT JOIN departments AS d
    ON e.department_id = d.department_id;
```

**Result:**

| employee_id | employee_name | department_name |
| ----------- | ------------- | --------------- |
| 1           | Rahim         | Engineering     |
| 2           | Karim         | Human Resources |
| 3           | Sumon         | NULL            |
| 4           | Hasan         | NULL            |

**Explanation:**

All four employees appear in the result. For Sumon, no matching department exists. For Hasan, the `department_id` is
`NULL`. In both cases, the `department_name` returned by the query is `NULL`. Finance does not appear because the
`departments` table is on the right side of the JOIN, and unmatched right-hand rows are not retained.

**Common use cases:**

- Retrieving all customers, including those without orders.
- Identifying employees without matching department records.
- Listing all products, including those without sales.
- Identifying records that are missing related information.

**Practical example:**

Find employees without a matching department:

```sql
SELECT
    e.employee_id,
    e.name
FROM employees AS e
LEFT JOIN departments AS d
    ON e.department_id = d.department_id
WHERE d.department_id IS NULL;
```

This query identifies employees who have no matching department record. In the sample data, it returns Sumon and Hasan.

> **Important:** Checking a right-hand column that is guaranteed to be non-`NULL` for real matching rows is a common way
> to identify unmatched records.

---

### 3.3 RIGHT JOIN (RIGHT OUTER JOIN)

A `RIGHT JOIN` returns all rows from the right table (`table_b`), along with matching rows from the left table
(`table_a`). If there is no match, the result contains `NULL` values for the left table columns.

**Syntax:**

```sql
SELECT columns
FROM table_a AS a
RIGHT JOIN table_b AS b
    ON a.common_column = b.common_column;
```

**Example:**

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
RIGHT JOIN departments AS d
    ON e.department_id = d.department_id;
```

**Result:**

| employee_id | employee_name | department_name |
| ----------- | ------------- | --------------- |
| 1           | Rahim         | Engineering     |
| 2           | Karim         | Human Resources |
| NULL        | NULL          | Finance         |

**Explanation:**

All departments appear in the result. `Engineering` and `Human Resources` have matching employees. `Finance` does not,
so its employee columns contain `NULL`.

**Common use cases:**

- Listing all departments, including those without employees.
- Retrieving all categories, including those without products.
- Preserving every record from a table placed on the right side of a `JOIN`.

**Engineering recommendation:**

`RIGHT JOIN` is valid SQL, but many engineering teams prefer `LEFT JOIN` for consistency and readability. The same
result can be obtained by reversing the table order:

```sql
SELECT
    d.department_id,
    d.name AS department_name,
    e.employee_id,
    e.name AS employee_name
FROM departments AS d
LEFT JOIN employees AS e
    ON e.department_id = d.department_id;
```

Choosing one consistent style across a codebase makes queries easier to review and maintain.

---

### 3.4. FULL OUTER JOIN

A `FULL OUTER JOIN` returns all rows from both tables (`table_a` and `table_b`). If there is no match, the result
contains `NULL` values for the missing columns.

**Syntax:**

```sql
SELECT columns
FROM table_a AS a
FULL OUTER JOIN table_b AS b
    ON a.common_column = b.common_column;
```

**Example:**

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    d.department_id,
    d.name AS department_name
FROM employees AS e
FULL OUTER JOIN departments AS d
    ON e.department_id = d.department_id;
```

**Result:**

| employee_id | employee_name | department_id | department_name |
| ----------- | ------------- | ------------- | --------------- |
| 1           | Rahim         | 101           | Engineering     |
| 2           | Karim         | 102           | Human Resources |
| 3           | Sumon         | NULL          | NULL            |
| 4           | Hasan         | NULL          | NULL            |
| NULL        | NULL          | 104           | Finance         |

**Explanation:**

The result includes every employee and every department. Matching employees and departments are combined into single
rows. Employees without matching departments and departments without matching employees are also retained.

For Sumon and Hasan, `department_id` and `department_name` are `NULL` because the query selects those columns from
`departments` (`d.department_id`, `d.name`). Sumon's unmatched value `103` still exists on the employee row
(`e.department_id`), but it is not shown in this result set.

**Common use cases:**

- Comparing records between two datasets.
- Reconciling imported data with existing database records.
- Identifying missing relationships on either side.
- Performing data migration validation.

**Database compatibility:**

`FULL OUTER JOIN` is supported by PostgreSQL and several other database systems, but MySQL does not support it
directly.

When using a database that does not support `FULL OUTER JOIN`, an equivalent result can be constructed using two
`LEFT JOIN` queries combined with `UNION ALL`, plus an anti-match condition so unmatched right-hand rows are not
duplicated.

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    d.department_id,
    d.name AS department_name
FROM employees AS e
LEFT JOIN departments AS d
    ON e.department_id = d.department_id

UNION ALL

SELECT
    e.employee_id,
    e.name AS employee_name,
    d.department_id,
    d.name AS department_name
FROM departments AS d
LEFT JOIN employees AS e
    ON e.department_id = d.department_id
WHERE e.employee_id IS NULL;
```

The first query keeps every employee and any matching department. The second query adds departments that have no
matching employee (Finance in the sample data). Test the exact implementation against the target database and its
`NULL`-handling behavior.

---

### 3.5. CROSS JOIN

A `CROSS JOIN` returns the Cartesian product of two tables. Every row from the first table is combined with every row
from the second table. Unlike the previous JOIN types, a `CROSS JOIN` does not require an `ON` condition.

**Syntax:**

```sql
SELECT columns
FROM table_a AS a
CROSS JOIN table_b AS b;
```

**Example:**

Assume the following tables.

`**products` table:\*\*

| product_id | name    |
| ---------- | ------- |
| 1          | T-Shirt |
| 2          | Hoodie  |

`**sizes` table:\*\*

| size_id | name |
| ------- | ---- |
| 1       | S    |
| 2       | M    |
| 3       | L    |

**Query:**

```sql
SELECT
    p.name AS product_name,
    s.name AS size
FROM products AS p
CROSS JOIN sizes AS s;
```

**Result:**

| product_name | size |
| ------------ | ---- |
| T-Shirt      | S    |
| T-Shirt      | M    |
| T-Shirt      | L    |
| Hoodie       | S    |
| Hoodie       | M    |
| Hoodie       | L    |

**Explanation:**

Two products and three sizes produce six combinations:

> Number of rows in the first table × Number of rows in the second table = 2 × 3 = 6

**Common use cases:**

- Generating product and size combinations.
- Creating combinations of configuration options.
- Generating date and category combinations.
- Producing test data for specific scenarios.

**Performance consideration:**

`CROSS JOIN` can generate a very large result set. If one table contains 10,000 rows and another contains 5,000 rows,
their Cartesian product contains 50 million rows. Use `CROSS JOIN` intentionally and consider its potential memory,
processing, and network costs.

---

### 3.6. SELF JOIN

A `SELF JOIN` joins a table to itself. It is useful when records in the same table are related to one another.

`SELF JOIN` is not a separate JOIN operator in SQL. It is a technique that uses an ordinary JOIN, such as `INNER JOIN`
or `LEFT JOIN`, with two aliases referring to the same table.

**Example scenario:**

An employee may report to another employee who acts as their manager. Instead of creating a separate managers table, the
`employees` table can store a `manager_id` referencing another employee's `employee_id`.

> **Note:** The sample table below is a separate schema used only for the SELF JOIN example. It is not the same
> `employees` table defined in [section 2](#2-simple-database-schema).

`**employees` table (manager hierarchy sample):\*\*

| employee_id | name  | manager_id |
| ----------- | ----- | ---------- |
| 1           | Rahim | NULL       |
| 2           | Karim | 1          |
| 3           | Sumon | 1          |
| 4           | Hasan | 2          |

**Query:**

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    m.name AS manager_name
FROM employees AS e
LEFT JOIN employees AS m
    ON e.manager_id = m.employee_id;
```

**Result:**

| employee_id | employee_name | manager_name |
| ----------- | ------------- | ------------ |
| 1           | Rahim         | NULL         |
| 2           | Karim         | Rahim        |
| 3           | Sumon         | Rahim        |
| 4           | Hasan         | Karim        |

**Explanation:**

The `employees` table is referenced twice:

- `e` represents the employee.
- `m` represents the manager.

The JOIN matches each employee's `manager_id` to another employee's `employee_id`. Rahim has no manager, so his manager
name is `NULL`. Karim and Sumon report to Rahim, while Hasan reports to Karim.

**Common use cases:**

- Employee-manager relationships.
- Organizational hierarchies.
- Parent-child relationships.
- Comparing records within the same table.
- Finding related records based on shared attributes.

---

## 4. Comparison of JOIN types

| No. | JOIN type       | Matching rows                         | Unmatched left rows                   | Unmatched right rows                  |
| --- | --------------- | ------------------------------------- | ------------------------------------- | ------------------------------------- |
| 1   | INNER JOIN      | Included                              | Excluded                              | Excluded                              |
| 2   | LEFT JOIN       | Included                              | Included                              | Excluded                              |
| 3   | RIGHT JOIN      | Included                              | Excluded                              | Included                              |
| 4   | FULL OUTER JOIN | Included                              | Included                              | Included                              |
| 5   | CROSS JOIN      | Produces all combinations             | Not applicable                        | Not applicable                        |
| 6   | SELF JOIN       | Depends on the selected JOIN operator | Depends on the selected JOIN operator | Depends on the selected JOIN operator |

---

## 5. Common pitfalls

### Filtering OUTER JOIN results in `WHERE`

Putting a condition on the right-hand table in `WHERE` can turn a `LEFT JOIN` into the equivalent of an `INNER JOIN`,
because unmatched rows have `NULL` on the right side and are filtered out.

**Unintended (unmatched left rows disappear):**

```sql
SELECT
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
LEFT JOIN departments AS d
    ON e.department_id = d.department_id
WHERE d.name = 'Engineering';
```

**Preferred when unmatched left rows must be preserved:**

```sql
SELECT
    e.name AS employee_name,
    d.name AS department_name
FROM employees AS e
LEFT JOIN departments AS d
    ON e.department_id = d.department_id
    AND d.name = 'Engineering';
```

Keep match-preserving filters in the `ON` clause when you still need unmatched left-hand rows, or filter only on
left-hand columns in `WHERE`.

### Join-key indexing

Equality JOINs on foreign keys usually benefit from indexes on the join columns (for example,
`employees.department_id` and `departments.department_id`). Missing indexes can make large JOINs expensive even when the
JOIN type is correct.

### Joining more than two tables

Multiple JOINs are evaluated step by step. Write and verify each JOIN condition independently, and confirm which table
is preserved when mixing `INNER JOIN` and `LEFT JOIN`.

## Resources

Here is the useful link for the database resources:

1. [https://neon.com/postgresql/tutorial](https://neon.com/postgresql/tutorial)

---
