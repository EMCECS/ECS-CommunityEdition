# ECS SW 2.x Single Node Deployments

Welcome to the Single Node installation for ECS Software 2.x. We have provided the following deployment options: 


- **[ECS Single Node Docker Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-SingleNode-Instructions.md "ECS Single Node Deployment Information")**
- **[ECS Single Node Vagrant Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-SingleNode-Vagrant-Instructions.md "ECS Single Node Vagrant Deployment Information")**
- **[Google Compute Engine Single Node Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-GCE-SingleNode-Instructions.md "ECS GCE Single Node  Deployment")**


## Requirements

The most machine should have these following minimum requirements: 

- **Operative system:** CentOS 7.1
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 16 GB RAM 
- **Disks:** An unpartitioned/raw disk with at least 100 GB of storage per disk per host. Multiple disks can be attached on each node to increase capacity and performance. Each disk needs to be de-partitioned before running the installation scripts (you can use the --cleanup option with the step1 script to accomplish this automatically).

Installation also requires internet connectivity to recieve the requisite utility packages and Docker images.
