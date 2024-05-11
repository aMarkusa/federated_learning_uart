import serial
import logging
from UartPeripheral import *
from threading import Thread
import time

class TrainingHost():
    def __init__(self, max_iterations = 100, training_limit = 3, uart_peripherals = []):
        self._max_iterations = max_iterations
        self._training_limit = training_limit
        self._uart_peripherals : list[UartPeripheral] = uart_peripherals
        self._threads : list[Thread] = []
        
    @property
    def max_iterations(self):
        return self._max_iterations
    
    @max_iterations.setter
    def max_iterations(self, iterations):
        self._max_iterations = iterations
        
    @property
    def training_limit(self):
        return self._training_limit
    
    @training_limit.setter
    def training_limit(self, limit):
        self._training_limit = limit
        
    @property
    def uart_peripherals(self): 
        return self._uart_peripherals
    
    @uart_peripherals.setter
    def uart_peripherals(self, peripherals):
        self._uart_peripherals = peripherals
        
    def connect_to_uart_peripherals(self):
        for peripheral in self.uart_peripherals:
            peripheral.open_serial_connection()
            
    def print_peripheral_parameters(self):
        logging.info("Printing peripherals training parameters:")
        for peripheral in self.uart_peripherals:
            logging.info(f"[{peripheral.port}] -> w: {peripheral.params[0]}, b: {peripheral.params[1]}")
        
    def parse_rx_data(self, rx_data) -> list:
        parsed_rx_data = rx_data.split(':') 
        print(parsed_rx_data)
        return parsed_rx_data
        
    
    def iterate_model(self, peripheral: UartPeripheral):  # This is run in a thread
        if peripheral.ready_to_receive:
            tx_data = f"{peripheral.params[0]}:{peripheral.params[1]}"
            peripheral.write_data(tx_data)
            peripheral.active_training = True
            peripheral.ready_to_receive = False
            time.sleep(0.1)
        rx_data = peripheral.wait_for_data(peripheral.timeout)
        if len(rx_data) > 0:
            parsed_rx_data = self.parse_rx_data(rx_data)
            peripheral.params = [parsed_rx_data[0], parsed_rx_data[1]]
            peripheral.latest_mse = parsed_rx_data[2]
        else:
            pass
        if peripheral.consecutive_mse_increases >= self.training_limit:
            peripheral.active_training = False
      
    def train_model(self):  
        for i in range(self.max_iterations):
            for peripheral in self.uart_peripherals:
                thread = Thread(target=self.iterate_model(peripheral))
                thread.start()
                thread.join()
                self._threads.append(thread)
            self.print_peripheral_parameters
              