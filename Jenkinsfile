// Nasty use of conditionals to make this work
// https://issues.jenkins-ci.org/browse/JENKINS-42643
String upstreamproject = BRANCH_NAME == "master" ? "core/inmanta-core/master" : ""

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
                sh 'rm -rf $INMANTA_TEST_ENV; python3 -m venv $INMANTA_TEST_ENV; $INMANTA_TEST_ENV/bin/python3 -m pip install ./pytest; $INMANTA_TEST_ENV/bin/python3 -m pip install -U -c https://raw.githubusercontent.com/inmanta/inmanta/master/requirements.txt git+https://github.com/inmanta/inmanta.git -r ./pytest/requirements.txt'

                dir("pytest"){
                    sh "$INMANTA_TEST_ENV/bin/python3 -m pytest --junitxml=junit.xml -vvv tests --basetemp=${env.WORKSPACE}/tmp"
                }
            }
        }
        stage("code linting"){
            steps{
                script{
                    dir("pytest"){
                        sh'''
                        $INMANTA_TEST_ENV/bin/flake8 examples pytest_inmanta tests
                        '''
                    }
                }
            }
        }

        stage("release") {
            when {
                expression { return BRANCH_NAME == "master" }
            }
            steps {
                dir("pytest"){
                    withCredentials([usernamePassword(credentialsId: 'devpi-user', usernameVariable: 'DEVPI_USER', passwordVariable: 'DEVPI_PASS')]) {
                    sh'''
                        "/opt/devpi-client/venv/bin/devpi" use https://artifacts.internal.inmanta.com/inmanta/dev/

                        "/opt/devpi-client/venv/bin/devpi" login "${DEVPI_USER}" --password="${DEVPI_PASS}"

                        rm -f dist/*

                        "${WORKSPACE}/env/bin/python3" setup.py egg_info -Db ".dev$(date +'%Y%m%d%H%M%S' --utc)" sdist

                        "/opt/devpi-client/venv/bin/devpi" upload dist/*.dev*

                        "/opt/devpi-client/venv/bin/devpi" logoff
                    '''
                    }
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
