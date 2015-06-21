## ECS UI - Web Driven Object Provisioning


### Login to the User Interface (UI) at https://IP-Address-of-ECS-Node-1

**Note:** user authentication is not enabled in this build. # root,<any password> will work. For this example, the latest Google Chrome browser was used.


### Input License
Go to Settings | Licensing and upload the license. The license was included in the zipfile that was downloaded. You should see something similar to the below:

![Upload License file](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/input_license.PNG)

**Note:** the UI will not automatically update in this release. Current beta version may look as if it is “frozen”. Navigating away from page and returning will usually fix this.

### Create Storage vPool
Go to Manage | Storage Pools, and create a storage pool. Keep the name simple, and add all nodes to the pool. Click save.

**Note:** While processing, the tab will appear frozen for about 1-2 minutes. Let it come back on its own, and you should see something similar to:

![Create Storage VPool](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/create_storage_vpool.PNG)


### Create Virtual Data Center

Create a Virtual Data Center using the below screenshot as a guide.
**Note:** Please wait for 20 minutes after creating a Storage vPool before creating a Virtual Data Center. There are several background tasks that must complete, and for object to fully initialize.

![Create Virtual Data Center](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/create_virtual_data_center.PNG)


### Create Replication Group

Next, create a Replication Group, using the below as an example. Note that currently only 1 VDC in a replication group is supported.

![Create Replication Group](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/Create_replication_group.PNG)


### Create Namespace

Next, set the Namespace. Note that in this build optional features such as Retention Policies, quotas, Authentication Domains are not supported. For Namespace, set a simple Namespace name such as ‘ns’, pick a user such as “ecs_user”, select the Replication
Group, and click Save at the very bottom.

![Create Namespace](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/create_namespace.PNG)

### Create object user  [TODO]

Once we have configured the NameSpace, we add a new user for the Object. 

![Create Namespace](https://github.com/emccode/solidsnakev2/blob/master/Documentation/media/create_namespace.PNG)

### Create User S3 Key [TODO]

Creating an object user in the Users panel


### Create User SWIFT Key [TODO]
 
Creating an object user in the Users panel

