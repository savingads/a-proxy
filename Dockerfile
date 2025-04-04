FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    chromium \
    openvpn \
    nodejs \
    npm \
    && apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN ls

WORKDIR /app

ADD . /app


RUN pip install --upgrade pip && pip install -r requirements.txt

# This needs to be added to the requirements file
RUN pip install pyyaml pywb shot_scraper

COPY package*.json ./
RUN npm install

RUN apt update && apt install openvpn -y && apt install -y chromium

RUN python ./database.py
RUN python ./create_sample_personas.py

EXPOSE 5002

CMD ["python", "app.py"]
