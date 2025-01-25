import logging
import time
import importlib.util
import os

def load_handler():
    # Path to the mounted handler.py file
    handler_path = "/app/config/handler.py"  # Matches the mountPath in Deployment.yaml

    if os.path.exists(handler_path):
        try:
            # Dynamically load the handler.py module
            spec = importlib.util.spec_from_file_location("handler", handler_path)
            handler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(handler_module)

            # Return the handler function
            return handler_module.handler
        except Exception as e:
            logging.critical(f"Failed to load handler: {e}")
            return lambda: "Default handler: Failed to load the handler function."
    else:
        logging.critical("handler.py not found in ConfigMap mount.")
        return lambda: "Default handler: handler.py is missing."


def main():

    # Load the handler function
    handler = load_handler()

    while True:
        # Call the handler function and log its output
        logging.critical(handler())
        time.sleep(5)

if __name__ == "__main__":
    main()
