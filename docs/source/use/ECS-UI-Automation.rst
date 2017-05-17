#

.. raw:: html

   <center> 

ECS UI - Script Driven Object Provisioning

.. raw:: html

   </center>

**step2\_object\_provisioning.py**

+--------------------+--------------------------------------+
| Argument           | Expected Input                       |
+====================+======================================+
| --ECSNodes=        | Comma delineated list of datanodes   |
+--------------------+--------------------------------------+
| --Namespace=       | Namespace                            |
+--------------------+--------------------------------------+
| --ObjectVArray=    | Object vArray Name                   |
+--------------------+--------------------------------------+
| --ObjectVPool=     | Object VPool Name                    |
+--------------------+--------------------------------------+
| --UserName=        | User name to be created              |
+--------------------+--------------------------------------+
| --DataStoreName=   | Name of datastore to be created      |
+--------------------+--------------------------------------+
| --VDCName=         | Name of the VDC                      |
+--------------------+--------------------------------------+
| --MethodName=      | Operation to be performed            |
+--------------------+--------------------------------------+

Run the script with below values 1 step at a time for –MethodName
parameter . The parameters are mentioned below in the sequence in which
they should be invoked.

-  UploadLicense
-  CreateObjectVarray
-  CreateDataStore
-  InsertVDC
-  CreateObjectVpool
-  CreateNamespace
-  CreateUser **Note:** CreateUser method will return an exception that
   user already exists. Ignore the exception and proceed to create
   secret key for the user. Looks like the user is being created in
   spite of the exception.
-  CreateSecretKey

**Note:** If -MethodName option is not provided all the Object
Provisioning steps will be run in the same sequence as above
automatically.

**Note:** The script may throw error when run using the old version of
Python 2.6.8. Python 2.7.8 works fine for the script

Executing the Script using individual steps
-------------------------------------------

Using the example Hosts and information provided on the documentation:

+----------------+--------------+-------------+
| Hostname       | IP Address   | Disk Name   |
+================+==============+=============+
| ecstestnode1   | 10.0.1.10    | sdc sdd     |
+----------------+--------------+-------------+
| ecstestnode2   | 10.0.1.11    | sdc sdd     |
+----------------+--------------+-------------+
| ecstestnode3   | 10.0.1.12    | sdc sdd     |
+----------------+--------------+-------------+
| ecstestnode4   | 10.0.1.13    | sdc sdd     |
+----------------+--------------+-------------+

These are example values for the parameters:

\|Variable Name\|Variable Description \| Example Value\|
\|-------------\|---------------------\|--------------\| \|ECSNodes \|
IP Addresses of the ECS Nodes (coma delimited list). \|
10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13 \| \|NameSpace \| The objects'
Namespace \| ns1 \| \|ObjectVArray \| The objects' Virtual Array \| ova1
\| \|ObjectVPool \| The objects' Virtual Pool \| ov1 \| \|DataStoreName
\| The name of the Data Store.\| ds1 \| \|VDCName \| The name of the
Virtual Data Center.\| vdc1 \| \|MethodName \| The name of step to be
executed. Leave blank for automated and add a value for a manual
installation\| [empty] \|

Step 1: Upload the License File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=UploadLicense

Step 2: Create Object Virtual Array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVarray

Step 3: Create the Data Store
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateDataStore

Step 4: Insert VDC
~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=InsertVDC

Step 5: Create Object Virtual Pool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVpool

Step 6: Create the Namespace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateNamespace

Step 7: Create a User
~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateUser

Step 8: Create the SecretKey
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13  --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateSecretKey

