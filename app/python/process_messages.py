from threading import Thread
from loguru import logger

class ProcessMessages(Thread):
    def __init__(self, app, bot_factory, message_queue):
        Thread.__init__(self)
        self.app = app
        self.bot_factory = bot_factory
        self.message_queue = message_queue

    def run(self):
        with self.app.app_context():
            while True:
                try:
                    # Wait for a message from the queue
                    msg = self.message_queue.get()
                    if msg:
                        bot = self.bot_factory.get_bot(msg)
                        bot.handle_message(msg)
                        logger.debug(f"Message processed: {msg}")
                except Exception as e:
                    logger.exception(f"Error in ProcessMessages thread: {e}")