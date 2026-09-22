FROM python:3.13-slim

RUN pip install --no-cache-dir "psycopg[binary]~=3.2"

COPY provision.py /provision.py

CMD ["python", "/provision.py"]
