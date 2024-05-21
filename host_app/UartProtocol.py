from enum import Enum
import struct

class DataType(Enum):
    GLOBAL_PARAMETERS = 0  # dtype = int16_t
    LOCAL_PARAMETERS = 1  # dtype = int16_t
    DATASET_X = 3  # dtype = int16_t
    DATASET_Y = 4  # dtype = int16_t
    SEQUENCE_START = 5  # dtype = uint16_t
    
class UartProtocol():
    def __init__(self, max_packet_size=64):
        self._sequence = []
        self._sequence_ongoing = False
        self._max_packet_size = max
    
    def parse_uart_packet(self, raw_data, data_type: DataType) -> list:
        match data_type:
            case DataType.LOCAL_PARAMETERS:
                parsed_data = struct.unpack(">hhh", raw_data)
                return list(parsed_data)
            case _:
                pass
      
    def construct_uart_packet(self, data_type: DataType, data: list, sequence):
        match data_type:
            case DataType.GLOBAL_PARAMETERS:
                data_len = len(data) * 2 
                format = ">BBBhh"
            case DataType.SEQUENCE_START:
                data_len = len(data) * 2 
                data[0] = data[0] * 2
                format = ">BBBH"
            case DataType.DATASET_X | DataType.DATASET_Y:
                data_len = len(data) * 2
                format = f">BBB{data_len + 3}h"
            case _:
                pass
            
        packet = [data_type.value, data_len, sequence]  # header
        packet.extend(data)
        packed_data = struct.pack(format, 5,2,1,1840)
        
        return packed_data
