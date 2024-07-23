pipeline {
    agent any

    environment {
        // 환경 변수 설정
        DOCKER_IMAGE_NAME = 'my-django-app' // Docker 이미지 이름
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        AWS_EC2_SERVER = 'http://13.209.101.185/'
        EMAIL_RECIPIENT = 'krozv.code@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                // Git 저장소에서 코드 체크아웃
                git branch: 'deploy', url: 'https://github.com/Maumkkut/maumkkut_Backend.git'
            }
        }

        stage('Build') {
            steps {
                // Docker 이미지 빌드
                script {
                    docker.build(DOCKER_IMAGE_NAME, '.')
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Django 테스트 실행 (pytest를 사용하여 테스트)
                    docker.image(DOCKER_IMAGE_NAME).inside {
                        sh 'pytest' // pytest를 사용하여 테스트
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Docker Compose를 사용하여 배포
                    sh "docker-compose -f ${DOCKER_COMPOSE_FILE} up -d"
                }
            }
        }
    }

    post {
        success {
            // 성공 시 이메일 알림
            mail to: EMAIL_RECIPIENT,
                 subject: "Jenkins Pipeline Success",
                 body: "The Jenkins pipeline has completed successfully.\n\nCheck the Jenkins build at: ${env.BUILD_URL}"
        }
        failure {
            // 실패 시 이메일 알림
            mail to: EMAIL_RECIPIENT,
                 subject: "Jenkins Pipeline Failure",
                 body: "The Jenkins pipeline has failed.\n\nCheck the Jenkins build at: ${env.BUILD_URL}"
        }
    }
}
