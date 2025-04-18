import asyncio
from loguru import logger
import aio_pika

from config import base_config, RABBIT_URL
from pika import message_router

PARALLEL_TASKS = 10

async def main() -> None:
    connection = await aio_pika.connect_robust(RABBIT_URL)

    queue_name = base_config.RABBITMQ_QUEUE

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=PARALLEL_TASKS)
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        logger.info("consumer started")

        await queue.consume(message_router)

        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == "__main__":
    logger.info("starting consumer")
    asyncio.run(main())
