FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install -y libpcap-dev tcpdump

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]
