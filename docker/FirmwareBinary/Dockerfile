FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the analyzer script
COPY firmware_analysis.py .

# Make the script executable
RUN chmod +x firmware_analysis.py

# Set the entry point
ENTRYPOINT ["python", "firmware_analysis.py"]

# Default command (can be overridden)
CMD ["--help"]
