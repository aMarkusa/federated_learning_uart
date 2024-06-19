#!/Users/maanders1/miniconda3/bin/python
from serial.tools import list_ports
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
from LinearDataset import *
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
INITIAL_W = 7
INITIAL_B = 5
INITIAL_PARAMS = f"{INITIAL_W}:{INITIAL_B}"
parsed_data = []
consecutive_increases = 0
dataset_parent_folder_path = Path(Path(__file__).resolve().parent, "datasets")
already_existing_dataset_path = "/Users/maanders1/personal/git/federated_learning_project/fl_workspace/federated_learning_over_usart/host_app/datasets/202406-1718-3304-5a0bac66-1e14-4296-8358-2cb372ae01cc/inital_datasets/"


def logger():
    return logging.getLogger(__name__)


def setup_logger():
    # Create a logger
    os.environ["PYTHONUNBUFFERED"] = "1"
    logger = logging.getLogger()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format=format)
    logging.getLogger('matplotlib.font_manager').disabled = True


if __name__ == "__main__":
    setup_logger()
    # Read all silabs peripherals, generate a dataset, divide the dataset, and assign the partial datasets to peripherals
    ports = list(list_ports.comports())
    peripheral_ports = [
        port for port in ports if port.device.startswith("/dev/cu.usbmodem")
    ]
    if len(peripheral_ports) == 0:
        logger().error("No peripherals detected. Exiting program.")
        exit()

    logger().info(
        f"{len(peripheral_ports)} peripherals detected. Press enter to generate training data and send it to the peripherals."
    )
    input()

    peripherals = [
        UartPeripheral(
            nickname=port.name,
            initial_training_params=[INITIAL_W, INITIAL_B],
            port=port.device,
        )
        for port in peripheral_ports
    ]
    if GENERATE_DATASET:
        full_dataset = prepare_datasets(
            len(peripherals),
            5,
            2,
            NUMBER_OF_DATAPOINTS,
            str(dataset_parent_folder_path),
        )
        assign_partial_datasets(peripherals, str(full_dataset._initial_datasets_path))
    else:
        # TODO: this does not work :( 
        assign_partial_datasets(peripherals, already_existing_dataset_path)

    # Create a trainer, connect to the peripherals, and send out the training data
    trainer = TrainingHost(
        starting_parameters=[INITIAL_W, INITIAL_B],
        uart_peripherals=peripherals,
        max_training_iterations=MAX_ITERATIONS,
        dataset=full_dataset,
        training_limit=2,
    )
    trainer.connect_to_uart_peripherals()
    trainer.send_out_training_data()

    logger().info(f"Training data sent out. Press enter to start training.")
    input()
    # Print the initial parameters for each peripheral, and start the training
    for peripheral in peripherals:
        trainer.print_peripheral_parameters(peripheral)
    trainer.train_model()

    # Once training is done, create plots to visualize the model
    model_weight = trainer.best_global_parameters[0]
    model_bias = trainer.best_global_parameters[1]
    model_rmse = trainer.lowest_rmse

    # model_weight = -1
    # model_bias = 2
    # model_rmse = 30
    full_dataset.create_final_plots(
        model_weight,
        model_bias,
        INITIAL_W,
        INITIAL_B,
        model_rmse,
        peripherals,
        str(dataset_parent_folder_path),
    )
