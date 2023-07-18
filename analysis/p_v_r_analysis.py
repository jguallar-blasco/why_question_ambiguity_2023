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
path_to_file = str(pathlib.Path(__file__).resolve().parent.parent.parent.joinpath("analysis") )
print(path_to_file)
sys.path.insert(0, path_to_file)
print(sys.path)
#from string_metrics import BleuSimilarityScore, BertSimilarityScore, BartSimilarityScore

import numpy as np

def process_row(row):
    columns_to_json = ['Answer.answer_groups', "Answer.answer_questions", "Input.answerGroups", "Input.answerQuestions"]
    for col in columns_to_json:
        # print(row[col])
        row[col] = json.loads(row[col])
    did_skip = True if row['Answer.is_skip'] == 'TRUE' else False
    
    row['Answer.is_skip'] = did_skip
    if did_skip:
        print(row['Input.questionStr'])
    return row

def process_pilot_row(row, as_json=False): 
    def infer_skip(answer_question, input_answer_question):
        # infer whether an annotator skipped, since some have None and some False 
        # if the lengths are different they must have edited 
        if len(answer_question) != len(input_answer_question):
            return False
        # if any question doesn't match the input, they edited 
        for ans, inp in zip(answer_question, input_answer_question):
            if ans != inp:
                return False
        return True

    columns_to_json = ['Answer.answer_groups_list', "Answer.answer_questions_list", "Input.answerGroupsList", 
                        "Input.answerQuestionsList", "Input.questionStrList", "Answer.is_skip_list"]
    rows = []
    n_rows = len(json.loads(row['Answer.is_skip_list']))
    print(f"n_rows: {n_rows}")
    # convert to json 
    for col in columns_to_json:
        row[col] = json.loads(row[col])

    # pdb.set_trace()
    for i in range(n_rows):
        row_copy = {}
        row_copy['WorkerId'] = row['WorkerId']
        row_copy['Answer.answer_groups'] = row['Answer.answer_groups_list'][i]
        row_copy['Answer.answer_questions'] = row['Answer.answer_questions_list'][i]
        row_copy['Answer.is_skip'] = infer_skip(row['Answer.answer_questions_list'][i], row['Input.answerQuestionsList'][i])
        row_copy['Input.answerGroups'] = row['Input.answerGroupsList'][i]
        row_copy['Input.questionStr'] = row['Input.questionStrList'][i]
        row_copy['Input.answerQuestions'] = row['Input.answerQuestionsList'][i]
        if as_json:
            row_copy = {k:json.dumps(v) for k,v in row_copy.items()}
        row_copy['HITId'] = f"{row['HITId']}_{i}"
        row_copy['Turkle.Username'] = row['WorkerId']
        rows.append(row_copy)
    return rows

def process_csv(filename, pilot=False, anns=None):
    to_ret = []
    with open(filename) as f1:
        reader = csv.DictReader(f1)
        for row in reader:
            if not pilot:
                to_ret.append(process_row(row)) 
            else:
                print(row['WorkerId'])
                data = process_pilot_row(row)
                print(len(data)) 
                to_ret += data
    if anns:
        to_ret = [x for x in to_ret if x['Turkle.Username'] in anns]
    return to_ret 

def get_groups(rows, enforce_num_anns, num_anns, mturk): 
    """
    Take raw csv rows, and return a dict of lists, with each list containt rows grouped 
    by HIT ID

    Parameters
    ----------
    - rows: List
        A list of csv rows 
    - enforce_num_anns: bool
        if true, only keep HITs with num_anns annotations
    - num_anns: int
        number of annotators participating 
    """
    key="HITId"
    rows_by_hit_id = defaultdict(list)
    for r in rows:
        rows_by_hit_id[r[key]].append(r) 
    if enforce_num_anns: 
        rows_by_hit_id = {k: v for k,v in rows_by_hit_id.items() if len(v) == num_anns}
    return rows_by_hit_id

def annotator_report(groups, mturk): 
    annotator_lines = defaultdict(list)
    if mturk:
        user_key = "WorkerId"
    else:
        user_key = "Turkle.Username"
    for hit_id, rows in groups.items():
        for row in rows:
            ann = row[user_key]
            annotator_lines[ann].append(row)

    ann_report = {}
    for ann, rows in annotator_lines.items():
        n_completed = len(rows)
        n_skipped = sum([1 if row['Answer.is_skip'] else 0 for row in rows])
        ann_report[ann] = (n_completed, n_skipped)

    for ann, (completed, skipped) in ann_report.items():
        print(f"Annotator: {ann}, skipped: {skipped}, completed: {completed}")


def skip_agreement(rows_by_hit_id, interact=False, mturk=False): # TO DO (TEST)
    """
    Compute the percentage of time all annotators agree 
    on whether to skip, and the percentage of times 
    each annotator agrees with each other annotator on
    skipping an example

    Parameters
    ----------
    - rows_by_hit_id: Dict[str, List]
        dict of csv rows with HITId as keys 
    """
    n_agree = 0
    total = 0
    agree = {}
    disagree = {}
    # correct, total 
    if mturk:
        user_key = "WorkerId"
    else:
        user_key = "Turkle.Username"

    per_annotator_agreement = defaultdict(lambda: {"correct": 0, "total": 0, "correct_skipped": 0, "correct_unskipped": 0})
    for hit_id, ex_rows in rows_by_hit_id.items(): 
        skips = [ann['Answer.is_skip'] for ann in ex_rows]
        if all(skips) or not any(skips):
            n_agree +=1 
            agree[hit_id] = ex_rows
        else:
            disagree[hit_id] = ex_rows
        for row1 in ex_rows:
            ann1 = row1[user_key]
            for row2 in ex_rows:
                ann2 = row2[user_key]
                key = f"{ann1}_{ann2}"
                if ann1 == ann2: 
                    continue
                else:
                    if row1['Answer.is_skip'] == row2['Answer.is_skip']: 
                        per_annotator_agreement[key]['correct'] += 1
                        if row1['Answer.is_skip']: 
                            per_annotator_agreement[key]['correct_skipped'] += 1
                        else:
                            per_annotator_agreement[key]['correct_unskipped'] += 1
                        if interact and not row1['Answer.is_skip']:
                            pprint([row1, row2], ['Input.imgUrl', 'Input.questionStr', user_key, 'Answer.is_skip'])
                            pdb.set_trace() 

                    per_annotator_agreement[key]['total'] += 1


        total += 1
    for k, v in per_annotator_agreement.items():
        per_annotator_agreement[k] = (safe_divide(v['correct'], v['total']), v)
    per_annotator_agreement_to_ret = {}
    for k,v in per_annotator_agreement.items():
        reverse_k = "_".join(k.split("_")[::-1])
        if k in per_annotator_agreement_to_ret.keys() or reverse_k in per_annotator_agreement_to_ret.keys():
            continue
        per_annotator_agreement_to_ret[k] = v
    
    return agree, disagree, n_agree/total, per_annotator_agreement_to_ret

def safe_divide(num, denom): 
    try: 
        return num/denom
    except ZeroDivisionError:
        return 0


def get_string_metrics(str_list1, str_list2, assignment, scorers):
    aligned_strs = []
    row, col = assignment
    for i, row_idx in enumerate(row):
        a_str = str_list1[i]
        b_str = str_list2[row_idx]
        if row[0] != 0:
            print(a_str)
            print(b_str)
        aligned_strs.append((a_str, b_str))

    metrics = defaultdict(list)
    for a, b in aligned_strs:
        for name, scorer in scorers:
            try:
                score = scorer.get_similarity(a,b)
            except KeyError:
                continue
                # pdb.set_trace()
            metrics[name].append(score)
    # mean_metrics = {name: np.mean(metrics[name]) for name in metrics}
    return metrics

def f1_helper(group1, group2): 
    """
    Helper function to compute the F1 score
    between two groups 
    """
    
    ids1 = set([x['id'] for x in group1])
    ids2 = set([x['id'] for x in group2])
    
    tp = len(ids1 & ids2)
    fp = len(ids1 - ids2) 
    fn = len(ids2 - ids1)

    precision = safe_divide(tp, tp+fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    
    return precision, recall, f1


def f1_score(groups1, groups2):
    print("F1 SCORE ---------------")
    #print(groups1)
    #print(groups2)
    """
    Compute the f1 score between two sets of groups.
    First, compute the F1 score between each of the 
    possible set combinations, then use the 
    Hungarian algorithm to find the maximum assignment,
    i.e. the best alignment between groups in the two sets.
    """

    f1 = 0
    precision = 0
    recall = 0
    by_group = True
    pairs_intra_group = False
    pairs_by_group = False

    if by_group:
        all_p, all_r, all_f1 = [], [], []
        # Get total number of annwers from each annotator
        total_1 = 0
        total_2 = 0 
        for group1, group2 in zip(groups1, groups2):
            total_1 += len(group1)
            total_2 += len(group2)

        for group1, group2 in zip(groups1, groups2): 
            len_1 = len(group1)
            len_2 = len(group2)
            if len(group1) == 0 and len(group2) == 0:
                f1 = 1.0
                all_f1.append(f1)
                continue 
            p, r, f1 = f1_helper(group1, group2) 
          
            all_p.append(p)
            all_r.append(r)
            all_f1.append(f1* ((len_1 + len_2)/(total_1+total_2)))

        best_f1_scores = np.mean(all_f1)
        best_p_scores = np.mean(all_p)
        best_r_scores = np.mean(all_r)

        f1 = best_f1_scores

    if pairs_by_group:

        f1_scores = []

        for group1, group2 in zip(groups1, groups2):
            pairs1 = set()
            pairs2 = set()

            print(group1)
            print(group2)
            
            ids1 = set([x['id'] for x in group1])
            ids2 = set([x['id'] for x in group2])

            if len(group1) == 0 and len(group2) == 0:
                f1_scores.append(1.0)
                continue
            
            for i in ids1:
                for e in ids1:
                    if i != e:
                        pairs1.add('{'+i+','+ e+'}')

            for i in ids2:
                for e in ids2:
                    if i != e:
                        pairs2.add('{'+i+','+ e+'}')

            tp = 0
            fp = 0
            fn = 0

            tp = len(pairs1 & pairs2)
            fp = len(pairs1 - pairs2)
            fn = len(pairs2 - pairs1)

            precision = safe_divide(tp, tp+fp)
            recall = safe_divide(tp, tp + fn)
            f1 = safe_divide(2 * precision * recall, precision + recall)

            f1_scores.append(f1)
            print(f1_scores)

        f1 = np.mean(f1_scores)
        print(f1)

    if pairs_intra_group:

        pairs1 = set()
        pairs2 = set()

        # Create pairs lists 
        for group1, group2 in zip(groups1, groups2): 

            ids1 = set([x['id'] for x in group1])
            ids2 = set([x['id'] for x in group2])

            print(ids1)
            print(ids2)
            
            if len(group1) == 0 and len(group2) == 0:
                continue
            
            for i in ids1:
                for e in ids1:
                    if i != e:
                        pairs1.add('{'+i+','+ e+'}')

            for i in ids2:
                for e in ids2:
                    if i != e:
                        pairs2.add('{'+i+','+ e+'}')

        tp = 0
        fp = 0
        fn = 0

        tp = len(pairs1 & pairs2)
        fp = len(pairs1 - pairs2)
        fn = len(pairs2 - pairs1)

        precision = safe_divide(tp, tp+fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)
        print(f1)
    
    return f1, precision, recall, 0

def group_agreement(rows, enforce_num_anns = False, num_anns=2, interact=False, mturk=False, string_scorers = None): 
    rows_by_hit_id = get_groups(rows, enforce_num_anns = enforce_num_anns, num_anns = num_anns, mturk=mturk) 
    agree, disagree, perc, __ = skip_agreement(rows_by_hit_id, mturk=mturk) # Agreement, disagreement, percent agreement

    if mturk:
        user_key = "WorkerId"
    else:
        user_key = "Turkle.Username"

    # Group by HitId and then compute pairwise group overlap
    # Have dictionary sorted by example id
    id_sorted_scores = {}

    total_unskipped = 0
    total_skipped = 0
    # Skip skipped examples
    # for hit_id, ex_rows in agree.items():
    # don't skip skipped examples for now, skip later
    for hit_id, ex_rows in rows_by_hit_id.items():
        #if ex_rows[0]['Answer.is_skip']: # was edited out
            #total_skipped += 1 # was edited out
            #print('heya')
            #continue

        #total_unskipped += 1

        # Put answer_groups into dictionary based on hit id
        if hit_id in id_sorted_scores:
            for ann in ex_rows:
                id_sorted_scores[hit_id]['Answer.answer_groups'].append((ann[user_key], ann['Answer.answer_groups']))

        else:
            id_sorted_scores[hit_id] = {} 
            id_sorted_scores[hit_id]['Answer.answer_groups'] = []
            for ann in ex_rows: 
                id_sorted_scores[hit_id]['Answer.answer_groups'].append((ann[user_key], ann['Answer.answer_groups']))
            # Can input other data such as Input.questionStr, Answer.is_skip, WorkerId, Answer.answer_questions here

    group_agree, group_disagree = [], []

 
    hit_id = list(id_sorted_scores.keys())[0]
    num_anns = len(id_sorted_scores[hit_id]['Answer.answer_groups']) 
    # group scores: num_annotators, num_annotators, num_annotations
    # group_scores = np.zeros((len(id_sorted_scores.keys()), num_anns, num_anns))
    # group scores: num_annotators, num_annotators 
    group_scores = np.zeros((num_anns, num_anns))
    group_totals = np.zeros((num_anns, num_anns))
    name_to_idx, idx_to_name = {}, {}
    scores_for_avg = []
    mean_string_metrics = defaultdict(list)
    mean_string_to_ref_metrics = defaultdict(list)
    group_f1 = 0
    for i, hit_id in enumerate(id_sorted_scores.keys()):
        for ann1_idx, (ann1_name, ann1_groups) in enumerate(id_sorted_scores[hit_id]['Answer.answer_groups']):
            for ann2_idx, (ann2_name, ann2_groups) in enumerate(id_sorted_scores[hit_id]['Answer.answer_groups']):
                if ann1_name == ann2_name:
                    continue
                # check if skipped for either annotator, if yes then skip
                rows = rows_by_hit_id[hit_id]
                rows = [r for r in rows if r[user_key] == ann1_name or r[user_key] == ann2_name]
                if rows[0]['Answer.is_skip'] or rows[1]['Answer.is_skip']:
                    total_skipped += 1
                    continue

                name_to_idx[ann1_name] = ann1_idx
                name_to_idx[ann2_name] = ann2_idx
                idx_to_name[ann1_idx] = ann1_name
                idx_to_name[ann2_idx] = ann2_name
                if ann1_name == ann2_name: 
                    continue
                
                group_f1, __, __, assignment = f1_score(ann1_groups, ann2_groups)

                # Add examples that have low f1 score to disagreement file
                #temp_dict 

                if string_scorers is not None:
                    string_metrics = get_string_metrics(rows[0]['Answer.answer_questions'], 
                                                        rows[1]['Answer.answer_questions'], 
                                                        assignment, 
                                                        string_scorers)
                    for k, l in string_metrics.items():
                        mean_string_metrics[k] += l
                # print([sorted([x['id'] for x in y]) for y in ann1_groups])
                # print([sorted([x['id'] for x in y]) for y in ann2_groups])
                # print(group_f1)
                # print()
                group_scores[ann1_idx, ann2_idx] += group_f1
                group_totals[ann1_idx, ann2_idx] += 1
            
            if ann1_name == ann2_name:
                continue
            
            rows = rows_by_hit_id[hit_id]
            rows = [r for r in rows if r[user_key] == ann1_name]
            if rows[0]['Answer.is_skip'] or string_scorers is None:
                pass 
            else:
                # get string metric to original question
                ref_string_metrics = get_string_metrics(rows[0]['Answer.answer_questions'],
                                                        [rows[0]['Input.questionStr'] for i in range(len(rows[0]['Answer.answer_questions']))],
                                                        assignment=[[i for i in range(len(rows[0]['Answer.answer_questions']))], None],
                                                        scorers=string_scorers)
                for k, l in ref_string_metrics.items():
                    mean_string_to_ref_metrics[k] += l

            
            if group_f1 <= 1.0:
                with open("disagreement_output.txt", 'a') as f:
                    f.write("--------------------------------------------------------------\n")
                    f.write("F1 Score: " + str(group_f1) + "\n")
                    #f.write("Pc Score: " + str(group_pc) + "\n")
                    f.write("Question: " + rows[0]['Input.questionStr']+ "\n")
                    f.write(rows[0]["Input.imgUrl"]+ "\n")
                    f.write("Response from: " + ann1_name+ "\n")
                    f.write("     Both: "+ "\n")
                    for item in ann1_groups[0]:
                        f.write("           "+item['content']+ "\n")
                    f.write("     Purpose: "+ "\n")
                    for item in ann1_groups[1]:
                        f.write("           "+item['content']+ "\n")
                    f.write("     Reason: "+ "\n") 
                    for item in ann1_groups[2]:
                        f.write("           "+item['content']+ "\n")
                #print(ann1_groups)
                    f.write("Response from: " + ann2_name+ "\n")
                    f.write("     Both: "+ "\n")
                    for item in ann2_groups[0]:
                        f.write("           "+item['content']+ "\n")
                    f.write("     Purpose: "+ "\n")
                    for item in ann2_groups[1]:
                        f.write("           "+item['content']+ "\n")
                    f.write("     Reason: "+ "\n") 
                    for item in ann2_groups[2]:
                        f.write("           "+item['content']+ "\n")             
                #print(ann2_groups)

    
    avg_score = group_scores / group_totals
    # reshape to take just upper triangle 
    avg_score = avg_score[np.triu_indices(num_anns, k=1)]
    #print(f"total skipped: {total_skipped}")
    #print(f"total unskipped: {total_unskipped}")

    return avg_score, mean_string_metrics, mean_string_to_ref_metrics

def pprint(rows, fields):
    def stringify(x): 
        if type(x) in [dict, list]: 
            return json.dumps(x, indent=4)
        else:
            return str(x)


    to_print = []
    header = f"{len(rows)} for fields {', '.join(fields)}"
    to_print.append(header) 
    prefix = "\t"
    for row in rows:

        values = [stringify(row[f]) for f in fields]
        to_print.append(f"{prefix}{', '.join(values)}")
    print("\n".join(to_print))
            


if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="path to results csv")
    parser.add_argument("--enforce-num-anns", action='store_true')
    parser.add_argument("--interact", action="store_true")
    parser.add_argument("--n", type=int, default=2, help="number of annotators per example")
    parser.add_argument("--mturk", action="store_true", help="set flag to true if csv is from mturk")
    parser.add_argument("--pilot", action="store_true", help="set flag to true if csv is from pilot")
    parser.add_argument("--anns", type=str, default=None, help='path to annotator file')
    parser.add_argument("--string-metrics", action="store_true")
    parser.add_argument("--output-disagreement", action="store_true")
    args = parser.parse_args()



    if args.anns is not None:
        anns = open(args.anns).read().split("\n")
    else:
        anns = None
    rows = process_csv(args.csv, pilot=args.pilot, anns=anns)
    rows_by_hit_id = get_groups(rows, 
                                args.enforce_num_anns, 
                                args.n,
                                args.mturk)

    annotator_report(rows_by_hit_id, args.mturk)
    agree, disagree, skip_agree_perc, skip_per_annotator_agreement = skip_agreement(rows_by_hit_id, interact=args.interact, mturk=args.mturk) 


    print(f"all annotators agree on skips {skip_agree_perc*100:.2f}% of the time")
    # print(f"per_annotator: {skip_per_annotator_agreement}")

    pairwise_skip_agreement = [v[0] for v in skip_per_annotator_agreement.values()] 
    print(f"pairwise skip agreement mean: {np.mean(pairwise_skip_agreement) * 100:.1f}%")
    print(f"pairwise skip agreement std: {np.std(pairwise_skip_agreement) * 100:.1f}%")
    print(f"pairwise skip agreement min: {np.min(pairwise_skip_agreement) * 100:.1f}%")
    print(f"pairwise skip agreement max: {np.max(pairwise_skip_agreement) * 100:.1f}%")

    #if args.string_metrics:
    #    bleu_scorer = BleuSimilarityScore()
    #    bert_scorer = BertSimilarityScore()
    #    bart_scorer = BartSimilarityScore()
    #
    #    string_scorers = [("bleu", bleu_scorer), ("bert", bert_scorer), ("bart", bart_scorer)]
    #else:
    string_scorers = None 
    (group_agreement_scores, 
     string_metrics, 
     ref_string_metrics) = group_agreement(rows, 
                                            num_anns = args.n, 
                                            enforce_num_anns=args.enforce_num_anns, 
                                            interact=args.interact, 
                                            mturk=args.mturk, 
                                            string_scorers = string_scorers) 
                                        

    print(f"pairwise agreement scores mean: {np.mean(group_agreement_scores) * 100:.1f}%")
    print(f"pairwise agreement scores std: {np.std(group_agreement_scores) * 100:.1f}%")
    print(f"pairwise agreement scores min: {np.min(group_agreement_scores) * 100:.1f}%")
    print(f"pairwise agreement scores max: {np.max(group_agreement_scores) * 100:.1f}%")

    mean_metrics = {k: np.mean(v) for k,v in string_metrics.items()}
    print(f"inter-annotator string metrics: {mean_metrics}")
    ref_mean_metrics = {k: np.mean(v) for k,v in ref_string_metrics.items()}
    print(f"annotator to reference string metrics: {ref_mean_metrics}")
