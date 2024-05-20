import numpy as np
import pandas as pd
import random
from pathlib import Path
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression

script_path = str(Path(__file__).resolve().parent)

# TODO: create validation set

class LinearDataset():
    def __init__(self, num_points: int, slope, intercept, value_range = 50, min_points_per_dataset=100, output_filename: str = 'dataset'):
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
        self.plot_dataset(self._x_values, self._y_values, 'full_dataset')
        
    
    def divide_and_save_datasets(self, divisor, filename = 'linear_dataset'):
        split_indices = np.random.choice(self._num_points - self._min_points_per_dataset, divisor - 1, replace=False) + self._min_points_per_dataset
        split_indices.sort()
        x_datasets = np.split(self._x_values, split_indices)
        y_datasets = np.split(self._y_values, split_indices)
        
        for i in range(len(x_datasets)):
            df = pd.DataFrame({'X': x_datasets[i], 'Y': y_datasets[i]})
            df.to_csv(script_path + '/' + filename + str(i) + ".csv")
            self.plot_dataset(x_datasets[i], y_datasets[i], filename + str(i))
            
    def plot_dataset(self, x_values, y_values, filename):
        plt.scatter(x_values, y_values)
        plt.title(f"{filename}, {len(x_values)} data points.")
        plt.xlabel("X-Values")
        plt.ylabel("Y-Values")
        plt.tight_layout
        plt.savefig(script_path + '/' + filename + '.png')
        plt.cla()
        
    def fit_initial_model(self):
        model = LinearRegression()
        model.fit(self._x_values, self._y_values)
        self._initial_model = model
        
    def validate_parameters(self, weight, intercept):
        predictions = self._x_values * weight + intercept
        mse = np.sqrt(np.mean(np.square(self._x_values - predictions)))
        
        return mse