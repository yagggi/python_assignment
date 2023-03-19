FROM python:3.7.16-alpine

# packages below is required by cryptography, which is required by PyMySQL
RUN apk add --update --no-cache gcc libc-dev libffi-dev

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt