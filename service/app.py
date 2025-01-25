import logging
import time
import os
import importlib.util

def load_handler():
    # Path to the mounted handler.py file
    handler_path = "/app/config/pyfile"  # Matches the mountPath in Deployment.yaml

    if os.path.exists(handler_path):
        try:
            # Dynamically load the handler.py file
            spec = importlib.util.spec_from_file_location("handler_module", handler_path)
            handler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(handler_module)

            # Check if the 'handler' function exists in the module
            if hasattr(handler_module, "handler") and callable(handler_module.handler):
                logging.critical(f"'handler' function successfully loaded from {handler_path}.")
                return handler_module.handler
            else:
                logging.critical(f"'handler' function not found in {handler_path}.")
                return lambda: "Default handler: 'handler' function not found."
        except Exception as e:
            logging.critical(f"Failed to load handler from {handler_path}: {e}")
            return lambda: "Default handler: Failed to load the handler function."
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

    # Load the handler function
    handler = load_handler()

    while True:
        # Log the REDIS_OUTPUT_KEY
        logging.critical(f"REDIS_OUTPUT_KEY: {redis_output_key}")

        # Call the handler function and log its output
        try:
            logging.critical(handler())
        except Exception as e:
            logging.critical(f"Error while executing the handler function: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()
