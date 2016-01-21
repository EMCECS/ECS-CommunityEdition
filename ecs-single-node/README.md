# ECS SW 2.2 Single Node Deployments

Welcome to the Single Node installation for ECS Software 2.0. We have provided the following deployment options: 


- **[ECS Single Node Docker Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-SingleNode-Instructions.md "ECS Single Node Deployment Information")**
- **[ECS Single Node Vagrant Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-SingleNode-Vagrant-Instructions.md "ECS Single Node Vagrant Deployment Information")**
- **[Google Compute Engine Single Node Deployment](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-GCE-SingleNode-Instructions.md "ECS GCE Single Node  Deployment")**


## Requirements

The Host Machine should have these following minimum requirements: 

- **Operative system:** CentOS 7.1(vagrant/gce deploy)  SLES12(docker deploy)
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 16 GB RAM 
- **Disks:** An un-partitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts (you can use the --cleanup option to have the step1 script do this for you).
