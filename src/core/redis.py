from fastapi import Request
from redis.asyncio import Redis


def create_redis_client(url: str) -> Redis:
    """Create a lazy Redis client; the connection is opened on first command."""
    return Redis.from_url(url, decode_responses=True)


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
