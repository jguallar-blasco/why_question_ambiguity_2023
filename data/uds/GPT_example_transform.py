import openai
import json 
import re

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
f = open('../examples.json', 'r')
data = json.load(f)

openai.api_key = "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"

for i, question_id in enumerate(data): 

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


    arg_prompt = "The subject of the sentence \"The man walking\" is \"man\". \n The subject of the sentence \""

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


    pred_prompt = "The predicate of the sentence \"The tree is blue\" is \"is blue\". The predicate of the sentence of \"The clothes are on the chair\" is \"are on the chair\". The predicate of the sentence of \"The men are walking\" is \"are walking\".\n The predicate of the sentence \""

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

    pp_prompt = "The present progressive of \"to walk\" is \"walking\". The present progressive of \"to be brown\" is \"being brown\". \n The present progressive of \""

    # Extract progressive form
    response_lemma = openai.Completion.create(
        model="text-davinci-003",
        prompt = pp_prompt + lemma + "\" is",
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
    print(f"Present progressive: {lemma}")

    if i == 20:
        exit()

    print("------------------------------------------------")

    line_dict = {
        'hit_file_format_version': hit_file_format_version, 
        'corpus_id': VQA, # TBD 
        'sentence_id': question_id, # Sentence ID
        'predicate_token_id': 0, # Position of predicate in sentence
        'roleset': 0, # Nothing
        'predicate_lemma': 0, # Lemma
        'predicate_progressive': 0, # Progressive
        'argnum': 0, # TBD
        'sentences_and_args_as_json': 0, # example -- {"argument_phrase": " ", "full_argument_label": " ", "sentence": "I <span class=\\\"predicate\\\">understand</span> <span class=\\\"argument\\\" class=\\\"dobj\\\">all of those comparisons</span> , however , the reality is if we lose Dean ( which we will if we do n&#39;t pay 65 k + 10 k ) , we will end up hiring a replacement at 75 - 80 k ."}
        'sampling_method': 0 # TBD
    }



# Format for csv
# hit_file_format_version, corpus_id, sentence_id, predicate_token_id, roleset, predicate_lemma, predicate_progressive, argnum, sentences_and_args_as_json, sampling_method

with open(out_path, "w") as f1:
    writer = csv.DictWriter(f1, fieldnames=['hit_file_format_version', 'corpus_id', 'sentence_id', 'predicate_token_id', 'roleset', 'predicate_lemma', 'predicate_progressive', 'argnum', 'sentences_and_args_as_json', 'sampling_method'])
    writer.writeheader()
    for line in to_write:
        writer.writerow(line)






