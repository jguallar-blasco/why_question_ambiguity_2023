import argparse
import argparse
import json
import csv 

def merge_csvs(filenames, fieldnames_):
    fieldnames = fieldnames_
    data = {filename:[] for filename in filenames}
    for filename in filenames:
        with open(filename) as f1:
            reader = csv.DictReader(f1)
            for i, row in enumerate(reader):
                row['HITId'] = i 
                data[filename].append(row)
    to_ret = []
    for i in range(len(data[filenames[0]])): 
        for filename in filenames:
            row = data[filename][i]
            to_ret.append(row)
    return to_ret 

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("--csvs", nargs="+", required=True, help="path to results csv")
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--file_type", type=str, required=True)
    args = parser.parse_args()

    if args.file_type == 'p_v_r':
        fieldnames = ["HITId","HITTypeId","Title","CreationTime","MaxAssignments","AssignmentDurationInSeconds","AssignmentId","WorkerId","AcceptTime","SubmitTime","WorkTimeInSeconds","Input.answerGroups","Input.answerQuestions","Input.imgUrl","Input.questionStr","Answer.answer_groups","Answer.answer_questions","Answer.is_skip","Answer.skipCheck","Answer.skip_reason","Turkle.Username"]
    elif args.file_type == 'uds':
        fieldnames = ["HITId","HITTypeId","Title","CreationTime","MaxAssignments","AssignmentDurationInSeconds","AssignmentId","WorkerId","AcceptTime","SubmitTime","WorkTimeInSeconds","Input.argnum","Input.corpus_id","Input.hit_file_format_version","Input.predicate_lemma","Input.predicate_progressive","Input.predicate_token_id","Input.roleset","Input.sampling_method","Input.sentence_id","Input.sentences_and_args_as_json","Answer.awareness","Answer.awareness_grammatical","Answer.awareness_makes_sense","Answer.change_of_location","Answer.change_of_location_grammatical","Answer.change_of_location_makes_sense","Answer.change_of_possession","Answer.change_of_possession_grammatical","Answer.change_of_possession_makes_sense","Answer.change_of_state","Answer.change_of_state_grammatical","Answer.change_of_state_makes_sense","Answer.dynamic","Answer.dynamic_grammatical","Answer.dynamic_makes_sense","Answer.existed_after","Answer.existed_after_grammatical","Answer.existed_after_makes_sense","Answer.existed_before","Answer.existed_before_grammatical","Answer.existed_before_makes_sense","Answer.existed_during","Answer.existed_during_grammatical","Answer.existed_during_makes_sense","Answer.instigation","Answer.instigation_grammatical","Answer.instigation_makes_sense","Answer.partitive","Answer.partitive_grammatical","Answer.partitive_makes_sense","Answer.question_presentation_order","Answer.sentence_grammatical","Answer.sentient","Answer.sentient_grammatical","Answer.sentient_makes_sense","Answer.volition","Answer.volition_grammatical","Answer.volition_makes_sense","Answer.was_for_benefit","Answer.was_for_benefit_grammatical","Answer.was_for_benefit_makes_sense","Answer.was_used","Answer.was_used_grammatical","Answer.was_used_makes_sense","Turkle.Username"]

    merged_lines = merge_csvs(args.csvs)
    with open(args.out,"w") as f1:
        writer = csv.DictWriter(f1, fieldnames=fieldnames) 
        writer.writeheader()
        for row in merged_lines:
            writer.writerow(row) 

