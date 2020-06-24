import numpy as np
from sklearn.ensemble import RandomForestClassifier
from hummingbird.ml import convert

# Create some random data for binary classification
from sklearn import datasets
X, y = datasets.make_classification(n_samples=100000, n_features=28)

# Create and train a model (scikit-learn RandomForestClassifier in this case)
skl_model = RandomForestClassifier(n_estimators=1000, max_depth=10)
skl_model.fit(X, y)

# Using Hummingbird to convert the model to PyTorch
model = convert(skl_model, 'pytorch')
print(type(model))

model.to('cuda')