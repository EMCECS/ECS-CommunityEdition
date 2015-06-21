class ecs3datanodes::configure
{
#Clean up first
exec{"Clean_Up":
 command =>"/usr/bin/umount /dev/sdc1;/usr/bin/rm -rf /ecs /data /host /var/log/vipr/",
 
}->

# Run a yum update
exec{"yum_update":
 command => "/usr/bin/yum -q -y update; ",
 timeout => 1800,
 before => exec["install_wget"],
 require => exec["Clean_Up"]
}->
# Install wget
exec{"install_wget":
 command => "/usr/bin/yum install wget -y ",
 timeout => 1800,
 require => exec["yum_update"]
}->
#Disable SELinux
exec{"Disable_SELinux":
 command => "/usr/sbin/setenforce 0 ",
}->

#Get Preperation script
exec{"Get_Prepration_script":
 command => "/usr/bin/wget -q https://emccodevmstore001.blob.core.windows.net/test/additional_prep.sh -O /tmp/additional_prep.sh",
 creates => "/tmp/additional_prep.sh",
 require=>exec["Clean_Up"]
}->

file{"/tmp/additional_prep.sh":
 mode => 777,
 require => exec["Get_Prepration_script"]
}->

file { [ "/ecs/","/ecs/uuid-1/","/host/", "/host/files/","/host/data/", "/data/","/var/log/vipr","/var/log/vipr/emcvipr-object/" ]:
 ensure => "directory",
 owner=>"root",
 group=>"444",
 before=>file["/host/data/network.json"]
}->

file {"/host/data/network.json":
 ensure  => file,
 owner=>"root",
 group=>"444",
 content =>"{\"private_interface_name\":\"eth0\",\"public_interface_name\":\"eth0\",\"hostname\":\"$hostname\",\"public_ip\":\"$ipaddress_eth0\"}",
 before =>file["/host/files/seeds"],
}->

file {"/host/files/seeds":
 ensure  => file,
 owner=>"root",
 group=>"444",
 content => "10.0.0.4,10.0.0.5,10.0.0.6",
 before  => exec["Create_partition"],
 require => file["/host/data/network.json"]
 }->

#Create Partition Hard rive
exec{"Create_partition":
 command => '/usr/bin/echo -e "o\nn\np\n1\n\n\nw" | fdisk /dev/sdc ',
 require => exec["Get_Prepration_script"]
}->

#Format New Drive
exec{"Format_drive":
 command => '/usr/sbin/mkfs.xfs -f /dev/sdc1 ',
 require => exec["Create_partition"]
}->

#Mount Drive
exec{"Mount_drive":
 command => '/usr/bin/mount /dev/sdc1 /ecs/uuid-1 ',
 require => exec["Format_drive"]
}->
#run script New Drive
exec{"run_preperation_script":
 command => '/tmp/additional_prep.sh /dev/sdc1 ',
 require => exec["Mount_drive"]
}->
#fix permission if needed
exec{"fix_permission":
 command => '/usr/bin/chown -R 444 /ecs /data /host /var/log/vipr/emcvipr-object/ ',
}->

#Install Docker RPM
exec{"install_docker":
 command => '/usr/bin/yum install -q -y docker'

}->


#disable Docker linux security
exec{"disable_docker_lxc":
 command => '/usr/bin/rm -f /etc/sysconfig/docker',
 notify => service["docker"]
}->

#Start Docker Service
service { "docker":
  ensure => "running",
}->

#pull docker image
exec{"docker_pull_image_ecs":
 command => '/usr/bin/docker pull emccode/ecsobjectsw:v2.0',

}->
#start docker conatiner
exec{"Start_ecs_container":
 command =>"/usr/bin/docker run -d -e SS_GENCONFIG=1 -v /ecs:/disks -v /host:/host -v /var/log/vipr/emcvipr-object:/opt/storageos/logs -v /data:/data:rw --net=host docker.io/emccode/ecsobjectsw:v2.0",
}->
file {"/host/ecscontainer":
 ensure  => file,
 content => "ecscontainer",
 }




}
