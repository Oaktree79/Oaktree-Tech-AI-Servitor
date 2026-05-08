FROM python:3.11-slim

WORKDIR /app
COPY python /app/python
WORKDIR /app/python

RUN python -m pip install -U pip && python -m pip install -e ".[dev]"

EXPOSE 8765
ENV SERVITER_ADMIN_PASSWORD=change-me
CMD ["serviter-service", "--root", "/app/python", "--mode", "api", "--host", "0.0.0.0", "--port", "8765"]
