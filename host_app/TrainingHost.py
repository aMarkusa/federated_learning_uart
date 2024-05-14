import serial
import logging
from UartPeripheral import *
from UartProtocol import *
from threading import Thread
import time

class TrainingHost():
    def __init__(self, max_iterations = 100, training_limit = 3, uart_peripherals = []):
        self._max_iterations = max_iterations
        self._training_limit = training_limit
        self._uart_peripherals : list[UartPeripheral] = uart_peripherals
        self._threads : list[Thread] = []
        self._logger = logging.getLogger(__name__)
        self._protocol = UartProtocol()
        
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
        self._logger.info("Printing peripherals training parameters:")
        for peripheral in self.uart_peripherals:
            self._logger.info(f"[{peripheral.port}] -> w: {peripheral.params[0]}, b: {peripheral.params[1]}, lowest mse: {peripheral.lowest_mse}")
        
    
    def data_handler(self, peripheral: UartPeripheral, data_header: list, parsed_data:list):
        match data_header[0]:
            case DataType.LOCAL_PARAMETERS.value:
                peripheral.params = [parsed_data[0], parsed_data[1]]
                peripheral.latest_mse = parsed_data[2]
                
                
    def update_global_params(self, peripherals:list[UartPeripheral]):
        w_numerator = float(sum([peripheral.params[0]*peripheral.dataset_len for peripheral in peripherals]))
        b_numerator = float(sum([peripheral.params[1]*peripheral.dataset_len for peripheral in peripherals]))
        denominator = float(sum([peripheral.dataset_len for peripheral in peripherals]))
         
        w_weighted_avg = w_numerator / denominator
        b_weighted_avg = b_numerator / denominator
        
        for peripheral in peripherals:
            peripheral.params = [w_weighted_avg, b_weighted_avg]
        
    
    def iterate_model(self, peripheral: UartPeripheral):  # This is run in a thread
        if peripheral.ready_to_receive:
            tx_data = [peripheral.params[0], peripheral.params[1]]
            peripheral.pack_and_write_data(DataType.GLOBAL_PARAMETERS, tx_data, 0)
            peripheral.ready_to_receive = False
            time.sleep(0.1)
        rx_data_header = peripheral.wait_for_data(peripheral.timeout)
        if len(rx_data_header) > 0:
            parsed_rx_data = peripheral.read_and_parse_data(rx_data_header)
            self.data_handler(peripheral, rx_data_header, parsed_rx_data)    
        else:
            pass
        '''if peripheral.consecutive_mse_increases >= self.training_limit:
            peripheral.training_done = True
            peripheral.consecutive_mse_increases = 0
        '''
        peripheral.current_training_iteration = peripheral.current_training_iteration + 1
        
    def train_model(self):  
        for i in range(self.max_iterations):
            for peripheral in self.uart_peripherals:
                if not peripheral.training_done:
                    thread = Thread(target=self.iterate_model(peripheral))
                    thread.start()
                    thread.join()
                    self._threads.append(thread)
                self._threads.clear()
                self.print_peripheral_parameters()
            
            self.update_global_params(self.uart_peripherals)
            if all(periph.training_done for periph in self.uart_peripherals):
                self._logger.info("Training done!")
                break