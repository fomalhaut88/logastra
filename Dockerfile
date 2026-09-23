FROM python:3.12-slim

WORKDIR /app

RUN pip install -U pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["fastapi", "run", "--entrypoint", "src:app", "--port", "8000"]
