#!/usr/bin/env bash

# Edited on 8 December 2017 to reflect ECS Lite prototype.
# Edited on 3 January 2018 to enable GC of partial chunks.
# Edited on 4 January 2018 to set object.MaxReplayRegionsCount = 128.
# Edited on 10 January 2018 to fix errors in how some cm-conf.xml insertions were applied.
# Edited on 2 February 2018 to establish aggressive garbage-collection parameter settings.
#
# this script should be used to generate an overlay Dockerfile, which may be applied on top of an object container image, reducing various parameters.

if [ "$#" -lt 2 ]; then
	echo "Usage: $0 <object image> <dockerfile>"
	echo "Example: $0 nile-object:1.2.0.0-123213 /path/to/Dockerfile"
	exit 1
fi

obj_image=$1
df=$2

echo "$0 creating $df to build reduced image from $1"

declare COREOS_MULTI_JVM_MEMORY_DIV=${COREOS_MULTI_JVM_MEMORY_DIV:-4}
declare COREOS_MULTI_EC_BUFFER_CAPACITY=${COREOS_MULTI_EC_BUFFER_CAPACITY:-2}
declare COREOS_MULTI_THREADS_DIV=${COREOS_MULTI_THREADS_DIV:-4}
declare COREOS_MULTI_BLOOM_ENABLED=${COREOS_MULTI_BLOOM_ENABLED:-false}
declare COREOS_MULTI_DT_MEMORY_PROPS=${COREOS_MULTI_DT_MEMORY_PROPS:-"object.DTMaxTotalTableCapacityBytes:3 object.DTReservedTableCapacityBytes:2 object.DTInitTableCapacityBytes:3 object.DTTableCapacityBytes:3 object.GeoRepDTMaxTotalTableCapacityBytes:3 object.GeoRepDTReservedTableCapacityBytes:3 object.GeoRepDTInitTableCapacityBytes:3 object.GeoRepDTTableCapacityBytes:3"}
declare COREOS_MULTI_BM_BUFFER_SIZE=${COREOS_MULTI_BM_BUFFER_SIZE:-16777216}
declare COREOS_MULTI_BM_BUFFER_COUNT=${COREOS_MULTI_BM_BUFFER_COUNT:-2}
declare COREOS_MULTI_BTREE_CACHE_PROPS=${COREOS_MULTI_BTREE_CACHE_PROPS:-"object.BPlusTreeReaderOffHeapCacheSizeMB:4 object.BPlusTreeReaderCacheSizeMB:4 object.BPlusTreeSharedWriterCachePoolSizeMB:4 object.BPlusTreeSharedPrefetchCachePoolSizeMB:4"}
declare COREOS_MAX_PARALLEL_THREADS=${COREOS_MAX_PARALLEL_THREADS:-2000}
declare COREOS_IOUTIL_HEAP_CACHE_SIZE=${COREOS_IOUTIL_HEAP_CACHE_SIZE:-209715200}

declare COREOS_NUM_DT_PER_COS=${COREOS_NUM_DT_PER_COS:-6}

#object.NumDirectoriesPerCoSForSystemDT=128
#object.NumDirectoriesPerCoSForUserDT=128

cat>$df<<EOF
FROM $obj_image

RUN grep -hoE 'Xmx[0-9]+m' /opt/storageos/bin/*| grep -oE '[0-9]+'| sort -n | uniq| while read m; do test "\$m" -gt 128 && { find /opt/storageos/bin -type f -print | while read f; do file "\$f" | grep -q 'shell script' && sed -r -i "s/Xmx\${m}m/Xmx\$((\$m/$COREOS_MULTI_JVM_MEMORY_DIV))m/g;s/-Xmn[0-9]+[kmg]?//g" "\$f" ; done } ; done ; true

RUN grep -hoE 'Xmx[0-9]+m' /opt/storageos/bin/georeceiver | grep -oE '[0-9]+'| sort -n | uniq| while read m; do test "\$m" -gt 128 && { find /opt/storageos/bin -type f -print | while read f; do file "\$f" | grep -q 'shell script' && sed -r -i "s/Xmx\${m}m/Xmx128m/g;s/-Xmn[0-9]+[kmg]?//g" "\$f" ; done } ; done ; true

#RUN grep -hoE 'Xmx[0-9]+m' /opt/storageos/bin/transformsvc | grep -oE '[0-9]+'| sort -n | uniq| while read m; do test "\$m" -gt 128 && { find /opt/storageos/bin -type f -print | while read f; do file "\$f" | grep -q 'shell script' && sed -r -i "s/Xmx\${m}m/Xmx512m/g;s/-Xmn[0-9]+[kmg]?//g" "\$f" ; done } ; done ; true

# Adjust memory adjustment
RUN sed -i s/-Xmx128m/-Xmx512m/ /opt/storageos/bin/transformsvc
RUN sed -i s/-Xmx2048m/-Xmx3072m/ /opt/storageos/bin/blobsvc
#RUN sed -i s/-Xmx512m/-Xmx256m/ /opt/storageos/bin/metering
RUN sed -i s/\\$\(_get_mem_fraction_mb\ 428.3m\ 0.0081\)/64/ /opt/storageos/bin/ecsportalsvc
#RUN sed -i s/-Xmx128m/-Xmx64m/ /opt/storageos/bin/dtquery
RUN sed -i s/-Xmx192m/-Xmx128m/ /opt/storageos/bin/eventsvc
RUN sed -i s/-Xmx256m/-Xmx128m/ /opt/storageos/bin/resourcesvc
RUN sed -i s/-Xmx1024m/-Xmx512m/ /opt/storageos/bin/rm
RUN sed -i s/-Xmx128m/-Xmx64m/ /opt/storageos/bin/objcontrolsvc
RUN sed -i s/-Xmx128m/-Xmx64m/ /opt/storageos/bin/provisionsvc
RUN sed -i s/-Xmx128m/-Xmx64m/ /opt/storageos/bin/authsvc

# adjust client ec buffer capacity
RUN grep -l 'object.ChunkTypeIEcDataBufferCapacity' /opt/storageos/conf/*.properties|grep -v standalone | while read f; do sed -r -i 's/(object.ChunkType(I|II)Ec(Code|Data)BufferCapacity)=[0-9]+/\1=$COREOS_MULTI_EC_BUFFER_CAPACITY/g' "\$f" ; done

# adjust number of threads
RUN grep -oE 'value= *\"[0-9]+' /opt/storageos/conf/shared-threadpool-conf.xml | cut -d'"' -f2| sort| uniq| while read num ; do test \$num -ge 20 && sed -i -r "s/value\s*=\s*\"\$num/value=\"\$((\$num/$COREOS_MULTI_THREADS_DIV))/g" /opt/storageos/conf/shared-threadpool-conf.xml; done

# set max threads count for parallel executor
RUN grep -l 'object.MaxParallelExecutorThreadCount' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.MaxParallelExecutorThreadCount\s*=\s*[0-9]*/object.MaxParallelExecutorThreadCount=$COREOS_MAX_PARALLEL_THREADS/g" "\$f"; done

# disable separate thread pools
RUN grep -l 'object.UseSeparateThreadPools' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.UseSeparateThreadPools\s*=\s*true/object.UseSeparateThreadPools=false/g" "\$f"; done

# set IOUtils cache limit
RUN grep -l 'object.IOUtilHeapCacheSizeInBytes' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.IOUtilHeapCacheSizeInBytes\s*=\s*[0-9]*/object.IOUtilHeapCacheSizeInBytes=$COREOS_IOUTIL_HEAP_CACHE_SIZE/g" "\$f"; done

# disable separate communicator executor
RUN grep -l 'separateExecutorPerCommunicator' /opt/storageos/conf/*-conf.xml | while read f; do sed -r -i "s/property\s*name=\"separateExecutorPerCommunicator\"\s*value=\"true\"/property name=\"separateExecutorPerCommunicator\" value=\"false\"/g" "\$f"; done

# configure number of DTs
RUN grep -l 'object.NumDirectoriesPerCoSForSystemDT' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.NumDirectoriesPerCoSForSystemDT\s*=\s*[0-9]*/object.NumDirectoriesPerCoSForSystemDT=$COREOS_NUM_DT_PER_COS/g" "\$f"; done
RUN grep -l 'object.NumDirectoriesPerCoSForUserDT' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.NumDirectoriesPerCoSForUserDT\s*=\s*[0-9]*/object.NumDirectoriesPerCoSForUserDT=$COREOS_NUM_DT_PER_COS/g" "\$f"; done

# adjust bloom filters
RUN grep -l 'object.BPlusTreeBloomFilterLocalEnabled' /opt/storageos/conf/*.properties|grep -v standalone |while read f; do sed -r -i "s/object.BPlusTreeBloomFilterLocalEnabled\s*=\s*(true|false)/object.BPlusTreeBloomFilterLocalEnabled=$COREOS_MULTI_BLOOM_ENABLED/g" "\$f"; done

RUN grep -l 'object.BPlusTreeBloomFilterRemoteEnabled' /opt/storageos/conf/*.properties|grep -v standalone |while read f; do sed -r -i "s/object.BPlusTreeBloomFilterRemoteEnabled\s*=\s*(true|false)/object.BPlusTreeBloomFilterRemoteEnabled=$COREOS_MULTI_BLOOM_ENABLED/g" "\$f"; done

# adjust DTs memory table properties and b+ tree caches
RUN for prop_val in ${COREOS_MULTI_DT_MEMORY_PROPS} ${COREOS_MULTI_BTREE_CACHE_PROPS} ; do prop=\$(echo \$prop_val|cut -d':' -f1); div=\$(echo \$prop_val|cut -d':' -f2); grep -l "\$prop" /opt/storageos/conf/*.properties|grep -v standalone |while read f; do grep -oE "\$prop=[0-9]+" "\$f"|grep -oE '[0-9]+'|while read value; do sed -i "s/\$prop=\$value/\$prop=\$((\$value/\$div))/g" "\$f"; done ; done; done

# adjust buffer manager
# set object.InitialBufferNumOnHeap to 1
RUN grep -l 'object.InitialBufferNumOnHeap' /opt/storageos/conf/*.properties|grep -v standalone |while read f; do grep -oE 'object.InitialBufferNumOnHeap=[0-9]+' "\$f"|grep -oE '[0-9]+'|while read value; do sed -i "s/object.InitialBufferNumOnHeap=\$value/object.InitialBufferNumOnHeap=1/g" "\$f"; done ; done

RUN grep -l 'object.BufferSize' /opt/storageos/conf/*.properties|grep -v standalone |while read f; do grep -oE 'object.BufferSize=[0-9]+' "\$f"|grep -oE '[0-9]+'|while read value; do sed -i "s/object.BufferSize=\$value/object.BufferSize=${COREOS_MULTI_BM_BUFFER_SIZE}/g" "\$f"; done ; done

RUN grep -l 'object.TotalBufferNumOffHeap' /opt/storageos/conf/*.properties|grep -v standalone |while read f; do grep -oE 'object.TotalBufferNumOffHeap=[0-9]+' "\$f"|grep -oE '[0-9]+'|while read value; do sed -i "s/object.TotalBufferNumOffHeap=\$value/object.TotalBufferNumOffHeap=${COREOS_MULTI_BM_BUFFER_COUNT}/g" "\$f"; done ; done

RUN echo 'ecs.minimum.node.requirement=1' >> /opt/storageos/ecsportal/conf/application.conf

#RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f
RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' "\$f"



# BufferNumOnHeap
RUN f=/opt/storageos/conf/blob-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="4"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/blobclient-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="45"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/datahead-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="45"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/dtquery-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/event-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/metering-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/objhead-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="45"/name="initialBufferNumOnHeap"\ value="5"/g' "\$f"
RUN f=/opt/storageos/conf/resource-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/rm-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/ssm-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/vnest-common-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="2"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"

RUN f=/opt/storageos/conf/cas-conf.xml; sed -i 's/key="object.InitialBufferNumOnHeap">8<\/prop>/key="object.InitialBufferNumOnHeap">1<\/prop>/g' "\$f"

RUN f=/opt/storageos/conf/cm-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="10"/name="initialBufferNumOnHeap"\ value="2"/g' "\$f"
RUN f=/opt/storageos/conf/cm-conf.xml; sed -i 's/key="object.InitialBufferNumOnHeap">50<\/prop>/key="object.InitialBufferNumOnHeap">2<\/prop>/g' "\$f"

RUN f=/opt/storageos/conf/georeceiver-conf.xml; sed -i 's/name="initialBufferNumOnHeap"\ value="60"/name="initialBufferNumOnHeap"\ value="1"/g' "\$f"
RUN f=/opt/storageos/conf/georeceiver-conf.xml; sed -i 's/key="object.InitialBufferNumOnHeap">60<\/prop>/key="object.InitialBufferNumOnHeap">1<\/prop>/g' "\$f"

RUN f=/opt/storageos/conf/hdfs-conf.xml; sed -i 's/key="object.InitialBufferNumOnHeap">8<\/prop>/key="object.InitialBufferNumOnHeap">1<\/prop>/g' "\$f"


#Turn Off EC
RUN sed -i s/object.EnableEcOptimization=true/object.EnableEcOptimization=false/  /opt/storageos/conf/shared.object.properties
RUN sed -i s/object.EcEncodeEnabled=true/object.EcEncodeEnabled=false/  /opt/storageos/conf/cm.object.properties
RUN sed -i s/object.totalDataBufferNumber=8/object.totalDataBufferNumber=0/  /opt/storageos/conf/cm.object.properties
RUN sed -i s/object.totalCodeBufferNumber=16/object.totalCodeBufferNumber=0/  /opt/storageos/conf/cm.object.properties

#Turn off geo replayer scanner
RUN sed -i s/geoReplayerScannerEnabled=true/geoReplayerScannerEnabled=false/ /opt/storageos/conf/shared.object.properties

#Turn on Heap Dump
RUN sed -i s/DoHeapDumpAtSelfStop=false/DoHeapDumpAtSelfStop=true/ /opt/storageos/conf/shared.object.properties
RUN sed -i s/DumpsNumberLimit=2/DumpsNumberLimit=8/ /opt/storageos/conf/shared.object.properties
RUN sed -i s/ZippedDumpsNumberLimit=2/ZippedDumpsNumberLimit=8/ /opt/storageos/conf/shared.object.properties

# ?????
RUN sed -i s/SizePerDumpThresholdBytes=134217728/SizePerDumpThresholdBytes=268435456/ /opt/storageos/conf/shared.object.properties
RUN sed -i s/object.BPlusTreeWriterCacheSize=1600/object.BPlusTreeWriterCacheSize=512/ /opt/storageos/conf/blobsvc.object.properties
RUN sed -i s/MaxReplayRegionsCount=1000/MaxReplayRegionsCount=128/ /opt/storageos/conf/shared.object.properties
RUN sed -i s/MaxReplayRegionsCount=32/MaxReplayRegionsCount=128/ /opt/storageos/conf/shared.object.properties
#RUN sed -i s/MaxIncrementalReplayJRMajorCount=3/MaxIncrementalReplayJRMajorCount=0/ /opt/storageos/conf/shared.object.properties


#Enable throttling of incoming traffic in s3-head-conf.xml
RUN sed -i 's/"maxThreads" value="1000"/"maxThreads" value="30"/' /opt/storageos/conf/s3-head-conf.xml

#Enable GC for partial chunks
RUN sed -i '/HeapDumpOnOutOfMemoryError/ a -XX:MaxDirectMemorySize=1G \\\\' /opt/storageos/bin/metering
RUN sed -i '/MaxHeapMemoryThresholdPercent/ a <prop key="object.EnableEcOptimization">true</prop>' /opt/storageos/conf/cm-conf.xml
RUN sed -i '/GeosenderEnabled/ a <prop key="object.EnableEcOptimization">true</prop>' /opt/storageos/conf/metering-conf.xml

#Tune garbage collection to occur much more aggressively
RUN sed -i '/"replication_checker_task_result_poll_sleep_millis"/c\        <config:duration name="replication_checker_task_result_poll_sleep_millis" value="10000" unit="ms"/>' /opt/storageos/conf/*-cf-conf.xml
RUN sed -i '/"list_time_safe_guard"/c\            <config:duration name="list_time_safe_guard" value="5" unit="s" description="Safe guard to list ChunkGcScanTasks in case time on nodes is not synchronized."/>' /opt/storageos/conf/client-cf-conf.xml
RUN sed -i '/"cache_expire"/c\            <config:duration name="cache_expire" value="2" unit="min" description="Scan tasks cache expiration time"/>' /opt/storageos/conf/client-cf-conf.xml
RUN sed -i '/"sleep_obj_interval"/c\            <config:long name="sleep_obj_interval" value="10000"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"run_interval"/c\            <config:duration name="run_interval" value="5" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"new_run_interval"/c\            <config:duration name="new_run_interval" value="5" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"checkpoint_interval"/c\            <config:duration name="checkpoint_interval" value="1" unit="s"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"error_interval"/c\            <config:duration name="error_interval" value="5" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"dump_interval"/c\            <config:duration name="dump_interval" value="5" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"ob_update_validation_check_interval"/c\            <config:duration name="ob_update_validation_check_interval" value="20" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/""/c\            <config:duration name="ob_update_check_interval" value="10" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"geo_ship_check_interval"/c\            <config:duration name="geo_ship_check_interval" value="10" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"chunk_copy_check_interval"/c\            <config:duration name="chunk_copy_check_interval" value="10" unit="min"' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"refresh_interval_initial"/c\            <config:duration name="refresh_interval_initial" value="5" unit="min"' /opt/storageos/conf/cm-cf-conf.xml
RUN sed -i '/"refresh_interval"/c\            <config:duration name="refresh_interval" value="5" unit="min"' /opt/storageos/conf/cm-cf-conf.xml
RUN sed -i '/"client_cache_refresh"/c\        <config:duration name="progress.client_cache_refresh" value="5" unit="min" description="CT client progress cache refresh time"/>' /opt/storageos/conf/client-cf-conf.xml
RUN sed -i '/"freeblock_task_delay"/c\        <config:duration name="freeblock_task_delay" value="10" unit="min" description="Chunk segment block free delay."/>' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"timeout"/c\            <config:duration name="timeout" value="3" unit="h" description="Task timeout value for delete job scanner"/>' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"job_pause_interval"/c\            <config:duration name="job_pause_interval" value="1" unit="ms" upgradeOverride="true" description="Pause interval between delete jobs"/>' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"cleanup_job_delay"/c\        <config:duration name="cleanup_job_delay" value="2" unit="min" description="Cleanup for object entry reclaim delay."/>' /opt/storageos/conf/gc-cf-conf.xml
RUN sed -i '/"list_max_size"/c\                <config:long name="list_max_size" value="1000" upgradeOverride="true" description="Maximum number of scan tasks to list for ChunkGcScanTracker"/>' /opt/storageos/conf/client-cf-conf.xml

EOF
