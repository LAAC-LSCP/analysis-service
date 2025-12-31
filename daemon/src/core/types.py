from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Operation(StrEnum):
    VTC = "vtc"
    ALICE = "alice"
    ACOUSTICS = "acoustics"
    W2V2 = "w2v2"
