FROM python:3.8-slim-buster
WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN PYTHONIOENCODING=utf-8 python3 -m laserembeddings download-models

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
