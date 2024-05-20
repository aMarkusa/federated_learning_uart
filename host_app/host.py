#!/Users/maanders1/miniconda3/bin/python
from serial.tools import list_ports
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
from host_app.dataset.LinearDataset import LinearDataset
import logging
from time import sleep
import sys
import os

MAX_ITERATIONS = 100
MAX_MSE_INCREASES = 5
START_W = 10
START_B = 5
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0


def setup_logger():
    # Create a logger
    os.environ['PYTHONUNBUFFERED'] = '1'
    logger = logging.getLogger()
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)
    
def prepare_dataset(number_of_peripherals):
    dataset = LinearDataset(5000, -1, 0)
    dataset.divide_and_save_datasets(2)
    
    return dataset

   

if __name__ == "__main__":
    ports = list(list_ports.comports())
    peripheral_ports = [port for port in ports if port.device.startswith('/dev/cu.usbmodem')]
    setup_logger()
    peripherals = [UartPeripheral(initial_training_params=[START_W, START_B], port=port.device) 
                   for port in peripheral_ports]
    dataset = prepare_dataset(len(peripherals))
    trainer = TrainingHost(uart_peripherals=peripherals, max_iterations=MAX_ITERATIONS)
    trainer.connect_to_uart_peripherals()
    
    trainer.print_peripheral_parameters()
    trainer.train_model()
        
       


        