import serial
from Peripheral import Peripheral
import logging

class UartPeripheral(Peripheral):
    def __init__(self, port=None, baud_rate=115200, rtscts=True, initial_training_params = [0,0]):
        Peripheral.__init__(self, initial_training_params=initial_training_params)
        self._port = port
        self._baud_rate=baud_rate
        self._rtscts = rtscts
        self._connection = None
    
    @property
    def port(self):
        return self._port    
    
    def open_serial_connection(self):
        try:
            self._connection = serial.Serial(self._port, self._baud_rate, rtscts=self._rtscts)
            logging.info("Connection established to " + self._port)
        except Exception as e:
            logging.error(e)
            exit()
            
    def write_data(self, data: str):
        data = data + '\r'
        logging.info(f"Sending data: [{data}] to {self.port}")
        data = bytes(data, 'utf-8')
        try:
            self.flush_input_buffer()
            self._connection.write(data)
        except Exception as e:
            logging.error(e)

    def wait_for_data(self, timeout) -> str: 
        self._connection.timeout = timeout
        data = self._connection.read_until(b'\r').decode('utf-8')
        logging.info(f"Received: [{data}] from {self.port}")
        return data
    
    def flush_input_buffer(self):
        self._connection.reset_input_buffer()
        
    def kill_interface(self):
        self._connection.close()
            
        
    