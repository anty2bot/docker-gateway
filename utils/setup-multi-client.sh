#!/bin/bash
# Author: Dot(anty2bot)
# Date: 2025-07-31
# Description: Shell script to manage multiple proxy clients (V2Fly, Xray)

readonly SCRIPT_PATH=$(dirname "$0")
readonly CLIENT="$1"
readonly SHA256_DIR="$SCRIPT_PATH/sha256"

case "$CLIENT" in
  "v2fly")
    CONFIG_FILE="/etc/v2fly/config.json"
    read -r IMAGE IMAGE_ID < "$SHA256_DIR/v2fly.sha256"
    DOCKER_IMAGE="${IMAGE:-v2fly/v2fly-core:v5.16.1}"
    DOCKER_IMAGE_ID="${IMAGE_ID:-sha256:d1c717b3cc8c7602fdb89a886d0c7fc0cf8c1d973501101d5f5e86f1ec6dcccf}"
    DOCKER_ARGS="run -c $CONFIG_FILE"
    ;;
  "xray")
    CONFIG_FILE="/etc/xray/config.json"
    read -r IMAGE IMAGE_ID < "$SHA256_DIR/xray.sha256"
    DOCKER_IMAGE="${IMAGE:-teddysun/xray:25.7.26}"
    DOCKER_IMAGE_ID="${IMAGE_ID:-sha256:5ca9e4c01ed0d42437d709403b531f14fac10cb84fcd49e5307b9f72eb09a8ea}"
    DOCKER_ARGS=""
    ;;
  *)
    echo "Unsupported client: $CLIENT"
    exit 1
    ;;
esac
shift

readonly CONFIG_FILE DOCKER_IMAGE DOCKER_IMAGE_ID DOCKER_ARGS

setup_image() {
  if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
    return
  fi

  if [ -f /tmp/$CLIENT.tar ]; then
    docker load < /tmp/$CLIENT.tar
  fi

  if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
    return
  fi

  echo "$DOCKER_IMAGE is not downloaded. Trying to pull the image..."
  for ((i=1; i<=5; i++)); do
    docker pull "$DOCKER_IMAGE"
    if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
      break;
    fi
    echo "Download failed. Retrying in 3 seconds... ($i/5)"
    sleep 3
  done
}

setup_container() {
  if [ "$#" -lt "4" ]; then
    echo "Usage: setup_container [name] [port] [FLAG] [FILE]"
    return
  fi

  readonly local NAME="$1"
  readonly local PORT="$2"
  readonly local FLAG="$3"
  readonly local TEMP_CONFIG_FILE="$4"

  readonly local CONTAINER_NAME="proxy-$NAME"
  readonly local CONTAINER_HTTP_PORT="$PORT"
  readonly local CONTAINER_SOCK_PORT="$(($PORT + 1))"

  docker container stop "$CONTAINER_NAME"
  docker container rm "$CONTAINER_NAME"
  if [ "$FLAG" == "off" ]; then
    echo "$CONTAINER_NAME: turn off"
    exit 0
  fi

  if ! [ -d "$(dirname $CONFIG_FILE)" ]; then
    mkdir -p "$(dirname $CONFIG_FILE)"
  fi

  mv $TEMP_CONFIG_FILE $CONFIG_FILE
  if ! [ -f "$CONFIG_FILE" ]; then
    echo "$CONFIG_FILE is not found"
    exit 1
  fi

  if ! [ "$(docker inspect --format '{{.Id}}' $DOCKER_IMAGE)" == "$DOCKER_IMAGE_ID" ]; then
    echo "$DOCKER_IMAGE is not valid"
    exit 1
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -v $CONFIG_FILE:$CONFIG_FILE \
    -p $CONTAINER_HTTP_PORT:$CONTAINER_HTTP_PORT \
    -p $CONTAINER_SOCK_PORT:$CONTAINER_SOCK_PORT \
    $DOCKER_IMAGE \
    $DOCKER_ARGS

  rm $CONFIG_FILE
}

setup_image
setup_container "$@"
