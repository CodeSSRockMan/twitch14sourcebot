#!/usr/bin/env bash
# Script to automate creation of Jenkins pipelines and credentials
# Usage: ./jenkins_create_pipelines.sh
set -e

echo "Checking and installing required tools..."
# Install required tools if missing (macOS and Debian/Ubuntu)
install_tool() {
  TOOL=$1
  if ! command -v $TOOL >/dev/null 2>&1; then
    echo "$TOOL not found. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
      if command -v brew >/dev/null 2>&1; then
        brew install $TOOL
      else
        echo "Homebrew not found. Please install $TOOL manually."
        exit 1
      fi
    elif [[ -f /etc/debian_version ]]; then
      sudo apt-get update && sudo apt-get install -y $TOOL
    else
      echo "Please install $TOOL manually."
      exit 1
    fi
  else
    echo "$TOOL already installed."
  fi
}

for tool in wget jq; do
  install_tool $tool
done

# Java special case (openjdk)
if ! command -v java >/dev/null 2>&1; then
  echo "Java not found. Attempting to install..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew >/dev/null 2>&1; then
      brew install openjdk
      sudo ln -sfn $(brew --prefix openjdk)/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk || true
      export PATH="$(brew --prefix openjdk)/bin:$PATH"
    else
      echo "Homebrew not found. Please install Java manually."
      exit 1
    fi
  elif [[ -f /etc/debian_version ]]; then
    sudo apt-get update && sudo apt-get install -y default-jre
  else
    echo "Please install Java manually."
    exit 1
  fi
else
  echo "Java already installed."
fi

# Load Jenkins CLI environment variables from .jenkins.env
if [ -f ".jenkins.env" ]; then
  set -a
  source .jenkins.env
  set +a
else
  echo ".jenkins.env file not found. Please create it with JENKINS_URL, JENKINS_USER, JENKINS_TOKEN, JENKINS_CLI_JAR."
  exit 1
fi

echo "JENKINS_URL=$JENKINS_URL"
echo "JENKINS_USER=$JENKINS_USER"
echo "JENKINS_CLI_JAR=$JENKINS_CLI_JAR"

echo "Checking if Jenkins is up..."
CURL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL/login")
echo "curl status: $CURL_STATUS"
if [ "$CURL_STATUS" != "200" ]; then
  echo "Jenkins is not running or not accessible at $JENKINS_URL (HTTP $CURL_STATUS). Please start Jenkins and try again."
  exit 1
fi
echo "Jenkins is up. Proceeding."

# Download Jenkins CLI if not present
if [ ! -f "$JENKINS_CLI_JAR" ]; then
  echo "Downloading Jenkins CLI..."
  wget "$JENKINS_URL/jnlpJars/jenkins-cli.jar" -O "$JENKINS_CLI_JAR"
else
  echo "Jenkins CLI already present."
fi

# Create credentials (username/password or secret text)
if [ -f "../secrets.json" ]; then
  echo "Reading secrets from ../secrets.json..."
  TWITCH_TOKEN=$(jq -r .twitch_token ../secrets.json)
  BOT_NICK=$(jq -r .bot_nick ../secrets.json)
  CHANNEL=$(jq -r .channel ../secrets.json)
  PREFIX=$(jq -r .prefix ../secrets.json)
  echo "Creating Jenkins credentials for twitch_token..."
  # When running CLI, prompt for password interactively
  java -jar $JENKINS_CLI_JAR -s $JENKINS_URL -auth $JENKINS_USER:$JENKINS_TOKEN create-credentials-by-xml system::system::jenkins _ <<EOF
<com.cloudbees.plugins.credentials.impl.StringCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>twitch_token</id>
  <secret>$TWITCH_TOKEN</secret>
  <description>Twitch OAuth Token</description>
</com.cloudbees.plugins.credentials.impl.StringCredentialsImpl>
EOF
  # Repeat for other secrets as needed
else
  echo "../secrets.json not found. Skipping credentials creation."
fi

# Create pipeline jobs using Jenkinsfile and test pipeline
for JOB in main pipeline_tests; do
  if [ "$JOB" == "main" ]; then
    JFILE="../Jenkinsfile"
    JOBNAME="twitch14-main"
  else
    JFILE="pipeline_tests.groovy"
    JOBNAME="twitch14-tests"
  fi
  echo "Creating Jenkins job $JOBNAME from $JFILE..."
  # When running CLI, prompt for password interactively
  java -jar $JENKINS_CLI_JAR -s $JENKINS_URL -auth $JENKINS_USER:$JENKINS_TOKEN create-job $JOBNAME < <(
    cat <<EOF
<flow-definition plugin="workflow-job@2.40">
  <description></description>
  <keepDependencies>false</keepDependencies>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
    <script>$(cat $JFILE)</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
</flow-definition>
EOF
  )
  echo "Job $JOBNAME created."
done

echo "Jenkins pipelines and credentials created."
