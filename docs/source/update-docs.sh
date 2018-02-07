#!/bin/bash

dimage="captntuttle/ubuntu-pandoc"
sts_msg="updating .rst for: "

echo "building docker image $dimage from Dockerfile"

for i in $(git diff --name-only --relative .); 
do
	if [[ $i == *.md ]]; then
		echo $sts_msg$i && sudo docker run \
		-v `pwd`:/source $dimage -f markdown -t rst \
		-o $(sed "s/.md/.rst/g" <<< "$i") $i; 
	fi
done


