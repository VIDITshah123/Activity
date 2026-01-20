from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_snapdeal_products(keyword: str):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    url = f"https://www.snapdeal.com/search?keyword={keyword.replace(' ', '%20')}"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    cards = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.product-tuple-description")
        )
    )[:4]
    products = []
    for card in cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, "p.product-title").text
        except:
            name = "N/A"
        try:
            price = card.find_element(By.CSS_SELECTOR, "span.product-price").text
        except:
            price = "N/A"
        try:
            rating = card.find_element(By.CSS_SELECTOR, "span.avrg-rating").text
        except:
            rating = "Not Available"
        try:
            delivery = card.find_element(By.CSS_SELECTOR, "span.delivery-time").text
        except:
            delivery = "Not Available"
        products.append({
            "name": name,
            "price": price,
            "rating": rating,
            "delivery": delivery
        })
    driver.quit()
    return products
