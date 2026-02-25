# Cloud Robot Viz

The Cloud Robot Viz platform provides a visualization interface for monitoring robot states in the cloud. It features a complete ROS 2 backend, a web dashboard, and automated CI/CD pipelines.

## 🚀 Features
- **Cloud-based ROS 2 Monitoring**: Real-time robot parameter tuning and simulation.
- **Web Interface**: Interactive dashboard using `rosbridge` and `nginx`.
- **Dockerized**: Fully containerized environment for consistent deployment.
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions.

## 🛠️ Project Structure
```markdown
.
├── docker/             # Docker configuration (Dockerfile, entrypoint)
├── ros_ws/             # ROS 2 workspace (source code)
├── web/                # Web frontend (HTML, CSS, JS)
├── tests/              # Integration tests
└── .github/workflows/  # CI/CD definitions
```

## 🏗️ Deployment
This project uses **GitHub Actions** for Continuous Delivery:
1.  **Build**: Multi-arch Docker images (amd64/arm64) are built on push to `main`.
2.  **Push**: Images are pushed to Docker Hub.
3.  **Deploy**: The latest image is automatically pulled and restarted on the Tencent Cloud server using SSH.

## 🔧 Troubleshooting
If you encounter issues during development or deployment, please refer to [CI_TROUBLESHOOTING.md](CI_TROUBLESHOOTING.md) for detailed solutions to common problems like:
- ROS 2 node startup failures
- Docker build network/permission errors
- SSH deployment authentication issues

## 📦 How to Run Locally
1. Ensure Docker and Docker Compose are installed.
2. Run the following command:
   ```bash
   docker compose up --build
   ```
3. Open your browser and visit `http://localhost`.
