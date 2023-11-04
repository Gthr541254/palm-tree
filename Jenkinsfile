pipeline {
    agent any

    stages {
        stage('Test Model') {
            steps {
              pwd()
              sh label: 'Run make model-test', script: 'make model-test'
            }
        }
    }
}
