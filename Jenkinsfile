pipeline {
    agent any // Assumes Docker is installed on the Jenkins server

    // Environment variables for our pipeline
    environment {
        // Change this to your Docker Hub username
        DOCKERHUB_USERNAME = 'aravindreddy9548'
        // Uses the Jenkins Credential ID you created
        DOCKERHUB_CREDS = 'dockerhub-creds' 
        // The public IP of your EC2 instance
        EC2_HOST = 'ubuntu@YOUR_EC2_PUBLIC_IP'
        // The Jenkins Credential ID for your .pem file
        EC2_CREDS = 'ec2-ssh-key' 
    }

    stages {
        
        stage('Build Docker Images') {
            steps {
                echo 'Building all services...'
                // This command reads your docker-compose.yml and builds 
                // the images named 'unit-converter-api' and 'unit-converter-compute'
                sh 'docker-compose build'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Logging in to Docker Hub...'
                // Logs in using the Jenkins credential
                withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh "docker login -u ${env.USER} -p ${env.PASS}"
                }
                
                echo 'Pushing API image...'
                sh "docker push ${env.DOCKERHUB_USERNAME}/unit-converter-api:latest"
                
                echo 'Pushing Compute image...'
                sh "docker push ${env.DOCKERHUB_USERNAME}/unit-converter-compute:latest"
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "Deploying to ${env.EC2_HOST}..."
                
                // Use the SSH key to log in to the EC2 instance
                sshagent([EC2_CREDS]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${EC2_HOST} "
                            
                            # 1. Go to the project folder
                            cd ~/my-project
                            
                            # 2. IMPORTANT: Pull the new images from Docker Hub
                            docker-compose pull
                            
                            # 3. Restart the services using the new images
                            # We no longer use --build here!
                            docker-compose up -d
                        "
                    '''
                }
            }
        }
    }
    
    post {
        // This 'post' block always runs, no matter what
        always {
            echo 'Logging out of Docker Hub...'
            sh 'docker logout'
        }
    }
}
