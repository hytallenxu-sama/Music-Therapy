import os
import json
from openai import AzureOpenAI
from modules.tools import *
from modules.Database import Database
from modules.Tables import *

class GPT(object):
    def __init__(self):
        ENDPOINT_URL, AZURE_OPENAI_API_KEY = self.getSecrets()
        endpoint = os.getenv("ENDPOINT_URL", ENDPOINT_URL)
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY)
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version="2024-08-01-preview",
        )

    def getSecrets(self): # get secrets from database
        db_handler = Database('sqlite:///SQLite/database.db')
        res = db_handler.query_data(Secrets)
        return res[0].ENDPOINT, res[0].API_KEY

    def autoReply(self, message, assistant_message=[]):
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI assistant that automatically response to user's comments. Using their comments, you need to reply in a soft and encouraging tone, in order to comfort the user."
                    }
                ]
            },{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
        messages = chat_prompt
        text, prompt_tokens, output_tokens = self.chat(messages)
        logger("AutoReply", f"{str(int(prompt_tokens)+int(output_tokens))} tokens used to reply: {text}")
        insertTokens(int(prompt_tokens)+int(output_tokens))
        return text

    def chat(self, messages):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        text = ''
        response = json.loads(completion.to_json())
        text += ''.join([response["choices"][i]["message"]["content"] for i in range(len(response["choices"]))])
        prompt_tokens, output_tokens = int(response["usage"]["prompt_tokens"]), int(response["usage"]["completion_tokens"])
        return text, prompt_tokens, output_tokens