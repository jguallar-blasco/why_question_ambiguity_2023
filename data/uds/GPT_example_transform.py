import openai
import json 
import re
import csv

'''
Code to convert VQA why-question examples from the why-question to the declarative form, extract the lemma, and 
prepare the data for UDS annotation HIT. 
'''

# CSV outpath
out_path = 'test'
formated_data = []
hit_file_format_version = 1

# Process VQA why-questions
data = []
f = open('../100_vqa_examples.json', 'r')
data = json.load(f)
to_write = []

openai.api_key = "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"

for i, question_id in enumerate(data): 

    url_base = "https://ugrad.cs.jhu.edu/~jgualla1/"

    append_num = 12 - len(str(data[question_id])[:-3])
    zero_append = append_num * '0'
    image_url = f"{url_base}{'COCO_train2014_'}{zero_append}{str(data[question_id])[:-3]}{'.jpg'}"    

    cur_data = data[question_id]
    cur_why_question = cur_data["question"]
    print(f"Why question: {cur_why_question}")

    # Rewrite sentence 
    response_re = openai.Completion.create(
        model="text-davinci-003",
        prompt = "The declarative form of \"Why are there so many birds in the sky\" is \"There are so many birds in the sky\". The declarative form of \"Why are there so many apples in the store\" is \"There are so many apples in the store\". \n The declarative form of \"" + cur_why_question + "\" is ", 
        temperature=0.1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    #print(response_re)
    choices = response_re["choices"]
    text = choices[-1]["text"]
    #print(f"Generated text: {text}")
    subjects = re.findall(r'"(.*?)"', text)
    declarative = subjects[0]
    print(f"Declarative: {declarative}")
    declarative_tokens = declarative.split(' ').copy()


    arg_prompt = "The subject of the sentence \"The man walking\" is \"the man\". The subject of the sentence \"The birds are here\" is \"The birds\". The subject of the sentence \"The police are running\" is \"The police\". The subject of the sentence \"The child is sad\" is \"The child\". The subject of the sentence \"The are only the birds in the sky\" is \"only birds in the sky\". \n The subject of the sentence \""

    # Extract argument
    response_arg = openai.Completion.create(
        model="text-davinci-003",
        prompt = arg_prompt + declarative + "\" is",
        temperature=0.1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )


    #print(f"Prompt for subject extraction: {arg_prompt + cur_why_question}")
    choices = response_arg["choices"]
    text = choices[-1]["text"]
    #print(f"Generated text: {text}")
    subjects = re.findall(r'"(.*?)"', text)
    subject = subjects[0]
    print(f"Subject: {subject}")


    pred_prompt = "The predicate of the sentence \"The tree is blue\" is \"is blue\". The predicate of the sentence \"The man is cooking so many hot dogs\" is \"is cooking\". The predicate of the sentence of \"The clothes are on the chair\" is \"are on the chair\". The predicate of the sentence of \"The men are walking\" is \"are walking\". The predicate of the sentence of \"The men appear only as they are\" is \"the men appear only as\".\n The predicate of the sentence \""

    # Extract predicate
    response_pred = openai.Completion.create(
        model="text-davinci-003",
        prompt = pred_prompt + declarative + "\" is",
        temperature=0.1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    


    #print(f"Prompt for predicate extraction: {pred_prompt + cur_why_question}")
    choices = response_pred["choices"]
    text = choices[-1]["text"]
    #print(f"Generated text: {text}")
    predicates = re.findall(r'"(.*?)"', text)
    predicate = predicates[0]
    print(f"Predicate: {predicate}")

    # Locate predicate tokens
    predicate_split = predicate.split(' ').copy()
    predicate_loc_s = declarative_tokens.index(predicate_split[0])
    predicate_loc_e = declarative_tokens.index(predicate_split[-1])
    predicate_loc = (predicate_loc_s, predicate_loc_e)

    lemma_prompt = "The lemma of \"is walking\" is \"to walk\". The lemma of \"is brown\" is \"to be brown\". \n The lemma of \""

    # Extract lemma
    response_lemma = openai.Completion.create(
        model="text-davinci-003",
        prompt = lemma_prompt + predicate + "\" is",
        temperature=0.1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    #print(f"Generated text: {response_lemma}")
    choices = response_lemma["choices"]
    text = choices[-1]["text"]
    lemmas = re.findall(r'"(.*?)"', text)
    lemma = lemmas[0]
    print(f"Lemma: {lemma}")

    pp_prompt = "The present progressive of \"to walk\" is \"walking\". The present progressive of \"to be brown\" is \"being brown\". The present progressive of \"to be in the car\" is \"being in the car\". \n The present progressive of \""

    # Extract progressive form
    response_pp = openai.Completion.create(
        model="text-davinci-003",
        prompt = pp_prompt + lemma + "\" is",
        temperature=0.1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    #print(f"Generated text: {response_lemma}")
    choices = response_pp["choices"]
    text = choices[-1]["text"]
    pp = re.findall(r'"(.*?)"', text)
    #lemma = lemmas[0]
    print(f"Present progressive: {pp[0]}")

    print("------------------------------------------------")

    dic = {"argument_phrase":subject,"full_argument_label":"nsubj","sentence":'<span class=\\\\\\"argument\\\\\\"class=\\\\\\"nsubj\\\\\\">'+subject+'</span><span class=\\\\\\"predicate\\\\\\">' + predicate + '</span>'}
    
    print('<span class=\\\\\\\'argument\\\\\\\'class=\\\\\\\'nsubj\\\\\\>')

    

    line_dict = {
        'hit_file_format_version': '2.0.0', 
        'corpus_id': 'VQA', # TBD 
        'video_id': image_url, # Sentence ID
        'predicate_token_id': predicate_loc, # Position of predicate in sentence
        'roleset': '', # Nothing
        'predicate_lemma': lemma, # Lemma
        'predicate_progressive': pp[0], # Progressive
        'argnum': subject, # TBD
        'sentences_and_args_as_json': dic,
        'sampling_method': 'it-happened' # TBD
    }
    #print(line_dict)
    to_write.append(line_dict)
    #print(to_write)
    if i == 2:
        break



# Format for csv
# hit_file_format_version, corpus_id, sentence_id, predicate_token_id, roleset, predicate_lemma, predicate_progressive, argnum, sentences_and_args_as_json, sampling_method

with open("../3_input_uds_with_images.csv", "w") as f1:
    fieldnames = ['hit_file_format_version', 'corpus_id', 'video_id', 'predicate_token_id', 'roleset', 'predicate_lemma', 'predicate_progressive', 'argnum', 'sentences_and_args_as_json', 'sampling_method']
    writer = csv.DictWriter(f1, fieldnames=fieldnames)
    writer.writeheader()
    #writer.writeheader()
    for line in to_write:
        writer.writerow(line)






