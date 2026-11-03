FROM python:3.9-slim
WORKDIR /app
COPY app/requirements.txt .

# Upgrade pip, setuptools, and wheel to ensure smooth wheel parsing
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ .
EXPOSE 5000
CMD ["python", "/app/main.py"]
