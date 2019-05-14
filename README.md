# Instructions to test the solution.

### Build image: 
sudo docker build --tag backend-server:latest .

### Run image:
sudo docker run --name backend-server -p 8084:8084 backend-server:latest

### Subcriber for CarStatus:
mosquitto_sub -v -d -h localhost -p 8084 -t carStatus

### Sunscriber for Events:

mosquitto_sub -v -d -h localhost -p 8084 -t events

### Run gps source simulator test:

cd test

python3 gpu_source_simulator.py


### Command to view container logs:
sudo docker logs -f container-id






