# ECS Software 2.0 - Troubleshooting Tips


## Troubleshooting Tips
This is a list of troubleshooting tips and nuggets that will help with issues. If you still have problems, please use the support section. 
  
 
### Provisioning of ECS 

It takes roughly 30 minutes to get the system provisioned for Step 2 (step2_object_provisioning.py).   ECS creates Storage Pools, Replication Groups with the attached disks. If Step 2 is successful, you should see something along these lines.

#### Adding a Secret Key for a user

Set the user and the key that needs to be used and execute the command. For example:

User: emccode
SecretKey: UORQB9Xxx8OKmjplSgKHRIPeeWcR2bbiagC5/xT+Add secret 

Executing REST API command: 

`curl -s -k -X GET -H 'Content-Type:application/json'     -H 'X-SDS-AUTH-TOKEN: BAAca1B6WUJ2Q2hFeUZWSkczNXFIT0I0LzA1SHg4PQMAQQIADTE0MzQ4Njk5Mjc0NzIDAC51cm46VG9rZW46ZWVlNGEwMDEtYzkyOC00ZTIyLTlkMzQtYmE0NWU2N2E4MmM4AgAC0A8='     -H 'ACCEPT:application/json'      https://23.99.93.171:9011/object/user-secret-keys/emccode 
{"secret_key_1":"UORQB9Xxx8OKmjplSgKHRIPeeWcR2bbiagC5/xT+","key_timestamp_1":"2015-06-21 07:31:48.515","key_expiry_timestamp_1":"","secret_key_2":"","key_timestamp_2":"","key_expiry_timestamp_2":"","link":{"rel":"self","href":"/object/secret-keys"}}`



### Checking Step 2 Object provisioning progress

If you want to see if system is making progress:

1. Log into one of ECS data nodes. 
2. Navigate to the **/var/log/vipr/emcvipr-object/** directory 
3. View the **/var/log/vipr/emc-viprobject/ssm.log** (tail -f /var/log/vipr/emcvipr-object/ssm.log
) 
   

**Note:** there are ~2k tables to be initialized for the provisioning to complete.  You can check the following command to see if the tables are close to that number and if all tables are ready.  Run this from the node.   

`curl -X GET "http://<YourIPAddress>:9101/stats/dt/DTInitStat”`


### For those operating behind EMC firewall

To install ECS Community Edition under these conditions, please view the readme file under **/emc-ssl-cert** for further instructions in installing the necessary CA certificate.

### List of Open ports required on each ECS data node

Ensure the following ports are open for communication.  Add these ports to the guide saying if a single node is used:


|Port Name-Usage=Port Number|
|---------------------------|
|port.ecsportal=80|
|port.activedir=389|
|port.ecsportalsvc=443|
|port.activedirssl=636|
|port.ssm=1095|
|port.rm=1096|
|port.blob=1098|
|port.provision=1198|
|port.objhead=1298|
|port.cassvc=3218|
|port.ecsmgmtapi=4443|
|port.rmmvdcr=5120|
|port.rmm=5123|
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
|port.cas=9250|
|port.resource=9888|
|port.tcpIpcServer=9898|
