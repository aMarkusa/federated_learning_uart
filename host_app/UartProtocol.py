from enum import Enum
import struct

class DataType(Enum):
    GLOBAL_MODEL_PARAMETERS = 0  # dtype = int16_t
    LOCAL_MODEL_PARAMETERS = 1  # dtype = int16_t
    DATASET_X = 2  # dtype = int16_t
    DATASET_Y = 3  # dtype = int16_t
    ACK = 4  # dtype = uint8_t
    
class UartProtocol():
    def __init__(self, max_packet_size=64):
        self._sequence = []
        self._sequence_ongoing = False
        self._max_packet_size = max
    
    def parse_uart_packet(self, raw_data, data_type: DataType) -> list:
        match data_type:
            case DataType.LOCAL_MODEL_PARAMETERS:
                parsed_data = struct.unpack(">hhh", raw_data)
            case DataType.ACK:
                parsed_data = struct.unpack(">B", raw_data)
            case _:
                pass
            
        return list(parsed_data)
      
    def construct_uart_packet(self, data_type: DataType, data: list, sequence):
        data_points_num = len(data)
        match data_type:
            case DataType.GLOBAL_MODEL_PARAMETERS:
                data_len = data_points_num * 2 
                format = ">BBBhh"
            case DataType.DATASET_X | DataType.DATASET_Y:
                data_len = data_points_num * 2
                format = f">BBB{data_points_num}h"
            case _:
                pass
            
        packet = [data_type.value, data_len, sequence]  # header
        packet.extend(data)
        packed_data = struct.pack(format, *packet)
        
        return packed_data
