# Jenkins Dockerfile (optional, for custom plugins or tools)
FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y docker.io python3 python3-pip git && rm -rf /var/lib/apt/lists/*
USER jenkins
RUN jenkins-plugin-cli --plugins docker-workflow
