// Nasty use of conditionals to make this work
// https://issues.jenkins-ci.org/browse/JENKINS-42643
String upstreamproject = BRANCH_NAME == "master" ? "inmanta-core/master" : ""

pipeline {
    agent any

    options{
        checkoutToSubdirectory('pytest')
        disableConcurrentBuilds()
    }

    triggers { 
        upstream upstreamproject
    }

    environment {
      INMANTA_TEST_ENV="${env.WORKSPACE}/env"
    } 

    stages {
        stage('Test') {
            steps {
                sh 'rm -rf $INMANTA_TEST_ENV; python3 -m venv $INMANTA_TEST_ENV; $INMANTA_TEST_ENV/bin/python3 -m pip install -U -c https://raw.githubusercontent.com/inmanta/inmanta/master/requirements.txt git+https://github.com/inmanta/inmanta.git; $INMANTA_TEST_ENV/bin/python3 -m pip install ./pytest'
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