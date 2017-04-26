For systems running systemd, you can start and stop the ECS container with the system using this script.  To install, run:

```
sudo cp docker.ecsmultinode.service /etc/systemd/system/
sudo systemctl enable docker.ecsmultinode.service
```

Then your docker container will restart with the system.  Also be sure that docker itself is set to restart with the system:

```
sudo systemctl enable docker.service
```

