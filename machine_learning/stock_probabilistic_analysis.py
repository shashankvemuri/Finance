import yfinance
from scipy import stats
import numpy as np

# Download historical data for AMD stock
data = yfinance.download('AMD', '2015-09-08', '2020-09-08')

def calculate_prereq(values):
    # Calculate standard deviation and mean
    std = np.std(values)
    mean = np.mean(values)
    return std, mean

def calculate_distribution(mean, std):
    # Create normal distribution with given mean and std
    return stats.norm(mean, std)

def extrapolate(norm, x):
    # Probability density function
    return norm.pdf(x)

def values_to_norm(dicts):
    # Convert lists of values to normal distributions
    for dictionary in dicts:
        for term in dictionary:
            std, mean = calculate_prereq(dictionary[term])
            dictionary[term] = calculate_distribution(mean, std)
    return dicts

def compare_possibilities(dicts, x):
    # Compare normal distributions and return index of higher probability
    probabilities = []
    for dictionary in dicts:
        dict_probs = [extrapolate(dictionary[i], x[i]) for i in range(len(x))]
        probabilities.append(np.prod(dict_probs))
    return probabilities.index(max(probabilities))

# Prepare data for increase and drop scenarios
drop = {}
increase = {}
for day in range(10, len(data) - 1):
    previous_close = data['Close'][day - 10:day]
    ratios = [previous_close[i] / previous_close[i - 1] for i in range(1, len(previous_close))]
    if data['Close'][day + 1] > data['Close'][day]:
        for i, ratio in enumerate(ratios):
            increase[i] = increase.get(i, ()) + (ratio,)
    elif data['Close'][day + 1] < data['Close'][day]:
        for i, ratio in enumerate(ratios):
            drop[i] = drop.get(i, ()) + (ratio,)

# Add new ratios for prediction
new_close = data['Close'][-11:-1]
new_ratios = [new_close[i] / new_close[i - 1] for i in range(1, len(new_close))]
for i, ratio in enumerate(new_ratios):
    increase[i] = increase.get(i, ()) + (ratio,)

# Convert ratio lists to normal distributions and make prediction
dicts = [increase, drop]
dicts = values_to_norm(dicts)
prediction = compare_possibilities(dicts, new_ratios)
print("Predicted Movement: ", "Increase" if prediction == 0 else "Drop")