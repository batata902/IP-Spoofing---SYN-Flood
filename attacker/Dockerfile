FROM python:3.12-slim

WORKDIR /dos

COPY requirements.txt .

RUN apt-get update && apt-get install net-tools
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/bash"]
