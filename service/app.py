import logging
import time
import os
import json
import redis
import copy
import importlib.util
from importlib.machinery import SourceFileLoader 
import zipfile
import sys

REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'metrics'


def unzip_file(zip_file, extract_to):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            logging.critical(f"Unzipped contents of {zip_file} to {extract_to}")
    except Exception as e:
        logging.critical(f"Failed to unzip file {zip_file}: {e}")
        return False
    return True


def load_handler():
    handler_path = "/app/config/file/newpyfile"
    zip_path = "/app/config/zip/zip"
    tmp_path = "/app/tmp"
    unzipped_handler_path = os.path.join(tmp_path, os.getenv("FILE_ENTRYPOINT", "handler.py"))
    function_entrypoint = os.getenv("FUNCTION_ENTRYPOINT", "handler")

    if os.path.exists(handler_path):
        try:
            # Dynamically load the module without the .py extension
            spec = importlib.util.spec_from_loader("newpyfile", SourceFileLoader("newpyfile", handler_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Retrieve the handler function from the module
            if hasattr(module, function_entrypoint) and callable(module.handler):
                return module.handler
            else:
                logging.critical("No 'handler' function found in the file.")
                return lambda: "Default handler: 'handler' function not defined."
        except Exception as e:
            logging.critical(f"Failed to load the file: {e}")
            return lambda: "Default handler: Failed to load the file."
    
    elif os.path.exists(zip_path):
        logging.critical(f"Zip file found at {zip_path}. Attempting to unzip.")

        # Unzip the file into /app/tmp
        if unzip_file(zip_path, tmp_path):
            logging.critical("Zip file unzipped successfully.")
            
            # Add the tmp directory to sys.path so Python can find the unzipped modules
            sys.path.append(tmp_path)
            
            # Check if handler.py exists in the unzipped files
            if os.path.exists(unzipped_handler_path):
                try:
                    # Dynamically load the handler from the unzipped content
                    spec = importlib.util.spec_from_loader("newpyfile", SourceFileLoader("newpyfile", unzipped_handler_path))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Retrieve the handler function from the module
                    if hasattr(module, function_entrypoint) and callable(module.handler):
                        logging.critical("Successfully loaded handler from unzipped handler.py")
                        return module.handler
                    else:
                        logging.critical("No 'handler' function found in the unzipped file.")
                        return lambda: "Default handler: 'handler' function not defined."
                except Exception as e:
                    logging.critical(f"Failed to load handler from the unzipped file: {e}")
                    return lambda: "Default handler: Failed to load handler from unzipped file."
            else:
                logging.critical("No handler.py found in the zip file.")
                return lambda: "Default handler: No handler.py found in the zip."
        else:
            logging.critical("Failed to unzip the zip file.")
            return lambda: "Default handler: Failed to unzip the zip file."
        
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
    redis_refresh_time = float(os.getenv("REDIS_REFRESH_TIME", "5"))

    # Load the handler function
    handler = load_handler()

    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    context = {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
        "input_key": REDIS_KEY,
        "output_key": redis_output_key,
        "function_getmtime": time.perf_counter(),
        "last_execution": None,
        "env": {},
    }

    while True:
        try:
            metrics = json.loads(redis_client.get(REDIS_KEY))            

            context_copy = copy.deepcopy(context)
            value = handler(metrics, context)
            logging.critical(value)
            redis_client.set(redis_output_key, json.dumps(value))

            context["last_execution"] = time.perf_counter()
            context["env"] = context_copy["env"]

        except Exception as e:
            logging.critical(f"Error while executing the handler function: {e}")

        time.sleep(redis_refresh_time)

if __name__ == "__main__":
    main()
