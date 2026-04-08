pipeline {
    agent any

    environment {
        // The URL of the local Streamlit application
        STREAMLIT_URL = "http://localhost:8501"
    }

    stages {
        stage('Checkout') {
            steps {
                // SCM checkout is handled automatically if this is a pipeline job from Git
                echo '📦 Checking out project source code...'
                checkout scm
            }
        }

        stage('Restore Dependencies') {
            steps {
                // Install required libraries from requirements.txt
                echo '🛠️ Installing Python dependencies...'
                powershell "python -m pip install -r requirements.txt"
            }
        }

        stage('Launch App') {
            steps {
                // Start Streamlit in a background job
                // Headless mode is forced to prevent UI popups on the Jenkins agent
                echo '🚀 Starting Streamlit application in background...'
                powershell """
                    \$jobName = "MumbaiHousingApp"
                    if (Get-Job -Name \$jobName -ErrorAction SilentlyContinue) { 
                        Stop-Job -Name \$jobName
                        Remove-Job -Name \$jobName 
                    }
                    
                    Start-Job -Name \$jobName -ScriptBlock { 
                        python -m streamlit run app_ann.py --server.port 8501 --server.headless true
                    }
                    
                    # Wait loop to ensure the app is ready before running tests
                    Write-Host "⏳ Waiting for app to respond at ${env.STREAMLIT_URL}..."
                    for (\$i=0; \$i -lt 30; \$i++) {
                        try {
                            \$response = Invoke-WebRequest -Uri "${env.STREAMLIT_URL}" -UseBasicParsing -ErrorAction Stop
                            if (\$response.StatusCode -eq 200) {
                                Write-Host "✅ Application is LIVE!"
                                return
                            }
                        } catch {
                            Start-Sleep -s 3
                        }
                    }
                    throw "❌ FAIL: Application did not start in time."
                """
            }
        }

        stage('Execute Selenium Tests') {
            steps {
                // Run the Selenium script with Microsoft Edge (Headless)
                echo '🧪 Running Automated UI Tests (Selenium + Edge)...'
                powershell "python tests/test_ui.py"
            }
        }
    }

    post {
        always {
            // Cleanup: Terminate the background application job
            echo '🧹 Cleaning up background processes...'
            powershell """
                Stop-Job -Name "MumbaiHousingApp" -ErrorAction SilentlyContinue
                Remove-Job -Name "MumbaiHousingApp" -ErrorAction SilentlyContinue
                
                # Cleanup any orphaned python processes running streamlit
                Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { \$_.CommandLine -like "*streamlit*" } | Stop-Process -Force -ErrorAction SilentlyContinue
            """
        }
        success {
            echo '🎉 All tests passed successfully!'
        }
        failure {
            echo '🚨 Pipeline Failed! Please check the stage logs and Selenium output.'
        }
    }
}
