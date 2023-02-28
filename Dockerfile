FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY src src
RUN cd /src
WORKDIR /src
CMD python app.py