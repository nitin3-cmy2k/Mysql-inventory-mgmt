pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'nitin3cmy2k'
        IMAGE_NAME      = 'inventory-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CRED_ID  = 'dockerhub-credentials' // Your Jenkins credentials ID
        KUBECONFIG      = 'k8skubeconfig'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                // Using standard shell instead of the docker plugin
                sh "docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }
        
        stage('Push to Registry') {
            steps {
                // Securely binds your Docker Hub credentials to temporary environment variables
                withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    // Safe command-line login
                    sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
                    
                    // Tag as latest and push both tags
                    sh "docker tag ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    
                    // Clean up authentication state on the agent
                    sh "docker logout"
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                // Securely binds your secret file to a temporary path variable
                withCredentials([file(credentialsId: 'k8skubeconfig', variable: 'KUBECONFIG')]) {
                    // Execute all kubectl commands using the cluster environment configuration
                    sh "KUBECONFIG=${KUBECONFIG} kubectl apply -f k8s/app-config.yaml"
                    sh "KUBECONFIG=${KUBECONFIG} kubectl apply -f k8s/mysql-pv.yaml"
                    sh "KUBECONFIG=${KUBECONFIG} kubectl apply -f k8s/mysql-deploy.yaml"
                    sh "KUBECONFIG=${KUBECONFIG} kubectl get all -n default"
                    
                    // Dynamically updates image tag in deployment manifest and deploys
                    sh "sed -i 's|image: .*inventory-app:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/app-deploy.yaml"
                    sh "KUBECONFIG=${KUBECONFIG} kubectl apply -f k8s/app-deploy.yaml"
            }
        }
    }
}
