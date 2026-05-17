from llm_sdk.llm_sdk import Small_LLM_Model
import json
import numpy as np

obj = Small_LLM_Model()


file_path = obj.get_path_to_vocab_file()
str_to_id = {}
id_to_str = {}


with open(file_path, "r") as f:
    data_str = f.read()
    str_to_id = json.loads(data_str)
for tok, id in str_to_id.items():
    id_to_str[id] = tok


funcs_difinitions = [
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_reverse_string",
    "description": "Reverse a string and return the reversed result.",
    "parameters": {
      "s": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_get_square_root",
    "description": "Calculate the square root of a number.",
    "parameters": {
      "a": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
  {
    "name": "fn_substitute_string_with_regex",
    "description": "Replace all occurrences matching a regex pattern in a string.",
    "parameters": {
      "source_string": {
        "type": "string"
      },
      "regex": {
        "type": "string"
      },
      "replacement": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  }
]


def prepare_data(lst, dct):
    for d in funcs_difinitions:
        val = {}
        funcs_list.append(d["name"])
        for k, v in d["parameters"].items():
            val.update({k: v["type"]})
        functions_parameters.update({d["name"]:val})



def masking(logits, alloweds=None):
    arr_logits = np.array(logits)

    mask = np.full_like(arr_logits, -np.inf)

    if alloweds is None:
        mask = np.full_like(arr_logits, 0.0)

    else:
        mask[list(alloweds)] = 0.0
    
    return np.argmax(arr_logits + mask)




funcs_list = []
functions_parameters = {}
prepare_data(funcs_list, functions_parameters)




prompt = "Greet shrek"

real_prompt = ""
for d in funcs_difinitions:
    real_prompt += "\n"
    real_prompt += d["name"]
    real_prompt += " : "
    real_prompt += d["description"]
real_prompt += f"\n\nUser Prompt: {prompt}\n\nJSON:"



state = "OPEN"
ids_prompt_json = obj.encode(real_prompt)[0].tolist()
ids_json = []
current_function_name = ""
done = []
current_key = ""
current_params_keys = ""


while True:

    if state == "OPEN":
        ids_json.append(str_to_id["{"])
        ids_prompt_json.append(str_to_id["{"])
        state = "NAME_AS_STR"
        continue


    if state == "NAME_AS_STR":
        lst = obj.encode('"name"')[0].tolist()

        for l in lst:
            ids_json.append(l)
            ids_prompt_json.append(l)

        state = "COLON"
        continue


    if state == "COLON":
        ids_json.append(str_to_id[":"])
        ids_prompt_json.append(str_to_id[":"])
        state = "FUNC_NAME"
        continue


    if state == "FUNC_NAME":
        buffer = ""
        
        fnames_encoded = []
        for n in funcs_list:
            fnames_encoded.append(obj.encode(f'"{n}"')[0].tolist())


        pos = 0
        while True:
            alloweds = set()

            for l in fnames_encoded:
                if len(l) > pos:
                    alloweds.add(l[pos])



            logits = obj.get_logits_from_input_ids(ids_prompt_json)
            next_id = int(masking(logits, alloweds))
            ids_json.append(next_id)
            ids_prompt_json.append(next_id)
            buffer += obj.decode(next_id)


            fnames_encoded = [
                lst for lst in fnames_encoded if len(lst) > pos and lst[pos] == next_id
            ]

            pos += 1
            if len(fnames_encoded) == 1 and pos == len(fnames_encoded[0]):
                current_function_name = buffer[1:-1]
                current_params_keys = functions_parameters[current_function_name]
                state = "COMMA"
                break
        continue


    if state == "COMMA":
        ids_json.append(str_to_id[","])
        ids_prompt_json.append(str_to_id[","])
        state = "PARAMETER_STR"
        continue


    if state == "PARAMETER_STR":
        lst = obj.encode('"parameters"')[0].tolist()

        for l in lst:
            ids_json.append(l)
            ids_prompt_json.append(l)
        
        state = "COLON2"
        continue


    if state == "COLON2":
        ids_json.append(str_to_id[":"])
        ids_prompt_json.append(str_to_id[":"])
        state = "PARA_OPEN"
        continue


    if state == "PARA_OPEN":
        ids_json.append(str_to_id["{"])
        ids_prompt_json.append(str_to_id["{"])
        state = "PARA_KEY"
        continue


    if state == "PARA_KEY":

        if len(current_params_keys) == 0 or len(done) == len(current_params_keys):
            ids_json.append(str_to_id["}"])
            ids_prompt_json.append(str_to_id["}"])
            state = "END_CLOSE"
            continue


        current_key = list(current_params_keys)[len(done)]
        
        lst = obj.encode(f'"{current_key}"')[0].tolist()
        for l in lst:
            ids_json.append(l)
            ids_prompt_json.append(l)

        state = "COLON3"
        continue


    if state == "COLON3":
        ids_prompt_json.append(str_to_id[":"])
        ids_json.append(str_to_id[":"])
        state = "VALUE"
        continue
    

    if state == "VALUE":

        buffer = ""
    
        while True:
            alloweds = set()
            typee = current_params_keys.get(current_key, "number")


            if (typee == "number"):
                alloweds = {id for id, tok in id_to_str.items() if tok.isdecimal()}
                alloweds.add(str_to_id["}"])
                alloweds.add(str_to_id[","])
            

            else:
                alloweds = {id for id, tok in id_to_str.items() if tok.isprintable()}



            logits = obj.get_logits_from_input_ids(ids_prompt_json)
            next_id = masking(logits, alloweds)

            token = obj.decode(next_id)

            if token != ",":
                ids_json.append(next_id)
                ids_prompt_json.append(next_id)

            buffer += obj.decode(next_id)
            




            if (typee == "number"):
                
                if "," in token:
                    done.append(current_key)
                    ids_json.append(str_to_id[","])
                    ids_prompt_json.append(str_to_id[","])
                    state = "PARA_KEY"
                    break

                if "}" in token:
                    state = "END_CLOSE"
                    break
            

            else:
                print(token)




        continue











    if state == "END_CLOSE":
        ids_json.append(str_to_id["}"])
        ids_prompt_json.append(str_to_id["}"])
        break





print(obj.decode(ids_json))

