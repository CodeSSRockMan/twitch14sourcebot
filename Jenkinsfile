# Jenkinsfile for twitch14sourcebot
pipeline {
  agent any
  environment {
    ANSIBLE_HOST_KEY_CHECKING = 'False'
  }
  stages {
    stage('Build App Container') {
      steps {
        sh 'docker build -t twitch14-app ./project'
      }
    }
    stage('Run Unit Tests') {
      steps {
        build job: 'pipeline_tests', propagate: true
      }
    }
    stage('Run Ansible') {
      steps {
        sh 'ansible-playbook -i "localhost," -c local ansible/playbook.yml'
      }
    }
    stage('Copy Logs') {
      steps {
        sh 'python3 utils/copythat.py /opt/twitch14sourcebot /var/jenkins_home/logs || true'
      }
    }
  }
}
