#!groovy
pipeline {
    agent{label 'staging'}
    environment {
        REPO_NAME = "currency_app"
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
        stage('Lint + SAST + Tests'){
            steps {
                script{
                    echo 'Creating venv...'
                    sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install flake8 bandit bandit-sarif-formatter pytest -r requirements.txt
                    '''
                    parallel(
                        "Linter (Python)": {
                            echo 'Runnung linter flake8...'
                            sh './venv/bin/flake8 . --exclude=venv,.git,__pycache__,.pytest_cache --tee --output-file=flake8_report.txt'
                        },
                        "Linter (Docker)": {
                            sh "docker run --rm -i hadolint/hadolint hadolint -f checkstyle - < Dockerfile > hadolint_report.xml || true"
                        },
                        "SAST(bandit)": {
                            echo "Running bandit..."
                            sh './venv/bin/bandit -r app/ -f sarif -o bandit_report.sarif || true'
                        },
                        "Unit tests": {
                            echo "Running unit-tests..."
                            sh '''
                                export PYTHONPATH=$PYTHONPATH:$(pwd)
                                ./venv/bin/pytest tests/test_unit.py --junitxml=unit_report.xml
                            '''
                        }

                    )
                }
            }
            post {
                always {
                    junit 'unit_report.xml'
                    archiveArtifacts artifacts: 'bandit_report.sarif, hadolint_report.xml, unit_report.xml', allowEmptyArchive: true
                    recordIssues(
                        tools: [
                            sarif(pattern: 'bandit_report.sarif', id: 'bandit', name: 'Bandit'),
                            checkStyle(pattern: 'hadolint_report.xml', id: 'hadolint', name: 'Hadolint')
                        ],
                        qualityGates: [[threshold: 1, type: 'TOTAL', severity: 'ERROR']]
                        // Если есть крит ошибки - пайп падает
                    )
                    cleanWs()
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    env.DEPLOY_TAG = "${USER}/${REPO_NAME}:${env.BUILD_NUMBER}"
                    }
                    echo "Building image: ${env.DEPLOY_TAG}"
                    sh "docker build -t ${env.DEPLOY_TAG} ."
                }
            }
        }
        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        sh "echo $PASS | docker login -u $USER --password-stdin"
                        sh "docker push ${env.DEPLOY_TAG}"
                        sh "docker rmi ${env.DEPLOY_TAG}"
                    }
                }
            }
        }
        stage('Deploy') {
            agent { label 'production' }
            options {
                timeout(time: 48, unit: 'HOURS')
            }
            steps {
                script {
                    conditionalStage(name: 'Deploy', condition: env.BRANCH_NAME == 'master') {
                        checkout scm
                        withCredentials([file(credentialsId: 'ENV_FILE', variable: 'SECRET_FILE_PATH')]) {
                            sh """
                                echo "Deploy image: ${env.DEPLOY_TAG}"
                                IMAGE_NAME=${env.DEPLOY_TAG} docker compose --env-file "${SECRET_FILE_PATH}" down --remove-orphans
                                IMAGE_NAME=${env.DEPLOY_TAG} docker compose --env-file "${SECRET_FILE_PATH}" up -d
                            """
                            sh 'docker system prune -f'
                        }
                    }
                }
            }
        }
        stage('Smoke test') {
            agent { label 'production' }
            steps {
                script {
                    conditionalStage(name: 'Smoke test', condition: env.BRANCH_NAME == 'master') {
                        echo 'Running tests...'
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            ./venv/bin/pip install -r requirements.txt
                            ./venv/bin/python3 -m pytest tests/test_currency_app.py --junitxml=integration_report.xml
                        '''
                        junit 'integration_report.xml'
                    }
                }
            }
        }
    }
    post {
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
