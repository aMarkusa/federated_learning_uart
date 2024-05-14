#!/Users/maanders1/miniconda3/bin/python
from UartPeripheral import UartPeripheral
from TrainingHost import TrainingHost
import logging
from time import sleep
import sys
import os

MAX_ITERATIONS = 100
MAX_MSE_INCREASES = 5
START_W = 0
START_B = 0
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0

peripheral_ports = ['/dev/cu.usbmodem0004402930881']


def setup_logger():
    # Create a logger
    os.environ['PYTHONUNBUFFERED'] = '1'
    logger = logging.getLogger()
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)

   

if __name__ == "__main__":
    setup_logger()
    peripherals = [UartPeripheral(initial_training_params=[START_W, START_B], port=port) 
                   for port in peripheral_ports]
    trainer = TrainingHost(uart_peripherals=peripherals, max_iterations=MAX_ITERATIONS)
    trainer.connect_to_uart_peripherals()
    
    trainer.print_peripheral_parameters()
    trainer.train_model()
        
       


        