## Capstone Dashboard repository : capstone_dashboard
This repository is the visual dashboard element of the full Himalaya Dataset project developed in Dagshub


### Restructure the Dash application folder structure

The series of articles on Medium starting out with [Structuring your Dash App](https://towardsdatascience.com/structuring-your-dash-app-e33d8e70133e) served as inspiration to create a Docker image and serve up the application
in a Docker container. We started out by creating a isolated folder structure for the Dash app as suggested in the article

Folder PATH listing for volume Google Drive

```
Folder PATH listing for volume Google Drive
Volume serial number is 1983-1116
Drive:.
¦   README.md
¦   requirements.txt
¦   Dockerfile
¦   
+---app
    ¦   app.py
    ¦   
    +---passwords
    ¦       mapbox_api_key.pickle
    ¦       
    +---data
    ¦   +---raw_data
    ¦   ¦       members.csv
    ¦   ¦       exped.csv
    ¦   ¦       refer.csv
    ¦   ¦       peaks.csv
    ¦   ¦       
    ¦   +---nhpp
    ¦           nhpp_peaks.csv
    ¦           peakvisor_peaks.csv
    ¦           manually_collected_peaks.csv
    ¦           non_matching_peaks.csv
    ¦           merged_nepal_peaks.csv
    ¦           
    +---lib
    ¦   ¦   data_network.py
    ¦   ¦   read_data.py
    ¦   ¦   social_media.py
    ¦   ¦   topic_modeling_visualization.py
    ¦   ¦   
    ¦   +---data_preparation
    ¦   ¦   ¦   member_data.py
    ¦   ¦   ¦   peaks_data.py
    ¦   ¦   ¦   
    ¦   +---data_collection
    ¦           nhpp_dataset.py
    ¦           
    +---docs
    ¦       credits.md
    ¦       Himalayan Database Papers Reviewed.docx
    ¦       
    +---pages
    ¦   ¦   peak_expeditions.py
    ¦   ¦   spatial_analysis.py
    ¦   ¦   not_found_404.py
    ¦   ¦   topic_visualization.py
    ¦   ¦   parallel_coords.py
    ¦   ¦   
    +---color_theme
    ¦   ¦   color_dicts.py
    ¦   ¦   
    +---assets
            pexels-ashok-sharma-11595461-cropped.jpg
            spatial_analysis_1_1920_2030.html
            Everest_Visualization_Two_topics.html
            mapbox-gl.css
           

```

Whereas in the Dagshub, app.py is under the root, here an app folder is created to contain the app.py file that will create the dash server with the hostname as seen below:

`
app.run_server(host="0.0.0.0", debug=True)
`

A requirements file was created using pipreqs package. This captures all the Dash dependencies as well as Python data manipulation libraries.
The pipreqs package was used instead of pip freeze of the environment to make sure that only the packages imported into the project are present in the requirements file. Since this repository is to be hosted on a free tier site, not all the machine learning code and data is set up here. 
The unsupervised learning visual output in the form of an html is carted over from [the main capstone Dagshub repository](https://dagshub.com/sjtalkar/capstone_himalayas) and served up as a page.
This is the file that can be found in the app/assets folder called Everest_Visualization_Two_topics.html.

### Setup Docker on local machine

Docker was installed from [this official site](https://docs.docker.com/desktop/install/windows-install/).
With the latest version (4.16), errors were encountered in ther log files during startup. The Docker Desktop would not startout and the log errors
indicated a missing file. To overcome this issue, a previous version 4.8.2 of Docker desktop was installed and when this version is started out, it indicated that Windows Subsystem for Linux 
WSL needs to by updated. With an update it is likely that a more recent version of the Docker Desktop can be installed. [Check this site to upgrade the WSL version](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)

`
wsl --update
`

### Create the Dockerfile 

The various layers of the building the Docker image are captured in the Dockerfile. You can choose to run all with the no-cache option or only those that have changed, without this option.

```FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# COPY . ./ Since we moved everthing to app folder, the image only needs everything from the app folder
COPY app app
CMD python app/app.py
```

### Create Docker Image to Deploy Dash Application

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

Stop a running container in another command line window:

Get the container id of the running container with 

`docker ps`
```
CONTAINER ID    IMAGE            COMMAND                  CREATED     STATUS     PORTS NAMES
941afd62a890    caps_dashboard   "/bin/sh -c 'python …"   2 hours ago Up 2 hours 0.0.0.0:8050->8050/tcp zen_lamarr
```

`docker stop 941afd62a890`

Prune non-running redundant images

`docker sytem prune`

Note that the host is set to 0.0.0.0 in the app.py Dash file

The application can be run as https://localhost:8050
