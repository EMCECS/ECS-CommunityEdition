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
        string(name: 'template', defaultValue: 'jenkins/ecsce-template', description: 'VM template')
        string(name: 'resource_pool', defaultValue: 'Cisco UCS Cluster/Resources/Tests', description: 'vSphere resource pool')
        string(name: 'datacenter', defaultValue: 'Datacenter', description: 'vSphere datacenter')
        string(name: 'network_interface', defaultValue: 'VM Network', description: 'VM network interface')
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
                sh 'printenv'
                script {
                  // Workaround until the GIT plugin automatically injects these environment variables
                  env.BRANCH_NAME = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                  env.COMMIT_ID = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                  env.AUTHOR_NAME = sh(returnStdout: true, script: 'git show -s --pretty=%an HEAD').trim()
                  env.REPO_URL = sh(returnStdout: true, script: 'git remote get-url origin').trim()
                }
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
            }
        }
        stage('Provision infrastructure') {
            steps {
                sh 'terraform plan -out=plan tests'
                sh 'terraform apply plan'
                sh 'terraform output -json > output.json'
            }
        }
        stage('Deploy ECS'){
            steps {
                  sh './tests/tf_to_hosts output.json hosts.ini'
                  ansiblePlaybook \
                      playbook: 'tests/ansible/install_node.yml',
                      inventory: 'hosts.ini',
                      extraVars: [
                          ansible_ssh_user: "$SSH_USR",
                          ansible_ssh_pass: "$SSH_PSW",
                          ansible_become_pass: "$SSH_PSW",
                          current_directory: "$WORKSPACE"
                      ],
                      extras: '-vvv'
              }
        }
    }

    post {
        always {
            echo 'Deprovision infrastructure'
            sh 'terraform destroy -force tests'
        }
        success {
            slackSend channel: 'ecs-community-edition', color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> passed: ${env.JOB_NAME}@${env.BRANCH_NAME} (<${env.REPO_URL}|${env.COMMIT_ID}>) by ${env.AUTHOR_NAME}"
        }
        failure {
            slackSend channel: 'ecs-community-edition', color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> failed: ${env.JOB_NAME}@${env.BRANCH_NAME} (<${env.REPO_URL}|${env.COMMIT_ID}>) by ${env.AUTHOR_NAME}"
        }
    }

}
