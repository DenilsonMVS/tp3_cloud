import logging
import time
import os
import json
import redis
import importlib.util
from importlib.machinery import SourceFileLoader 

REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'metrics'


def load_handler():
    # Path to the mounted file (without .py extension)
    handler_path = "/app/config/newpyfile"  # No .py extension

    if os.path.exists(handler_path):
        try:
            # Dynamically load the module without the .py extension
            spec = importlib.util.spec_from_file_location("newpyfile", SourceFileLoader("newpyfile", handler_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Retrieve the handler function from the module
            if hasattr(module, "handler") and callable(module.handler):
                return module.handler
            else:
                logging.critical("No 'handler' function found in the file.")
                return lambda: "Default handler: 'handler' function not defined."
        except Exception as e:
            logging.critical(f"Failed to load the file: {e}")
            return lambda: "Default handler: Failed to load the file."
    else:
        logging.critical("File not found in ConfigMap mount.")
        return lambda: "Default handler: File is missing."


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Load the REDIS_OUTPUT_KEY from environment variable
    redis_output_key = os.getenv("REDIS_OUTPUT_KEY", "Default REDIS_OUTPUT_KEY")

    # Load the handler function
    handler = load_handler()

    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    while True:
        try:
            metrics = json.loads(redis_client.get(REDIS_KEY))

            context = {}

            logging.critical(handler(metrics, context))
        except Exception as e:
            logging.critical(f"Error while executing the handler function: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()
