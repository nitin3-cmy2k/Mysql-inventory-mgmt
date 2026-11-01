pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'nitin3cmy2k'
        IMAGE_NAME      = 'inventory-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CRED_ID  = 'dockerhub-credentials'
        KUBEADM_LOGIN   = 'kubeadmssh'
        // FIXME: Replace this with the actual IP address of your Kubernetes Master/Control-Plane node
        K8S_MASTER_IP   = '192.168.1.11' 
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
        
        stage('Deploy to Kubernetes via SSH') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: env.KUBEADM_LOGIN, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                    // 1. Copy the k8s manifests folder from Jenkins agent to the remote master node
                    sh "scp -i ${SSH_KEY} -o StrictHostKeyChecking=no -r k8s/ root@${K8S_MASTER_IP}:/tmp/k8s"
                    
                    // 2. Execute the commands remotely on the master node where kubectl is fully configured
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no root@${K8S_MASTER_IP} '
                            kubectl apply -f /tmp/k8s/app-config.yaml
                            kubectl apply -f /tmp/k8s/mysql-pv.yaml
                            kubectl apply -f /tmp/k8s/mysql-deploy.yaml
                            
                            sed -i "s|image: .*inventory-app:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g" /tmp/k8s/app-deploy.yaml
                            kubectl apply -f /tmp/k8s/app-deploy.yaml
                            
                            rm -rf /tmp/k8s
                        '
                    """
                }
            }
        }
    }
}
