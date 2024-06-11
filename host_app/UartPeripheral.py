import serial
from Peripheral import Peripheral
from UartProtocol import *
import logging
import struct


def logger():
    return logging.getLogger(__name__)


class UartPeripheral(Peripheral):
    def __init__(
        self, nickname, port=None, baud_rate=115200, rtscts=True, initial_training_params=[0, 0]
    ):
        Peripheral.__init__(self, initial_training_params=initial_training_params, nickname=nickname)
        self._port = port
        self._baud_rate = baud_rate
        self._rtscts = rtscts
        self._connection = None
        self._uart_protocol = UartProtocol()
        self._rx_sequence = []

    @property
    def port(self):
        return self._port

    def open_serial_connection(self):
        try:
            self._connection = serial.Serial(
                self._port, self._baud_rate, rtscts=self._rtscts
            )
            logger().info("Connection established to " + self._port)
        except Exception as e:
            logger().error(e)
            exit()

    def pack_and_write_data(self, data_type: DataType, data: list, sequence):
        data = self._uart_protocol.construct_uart_packet(data_type, data, sequence)
        try:
            self.flush_input_buffer()
            logger().info(f"Sending data: {data} to {self.port}")
            self._connection.write(data)
        except Exception as e:
            logger().error(e)

        return self.wait_for_ack()

    def wait_for_data(self, timeout) -> list:
        self._connection.timeout = timeout
        raw_data_header = self._connection.read(3)
        data_header = struct.unpack(">bbb", raw_data_header)

        return list(data_header)

    def read_and_parse_data(self, data_header: list):
        raw_data = self._connection.read(data_header[1])
        parsed_data = self._uart_protocol.parse_uart_packet(
            raw_data, DataType(data_header[0])
        )
        logger().info(f"Received data {data_header + parsed_data} from {self.port}")

        return parsed_data

    def flush_input_buffer(self):
        self._connection.reset_input_buffer()

    def kill_interface(self):
        self._connection.close()

    def wait_for_ack(self):
        ack_header = self.wait_for_data(20)
        if ack_header:
            ack_data = self.read_and_parse_data(ack_header)
            return ack_data[0]
