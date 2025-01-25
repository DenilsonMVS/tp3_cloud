import logging
import time
import os

def load_handler():
    # Path to the mounted handler file (renamed)
    handler_path = "/app/config/pyfile"  # Use the updated file name

    if os.path.exists(handler_path):
        try:
            # Read the content of the file
            with open(handler_path, "r") as file:
                code = file.read()
                logging.critical(f"Content of pyfile:\n{code}")

                # Define a local scope for executing the file
                local_scope = {}
                exec(code, {}, local_scope)

                # Retrieve the handler function from the executed code
                if "handler" in local_scope and callable(local_scope["handler"]):
                    return local_scope["handler"]
                else:
                    logging.critical("No 'handler' function found in pyfile.")
                    return lambda: "Default handler: 'handler' function not defined."
        except Exception as e:
            logging.critical(f"Failed to load pyfile: {e}")
            return lambda: "Default handler: Failed to load the file."
    else:
        logging.critical("pyfile not found in ConfigMap mount.")
        return lambda: "Default handler: pyfile is missing."

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
