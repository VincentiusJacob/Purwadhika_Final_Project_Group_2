FROM python:3.12-slim

WORKDIR /app

ARG LIVEKIT_URL LIVEKIT_API_KEY LIVEKIT_API_SECRET OPENAI_API_KEY
ENV LIVEKIT_URL=$LIVEKIT_URL \
    LIVEKIT_API_KEY=$LIVEKIT_API_KEY \
    LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET \
    OPENAI_API_KEY=$OPENAI_API_KEY

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python download_model.py 

# USER nobody

EXPOSE 8000 8501
