import subprocess
import json
import sys
import pathlib 

sorted_question_data = {}

examples_needed = 1000
count = 0

f = open('/brtx/603-nvme2/jgualla1/why_question_ambiguity/vqa/v2_OpenEnded_mscoco_train2014_questions.json', 'r')
question_data = json.load(f)

g = open('/brtx/603-nvme2/jgualla1/why_question_ambiguity/vqa/v2_mscoco_train2014_annotations.json', 'r')
annotation_data = json.load(g)

for question_ in question_data['questions']:
    #print(question)
    if "Why" in question_["question"]: 
        count += 1
        question_id = question_["question_id"]
        image_id = question_["image_id"]
        question = question_["question"]
        sorted_question_data[question_id] = {"question": question, "image_id": image_id}

    if count >= examples_needed:
        break

for annotation_ in annotation_data['annotations']:
    #print(annotation_)
    if annotation_['question_id'] in sorted_question_data:
        if len(annotation_["answers"]) >= 1:
            sorted_question_data[annotation_['question_id']]["multiple_answer"] = "yes"
            sorted_question_data[annotation_['question_id']]["answers"] = annotation_["answers"]
        else:
            sorted_question_data[annotation_['question_id']]["multiple_answer"] = "no"
            sorted_question_data[annotation_['question_id']]["answers"] = annotation_["answers"]


with open("why_question_examples.json", "w") as outfile:
    json.dump(sorted_question_data, outfile)








