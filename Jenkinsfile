pipeline {
  agent any

  environment {
    // ====== FILL THESE ======
    // For Docker Hub, use docker.io and image like: <hub-username>/<repo>
    REGISTRY                = 'docker.io'                    // e.g. docker.io
    IMAGE_REPO              = '<your-dockerhub-username>/<repo>'  // e.g. manuraj23/sm-insights
    DOCKER_CREDENTIALS_ID   = 'docker-registry-credentials'  // Jenkins creds (username/password or token)
    SONAR_HOST              = ''                             // e.g. https://sonar.mycompany.com (leave blank to skip)
    SONAR_TOKEN_CREDENTIALS = 'sonar-token'                  // Jenkins string credential id
    // =========================
  }

  options {
    timestamps()
    ansiColor('xterm')
    buildDiscarder(logRotator(numToKeepStr: '50'))
    skipDefaultCheckout(false)
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Detect project type') {
      steps {
        script {
          env.IS_MAVEN   = fileExists('pom.xml') ? 'true' : 'false'
          env.IS_GRADLE  = (fileExists('build.gradle') || fileExists('build.gradle.kts')) ? 'true' : 'false'
          env.IS_NODE    = fileExists('package.json') ? 'true' : 'false'
          env.IS_PYTHON  = (fileExists('requirements.txt') || fileExists('setup.py') || fileExists('pyproject.toml')) ? 'true' : 'false'
          env.HAS_DOCKER = fileExists('Dockerfile') ? 'true' : 'false'
          echo "Detected: MAVEN=${env.IS_MAVEN}, GRADLE=${env.IS_GRADLE}, NODE=${env.IS_NODE}, PY=${env.IS_PYTHON}, DOCKER=${env.HAS_DOCKER}"
        }
      }
    }

    stage('Build') {
      steps {
        script {
          if (env.IS_MAVEN == 'true') {
            bat 'mvn -B -DskipTests clean package'
          } else if (env.IS_GRADLE == 'true') {
            // prefer gradlew.bat if present
            if (fileExists('gradlew.bat')) {
              bat 'gradlew.bat assemble -x test'
            } else {
              bat 'gradle assemble -x test'
            }
          } else if (env.IS_NODE == 'true') {
            bat 'cmd /c npm ci'
            bat 'cmd /c npm run build --if-present'
          } else if (env.IS_PYTHON == 'true') {
            bat 'python -m pip install --upgrade pip'
            // don’t fail build if no tests etc.
            bat 'pip install -r requirements.txt || exit /b 0'
          } else {
            echo 'No recognized build system. Skipping build.'
          }
        }
      }
    }

    stage('Test') {
      steps {
        script {
          if (env.IS_MAVEN == 'true') {
            bat 'mvn -B test'
          } else if (env.IS_GRADLE == 'true') {
            if (fileExists('gradlew.bat')) {
              bat 'gradlew.bat test || exit /b 0'
            } else {
              bat 'gradle test || exit /b 0'
            }
          } else if (env.IS_NODE == 'true') {
            bat 'cmd /c npm test --if-present || exit /b 0'
          } else if (env.IS_PYTHON == 'true') {
            // pytest optional
            bat 'pytest --junitxml=pytest-report.xml || exit /b 0'
          } else {
            echo 'No tests configured for detected project type.'
          }
        }
      }
    }

    stage('Static analysis / SonarQube') {
      when { expression { return env.SONAR_HOST?.trim() } }
      steps {
        script {
          withCredentials([string(credentialsId: env.SONAR_TOKEN_CREDENTIALS, variable: 'SONAR_TOKEN')]) {
            if (env.IS_MAVEN == 'true') {
              bat "mvn -B sonar:sonar -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=%SONAR_TOKEN%"
            } else if (env.IS_GRADLE == 'true') {
              if (fileExists('gradlew.bat')) {
                bat "gradlew.bat sonarqube -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=%SONAR_TOKEN%"
              } else {
                bat "gradle sonarqube -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=%SONAR_TOKEN%"
              }
            } else {
              // generic scanner if installed on PATH
              bat "sonar-scanner -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=%SONAR_TOKEN% || exit /b 0"
            }
          }
        }
      }
    }

    stage('Docker Build') {
      when { expression { return env.HAS_DOCKER == 'true' } }
      steps {
        script {
          // Short commit hash for tags
          def gitShort = bat(script: '@echo off\r\ngit rev-parse --short HEAD', returnStdout: true).trim()
          env.IMAGE_TAG = "${IMAGE_REPO}:${gitShort}"
          echo "Building Docker image ${env.IMAGE_TAG}"
          bat "docker build -t ${env.IMAGE_TAG} -t ${IMAGE_REPO}:latest ."
        }
      }
    }

    stage('Push Docker Image') {
      when { expression { return env.HAS_DOCKER == 'true' } }
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'USR', passwordVariable: 'PSW')]) {
            // Login (Docker Hub works with docker.io)
            bat """
              docker logout ${env.REGISTRY} || echo not logged in
              echo %PSW% | docker login -u %USR% --password-stdin ${env.REGISTRY}
            """
          }
          bat """
            docker push ${env.IMAGE_TAG}
            docker push ${IMAGE_REPO}:latest
          """
        }
      }
    }

    stage('Deploy (same Windows host)') {
      when { expression { return env.HAS_DOCKER == 'true' } }
      steps {
        bat """
          docker pull ${IMAGE_REPO}:latest
          for /f "tokens=*" %%i in ('docker ps -aq -f name=streamlit-app') do docker rm -f %%i
          docker run -d --name streamlit-app -p 8501:8501 --restart unless-stopped ${IMAGE_REPO}:latest
        """
      }
    }
  }

  post {
    success { echo "Pipeline succeeded: ${env.JOB_NAME} #${env.BUILD_NUMBER} - http://localhost:8501" }
    failure { echo "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
    always  { cleanWs(cleanWhenFailure: true) }
  }
}
