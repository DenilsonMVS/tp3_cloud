from datetime import datetime
from typing import Any

def handler(input: dict, context: object) -> dict[str, Any]:
    current_time = datetime.now(datetime.timezone.utc).isoformat()
    return {"test": current_time}
