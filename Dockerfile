FROM python:3.12-slim

RUN mkdir /opt/qbus-scraper
WORKDIR /opt/qbus-scraper

EXPOSE 5000

COPY requirements.txt /opt/qbus-scraper/requirements.txt
RUN pip install -r requirements.txt

COPY / /opt/qbus-scraper

CMD ["python", "/opt/qbus-scraper/src/scraper/run.py"]
