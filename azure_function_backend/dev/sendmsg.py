from azure.servicebus import ServiceBusClient, ServiceBusMessage

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_sender(queue_name) as sender:
        # Sending a single message
        # single_message = ServiceBusMessage("03082021")
        # sender.send_messages(single_message)

        # Sending a list of messages
        messages = [ServiceBusMessage("28122019"), ServiceBusMessage("09122020"), ServiceBusMessage("10082021"), ServiceBusMessage("25032017")]
        sender.send_messages(messages)