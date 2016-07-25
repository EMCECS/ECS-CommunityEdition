#!/usr/bin/env python
# An installation program for ECS SW 2.2.1 Multiple Data nodes
import argparse
import getopt
import subprocess
from subprocess import PIPE, Popen
import logging
import logging.config
import sys
import socket
import os
import time
import settings
import re
import StringIO

# Logging Initialization
logging.config.dictConfig(settings.ECS_SINGLENODE_LOGGING)
logger = logging.getLogger("root")

DockerCommandLineFlags=[]

def yum_update_func():
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
        yum_package_docker = "docker"
        yum_package_xfsprogs = "xfsprogs"
        yum_auto_install = "-y"

        logger.info("Performing installation of the following package: {} .".format(yum_package_wget))
        subprocess.call([yum, yum_arg, yum_package_wget, yum_auto_install])

        logger.info("Performing installation of the following package: {} .".format(yum_package_tar))
        subprocess.call([yum, yum_arg, yum_package_tar, yum_auto_install])

        logger.info("Performing installation of the following package: {} .".format(yum_package_xfsprogs))
        subprocess.call([yum, yum_arg, yum_package_xfsprogs, yum_auto_install])

        logger.info("Performing installation of the following package: {} .".format(yum_package_docker))
        subprocess.call([yum, yum_arg, yum_package_docker, yum_auto_install])

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



def prep_file_func():
    """
    Downloads and configures the preparation file
    """

    file_name = "additional_prep.sh"

    try:
        chmod = "chmod"
        chmod_arg = "777"
        logger.info("Changing the additional_prep.sh file permissions.")
        subprocess.call([chmod, chmod_arg, file_name])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def docker_load_image(imagefile):
    """
    Load the specified docker image file.
    """
    try:
        logger.info("Loading docker image file %s" % imagefile)
        res = subprocess.check_output("docker load -i \"%s\"" % imagefile, shell=True)
    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Error loading docker image file %s" % imagefile)
        sys.exit(13)



def docker_cleanup_old_images():
    """
    Clean up images and containers from the Host Docker images repository
    sudo docker rm -f $(sudo docker ps -a -q) 2>/dev/null
    sudo docker rmi -f $(sudo docker images -q) 2>/dev/null
    """
    try:

        logger.info("Clean up Docker containers and images from the Host")

        os.system("docker rm -f $(docker ps -a -q) 2>/dev/null")
        # os.system("docker rmi -f $(docker images -q) 2>/dev/null")

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def docker_pull_func(docker_image_name,proxy=None):
    """
    Getting the ECS Docker image from DockerHub. Using Docker Pull
    """
    try:
        if proxy!=None:
            os.system("echo http_proxy=" + proxy +" >>/etc/sysconfig/docker")
            os.system("echo https_proxy=" + proxy +" >>/etc/sysconfig/docker")
            os.system("echo HTTP_PROXY=" + proxy +" >>/etc/sysconfig/docker")
            os.system("echo HTTPS_PROXY=" + proxy +" >>/etc/sysconfig/docker")
        
    
        #Start docker service
        subprocess.call(["service","docker","start"])

        docker = "docker"
        docker_arg = "pull"
        logger.info("Executing a Docker Pull for image {}".format(docker_image_name))
        subprocess.call([docker, docker_arg, docker_image_name])
        command_line = [docker, docker_arg, docker_image_name]
        command_line[1:1] = DockerCommandLineFlags
        subprocess.call(command_line)

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def network_file_func(ethadapter):
    """
    Creates and configures the the network configuration file
    """

    try:

        # Get the IP address
        ip_address = subprocess.check_output(['hostname', '-i']).rstrip('\r\n')

        # Get the hostname
        hostname = subprocess.check_output(['hostname']).rstrip('\r\n')

        # Create the Network.json file
        logger.info("Creating the Network.json file with Ethernet Adapter: {} Hostname: {} and IP: {}:".format(ethadapter, hostname, ip_address))
        logger.info(
            "{\"private_interface_name\":\"%s\",\"public_interface_name\":\"%s\",\"hostname\":\"%s\",\"data_ip\":\"%s\",\"mgmt_ip\":\"%s\",\"replication_ip\":\"%s\"}" % (
                ethadapter, ethadapter, hostname, ip_address, ip_address, ip_address))

        # Open a file
        network_file = open("network.json", "wb")

        network_string = "{\"private_interface_name\":\"%s\",\"public_interface_name\":\"%s\",\"hostname\":\"%s\",\"data_ip\":\"%s\",\"mgmt_ip\":\"%s\",\"replication_ip\":\"%s\"}" % (
            ethadapter, ethadapter, hostname, ip_address, ip_address, ip_address)

        network_file.write(network_string)

        # Close file
        network_file.close()

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def seeds_file_func(ips):
    """
    Creates and configures the seeds file. This file contains the list of the ECS Nodes' IPs
    """

    try:

        logger.info("Creating the seeds.example file with IP addresses: {} ".format(ips))
        # Open a file
        seeds_file = open("seeds", "wb")

        seeds_file.write("%s\n" % ','.join(ips))

        # Close file
        seeds_file.close()

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def cmdline(command):
    """
    Function that executes a Shell command and returns the output
    :param command: Shell command to be passed in
    :return: Returns a string with the Shell command output
    """
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]


def hosts_file_func(ips, hostnames):
    """
    Updates the /etc/hosts file with the IP-Hostname of each one of the DataNodes in the cluster
    :rtype : null
    """

    try:
        logger.info("Updating the /etc/hosts file with the IP-Hostname of each one of the DataNodes in the cluster")
        # Open a file
        seeds_file = open("/etc/hosts", "a")

        for index in range(len(ips)):
            # Check if the hosts file has the entries
            hostname_exists = cmdline("cat /etc/hosts | grep %s" % ips[index])
            if not hostname_exists:
                print "(Adding) Hostname does not Exist: %s    %s" % (ips[index], hostnames[index])
                seeds_file.write("%s    %s\n" % (ips[index], hostnames[index]))
            else:
                print "(Ignoring) Hostname Exists: %s" % hostname_exists
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

            uuid_name = uuid_filename(device_name)
            # mkdir -p /ecs/uuid-[uuid]
            logger.info("Make /ecs/{} Directory in attached Volume".format(uuid_name))
            subprocess.call(["mkdir", "-p", "/ecs/{}".format(uuid_name)])

            # mount /dev/sdc1 /ecs/uuid-[uuid]
            logger.info("Mount attached {} to /ecs/{} volume.".format(device_name, uuid_name))
            subprocess.call(["mount", device_name, "/ecs/{}".format(uuid_name), "-o", "noatime,seclabel,attr2,inode64,noquota"])

            # add entry to fstab if not pre-existing
            fstab = "/etc/fstab"
            p = subprocess.Popen(["grep", device_name, fstab], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode == 0:
                logger.info("Data disk already entered in fs table")
            elif p.returncode == 1:
                with open("/etc/fstab", 'a') as file:
                    file.write("{} /ecs/{} xfs rw,noatime,seclabel,attr2,inode64,noquota 0 0\n".format(device_name, uuid_name) )
            else:
                logger.info("Error in checking filesystem table: {}".format(err))

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()

def uuid_filename(device_name):
    blkd_id_process = subprocess.Popen(["blkid", "-s", "UUID", "-o", "value", device_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = blkd_id_process.communicate()
    return "uuid-{}".format(stdout.strip())


def clean_data_disk_func(disks):
    """
    Un-mounts created disks, removes files and directories created by ECS
    """

    try:

        for index, disk in enumerate(disks):
            disk_path = "/dev/{}".format(disk)

            device_name = disk_path + "1"
            uuid_name = uuid_filename(device_name)
            uuid_name = "uuid-{}".format(index + 1)

            # umount /dev/sdc1 /ecs/uuid-[uuid]
            logger.info("Umount attached /dev{} to /ecs/{} volume.".format(device_name, uuid_name))
            subprocess.call(["umount", device_name, "/ecs/{}".format(uuid_name)])

            # rm -rf /ecs/uuid-[uuid]
            logger.info("Remove /ecs/{} Directory in attached Volume".format(uuid_name))
            subprocess.call(["rm", "-rf", "/ecs/{}".format(uuid_name)])

            logger.info("Remove {} from fs table".format(disk_path))
            fstab = "/etc/fstab"
            f = open(fstab, "r+")
            rl = f.readlines()
            f.seek(0)
            for ln in rl:
                if not disk_path in ln:
                    f.write(ln)
            f.truncate()
            f.close()

        # sudo rm -rf /data/*
        logger.info("Remove /data/* Directory in attached Volume")
        subprocess.call(["rm", "-rf", "/data"])

        # sudo rm -rf /var/log/vipr/emcvipr-object/*
        logger.info("Remove /var/log/vipr/emcvipr-object/* Directory ")
        subprocess.call(["rm", "-rf", "/var/log/vipr/emcvipr-object/*"])

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

        chmod = "chmod"
        chmod_arg = "0755"
        logger.info("Setting the additional preparation script permissions.")
        subprocess.call([chmod, chmod_arg, prep_file_name])

        for disk in disks:
            device_name = "/dev/{}1".format(disk)
            # Gets the prep. file
            logger.info("Executing the additional preparation script in '{}'".format(device_name))
            subprocess.call([prep_file_name, device_name])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def precheck():
    """
    Checks for common errors like the /data directory not being empty before install.
    """
    logger.info("PRECHECK: Check that /data directory is clean")
    data_dir = "/data"
    if os.path.exists(data_dir):
        if not os.path.isdir(data_dir):
            logger.fatal("The path %s is a file.  Please delete it.  It is used as a directory to store "
                         "configuration information for ECS." % data_dir)
            sys.exit(1)
        if len(os.listdir(data_dir)) > 0:
            logger.fatal("The directory %s is not empty.  Please remove or empty it before installing ECS.  It is "
                         "used as a directory to store local configuration information for ECS" % data_dir)
            sys.exit(1)


def directory_files_conf_func():
    """
    Configure and create required directories and copy files into them.
    """
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
        subprocess.call(["chown", "-R", "444", "/data"])

        # Put flag that we're really community edition so SS startup doesn't think this
        # is developer sanity build.
        logger.info("Marking node as ECS Community Edition (for bootstrap scripts)")
        subprocess.call(["touch", "/data/is_community_edition"])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def set_docker_configuration_func():
    '''
    Sets Docker Configuration and Restarts the Service
    '''

    try:

        # cp /etc/sysconfig/docker /etc/sysconfig/dockerold
        logger.info("Copy files /etc/sysconfig/docker to /etc/sysconfig/dockerold.")
        subprocess.call(["cp", "/etc/sysconfig/docker", "/etc/sysconfig/dockerold"])

        # service docker restart
        logger.info("Restart Docker service.")
        subprocess.call(["service", "docker", "restart"])

        # service docker status
        logger.info("Check Docker service status.")
        subprocess.call(["service", "docker", "status"])

        logger.info("Set container to start on boot.")
        subprocess.call(["systemctl", "enable", "docker.service"])
        os.system("echo \"docker start ecsmultinode\" >>/etc/rc.local")
        os.system("chmod +x /etc/rc.d/rc.local")

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def execute_docker_func(docker_image_name, use_urandom=False,proxy=None):
    """
    Execute Docker Container
    """
    try:

        # docker run -d -e SS_GENCONFIG=1 -v /ecs:/dae -v /host:/host -v /var/log/vipr/emcvipr-object:/var/log -v /data:/data:rw --net=host emccorp/ecs-software --name=ecsmultinode
        docker_command = ["docker", "run", "-d", "-e", "SS_GENCONFIG=1"]
        if proxy!=None:
            docker_command.extend(["-e", "HTTP_PROXY="+proxy, "-e", "HTTPS_PROXY="+proxy])
       
        if use_urandom:
            docker_command.extend(["-v", "/dev/urandom:/dev/random"])
        docker_command.extend(["-v", "/ecs:/dae", "-v", "/host:/host", "-v", "/var/log/vipr/emcvipr-object:/var/log", "-v", "/data:/data:rw", "--net=host",
                         "--name=ecsmultinode", "{}".format(docker_image_name)])
        logger.info("Execute the Docker Container.")
        docker_command[1:1] = DockerCommandLineFlags
        logger.info(" ".join(docker_command))
        subprocess.call(docker_command)

        # docker ps
        logger.info("Check the Docker processes.")
        subprocess.call(["docker", "ps"])

    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log")


def valid_ip(address):
    """
    Functions that checks for valid IPs
    :param address: IP Address
    :return: True or False
    """
    try:
        socket.inet_aton(address)
        return True
    except:
        return False

def get_first(iterable, default=None):
    """
    Returns the first item from a list
    :rtype : object
    """
    if iterable:
        for item in iterable:
            return item
    return default


def modify_container_conf_func(no_internet):
    try:
        #
        # Reduce number of partitions for each table from 128 to 32 to reduce memory/threads
        #
        logger.info("Backup common-object properties file")
        os.system(
            "docker exec -t  ecsmultinode cp /opt/storageos/conf/common.object.properties /opt/storageos/conf/common.object.properties.old")

        logger.info("Copy common-object properties files to host")
        os.system(
            "docker exec -t ecsmultinode cp /opt/storageos/conf/common.object.properties /host/common.object.properties1")

        logger.info("Modify Directory Table config for multi node")
        os.system(
            "sed --expression='s/object.NumDirectoriesPerCoSForSystemDT=128/object.NumDirectoriesPerCoSForSystemDT=32/' --expression='s/object.NumDirectoriesPerCoSForUserDT=128/object.NumDirectoriesPerCoSForUserDT=32/' < /host/common.object.properties1 > /host/common.object.properties")

        logger.info("Copy modified files to container")
        os.system(
            "docker exec -t  ecsmultinode cp /host/common.object.properties /opt/storageos/conf/common.object.properties")

        #
        # Change Storage Server block allocation watermarks to deal with smaller storage footprints
        # (NOTE: if you have 100+TB of storage you can comment this out)
        #
        logger.info("Backup ssm properties file")
        os.system(
            "docker exec -t  ecsmultinode cp /opt/storageos/conf/ssm.object.properties /opt/storageos/conf/ssm.object.properties.old")

        logger.info("Copy ssm properties files to host")
        os.system(
            "docker exec -t ecsmultinode cp /opt/storageos/conf/ssm.object.properties /host/ssm.object.properties1")

        logger.info("Modify SSM config for multi node")
        os.system(
            "sed --expression='s/object.freeBlocksHighWatermarkLevels=1000,200/object.freeBlocksHighWatermarkLevels=100,50/' --expression='s/object.freeBlocksLowWatermarkLevels=0,100/object.freeBlocksLowWatermarkLevels=0,20/' < /host/ssm.object.properties1 > /host/ssm.object.properties")

        logger.info("Copy modified files to container")
        os.system(
            "docker exec -t  ecsmultinode cp /host/ssm.object.properties /opt/storageos/conf/ssm.object.properties")

        if not no_internet:
            logger.info("Adding python setuptools to container")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode curl -OLk https://bootstrap.pypa.io/ez_setup.py")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode python ez_setup.py --insecure")

            logger.info("Adding python requests library to container")
            os.system(
                "docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode curl -OLk https://github.com/kennethreitz/requests/tarball/master")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode tar zxvf master -C /tmp")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t -i ecsmultinode bash -c \"cd /tmp/kennethreitz-requests-* && python setup.py install\"")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode curl -OLk https://bootstrap.pypa.io/ez_setup.py")
            logger.info("Cleaning up python packages")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode rm master")
            os.system("docker "+' '.join(DockerCommandLineFlags)+" exec -t  ecsmultinode rm setuptools-*.zip")

        # Flush vNest to clear data and restart.
        logger.info("Flush VNeST data")
        os.system("docker exec -t ecsmultinode rm -rf /data/vnest/vnest-main/*")

        logger.info("Stop container")
        os.system("docker stop ecsmultinode")

        logger.info("Start container")
        os.system("docker start ecsmultinode")

        logger.info("Clean up local files")
        os.system("rm -rf /host/common.object.properties*")
        os.system("rm -rf /host/ssm.object.properties*")


    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def getAuthToken(ECSNode, User, Password):
    """
    Poll to see if Auth Service is active.
    """
    logger.info("Waiting on Authentication Service. This may take several minutes.")
    for i in range (0,60):
        time.sleep(30)
        try:
            curlCommand = "curl -i -k https://%s:4443/login -u %s:%s" % (ECSNode, User, Password)
            print ("Executing getAuthToken: %s " % curlCommand)
            res=subprocess.check_output(curlCommand, shell=True)
            authTokenPattern = "X-SDS-AUTH-TOKEN:(.*)\r\n"
            searchObject=re.search(authTokenPattern,res)
            assert searchObject, "Get Auth Token failed"
            print("Auth Token %s" % searchObject.group(1))
            return searchObject.group(1)
        except Exception as ex:
            logger.info("Problem reaching authentication server. Retrying shortly. %s" % (ex.message))
            # logger.info("Attempting to authenticate for {} minutes.".format(i%2))

    logger.fatal("Authentication service not yet started.")


def main():
    import os

    if os.getuid() != 0:
        print("You need to run it as root.")
        sys.exit(3)

    parser = argparse.ArgumentParser(
        description='EMC\'s Elastic Cloud Storage 2.0 Software in a Docker container installation script.')
    parser.add_argument('--ips', nargs='+', help='A list of data nodes\' IPs. Example: 10.1.0.4 10.1.0.5 10.1.0.6',
                        required=True)
    parser.add_argument('--hostnames', nargs='+',
                        help='A list of data nodes\' hostnames. Example: ECSNode1.mydomain.com ECSNode2.mydomain.com ECSNode3.mydomain.com',
                        required=True)
    parser.add_argument('--ethadapter', nargs='+', help='The main Ethernet Adapter used by the Host VM to communicate with the internet. Example: eth0.',
                        required=True)
    parser.add_argument('--disks', nargs='+', help='A list of disk names to be prepared. Example: sda sdb sdc',
                        required=True)
    parser.add_argument('--cleanup', dest='cleanup', action='store_true',
                        help='If present, run the Docker container/images Clean up and the /data Folder. Example: True/False',
                        required=False)
    parser.add_argument('--imagename', dest='imagename', nargs='?',
                        help='If present, pulls a specific image from DockerHub. Defaults to emccorp/ecs-software-2.2',
                        required=False)
    parser.add_argument('--imagetag', dest='imagetag', nargs='?',
                        help='If present, pulls a specific version of the target image from DockerHub. Defaults to latest',
                        required=False)
    parser.add_argument('--use-urandom', dest='use_urandom', action='store_true', default=True,
                        help='If present, /dev/random will be mapped to /dev/urandom on the host.  If you container starts up slow the first time could help.',
                        required=False)
    parser.add_argument('--no-internet', dest='no_internet', action='store_true', default=False,
                        help='When specified, do not perform any actions that require an Internet connection.',
                        required=False)
    parser.add_argument('--load-image', dest='image_file', nargs='?',
                        help='If present, gives the name of a docker image file to load.',
                        required=False)
    parser.add_argument('--proxy', dest='proxy',nargs='?',
                        help='If present, use defined proxy to pull docker images and run docker',
                        required=False)
    parser.set_defaults(cleanup=False)
    parser.set_defaults(imagename="emccorp/ecs-software-2.2.1")
    parser.set_defaults(imagetag="latest")
    parser.set_defaults(proxy=False)
    parser.set_defaults(image_file=False)
    args = parser.parse_args()

    # Check if hotname is valid
    for hostname in args.hostnames: 
        if not re.match("^[a-z0-9]+", hostname):
            logger.info("Hostname must consist of alphanumeric (lowercase) characters.")
            sys.exit(2)


    # Check if only wants to run the Container Configuration section
    if args.cleanup:
        logger.info("Starting CleanUp: Removing Previous Docker containers and images. Deletes the created Directories.")
        subprocess.call(["service","docker","start"])
        docker_cleanup_old_images()
        clean_data_disk_func(args.disks)
        sys.exit(4)

    # Check if Number of IPs and Hostnames are the same
    if len(args.ips) != len(args.hostnames):
        print 'The number of IPs and hostnames do not match.'
        sys.exit(1)

    # Check for Valid IP Addresses
    for ip in args.ips:
        if not valid_ip(ip):
            print "Please check the --ips parameter. The IP '%s' is not valid" % ip
            sys.exit(2)


    # Check that the Selected Disks have not been initialized and can be used
    for disk in args.disks:
        if not os.path.exists("/dev/{}".format(disk)):
            print "Disk '/dev/{}' does not exist".format(disk)
            sys.exit(4)

            # disk_ready = cmdline("fdisk -l /dev/{} | grep \"Disk label type:\"".format(disk))
            # if disk_ready:
            #    print "Please check that Disk: {} is not formatted (fdisk -l).".format(disk)
            #    sys.exit(5)
            # else:
            #    print "Disk {} checked. Ready for the installation.".format(disk)

    docker_image_name = "{}:{}".format(args.imagename, args.imagetag)
    ethernet_adapter_name = get_first(args.ethadapter)
    
    
    #Pick the first node for test purposes
    ip_address = args.ips[0]

    # Step 1 : Configuration of Host Machine to run the ECS Docker Container
    logger.info("Starting Step 1: Configuration of Host Machine to run the ECS Docker Container: {}".format(docker_image_name))
    
    # yum_update_func()
    precheck()
    update_selinux_os_configuration()
    if not args.no_internet:
        package_install_func()
    prep_file_func()
    docker_cleanup_old_images()
    if args.image_file:
        docker_load_image(args.image_file)
    elif not args.no_internet:
        if args.proxy:
            docker_pull_func(docker_image_name,args.proxy)
        else:
            docker_pull_func(docker_image_name)
    network_file_func(ethernet_adapter_name)
    seeds_file_func(args.ips)
    hosts_file_func(args.ips, args.hostnames)
    prepare_data_disk_func(args.disks)
    run_additional_prep_file_func(args.disks)
    directory_files_conf_func()
    set_docker_configuration_func()
    if args.proxy:
        execute_docker_func(docker_image_name, args.use_urandom,args.proxy)
    else:
        execute_docker_func(docker_image_name, args.use_urandom)
    modify_container_conf_func(args.no_internet)
    getAuthToken(ip_address,"root","ChangeMe")
    logger.info(
        "Step 1 Completed.  Navigate to the administrator website that is available from any of the ECS data nodes. \
        The ECS administrative portal can be accessed from port 443. For example: https://ecs-node-external-ip-address. \
        The website may take a few minutes to become available.")


if __name__ == "__main__":
    main()
