#!/bin/bash
# Author: Dot(anty2bot)
# Date: 2024-12-14
# Description: This is a Shell script for Docker Install/Uninstall

install_docker() {
  echo "Updating system and installing dependencies..."
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  
  echo "Adding Docker's official GPG key..."
  sudo install -m 0755 -d /etc/apt/keyrings

  for ((i=1; i<=5; i++)); do
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    if [ -s /etc/apt/keyrings/docker.asc ]; then
      break;
    fi
    echo "Download failed. Retrying in 3 seconds... ($i/5)"
    sleep 3
  done
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  
  echo "Adding Docker repository to Apt sources..."
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update

  echo "Installing Docker and related components..."
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  echo "Starting and enabling Docker service..."
  sudo systemctl start docker
  sudo systemctl enable docker

  echo "Docker installation completed."
}

uninstall_docker() {
  echo "Stopping and disabling Docker service..."
  sudo systemctl stop docker
  sudo systemctl disable docker

  echo "Removing Docker packages..."
  sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras

  echo "Removing Docker files and directories..."
  sudo rm -rf /var/lib/docker
  sudo rm -rf /var/lib/containerd

  echo "Removing Docker repository and GPG key..."
  sudo rm /etc/apt/sources.list.d/docker.list
  sudo rm /etc/apt/keyrings/docker.asc

  echo "Docker uninstallation completed."
}

case "$1" in
  install)
    install_docker
    ;;
  uninstall)
    uninstall_docker
    ;;
  *)
    echo "Usage: $0 {install|uninstall}"
    exit 1
    ;;
esac
