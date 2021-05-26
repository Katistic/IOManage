import threading
import asyncio
import uuid
import enum
import time
import json
import os


class ParsingType(enum.Enum):
    RAW = 0
    TEXT = 1
    JSON = 2


class OperationType(enum.Enum):
    READ = "read"
    WRITE = "write"


class Operation:
    def __init__(self, operation_type: OperationType, data=None):
        self.data = data
        self.operation_type = operation_type

        self.id = uuid.uuid4()
        self._result = None

    @property
    def finished(self):
        return self._result != None

    def wait_for_finish(self):
        while not self.finished:
            time.sleep(0)
            
    async def wait_for_finish_a(self):
        while not self.finished:
            await asyncio.sleep(0)

    @property
    def result(self):
        if self.operation_type is OperationType.WRITE:
            return None

        return self._result


class IOManager:
    def __init__(self, file, parsing_type: ParsingType = ParsingType.JSON):
        self.operations = []
        self.parsing_type = parsing_type

        self._stop = False
        self._thread = None
        self.file = file

        self._opened_file = None

        if not os.path.isfile(self.file):
            with open(self.file, "w+") as file:
                if self.parsing_type == ParsingType.JSON:
                    file.write("{}")

    def _start(self):
        if self.stopped and not self._stop:
            self._stop = False

            self._thread = threading.Thread(target=self._operation_loop)
            self._thread.start()

    def _get_next_operation_type(self):
        if len(self.operations) > 0:
            return self.operations[0].operation_type

        return None

    def _operation_loop(self):
        while not self._stop and len(self.operations) > 0:
            operation = self.operations.pop(0)

            if self._opened_file is None:
                rw = "r" if operation.operation_type is OperationType.READ else "w"
                if self.parsing_type is ParsingType.RAW:
                    rw += "b"

                self._opened_file = open(self.file, rw)

            if operation.operation_type is OperationType.READ:
                if self.parsing_type is ParsingType.JSON:
                    operation._result = json.load(self._opened_file)
                else:
                    operation._result = self._opened_file.read()
            elif operation.operation_type is OperationType.WRITE:
                if self.parsing_type is ParsingType.JSON:
                    json.dump(operation.data, self._opened_file, indent=4)
                else:
                    self._opened_file.write(operation.data)

                operation._result = True

            if self._get_next_operation_type() is operation.operation_type:
                self._opened_file.seek(0)
            else:
                self._opened_file.close()
                self._opened_file = None

        if self._opened_file is not None:
            self._opened_file.close()
            self._opened_file = None

    @property
    def stopped(self):
        return self._thread is None or self._thread.is_alive() is False

    def stop(self):
        self._stop = True

    def read(self):
        operation = Operation(OperationType.READ)
        self.operations.append(operation)

        self._start()

        return operation

    def write(self, data):
        operation = Operation(OperationType.WRITE, data)
        self.operations.append(operation)

        self._start()

        return operation
