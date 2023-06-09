FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app
run mkdir data

COPY ./postgres/postgres.py /app
COPY ./postgres/param.py /app
COPY ./postgres/db_init.py /app
COPY api.py /app

# Plus besoin des fichiers csv avec mongo dans l'api
COPY ./data/csv/POI.csv /app/data
COPY ./data/csv/theme_unique.csv /app/data
COPY ./data/csv/theme.csv /app/data

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

EXPOSE 8000

#run python3 db_init.py

CMD ["uvicorn", "api:api", "--reload", "--host", "0.0.0.0", "--port", "8000"]
