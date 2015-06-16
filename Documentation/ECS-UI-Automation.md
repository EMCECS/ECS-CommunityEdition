## ECS UI - Script Driven Object Provisioning -: ##

- In case on any nodes, the object container enumerates with "docker ps -a" but not "docker ps" and the disks are in Object:Formatted:Suspect state, apply the below workaround:•Stop object container on the node
- Manually remove object container on the node (docker rm 05)
- The container should now enumerate with "docker ps"

- Not a known issue at this stage, so please file a bug and report to caspian.fabric.
 
- Copy the attached provisioning script (ObjectProvisioning.py) and license XML(license.xml) on your machine under the same folder, below is the usage to the script:
- 
**ObjectProvisioning.py** --ECSNodes=`Coma seperated list of datanodes` --Namespace=`namespace` --ObjectVArray=`Object vArray Name` --ObjectVPool=`Object VPool name` --UserName=`user name to be created` --DataStoreName=`Name of the datastore to be created` --VDCName=`Name of the VDC` --MethodName=`Operation to be performed`

Run the script with below values 1 step at a time for –MethodName parameter . The parameters are mentioned below in the sequence in which they should be invoked.
- UploadLicense
- CreateObjectVarray
- CreateDataStore
- InsertVDC
- CreateObjectVpool
- CreateNamespace

**CreateUser**  - CreateUser method will return an exception that user already exists. Ignore the exception and proceed to create secret key for the user. Looks like the user is being created inspite of the exception.

**CreateSecretKey** 
 
Note:  If -MethodName option is not provided all the Object Provisioning steps will be run in the same sequence as above automatically.  

           The script may throw error when run using the old version of Python 2.6.8. Python 2.7.8 works fine for the script


## Automation steps 

### Step 1: Upload the License File
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=UploadLicense

### Step 2: Create Ojbect Virtual Array
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVarray

### Step 3: Create the Data Store
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateDataStore

### Step 4: Insert VDC
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=InsertVDC

### Step 5: Create Object Virtual Pool
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVpool

### Step 6: Create the Namespace
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateNamespace

### Step 7: Create a User
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateUser

### Step 8: Create the SecretKey
sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateSecretKey

