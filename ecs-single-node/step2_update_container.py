#!/usr/bin/env python

import subprocess
import logging
import logging.config
import sys
import settings
import os

# Logging Init
logging.config.dictConfig(settings.CONTAINER_LOGGING)
logger = logging.getLogger("root")


def modify_container_conf_func():
    try:
        logger.info("Backup object properties file")
        os.system(
            "docker exec -i -t  ecsstandalone cp /opt/storageos/conf/cm.object.properties /opt/storageos/conf/cm.object.properties.old")

        logger.info("Backup application config file")
        os.system(
            "docker exec -i -t  ecsstandalone cp /opt/storageos/ecsportal/conf/application.conf /opt/storageos/ecsportal/conf/application.conf.old")

        logger.info("Copy object properties file to host")
        os.system(
            "docker exec -i -t ecsstandalone cp /opt/storageos/conf/cm.object.properties /host/cm.object.properties1")

        logger.info("Copy application config file to host")
        os.system(
            "docker exec -i -t  ecsstandalone cp /opt/storageos/ecsportal/conf/application.conf /host/application.conf")

        logger.info("Modify BlobSvc config for single node")
        os.system(
            "sed s/object.MustHaveEnoughResources=true/object.MustHaveEnoughResources=false/  < /host/cm.object.properties1 > /host/cm.object.properties")

        logger.info("Modify Portal config for to bypass validation")
        os.system("echo ecs.minimum.node.requirement=1 >> /host/application.conf")

        logger.info("Copy modified files to container")
        os.system(
            "docker exec -i -t  ecsstandalone cp /host/cm.object.properties /opt/storageos/conf/cm.object.properties")
        os.system(
            "docker exec -i -t  ecsstandalone cp /host/application.conf /opt/storageos/ecsportal/conf/application.conf")

        logger.info("Stop container")
        os.system("docker stop ecsstandalone")

        logger.info("Start container")
        os.system("docker start ecsstandalone")

        logger.info("Clean up local files")
        os.system("rm -rf /host/cm.object.properties*")
        os.system("rm -rf /host/application.conf")


    except Exception as ex:
        logger.exception(ex)
        logger.fatal("Aborting program! Please review log.")
        sys.exit()


def main():
    logger.info("Starting Step 2: Modify Container for Single Node Deployment.")
    modify_container_conf_func()
    logger.info("Completed Step 2. Please wait for ECS to Start")


if __name__ == "__main__":
    main()
