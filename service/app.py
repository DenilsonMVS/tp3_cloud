import logging
import time
import os

def main():
    outputkey = os.getenv("REDIS_OUTPUT_KEY", "Default message: ConfigMap value not found")

    while True:
        logging.critical(outputkey)
        time.sleep(5)

if __name__ == "__main__":
    main()
