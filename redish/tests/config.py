import os

from redish.client import DEFAULT_PORT

connection = dict(
    host=os.environ.get("REDIS_TEST_HOST") or "localhost",
    port=os.environ.get("REDIS_TEST_PORT") or DEFAULT_PORT,
    db=os.environ.get("REDIS_TEST_DB") or "redish-test",
)
