FROM python:3.11-slim

WORKDIR /app

COPY requirements-streaming.txt /app/requirements-streaming.txt
RUN pip install --no-cache-dir -r /app/requirements-streaming.txt

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.streaming.order_producer"]
