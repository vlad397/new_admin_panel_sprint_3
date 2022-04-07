FROM python:3.9.0

WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python -u postgres_to_es/etl.py
