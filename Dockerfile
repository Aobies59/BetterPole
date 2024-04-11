# Use a lightweight Python image
FROM python:3.9

# Set a working directory for your script
WORKDIR /app

# Copy your Python script to the container
COPY requirements.txt .
COPY better_pole.py .
COPY .token .
COPY pole_day.json .
COPY score.json .

# Install any required dependencies (if applicable)
RUN pip install -r requirements.txt

# Run your Python script as the entrypoint
CMD ["python", "better_pole.py"]