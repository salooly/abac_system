# ABAC Task
This project is a simple Attribute-Based Access
Control system.\
In order for everything to function properly it's important to set the environment correctly.

First, make sure to initiate a MongoDB, as it's a crucial part fot the program to function.

```
docker run -idt -p 27017:27017 --name abac-mongo mongo:latest
```

Afterward, build the API image using the following command:
```
docker build -t abac-api .
```

Now, run the API container:
```
docker run -idt -p 80:80 --name abac-api -e MONGO_HOST={MONGO_IP} abac-api
```
**NOTE:**
Make sure the hostname is configured correctly. Feel free to use `docker inspect abac-mongo` to check the container's IP

After all is set correctly, the API should be available on port 80.
# Assumptions
* There has to be a match between the attributes type and the value
* Same goes to conditions, meaning that the condition value must match the attribute they refer to
* Different operators apply to different data types. For example, a boolean only supports '=', integers support
 '<', '>', '=', and string supports all operators. The API won't allow mismatching values.
 
# API Docs
Since the project is based on FastAPI, you can access the docs once you initiate the API.\
It should be in the following url `http://localhost/docs` (unless configured differently)\
For additional resources, feel free to take a look into the postman folder where you can find postman requests.