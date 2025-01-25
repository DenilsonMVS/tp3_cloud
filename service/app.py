import logging
import time
import os

def load_handler():
    # Path to the mounted handler.py file
    handler_path = "/app/config/pyfile"  # Matches the mountPath in Deployment.yaml

    if os.path.exists(handler_path):
        try:
            # Read the content of the handler.py file
            with open(handler_path, "r") as file:
                content = file.read()
                logging.critical(f"Content of handler.py:\n{content}")
                return lambda: "Handler file content successfully logged."
        except Exception as e:
            logging.critical(f"Failed to read handler.py: {e}")
            return lambda: "Default handler: Failed to read the handler file."
    else:
        logging.critical("handler.py not found in ConfigMap mount.")
        return lambda: "Default handler: handler.py is missing."

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

    # Load and print the content of the handler file
    handler = load_handler()

    # Directory to list files
    mounted_dir = "/app/config"

    while True:
        # Log the REDIS_OUTPUT_KEY
        logging.critical(f"REDIS_OUTPUT_KEY: {redis_output_key}")

        # Call the handler function and log its output
        logging.critical(handler())

        time.sleep(5)

if __name__ == "__main__":
    main()
