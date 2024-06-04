import serial
import logging
from UartPeripheral import *
from UartProtocol import *
from threading import Thread
from datasets.LinearDataset import LinearDataset
import time

# TODO: Check for training done
# TODO: Add sequence send

def logger():
    return logging.getLogger(__name__)

class TrainingHost():
    def __init__(self, starting_parameters, max_iterations = 100, training_limit = 2, uart_peripherals = [], dataset: LinearDataset = None, max_payload = 250):
        self._max_iterations = max_iterations
        self._training_limit = training_limit
        self._uart_peripherals : list[UartPeripheral] = uart_peripherals
        self._threads : list[Thread] = []
        self._protocol = UartProtocol()
        self._dataset = dataset
        self._global_parameters = starting_parameters
        self._best_global_parameters = []
        self._latest_mse = 0
        self._lowest_mse = 0
        self._consecutive_mse_increases = 0
        self._current_training_iteration = 0
        self._training_done = False
        self._max_payload_size = 250  # this is in byte elements. This mean 250 int8_t and 125 int16_t

        
    def connect_to_uart_peripherals(self):
        for peripheral in self.uart_peripherals:
            peripheral.open_serial_connection()
            
    def print_peripheral_parameters(self, peripheral: Peripheral):
        logger().info("Printing peripherals training parameters:")
        logger().info(f"[{peripheral.port}] -> w: {peripheral.params[0]}, b: {peripheral.params[1]}, lowest mse: {peripheral.lowest_mse}")
        
    
    def data_handler(self, peripheral: UartPeripheral, data_header: list, parsed_data:list):
        match data_header[0]:
            case DataType.LOCAL_MODEL_PARAMETERS.value:
                peripheral.params = [parsed_data[0], parsed_data[1]]
                peripheral.latest_mse = parsed_data[2]
        
    
    def iterate_model(self, peripheral: UartPeripheral):  # This is run in a thread
        if peripheral.ready_to_receive:
            tx_data = [peripheral.params[0], peripheral.params[1]]
            peripheral.pack_and_write_data(DataType.GLOBAL_MODEL_PARAMETERS, tx_data, 0)
            peripheral.ready_to_receive = False
            time.sleep(0.1)
        rx_data_header = peripheral.wait_for_data(peripheral.timeout)
        if len(rx_data_header) > 0:
            parsed_rx_data = peripheral.read_and_parse_data(rx_data_header)
            self.data_handler(peripheral, rx_data_header, parsed_rx_data)    
        else:
            pass
    
            
        peripheral.current_training_iteration = peripheral.current_training_iteration + 1
        
    def train_model(self):  
        for i in range(self.max_iterations):
            for peripheral in self.uart_peripherals:
                if not peripheral.training_done:
                    thread = Thread(target=self.iterate_model(peripheral))
                    self._threads.append(thread)          
            [thread.start() for thread in self._threads]
            [thread.join() for thread in self._threads]
            self._threads.clear()
            for peripheral in self.uart_peripherals:
                self.print_peripheral_parameters(peripheral)
            
            self.update_global_params(self.uart_peripherals)
            if self._training_done == True:
                break
            else:
                self._current_training_iteration = self._current_training_iteration + 1
    
    def update_global_params(self, peripherals:list[UartPeripheral]):
        w_numerator = float(sum([peripheral.params[0]*peripheral.dataset_len for peripheral in peripherals]))
        b_numerator = float(sum([peripheral.params[1]*peripheral.dataset_len for peripheral in peripherals]))
        denominator = float(sum([peripheral.dataset_len for peripheral in peripherals]))
         
        w_weighted_avg = w_numerator / denominator
        b_weighted_avg = b_numerator / denominator
        
        self.latest_mse = round(self._dataset.validate_parameters(w_weighted_avg, b_weighted_avg), 2)
        
        logger().info(f"Training iteration {self._current_training_iteration} resulted in -> w: {w_weighted_avg}, b: {b_weighted_avg}, mse: {self.latest_mse}")
        
        if self._consecutive_mse_increases >= self.training_limit:
            logger().info("Training done")
            self._training_done = True
        else:
            for peripheral in peripherals:
                peripheral.params = [w_weighted_avg, b_weighted_avg]
                peripheral._ready_to_receive = True

   
    def send_out_training_data(self):
        for peripheral in self.uart_peripherals:
            x_values = peripheral._x_values
            y_values = peripheral._y_values
            max_payload_size = int(self._max_payload_size / 2)
            send_sequence(DataType.DATASET_X, x_values, max_payload_size, peripheral)
            send_sequence(DataType.DATASET_Y, y_values, max_payload_size, peripheral)
            
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
        
    @property
    def latest_mse(self):
        return self._latest_mse
    
    @latest_mse.setter
    def latest_mse(self, mse):
        self._latest_mse = mse
        if self._current_training_iteration == 0:
            self.lowest_mse = mse
        elif mse < self.lowest_mse:
            self.lowest_mse = mse
            self._consecutive_mse_increases = 0
        else:
            self._consecutive_mse_increases = self._consecutive_mse_increases + 1
        
    @property
    def lowest_mse(self):
        return self._lowest_mse
    
    @lowest_mse.setter
    def lowest_mse(self, mse):
        self._lowest_mse = mse

def send_sequence(datatype: DataType, sequence_buffer, max_payload_size: int, peripheral: Peripheral): 
    total_len = len(sequence_buffer)
    remaining_len = total_len
    sliding_window_start = 0
    sliding_window_end = max_payload_size

    sequence_nr = 1
    while remaining_len > 0: 
        if remaining_len <= max_payload_size:  # TODO: This could be done a bit cleaner  
            sequence_nr = 255
            sliding_window_end = total_len
        payload = sequence_buffer[sliding_window_start: sliding_window_end]
        last_received_sequence = peripheral.pack_and_write_data(datatype, payload, sequence_nr)
        if last_received_sequence != sequence_nr:
            remaining_len = total_len - last_received_sequence * max_payload_size
            sequence_nr = last_received_sequence
        else:
            remaining_len = remaining_len - len(payload)
            if sequence_nr == 255:
                break
        
        sliding_window_start = sequence_nr * max_payload_size    
        sliding_window_end = sliding_window_start + max_payload_size
        sequence_nr = sequence_nr + 1
        #time.sleep(0.1)
    

        
            
