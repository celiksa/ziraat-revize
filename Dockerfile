FROM python:3.11.8-bullseye
COPY . /src
WORKDIR /src
COPY requirements.txt .
RUN pip3 install -r requirements.txt 
COPY . .
EXPOSE 8510
CMD python flaskApp.py
