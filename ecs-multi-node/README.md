# ECS SW 2.0 Multiple Nodes Deployments

Welcome to the Multiple Nodes installation for ECS Software 2.0. We have provided the following deployment options: 


- **[Using Docker](https://github.com/emccode/solidsnakev2/blob/master/Documentation/ECS-MultiNode-Instructions.md "ECS Single Node Deployment Information")**
- **[Using Docker Compose](https://github.com/emccode/ecs-dockerswarm)**
- **[Using Puppet]()**


## Requirements

The Host Machines should have these following minimum requirements: 

- **Operative system:** CentOS 7
- **CPU/Cores:** 4 Cores
- **Memory:** Mininum of 30 GB RAM
- **Disks:** An unpartitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.

We have performed testing against the following platform(s): 

|Deployment Type | OS Name | Version | Docker Version |
|----------------|-------|---------|----------------|
| Docker + Scripts |CentOS	| 7.1	  | 1.4.1          |
| Docker Compose |Ubuntu	| 14	  | 1.5          |
| Puppet |CentOS	| 7.1	  | 1.4.1          |
