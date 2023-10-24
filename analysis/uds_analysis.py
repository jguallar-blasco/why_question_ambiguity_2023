import argparse
import argparse
from collections import defaultdict
import itertools
import json
import csv 
import pdb
from scipy.optimize import linear_sum_assignment
import sys 
import pathlib 
from csv import DictReader

sorted_data = {}


# Sort data from csv 
with open('3_examples_uds-Batch_2414_results.csv', newline='') as f:
    dict_reader = DictReader(f)
    list_of_dict = list(dict_reader)

    count = 0

    for row in list_of_dict:
        
        #print(row)
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

    
# Calculate agreement 


# 
     

with open("uds_sorted_data.json", "w") as outfile:
    json.dump(sorted_data, outfile)


        