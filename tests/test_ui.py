import sys
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_streamlit_app():
    print("Starting Selenium UI Test (Edge Headless)...")

    # Edge options (CI safe)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # ✅ LOCAL DRIVER PATH (IMPORTANT)
    EDGE_DRIVER_PATH = "C:\\edgedriver\\msedgedriver.exe"

    try:
        service = Service(EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
    except Exception as e:
        print(f"Error initializing Edge Driver: {e}")
        sys.exit(1)

    try:
        driver.set_page_load_timeout(30)

        print("Opening Streamlit app...")
        driver.get("http://localhost:8501")

        print("Waiting for page to load...")
        wait = WebDriverWait(driver, 30)

        title_element = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        title_text = title_element.text
        print(f"Page Title: {title_text}")

        # Assertions
        if "Mumbai Housing Price Predictor" not in title_text:
            raise Exception("Main title not found")

        if "Fuzzy Logic" not in driver.page_source:
            raise Exception("Fuzzy Logic text not found")

        print("UI Test Passed Successfully")

    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)

    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    test_streamlit_app()