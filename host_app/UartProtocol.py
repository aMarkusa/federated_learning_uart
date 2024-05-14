from enum import Enum
import struct

class DataType(Enum):
    GLOBAL_PARAMETERS = 0
    LOCAL_PARAMETERS = 1
    
class UartProtocol():
    def __init__(self, max_packet_size=64):
        self._sequence = []
        self._sequence_ongoing = False
        self._max_packet_size = max
    
    def parse_uart_packet(self, raw_data, data_type: DataType):
        match data_type:
            case DataType.LOCAL_PARAMETERS:
                parsed_data = struct.unpack('>hhh', raw_data)
                return parsed_data
            case _:
                pass
      
    def construct_uart_packet(self, data_type: DataType, data: list, sequence):
        data_len = len(data) * 2 # long split to bytes
        data.insert(0, sequence)
        data.insert(0, data_len)
        data.insert(0, data_type.value)
        match data_type:
            case DataType.GLOBAL_PARAMETERS:
                packed_data = struct.pack('>bbbhh', *data)    
                return packed_data
            case _:
                pass
