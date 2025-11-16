pipeline {

    // Your Jenkins master/agent is Windows

    agent any
 
    environment {

        PROJECT_DIR      = 'Unit_Converter'
 
        DOCKERHUB_USERNAME = 'aravindreddy9548'

        DOCKERHUB_CREDS    = 'dockerhub-creds'
 
        // e.g. ubuntu@11.22.33.44

        EC2_HOST        = 'ubuntu@54.213.96.150'

        // Jenkins SSH private key credential ID (.pem)

        EC2_CREDS       = 'ec2-ssh-key'

    }
 
    stages {
 
        stage('Build Docker Images') {

            steps {

                echo "Building all services in ${env.PROJECT_DIR}..."
 
                dir(PROJECT_DIR) {

                    // Use Docker Compose v2 style on Windows

                    bat '''

docker --version

docker compose version

docker compose build

'''

                }

            }

        }
 
        stage('Push to Docker Hub') {
    steps {
        dir(PROJECT_DIR) {
            echo 'Logging in to Docker Hub...'
 
            withCredentials([usernamePassword(
                credentialsId: DOCKERHUB_CREDS,
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
            )]) {
                // 1) Login using credentials
                bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
 
                // 2) Show who we are (safe to log)
                bat 'echo Logged in as %DOCKER_USER%'
 
                // 3) Push images under that same username
                echo 'Pushing API image...'
                bat "docker push %DOCKER_USER%/unit-converter-api:latest"
 
                echo 'Pushing Compute image...'
                bat "docker push %DOCKER_USER%/unit-converter-compute:latest"
            }
        }
    }
}
        stage('Debug SSH') {

    steps {

        bat '''

  where ssh

  ssh -V

'''

    }

}

 
 
        stage('Deploy to EC2') {

            steps {

                echo "Deploying to ${env.EC2_HOST}..."
 
                // Avoid sshagent plugin; use SSH key directly

                withCredentials([sshUserPrivateKey(

                    credentialsId: EC2_CREDS,

                    keyFileVariable: 'SSH_KEY',

                    usernameVariable: 'SSH_USER'

                )]) {

                    // On Windows, this runs cmd.exe. `ssh` must be on PATH

                    bat """

    ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %EC2_HOST% "cd ~/my-project/${PROJECT_DIR} && docker compose pull && docker compose up -d"

"""

                    // If Docker Compose v1 is installed on EC2 instead, use:

                    // docker-compose pull && docker-compose up -d

                }

            }

        }

    }
 
    post {

        always {

            dir(PROJECT_DIR) {

                echo 'Logging out of Docker Hub...'

                bat 'docker logout'

            }

        }

    }

}

 