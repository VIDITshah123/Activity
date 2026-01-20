import re
from datetime import datetime, timedelta

def sanitize_table_name(keyword: str) -> str:
    keyword = keyword.lower()
    keyword = re.sub(r"[^a-z0-9 ]", "", keyword).strip()
    if not keyword:
        keyword = "default"
    return keyword.replace(" ", "_") + "_products"
def is_expired(last_scraped):
    if not last_scraped:
        return True
    return datetime.now() - last_scraped >= timedelta(hours=24)