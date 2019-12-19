#! /bin/sh

TAG=tf-2.0

if [ $# -eq 1 ]; then
	if [ "$1" = "--build" ]; then
		# Build the docker container
		docker build -t $TAG .
	fi
fi


# Run the docker container
docker run -d --runtime=nvidia -v $(pwd)/main:/tf/main      \
	-v /mnt/data/dl_code_gen/models:/tf/data/models     \
	-v /mnt/data/dl_code_gen/datasets:/tf/data/datasets \
	-p 0.0.0.0:6006:6006 -p 8888:8888 $TAG
