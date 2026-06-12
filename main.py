"""
AutoBoost Agent — entry point.

Starts the FastAPI webhook server. On startup the server loads sample
post data into the registry, then waits for events on /webhook/engagement
and /webhook/slack.

To exercise the full pipeline against the sample posts, run
`uv run python test_pipeline.py` (in a separate terminal) or POST to
/webhook/engagement directly.

NOTE: APScheduler polling fallback is a planned feature, not yet wired up —
the agent currently relies on /webhook/engagement being called.
"""
import uvicorn

from server.webhook import app


def main():
    print("=" * 60)
    print("  AutoBoost Agent")
    print("  http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
