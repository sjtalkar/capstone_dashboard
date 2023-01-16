# capstone_dashboard Capstone Dashboard
This repository is the visual dashboard element of the full Himalaya Dataset project developed in Dagshub


## Restructure the Dash application folder structure

We start out by creating a isolated folder structure for the Dash app. 

Folder PATH listing for volume Google Drive

```
+---app
    +---passwords
    +---data
    ¦   +---HIMDATA-2.5-Spring2022
    ¦   +---raw_data
    ¦   +---nhpp
    ¦   +---social_media_data
    ¦       +---tweet_search_data
    ¦       +---cleaned_tweets
    ¦       +---models
    ¦       ¦   +---lda_models
    ¦       ¦   +---gsdmm_models
    ¦       +---visual_creation_data
    +---lib
    ¦   +---__pycache__
    ¦   +---data_preparation
    ¦   ¦   +---__pycache__
    ¦   +---data_collection
    +---docs
    +---pages
    ¦   +---__pycache__ 
    +---color_theme
    ¦   +---__pycache__
    +---assets

```

Whereas in the Dagshub, app.py is under the root, here an app folder is created 



## Create the Dockerfile
```FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# COPY . ./ Since we moved everthing to app folder, the image only needs everything from the app folder
COPY app app
CMD python app/app.py
```

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
