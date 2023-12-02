import argparse
import argparse
from collections import defaultdict
import itertools
import json
import csv 
from csv import reader
import pdb
from scipy.optimize import linear_sum_assignment
import ast
import sklearn.metrix.cohen_kappa_score 

"""
Analyze "purpose" vs "reason" HIT results.
Get agreement. 
"""

sorted_data = {}

def agreement_score(sorted_data):
    total_score = 0 
    total_examples = 0 
    for example in sorted_data:
        total_example += 1

        scores = 0
        count = 0 
        for user_1 in sorted_data[example]:
            count += 1
            for user_2 in sorted_data[example]:
                if user_1 == user_2:
                    continue
                else:
                    score = cohen_kappa_score(sorted_data[example][user_1], sorted_data[example][user_2])
                    scores += score

        example_score = score/count
        total_score += example_score
    return total_score/total_examples


def sort(data):
    for line in data:

        #print(row)
        question_id = row['Input.sentence_id']
        question_id = question_id[:-3]

        username = row['Turkle.Username']

        if row['Answer.awareness'] == '' or row['Answer.instigation'] == '' or row['Answer.was_for_benefit'] == '' or row['Answer.was_used'] == '' or row['Answer.sentient'] == '':
            skip_uds.append(question_id)

        

        scores_for_example = []
            
        scores_for_example.append(row['Answer.awareness'])
        scores_for_example.append(row['Answer.change_of_location'])
        scores_for_example.append(row['Answer.change_of_possession'])
        scores_for_example.append(row['Answer.change_of_state'])
        scores_for_example.append(row['Answer.dynamic'])
        scores_for_example.append(row['Answer.existed_after'])
        scores_for_example.append(row['Answer.existed_before'])
        scores_for_example.append(row['Answer.existed_during'])
        scores_for_example.append(row['Answer.instigation'])
        scores_for_example.append(row['Answer.partitive'])
        scores_for_example.append(row['Answer.sentient'])
        scores_for_example.append(row['Answer.volition'])
        scores_for_example.append(row['Answer.was_for_benefit'])
        scores_for_example.append(rowrow['Answer.was_used'])
        
        if question_id not in sorted_data:
            sorted_data[question_id] = {}

        sorted_data[question_id][username] = scores_for_example

    
    # Send to json
    #write_csv(to_write, args.out_path)

def main(args):
    data = []

    
    with open(args.input_csv) as read_obj:
        csv_reader = csv.DictReader(read_obj)
        for row in csv_reader:
            data.append(row)
    sort(data)

    cohens_kappa = agreement_score(sorted_data)
    print(cohens_kappa)
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=str, dest='input_csv', required=True)
    parser.add_argument("--out-path", type=str, dest='out_path', required=False)
    args = parser.parse_args()

    main(args)