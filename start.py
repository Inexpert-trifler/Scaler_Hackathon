import uvicorn
import sys

if __name__ == "__main__":
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        log_level="info"
    )
