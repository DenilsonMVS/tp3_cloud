import logging
import time
import os
import json
import redis

REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'metrics'


def load_handler():
    # Path to the mounted handler file (renamed)
    handler_path = "/app/config/newpyfile"  # Use the updated file name

    if os.path.exists(handler_path):
        try:
            # Read the content of the file
            with open(handler_path, "r") as file:
                code = file.read()

                # Define a local scope for executing the file
                local_scope = {}
                exec(code, {}, local_scope)

                # Retrieve the handler function from the executed code
                if "handler" in local_scope and callable(local_scope["handler"]):
                    return local_scope["handler"]
                else:
                    logging.critical("No 'handler' function found in newpyfile.")
                    return lambda: "Default handler: 'handler' function not defined."
        except Exception as e:
            logging.critical(f"Failed to load newpyfile: {e}")
            return lambda: "Default handler: Failed to load the file."
    else:
        logging.critical("newpyfile not found in ConfigMap mount.")
        return lambda: "Default handler: newpyfile is missing."

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
