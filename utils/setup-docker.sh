#!/bin/bash
# Author: Dot(anty2bot)
# Date: 2024-12-14
# Description: This is a Shell script for Docker Install/Uninstall

install_docker() {
  echo "Updating system and installing dependencies..."
  apt-get update
  apt-get install -y ca-certificates curl
  
  echo "Adding Docker's official GPG key..."
  install -m 0755 -d /etc/apt/keyrings

  for ((i=1; i<=5; i++)); do
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    if [ -s /etc/apt/keyrings/docker.asc ]; then
      break;
    fi
    echo "Download failed. Retrying in 3 seconds... ($i/5)"
    sleep 3
  done
  chmod a+r /etc/apt/keyrings/docker.asc
  
  echo "Adding Docker repository to Apt sources..."
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update

  echo "Installing Docker and related components..."
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  echo "Starting and enabling Docker service..."
  systemctl start docker
  systemctl enable docker

  echo "Docker installation completed."
}

uninstall_docker() {
  echo "Stopping and disabling Docker service..."
  systemctl stop docker
  systemctl disable docker

  echo "Removing Docker packages..."
  apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras

  echo "Removing Docker files and directories..."
  rm -rf /var/lib/docker
  rm -rf /var/lib/containerd

  echo "Removing Docker repository and GPG key..."
  rm /etc/apt/sources.list.d/docker.list
  rm /etc/apt/keyrings/docker.asc

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
