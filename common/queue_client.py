import aio_pika
from typing import Callable, Coroutine, Any
import asyncio
import loguru

class QueueClient(object):
    def __init__(
            self,
            user:str,
            pwd: str,
            host_name:str, 
            port: str,
            queue_name:str,
            call_back: Callable[[aio_pika.abc.AbstractIncomingMessage], Coroutine[None, None, None]],
            service_logger: loguru._logger.Logger
        )->None:
        self._url = f"amqp://{user}:{pwd}@{host_name}:{port}"
        self._queue_name = queue_name
        self._call_back = call_back
        self._logger = service_logger

    async def _run_queue(self) -> None:
        connection = await aio_pika.connect_robust(self._url)
        try:
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=2)
                queue = await channel.declare_queue(self._queue_name, auto_delete=True)

                self._logger.info("start")
                
                await queue.consume(self._call_back)

                await asyncio.Future()

        except aio_pika.exceptions.AMQPConnectionError as e:
            self._logger.error(f"Failed to connect to RabbitMQ: {e}")
            # Depending on your error handling strategy, you might want to
            # implement a retry mechanism here.
        except asyncio.CancelledError:
            self._logger.info("RabbitMQ consumer task was cancelled.")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred in the run_queue task: {e}")
        finally:
            if connection and not connection.is_closed:
                self._logger.info("Closing RabbitMQ connection...")
                await connection.close()
                self._logger.info("RabbitMQ connection closed.")


    def start_background_task(self, loop: asyncio.AbstractEventLoop):
        self.rabbitmq_handler_task = loop.create_task(self._run_queue())

    async def stop_background_task(self):
        if self.rabbitmq_handler_task and not self.rabbitmq_handler_task.done():
            self.rabbitmq_handler_task.cancel()
            # Optionally, wait for the task to actually finish cancelling
            try:
                await asyncio.wait_for(self.rabbitmq_handler_task, timeout=5.0) # Wait max 5 seconds for cleanup
            except asyncio.TimeoutError:
                self._logger.warning("Background task did not finish cancelling within timeout.")
            except asyncio.CancelledError:
                self._logger.info("Background task confirmed cancelled.")
            except Exception as e:
                self._logger.error(f"Error during background task cancellation wait: {e}")
        else:
            self._logger.info("No background task to cancel or task already done.")
