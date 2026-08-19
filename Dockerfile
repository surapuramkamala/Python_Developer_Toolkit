# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and test suite
COPY document_toolkit.py .
COPY tests/ tests/

# Create application folders
RUN mkdir -p input output logs

# Add a default sample file so standalone `docker run` has something to process
RUN echo "Sample text for document toolkit processing." > input/sample.txt

# Run unit tests at build time
RUN python -m unittest discover -s tests -v

CMD ["python", "document_toolkit.py"]