import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Define parameters for the linear equation y = ax + b
a = 2  # slope
b = 3  # y-intercept

# Generate random values for the independent variable (x)
num_samples = 500
x_values = np.random.randint(low=0, high=100, size=num_samples, )

# Calculate the corresponding dependent variable (y) based on the linear equation y = ax + b
y_values = a * x_values + b

# Optionally, introduce some noise to the dependent variable
noise = np.random.normal(loc=0, scale=15, size=num_samples)
y_values_with_noise = y_values + noise

# Split the dataset into training and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_values, y_values_with_noise, test_size=0.2, random_state=42)

# Split the training set into multiple subsets
num_datasets = 2
x_train_subsets = []
y_train_subsets = []

for i in range(num_datasets):
    x_subset, _, y_subset, _ = train_test_split(x_train, y_train, test_size=1/num_datasets, random_state=i)
    x_train_subsets.append(x_subset)
    y_train_subsets.append(y_subset)
    
    # Write subset data to a .txt file
    with open(f'dataset_subset_{i}.txt', 'w') as file:
        file.write("x:\n")
        for x in x_subset:
            file.write(f'{x},')
        file.write("\ny:\n")
        for y in y_subset:
            file.write(f'{int(y)},')
            
# Plot the dataset
plt.scatter(x_subset, y_subset, label='Data with Noise')
plt.plot(x_values, y_values, color='red', label='True Line (y = {}x + {})'.format(a, b))
plt.xlabel('x')
plt.ylabel('y')
plt.title('2D Linear Regression Dataset')
plt.legend()
plt.grid(True)
plt.savefig('total_training_set.png')
