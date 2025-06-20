import json
import logging
import time
from typing import Any, Dict
from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient

logger = logging.getLogger("kafka-producer")
logger.setLevel(logging.INFO)

class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: str = 'kafka:9092', max_retries: int = 5, retry_delay: int = 5):
        self._conf = {
            'bootstrap.servers': bootstrap_servers,
            'message.timeout.ms': 10000,
            'retry.backoff.ms': 1500,
            'retry.backoff.max.ms': 3000,
            'socket.keepalive.enable': True,
            'socket.timeout.ms': 10000,
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._producer = None
        self._initialize()

    def _initialize(self):
        """Tenta conectar com retry exponencial"""
        for attempt in range(self.max_retries):
            try:
                self._producer = Producer(self._conf)
                # Testa a conexão com um ping leve
                admin_client = AdminClient({'bootstrap.servers': self._conf['bootstrap.servers']})
                admin_client.list_topics(timeout=5)
                logger.info(f"Conectado ao Kafka em {self._conf['bootstrap.servers']}")
                return
            except KafkaException as e:
                logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay * (attempt + 1))

    def publish_message(self, topic: str, message: Dict[str, Any]):
        """Publica mensagem com tratamento de erro reforçado"""
        if not self._producer:
            raise KafkaException("Producer não inicializado")

        try:
            self._producer.produce(
                topic=topic,
                value=json.dumps(message).encode('utf-8'),
                on_delivery=self._delivery_report
            )
            self._producer.flush(timeout=10)
        except Exception as e:
            logger.error(f"Falha ao publicar: {str(e)}")
            raise

    @staticmethod
    def _delivery_report(err, msg):
        if err:
            logger.error(f"Falha na entrega: {err}")
        else:
            logger.debug(f"Mensagem entregue em {msg.topic()} [{msg.partition()}]")

# Singleton com inicialização preguiçosa
_kafka_producer = None

def get_kafka_producer():
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducerWrapper()
    return _kafka_producer