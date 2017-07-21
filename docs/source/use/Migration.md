# Migration

## General Cases

Most migration cases can be handled by a great tool we wrote called ecs-sync, found [here](https://github.com/EMCECS/ecs-sync).

## HDFS

An HDFS migration is possible with s3distcp or distcp. Please note that if using s3distcp with the s3a driver, it needs to be the latest version or you may run into issues. If using distcp, ECS's HCFS driver "viprfs" will need to be set up as a secondary FS and the distcp made from `hdfs://...` to `viprfs://...`. Instructions for installing the HCFS driver can be found [here](http://doc.isilon.com/ECS/3.0/DataAccessGuide/wwhelp/wwhimpl/js/html/wwhelp.htm#href=vipr_c_hdfs_ViPRHDFS_intro.html).

