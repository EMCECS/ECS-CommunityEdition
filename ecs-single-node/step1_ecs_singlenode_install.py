#!/usr/bin/env python
# An installation program for ECS SW 2.0 Single Data node
import argparse

import subprocess
import logging
import logging.config
import sys
import os

import settings
import step2_update_container


# Logging Initialization
logging.config.dictConfig(settings.ECS_SINGLENODE_LOGGING)
logger = logging.getLogger("root")


def yum_func():
    """
    Performs CentOS update
    """
    logger.info("Performing a yum update.")

    try:
        subprocess.call(["yum", "update", "-y"])

    except Exception as ex:
        logger.exception(ex)
        # Abort Program
        # http://stackoverflow.com/questions/73663/terminating-a-python-script
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def package_install_func():
    """
    Installs required packages
    """
    try:

        yum = "yum"
        yum_arg = "install"
        yum_package_wget = "wget"
        yum_package_tar = "tar"
        yum_auto_install = "-y"

        logger.info("Performing installation of the following package: {} .".format(yum_package_wget))
        subprocess.call([yum, yum_arg, yum_package_wget, yum_auto_install])

        logger.info("Performing installation of the following package: {} .".format(yum_package_tar))
        subprocess.call([yum, yum_arg, yum_package_tar, yum_auto_install])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def update_selinux_os_configuration():
    """
    Update the selinux permissions to permissive
    """

    logger.info("Updating SELinux to Permissive mode.")
    subprocess.call(["setenforce", "0"])


def docker_install_func():
    """
    Downloads, Install and starts the service for the  Supported Docker Version  1.4.1
    """
    try:

        docker_yum = "yum"
        docker_yum_arg = "remove"
        docker_name = "docker"
        docker_package_auto = "-y"

        # Removes previous Docker installations
        logger.info("Removing Docker Packages.")
        subprocess.call([docker_yum, docker_yum_arg, docker_name, docker_package_auto])

        docker_wget = "wget"
        docker_url = "http://cbs.centos.org/kojifiles/packages/docker/1.4.1/2.el7/x86_64/docker-1.4.1-2.el7.x86_64.rpm"

        # Gets the docker package
        logger.info("Downloading the Docker Package.")
        subprocess.call([docker_wget, docker_url])

        docker_yum = "yum"
        docker_yum_arg = "install"
        docker_package = "docker-1.4.1-2.el7.x86_64.rpm"
        docker_package_auto_install = "-y"

        # Installs the docker package
        logger.info("Installing the Docker Package.")
        subprocess.call([docker_yum, docker_yum_arg, docker_package, docker_package_auto_install])

        docker_service = "service"
        docker_service_name = "docker"
        docker_service_action = "start"

        # Starts the Docker Service
        logger.info("Starting the Docker Service.")
        subprocess.call([docker_service, docker_service_name, docker_service_action])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def prep_file_func():
    """
    Downloads and configures the preparation file
    """
    try:

        wget = "wget"
        url = "https://emccodevmstore001.blob.core.windows.net/test/additional_prep.sh"

        # Gets the prep. file
        logger.info("Downloading the additional_prep file.")
        subprocess.call([wget, url])

        chmod = "chmod"
        chmod_arg = "777"
        file_name = "additional_prep.sh"
        logger.info("Changing the additional_prep.sh file permissions.")
        subprocess.call([chmod, chmod_arg, file_name])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def docker_cleanup_old_images():
    """
    Clean up images and containers from the Host Docker images repository
    sudo docker rm -f $(sudo docker ps -a -q) 2>/dev/null
    sudo docker rmi -f $(sudo docker images -q) 2>/dev/null
    """
    try:

        logger.info("Clean up Docker containers and images from the Host")

        os.system("docker rm -f $(docker ps -a -q) 2>/dev/null")
        os.system("docker rmi -f $(docker images -q) 2>/dev/null")

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def docker_pull_func():
    """
    Getting the ECS Docker image from DockerHub. Using Docker Pull
    """
    try:

        docker = "docker"
        docker_arg = "pull"
        docker_file = "emccode/ecsobjectsw:v2.0"
        logger.info("Executing a Docker Pull for image {}".format(docker_file))
        subprocess.call([docker, docker_arg, docker_file])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def network_file_func():
    """
    Creates and configures the the network configuration file
    """

    try:

        # Get the IP address
        ip_address = subprocess.check_output(['hostname', '-i']).rstrip('\r\n')

        # Get the hostname
        hostname = subprocess.check_output(['hostname']).rstrip('\r\n')

        # Create the Network.json file
        logger.info("Creating the Network.json file with Hostname: {} and IP: {}:".format(hostname, ip_address))
        logger.info(
            "{\"private_interface_name\":\"eth0\",\"public_interface_name\":\"eth0\",\"hostname\":\"%s\",\"public_ip\":\"%s\"}" % (
                hostname, ip_address))

        # Open a file
        network_file = open("network.json", "wb")

        network_string = "{\"private_interface_name\":\"eth0\",\"public_interface_name\":\"eth0\",\"hostname\":\"%s\",\"public_ip\":\"%s\"}" % (
            hostname, ip_address)

        network_file.write(network_string)

        # Close file
        network_file.close()

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def seeds_file_func():
    """
    Creates and configures the seeds file
    """

    try:
        # Get the IP address
        ip_address = subprocess.check_output(['hostname', '-i']).rstrip('\r\n')

        logger.info("Creating the seeds file with IP address: {} ".format(ip_address))
        # Open a file
        seeds_file = open("seeds", "wb")

        seeds_file.write("%s" % ip_address)

        # Close file
        seeds_file.close()

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()



def prepare_data_disk_func(disks):
    """
    Prepare the data disk for usage. This includes format, and mount
    """

    try:

        # echo -e "o\nn\np\n1\n\n\nw" | fdisk /dev/sdc

        for index, disk in enumerate(disks):
            disk_path = "/dev/{}".format(disk)

            logger.info("Partitioning the disk '{}'".format(disk_path))
            ps = subprocess.Popen(["echo", "-e", "\"o\nn\np\n1\n\n\nw\""], stdout=subprocess.PIPE)
            output = subprocess.check_output(["fdisk", disk_path], stdin=ps.stdout)
            ps.wait()
            # os.system("echo -e o\nn\np\n1\n\n\nw | fdisk /dev/sdc")

            device_name = disk_path + "1"
            # Make File Filesystem in attached Volume
            logger.info("Make File filesystem in '{}'".format(device_name))
            subprocess.call(["mkfs.xfs", "-f", device_name])

            uuid_name = "uuid-{}".format(index + 1)
            # mkdir -p /ecs/uuid-1
            logger.info("Make /ecs/{} Directory in attached Volume".format(uuid_name))
            subprocess.call(["mkdir", "-p", "/ecs/{}".format(uuid_name)])

            # mount /dev/sdc1 /ecs/uuid-1
            logger.info("Mount attached /dev{} to /ecs/{} volume.".format(device_name, uuid_name))
            subprocess.call(["mount", device_name, "/ecs/{}".format(uuid_name)])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()



def run_additional_prep_file_func(disks):
    """
    Execute the additional preparation script
    """

    try:
        prep_file_name = "./additional_prep.sh"

        for disk in disks:
            device_name = "/dev/{}1".format(disk)
            # Gets the prep. file
            logger.info("Executing the additional preparation script in '{}'".format(device_name))
            subprocess.call([prep_file_name, device_name])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def directory_files_conf_func():
    '''
    Configure and create required directories and copy files into them.
    '''
    try:
        # chown -R 444 /ecs
        logger.info("Changing /ecs folder permissions.")
        subprocess.call(["chown", "-R", "444", "/ecs"])

        # mkdir -p /host/data
        logger.info("Creating the /host/data directory.")
        subprocess.call(["mkdir", "-p", "/host/data"])

        # mkdir -p /host/files
        logger.info("Creating the /host/files directory.")
        subprocess.call(["mkdir", "-p", "/host/files"])

        # cp network.json /host/data
        logger.info("Copying network.json to /host/data.")
        subprocess.call(["cp", "network.json", "/host/data"])

        # cp seeds /host/files
        logger.info("Copying seeds file to /host/files.")
        subprocess.call(["cp", "seeds", "/host/files"])

        # chown -R 444 /host
        logger.info("Changing permissions to the /host folder.")
        subprocess.call(["chown", "-R", "444", "/host"])

        # mkdir -p /var/log/vipr/emcvipr-object
        logger.info("Creating the /var/log/vipr/emcvipr-object directory.")
        subprocess.call(["mkdir", "-p", "/var/log/vipr/emcvipr-object"])

        # chown 444 /var/log/vipr/emcvipr-object
        logger.info("Changing permissions to /var/log/vipr/emcvipr-object directory.")
        subprocess.call(["chown", "444", "/var/log/vipr/emcvipr-object"])

        # mkdir /data
        logger.info("Creating the /data folder.")
        subprocess.call(["mkdir", "/data"])

        # chown 444 /data
        logger.info("Changing permissions to /data folder.")
        subprocess.call(["chown","-R", "444", "/data"])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def set_docker_configuration_func():
    '''
    Sets Docker Configuration and Restarts the Service
    '''

    try:

        # mv /etc/sysconfig/docker /etc/sysconfig/dockerold
        logger.info("Move files /etc/sysconfig/docker to /etc/sysconfig/dockerold.")
        subprocess.call(["mv", "/etc/sysconfig/docker", "/etc/sysconfig/dockerold"])

        # service docker restart
        logger.info("Restart Docker service.")
        subprocess.call(["service", "docker", "restart"])

        # service docker status
        logger.info("Check Docker service status.")
        subprocess.call(["service", "docker", "status"])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def execute_docker_func():
    '''
    Execute Docker Container
    '''
    try:

        # docker run -d -e SS_GENCONFIG=1 -v /ecs:/disks -v /host:/host -v /var/log/vipr/emcvipr-object:/opt/storageos/logs -v /data:/data:rw --net=host emccode/ecsstandalone:v2.0
        logger.info("Execute the Docker Container.")
        subprocess.call(["docker", "run", "-d", "-e", "SS_GENCONFIG=1", "-v", "/ecs:/disks", "-v", "/host:/host", "-v",
                         "/var/log/vipr/emcvipr-object:/opt/storageos/logs", "-v", "/data:/data:rw", "--net=host",
                         "--name=ecsstandalone",
                         "emccode/ecsobjectsw:v2.0"])

        # docker ps
        logger.info("Check the Docker processes.")
        subprocess.call(["docker", "ps"])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def cmdline(command):
    """
    Function that executes a Shell command and returns the output
    :param command: Shell command to be passed in
    :return: Returns a string with the Shell command output
    """
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        shell=True
    )
    return process.communicate()[0]


# Main Execution
def main():
    import os

    if os.getuid() != 0:
        print("You need to run it as root.")
        sys.exit(3)

    parser = argparse.ArgumentParser(
        description='EMC\'s Elastic Cloud Storage 2.0 Software in a Docker container installation script. ')
    parser.add_argument('--disks', nargs='+', help='The disk(s) name(s) to be prepared. Example: sda sdb sdc',
                        required=True)
    args = parser.parse_args()

    # Check that the Selected Disks have not been initialized and can be used
    for disk in args.disks:
        if not os.path.exists("/dev/{}".format(disk)):
            print "Disk '/dev/{}' does not exist".format(disk)
            sys.exit(4)

        disk_ready = cmdline("fdisk -l /dev/{} | grep \"Disk label type:\"".format(disk))
        if disk_ready:
            print "Please check that Disk: {} is not formatted (fdisk -l).".format(disk)
            sys.exit(5)
        else:
            print "Disk {} checked. Ready for the installation.".format(disk)


    # Step 1 : Configuration of Host Machine to run the ECS Docker Container
    logger.info("Staring Step 1: Configuration of Host Machine to run the ECS Docker Container.")

    yum_func()
    package_install_func()
    update_selinux_os_configuration()
    docker_install_func()
    prep_file_func()
    docker_pull_func()
    network_file_func()
    seeds_file_func()
    prepare_data_disk_func(args.disks)
    run_additional_prep_file_func(args.disks)
    directory_files_conf_func()
    set_docker_configuration_func()
    execute_docker_func()
    logger.info(
        "Step 1 Completed.  Navigate to the administrator website that is available from any of the ECS data nodes. \
        The ECS administrative portal can be accessed from port 443. For example: https://ecs-node-external-ip-address. \
        The website may take a few minutes to become available.")


if __name__ == "__main__":
    main()
