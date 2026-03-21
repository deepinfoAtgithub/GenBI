# Use official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies and Microsoft ODBC Driver 18
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg2 unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "azure-multi-agent.py", "--server.port=8501", "--server.address=0.0.0.0"]
