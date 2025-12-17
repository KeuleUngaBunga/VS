import sys
from rabbitmq_connector import RabbitMQConnector
from message_bus import MessageBus
from process import GGTProcess

import logging


def main():
    if len(sys.argv) < 5:
        print("Usage: ggt_worker.py <process_id> <initial_value> <pred> <succ> [host]")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    process_id = int(sys.argv[1])
    initial_value = int(sys.argv[2])
    pred = int(sys.argv[3])
    succ = int(sys.argv[4])
    host = sys.argv[5] if len(sys.argv) > 5 else "localhost"

    connector = RabbitMQConnector(host, process_id)
    bus = MessageBus(connector)

    process = GGTProcess(process_id, initial_value, pred, succ, connector, bus)
    process.start()


if __name__ == "__main__":
    main()

# import sys
# from rabbitmq_connector import RabbitMQConnector
# from message_bus import MessageBus
# from process import GGTProcess
        
# import logging


# def main():
#     if len(sys.argv) < 5:
#         print("Usage: ggt_worker.py <process_id> <initial_value> <pred> <succ> [host]")
#         sys.exit(1)

#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )

#     process_id = int(sys.argv[1])
#     initial_value = int(sys.argv[2])
#     pred = int(sys.argv[3])
#     succ = int(sys.argv[4])
#     host = sys.argv[5] if len(sys.argv) > 5 else "localhost"

#     connector = RabbitMQConnector(host, process_id)
#     bus = MessageBus(connector)

#     process = GGTProcess(process_id, initial_value, pred, succ, connector, bus)
#     process.start()

# if __name__ == "__main__":
#     main()

