"""
=========================================================
AI Signal Engine
Message Queue
Version : 2.1
=========================================================
"""

from queue import Queue, Empty


class MessageQueue:

    def __init__(self, logger, database):

        self.logger = logger
        self.database = database
        self.queue = Queue()

    # =====================================================
    # ADD MESSAGE
    # =====================================================

    def add(
        self,
        messenger,
        report_id,
        message_type,
        payload,
        retry=0,
    ):

        item = {

            "messenger": messenger,
            "report_id": report_id,
            "message_type": message_type,
            "payload": payload,
            "retry": retry,

        }

        self.queue.put(item)

        try:

            if (

                self.database is not None
                and hasattr(self.database, "save_queue")

            ):

                self.database.save_queue(item)

        except Exception as ex:

            self.logger.exception(ex)

    # =====================================================
    # NEXT MESSAGE
    # =====================================================

    def get_next(self):

        try:

            return self.queue.get(timeout=1)

        except Empty:

            return None

        except Exception as ex:

            self.logger.exception(ex)

            return None

    # =====================================================
    # QUEUE SIZE
    # =====================================================

    def size(self):

        return self.queue.qsize()

    # =====================================================
    # EMPTY
    # =====================================================

    def is_empty(self):

        return self.queue.empty()