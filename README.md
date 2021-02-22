# jij-api

A place to provide simple online services for Jobs In Japan

#Notes on running the docker containers

#Run the database container
docker run -d --name my-test-db -p 5432:5432 -v postgres-volume:/var/lib/postgresql/data postgres-image

#Connecting to db container 
docker exec -it my-test-db bash

#Running main app
./start.sh 

#tailng logs
docker logs --follow <dockerid>
