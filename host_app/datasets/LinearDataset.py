import numpy as np
import pandas as pd
import random
from pathlib import Path
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import os
from UartPeripheral import UartPeripheral

script_path = str(Path(__file__).resolve().parent)

# TODO: create validation set

class LinearDataset():
    def __init__(self, num_points: int, slope, intercept, value_range = 50, min_points_per_dataset=100, output_filename: str = 'linear_dataset'):
        self._num_points = num_points
        self._slope = slope
        self._intercept = intercept
        self._value_range = value_range
        self._min_points_per_dataset = min_points_per_dataset
        self._x_values = None
        self._y_values = None
        self._initial_model = None
        self.generate_dataset()
        
    def generate_dataset(self):
        self._x_values = np.random.randint(low=-100, high=100, size=self._num_points)
        self._y_values = self._slope * self._x_values + self._intercept + np.random.randint(low=-(self._value_range), high=self._value_range, size=self._num_points)

        df = pd.DataFrame({'X': self._x_values, 'Y': self._y_values})
        df.to_csv(script_path + '/' + "full_dataset" + ".csv", index=False)

        plot_dataset(self._x_values, self._y_values, 'full_dataset')
        
        
    
    def divide_and_save_datasets(self, divisor, filename = 'partial_dataset'):
        split_indices = np.random.choice(self._num_points - self._min_points_per_dataset, divisor - 1, replace=False) + self._min_points_per_dataset
        split_indices.sort()
        x_datasets = np.split(self._x_values, split_indices)
        y_datasets = np.split(self._y_values, split_indices)
        
        old_files = os.listdir(script_path)
        for file in old_files:
            if file.endswith('.csv') or file.endswith('.png'):
                os.remove(script_path + '/' + file)
        
        for i in range(len(x_datasets)):
            df = pd.DataFrame({'X': x_datasets[i], 'Y': y_datasets[i]})
            df.to_csv(script_path + '/' + filename + str(i) + ".csv", index=False)
            plot_dataset(x_datasets[i], y_datasets[i], filename + str(i))
        
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
        
def calculate_rmse(weight, bias, inputs, targets):  # TODO: Should only accept numpy array
    predictions = inputs * weight + bias
    rmse = np.sqrt(np.mean(np.square(targets - predictions)))
    
    return rmse
    
def create_final_plots(weight, bias, peripherals: list[UartPeripheral], full_dataset: LinearDataset):
    # max_x_value = full_dataset.x_values.max()
    # min_x_value = full_dataset.x_values.min()
    predictions = weight * full_dataset.x_values + bias
    
    num_subplots = len(peripherals)
    fig, axs = plt.subplots(num_subplots + 1, 1)
    # TODO: Add RMSE to plots
    # TODO: Add titles
    axs[0].scatter(x=full_dataset.x_values, y=full_dataset.y_values)
    axs[0].plot(full_dataset.x_values, predictions, '-r', label=f"Prediction ({weight}x + {bias})")
    for i, peripheral in enumerate(peripherals):
        axs[i + 1].scatter(x=peripheral.x_values, y=peripheral.y_values)
        axs[i + 1].plot(full_dataset.x_values, predictions, '-r', label=f"Prediction ({weight}x + {bias})")
        
        
    fig.savefig("final_plots.png")
          
    
def plot_dataset(x_values, y_values, filename):
    plt.scatter(x_values, y_values)
    plt.title(f"{filename}, {len(x_values)} data points.")
    plt.xlabel("X-Values")
    plt.ylabel("Y-Values")
    plt.tight_layout
    plt.savefig(script_path + '/' + filename + '.png')
    #plt.cla()
    
def assign_partial_datasets(peripherals: list[UartPeripheral]):
    peripheral_index = 0
    for file in os.listdir(script_path):
        if file.endswith('.csv') and "partial" in file:
            data = np.genfromtxt(script_path + '/' + file, delimiter=',',dtype=int, skip_header=True)
            x_values = data[0:, 0].tolist() 
            y_values = data[0:, 1].tolist()
            
            peripherals[peripheral_index].x_values = x_values
            peripherals[peripheral_index].y_values = y_values
            
            peripheral_index = peripheral_index + 1