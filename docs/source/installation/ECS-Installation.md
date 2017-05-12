# ECS Community Edition Installation

ECS Community Edition now features a brand new installer. This installer aims to greatly improve user experience through automation. This document will guide the user through the new installation process.

## Prerequisites

Listed below are all necessary components for a successful ECS Community Edition installation. If they are not met the installation will likely fail.

### Hardware Requirements

The installation process is designed to be done from a dedicated installation node. This node will bootstrap the ECS instance and, when the process is complete, can be destroyed. Both single node and multi-node require only a single installation node. The technical requirements for this machine are minimal, but will affect the speed of the installation process. We recommend the following:

* 2 Cores
* 4 GB Memory
* 10GB HDD
* CentOS 7 Minimal

 The minimum technical requirements for the target node is as follows:
 * 4 Cores
 * 16 GB Memory
 * 100 GB block storage unit (raw, unpartitioned)
 * CentOS 7 Minimal

 For multi-node installations each data node must fulfill these minimum qualifications. The installer will do a pre-flight check to ensure that the minimum qualifications are met. If they are not the installation will not continue. 

### Environmental Requirements

The following environment is required to ensure a successful installation. 

* **Network:** Currently, all nodes, installation and target, must exist on the same subnet.
* **SSH:** Installation is coordinated via SSH, however, key authentication is not yet supported and password authentication must be enabled.
* **OS:** 

### Additional Information

This installation will work

## Getting Started

Before the data nodes can be created we have to

## The YAML File
Installation requires the creation of a YML configuration file called deploy.yml. Create this file in `/opt/emc/ecs-install`. A template guide for writing this file can be found [here](docs/design/reference.deploy.yml)
