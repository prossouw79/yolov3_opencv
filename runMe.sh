#!/bin/bash

echo "Removing INPUT ramdisk"
sudo umount input
rm -rf input

echo "Creating INPUT ramdisk"
mkdir input
sudo mount -t tmpfs -o rw,size=16M tmpfs $PWD/input

df | grep $PWD/input

echo "Starting Containers"
docker-compose down 
docker-compose up --build -d

watch -n 1 "tree input/"