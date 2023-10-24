import numpy as np
from sklearn.linear_model import LinearRegression
import json 

with open('uds_sorted_data.json', 'r') as openfile:
    uds_data = json.load(openfile)

# UDS properties
awareness = []
change_of_location = []
change_of_state = []
change_of_posession = []
existed_before = []
existed_during = []
existed_after = []
instigation = []
was_used = []
volition = []
was_for_benefit = []
partitive = []
sentient = []
dynamic = []

for example in uds_data:
    print(uds_data[example])
    awareness.append(int(uds_data[example]['awareness']))
    change_of_location.append(int(uds_data[example]['change_of_location']))
    change_of_state.append(int(uds_data[example]['change_of_state']))
    change_of_posession.append(int(uds_data[example]['change_of_possesion']))
    existed_before.append(int(uds_data[example]['existed_before']))
    existed_during.append(int(uds_data[example]['existed_during']))
    existed_after.append(int(uds_data[example]['existed_after']))
    instigation.append(int(uds_data[example]['instigation']))
    was_used.append(int(uds_data[example]['was_used']))
    volition.append(int(uds_data[example]['volition']))
    was_for_benefit.append(int(uds_data[example]['was_for_benefit']))
    partitive.append(int(uds_data[example]['partitive']))
    sentient.append(int(uds_data[example]['sentient']))
    dynamic.append(int(uds_data[example]['dynamic']))

X = np.array([awareness, change_of_location, change_of_state, change_of_posession, existed_before, existed_during, existed_after, instigation, was_used, volition, was_for_benefit, partitive, sentient, dynamic])
print(X)
# Development examples
# 1) The girl was holding the umbrella
# 2) The man was raising his arm
# #) The lines were painted

y = np.dot(X, np.array([1.0,0.0,1.0])) + 3

reg = LinearRegression().fit(X, y)
print(reg.score(X, y))
print(reg.coef_)


