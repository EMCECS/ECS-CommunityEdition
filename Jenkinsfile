pipeline {
    agent any

    environment {
        TF_VAR_vsphere_user       = "${params.vsphere_user}"
        TF_VAR_vsphere_password   = "${params.vsphere_password}"
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
                          ansible_ssh_user: "${params.ssh_user}",
                          ansible_ssh_pass: "${params.ssh_pass}",
                          ansible_become_pass: "${params.ssh_pass}",
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
    }

}
