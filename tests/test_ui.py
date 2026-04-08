import time
import sys
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_streamlit_app():
    print("Starting Selenium UI Test (Edge Headless)...")
    
    # Setup Edge Options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize Driver
    try:
        driver = webdriver.Edge(options=options)
    except Exception as e:
        print(f"Error initializing Edge Driver: {e}")
        sys.exit(1)
    
    try:
        # 1. Open Streamlit App
        print("Navigating to http://localhost:8501...")
        driver.get("http://localhost:8501")
        
        # 2. Wait for title
        print("Waiting for title to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # 3. Verify content
        title_text = driver.find_element(By.TAG_NAME, "h1").text
        print(f"Found Page Title: {title_text}")
        
        assert "Mumbai Housing Price Predictor" in title_text
        print("Success: Main title is correct.")
        
        assert "Fuzzy Logic" in driver.page_source
        print("Success: 'Fuzzy Logic' detected in UI.")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    test_streamlit_app()