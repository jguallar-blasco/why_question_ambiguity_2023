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

sorted_data = {}

with open('../data/uds/Jimena_3_input_uds.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
        example_id = row['Input.roleset']
        scores = {
            'Answer.awareness': row['Answer.awareness']
        }

        sorted_data[example_id]

        