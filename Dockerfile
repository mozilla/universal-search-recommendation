FROM python:3.5.1

WORKDIR /app
COPY . /app

RUN pip install --upgrade --no-cache-dir -r app/requirements.txt \
    && python setup.py install
