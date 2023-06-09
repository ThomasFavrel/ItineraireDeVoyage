FROM python:3.9-slim

WORKDIR /app2

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY etl.py /app2/
COPY requirements.txt /app2

RUN pip3 install -r requirements.txt
RUN mkdir /app2/Data

CMD ["python3", "etl.py"]