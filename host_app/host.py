#!/Users/maanders1/miniconda3/bin/python
from serial.tools import list_ports
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
from datasets.LinearDataset import LinearDataset
import logging
from time import sleep
import sys
import os
import numpy as np
from pathlib import Path

GENERATE_DATASET = False
MAX_ITERATIONS = 100
MAX_MSE_INCREASES = 5
START_W = 10
START_B = 5
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0

script_path = str(Path(__file__).resolve().parent)

def setup_logger():
    # Create a logger
    os.environ['PYTHONUNBUFFERED'] = '1'
    logger = logging.getLogger()
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)
    
def prepare_datasets(number_of_peripherals):
    dataset = LinearDataset(920, -1, 0)
    dataset.divide_and_save_datasets(number_of_peripherals)
    
    return dataset

def assign_partial_datasets(peripherals: list[UartPeripheral]):
    peripheral_index = 0
    for file in os.listdir(script_path + '/' + "datasets"):
        if file.endswith('.csv'):
            file_path = script_path + '/' + "datasets" + '/' + file
            data = np.genfromtxt(file_path, delimiter=',',dtype=int, skip_header=True)
            x_values = data[0:, 0].tolist() 
            y_values = data[0:, 1].tolist()
            
            peripherals[peripheral_index].x_values = x_values
            peripherals[peripheral_index].y_values = y_values
            
            peripheral_index = peripheral_index + 1

   

if __name__ == "__main__":
    ports = list(list_ports.comports())
    peripheral_ports = [port for port in ports if port.device.startswith('/dev/cu.usbmodem')]
    setup_logger()
    peripherals = [UartPeripheral(initial_training_params=[START_W, START_B], port=port.device) 
                   for port in peripheral_ports]
    if GENERATE_DATASET:
        full_dataset = prepare_datasets(len(peripherals))
    assign_partial_datasets(peripherals)
    trainer = TrainingHost(uart_peripherals=peripherals, max_iterations=MAX_ITERATIONS)
    trainer.connect_to_uart_peripherals()
    trainer.send_out_training_data()
    for peripheral in peripherals:
        trainer.print_peripheral_parameters(peripheral)
    trainer.train_model()
        
       


        