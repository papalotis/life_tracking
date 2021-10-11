from datetime import datetime
from enum import Enum
from hashlib import sha1
from typing import Any, Mapping, Optional

from pydantic import BaseModel, constr, validator
from enum import auto


class EntryType(Enum):
    financial = "financial" 
    weight = "weight"
    calories = "calories"


class Entry(BaseModel):
    value: float
    datetime: datetime
    comment: constr(strip_whitespace=True)
    type: EntryType
    key: str = None

    @validator("key", pre=True, always=True, allow_reuse=True)
    def validate_key(key, values: Mapping[str, Any], **kwargs) -> Optional[str]:
        created_key = sha1("".join(map(str, values.values())).encode()).hexdigest()

        if key != None and key != created_key:
            # calculated key and provided key are not the same
            # return None to cause an error
            return None

        return created_key
