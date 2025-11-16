pipeline {
    agent any // This agent is your Windows machine

    environment {
        // !! ADD THIS NEW VARIABLE !!
        // Change this to the name of the folder that contains your docker compose.yml
        PROJECT_DIR = 'Unit_Converter' 

        // Change this to your Docker Hub username
        DOCKERHUB_USERNAME = 'aravindreddy9548'
        // Uses the Jenkins Credential ID you created
        DOCKERHUB_CREDS = 'dockerhub-creds' 
        // The public IP of your EC2 instance
        EC2_HOST = 'ubuntu@54.213.96.150' // Make sure you've filled this in
        // The Jenkins Credential ID for your .pem file
        EC2_CREDS = 'ec2-ssh-key' 
    }

    stages {
        
        stage('Build Docker Images') {
            steps {
                echo "Building all services in ${env.PROJECT_DIR}..."
                // Tell Jenkins to step into your subfolder first
                dir(PROJECT_DIR) { 
                    bat 'docker compose build'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                // Also run from inside that folder
                dir(PROJECT_DIR) {
                    echo 'Logging in to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        bat "docker login -u %USER% -p %PASS%"
                    }
                    
                    echo 'Pushing API image...'
                    bat "docker push %DOCKERHUB_USERNAME%/unit-converter-api:latest"
                    
                    echo 'Pushing Compute image...'
                    bat "docker push %DOCKERHUB_USERNAME%/unit-converter-compute:latest"
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "Deploying to ${env.EC2_HOST}..."
                
                sshagent([EC2_CREDS]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${EC2_HOST} "
                            
                            # This path on the EC2 server must also match!
                            cd ~/my-project/${PROJECT_DIR} 
                            
                            # 1. Pull the new images from Docker Hub
                            docker compose pull
                            
                            # 2. Restart the services using the new images
                            docker compose up -d
                        "
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // Also run this from inside that folder
            dir(PROJECT_DIR) {
                echo 'Logging out of Docker Hub...'
                bat 'docker logout'
            }
        }
    }
}