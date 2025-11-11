pipeline {
    agent any

    environment {
        // Configure these in Jenkins or override at job time
        REGISTRY = ''                       // e.g. registry.example.com/myorg
        DOCKER_CREDENTIALS_ID = 'docker-registry-credentials' // credential id for docker registry (username/password)
        SONAR_HOST = ''                     // e.g. https://sonar.example.com
        SONAR_TOKEN_CREDENTIALS = 'sonar-token' // credential id for sonar token (string)
    }

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '50'))
        skipDefaultCheckout(false)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
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
                        sh 'mvn -B -DskipTests clean package'
                    } else if (env.IS_GRADLE == 'true') {
                        sh './gradlew assemble -x test || ./gradlew.bat assemble -x test'
                    } else if (env.IS_NODE == 'true') {
                        sh 'npm ci'
                        sh 'npm run build --if-present'
                    } else if (env.IS_PYTHON == 'true') {
                        sh 'python -m pip install --upgrade pip'
                        sh 'pip install -r requirements.txt || true'
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
                        sh 'mvn -B test'
                    } else if (env.IS_GRADLE == 'true') {
                        sh './gradlew test || true'
                    } else if (env.IS_NODE == 'true') {
                        sh 'npm test --if-present || true'
                    } else if (env.IS_PYTHON == 'true') {
                        sh 'pytest --junitxml=pytest-report.xml || true'
                    } else {
                        echo 'No tests configured for detected project type.'
                    }
                }
            }
        }

        stage('Static analysis / SonarQube') {
            when {
                expression { return env.SONAR_HOST?.trim() }
            }
            steps {
                script {
                    withCredentials([string(credentialsId: env.SONAR_TOKEN_CREDENTIALS, variable: 'SONAR_TOKEN')]) {
                        if (env.IS_MAVEN == 'true') {
                            sh "mvn -B sonar:sonar -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=${SONAR_TOKEN}"
                        } else if (env.IS_GRADLE == 'true') {
                            sh "./gradlew sonarqube -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=${SONAR_TOKEN}"
                        } else {
                            // try generic scanner if available
                            sh "sonar-scanner -Dsonar.host.url=${env.SONAR_HOST} -Dsonar.login=${SONAR_TOKEN} || true"
                        }
                    }
                }
            }
        }

        stage('Docker Build') {
            when {
                expression { return env.HAS_DOCKER == 'true' }
            }
            steps {
                script {
                    def imageBase = env.REGISTRY?.trim() ? "${env.REGISTRY}/${env.JOB_NAME}" : "${env.JOB_NAME}"
                    env.IMAGE_NAME = "${imageBase}:${env.BUILD_NUMBER}"
                    echo "Building Docker image ${env.IMAGE_NAME}"
                    sh "docker build -t ${env.IMAGE_NAME} ."
                }
            }
        }

        stage('Push Docker Image') {
            when {
                allOf {
                    expression { return env.HAS_DOCKER == 'true' }
                    expression { return env.REGISTRY?.trim() }
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${env.REGISTRY}", env.DOCKER_CREDENTIALS_ID) {
                        sh "docker push ${env.IMAGE_NAME}"
                        sh "docker tag ${env.IMAGE_NAME} ${env.REGISTRY}/${env.JOB_NAME}:latest || true"
                        sh "docker push ${env.REGISTRY}/${env.JOB_NAME}:latest || true"
                    }
                }
            }
        }

        stage('Archive artifacts & test results') {
            steps {
                script {
                    // common test report locations
                    junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml,**/build/test-results/**/*.xml,**/pytest-report.xml,**/test-results/**/*.xml'
                    archiveArtifacts artifacts: '**/target/*.jar,**/build/libs/*.jar,**/dist/**,**/*.zip,**/*.tar.gz', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        always {
            cleanWs(cleanWhenFailure: true)
        }
    }
}