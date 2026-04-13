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
        skipDefaultCheckout()
    }
    triggers {
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All')
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    conditionalStage(name: 'Checkout', condition: true) {
                        checkout scm
                    }
                }
            }
        }
        stage('Lint + SAST + Tests'){
            steps {
                script {
                    conditionalStage(name: 'Lint + SAST + Tests', condition: true) {
                        LintSASTTests()
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    def isMR = (env.gitlabMergeRequestIid != null || env.CHANGE_ID != null)
                    def isMaster = (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main')
                    def isTag = (env.TAG_NAME != null)

                    def buildCond = (isMR || isMaster || isTag)

                    conditionalStage(name: 'Build', condition: buildCond) {
                        dockerBuild(repoName: env.REPO_NAME)
                    }
                }
            }
        }
        stage('Security Scan (Trivy)') {
            steps {
                script {
                    if (env.BRANCH_NAME.contains('MR-') || env.BRANCH_NAME == 'main' || env.TAG_NAME != null) {
                        echo "VULNERABILITY SCAN STARTING for branch: ${env.BRANCH_NAME}"
                        sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --format sarif --output trivy_report.sarif ${IMAGE_NAME}"
                        archiveArtifacts artifacts: 'trivy_report.sarif', allowEmptyArchive: true
                        recordIssues(
                            tools: [sarif(pattern: 'trivy_report.sarif', id: 'trivy', name: 'Trivy SCA Scan')]
                        )
                    } else {
                        echo "Trivy skipped for branch: ${env.BRANCH_NAME}"
                    }
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    def isMaster = (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main')
                    def isTag = (env.TAG_NAME != null)

                    def pushCond = (isMaster || isTag)

                    conditionalStage(name: 'Push', condition: pushCond) {
                        dockerPush(deployTag: env.DEPLOY_TAG)
                    }
                }
            }
        }
        stage('Deploy to Staging') {
            steps {
                script {
                    def isMaster = (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main')

                    conditionalStage(name: 'Deploy to Staging', condition: isMaster) {
                        echo "Target: Staging. Starting Deploy_app job..."
                        build job: 'Deploy_app',
                            parameters: [
                                string(name: 'IMAGE_TAG', value: env.DEPLOY_TAG),
                                string(name: 'ENVIRONMENT', value: 'staging')
                            ],
                            wait: true,
                            propagate: true
                    }
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                script {
                    def isTag = (env.TAG_NAME != null)

                    conditionalStage(name: 'Deploy to Production', condition: isTag) {
                        echo "Target: Production. Starting Deploy_app job..."
                        build job: 'Deploy_app',
                            parameters: [
                                string(name: 'IMAGE_TAG', value: env.DEPLOY_TAG),
                                string(name: 'ENVIRONMENT', value: 'production')
                            ],
                            wait: true,
                            propagate: true
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
