# Use Python as the base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create ephe directory and copy ephemeris files
RUN mkdir -p /app/ephe
COPY ephe/ephe/*.se1 /app/ephe/

# Copy the rest of the application
COPY . .

# Debug: List contents of ephe directory
RUN echo "Listing contents of /app/ephe:" && ls -la /app/ephe

# Expose port 5000
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
