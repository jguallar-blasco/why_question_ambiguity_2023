import subprocess
import json
import sys
import pathlib 

data = json.load(open(sys.argv[1]))

def get_image_fname(num):
    num_digits = len("000000264110")
    n = len(str(num))
    n_zeros = num_digits-n
    zeros = "".join(['0'] * n_zeros)
    name = f"COCO_train2014_{zeros}{num}.jpg"
    return name

image_root = pathlib.Path("/brtx/603-nvme2/estengel/annotator_uncertainty/vqa/train2014/") 

to_copy_path = pathlib.Path("to_copy")
to_copy_path.mkdir(exist_ok=True)

#print(data)
#data = data[0]
for example in data:
    image_id = data[example]['question_id']
    image_id = str(image_id)[0:-3]
    #print(image_id)
    fname = get_image_fname(image_id) 
    path_to_image = image_root.joinpath(fname) 
    
    print(path_to_image)
   
    # copy 
    subprocess.Popen(["cp", str(path_to_image), "to_copy"])  