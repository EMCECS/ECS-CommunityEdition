pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        skipDefaultCheckout()
        timeout(time: 1, unit: 'HOURS')
    }

    parameters {
        string(name: 'vsphere_server', defaultValue: '10.1.83.17', description: 'vSphere host')
        string(name: 'datastore', defaultValue: 'iSCSI-2', description: 'vSphere datastore')
        string(name: 'template', defaultValue: 'jenkins/jenkins-ecsce-template', description: 'VM template')
        string(name: 'resource_pool', defaultValue: 'Cisco UCS Cluster/Resources/Tests', description: 'vSphere resource pool')
        string(name: 'datacenter', defaultValue: 'Datacenter', description: 'vSphere datacenter')
        string(name: 'network_interface', defaultValue: 'CI Network', description: 'CI network interface')
        string(name: 'ecs_nodes', defaultValue: '1', description: 'Number of ECS nodes to be deployed')
    }

    environment {
        VSPHERE                   = credentials('vsphere_gotham')
        SSH                       = credentials('ssh_credentials')
        TF_VAR_vsphere_user       = "${VSPHERE_USR}"
        TF_VAR_vsphere_password   = "${VSPHERE_PSW}"
        TF_VAR_vsphere_server     = "${params.vsphere_server}"
        TF_VAR_datastore          = "${params.datastore}"
        TF_VAR_template           = "${params.template}"
        TF_VAR_resource_pool      = "${params.resource_pool}"
        TF_VAR_datacenter         = "${params.datacenter}"
        TF_VAR_network_interface  = "${params.network_interface}"
        TF_VAR_ecs_nodes          = "${params.ecs_nodes}"
        ANSIBLE_HOST_KEY_CHECKING = "False"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                  // Workaround until the GIT plugin automatically injects these environment variables
                  env.COMMIT_ID = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                  env.AUTHOR_NAME = sh(returnStdout: true, script: 'git show -s --pretty=%an HEAD').trim()
                  env.REPO_URL = sh(returnStdout: true, script: 'git remote get-url origin').trim()
                }
                sh 'printenv'
            }
        }
        stage('Install tools') {
            steps {
                script {
                    def tfHome = tool name: 'terraform-linux-x64', type: 'com.cloudbees.jenkins.plugins.customtools.CustomTool'
                    env.PATH = "${tfHome}:${env.PATH}"
                }
                sh 'terraform --version'
                sh 'ansible --version'
                sh 'terraform init tests'
            }
        }
        stage('Provision infrastructure') {
            steps {
                sh 'terraform plan -out=plan tests'
                sh 'terraform apply plan'
                sh 'terraform output -json > output.json'
            }
        }
        stage('Setup install node'){
            steps {
                  sh 'chmod +x ./tests/tf_to_hosts.py'
                  sh 'chmod +x ./tests/tf_to_ssh.py'
                  sh './tests/tf_to_hosts.py output.json hosts.ini'
                  sh "./tests/tf_to_ssh.py output.json ./ssh.sh $SSH_USR"
                  sh 'chmod +x ./ssh.sh'
                  sh 'cat output.json'
                  sh 'cat hosts.ini'
                  sh 'cat ./ssh.sh'
                  ansiblePlaybook \
                      playbook: 'tests/ansible/install_node_setup.yml',
                      inventory: 'hosts.ini',
                      extraVars: [
                          ansible_ssh_user: "$SSH_USR",
                          ansible_ssh_pass: "$SSH_PSW",
                          ansible_become_pass: "$SSH_PSW",
                          current_directory: "$WORKSPACE"
                      ]
              }
        }
        stage('Bootstrap install node'){
            steps {
                  sh './ssh.sh curl http://cache.gotham.local/registry.crt -o /tmp/registry.crt'
                  sh './ssh.sh /root/ecs/bootstrap.sh -n -v --build-from http://cache.gotham.local/alpine --vm-tools --proxy-cert /root/ecs/contrib/sslproxycert/emc_ssl.pem --proxy-endpoint cache.gotham.local:3128 -c /root/ecs/deploy.yml --centos-mirror cache.gotham.local --registry-cert /tmp/registry.crt --registry-endpoint cache.gotham.local:5000 --override-dns 10.1.83.19'
              }
        }
        stage('Reboot install node'){
            steps {
                  ansiblePlaybook \
                      playbook: 'tests/ansible/install_node_reboot.yml',
                      inventory: 'hosts.ini',
                      extraVars: [
                          ansible_ssh_user: "$SSH_USR",
                          ansible_ssh_pass: "$SSH_PSW",
                          ansible_become_pass: "$SSH_PSW",
                          current_directory: "$WORKSPACE"
                      ]
              }
        }
        stage('Deploy ECS'){
            steps {
                  sh './ssh.sh step1'
              }
        }
        stage('Configure ECS'){
            steps {
                  sh './ssh.sh step2'
              }
        }
    }

    post {
        always {
            echo 'Deprovision infrastructure'
            sh 'terraform destroy -force tests'
        }
        success {
            slackSend channel: 'ecs-community-edition', color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> passed: ${env.JOB_NAME} (<${env.REPO_URL}|${env.COMMIT_ID}>) by ${env.AUTHOR_NAME}"
        }
        failure {
            slackSend channel: 'ecs-community-edition', color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> failed: ${env.JOB_NAME} (<${env.REPO_URL}|${env.COMMIT_ID}>) by ${env.AUTHOR_NAME}"
        }
    }

}
