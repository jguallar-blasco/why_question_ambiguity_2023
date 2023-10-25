import numpy as np
from sklearn.linear_model import LinearRegression
import json 


p_v_r_scores_by_question_id = {}

# Take in the merged p vs r hit file
with open('merged.csv', newline='') as g:
    dict_reader = DictReader(f)
    list_of_dict = list(dic_reader)

    for row in list_of_dict:

        dic_ = rows_by_hit_id[hit_id]
        #print(dic_)
        image_id = dic_[0]['Input.imgUrl']
        question_id_ = image_id.split('/')
        question_id_ = question_id_[-1][0:-5]
        question_id_ = question_id_.split('_')
        question_id = question_id_[-1] 

        p_v_r_scores_by_question_id[question_id] = []      

               
               
               
               
               
               
               
                a = len(ann['Answer.answer_groups'][0])
                b = len(ann['Answer.answer_groups'][1])
                c = len(ann['Answer.answer_groups'][2])
                if (a >= b) and (a >= c): 
                    sorted_data[question_id].append(2) # Both
                elif (b >= a) and (b >= c): 
                    sorted_data[question_id].append(1) # Purpose
                else: 
                    sorted_data[question_id].append(3) # Reason


uds_score_by_question_id = []

# Take in the merged UDS hit file
with open('3_examples_uds-Batch_2414_results.csv', newline='') as f:
    dict_reader = DictReader(f)
    list_of_dict = list(dict_reader)

    count = 0

    for row in list_of_dict:
        
        #print(row)
        question_id = row['sentence_id']
        example_id = row['Input.roleset']
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

        sorted_data[count] = scores
        count += 1

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


