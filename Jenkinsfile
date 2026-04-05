#!groovy
pipeline {
    agent none
    environment {
        REPO_NAME = "imageforpipe"
    }
    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    stages {
        stage('Lint') {
            agent { label 'worker1' }
            steps {
                echo 'Running linter...'
                withCredentials([string(credentialsId: 'SUDO_PASS', variable: 'SUDO_PASSWORD')]) {
                    sh "echo $SUDO_PASSWORD | sudo -S apt-get update && sudo -S apt-get install -y python3-venv"
                }
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install flake8'
                sh './venv/bin/flake8 . --exclude=venv,.git,__pycache__,.pytest_cache'
                sleep 2
            }
        }
        stage('Unit Tests') {
            agent { label 'worker1' }
            steps {
                echo 'Start unit tests...'
                sh '''
                    . venv/bin/activate
                    pip install pytest pytest-asyncio httpx fastapi
                    pytest test_unit.py --junitxml=unit_report.xml
                '''
            }
        }
        stage('Build') {
            agent { label 'worker2' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        env.DEPLOY_TAG = "${USER}/${REPO_NAME}:${env.BUILD_NUMBER}"
                        sh "echo $PASS | docker login -u $USER --password-stdin"
                        sh "docker build -t ${env.DEPLOY_TAG} ."
                        sh "docker push ${env.DEPLOY_TAG}"
                    }
                }
            } 
        }
        stage('Deploy') {
            agent { label 'worker2' }
            environment {
                IMAGE_NAME = "${env.DEPLOY_TAG}"
            }
            steps {
                checkout scm
                withCredentials([file(credentialsId: 'ENV_FILE', variable: 'SECRET_FILE_PATH')]) {
                    sh '''
                        echo "Deploy image: $IMAGE_NAME"
                        if [ -z "$IMAGE_NAME" ] || [ "$IMAGE_NAME" = "null" ]; then
                        echo "ОШИБКА: Имя образа потерялось!"
                        exit 1
                        fi
                        docker compose --env-file "$SECRET_FILE_PATH" down --remove-orphans
                        docker compose --env-file "$SECRET_FILE_PATH" up -d
                    '''
                }
            }
        }
        stage('Integration_tests') {
            agent { label 'worker1' }
            steps {
                echo 'Running tests...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest test_currency_app.py --junitxml=integration_report.xml
                '''
                sleep 3
            }
        }
    }
    post {
        always {
            node ('worker2'){
                sh 'IMAGE_NAME=cleanup docker compose down --remove-orphans -v'
                sh 'docker system prune -f'
            }
        }
        success {
            echo 'Pipeline finished successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}
