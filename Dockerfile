FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# COPY . ./
COPY app app
CMD python app/app.py