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
from sklearn.metrics import cohen_kappa_score
import krippendorff

"""
Analyze "purpose" vs "reason" HIT results.
Get agreement. 
"""

sorted_data = {}

def agreement_score(sorted_data):
    total_score = 0 
    total_k_score = 0
    total_examples = 0 
    for example in sorted_data:
        #print('EXAMPLE')
        total_examples += 1

        k = []
        for user in sorted_data[example]:
            k.append(sorted_data[example][user])

        scores = 0
        k_scores = 0
        count = 0 
        for user_1 in sorted_data[example]:
            #print(user_1)
            count += 1
            for user_2 in sorted_data[example]:
                #print(user_2)
                if user_1 == user_2:
                    continue
                else:
                    score = cohen_kappa_score(sorted_data[example][user_1], sorted_data[example][user_2])
                    #k = []
                    #k.append(sorted_data[example][user_1])
                    #k.append(sorted_data[example][user_2])
                    k_score = krippendorff.alpha(k, level_of_measurement='ordinal')
                    #print(k_score)
                    if score < 0.10:
                        print(example)
                        #print('-----------')
                    scores += score
                    k_scores += k_score

        _score = scores/count
        _k_score = k_scores/count
        total_score += _score
        total_k_score += _k_score
    return total_score/total_examples, total_k_score/total_examples


def sort(data):
    for row in data:

        question_id = row['HITId']
        username = row['WorkerId']
        

        # Without 'A17TKHT8FEVH0R', 0.21, 0.34
        # Without 'A28HB7240OFGEW', 0.06, 0.22
        # Without 'ACKG8OU1KHKO2', 0.26, 0.48
        # Without 'A3UV55HC87DO9C', 0.23, 0.41
        # Without 'AKQAI78JTXXC9', 0.32, 0.62


        if row['Answer.awareness'] == '' or row['Answer.instigation'] == '' or row['Answer.was_for_benefit'] == '' or row['Answer.was_used'] == '' or row['Answer.sentient'] == '':
            continue

        scores_for_example = []
            
        scores_for_example.append(int(row['Answer.awareness']))
        scores_for_example.append(int(row['Answer.change_of_location']))
        scores_for_example.append(int(row['Answer.change_of_possession']))
        scores_for_example.append(int(row['Answer.change_of_state']))
        scores_for_example.append(int(row['Answer.can_be_dynamic']))
        scores_for_example.append(int(row['Answer.is_dynamic']))
        scores_for_example.append(int(row['Answer.existed_after']))
        scores_for_example.append(int(row['Answer.existed_before']))
        scores_for_example.append(int(row['Answer.existed_during']))
        scores_for_example.append(int(row['Answer.instigation']))
        scores_for_example.append(int(row['Answer.partitive']))
        scores_for_example.append(int(row['Answer.sentient']))
        scores_for_example.append(int(row['Answer.volition']))
        scores_for_example.append(int(row['Answer.was_for_benefit']))
        scores_for_example.append(int(row['Answer.was_used']))
        
        if question_id not in sorted_data:
            sorted_data[question_id] = {}

        sorted_data[question_id][username] = scores_for_example

    
    # Send to json
    #write_csv(to_write, args.out_path)

def main(args):
    data = []
    gold_data = []

    if args.gold_csv != None:
        with open(args.gold_csv) as read_obj:
            csv_reader = csv.DictReader(read_obj)
            for row in csv_reader:
                gold_data.append(row)
        sort(gold_data)

    
    with open(args.input_csv) as read_obj:
        csv_reader = csv.DictReader(read_obj)
        for row in csv_reader:
            data.append(row)
    sort(data)

    cohens_kappa, k_score = agreement_score(sorted_data)
    print(cohens_kappa)
    print(k_score)
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=str, dest='input_csv', required=True)
    parser.add_argument("--gold-csv", type=str, dest='gold_csv', required=False)
    parser.add_argument("--out-path", type=str, dest='out_path', required=False)
    args = parser.parse_args()

    main(args)