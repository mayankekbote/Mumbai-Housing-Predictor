import sys
import requests

def test_streamlit_app():
    print("Starting HTTP UI Test (no browser required)...")

    url = "http://localhost:8501"

    try:
        response = requests.get(url, timeout=15)

        print(f"HTTP Status Code: {response.status_code}")

        if response.status_code != 200:
            raise Exception(f"Expected 200, got {response.status_code}")

        page_content = response.text

        if "Mumbai Housing Price Predictor" not in page_content:
            raise Exception("Main title not found in page source")

        if "Fuzzy Logic" not in page_content:
            raise Exception("Fuzzy Logic text not found in page source")

        print("UI Test Passed Successfully")

    except requests.exceptions.ConnectionError:
        print("Test Failed: Could not connect to Streamlit app at localhost:8501")
        sys.exit(1)
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_streamlit_app()