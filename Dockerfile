# FROM python:3.8-slim-buster
FROM tensorflow/tensorflow:2.0.0-py3
WORKDIR /python-docker

COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt
# RUN PYTHONIOENCODING=utf-8 python -m laserembeddings download-models
RUN pip install --no-cache-dir -r requirements.txt
RUN PYTHONIOENCODING=utf-8 python -m laserembeddings download-models

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
