#/bin/bash

echo $'@@@@\n @ Building image\n @@@@'
docker build -t $1 .
rm -rf mount
mkdir mount
mkdir mount/front
echo $'@@@@\n @ Running container\n @@@@'
docker run -v "$(pwd)"/mount/front:/mnt -p 5000:5000 $2 $1
