FROM python:3.11-slim AS builder
COPY requirements.txt .

RUN pip install --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /src

COPY --from=builder /root/.local /root/.local
COPY /src .

ENV PYTHONPATH /src

ENTRYPOINT  ["python", "/src/Blockchain/main.py"]