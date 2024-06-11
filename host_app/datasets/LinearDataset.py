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

script_path = str(Path(__file__).resolve().parent)

# TODO: create validation set
# TODO: Rename X- and Y-Values to inputs and targets


class LinearDataset:
    def __init__(
        self,
        num_points: int,
        weight,
        bias,
        value_range=50,
        min_points_per_dataset=100,
        output_filename: str = "linear_dataset",
    ):
        self._num_points = num_points
        self._weight = weight
        self._bias = bias
        self._value_range = value_range
        self._min_points_per_dataset = min_points_per_dataset
        self._x_values = None
        self._y_values = None
        self._initial_model = None
        self._uuid = str(uuid4())
        self._path = Path(script_path, "datasets", self._uuid)

        os.makedirs(Path(self._path, "initial_datasets"))
        os.makedirs(Path(self._path, "final_results"))
        self.generate_dataset()

    def generate_dataset(self):
        self._x_values = np.random.randint(low=-100, high=100, size=self._num_points)
        self._y_values = (
            self._weight * self._x_values
            + self._bias
            + np.random.randint(
                low=-(self._value_range), high=self._value_range, size=self._num_points
            )
        )

        save_path = Path(self._path, "initial_datasets")
        dataset_name = "full_dataset"
        save_dataset(self._x_values, self._y_values, save_path, dataset_name)
        fig, ax = plt.subplots(1, 1)
        plot = plot_dataset(ax, self._x_values, self._y_values, dataset_name)
        fig.savefig(str(save_path)+ '/' + dataset_name + ".png")
        
    def divide_and_save_datasets(self, divisor, filename="partial_dataset"):
        split_indices = (
            np.random.choice(
                self._num_points - self._min_points_per_dataset,
                divisor - 1,
                replace=False,
            )
            + self._min_points_per_dataset
        )
        split_indices.sort()
        x_datasets = np.split(self._x_values, split_indices)
        y_datasets = np.split(self._y_values, split_indices)

        # old_files = os.listdir(script_path)
        # for file in old_files:
        #     if file.endswith('.csv') or file.endswith('.png'):
        #         os.remove(script_path + '/' + file)

        save_path = Path(self._path, "initial_datasets")
        for i in range(len(x_datasets)):
            dataset_name = f"partial_dataset_{i}"
            save_dataset(x_datasets[i], y_datasets[i], save_path, dataset_name)
            fig, ax = plt.subplots(1, 1)
            plot_dataset(ax, x_datasets[i], y_datasets[i], dataset_name)
            fig.savefig(str(save_path) + '/' + dataset_name + ".png")

    def assign_partial_datasets(self, peripherals: list[UartPeripheral]):
        peripheral_index = 0
        dataset_path = Path(self._path, "initial_datasets")
        for file in os.listdir(dataset_path):
            if file.endswith(".csv") and "partial" in file:
                data = np.genfromtxt(
                    str(dataset_path) + "/" + file, delimiter=",", dtype=int, skip_header=True
                )
                x_values = data[0:, 0].tolist()
                y_values = data[0:, 1].tolist()

                peripherals[peripheral_index].x_values = x_values
                peripherals[peripheral_index].y_values = y_values

                peripheral_index = peripheral_index + 1
                
    def fit_initial_model(self):
        model = LinearRegression()
        model.fit(self._x_values, self._y_values)
        self._initial_model = model

    def validate_parameters(self, weight, bias):
        return calculate_rmse(weight, bias, self.x_values, self.y_values)

    @property
    def x_values(self):
        return self._x_values

    @x_values.setter
    def x_values(self, x_values: list):
        self._x_values = x_values

    @property
    def y_values(self):
        return self._y_values

    @x_values.setter
    def x_values(self, y_values: list):
        self._y_values = y_values


def calculate_rmse(
    weight, bias, inputs, targets
):  # TODO: Should only accept numpy array
    predictions = inputs * weight + bias
    rmse = np.sqrt(np.mean(np.square(targets - predictions)))

    return round(rmse, 2)


def create_final_plots(
    weight, bias, peripherals: list[UartPeripheral], full_dataset: LinearDataset
):
    save_path = Path(full_dataset._path, "final_results")  # FIXME: Using private attribute
    # max_x_value = full_dataset.x_values.max()
    # min_x_value = full_dataset.x_values.min()
    predictions = weight * full_dataset.x_values + bias

    num_plots = len(peripherals)
    # TODO: Add RMSE to plots
    # TODO: Add titles
    for i in range(num_plots):
        plot_name = f"final_result_{peripherals[i].nickname}"
        fig, ax = plt.subplots(1, 1)
        ax = plot_dataset(ax, peripherals[i].x_values, peripherals[i].y_values, plot_name)
        ax.plot(full_dataset.x_values, predictions, "-r", label=f"Prediction ({weight}x + {bias})")
        fig.savefig(str(save_path) + '/' + plot_name + ".png")

def plot_dataset(ax: Axes, x_values, y_values, dataset_name: str) -> Axes:
    ax.scatter(x_values, y_values)
    ax.set_title(f"{dataset_name}, {len(x_values)} data points.")
    ax.set_xlabel("X-Values")
    ax.set_ylabel("Y-Values")
    
    return ax



def get_total_dataset():
    for file in os.listdir(script_path + "/" + "datasets"):
        if "total_linear_dataset" in file:
            file_path = script_path + "/" + "datasets" + "/" + file
            data = np.genfromtxt(file_path, delimiter=",", dtype=int, skip_header=True)
            x_values = data[0:, 0].tolist()
            y_values = data[0:, 1].tolist()


def prepare_datasets(number_of_peripherals, weight, bias, num_of_datapoints):
    dataset = LinearDataset(num_points=num_of_datapoints, weight=weight, bias=bias)
    dataset.divide_and_save_datasets(number_of_peripherals)

    return dataset


def save_dataset(x_values, y_values, output_path: Path, filename: str):
    df = pd.DataFrame({"X": x_values, "Y": y_values})
    save_path = str(Path(output_path, filename + ".csv"))
    df.to_csv(save_path, index=False)
