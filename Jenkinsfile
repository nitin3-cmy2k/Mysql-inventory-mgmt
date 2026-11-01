pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'nitin3cmy2k'
        IMAGE_NAME      = 'inventory-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CRED_ID  = 'dockerhub-credentials' 
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }
        
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
                    sh "docker tag ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    sh "docker logout"
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                // No KUBECONFIG credentials required because Jenkins runs inside the cluster!
                sh """
                    kubectl apply -f k8s/app-config.yaml
                    kubectl apply -f k8s/mysql-pv.yaml
                    kubectl apply -f k8s/mysql-deploy.yaml
                    
                    sed -i 's|image: .*inventory-app:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/app-deploy.yaml
                    kubectl apply -f k8s/app-deploy.yaml
                """
            }
        }
    }
}
