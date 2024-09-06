#!/bin/bash

python3 ../server_quic.py > server_output.txt &

sleep 0.01

python3 ../client_quic.py > client_output.txt &

wait