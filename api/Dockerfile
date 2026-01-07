FROM python:3.12-slim

WORKDIR /app

# Install AWS CLI (works on both ARM and x86)
RUN apt-get update && \
    apt-get install -y curl unzip groff less && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . . 

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
