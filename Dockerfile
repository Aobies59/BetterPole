# Use a lightweight Python image
FROM python:3.9

# Set a working directory for your script
WORKDIR /betterpole

COPY --from=source . ./

# Install any required dependencies (if applicable)
RUN ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime
RUN pip install -r ./requirements.txt

# Run your Python script as the entrypoint
CMD ["python","-u","better_pole.py"]
