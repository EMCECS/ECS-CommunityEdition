This directory contains the CA certificate for the internal EMC SSL proxy.  If you're installing ECS Community edition on a system behind the EMC firewall, you will need to install this certificate in your list of trusted CAs.  To do this on CentOS, do the following:

```
cp emc_ssl.pem /etc/pki/ca-trust/source/anchors/
update-ca-trust extract
```

Do this on each host and restart the docker process:

```
systemctl restart docker
```

