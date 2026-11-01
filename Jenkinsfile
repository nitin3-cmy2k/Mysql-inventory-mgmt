        stage('Deploy to Kubernetes') {
            steps {
                sh """
                    # Force kubectl to talk directly to the internal Kubernetes API service endpoint
                    # and bypass the OpenAPI validation check
                    
                    kubectl --server=https://default.svc --validate=false apply -f k8s/app-config.yaml
                    kubectl --server=https://default.svc --validate=false apply -f k8s/mysql-pv.yaml
                    kubectl --server=https://default.svc --validate=false apply -f k8s/mysql-deploy.yaml
                    
                    sed -i 's|image: .*inventory-app:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/app-deploy.yaml
                    kubectl --server=https://default.svc --validate=false apply -f k8s/app-deploy.yaml
                """
            }
        }
