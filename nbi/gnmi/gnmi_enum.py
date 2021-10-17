from enum import Enum

class GnmiSubscribeMode(Enum):
    STREAM = 0
    ONCE = 1
    POLL = 2

class GnmiStreamMode(Enum):
    TARGET_DEFINED = 0  # The target selects the relevant mode for each element.
    ON_CHANGE = 1  # The target sends an update on element value change.
    SAMPLE = 2  # The target samples values according to the interval.

class GnmiSubscribeEncoding(Enum):
    JSON = 0
    BYTES = 1
    PROTO = 2
    ASCII = 3
    JSON_IETF = 4

class GnmiSubscribeKey:
    PREFIX = "prefix"
    MODE = "mode"


class GnmiSubscriptionKey:
    PATH = "xpath"
    MODE = "mode"
    SAMPLE_INTERVAL = "sample_interval"
    HEARTBEAT_INTERVAL = "heartbeat_interval"
    SUPPRESS_REDUNDANT = "suppress_redundant"

