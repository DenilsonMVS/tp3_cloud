import time
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Redis server configuration
REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
KEY = '2021032030-proj3-output'

def main():
    try:
        # Connect to Redis server
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        logging.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

        while True:
            try:
                # Get the value of the specified key
                value = redis_client.get(KEY)

                if value is not None:
                    logging.info(f"Value for key '{KEY}': {value}")
                else:
                    logging.warning(f"Key '{KEY}' does not exist or has no value.")

                # Wait for 5 seconds
                time.sleep(5)
            except KeyboardInterrupt:
                logging.info("Stopping the script.")
                break
            except Exception as e:
                logging.error(f"Error fetching key '{KEY}': {e}")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")

if __name__ == "__main__":
    main()