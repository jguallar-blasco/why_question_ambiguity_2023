import numpy as np
import csv
from sklearn import linear_model
import json 
from matplotlib import pyplot as plt
import seaborn as sns
import ast


def report(score):
    if score <= 1.5: 
        print('Purpose\n')
        return 
    if score <= 2.0:
        print('Purpose/Both\n')
        return 
    if score <= 2.5:
        print('Reason/Both\n')
        return 
    else: 
        print('Reason')


p_v_r_scores_by_question_id = {}

# Take in the merged p vs r hit file
with open('merged.csv', newline='') as g:
    dict_reader = csv.DictReader(g)
    list_of_dict = list(dict_reader)

    for row in list_of_dict:

        #print(row)
        image_id = row['Input.imgUrl']
        question_id_ = image_id.split('/')
        question_id_ = question_id_[-1][0:-5]
        question_id_ = question_id_.split('_')
        question_id = question_id_[-1] 

        #print(int(question_id))

        if question_id not in p_v_r_scores_by_question_id:
            p_v_r_scores_by_question_id[question_id] = []      
 
        #print(row['Answer.answer_groups'])
        l = ast.literal_eval(row['Answer.answer_groups'])
        a = len(l[0])
        #print(row['Answer.answer_groups'][0])
        #print(a)
        b = len(l[1])
        #print(b)
        c = len(l[2])
        #print(c)
        if (a >= b) and (a >= c): 
            p_v_r_scores_by_question_id[question_id].append(2) # Both
        elif (b >= a) and (b >= c): 
            p_v_r_scores_by_question_id[question_id].append(1) # Purpose
        else: 
            p_v_r_scores_by_question_id[question_id].append(3) # Reason


#print(p_v_r_scores_by_question_id)
uds_scores_by_question_id = {}
skip_uds = []
# Take in the merged UDS hit file
with open('../data/uds/hit_output/Jimena_45_output_uds.csv', newline='') as f:
    dict_reader = csv.DictReader(f)
    list_of_dict = list(dict_reader)

    count = 0

    for row in list_of_dict:
        
        #print(row)
        question_id = row['Input.sentence_id']
        question_id = question_id[:-3]
        if row['Answer.awareness'] == '' or row['Answer.instigation'] == '' or row['Answer.was_for_benefit'] == '' or row['Answer.was_used'] == '' or row['Answer.sentient'] == '':
            skip_uds.append(question_id)

        

        scores = {
            'awareness': row['Answer.awareness'],
            'change_of_location': row['Answer.change_of_location'],
            'change_of_possesion': row['Answer.change_of_possession'],
            'change_of_state': row['Answer.change_of_state'],
            'dynamic': row['Answer.dynamic'],
            'existed_after': row['Answer.existed_after'],
            'existed_before': row['Answer.existed_before'],
            'existed_during': row['Answer.existed_during'],
            'instigation': row['Answer.instigation'],
            'partitive': row['Answer.partitive'],
            'sentient': row['Answer.sentient'],
            'volition': row['Answer.volition'],
            'was_for_benefit': row['Answer.was_for_benefit'],
            'was_used': row['Answer.was_used']
        }

        uds_scores_by_question_id[question_id] = scores

print(uds_scores_by_question_id)
print(skip_uds)

# p v r data for linear regression model 
p_v_r = []

# UDS data for linear regression model
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

uds_array = []
for_plot = []
for uds_ in uds_scores_by_question_id:

    #print(uds_)
    if uds_ in skip_uds:
        continue

    cur_array = []
    cur_for_plot = ()
    cur_array.append(int(uds_scores_by_question_id[uds_]['awareness']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['change_of_location']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['change_of_state']))
    
    cur_array.append(int(uds_scores_by_question_id[uds_]['existed_before']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['existed_during']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['existed_after']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['instigation']))
    
    cur_array.append(int(uds_scores_by_question_id[uds_]['volition']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['sentient']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['dynamic']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['was_for_benefit']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['partitive']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['change_of_possesion']))
    cur_array.append(int(uds_scores_by_question_id[uds_]['was_used']))

    uds_array.append(cur_array)

    padded_ = str(uds_)
    pad = 12 - len(padded_)
    padded_ = (pad * '0') + padded_ 
    #print(padded_)
    p_v_r.append((np.mean(p_v_r_scores_by_question_id[padded_])))



X = np.array(uds_array)
y = np.array(p_v_r)
#print(X)
#print(y)

print('RUN REGRESSION')
reg = linear_model.LinearRegression()
reg.fit(X, y)

print(reg.score(X, y))
print(reg.coef_)
tested_properties = ['awareness', 'change_of_location', 'change_of_state', 'existed_before', 'existed_during', 'existed_after', 'instigation', 'volition', 'was_for_benefit', 'partitive', 'sentient', 'dynamic', 'change_of_possesion', 'was_used']
for score, tested_properties in zip(reg.coef_, tested_properties):
    print(tested_properties + ": " + str(score))

#print(reg.intercept_)

print('Why is the man in midair?')
score = reg.predict(np.array([[5, 5, 3, 5, 5, 5, 5, 3, 5, 5, 4, 3, 3, 3]]))
report(score)

print('Why are these people on their cell phones?')
score = reg.predict(np.array([[5, 3, 3, 5, 5, 5, 5, 5, 5, 4, 5, 4, 3, 3]]))
report(score)

print('Why are these people carrying umbrellas?')
score = reg.predict(np.array([[5, 4, 3, 5, 5, 5, 5, 5, 5, 4, 5, 4, 3, 3]]))
report(score)

print('Why are they on display')
score = reg.predict(np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4]]))
report(score)

print('Why do they wear head protection?')
score = reg.predict(np.array([[5, 3, 3, 5, 5, 5, 4, 4, 5, 4, 5, 5, 3, 3]]))
report(score)

print('Why do the woman\'s feet seem to be off of the ground?')
score = reg.predict(np.array([[5, 4, 3, 5, 5, 5, 5, 5, 5, 4, 5, 5, 3, 3]]))
report(score)

# Why is the person's arm upraised?
#print(reg.predict(np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])))
# Why is the woman sit on a cushion?
#print(reg.predict(np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])))
# Why does the man have a helmet on his head?
#print(reg.predict(np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])))
# Why are the animal's heads down?

# awareness, change_of_location, change_of_state,  
# existed_before, existed_during, existed_after, instigation 
# volition, was_for_benefit, partitive, sentient, dynamic


