import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json


def scrape_page(driver, url):
    driver.get(url)
    print(f"Scraping: {url}")

    wait = WebDriverWait(driver, 30)

    # Step 1: Wait for the container
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.flex-col.gap-4")))
    except TimeoutException:
        print(f"Timed out waiting for container on {url}")
        return []

    # Step 2: Wait specifically for titles to be visible before scraping
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.text-base.font-semibold.text-dark-gray")))
        print("Titles loaded!")
    except TimeoutException:
        print(f"Timed out waiting for titles on {url}")
        return []

    #  Step 3: Small extra delay just to be safe
    time.sleep(3)

    elements = driver.find_elements(By.CSS_SELECTOR, 'button[data-test^="spotlight-result-product"]')
    print(f"Found {len(elements)} products")

    results = []
    for el in elements:
        try:
            product_id = el.get_attribute("data-test").replace("spotlight-result-product-", "")

            #  Same selector as before — correct
            try:
                title = el.find_element(By.CSS_SELECTOR, "span.text-base.font-semibold.text-dark-gray").text.strip()
            except:
                title = "N/A"

            # Same selector as before — correct
            try:
                description = el.find_element(By.CSS_SELECTOR, "span.text-sm.font-normal.text-light-gray").text.strip()
            except:
                description = "N/A"

            #  Same selector as before — correct
            try:
                reviews = el.find_element(By.CSS_SELECTOR, "span.text-sm.font-semibold.text-brand-500").text.strip()
            except:
                reviews = "0 reviews"

            # Only save if title is not empty
            if title and title != "N/A":
                results.append({
                    "ID": product_id,
                    "Title": title,
                    "Description": description,
                    "Reviews": reviews
                })
            else:
                print(f"Skipping ID {product_id} — title not loaded yet")

        except Exception as e:
            print(f"Error: {e}")
            continue

    return results


def scrape_all_pages(base_url, total_pages=5):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    all_results = []

    try:
        for page in range(1, total_pages + 1):
            url = f"{base_url}&page={page}"
            page_results = scrape_page(driver, url)
            all_results.extend(page_results)
            print(f"Page {page} done — total so far: {len(all_results)} products")
            time.sleep(5)  # delay between pages

    finally:
        try:
            driver.quit()
        except:
            pass

    return all_results


if __name__ == "__main__":
    base_url = "https://www.producthunt.com/search?q=mental+health+ai"

    data = scrape_all_pages(base_url, total_pages=5)

    if data:
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nSaved {len(data)} products to results.json")
    else:
        print("No data scraped.")