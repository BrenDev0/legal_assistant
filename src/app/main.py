from  dotenv import load_dotenv
load_dotenv()
import uvicorn
from src.app.setup.startup_event import startup_event



if __name__ == "__main__":
    startup_event()