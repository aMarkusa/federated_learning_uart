#!/Users/maanders1/miniconda3/bin/python
from serial.tools import list_ports
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
from datasets.LinearDataset import *
import logging
from time import sleep
import sys
import os
import numpy as np
from pathlib import Path

GENERATE_DATASET = True
MAX_ITERATIONS = 100
MAX_MSE_INCREASES = 5
START_W = -2.6
START_B = 1
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0


def setup_logger():
    # Create a logger
    os.environ["PYTHONUNBUFFERED"] = "1"
    logger = logging.getLogger()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)


def prepare_datasets(number_of_peripherals):
    dataset = LinearDataset(2000, 2, 5)
    dataset.divide_and_save_datasets(number_of_peripherals)

    return dataset


def get_total_dataset():
    for file in os.listdir(script_path + "/" + "datasets"):
        if "total_linear_dataset" in file:
            file_path = script_path + "/" + "datasets" + "/" + file
            data = np.genfromtxt(file_path, delimiter=",", dtype=int, skip_header=True)
            x_values = data[0:, 0].tolist()
            y_values = data[0:, 1].tolist()


if __name__ == "__main__":
    # Read all silabs peripherals, generate a dataset, divide the dataset, and assign the partial datasets to peripherals
    ports = list(list_ports.comports())
    peripheral_ports = [
        port for port in ports if port.device.startswith("/dev/cu.usbmodem")
    ]
    setup_logger()
    peripherals = [
        UartPeripheral(initial_training_params=[START_W, START_B], port=port.device)
        for port in peripheral_ports
    ]
    if GENERATE_DATASET:
        full_dataset = prepare_datasets(len(peripherals))
    assign_partial_datasets(peripherals)

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

    # Print the initial parameters for each peripheral, and start the training
    for peripheral in peripherals:
        trainer.print_peripheral_parameters(peripheral)
    trainer.train_model()

    # Once training is done, create plots to visualize the model
    model_weight = trainer.best_global_parameters[0]
    model_bias = trainer.best_global_parameters[1]
    create_final_plots(model_weight, model_bias, peripherals, full_dataset)
