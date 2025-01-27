import serial
import logging
from UartPeripheral import *
from UartProtocol import *
from threading import Thread
from LinearDataset import LinearDataset, calculate_rmse
import time


def logger():
    return logging.getLogger(__name__)


class TrainingHost:
    def __init__(
        self,
        starting_parameters,
        max_training_iterations=100,
        training_limit=2,
        uart_peripherals=[],
        dataset: LinearDataset = None,
        max_payload=250,
    ):
        self._max_training_iterations = max_training_iterations
        self._training_limit = training_limit
        self._uart_peripherals: list[UartPeripheral] = uart_peripherals
        self._threads: list[Thread] = []
        self._protocol = UartProtocol()
        self._dataset = dataset
        self._latest_global_parameters = starting_parameters
        self._best_global_parameters = []
        self._latest_rmse = 0
        self._lowest_rmse = 0
        self._consecutive_rmse_increases = 0
        self._current_training_iteration = 0
        self._training_done = False
        self._max_payload_size = (
            250  # this is in byte elements. This mean 250 int8_t and 125 int16_t
        )

    def connect_to_uart_peripherals(self):
        for peripheral in self.uart_peripherals:
            peripheral.open_serial_connection()

    def print_peripheral_parameters(self, peripheral: Peripheral):
        logger().info("Printing peripherals training parameters:")
        logger().info(
            f"[{peripheral.port}] -> w: {peripheral.params[0]}, b: {peripheral.params[1]}, lowest rmse: {peripheral.lowest_rmse}"
        )

    def data_handler(
        self, peripheral: UartPeripheral, data_header: list, parsed_data: list
    ):
        match data_header[0]:
            case DataType.LOCAL_MODEL_PARAMETERS.value:
                peripheral.params = [parsed_data[0], parsed_data[1]]
                peripheral.latest_rmse = round(parsed_data[2], 1)

    def iterate_model(self, peripheral: UartPeripheral):
        """Send out the global parameters, wait for the peripheral to complete a training iteration, and receive the local parameters."""
        if peripheral.ready_to_receive:
            tx_data = [peripheral.params[0], peripheral.params[1]]
            peripheral.pack_and_write_data(DataType.GLOBAL_MODEL_PARAMETERS, tx_data, 0)
            peripheral.ready_to_receive = False
        rx_data_header = peripheral.wait_for_data(peripheral.timeout)
        if len(rx_data_header) > 0:
            parsed_rx_data = peripheral.read_and_parse_data(rx_data_header)
            self.data_handler(peripheral, rx_data_header, parsed_rx_data)
        else:
            pass

        peripheral.current_training_iteration = (
            peripheral.current_training_iteration + 1
        )

    def train_model(self):
        """Start threads for each peripheral, wait for them to finish, and update the global parameters."""
        for i in range(self.max_training_iterations):
            for peripheral in self.uart_peripherals:
                thread = Thread(target=self.iterate_model(peripheral))
                self._threads.append(thread)
            [thread.start() for thread in self._threads]
            [thread.join() for thread in self._threads]
            self._threads.clear()

            for peripheral in self.uart_peripherals:
                self.print_peripheral_parameters(peripheral)

            self.calculate_global_params(self.uart_peripherals)

            model_weight = self._latest_global_parameters[0]
            model_bias = self._latest_global_parameters[1]
            self._latest_rmse = calculate_rmse(
                model_weight, model_bias, self._dataset.model_inputs, self._dataset.model_targets
            )
            logger().info(f"Training iteration {self._current_training_iteration} resulted in:" +
                           f" RMSE: {self._latest_rmse}, w: {model_weight}, b: {model_bias}")
            if self.is_training_done():
                logger().info(
                    f"RMSE has not improved for {self._training_limit} iterations. Training done."
                )
                break
            else:
                self.update_peripheral_parameters()
                self._current_training_iteration = self._current_training_iteration + 1

            for peripheral in self.uart_peripherals:
                    peripheral.final_rmse = calculate_rmse(self.best_global_parameters[0], self.best_global_parameters[1], peripheral.model_inputs, peripheral.model_targets)
            
    def is_training_done(self):
        if (
            self._current_training_iteration == 0
            or self._latest_rmse < self._lowest_rmse
        ):
            self._lowest_rmse = self._latest_rmse
            self._best_global_parameters = self._latest_global_parameters
            self._consecutive_rmse_increases = 0
        else:
            self._consecutive_rmse_increases = self._consecutive_rmse_increases + 1
            if self._consecutive_rmse_increases >= self.training_limit:
                return True

        return False

    def update_peripheral_parameters(self):
        for peripheral in self.uart_peripherals:
            peripheral.params = self._latest_global_parameters
            peripheral._ready_to_receive = True

    def calculate_global_params(self, peripherals: list[UartPeripheral]):
        w_numerator = float(
            sum(
                [
                    peripheral.params[0] * peripheral.dataset_len
                    for peripheral in peripherals
                ]
            )
        )
        b_numerator = float(
            sum(
                [
                    peripheral.params[1] * peripheral.dataset_len
                    for peripheral in peripherals
                ]
            )
        )
        denominator = float(sum([peripheral.dataset_len for peripheral in peripherals]))

        w_weighted_avg = round(w_numerator / denominator, 2)
        b_weighted_avg = round(b_numerator / denominator, 2)

        self._latest_global_parameters = [w_weighted_avg, b_weighted_avg]

    def send_out_training_data(self):
        for peripheral in self.uart_peripherals:
            model_inputs = peripheral._model_inputs
            model_targets = peripheral._model_targets
            max_payload_size = int(self._max_payload_size / 2)
            send_sequence(DataType.DATASET_X, model_inputs, max_payload_size, peripheral)
            send_sequence(DataType.DATASET_Y, model_targets, max_payload_size, peripheral)

    @property
    def max_training_iterations(self):
        return self._max_training_iterations

    @max_training_iterations.setter
    def max_training_iterations(self, iterations):
        self._max_training_iterations = iterations

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
    def latest_rmse(self):
        return self._latest_rmse

    @latest_rmse.setter
    def latest_rmse(self, rmse):
        self._latest_rmse = rmse

    @property
    def lowest_rmse(self):
        return self._lowest_rmse

    @lowest_rmse.setter
    def lowest_rmse(self, rmse):
        self._lowest_rmse = rmse

    @property
    def best_global_parameters(self):
        return self._best_global_parameters

    @best_global_parameters.setter
    def best_global_parameters(self, global_parameters: list):
        self._best_global_parameters = global_parameters


def send_sequence(
    datatype: DataType, sequence_buffer, max_payload_size: int, peripheral: Peripheral
):
    total_len = len(sequence_buffer)
    remaining_len = total_len
    sliding_window_start = 0
    sliding_window_end = max_payload_size

    sequence_nr = 1
    while remaining_len > 0:
        if remaining_len <= max_payload_size:  # TODO: This could be done a bit cleaner
            sequence_nr = 255
            sliding_window_end = total_len
        payload = sequence_buffer[sliding_window_start:sliding_window_end]
        last_received_sequence = peripheral.pack_and_write_data(
            datatype, payload, sequence_nr
        )
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
        # time.sleep(0.1)
