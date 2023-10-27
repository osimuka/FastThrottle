import time
import redis
import aioredis
from functools import wraps
from fastapi import HTTPException, Request


class ThrottleSync:
    def __init__(self, redis_host: str, redis_port: int = 6379) -> None:
        self.redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0, decode_responses=True)

    def get_redis(self):
        return redis.Redis(connection_pool=self.redis_pool)

    def is_throttled(self, key: str, max_requests: int, window: int) -> bool:
        current = int(time.time())
        window_start = current - window
        redis_conn = self.get_redis()
        with redis_conn.pipeline() as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {current: current})
                pipe.expire(key, window)
                results = pipe.execute()
            except redis.RedisError as e:
                raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}") from e

        return results[1] > max_requests


class ThrottleAsync:
    def __init__(self, redis_host: str, redis_port: int = 6379) -> None:
        self.redis_host = redis_host
        self.redis_port = redis_port

    async def init_redis(self):
        self.redis = await aioredis.create_redis_pool(f'redis://{self.redis_host}:{self.redis_port}')

    async def is_throttled(self, key: str, max_requests: int, window: int) -> bool:
        current = int(time.time())
        window_start = current - window
        with await self.redis.multi_exec() as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {current: current})
                pipe.expire(key, window)
                results = await pipe.execute()
            except aioredis.RedisError as e:
                raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}") from e

        return results[1] > max_requests


def rate_limit_async(key: str, max_requests: int, window: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            key = f"rate_limit:{request.client.host}:{request.url.path}"
            throttler = ThrottleAsync()
            await throttler.init_redis()
            if await throttler.is_throttled(key, max_requests, window):
                raise HTTPException(status_code=429, detail="Too many requests")
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


def rate_limit_sync(key: str, max_requests: int, window: int):
    def decorator(func):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            key = f"rate_limit:{request.client.host}:{request.url.path}"
            throttler = ThrottleSync()
            if throttler.is_throttled(key, max_requests, window):
                raise HTTPException(status_code=429, detail="Too many requests")
            return func(request, *args, **kwargs)

        return wrapper
    return decorator
