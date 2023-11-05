pipeline {
    agent any

    stages {
        stage('Verify folder') {
            steps {
                echo workspace
                // cleanWs()
                // sh label: 'checkout', script: 'git clone https://github.com/Gthr541254/palm-tree .'
            }
        }
        stage('Setup') {
            steps {
                dir ('.venv') {
                    deleteDir()
                }
                sh label: 'Run make venv', script: 'make venv'
                sh label: 'Run make install', script: '''
                    source .venv/bin/activate
                    pip install -r requirements.txt
                    deactivate
                '''
            }
        }
/*
        //These are already done at gh
        stage('Test Model') {
            steps {
                sh label: 'Run make model-test', script: '''
                    source .venv/bin/activate
                    make model-test
                '''
            }
        }
        stage('Test API') {
            steps {
                sh label: 'Run make api-test', script: '''
                    source .venv/bin/activate
                    make api-test
                '''
            }
        }
        stage('Stress Test') {
            steps {
                sh label: 'Kill build server', script: 'kill "$(ps ax | grep uvicorn | grep 8001 | awk \'{split($0,a," "); print a[1]}\' | head -n 1)" || true'
                
                sh label: 'Run build server', script: '''
                    source .venv/bin/activate
                    uvicorn challenge:app --host 0.0.0.0 --port 8001 &
                    sleep 10s
                    make stress-test
                '''
                
                sh label: 'Kill build server', script: 'kill "$(ps ax | grep uvicorn | grep 8001 | awk \'{split($0,a," "); print a[1]}\' | head -n 1)" || true'
            }
        }
*/
        stage('Package') {
            steps {
                // sh label: 'Manual', script: 'sudo apt install zip unzip'
                sh label: 'Remove dev files', script: 'find . | grep -E "(/__pycache__$|\\.pyc$|\\.pyo$)" | xargs rm -rf'
                sh label: 'Remove previous artifact', script: 'rm -rf palmtree.zip'
                sh label: 'Package artifact', script: 'zip --symlinks -r1 palmtree.zip challenge/model.py challenge/api.py challenge/model.pkl challenge/__init__.py .venv'
                // tag artifact with BUILD_NUMBER and submit artifact to permanent storage?
            }
        }
        stage('Deploy') {
            steps {
                sh label: 'Kill production server', script: 'kill "$(ps ax | grep uvicorn | grep 8000 | awk \'{split($0,a," "); print a[1]}\' | head -n 1)" || true'
                dir('/srv/palm-tree') {
                    sh label: 'Clean', script: 'rm -rf ../palm-tree/*'
                    sh label: 'Install artifact', script: "unzip -o ${WORKSPACE}/palmtree.zip"
                    withEnv(['JENKINS_NODE_COOKIE=do_not_kill']) {
                        sh label: 'Run production server', script: '''
                            source .venv/bin/activate
                            uvicorn challenge:app --host 0.0.0.0 --port 8000 & disown
                            sleep 10s
                        '''
                    }
                }
                // post deploy testing, could also send an email
                sh label: 'Run make stress-test', script: '''
                    source .venv/bin/activate
                    pip install -r requirements-test.txt
                    make stress-test-prod
                '''
            }
        }
        stage('Recover Space') {
            steps {
                cleanWs()
            }
        }
    }
}
