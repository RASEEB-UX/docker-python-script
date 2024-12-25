import os
import subprocess
import sys

# Configuration
GIT_REPO = "https://github.com/RASEEB-UX/Docker-Zero-to-Hero.git"
DOCKER_IMAGE = "raseebriyazkhan/docker-zero-to-hero:latest"
DOCKER_USERNAME = "raseebriyazkhan"
DOCKER_PASSWORD = "*********8"
DEPLOYMENT_YAML = "deployment.yaml"
SERVICE_YAML = "service.yaml"
APP_NAME = "docker-zero-to-hero"
DOCKERFILE_PATH = "examples/python-web-app"

def run_command(command, shell=False):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, shell=shell, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e.stderr)
        sys.exit(1)

def clone_repo():
    """Clone the Git repository."""
    print("Cloning repository...")
    run_command(["git", "clone", GIT_REPO])

def build_docker_image():
    """Build the Docker image."""
    print("Building Docker image...")
    os.chdir(DOCKERFILE_PATH)
    run_command(["docker", "build", "-t", DOCKER_IMAGE, "."])
    os.chdir("../../")

def push_docker_image():
    """Push the Docker image to Docker Hub."""
    print("Logging in to Docker Hub...")
    run_command(f"echo {DOCKER_PASSWORD} | docker login -u {DOCKER_USERNAME} --password-stdin", shell=True)
    print("Pushing Docker image...")
    run_command(["docker", "push", DOCKER_IMAGE])

def create_k8s_files():
    """Generate Kubernetes deployment and service YAML files."""
    print("Creating Kubernetes deployment and service YAML files...")

    deployment_content = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {APP_NAME}-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {APP_NAME}
  template:
    metadata:
      labels:
        app: {APP_NAME}
    spec:
      containers:
      - name: {APP_NAME}
        image: {DOCKER_IMAGE}
        ports:
        - containerPort: 8000
"""
    service_content = f"""
apiVersion: v1
kind: Service
metadata:
  name: {APP_NAME}-service
spec:
  selector:
    app: {APP_NAME}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: NodePort
"""
    with open(DEPLOYMENT_YAML, "w") as deployment_file:
        deployment_file.write(deployment_content)

    with open(SERVICE_YAML, "w") as service_file:
        service_file.write(service_content)

    print(f"Generated {DEPLOYMENT_YAML} and {SERVICE_YAML}")

def apply_k8s_files():
    """Deploy the application to Kubernetes."""
    print("Deploying to Kubernetes...")
    run_command(["kubectl", "apply", "-f", DEPLOYMENT_YAML])
    run_command(["kubectl", "apply", "-f", SERVICE_YAML])

if __name__ == "__main__":
    print("Starting pipeline...")
    # Step 1: Clone the repository
    clone_repo()
    os.chdir("Docker-Zero-to-Hero")

    # Step 2: Build Docker image
    build_docker_image()

    # Step 3: Push Docker image to Docker Hub
    push_docker_image()

    # Step 4: Generate Kubernetes YAML files
    os.chdir("..")
    create_k8s_files()

    # Step 5: Deploy to Kubernetes
    apply_k8s_files()

    print("Pipeline executed successfully!")