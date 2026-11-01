pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'nitin3cmy2k'
        IMAGE_NAME      = 'inventory-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CRED_ID  = 'dockerhub-credentials' // Configured in Jenkins Credentials
    }
     stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build inventory-app') {
                    steps {
                        script {
                            echo 'Building Inventory-app Docker Image...'
                            sh "docker build -t ${DOCKER_REGISTRY_USER}/${inventory-app}:${IMAGE_TAG} ./inventory-app"
                            sh "docker tag ${DOCKER_REGISTRY_USER}/${inventory-app}:${IMAGE_TAG} ${DOCKER_REGISTRY_USER}/${inventory-app}:latest"
                        }
                    }
                }
        
        stage('Deploy to Kubernetes') {
            steps {
                // Assumes kubectl is installed and configured on the Jenkins agent
                // Inside your Jenkinsfile deploy stage:
                // Apply ConfigMap and Secret first
                  sh "kubectl apply -f k8s/app-config.yaml"
        
                 // Apply Storage and Database
                  sh "kubectl apply -f k8s/mysql-pv.yaml"
                  sh "kubectl apply -f k8s/mysql-deploy.yaml"
        
                   // Dynamically updates image tag in deployment manifest and deploy app
                  sh "sed -i 's|image: .*inventory-app:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/app-deploy.yaml"
                  sh "kubectl apply -f k8s/app-deploy.yaml"
            }
        }
    }
}

