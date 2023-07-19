import json 
import csv
import argparse
from collections import defaultdict

# All answers grouped by default to "other"
def get_answer_groups(annotations):
    #data = annotations[0] # get annotations dict
    #new_clusters = data["non_repeat_answers"]
    #groups = defaultdict(set)
    #print(data)

    to_ret = []
    i = 0
    to_group = []
    for cluster in annotations:
        #j = 0
        for object in cluster:
            ans = object["content"]
            
            to_group.append({"id": f"g{1}.{i}", "content": ans})
            #j += 1
        i += 1
    to_ret.append(to_group)
        
    empty = []
    to_ret.append(empty)
    to_ret.append(empty)
    return to_ret


def get_line(line, url_base = "https://ugrad.cs.jhu.edu/~jgualla1/"):
    line_dict = {"imgUrl": None,
                "questionStr": None, 
                "answerGroups": None, # From annotator
                "answerQuestions": None} # From annotator
                    

    append_num = 12 - len(str(line['question_id'])[:-3])
    zero_append = append_num * '0'
    image_url = f"{url_base}{'COCO_train2014_'}{zero_append}{str(line['question_id'])[:-3]}{'.jpg'}"
    question_str = line['question']
    # To do: 
   
    answer_groups = get_answer_groups(line['non_repeat_answers']) # getting new groups
    #annotator_1 = line['annotations'][0]
    answer_questions = ["both", "purpose/motivation", "reason/cause"] # getting new questions

    # metadata
    #line_dict['question_id'] = line['question_id'] # question id
    line_dict['imgUrl'] = json.dumps(image_url) # image url
    line_dict['questionStr'] = json.dumps(question_str) # question string
    # To do: 
    line_dict['answerGroups'] = json.dumps(answer_groups) # annotator answer groups
    line_dict['answerQuestions'] = json.dumps(answer_questions) # annotator group questions
    return line_dict 

def write_csv(to_write, out_path):
    with open(out_path, "w") as f1:
        writer = csv.DictWriter(f1, fieldnames=['imgUrl', 'questionStr', 'answerGroups', 'answerQuestions'])
        writer.writeheader()
        for line in to_write:
            writer.writerow(line)

def main(args):
    data = []
    for line in open(args.input_json, 'r'):
        data.append(json.loads(line))
    print(data)
    data = data[0]
    to_write = [get_line(data[l]) for l in data]
    write_csv(to_write, args.out_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=str, dest='input_json', required=True)
    parser.add_argument("--out-path", type=str, dest='out_path', required=True)
    args = parser.parse_args()
    print("hello")

    main(args)