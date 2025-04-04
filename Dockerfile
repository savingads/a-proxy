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

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY package*.json ./
RUN npm install

RUN python ./database.py
RUN python ./create_sample_personas.py

EXPOSE 5002

# Run with host 0.0.0.0 to make the application accessible outside the container
CMD ["python", "app.py", "--host", "0.0.0.0"]
