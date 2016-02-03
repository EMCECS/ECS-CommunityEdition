
## Update 2015-01-19: v2.2.0.0
- Updated Docker Image to [ECS Software v2.2](https://support.emc.com/docu62941_ECS_2.2_Release_Notes.pdf?language=en_US&language=en_US)
- **Note:** Due to export restrictions, ECS Community Edition does not include encryption functionality.
- Updated install scripts to work with ECS 2.2.  **Note:** if you want to install ECS 2.1, please download the install scripts for 2.1 from github.  The changes to install 2.2 are not backward-compatible.

## Update 2015-12-29: v.2.1.0.2
- Updated Docker Image to [ECS Software v2.1 Hotfix 2](https://support.emc.com/docu62377_ECS_2.1_HF2_Readme.txt?language=en_US&language=en_US)
- Various improvements to retry code
- Changes to and fixes for VDC creation, esp. in multi-VDC builds
- VDC Provisioning may now be deliberately omitted with -SkipVDCProvision
- Modification of storage server (SSM) parameters to better support smaller disk configurations
- Pre-existing docker images no longer removed during installation
- Addition of systemd script for container start/stop
- Fixes for import, formatting, and other assorted minor bugs


## Update 2015-11-30
- Updated Docker Image to a [ECS Software v2.1 Hotfix 1](https://support.emc.com/docu62132_ECS_2.1_HF1_Readme.txt?language=en_US&language=en_US)
- Users can now optionally specify docker image via command-line arguments in step1.
- Installation script provides more inforamation to user, proceeds depending on services' availability.
- Fix for authentication issues resulting from default provisioning.

