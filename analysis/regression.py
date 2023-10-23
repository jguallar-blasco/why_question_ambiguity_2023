import numpy as np
from sklearn.linear_model import LinearRegression

# UDS properties
# awareness, change_of_location, change_of_state, change_of_posession
# existed_before, existed_during, existed_after
# instigation, was_used, voliton,
# was_for_benefit, partitive, sentient, dynamic
X = np.array([[, ,],[1],[1],[1],[1],[1],[1],[1],[1],[1],[1],[1],[1],[1]])

# Development examples
# 1) The girl was holding the umbrella
# 2) The man was raising his arm
# #) The lines were painted

y = np.dot(X, np.array([])) + 3

reg = LinearRegression().fit(X, y)
print(reg.score(X, y))
print(reg.coef_)


