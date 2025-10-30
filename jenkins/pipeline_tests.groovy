pipeline {
  agent any
  stages {
    stage('Unit Tests') {
      steps {
        sh 'pip install -r requirements.txt pytest'
        sh 'pytest tests/test_api.py'
        sh 'pytest tests/test_db_utils.py'
        sh 'pytest tests/test_copythat.py'
      }
    }
  }
}
