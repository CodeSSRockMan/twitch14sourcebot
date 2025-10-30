# Alpine-based Dockerfile for the project app container
FROM python:3.11-alpine
WORKDIR /app
RUN apk add --no-cache git bash
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
