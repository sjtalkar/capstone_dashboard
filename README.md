# capstone_dashboard Capstone Dashboard
This repository is the visual dashboard element of the full Himalaya Dataset project developed in Dagshub


## Restructure the Dash application folder structure



## Create the Dockerfile
FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# COPY . ./ Since we moved everthing to app folder, the image only needs everything from the app folder
COPY app app
CMD python app/app.py


## Create Docker Image to Deploy Dash Application

If you want to build the all the elements including setting the packages, use no-cache:

`docker build -t caps_dashboard --no-cache .`

If you only want elements that have changed to build:

`docker build -t caps_dashboard  . `


Check if there are any running images

`docker ps`


Check all available images built 

`docker image ls`

Run an image

`docker run -p 8050:8050 caps_dashboard`

Prune non-running redundant images

`docker sytem prune`

Note that the host is set to 0.0.0.0 in the app.py Dash file

The application can be run as https://localhost:8050
