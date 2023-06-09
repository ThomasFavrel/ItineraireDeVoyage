FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY ExtractData.sh /app
COPY pymongo.py /app
COPY requirements.txt /app

RUN pip3 install -r requirements.txt
RUN sh ExtractData.sh

EXPOSE 27021

CMD ["python3", "pymongo.py"]