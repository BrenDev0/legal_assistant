from  dotenv import load_dotenv
load_dotenv()
import uvicorn
from src.app.interface.fastapi.server import create_fastapi_app

app = create_fastapi_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000
    )