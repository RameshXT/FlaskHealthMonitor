# BUILD
FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# DEPLOY
FROM python:3.9-slim

ENV VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
