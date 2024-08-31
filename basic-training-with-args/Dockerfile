# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py .
COPY titanic_processed.csv .

CMD ["python", "train.py"]
