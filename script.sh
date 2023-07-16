#!/bin/bash

while true
do
    timeout -k 5h 5h python3 gameServer.py
    sleep 2
done