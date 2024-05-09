#!/Users/maanders1/miniconda3/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generate x values
x = np.random.uniform(0, 100, 100)

# Generate noise around the line y = 0.5x + 3
noise = np.random.normal(scale=2, size=100)  # Adjust the scale parameter as needed

# Generate y values around the line y = 0.5x + 3 with added noise
y = 0.5 * x + 3 + noise

for i in range(100):
    print(f"{int(x[i])},", end='')
print("\n\n")
for i in range(100):
    print(f"{int(y[i])},", end='')
        
data = {'x': x, 'y': y}
df = pd.DataFrame(data=data)

ax1 = df.plot.scatter(x='x', y='y')
#plt.show()
# Print the first 10 data points for demonstration

