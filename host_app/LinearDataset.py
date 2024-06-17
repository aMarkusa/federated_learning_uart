import numpy as np
import pandas as pd
import random
from pathlib import Path
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import os
from UartPeripheral import UartPeripheral
from uuid import uuid4
from matplotlib.axes import Axes
from datetime import datetime
import logging

script_path = str(Path(__file__).resolve().parent)

# TODO: create validation set
# TODO: Add Initial guess line to 


def logger():
    return logging.getLogger(__name__)


class LinearDataset:
    def __init__(
        self,
        dataset_len: int,
        weight,
        bias,
        value_range=100,
        min_points_per_dataset=100,
    ):
        self._dataset_len = dataset_len
        self._weight = weight
        self._bias = bias
        self._value_range = value_range
        self._min_points_per_dataset = min_points_per_dataset
        self._model_inputs = None
        self._model_targets = None
        self._initial_model = None
        self._uuid = None
        self._initial_datasets_path = None
        self._dataset_target_range = 500  # +- 32000 (approx int16_t)

    def generate_dataset(self, dataset_parent_folder_path: str, full_dataset_name: str):
        self._uuid = datetime.now().strftime("%Y%m-%d%H-%M%S-") + str(uuid4())
        self._initial_datasets_path = Path(
            dataset_parent_folder_path, self._uuid, "inital_datasets"
        )
        os.makedirs(self._initial_datasets_path, exist_ok=False)

        input_max_value = abs(
            int((self._dataset_target_range - self._bias) / self._weight)
        )

        self._model_inputs = np.random.randint(
            low=(-input_max_value), high=input_max_value, size=self._dataset_len
        )
        self._model_targets = (
            self._weight * self._model_inputs
            + self._bias
            + np.random.randint(
                low=-(self._value_range), high=self._value_range, size=self._dataset_len
            )
        )
        save_dataset(
            self._model_inputs,
            self._model_targets,
            self._initial_datasets_path,
            full_dataset_name,
        )
        fig, ax = plt.subplots(1, 1)
        ax = plot_dataset(ax, self._model_inputs, self._model_targets)
        fig.suptitle(full_dataset_name)
        fig.savefig(str(self._initial_datasets_path) + "/" + full_dataset_name + ".png")

    def divide_and_save_datasets(self, divisor, partial_dataset_name: str):
        split_indices = (
            np.random.choice(
                self._dataset_len - self._min_points_per_dataset,
                divisor - 1,
                replace=False,
            )
            + self._min_points_per_dataset
        )
        split_indices.sort()
        x_datasets = np.split(self._model_inputs, split_indices)
        y_datasets = np.split(self._model_targets, split_indices)

        for i in range(len(x_datasets)):
            dataset_name = partial_dataset_name + '_' + str(i)
            save_dataset(
                x_datasets[i],
                y_datasets[i],
                self._initial_datasets_path,
                dataset_name,
            )
            fig, ax = plt.subplots(1, 1)
            plot_dataset(ax, x_datasets[i], y_datasets[i])
            fig.savefig(str(self._initial_datasets_path) + "/" + dataset_name)
            plt.close(fig)

    def create_final_plots(
        self,
        weight,
        bias,
        initial_weight,
        initial_bias,
        global_rmse,
        peripherals: list[UartPeripheral],
        dataset_parent_folder_path: str,
    ):
        # max_x_value = full_dataset.model_inputs.max()
        # min_x_value = full_dataset.model_inputs.min()

        final_results_folder_path = Path(
            dataset_parent_folder_path, self._uuid, "final_datasets"
        )
        os.makedirs(final_results_folder_path, exist_ok=False)
        predictions = weight * self.model_inputs + bias
        initial_predictions = initial_weight * self.model_inputs + initial_bias
        num_plots = len(peripherals) + 1  # We are also plotting the full dataset

        for i in range(num_plots):
            fig, ax = plt.subplots(1, 1)
            if i == (num_plots - 1):  # We are on the last iteration
                plot_name = "final_result_full_dataset"
                subtitle = f"{self.dataset_len} data points, {len(peripherals)} peripherals, RMSE: {global_rmse}"
                inputs = self.model_inputs
                targets = self.model_targets
                ax.plot(
                    self.model_inputs,
                    initial_predictions,
                    "-k",
                    label=f"Initial prediction (y = {initial_weight}x + {initial_bias})",
                    zorder=2
                )
            else:
                plot_name = f"final_result_{peripherals[i].nickname}"
                subtitle = f"{peripherals[i].dataset_len} data points, RMSE: {peripherals[i].final_rmse}"
                inputs = peripherals[i].model_inputs
                targets = peripherals[i].model_targets

            ax = plot_dataset(ax, inputs, targets)
            fig.suptitle(plot_name)
            ax.set_title(subtitle)
            ax.plot(
                self.model_inputs,
                predictions,
                "-r",
                label=f"Final prediction (y = {weight}x + {bias})",
            )
            ax.legend()
            fig.savefig(str(final_results_folder_path) + "/" + plot_name + ".png")
            plt.close(fig)

    def fit_initial_model(self):
        model = LinearRegression()
        model.fit(self._model_inputs, self._model_targets)
        self._initial_model = model

    def validate_parameters(self, weight, bias):
        return calculate_rmse(weight, bias, self.model_inputs, self.model_targets)

    @property
    def model_inputs(self):
        return self._model_inputs

    @model_inputs.setter
    def model_inputs(self, model_inputs: list):
        self._model_inputs = model_inputs

    @property
    def model_targets(self):
        return self._model_targets

    @model_inputs.setter
    def model_inputs(self, model_targets: list):
        self._model_targets = model_targets

    @property
    def dataset_len(self):
        return self._dataset_len

    @dataset_len.setter
    def dataset_len(self, len):
        self._dataset_len = len


def calculate_rmse(
    weight, bias, inputs, targets
):  # TODO: Should only accept numpy array
    predictions = inputs * weight + bias
    rmse = np.sqrt(np.mean(np.square(targets - predictions)))

    return round(rmse, 1)


def plot_dataset(ax: Axes, model_inputs, model_targets) -> Axes:
    ax.scatter(model_inputs, model_targets)
    ax.set_xlabel("X-Values")
    ax.set_ylabel("Y-Values")

    return ax


def get_dataset(dataset_path: str):
    data = np.genfromtxt(dataset_path, delimiter=",", dtype=int, skip_header=True)
    model_inputs = data[0:, 0].tolist()
    model_targets = data[0:, 1].tolist()

    return np.array(model_inputs, model_targets)


def prepare_datasets(
    number_of_peripherals,
    weight,
    bias,
    num_of_datapoints,
    dataset_parent_folder_path: str,
):
    dataset = LinearDataset(
        dataset_len=num_of_datapoints, weight=weight, bias=bias
    )
    dataset.generate_dataset(dataset_parent_folder_path, "full_dataset")
    dataset.divide_and_save_datasets(number_of_peripherals, "partial_dataset")

    return dataset


def save_dataset(model_inputs, model_targets, dataset_folder_path: str, filename: str):
    df = pd.DataFrame({"X": model_inputs, "Y": model_targets})
    save_path = str(Path(dataset_folder_path, filename + ".csv"))
    df.to_csv(save_path, index=False)


def assign_partial_datasets(
    peripherals: list[UartPeripheral], dataset_folder_path: str
):
    file_list = os.listdir(dataset_folder_path)
    file_list = [
        file for file in file_list if file.endswith(".csv") and "partial" in file
    ]

    if len(file_list) != len(peripherals):
        logger().error(
            f"The amount of datasets ({len(file_list)}) and peripherals {len(peripherals)} does not match. Exiting program."
        )
        exit()

    peripheral_index = 0
    for file in file_list:
        data = np.genfromtxt(
            str(dataset_folder_path) + "/" + file,
            delimiter=",",
            dtype=int,
            skip_header=True,
        )
        model_inputs = data[0:, 0]
        model_targets = data[0:, 1]

        peripherals[peripheral_index].model_inputs = model_inputs
        peripherals[peripheral_index].model_targets = model_targets
        peripherals[peripheral_index].dataset_len = len(model_inputs)

        peripheral_index = peripheral_index + 1
