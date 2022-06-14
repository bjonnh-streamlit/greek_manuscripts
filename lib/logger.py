import datetime
from enum import Enum
import sys

class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

class MessageLevels(OrderedEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    FATAL = 3
    ULTIMATE = 4

class LogEntry:
    def __init__(self, level: MessageLevels, message: str):
        self.timestamp = datetime.datetime.now()
        self.level = level
        self.message = message
    def __str__(self):
        return f"{self.timestamp.isoformat()} - {self.level.name} - {self.message}"


class Logger:
    def __init__(self, minimum_logging_level: MessageLevels = MessageLevels.INFO,
                 fail_on: MessageLevels = MessageLevels.ULTIMATE):
        self.messages: list[LogEntry] = []
        self.minimum_logging_level = minimum_logging_level
        self.fail_on = fail_on
        self.hook = lambda logentry: None

    def append(self, level: MessageLevels, message: str):
        if level >= self.minimum_logging_level:
            entry = LogEntry(level, message)
            self.messages.append(entry)
            self.hook(entry)
            if level >= self.fail_on:
                sys.exit()

    def info(self, message: str):
        self.append(MessageLevels.INFO, message)

    def warning(self, message: str):
        self.append(MessageLevels.WARNING, message)

    def error(self, message: str):
        self.append(MessageLevels.ERROR, message)

    def fatal(self, message: str):
        self.append(MessageLevels.FATAL, message)

    def set_hook(self, fun):
        self.hook = fun
