import openai
from decouple import config
from pydub import AudioSegment
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests
import json


#from functions.database import get_recent_messages
#from functions.prompt import LANGUAGE

# Retrieve Enviornment Variables
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")


# Open AI - Chat GPT
def next_qns(message_input):

  messages = []
  assistant_message = {"role": "assistant", "content": "You are a German friend who is having conversation with your friend who is learning German in the last 2 weeks. Your aim is to speak in German as much as possible so that he learns from you"}
  messages.append(assistant_message)
  user_message = {"role": "user", "content": message_input }
  messages.append(user_message)

  try:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0613",
      messages=messages
    )
    #print(response)
    message_text = response["choices"][0]["message"]["content"]
    return message_text
  except Exception as e:
    print(e)
    return e

GPT_MODEL = "gpt-3.5-turbo-0613"
@retry(wait=wait_random_exponential(multiplier=1, max=50), stop=stop_after_attempt(5))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

functionss = [
    {
        "name": "evaluate_sentence_data",
        "description": "Based on the question and sentence given evalaute the sentence based on grammar and appropriateness",
        "parameters": {
            "type": "object",
            "properties": 
            {
                "grammar_feedback": {
                    "type": "string",
                    "description": "Evalaute the usage of grammar and point out any mistakes.",
                },
                "appropriateness_feedback": {
                    "type": "string",
                    "description": "Based on the question and answer, evalaute the how appropriate it is and give feedback on how to enhance the reply"    
                },
                "suggested_answer":{
                    "type":"string",
                    "description":"Suggest one model answer for the question based on the user's mistake, with same formality as the user"
                },
                "grammar_score":{
                    "type":"integer",
                    "description":"Give a score out of 5 for grammar"
                },
                "appropriateness_score":{
                    "type":"integer",
                    "description":"Give a score out of 5 for appropriateness"
                },
            },
            "required": ["grammar_feedback","conjucation_feedback","appropriateness_feedback","suggested_answer","grammar_score","appropriateness_score"],
        },
    },
]


def feedback_fn(question,answer):
    if answer != "Error":
        messages = []
        messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. The user is a German beginer. Hence, give feedback as much as possible in simple english."})
        messages.append({"role": "user", "content": "Question: "+ question})
        messages.append({"role": "user", "content": "Answer: "+ answer})
        chat_response = chat_completion_request(
            messages, functions=functionss, function_call={"name": "evaluate_sentence_data"}
        )
        print(chat_response)
        assistant_message = chat_response.json()["choices"][0]["message"]
        return json.loads(assistant_message['function_call']['arguments'])
