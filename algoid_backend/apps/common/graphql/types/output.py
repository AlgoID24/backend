import enum
from typing import Generic, Optional, TypeVar
import strawberry

T = TypeVar("T")


@strawberry.enum
class ResponseStatus(enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


@strawberry.type
class Response(Generic[T]):
    status: ResponseStatus
    message: Optional[str] = None
    data: T
