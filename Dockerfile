FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y --fix-missing libusb-1.0-0 && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir pyusb

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "DOA.py", "128.148.140.22"]