#!/bin/bash

for file in combined*
do
	echo "**********"
	echo $file
	./idm image upload $file --size 64 --address 9E:D8:18:C5:D9:CC
done
