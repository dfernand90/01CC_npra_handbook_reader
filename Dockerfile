FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Port is provided dynamically by Cloud Run

# Command to run
CMD ["python", "server.py"]
