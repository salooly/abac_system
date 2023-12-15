FROM ubuntu:latest

WORKDIR /usr/src/abac_system

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y pip


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
