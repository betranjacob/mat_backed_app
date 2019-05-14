Instructions to test the Image. 

Build docker image: 
==================
sudo docker build --tag backend-server:latest .

Run docker image: sudo docker run --name backend-server -p 8084:8084 backend-server:latest

Subcriber for CarStatus:
=======================
mosquitto_sub -v -d -h localhost -p 8084 -t carStatus

Sunscribe for Events:
====================
mosquitto_sub -v -d -h localhost -p 8084 -t events

Run gps source simulator test:
=============================
cd test
python3 gpu_source_simulator.py

Check logs from container:
=========================
sudo docker logs -f <container-id>






