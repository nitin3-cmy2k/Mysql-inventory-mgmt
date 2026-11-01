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
        
        stage('Build Docker Image') {
            steps {
                script {
                    appImage = docker build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}") .
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    // Fixed: Wrapped 'dockerhub-credentials' in quotes or used the DOCKER_CRED_ID environment variable
                    docker.withRegistry('', DOCKER_CRED_ID) {
                        appImage.push()
                        appImage.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                // Assumes kubectl is installed and configured on the Jenkins agent
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
