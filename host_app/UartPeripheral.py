import serial
from Peripheral import Peripheral
from UartProtocol import *
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
        self._uart_protocol = UartProtocol()
        self._rx_sequence = []
    
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
            
    def pack_and_write_data(self, data_type: DataType, data: str, sequence):
        self._logger.info(f"Sending data: [{data_type.value}, {len(data)}, {sequence}, {data[0]}, {data[1]}] to {self.port}")
        data = self._uart_protocol.construct_uart_packet(data_type, data, sequence)
        try:
            self.flush_input_buffer()
            self._connection.write(data)
        except Exception as e:
            self._logger.error(e)

    def wait_for_data(self, timeout) -> str: 
        self._connection.timeout = timeout
        raw_data_header = self._connection.read(3)
        data_header = struct.unpack('>bbb', raw_data_header)
        
        return data_header
    
    def read_and_parse_data(self, data_header: list):
        raw_data = self._connection.read(data_header[1])
        parsed_data = self._uart_protocol.parse_uart_packet(raw_data, DataType(data_header[0]))
        
        return parsed_data
    
    def flush_input_buffer(self):
        self._connection.reset_input_buffer()
        
    def kill_interface(self):
        self._connection.close()
            
        
    