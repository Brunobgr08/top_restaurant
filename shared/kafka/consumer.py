import json
import logging
from typing import Callable, Dict, Any
from confluent_kafka import Consumer, KafkaException
from functools import wraps

logger = logging.getLogger("kafka-consumer")
logger.setLevel(logging.INFO)

class KafkaConsumerWrapper:
    def __init__(self, bootstrap_servers: str = 'kafka:9092', group_id: str = None):
        self._conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'session.timeout.ms': 10000,
            'heartbeat.interval.ms': 3000
        }
        self._consumer = Consumer(self._conf)
        logger.info(f"Consumer configurado para brokers: {bootstrap_servers}")

    def handle_errors(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except KafkaException as e:
                logger.error(f"Erro no Kafka: {str(e)}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar mensagem: {str(e)}")
            except Exception as e:
                logger.critical(f"Erro inesperado: {str(e)}")
                raise
        return wrapper

    @handle_errors
    def subscribe_and_consume(self, topics: list, callback: Callable[[Dict[str, Any]], None]):
        """Consome mensagens com tratamento de erros integrado"""
        self._consumer.subscribe(topics)
        logger.info(f"Inscrito nos tópicos: {topics}")

        try:
            while True:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"Erro no consumer: {msg.error()}")
                    continue

                message_data = json.loads(msg.value().decode('utf-8'))
                logger.debug(f"Mensagem recebida: {message_data}")

                callback(message_data)
                self._consumer.commit(asynchronous=False)
        finally:
            self._consumer.close()
            logger.info("Consumer fechado corretamente")

    @handle_errors
    def subscribe_and_consume_multiple(self, topic_callbacks: Dict[str, Callable[[Dict[str, Any]], None]]):
        """Consome mensagens com callbacks diferentes por tópico"""
        topics = list(topic_callbacks.keys())
        self._consumer.subscribe(topics)
        logger.info(f"Inscrito nos tópicos: {topics}")

        try:
            while True:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"Erro no consumer: {msg.error()}")
                    continue

                topic = msg.topic()
                message_data = json.loads(msg.value().decode('utf-8'))
                logger.debug(f"Mensagem recebida do tópico {topic}: {message_data}")

                callback = topic_callbacks.get(topic)
                if callback:
                    callback(message_data)

                self._consumer.commit(asynchronous=False)

        finally:
            self._consumer.close()
            logger.info("Consumer fechado corretamente")