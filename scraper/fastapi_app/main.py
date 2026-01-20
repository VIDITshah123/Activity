from fastapi import FastAPI, HTTPException
from datetime import datetime
import traceback
import concurrent.futures
from db import get_db
from utils import sanitize_table_name, is_expired
from scraper import scrape_snapdeal_products

app = FastAPI(title="Snapdeal Scraper API")
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

@app.post("/api/search")
def search(keyword: str):
    db = None
    cur = None
    try:
        table = sanitize_table_name(keyword)
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT last_scraped_at FROM scrape_metadata WHERE table_name=%s",
            (table,)
        )
        meta = cur.fetchone()
        if meta and not is_expired(meta["last_scraped_at"]):
            cur.execute(f"SELECT * FROM `{table}`")
            data = cur.fetchall()
            return {"source": "database", "products": data}
        if meta:
            cur.execute(f"DROP TABLE IF EXISTS `{table}`")
            cur.execute(
                "DELETE FROM scrape_metadata WHERE table_name=%s",
                (table,)
            )
            db.commit()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS `{table}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(255),
                price VARCHAR(50),
                rating VARCHAR(20),
                delivery_time VARCHAR(50),
                scraped_at DATETIME
            )
        """)
        future = executor.submit(scrape_snapdeal_products, keyword)
        products = future.result(timeout=60)
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        now = datetime.now()
        for p in products:
            cur.execute(f"""
                INSERT INTO `{table}`
                (product_name, price, rating, delivery_time, scraped_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                p["name"],
                p["price"],
                p["rating"],
                p["delivery"],
                now
            ))
        cur.execute("""
            INSERT INTO scrape_metadata (table_name, last_scraped_at)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE last_scraped_at = %s
        """, (table, now, now))

        db.commit()
        return {"source": "scraped", "products": products}
    except HTTPException:
        raise
    except Exception as e:
        print("========= FASTAPI ERROR =========")
        print(traceback.format_exc())
        print("================================")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if db:
            db.close()
