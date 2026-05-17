from llm_sdk.llm_sdk import Small_LLM_Model
import json

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
    }
]


def prepare_data(lst, dct):
    val = {}
    for d in funcs_difinitions:
        funcs_list.append(d["name"])
        for k, v in d["parameters"].items():
            val.update({k: v["type"]})
        functions_parameters.update(val)

funcs_list = []
functions_parameters = {}
prepare_data(funcs_list, functions_parameters)




prompt = "What is the sum of 265 and 345?"

real_prompt = ""
for d in funcs_difinitions:
    real_prompt += "\n"
    real_prompt += d["name"]
    real_prompt += " : "
    real_prompt += d["description"]
real_prompt += f"\n\nUser Prompt: {prompt}\n\nJSON:"


print(real_prompt)



state = "OPEN"
ids_prompt_json = []
ids_json = []


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

        state == "COLON"
        continue


    if state == "COLON":
        break





print(obj.decode(ids_json))
