from kafka import KafkaConsumer
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from controllers import create_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-consumer")

DATABASE_URL = 'postgresql://user:pass@notification-db:5432/notificationdb'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

consumer = KafkaConsumer(
    'payment_processed', 'order_ready',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='notification-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

logger.info("Aguardando mensagens nos tópicos 'payment_processed' e 'order_ready'...")

for message in consumer:
    logger.info(f"Mensagem recebida do tópico {message.topic}: {message.value}")
    session = Session()
    data = message.value
    if message.topic == 'payment_processed':
        create_notification(session, {
            'recipient': 'admin@local',
            'message': f"Pagamento processado para o pedido {data['order_id']}"
        })
    elif message.topic == 'order_ready':
        create_notification(session, {
            'recipient': 'customer@local',
            'message': f"Seu pedido #{data['order_id']} está pronto para retirada. {data['pickup_time']}"
        })