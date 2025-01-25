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

def list_files_in_directory(directory):
    """Log all files in the given directory."""
    if os.path.exists(directory):
        files = os.listdir(directory)
        if files:
            logging.critical(f"Files in {directory}: {', '.join(files)}")
        else:
            logging.critical(f"No files found in {directory}.")
    else:
        logging.critical(f"Directory {directory} does not exist.")

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

    # Directory to list files
    mounted_dir = "/app/config"

    while True:
        # Log the REDIS_OUTPUT_KEY
        logging.critical(f"REDIS_OUTPUT_KEY: {redis_output_key}")

        # List files in the mounted directory
        list_files_in_directory(mounted_dir)

        # Call the handler function and log its output
        logging.critical(handler())

        time.sleep(5)

if __name__ == "__main__":
    main()
