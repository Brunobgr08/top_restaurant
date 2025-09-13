import sys
import time
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka-waiter")

def check_kafka_ready(brokers, max_retries=30, retry_delay=2):
    """Verifica se Kafka está pronto via conexão TCP simples"""
    for attempt in range(1, max_retries + 1):
        logger.info(f"Tentativa {attempt}/{max_retries}: Verificando Kafka...")

        for broker in brokers:
            try:
                host, port = broker.split(':')
                port = int(port)

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        logger.info(f"✅ Broker {broker} está respondendo!")
                        return True
                    else:
                        logger.debug(f"Broker {broker} ainda não pronto (code: {result})")

            except Exception as e:
                logger.debug(f"Erro ao conectar com {broker}: {e}")

        if attempt < max_retries:
            logger.info(f"Kafka não pronto. Aguardando {retry_delay}s...")
            time.sleep(retry_delay)

    logger.error("❌ Kafka não ficou pronto a tempo")
    return False

if __name__ == "__main__":
    brokers = sys.argv[1].split(',') if len(sys.argv) > 1 else [
        'kafka-controller:9092',
        'kafka-broker-2:9094',
        'kafka-broker-3:9095'
    ]

    if check_kafka_ready(brokers):
        sys.exit(0)
    else:
        sys.exit(1)