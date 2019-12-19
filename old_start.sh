#! /bin/sh

TAG=tf-2.0

if [ $# -eq 1 ]; then
	if [ "$1" = "--build" ]; then
		# Build the docker container
		docker build -t $TAG .
	fi
fi


# Run the docker container
docker run -d --runtime=nvidia -v $(pwd)/src:/tf/src -p 0.0.0.0:6006:6006 -p 8888:8888 $TAG
