import logging
import time
import os
import json
import redis
import importlib.util
import shutil

REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'metrics'


def load_handler():
    # Paths for the mounted file and the renamed file
    old_path = "/app/config/newpyfile"
    new_path = "/app/config/newpyfile.py"

    # Ensure the file is renamed to newpyfile.py
    if os.path.exists(old_path):
        try:
            shutil.copy(old_path, new_path)
            logging.info(f"File copied from {old_path} to {new_path}.")
        except Exception as e:
            logging.critical(f"Failed to copy {old_path} to {new_path}: {e}")
            return lambda: "Default handler: Failed to prepare the file."
    elif not os.path.exists(new_path):
        logging.critical("newpyfile or newpyfile.py not found in ConfigMap mount.")
        return lambda: "Default handler: newpyfile is missing."

    # Load the newpyfile.py module dynamically
    try:
        spec = importlib.util.spec_from_file_location("newpyfile", new_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Retrieve the handler function from the module
        if hasattr(module, "handler") and callable(module.handler):
            return module.handler
        else:
            logging.critical("No 'handler' function found in newpyfile.py.")
            return lambda: "Default handler: 'handler' function not defined."
    except Exception as e:
        logging.critical(f"Failed to load newpyfile.py: {e}")
        return lambda: "Default handler: Failed to load the file."


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
