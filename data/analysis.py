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

"""
Analyze "purpose" vs "reason" HIT results. 
Send data to json file format
"""

def get_line(line):
    global only_reason 
    global only_purpose
    global more_reason 
    global more_purpose
    global both_readings

    line_dict = {"imgUrl": None,
                "questionStr": None, 
                "answerGroups": None, # From annotator
                "answerQuestions": None, # From annotator
                "question_id": None}


    #line_dict['question_id'] = line['Input.question_id'] # question id
    line_dict['imgUrl'] = line['Input.imgUrl'] # image url
    line_dict['questionStr'] = line['Input.questionStr'] # question string
    # To do: 
    line_dict['answerGroups'] = line['Answer.answer_groups'] # annotator answer groups
    answer_groups = ast.literal_eval(line['Answer.answer_groups'])
    #print(answer_groups)

    # Analyze answer groups 
    both = answer_groups[0]
    #print(both)
    purpose = answer_groups[1]
    #print(purpose)
    reason = answer_groups[2]
    #print(reason)

    # Has both
    if len(purpose) > 0 and len(reason) > 0:
        both_readings += 1
    # Only reason
    if len(purpose) == 0 and len(reason) > 0:
        only_reason = only_reason + 1
    # Only purpose
    if len(reason) == 0 and len(purpose) > 0:
        only_reason = only_reason + 1
    # More reason
    if len(reason) > len(purpose) == 0 and len(reason) > len(both):
        more_reason += 1
    # More purpose
    if len(purpose) > len(reason) == 0 and len(purpose) > len(both):
        more_purpose += 1
    line_dict['answerQuestions'] = line['Answer.answer_questions'] # annotator group questions


    return line_dict 

def write_csv(to_write, out_path):
    with open(out_path, "w") as f1:
        writer = csv.DictWriter(f1, fieldnames=['imgUrl', 'questionStr', 'answerGroups', 'answerQuestions', 'question_id'])
        writer.writeheader()
        for line in to_write:
            writer.writerow(line)

def sort(data):
    sorted_data = []
    to_delete = []
    to_skip = []
    for line in data:
        if line["Answer.skip_reason"] == '"delete"':
            to_delete.append(line)
        else:
            if line["Answer.is_skip"] == "true":
                to_skip.append(line)
            sorted_data.append(line)
    to_write = [get_line(l) for l in sorted_data]
    print(f"Both readings: {both_readings}")
    print(f"Only reason: {only_reason}")
    print(f"Only purpose: {only_purpose}")
    print(f"More reason: {more_reason}")
    print(f"More purpose: {more_purpose}")
    print(f"Examples deleted: {len(to_delete)}")
    print(f"Examples to go over: {len(to_skip)}")
    # Send to json
    #write_csv(to_write, args.out_path)

def main(args):
    data = []

    

    with open(args.input_csv) as read_obj:
        csv_reader = csv.DictReader(read_obj)
        for row in csv_reader:
            data.append(row)
    sort(data)

global only_reason 
global only_purpose
global more_reason 
global more_purpose
global both_readings
only_reason = 0
only_purpose = 0 
more_reason = 0
more_purpose = 0 
both_readings = 0
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=str, dest='input_csv', required=True)
    parser.add_argument("--out-path", type=str, dest='out_path', required=False)
    args = parser.parse_args()

    main(args)