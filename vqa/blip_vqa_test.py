import os
from PIL import Image 
import json
import requests

# -------------------------------------------------
# Run VQA task on LLaVA model
os.environ['TRANSFORMERS_CACHE'] = '/brtx/603-nvme2/jgualla1/'
from transformers import AutoProcessor, Blip2ForConditionalGeneration

processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")
model.to(device)

f = open("data/100_vqa_examples.json") # Json file
data_json = json.load(f)

#f = open('../data/uds/hit_output/Jimena_45_output_uds.csv', newline='') as f:
#dict_reader = csv.DictReader(f)
#data_csv = list(dict_reader)

for question_ in data_json:
    cur_dict = data_json[question_]
    original_question = cur_dict['question']

    # Remove 'why' from question
    split_question = original_question.split(' ')
    question = split_question[1:]

    #Edit question
    # Purpose question
    purpose_question = "For what purpose " + ' '.join(question)
    # Reason question
    reason_question = "For what reason " +  ' '.join(question)

    # Get the image file 
    image_id = question_[0:-3]
    r_len = 12 - len(image_id)
    image_id = (r_len * "0") + image_id
    #image = Image.open("data/to_copy/COCO_train2014_" + image_id + ".jpg")

    image_file = "/home/jgualla1/why_ambiguity_2023/why_question_ambiguity_2023/data/to_copy/COCO_train2014_" + image_id + ".jpg"
    image = Image.open(image_file)
    image.resize((596, 437))

    inputs = processor(image, text=purpose_question, return_tensors="pt").to(device, torch.float16)
    generated_ids = model.generate(**inputs, max_new_tokens=10)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    print(generated_text)

# --------------------------------------------------




