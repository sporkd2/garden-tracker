FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV DATABASE_PATH=/app/data/garden.db
ENV PORT=8000

# Run the application
CMD ["python", "app.py"]
