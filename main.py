"""
AutoBoost Agent — entry point.

Starts the FastAPI webhook server. On startup the server:
  1. Loads sample post data into the registry
  2. Fires the Rallio engagement simulator (shows the full pipeline)
  3. Starts APScheduler polling every 5 minutes as a fallback
"""
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from server.webhook import app
from integrations.rallio import RallioClient
from agent.agent import process_post


def main():
    print("=" * 60)
    print("  AutoBoost Agent")
    print("  Ignite Visibility × Rallio")
    print("  http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
