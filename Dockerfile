FROM python:3.11.4-slim

COPY requirements.txt .
RUN pip install -r requirements.txt && apt-get update
RUN apt-get install -y curl 
RUN apt-get install -y iputils-ping 
RUN apt-get install -y net-tools

COPY . .