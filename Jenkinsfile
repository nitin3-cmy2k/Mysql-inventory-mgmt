pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'nitin3cmy2k'
        IMAGE_NAME      = 'inventory-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CRED_ID  = 'dockerhub-credentials'
        KUBECONFIG_CRED = 'config' // Your Jenkins Secret File Credentials ID containing the kubeconfig
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
                // withCredentials extracts your kubeconfig file securely to a temporary location path stored in KUBECONFIG
                withCredentials([file(credentialsId: env.KUBECONFIG_CRED, variable: 'KUBECONFIG')]) {
                    // Apply manifests using the injected kubeconfig environment variable
                    sh "kubectl apply -f k8s/"
                    
                    // Force the rolling update to use your latest build tag
                    sh "kubectl set image deployment/${IMAGE_NAME} ${IMAGE_NAME}=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }
}

