#!/usr/bin/env bash
# Cross-platform local setup script for twitch14sourcebot
set -e

# Detect OS
OS="$(uname -s)"
echo "Detected OS: $OS"

# Python & pip check
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 is required. Please install it."
  exit 1
fi
if ! command -v pip3 >/dev/null 2>&1; then
  echo "pip3 is required. Please install it."
  exit 1
fi

# Install requirements
pip3 install --user -r requirements.txt

# Docker check
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Please install it."
  exit 1
fi

# Jenkins setup
cd jenkins
chmod +x jenkins_setup.sh
# Only start Jenkins if the container is not running
if ! docker ps --format '{{.Names}}' | grep -Eq "^jenkins-twitch14$"; then
  ./jenkins_setup.sh start
else
  echo "Jenkins container is already running. Skipping setup."
fi
cd ..

echo "Local setup complete. Jenkins is running at http://localhost:8080"
