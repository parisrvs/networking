# Base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /networking

# Install dependencies
COPY ./requirements.txt /tmp/requirements.txt

# Create a virtual environment and install dependencies
# Set the user to use when running this image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Copy the project code into the container
COPY ./networking /networking

# Set the path to the virtual environment
ENV PATH="/py/bin:$PATH"
