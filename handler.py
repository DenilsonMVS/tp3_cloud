import main
from typing import Any, Dict

def handler(input: Dict[str, Any], context: object) -> Dict[str, Any]:
    return main.handler(input, context)
