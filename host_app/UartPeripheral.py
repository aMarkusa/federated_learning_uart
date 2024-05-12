import serial
from Peripheral import Peripheral
from UartProtocol import DataType
import logging
import struct

class UartPeripheral(Peripheral):
    def __init__(self, port=None, baud_rate=115200, rtscts=True, initial_training_params = [0,0]):
        Peripheral.__init__(self, initial_training_params=initial_training_params)
        self._port = port
        self._baud_rate=baud_rate
        self._rtscts = rtscts
        self._connection = None
        self._logger = logging.getLogger(__name__)
    
    @property
    def port(self):
        return self._port    
    
    def open_serial_connection(self):
        try:
            self._connection = serial.Serial(self._port, self._baud_rate, rtscts=self._rtscts)
            self._logger.info("Connection established to " + self._port)
        except Exception as e:
            self._logger.error(e)
            exit()
            
    def write_data(self, data: str):
        port = self.port
        self._logger.info(f"Sending data: [{data}] to {self.port}")
        data = data + '\r'
        data = bytes(data, 'utf-8')
        try:
            self.flush_input_buffer()
            self._connection.write(data)
        except Exception as e:
            self._logger.error(e)

    def wait_for_data(self, timeout) -> str: 
        self._connection.timeout = timeout
        raw_data_header = self._connection.read(2)
        data_header = struct.unpack('>bb', raw_data_header)
        data_len = data_header[0]
        data_type = data_header[1]
        
        match data_type:
            case DataType.LOCAL_PARAMETERS.value:
                raw_data = self._connection.read(data_len)
                data = struct.unpack('>hhh', raw_data)
                data = data.rstrip()
            case _:
                pass
            
        self._logger.info(f"Received: [{data}] from {self.port}")
        return data
    
    def flush_input_buffer(self):
        self._connection.reset_input_buffer()
        
    def kill_interface(self):
        self._connection.close()
            
        
    