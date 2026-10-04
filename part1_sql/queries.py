import csv
import sqlite3
from pathlib import Path


# Find paths relative to this file, so the script works from any terminal folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "meesho_reseller.db"
OUTPUT_DIR = PROJECT_ROOT / "part1_sql" / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def save_query(connection, filename, sql):
    """Run one SQL query and save its column names and rows to a CSV."""
    cursor = connection.execute(sql)

    column_names = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    output_path = OUTPUT_DIR / filename

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(rows)

    print(f"{filename}: {len(rows)} data row(s)")
    return rows


def main():
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}. Run data/generate_dataset.py first."
        )

    with sqlite3.connect(DB_PATH) as connection:

        # 1. Monthly revenue and number of orders for each category.
        monthly_rows = save_query(
            connection,
            "monthly_category_revenue.csv",
            """
            SELECT
                month,
                category,
                ROUND(SUM(quantity * unit_price), 2) AS revenue,
                COUNT(*) AS n_orders
            FROM orders
            GROUP BY month, category
            ORDER BY
                CASE month
                    WHEN 'April' THEN 1
                    WHEN 'May' THEN 2
                    WHEN 'June' THEN 3
                END,
                CASE category
                    WHEN 'Ethnic Wear' THEN 1
                    WHEN 'Western Wear' THEN 2
                    WHEN 'Kids Wear' THEN 3
                    WHEN 'Home & Kitchen' THEN 4
                    WHEN 'Beauty & Personal Care' THEN 5
                END
            """,
        )

        # 2. Revenue and order count by reseller region.
        region_rows = save_query(
            connection,
            "region_revenue.csv",
            """
            SELECT
                r.region,
                ROUND(SUM(o.quantity * o.unit_price), 2) AS revenue,
                COUNT(*) AS n_orders
            FROM orders AS o
            JOIN resellers AS r
                ON o.reseller_id = r.reseller_id
            GROUP BY r.region
            ORDER BY revenue DESC
            """,
        )

        # 3. Five highest-spend resellers above INR 50,000.
        top_rows = save_query(
            connection,
            "top_resellers.csv",
            """
            SELECT
                r.reseller_id,
                r.reseller_name,
                r.region,
                ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
            FROM resellers AS r
            JOIN orders AS o
                ON r.reseller_id = o.reseller_id
            GROUP BY r.reseller_id, r.reseller_name, r.region
            HAVING SUM(o.quantity * o.unit_price) > 50000
            ORDER BY total_spend DESC
            LIMIT 5
            """,
        )

        # 4a. Start with ALL resellers, then find those with no matching orders.
        never_ordered_rows = save_query(
            connection,
            "never_ordered_resellers.csv",
            """
            SELECT
                r.reseller_id,
                r.reseller_name,
                r.region
            FROM resellers AS r
            LEFT JOIN orders AS o
                ON r.reseller_id = o.reseller_id
            WHERE o.order_id IS NULL
            ORDER BY r.reseller_id
            """,
        )

        # 4b. Demonstrate why COUNT(*) cannot detect a zero-match LEFT JOIN.
        count_demo_rows = save_query(
            connection,
            "zero_order_count_demo.csv",
            """
            SELECT
                r.reseller_id,
                COUNT(*) AS count_star,
                COUNT(o.order_id) AS count_order_id
            FROM resellers AS r
            LEFT JOIN orders AS o
                ON r.reseller_id = o.reseller_id
            WHERE r.reseller_id = 'RS024'
            GROUP BY r.reseller_id
            """,
        )

        # 5. Average order value: June orders with Delivered status ONLY.
        aov_rows = save_query(
            connection,
            "june_delivered_aov.csv",
            """
            SELECT
                ROUND(
                    SUM(quantity * unit_price) / COUNT(*),
                    2
                ) AS aov
            FROM orders
            WHERE month = 'June'
              AND status = 'Delivered'
            """,
        )

        # An extra check: all 900 orders should total INR 1,262,066.92.
        grand_total = connection.execute(
            "SELECT ROUND(SUM(quantity * unit_price), 2) FROM orders"
        ).fetchone()[0]

    print(f"Grand total revenue: INR {grand_total}")
    print(f"Monthly rows: {len(monthly_rows)}")
    print(f"Region rows: {len(region_rows)}")
    print(f"Top reseller rows: {len(top_rows)}")
    print(f"Never-ordered reseller rows: {len(never_ordered_rows)}")
    print(f"RS024 count demonstration: {count_demo_rows}")
    print(f"June Delivered AOV: INR {aov_rows[0][0]}")


if __name__ == "__main__":
    main()
