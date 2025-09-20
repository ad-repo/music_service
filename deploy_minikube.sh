#!/bin/bash

set -euo pipefail

APP_NAME="music-service"
GIT_REPO="git@github.com:ad-repo/music_service.git"
GIT_BRANCH="ad-repo-patch-1"
CLONE_DIR="./cloned-repo"

# === Step 0: Cleanup old resources ===
echo "🧼 Cleaning up old K8s resources..."
kubectl delete deployment "$APP_NAME" --ignore-not-found
kubectl delete service "$APP_NAME" --ignore-not-found
kubectl delete rs -l app="$APP_NAME" --ignore-not-found --grace-period=0 --force
kubectl delete pod -l app="$APP_NAME" --ignore-not-found --grace-period=0 --force

# === Step 1: Switch to Minikube Docker ===
echo "🐳 Using Minikube Docker daemon..."
eval $(minikube docker-env)

# Remove old images
docker rmi $(docker images -q "$APP_NAME") || true

# === Step 2: Clone repo ===
echo "📥 Cloning branch $GIT_BRANCH from $GIT_REPO..."
rm -rf "$CLONE_DIR"
git clone --branch "$GIT_BRANCH" "$GIT_REPO" "$CLONE_DIR"

# Compute commit hash for tagging
GIT_COMMIT=$(git -C "$CLONE_DIR" rev-parse --short HEAD)
IMAGE_TAG="$APP_NAME:$GIT_COMMIT"

# === Step 3: Build inside Minikube Docker ===
echo "🐳 Building Docker image inside Minikube: $IMAGE_TAG"
docker build --no-cache -t "$IMAGE_TAG" "$CLONE_DIR"

# === Step 4: Verify image exists in Minikube ===
if ! minikube ssh "docker images $IMAGE_TAG --format '{{.Repository}}:{{.Tag}}'" | grep -q "$IMAGE_TAG"; then
  echo "❌ ERROR: Image $IMAGE_TAG not found inside Minikube Docker!"
  exit 1
fi
echo "✅ Verified image $IMAGE_TAG exists inside Minikube"

# === Step 5: Deploy to Kubernetes ===
echo "🚀 Deploying $APP_NAME with image $IMAGE_TAG"
kubectl create deployment "$APP_NAME" --image="$IMAGE_TAG"

# Force imagePullPolicy: Never (so it won’t try Docker Hub)
kubectl patch deployment "$APP_NAME" \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"'"$APP_NAME"'","imagePullPolicy":"Never"}]}}}}'

# === Step 6: Expose service ===
echo "🌐 Exposing service on port 9111"
kubectl expose deployment "$APP_NAME" --type=NodePort --port=9111 --target-port=9111

# === Step 7: Wait for pod ===
echo "📊 Waiting for pod to be Running..."
kubectl wait --for=condition=available --timeout=120s deployment/"$APP_NAME" || true
kubectl get pods -l app="$APP_NAME"

# === Step 8: Open service ===
echo "🌍 Opening app in browser..."
minikube service "$APP_NAME"

