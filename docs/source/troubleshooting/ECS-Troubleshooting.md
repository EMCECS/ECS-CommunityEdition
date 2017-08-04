# ECS Software 3.x - Troubleshooting Tips

This is a list of troubleshooting tips and nuggets that will help with issues. If you still have problems, please use the support section. 

## Installation

### If you change deploy.yml after running step1, you must run `update_deploy` before running step1 again. Otherwise you will likely get the following error:

```
{"failed": true, "msg": "An unhandled exception occurred while running the lookup plugin 'file'.
 Error was a <class 'ansible.errors.AnsibleFileNotFound'>, original message: the file_name 
 '/opt/ssh/id_ed25519.pub' does not exist, or is not readable"}

```

### `A block device configured in deploy.yml for data nodes is already partitioned.`

This error often shows up after a failed installation attempt. In order to clean up the block devices to start over run `ecsremove purge-nodes`.
  
 
## Provisioning of ECS 

It takes roughly 30 minutes to get the system provisioned for Step2.   ECS creates Storage Pools, Replication Groups with the attached disks. If Step2 is successful, you should see something along these lines.

### Checking Step 2 Object provisioning progress

If you want to see if system is making progress:

1. Log into one of ECS data nodes. 
2. Navigate to the **/var/log/vipr/emcvipr-object/** directory 
3. View the **/var/log/vipr/emc-viprobject/ssm.log** (tail -f /var/log/vipr/emcvipr-object/ssm.log
) 
   

**Note:** there are ~2k tables to be initialized for the provisioning to complete.  You can check the following command to see if the tables are close to that number and if all tables are ready.  Run this from the node.   

`curl -X GET "http://<YourIPAddress>:9101/stats/dt/DTInitStat”`

## ECS Services


### Docker Container immediately exits on startup

If your docker instance immediately exits when started, please ensure that the entries in `/etc/hosts` on the host system and `network.json` in the install directory are correct (the latter should reflect the host's public IP and the corresponding network adapter).


### ECS web portal will not start

The portal service will listen on ports 443 and 4443; check to make sure no other services (such as virtual hosts or additional instances of ECSCE) are not attempting to utilize these same ports. 

For multiple-node installations, the `/etc/hosts` file on the host VM should include entries for each node and their hostname. Additionally, many services including the ECS web portal will not start until all nodes specified to the installation step 1 script have been successfully installed and concurrently running; the installation script should be run on all nodes in a cluster before attempting authentication or use of the GUI.

If attempting to authenticate results in a response of "Connection Refused", review the below section and ensure all necessary ports are open on all ECS nodes in the cluster. 

## NFS

### Necessary NFS Ports
The following ports must be opened for NFS to function properly

Port Number |
|---|
| 111 |
| 2049 |


### NFS Volume Refuses to Mount

ECS does support the NFS file system. However, troubles can occur when ECS is installed on the full version, or "Everything" version, of CentOS 7. ***Note that the following solution is not necessary on CentOS 7 Minimal.***

#### The Problem
CentOS 7 Everything starts with NFS/RPC/Portmap components running in the root scope. This is a problem as the ECS-CE Docker container runs its own version of rpcbind. This is the instance of rpcbind that ECS is intended to communicate with. When CentOS is running rpcbind in root scope in addition to the ECS Docker container, a conflict is created and a NFS volume cannot be mounted.

This can be seen by `# rpcinfo -p` returning no NFS services.

#### The Solution
The conflict can be resolved by simply running `systemctl disable rpcbind`. This command will shut down the rpc service running on the host OS while leaving the Docker instance untouched.

To confirm the CentOS service is gone, run `rpcinfo -p` in the CentOS shell. This should return an error: `rpcinfo: can't contact portmapper: RPC: Remote system error - No such file or directory`

The same command, `rpcinfo-p`, can be run in the Docker container, which should return something similar to:
```
   program vers proto   port  service
    100000    4   tcp    111  portmapper
    100000    3   tcp    111  portmapper
    100000    2   tcp    111  portmapper
    100000    4   udp    111  portmapper
    100000    3   udp    111  portmapper
    100000    2   udp    111  portmapper
    100005    3   tcp   2049  mountd
    100005    3   udp   2049  mountd
    100003    3   tcp   2049  nfs
    100024    1   tcp   2049  status
    100021    4   tcp  10000  nlockmgr
    100021    4   udp  10000  nlockmgr
```

NFS should now function correctly. 

## IBM Tivoli Monitoring

### Issue
ECS Community edition will fail to completely initialize the storage pool on machines that have the IBM Tivoli Monitoring agent installed.  The storage pool will forever stick in the "Initializing" state and attempts to create a VDC will result in HTTP 400 errors.

### Analysis
Doing a `ps -ef` inside the container will show that dataheadsvc and metering are restarting frequently.  Looking at `/opt/storageos/logs/metering.log` will show a bind exception on port 10110.  This port is already bound by Tivoli's `k10agent` process.

### Workaround
1. Uninstall Tivoli Monitoring
or
2. Change the port on impacted nodes.

#### Changing the port on ECS
On _all_ nodes, you will need to edit `/opt/storageos/conf/mt-var.xml` to change the bind port from 10110 to 10109.  Edit the file and change the line:

```
<property name="serviceUrl" value="service:jmx:rmi://127.0.0.1:10110/jndi/rmi://127.0.0.1:10111/sos" />
```

to:

```
<property name="serviceUrl" value="service:jmx:rmi://127.0.0.1:10109/jndi/rmi://127.0.0.1:10111/sos" />
```

Then restart the metering service:

```
kill `pidof metering`
```

## Network Troubleshooting

### For those operating behind EMC firewall

To install ECS Community Edition under these conditions, please view the readme file under **/emc-ssl-cert** for further instructions in installing the necessary CA certificate.

### Disabling IPv6

ECS Community Edition does not yet support IPv6. The following procedure can be used to disable IPv6 in CentOS 7. 

### To disable IPv6 on startup:

Add the following to /etc/sysctl.conf

```
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
```

### To disable IPv6 running:

```
echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6
```
or

```
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.default.disable_ipv6=1
```

### Get correct interface name

CentOS 7 does not assign network interface names as eth0, eth1, etc, but rather assigns "predictable" names to each interface that generally look like `ens32` or similar. There are many benefits to this that can be read about [here](https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/).

This can be disabled as documented in the above link, however, these names can otherwise be simply found and used in the ECS-Community installer without issue. To find the names for each device enter the following command: `ip a`. This command will output a list of network devices. Simply find the corresponding device and substitute it for eth0 in the stage1 installation script.

### Port Conflicts

It is possible that on multinode installations ECS may run into a port conflict. So far there exists a port conflict with the following:

*   ScaleIO - Ports: 9011, 9099
  
In these instances the user can attempt to: 

1. Enter the container
2. Change all instances of the conflicting ports to unused ports in `/opt/storageos/conf` 
3. Reboot the nodes after altering the conf file.

### List of open ports required on each ECS data node

Ensure the ports in the following table are open for communication. In the case of a multiple-node installation, additionally ensure that each node is trusted to itself and to other nodes in the system by using the following command on each node:

`firewall-cmd --permanent --zone=trusted --add-source=<ECS-node-IP>/32`

followed by `firewall-cmd --reload` for each host.

`fwd_settings.sh` in the main directory will invoke the `firewalld` service and permanently open necessary ports. In the case of a failure in this setup referencing `iptables`, please ensure that your docker network bridge is running and installed using `yum install bridge-utils`.



|Port Name-Usage=Port Number|
|---------------------------|
|port.ssh=22|
|port.ecsportal=80|
|port.rcpbind=111|
|port.activedir=389|
|port.ecsportalsvc=443|
|port.activedirssl=636|
|port.ssm=1095|
|port.rm=1096|
|port.blob=1098|
|port.provision=1198|
|port.objhead=1298|
|port.nfs=2049|
|port.zookeeper=2181|
|port.coordinator=2889|
|port.cassvc=3218|
|port.ecsmgmtapi=4443|
|port.rmmvdcr=5120|
|port.rmm=5123|
|port.coordinator=7399|
|port.coordinatorsvc=7400|
|port.rmmcmd=7578|
|port.objcontrolUnsecure=9010|
|port.objcontrolSecure=9011|
|port.s3MinUnsecure=9020|
|port.s3MinSecure=9021|
|port.atmosMinUnsecure=9022|
|port.atmosMinSecure=9023|
|port.swiftMinUnsecure=9024|
|port.swiftMinSecure=9025|
|port.apiServerMinUnsecure=9028|
|port.apiServerMinSecure=9029|
|port.hdfssvc=9040|
|port.netserver=9069|
|port.cm=9091|
|port.geoCmdMinUnsecure=9094|
|port.geoCmdMinSecure=9095|
|port.geoDataMinUnsecure=9096|
|port.geoDataMinSecure=9097|
|port.geo=9098|
|port.ss=9099|
|port.dtquery=9100|
|port.dtqueryrecv=9101|
|port.georeplayer=9111|
|port.stat=9201|
|port.statWebServer=9202|
|port.vnest=9203|
|port.vnesthb=9204|
|port.vnestMinUnsecure=9205|
|port.vnestMinSecure=9206|
|port.hdfs=9208|
|port.event=9209|
|port.objcontrolsvc=9212|
|port.zkutils=9230|
|port.cas=9250|
|port.resource=9888|
|port.tcpIpcServer=9898|
