# Import dependencies
import yfinance
from scipy import stats
import numpy as np

# Download historical data for AMD stock from Yahoo Finance API
data = yfinance.download('AMD','2015-09-08','2020-09-08')

def calculate_prereq(values):
    # Calculate standard deviation and mean for a given list of values
    std = np.std(values)
    mean = np.mean(values)
    return std,mean

def calculate_distribution(mean,std):
    # Create a normal distribution object with a given mean and standard deviation
    norm = stats.norm(mean, std)
    return norm

def extrapolate(norm,x):
    # Calculate the probability density function for a given normal distribution object and value
    return norm.pdf(x)

def values_to_norm(dicts):
    # Convert lists of values in a list of dictionaries to normal distribution objects
    for dictionary in dicts:
        for term in dictionary:
            std,mean = calculate_prereq(dictionary[term])
            norm = calculate_distribution(mean,std)
            dictionary[term] = norm
    return dicts

def compare_possibilities(dicts,x):
    # Compare two sets of normal distribution objects for a given list of values and return the index of the set with higher probability
    probabilities = []
    for dictionary in dicts:
        dict_probs = []
        for i in range(len(x)):
            value = x[i]
            dict_probs.append(extrapolate(dictionary[i],value))
        probabilities.append(np.prod(dict_probs))
    return probabilities.index(max(probabilities))

# Calculate daily stock ratios and store them in dictionaries based on whether the stock price increased or decreased
drop = {}
increase = {}
for day in range(10,len(data)-1):
    previous_close = data['Close'][day-10:day]
    ratios = []
    for i in range(1,len(previous_close)):
        ratios.append(previous_close[i]/previous_close[i-1])
    if data['Close'][day+1] > data['Close'][day]:
        for i in range(len(ratios)):
            if i in increase:
                increase[i] += (ratios[i],)
            else:
                increase[i] = ()
    elif data['Close'][day+1] < data['Close'][day]:
        for i in range(len(ratios)):
            if i in drop:
                drop[i] += (ratios[i],)
            else:
                drop[i] = ()

# Calculate new daily ratios and store them in the corresponding dictionary
new_close = data['Close'][-11:-1]
ratios = []
for i in range(1,len(new_close)):
    ratios.append(new_close[i]/new_close[i-1])
for i in range(len(ratios)):
    if i in increase:
        increase[i] += (ratios[i],)
    else:
        increase[i] = ()

# Convert lists of ratios in both dictionaries to normal distribution objects and compare the two dictionaries to predict future stock price movements
X = ratios
dicts = [increase,drop]
dicts = values_to_norm(dicts)
print(compare_possibilities(dicts,X))