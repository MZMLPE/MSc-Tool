FROM python:3.8.10
LABEL maintainer="mzml@cin.ufpe.br"
RUN apt-get update
RUN apt-get install ffmpeg libgl1 libsm6 libxext6  -y 
RUN pip install opencv-python

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]

