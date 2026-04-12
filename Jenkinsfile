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
        stage('Deploy Trigger') {
            steps {
                script {
                    def shouldDeploy = (env.BRANCH_NAME == 'master' || env.TAG_NAME != null)
                    def targetEnv = (env.TAG_NAME != null) ? 'production' : 'staging'
                    conditionalStage(name: 'Deploy Trigger', condition: shouldDeploy) {
                        echo "Triggering deploy to ${targetEnv}..."
                        build job: 'Deploy_app',
                            parameters: [
                                string(name: 'IMAGE_TAG', value: env.DEPLOY_TAG),
                                string(name: 'ENVIRONMENT', value: targetEnv)
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
