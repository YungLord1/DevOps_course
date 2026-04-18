#!groovy
pipeline {
    agent none
    environment {
        REPO_NAME = "imageforpipe"
    }
    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
        gitLabConnection('gitlab-server')
    }
    triggers {
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All')
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
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
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
            when {
                branch 'master'
                beforeInput true
            }
            options {
                timeout(time: 48, unit: 'HOURS')
            }
            input{
                message 'Do u want to deploy?'
                ok 'Deploy now'
            }
            environment {
                IMAGE_NAME = "${env.DEPLOY_TAG}"
            }
            steps {
                checkout scm
                withCredentials([file(credentialsId: 'ENV_FILE', variable: 'SECRET_FILE_PATH')]) {
                    sh '''
                        echo "Deploy image: $IMAGE_NAME"
                        docker compose --env-file "$SECRET_FILE_PATH" down --remove-orphans
                        docker compose --env-file "$SECRET_FILE_PATH" up -d
                    '''
                }
            }
        }
        stage('Integration_tests') {
            agent { label 'worker1' }
            when {
                branch 'master'
            }
            steps {
                echo 'Running tests...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest test_currency_app.py --junitxml=integration_report.xml
                '''
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
            updateGitlabCommitStatus(name: 'jenkins', state: 'success')
            echo 'Pipeline finished successfully'
        }
        failure {
            updateGitlabCommitStatus(name: 'jenkins', state: 'failed')
            echo 'Pipeline failed'
        }
    }
}
