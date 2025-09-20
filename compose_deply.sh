#!/bin/bash
set -euo pipefail

APP_NAME="music-service"
BRANCH="ad-repo-patch-1"
GIT_REPO="git@github.com:ad-repo/music_service.git"
CLONE_DIR="./cloned-repo"
COMPOSE_FILE="docker-compose.yml"

# Host → Minikube mount paths
MOUNT_SRC="/Users/ad/Projects/music_service/mounts"
MOUNT_DST="/mnt/music_service"

echo "🧼 Cleaning up old resources..."
kubectl delete deployment "$APP_NAME" --ignore-not-found
kubectl delete service "$APP_NAME" --ignore-not-found
kubectl delete pod -l app="$APP_NAME" --ignore-not-found || true

# === Step 0b: Ensure Minikube mount is running ===
echo "📂 Ensuring host directories are mounted into Minikube..."
pgrep -f "minikube mount $MOUNT_SRC:$MOUNT_DST" >/dev/null || \
  (minikube mount "$MOUNT_SRC:$MOUNT_DST" >/dev/null 2>&1 & sleep 3)

# === Step 1: Clone repo ===
echo "📥 Cloning repo branch $BRANCH..."
rm -rf "$CLONE_DIR"
git clone --branch "$BRANCH" "$GIT_REPO" "$CLONE_DIR"
cd "$CLONE_DIR"

# === Step 2: Build image with docker-compose ===
echo "🐳 Building image via docker-compose..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# Extract image name
IMAGE_TAG=$(docker-compose -f "$COMPOSE_FILE" config | grep 'image:' | awk '{print $2}')

# === Step 3: Load image into Minikube ===
echo "📦 Loading image into Minikube: $IMAGE_TAG"
docker save "$IMAGE_TAG" | (eval $(minikube docker-env) && docker load)

echo "✅ Verifying image exists in Minikube..."
if minikube ssh "docker images | grep -q $APP_NAME"; then
  echo "✅ Image $IMAGE_TAG found in Minikube"
else
  echo "❌ ERROR: Image $IMAGE_TAG not found in Minikube"
  exit 1
fi

# === Step 4: Deploy to Kubernetes with volume mounts ===
echo "🚀 Deploying to Kubernetes with volume mounts..."
kubectl delete deployment "$APP_NAME" --ignore-not-found

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $APP_NAME
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $APP_NAME
  template:
    metadata:
      labels:
        app: $APP_NAME
    spec:
      containers:
      - name: $APP_NAME
        image: $IMAGE_TAG
        imagePullPolicy: Never
        ports:
        - containerPort: 9111
        volumeMounts:
        - name: split-volume
          mountPath: /split_dir
        - name: flac-volume
          mountPath: /flac_dir
        - name: mp3-volume
          mountPath: /mp3_dir
        - name: db-volume
          mountPath: /db
        - name: video-volume
          mountPath: /video
      volumes:
      - name: split-volume
        hostPath:
          path: $MOUNT_DST/split_dir
          type: Directory
      - name: flac-volume
        hostPath:
          path: $MOUNT_DST/test_data
          type: Directory
      - name: mp3-volume
        hostPath:
          path: $MOUNT_DST/test_data
          type: Directory
      - name: db-volume
        hostPath:
          path: $MOUNT_DST/app
          type: Directory
      - name: video-volume
        hostPath:
          path: $MOUNT_DST/test_data
          type: Directory
EOF

# === Step 5: Expose service ===
echo "🌐 Exposing $APP_NAME on port 9111..."
kubectl delete service "$APP_NAME" --ignore-not-found
kubectl expose deployment "$APP_NAME" --type=NodePort --port=9111 --target-port=9111

# === Step 6: Wait for rollout ===
echo "📊 Waiting for rollout..."
kubectl rollout status deployment/"$APP_NAME" --timeout=120s || true

echo "📦 Pods:"
kubectl get pods -l app="$APP_NAME" -o wide

# === Step 7: Open service in browser ===
echo "🌍 Opening app in browser..."
minikube service "$APP_NAME"

