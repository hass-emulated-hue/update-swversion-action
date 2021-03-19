FROM python:3.9-alpine

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src action

CMD ["python3", "-u", "/action/main.py"]
