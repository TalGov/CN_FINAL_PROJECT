#!/bin/bash

python3 ../server_quic.py -p $1 -m $2 -s $3 > server_output.txt &

sleep 0.1

python3 ../client_quic.py > client_output.txt &

wait