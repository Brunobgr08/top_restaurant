from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka-init")

admin_client = KafkaAdminClient(
    bootstrap_servers="kafka:9092",
    client_id='admin-client'
)

logger.info("Verificando tópicos existentes...")
existing_topics = admin_client.list_topics()

logger.info(f"Tópicos existentes: {existing_topics}")

topic_definitions = {
    "order_created": {'retention.ms': '3600000'},
    "payment_processed": {'retention.ms': '3600000'},
    "order_ready": {'retention.ms': '600000'},
    "menu_updated": {'retention.ms': '86400000'}
}

topics_to_create = []
for topic_name, configs in topic_definitions.items():
    if topic_name not in existing_topics:
        topics_to_create.append(
            NewTopic(name=topic_name, num_partitions=1, replication_factor=1, topic_configs=configs)
        )

if topics_to_create:
    try:
        admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
        logger.info(f"Tópicos criados com sucesso: {[t.name for t in topics_to_create]}")
    except TopicAlreadyExistsError:
        logger.warning("Alguns tópicos já existiam.")
else:
    logger.info("Todos os tópicos já existem. Nenhum novo criado.")


# ### 🔧 Explicação das configurações dos tópicos
# - `num_partitions=1`: Cada tópico possui apenas uma partição para simplificar o ambiente (ideal para dev/testes)
# - `replication_factor=1`: Não há replicação, pois há apenas um broker (produção exige ≥2 para tolerância a falhas)
# - `retention.ms`: tempo de retenção das mensagens:
#   - `menu_updated, order_created` e `payment_processed`: 1 hora (suficiente para fluxo completo de pedido)
#   - `order_ready`: 10 minutos (apenas até o cliente receber notificação)

# Essas configurações garantem:
# - **Desempenho estável**
# - **Evita acúmulo desnecessário de mensagens antigas**
# - **Tópicos leves para um sistema de pedidos enxuto**sim