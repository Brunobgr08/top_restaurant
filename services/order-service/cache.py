import os
import redis
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Redis via variáveis de ambiente
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    # Se REDIS_URL estiver definida, usar diretamente
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
else:
    # Caso contrário, usar host e porta individuais
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# TTL configurável via variável de ambiente
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', 300))

def set_cached_menu_item(item_id: str, data: dict):
    redis_client.setex(f"menu:item:{item_id}", CACHE_TTL_SECONDS, json.dumps(data))

def get_cached_menu_item(item_id: str):
    cached = redis_client.get(f"menu:item:{item_id}")
    return json.loads(cached) if cached else None
