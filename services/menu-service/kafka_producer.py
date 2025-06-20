from shared.kafka.producer import get_kafka_producer
import json

def publish_menu_updated(item):
    producer = get_kafka_producer()
    data = {
        "event_type": "menu_updated",
        "payload": {
            "item_id": str(item.item_id),
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "available": item.available
        }
    }
    producer.produce("menu_updated", json.dumps(data).encode("utf-8"))
    producer.flush()
