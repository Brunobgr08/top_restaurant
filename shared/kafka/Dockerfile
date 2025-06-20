FROM python:3.10-slim

WORKDIR /app

COPY create_topics.py .

RUN pip install kafka-python

CMD ["python", "create_topics.py"]