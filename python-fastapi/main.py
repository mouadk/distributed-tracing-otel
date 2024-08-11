import logging
import os
import asyncio
import sys

from fastapi import FastAPI, Request
from aiokafka import AIOKafkaConsumer
import asyncpg
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel
import httpx
import uvicorn
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace as otel_trace


POSTGRES_USER = os.getenv("POSTGRES_USER", "testuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "testpass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "testdb")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "test-topic")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "test-group")

HELLO_SERVICE = os.getenv("HELLO_SERVICE")

HTTPXClientInstrumentor().instrument()
AsyncPGInstrumentor().instrument()
KafkaInstrumentor().instrument()

otel_trace.set_tracer_provider(TracerProvider())
tracer_provider = otel_trace.get_tracer_provider()

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# FastAPI application
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)


# Database and Kafka consumer setup
async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL
        )
    """)
    await conn.close()


class Message(BaseModel):
    content: str


async def consume_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID
    )
    await consumer.start()
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        async for msg in consumer:
            await conn.execute("INSERT INTO messages (content) VALUES ($1)", msg.value.decode('utf-8'))
    finally:
        await consumer.stop()
        await conn.close()


@app.on_event("startup")
async def startup_event():
    await create_table()
    asyncio.create_task(consume_messages())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/messages")
async def get_messages(request: Request):
    headers = dict(request.headers)
    logger.info(f"Received headers: {headers}")
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM messages")
    await conn.close()
    async with httpx.AsyncClient() as client:
        response = await client.get(HELLO_SERVICE)
    return rows


"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
