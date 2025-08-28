import os
import json
import logging
import time
from typing import Any, Dict
from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("kafka-producer")
logger.setLevel(logging.INFO)


base_conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL'),
    'sasl.mechanism': os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN'),
    'sasl.username': os.getenv('KAFKA_SASL_USERNAME'),
    'sasl.password': os.getenv('KAFKA_SASL_PASSWORD'),
    'socket.keepalive.enable': True,
    'socket.timeout.ms': 10000,
    'api.version.request': True,
}


producer_specific_conf = {
    'message.timeout.ms': 10000,
    'retry.backoff.ms': 1500,
    'retry.backoff.max.ms': 3000,
}

LOCAL_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka-controller:9092,kafka-broker-2:9094,kafka-broker-3:9095')

class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: str = LOCAL_BROKERS, max_retries: int = 5, retry_delay: int = 5):

        # Verifica se estamos em ambiente de produção
        is_production = all([
            base_conf.get('bootstrap.servers'),
            base_conf.get('security.protocol'),
            base_conf.get('sasl.mechanism'),
            base_conf.get('sasl.username'),
            base_conf.get('sasl.password')
        ])

        if is_production:
            # Configuração de produção = base + específicas do producer
            self._producer_conf = {**base_conf, **producer_specific_conf}
            self._admin_conf = base_conf  # Admin usa apenas a base
            logger.info(f"Producer configurado para produção com brokers: {base_conf['bootstrap.servers']}")
        else:
            # Configuração local
            local_base = {
                'bootstrap.servers': bootstrap_servers,
                'socket.keepalive.enable': True,
                'socket.timeout.ms': 10000,
            }
            self._producer_conf = {**local_base, **producer_specific_conf}
            self._admin_conf = local_base
            logger.info(f"Producer configurado para desenvolvimento local com brokers: {bootstrap_servers}")

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._producer = None
        self._initialize()

    def _initialize(self):
        """Tenta conectar com retry exponencial"""
        for attempt in range(self.max_retries):
            try:
                self._producer = Producer(self._producer_conf)

                admin_client = AdminClient(self._admin_conf)
                admin_client.list_topics(timeout=5)

                logger.info(f"Conectado ao Kafka em {self._admin_conf['bootstrap.servers']}")
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