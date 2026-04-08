pipeline {
    agent any

    environment {
        STREAMLIT_URL = "http://localhost:8501"
        PYTHON = "C:\\Users\\mayan\\AppData\\Local\\Programs\\Python\\Python310\\python.exe"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📦 Checking out project source code...'
                checkout scm
            }
        }

        stage('Verify Python') {
            steps {
                echo '🔍 Verifying Python setup...'
                bat "\"%PYTHON%\" --version"
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '🛠️ Installing dependencies...'
                bat "\"%PYTHON%\" -m pip install --upgrade pip"
                bat "\"%PYTHON%\" -m pip install -r requirements.txt"
            }
        }

        stage('Start Streamlit App') {
            steps {
                echo '🚀 Starting Streamlit app...'

                // Start app in background (stable Windows way)
                bat """
                start "" /B "%PYTHON%" -m streamlit run app_ann.py --server.port 8501 --server.headless true
                """

                // Wait until app is live
                echo '⏳ Waiting for app to be ready...'
                timeout(time: 30, unit: 'SECONDS')
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                bat "\"%PYTHON%\" tests/test_ui.py"
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up processes...'

            // Kill all streamlit/python processes safely
            bat """
            taskkill /F /IM python.exe /T >nul 2>&1
            """
        }

        success {
            echo '🎉 All tests passed!'
        }

        failure {
            echo '🚨 Pipeline failed. Check logs.'
        }
    }
}