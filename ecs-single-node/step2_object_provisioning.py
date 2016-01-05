#!/usr/bin/env python

import os,json
import subprocess
import shutil
import getopt
import sys,re
import time

AuthToken=None
def getAuthToken(ECSNode, User, Password):
    curlCommand = "curl -i -k https://%s:4443/login -u %s:%s" % (ECSNode, User, Password)
    print ("Executing getAuthToken: %s " % curlCommand)
    res=subprocess.check_output(curlCommand, shell=True)
    authTokenPattern = "X-SDS-AUTH-TOKEN:(.*)\r\n"
    searchObject=re.search(authTokenPattern,res)
    assert searchObject, "Get Auth Token failed"
    print("Auth Token %s" % searchObject.group(1))
    return searchObject.group(1)


def executeRestAPI(url, method, filter, data, ECSNode,contentType='json',checkOutput=0):
    if data:
        subprocess.call("echo %s > request_body.tmp" % data, shell=True)
        data="-d @request_body.tmp"
    if "license" in url:
        data="-T license.xml"
    curlCommand = "curl -s -k -X %s -H 'Content-Type:application/%s' \
    -H 'X-SDS-AUTH-TOKEN:%s' \
    -H 'ACCEPT:application/%s' \
    %s https://%s:9011%s" %(method, contentType, AuthToken, contentType,data, ECSNode, url)
    print ("Executing REST API command: %s " % curlCommand)
#print jsonResult
    if checkOutput:
        subprocess.call(curlCommand, shell=True)
        jsonResult = subprocess.check_output(curlCommand, shell=True)
        RestOutputDict = {}
        RestOutputDict = json.loads(jsonResult)
        return RestOutputDict
        assert "code" not in jsonResult, "%s %s failed" % (method, url)
    else:
        res=subprocess.call(curlCommand, shell=True)
        print res


def retry( numberOfRetries, timeToWaitBetweenTriesInSeconds, functionToRetry, argumentList, keywordArgs = {}):
    for i in range(numberOfRetries):
        try:
            return apply(functionToRetry, argumentList, keywordArgs)
        except Exception, e:
            print("Method %s threw error %s" % (functionToRetry, e))
            print("Sleep for %s seconds before retry" % timeToWaitBetweenTriesInSeconds)
            time.sleep(timeToWaitBetweenTriesInSeconds)
    raise e


def getVDCID(ECSNode,VDCName):
    url ='/object/vdcs/vdc/%s' %VDCName
    return executeRestAPI(url, 'GET','.id', "", ECSNode,checkOutput=1)["id"]

def getVarrayID(ECSNode):
    return executeRestAPI('/vdc/data-services/varrays', 'GET','.id', "", ECSNode, checkOutput=1)['varray'][0]["id"]

def getVpoolID(ECSNode):
    return executeRestAPI('/vdc/data-service/vpools', 'GET','.id', "", ECSNode, checkOutput=1)['data_service_vpool'][0]["id"]

def getNamespaces(ECSNode):
    return executeRestAPI('/object/namespaces', 'GET','.id', "", ECSNode, checkOutput=1)['namespace'][0]["id"]


def DeleteNamespace(ECSNode, Namespace):
    url ='/object/namespaces/namespace/%s/deactivate' %Namespace
    return executeRestAPI(url, 'POST','', "", ECSNode)


def DeleteUser(ECSNode,userName,Namespace):
    print("\nDelete User %s" % userName)
    DeleteUserPayload ='{\\"user\\":\\"%s\\",\
    \\"namespace\\":\\"%s\\"\
    }' % (userName, Namespace)
    executeRestAPI("/object/users/deactivate", 'POST','.id', DeleteUserPayload, ECSNode)


def getVDCSecretKey(ECSNode):
    secretKeyDict = executeRestAPI("/object/vdcs/vdc/local/secretkey", 'GET', '.secret_key', "", ECSNode, checkOutput=1)
    return secretKeyDict['key']


def UploadLicense(ECSNode):
    executeRestAPI("/license", 'POST','', '', ECSNode, contentType='xml')

def UploadLicenseWithRetry(ECSNode):
    retry(5, 60, UploadLicense, [ECSNode])


def CreateObjectVArray(ECSNode, objectVArrayName):
    print("\nCreate Object Varray %s" % objectVArrayName)
    objectVArrayPayload ='{\\"name\\":\\"%s\\",\
    \\"description\\":\\"%s\\",\
    \\"isProtected\\":\\"%s\\"\
    }' % (objectVArrayName, objectVArrayName, "false")
    executeRestAPI("/vdc/data-services/varrays", 'POST','.id', objectVArrayPayload, ECSNode, checkOutput=1)
    print("Object Varray %s is created" % objectVArrayName)

def CreateObjectVarrayWithRetry(ECSNode, objectVArrayName):
    retry(30, 60, CreateObjectVArray, [ECSNode, objectVArrayName])


def createDataStoreOnCommodityNodes(ECSNode, dataStoreName, varray):
    createDataStorePayLoad ='{ \\"nodes\\":[\
    {\
    \\"nodeId\\":\\"%s\\",\\"name\\":\\"%s\\",\
    \\"virtual_array\\":\\"%s\\",\\"description\\":\\"%s\\"\
    }]}' % (ECSNode, dataStoreName, varray, dataStoreName)
    return executeRestAPI('/vdc/data-stores/commodity', 'POST','.id', createDataStorePayLoad, ECSNode)


def CreateDataStoreOnCommodityNodesWithRetry(ECSNode, dataStoreName, varray):
    retry(5, 60, createDataStoreOnCommodityNodes, [ECSNode, dataStoreName, varray])


def RetryDTStatus(ECSNode):
    # DTs stagger their init, so wait for >200 before we accept 100% as okay
    # Real number is more like 384
    minDt = 200

    print("\nWaiting on Directory Tables to Initialize...")

    curlCommand = "curl -s http://%s:9101/stats/dt/DTInitStat" % (ECSNode)
    timeout = time.time() + 60*60
    ret = ""

    try:
        dtPrev=1
        while True:
            ret = subprocess.check_output(curlCommand, shell=True)
            dtTot = re.findall("<total_dt_num>(.+?)</total_dt_num>", ret)[0]
            dtUnready = re.findall("<unready_dt_num>(.+?)</unready_dt_num>", ret)[0]
            dtUnknown = re.findall("<unknown_dt_num>(.+?)</unknown_dt_num>", ret)[0]
            dtTotal = int(float(dtTot))
            dtBad = int(float(dtUnready)) + int(float(dtUnknown))
            initPercent=((dtTotal-dtBad)*100.0/dtTotal)
            print("Directory Tables %.1f%% ready. (%s total %s unready %s unknown)") % (initPercent, dtTot, dtUnready, dtUnknown)

            if (dtBad == 0 and dtPrev == dtTotal and dtTotal > minDt):
                break
            elif(time.time() > timeout):
                print("Directory Tables failed to initialize.")
                break

            dtPrev = dtTotal
            time.sleep(20)

    except Exception, e:
        if("Cannot update" in ret):
            print(ret)
        else:
            print("Failed to retrieve DT status: %s" % (e))


def InsertVDC(ECSNode, VDCName):
    # count storagepool nodes in state "readytouse"
    
    for i in range(0, 9):
        curlCommand = "curl -s -k -H\"X-SDS-AUTH-TOKEN: %s\" https://%s/storagepools\ | grep -c 'readytouse'"  % (AuthToken, ECSNode)
        stateCheck = subprocess.check_output(curlCommand, shell=True)
        if stateCheck is "0":
            print("Step 2 loading, Storage data creation in progress")
            time.sleep(180)
        elif i == 9:
            print("No storage pools could be found.")
            return None
        else:
            break

    #secretKey="secret12345"
    secretKey=getVDCSecretKey(ECSNode)
    InsertVDCPayload ='{\\"vdcName\\":\\"%s\\",\
    \\"interVdcEndPoints\\":\\"%s\\", \
    \\"secretKeys\\":\\"%s\\"\
    }' % (VDCName, ECSNode, secretKey)
    executeRestAPI('/object/vdcs/vdc/%s' % VDCName, 'PUT','',InsertVDCPayload, ECSNode)
    return getVDCID(ECSNode,VDCName)


def InsertVDCWithRetry(ECSNode, objectVpoolName):
    retry(30, 60, InsertVDC, [ECSNode, objectVpoolName])


def CreateObjectVpool(ECSNode, objectVpoolName, VDCName):
    vdcID = getVDCID(ECSNode,VDCName)
    print("\nVDC ID is %s" % vdcID)
    vArrayID = getVarrayID(ECSNode)
    print("\nVArray ID is %s" % vArrayID)
    objectVpoolPayload ='{\\"description\\":\\"%s\\",\
    \\"name\\":\\"%s\\", \
    \\"zone_mappings\\":[\
    {\
    \\"name\\":\\"%s\\",\\"value\\":\\"%s\\"\
    }]}' % (objectVpoolName, objectVpoolName, vdcID, vArrayID)
    print("\nCreate Object VPool %s" % objectVpoolName)
    executeRestAPI("/vdc/data-service/vpools", 'POST','.id', objectVpoolPayload, ECSNode, checkOutput=1)
    print("Object Vpool %s is created" % objectVpoolName)

def CreateObjectVpoolWithRetry(ECSNode, objectVpoolName, VDCName):
    retry(5, 60, CreateObjectVpool, [ECSNode, objectVpoolName, VDCName])


def CreateNamespace(ECSNode, Namespace, objectVpoolName):
    print("\nCreate Namespace %s" % Namespace)
    NamespacePayload='{\\"namespace\\": \\"%s\\", \\"default_data_services_vpool\\": \\"%s\\"}'%(Namespace, objectVpoolName)
    executeRestAPI("/object/namespaces/namespace", 'POST','.id', NamespacePayload, ECSNode, checkOutput=1)
    print("Namespace %s is created" % Namespace)

def CreateNamespaceWithRetry(ECSNode, Namespace):
    retry(5, 60, CreateNamespace, [ECSNode, Namespace])


def addUser(ECSNode,userName,Namespace):
    print("\nCreate User %s" % userName)
    createUserPayload ='{\\"user\\":\\"%s\\",\
    \\"namespace\\":\\"%s\\"\
    }' % (userName, Namespace)
    executeRestAPI("/object/users", 'POST','.id', createUserPayload, ECSNode)


def addUserSecretKey(ECSNode, username):
    secretKeyPayload='{\\"existing_key_expiry_time_mins\\":20000}'
    secretKeyDict = executeRestAPI("/object/user-secret-keys/%s" % username, 'POST', '.secret_key', secretKeyPayload, ECSNode)
    print("\nAdd secret key for user %s" % username)

def getUserSecretKey(ECSNode, username):
    secretKeyDict = executeRestAPI("/object/user-secret-keys/%s" % username, 'GET', '.secret_key', "", ECSNode, checkOutput=1)
    print("\n\nUser %s SecretKey is %s" % (username,secretKeyDict['secret_key_1']))



def main(argv):
    try:
        opts, argv = getopt.getopt(argv, '', ["ECSNodes=","Namespace=","ObjectVArray=","ObjectVPool=","UserName=","DataStoreName=","VDCName=","MethodName="])
    except getopt.GetoptError, e:
        print e
        print 'ObjectProvisioning.py --ECSNodes=<Coma separated list of datanodes> --Namespace=<namespace> --ObjectVArray=<Object vArray Name> --ObjectVPool=<Object VPool name> --UserName=<user name to be created> --DataStoreName=<Name of the datastore to be created> --VDCName=<Name of the VDC> --MethodName=<Operation to be performed>\n  --MethodName is required only when you need to run a particular step in Object Provisioning.If this option is not provided all the Object Provisioning steps will be run.\n Supported options for --MethodName are:\n UploadLicense \n CreateObjectVarray \n GetVarrayID \n CreateDataStore \n InsertVDC \n CreateObjectVpool \n CreateNamespace \n CreateUserAndSecretKey \n'
        sys.exit(2)
    ECSNodes=""
    MethodName=""
    for opt, arg in opts:
        if opt == '-h':
            print 'ObjectProvisioning.py --ECSNodes=<Coma separated list of datanodes> --Namespace=<namespace> --ObjectVArray=<Object vArray Name> --ObjectVPool=<Object VPool name> --UserName=<user name to be created> --DataStoreName=<Name of the datastore to be created> --VDCName=<Name of the VDC> --MethodName=<Operation to be performed>\n  --MethodName is required only when you need to run a particular step in Object Provisioning.If this option is not provided all the Object Provisioning steps will be run.\n Supported options for --MethodName are:\n UploadLicense \n CreateObjectVarray \n GetVarrayID \n CreateDataStore \n InsertVDC \n CreateObjectVpool \n CreateNamespace \n CreateUserAndSecretKey \n'
            sys.exit()
        elif opt in ("-ECSNodes", "--ECSNodes"):
            ECSNodes = arg
            ECSNodeList = ECSNodes.split(",")
            ECSNode = ECSNodeList[0]
        elif opt in ("-Namespace", "--Namespace"):
            Namespace = arg
        elif opt in ("-ObjectVArray", "--ObjectVArray"):
            ObjectVArray = arg
        elif opt in ("-ObjectVPool", "--ObjectVPool"):
            ObjectVPool = arg
        elif opt in ("-UserName", "--UserName"):
            UserName = arg
        elif opt not in ("-UserName", "--UserName"):
            print("Username is a required argument.")
            sys.exit(2)
        elif opt in ("-DataStoreName", "--DataStoreName"):
            DataStoreName = arg
        elif opt in ("-VDCName", "--VDCName"):
            VDCName = arg
        elif opt in ("-MethodName", "--MethodName"):
            MethodName = arg

    global AuthToken
    AuthToken=getAuthToken(ECSNode, "root", "ChangeMe")
    
    print("ECSNodes: %s" %ECSNode)
    print("Namespace: %s" %Namespace)
    print("ObjectVArray: %s" %ObjectVArray)
    print("ObjectVPool: %s" %ObjectVPool)
    print("UserName: %s" %UserName)
    print("DataStoreName: %s" %DataStoreName)
    print("VDCName: %s" %VDCName)
    print("MethodName: %s" %MethodName)
    
    
    if MethodName == "UploadLicense":
        UploadLicense(ECSNode)
        sys.exit()
    elif MethodName == "CreateObjectVarray":
        CreateObjectVarrayWithRetry(ECSNode, ObjectVArray)
        print("Virtual Array: %s" %getVarrayID(ECSNode))
        sys.exit()
    elif MethodName == "GetVarrayID":
        ObjectVArrayID = getVarrayID(ECSNode)
        sys.exit()
    elif MethodName == "CreateDataStore":
        ObjectVArrayID = getVarrayID(ECSNode)
        for node in ECSNodeList:
            CreateDataStoreOnCommodityNodesWithRetry(node, DataStoreName, ObjectVArrayID)
        time.sleep(20 * 60)
        sys.exit()
    elif MethodName == "InsertVDC":
        InsertVDC(ECSNode, VDCName)
        print("VDCID: %s" %getVDCID(ECSNode, VDCName))
        sys.exit()
    elif MethodName == "CreateObjectVpool":
        CreateObjectVpoolWithRetry(ECSNode, ObjectVPool, VDCName)
        print("Data service vPool ID:%s" %getVpoolID(ECSNode))
        sys.exit()
    elif MethodName == "CreateNamespace":
        ObjectVPoolID = getVpoolID(ECSNode)
        CreateNamespace(ECSNode, Namespace, ObjectVPoolID)
        print("Namespace: %s" %getNamespaces(ECSNode))
        sys.exit()
    elif MethodName == "CreateUser":
        addUser(ECSNode, UserName,  Namespace)
        sys.exit()
    elif MethodName == "CreateSecretKey":
        addUserSecretKey(ECSNode, UserName)
        getUserSecretKey(ECSNode, UserName)
        sys.exit()
    elif MethodName == "DeleteUser":
        DeleteUser(ECSNode, UserName,  Namespace)
        sys.exit()
    elif MethodName == "getUserSecretKey":
        getUserSecretKey(ECSNode, UserName)
        sys.exit()

    else:
        UploadLicense(ECSNode)
        CreateObjectVarrayWithRetry(ECSNode, ObjectVArray)
        print("Virtual Array: %s" %getVarrayID(ECSNode))
        ObjectVArrayID = getVarrayID(ECSNode)
        
        for node in ECSNodeList:
                CreateDataStoreOnCommodityNodesWithRetry(node, DataStoreName, ObjectVArrayID)

        RetryDTStatus(ECSNode)
        InsertVDC(ECSNode, VDCName)
        print("VDCID: %s" %getVDCID(ECSNode, VDCName))
        CreateObjectVpoolWithRetry(ECSNode, ObjectVPool, VDCName)
        print("Data service vPool ID:%s" %getVpoolID(ECSNode))
        ObjectVPoolID = getVpoolID(ECSNode)
        CreateNamespace(ECSNode, Namespace, ObjectVPoolID)
        print("Namespace: %s" %getNamespaces(ECSNode))
        addUser(ECSNode, UserName,  Namespace)
        addUserSecretKey(ECSNode, UserName)
        getUserSecretKey(ECSNode, UserName)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
