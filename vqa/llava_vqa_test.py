import os
from PIL import Image 
import json

# -------------------------------------------------
# Run VQA task on LLaVA model
os.chdir("/brtx/603-nvme2/jgualla1/LLaVA/")
os.environ['TRANSFORMERS_CACHE'] = '/brtx/603-nvme2/jgualla1/'
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path
from llava.eval.run_llava import eval_model

os.chdir("/home/jgualla1/why_ambiguity_2023/why_question_ambiguity_2023/")
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

    os.chdir("/brtx/603-nvme2/jgualla1/LLaVA/")
    model_path = "liuhaotian/llava-v1.5-7b"
    prompt = purpose_question
    image_file = "/home/jgualla1/why_ambiguity_2023/why_question_ambiguity_2023/data/to_copy/COCO_train2014_" + image_id + ".jpg"

    args = type('Args', (), {
        "model_path": model_path,
        "model_base": None,
        "model_name": get_model_name_from_path(model_path),
        "query": prompt,
        "conv_mode": None,
        "image_file": image_file,
        "sep": ",",
        "temperature": 0,
        "top_p": 1,
        "num_beams": 1,
        "max_new_tokens": 1024,
        "use_cache": True
    })()

    eval_model(args)

# --------------------------------------------------




