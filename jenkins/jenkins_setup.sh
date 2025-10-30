#!/bin/bash
# Jenkins setup script: creates or reuses a Jenkins container with persistent volume
# Usage: ./jenkins_setup.sh [start|destroy|timed]

JENKINS_HOME_DIR="$PWD/jenkins_home"
JENKINS_CONTAINER="jenkins-twitch14"
JENKINS_IMAGE="jenkins/jenkins:lts"
JENKINS_PORT=8080

if [ "$1" == "destroy" ]; then
    echo "Stopping and removing Jenkins container..."
    docker stop $JENKINS_CONTAINER 2>/dev/null
    docker rm $JENKINS_CONTAINER 2>/dev/null
    echo "Removing Jenkins home volume..."
    rm -rf "$JENKINS_HOME_DIR"
    echo "Jenkins destroyed."
    exit 0
fi

# Maintain Jenkins container for 5 minutes, then destroy if requested
if [ "$1" == "timed" ]; then
    echo "Jenkins will run for 5 minutes, then be destroyed."
    sleep 300
    "$0" destroy
    exit 0
fi

# Create persistent volume if it doesn't exist
mkdir -p "$JENKINS_HOME_DIR"

# Pull Jenkins image
if ! docker image inspect $JENKINS_IMAGE >/dev/null 2>&1; then
    docker pull $JENKINS_IMAGE
fi

# Start Jenkins container
if ! docker ps -a --format '{{.Names}}' | grep -Eq "^$JENKINS_CONTAINER$"; then
    echo "Creating Jenkins container..."
    docker run -d \
        --name $JENKINS_CONTAINER \
        -p $JENKINS_PORT:8080 \
        -v "$JENKINS_HOME_DIR":/var/jenkins_home \
        -v /var/run/docker.sock:/var/run/docker.sock \
        $JENKINS_IMAGE
else
    echo "Jenkins container already exists. Starting..."
    docker start $JENKINS_CONTAINER
fi

# Install Docker Pipeline plugin
sleep 10
echo "Installing Docker Pipeline plugin..."
docker exec $JENKINS_CONTAINER bash -c "jenkins-plugin-cli --plugins docker-workflow"

# If secrets.json does not exist, copy from template
if [ ! -f "$PWD/../secrets.json" ] && [ -f "$PWD/../secrets.json.template" ]; then
    cp "$PWD/../secrets.json.template" "$PWD/../secrets.json"
    echo "Created secrets.json from template. Please update it with your credentials."
fi
# If terraform.tfvars does not exist, copy from template
if [ ! -f "$PWD/../terraform/terraform.tfvars" ] && [ -f "$PWD/../terraform/terraform.tfvars.template" ]; then
    cp "$PWD/../terraform/terraform.tfvars.template" "$PWD/../terraform/terraform.tfvars"
    echo "Created terraform.tfvars from template. Please update it with your values."
fi

# Inject secrets into Jenkins as environment variables (if Jenkins is running)
if docker ps --format '{{.Names}}' | grep -Eq "^jenkins-twitch14$"; then
  if [ -f "$PWD/../secrets.json" ]; then
    echo "Injecting secrets into Jenkins..."
    TWITCH_TOKEN=$(jq -r .twitch_token "$PWD/../secrets.json")
    BOT_NICK=$(jq -r .bot_nick "$PWD/../secrets.json")
    CHANNEL=$(jq -r .channel "$PWD/../secrets.json")
    PREFIX=$(jq -r .prefix "$PWD/../secrets.json")
    docker exec jenkins-twitch14 bash -c "echo 'TWITCH_OAUTH_TOKEN=$TWITCH_TOKEN' >> /var/jenkins_home/.env && \
      echo 'TWITCH_BOT_NICK=$BOT_NICK' >> /var/jenkins_home/.env && \
      echo 'TWITCH_CHANNEL=$CHANNEL' >> /var/jenkins_home/.env && \
      echo 'TWITCH_PREFIX=$PREFIX' >> /var/jenkins_home/.env"
    echo "Secrets injected into Jenkins .env file. Configure your Jenkins jobs to load from /var/jenkins_home/.env."
  else
    echo "secrets.json not found, skipping Jenkins secrets injection."
  fi
fi

echo "Jenkins is running at http://localhost:$JENKINS_PORT"
echo "Initial admin password:"
docker exec $JENKINS_CONTAINER cat /var/jenkins_home/secrets/initialAdminPassword
