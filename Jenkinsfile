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
                LintSASTTests()
            }
        }
        stage('Build') {
            steps {
                dockerBuild(repoName: env.REPO_NAME)
            }
        }
        stage('Push') {
            steps {
                dockerPush(deployTag: env.DEPLOY_TAG)
            }
        }
        stage('Deploy') {
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
            steps {
                script {
                    conditionalStage(name: 'Smoke test', condition: env.BRANCH_NAME == 'master') {
                        echo 'Running tests...'
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            ./venv/bin/pip install -r requirements.txt
                            ./venv/bin/python3 -m pytest tests/test_currency_app.py --junitxml=smoke_report.xml
                        '''
                        junit 'smoke_report.xml'
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
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
