#!/Users/maanders1/miniconda3/bin/python
from serial.tools import list_ports
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
import datasets.LinearDataset as ld
import logging
from time import sleep
import sys
import os
import numpy as np
from pathlib import Path

GENERATE_DATASET = True
NUMBER_OF_DATAPOINTS = 5000
MAX_ITERATIONS = 100
MAX_MSE_INCREASES = 5
START_W = 2.6
START_B = 1
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0


def logger():
    return logging.getLogger(__name__)


def setup_logger():
    # Create a logger
    os.environ["PYTHONUNBUFFERED"] = "1"
    logger = logging.getLogger()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)


if __name__ == "__main__":
    setup_logger()
    # Read all silabs peripherals, generate a dataset, divide the dataset, and assign the partial datasets to peripherals
    ports = list(list_ports.comports())
    peripheral_ports = [
        port for port in ports if port.device.startswith("/dev/cu.usbmodem")
    ]
    logger().info(f"{len(peripheral_ports)} peripherals detected. Press enter to generate training data and send it to the peripherals.")
    input()
    
    peripherals = [
        UartPeripheral(nickname=port.name , initial_training_params=[START_W, START_B], port=port.device)
        for port in peripheral_ports
    ]
    if GENERATE_DATASET:
        full_dataset = ld.prepare_datasets(len(peripherals), -5, 2, NUMBER_OF_DATAPOINTS)
    full_dataset.assign_partial_datasets(peripherals)

    # Create a trainer, connect to the peripherals, and send out the training data
    trainer = TrainingHost(
        starting_parameters=[START_W, START_B],
        uart_peripherals=peripherals,
        max_training_iterations=MAX_ITERATIONS,
        dataset=full_dataset,
        training_limit=2,
    )
    trainer.connect_to_uart_peripherals()
    trainer.send_out_training_data()

    logger().info(f"Training data sent out. Press enter to start training.")
    input()
    # # Print the initial parameters for each peripheral, and start the training
    for peripheral in peripherals:
        trainer.print_peripheral_parameters(peripheral)
    trainer.train_model()

    # Once training is done, create plots to visualize the model
    model_weight = trainer.best_global_parameters[0]
    model_bias = trainer.best_global_parameters[1]
    model_rmse = trainer.lowest_rmse
    ld.create_final_plots(model_weight, model_bias, model_rmse, peripherals, full_dataset)
