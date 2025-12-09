import enum


class SourceType(str, enum.Enum):
    HUMAN = "human"
    SERVICE = "service"
    ANONYMOUS = "anonymous"
    UNKNOWN = "unknown"
