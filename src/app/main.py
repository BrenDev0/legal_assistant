from dotenv import load_dotenv
load_dotenv()
from src.app.setup.startup_event import startup_event
import signal
import time

def main():
    startup_event()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)  # Sleep to prevent busy-waiting
    except KeyboardInterrupt:
        print("Shutting down gracefully...")

if __name__ == "__main__":
    main()