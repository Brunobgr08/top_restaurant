import redis
import json
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
CACHE_TTL_SECONDS = 300

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def set_cached_menu_item(item_id: str, data: dict):
    redis_client.setex(f"menu:item:{item_id}", CACHE_TTL_SECONDS, json.dumps(data))

def get_cached_menu_item(item_id: str):
    cached = redis_client.get(f"menu:item:{item_id}")
    return json.loads(cached) if cached else None
