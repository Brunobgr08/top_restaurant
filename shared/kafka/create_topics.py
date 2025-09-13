import os
import time
import logging
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kafka-init")

def create_kafka_admin_client(brokers, max_retries=10, retry_delay=3):
    """Cria cliente admin com retry automático"""
    for attempt in range(1, max_retries + 1):
        try:
            client = KafkaAdminClient(
                bootstrap_servers=brokers,
                client_id='admin-client',
                request_timeout_ms=10000
            )
            logger.info("✅ Conectado ao Kafka com sucesso!")
            return client
        except NoBrokersAvailable as e:
            if attempt < max_retries:
                logger.warning(f"Tentativa {attempt}/{max_retries}: Kafka não disponível. Retry em {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Não foi possível conectar ao Kafka após várias tentativas")
                raise

def main():
    BROKERS_STR = os.getenv('KAFKA_BROKERS', 'kafka-controller:9092,kafka-broker-2:9094,kafka-broker-3:9095')
    BROKERS = [broker.strip() for broker in BROKERS_STR.split(',') if broker.strip()]

    logger.info(f"🔄 Iniciando criação de tópicos para brokers: {BROKERS}")

    try:
        admin_client = create_kafka_admin_client(BROKERS)

        # Verifica tópicos existentes
        existing_topics = admin_client.list_topics()
        logger.info(f"📋 Tópicos existentes: {existing_topics}")

        # Define tópicos para criar
        topic_definitions = {
            "order_created": {'retention.ms': '3600000'},
            "payment_processed": {'retention.ms': '3600000'},
            "order_ready": {'retention.ms': '600000'},
            "menu_updated": {'retention.ms': '86400000'}
        }

        topics_to_create = [
            NewTopic(
                name=topic_name,
                num_partitions=3,  # Aumentado para melhor distribuição
                replication_factor=2,
                topic_configs=configs
            )
            for topic_name, configs in topic_definitions.items()
            if topic_name not in existing_topics
        ]

        if topics_to_create:
            admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
            logger.info(f"✅ Tópicos criados: {[t.name for t in topics_to_create]}")
        else:
            logger.info("✅ Todos os tópicos já existem")

    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        raise

if __name__ == "__main__":
    main()