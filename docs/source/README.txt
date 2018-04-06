To update markdown (.md) documents to restructured (.rst) run the update-docs.sh script with ./update-docs.sh,
you will be prompted to authenticate for sudo.

This script downloads an Ubuntu-based docker image from Dockerhub with pandoc installed.
When run the script uses git to find all changes to .md files and feeds them into the pandoc container.
The container then spits out restructured versions of the markdown documents.

NOTE: Be sure to run git status after running the script as new .rst files will be created if they do not already exist.
These files will need to be added before committing the changes.
