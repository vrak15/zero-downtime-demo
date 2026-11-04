pipeline {
    agent any

    environment {
        DOCKERHUB  = "vrak45"
        APP        = "zero-demo"
        GREEN_PORT = "5002"
        BLUE_PORT  = "5001"
        UPSTREAM   = "/etc/nginx/conf.d/active_upstream.conf"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build v2') {
            steps {
                sh "docker build -t ${DOCKERHUB}/${APP}:v2 ./app-v2"
            }
        }

        stage('Push v2') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                    sh "docker push ${DOCKERHUB}/${APP}:v2"
                }
            }
        }

        stage('Deploy v2 (green)') {
            steps {
                sh "docker rm -f app-v2 || true"
                sh "docker run -d --name app-v2 -p ${GREEN_PORT}:5000 ${DOCKERHUB}/${APP}:v2"
            }
        }

        stage('Health check v2') {
            steps {
                script {
                    def healthy = false
                    for (int i = 0; i < 10; i++) {
                        def code = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:${GREEN_PORT}/health || true", returnStdout: true).trim()
                        def body = sh(script: "curl -s http://localhost:${GREEN_PORT}/health || true", returnStdout: true).trim()
                        if (code == "200" && body.contains('"status":"healthy"')) {
                            healthy = true
                            echo "v2 healthy on attempt ${i + 1}"
                            break
                        }
                        echo "waiting for v2... attempt ${i + 1}"
                        sleep 3
                    }
                    if (!healthy) {
                        error "v2 failed health check — aborting before traffic switch"
                    }
                }
            }
        }

        stage('Switch traffic to v2') {
            steps {
                sh "sudo sed -i 's#server 127.0.0.1:${BLUE_PORT};#server 127.0.0.1:${GREEN_PORT};#' ${UPSTREAM}"
                sh "sudo nginx -t"
                sh "sudo systemctl reload nginx"
                sh "curl -sf http://localhost/version | grep '\"version\":\"v2\"'"
            }
        }
    }

    post {
        success {
            echo "v2 live. app-v1 kept running as standby for rollback."
        }
        failure {
            echo "Pipeline failed — rolling traffic back to v1 and removing v2."
            sh "sudo sed -i 's#server 127.0.0.1:${GREEN_PORT};#server 127.0.0.1:${BLUE_PORT};#' ${UPSTREAM} || true"
            sh "sudo nginx -t || true"
            sh "sudo systemctl reload nginx || true"
            sh "docker rm -f app-v2 || true"
        }
    }
}
