pipeline {
    agent any

    options{
        checkoutToSubdirectory('pytest')
        disableConcurrentBuilds()
    }

    environment {
      INMANTA_TEST_ENV="${env.WORKSPACE}/env"
    } 

    stages {
        stage('Test') {
            steps {
                sh 'rm -rf $INMANTA_TEST_ENV; python3 -m venv $INMANTA_TEST_ENV; $INMANTA_TEST_ENV/bin/python3 -m pip install -U  git+https://github.com/inmanta/inmanta.git; $INMANTA_TEST_ENV/bin/python3 -m pip install pytest'
                dir("pytest"){
                    sh "$INMANTA_TEST_ENV/bin/python3 -m pytest --junitxml=junit.xml -vvv tests --basetemp=${env.WORKSPACE}/tmp"
                }
            }       
        }
    }

    post {
        always {
            junit 'pytest/junit.xml'
        }
    }
}