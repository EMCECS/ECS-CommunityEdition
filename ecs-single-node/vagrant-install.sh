#!/bin/bash

sudo python /ecs/step1_ecs_singlenode_install.py --disks sdc

RESULT=$?
if [ $RESULT -eq 0 ]; then
    sudo python /ecs/step2_update_container.py
fi

if [ $RESULT == 0 ]; then
    echo "Waiting 1 minutes for ECS to start"
    sleep 60
    sudo python /ecs/step3_object_provisioning.py --ECSNodes=$(hostname -i | tr '\n' ' ') --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=
fi
