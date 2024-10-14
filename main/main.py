import requests
import json

def ask_gpt(user_text):
    if not user_text:
        return "Input text is empty."

    # Структура promt
    prompt = {
        "modelUri": "gpt://b1gu0eskj5a33vgrltde/yandexgpt-lite",
        #"modelUri": "gpt://ajeui789jl571s365li4/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": "1000"
        },
        "messages": [
            {"role": "system", "text": "You are a computer science teacher, you are given a student's decision, it is wrong or correct.Find the errors and if there are any, then offer to look for them to the student, giving a hint where they may be"},
            {"role": "user", "text": user_text}
        ]
    }

    # Конвертит в JSON формат
    json_prompt = json.dumps(prompt)
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2NvJxczfE7Xdk70FVtDIjmaYyj1UomQGZpZU"
        #"Authorization": "Api-Key AQVN3pHQmdSnDwZi1kSnZ0VPVuCKxIjlUojYqxXg"
    }

    try:
        response = requests.post(url, headers=headers, data=json_prompt)
        response.raise_for_status()
        
        # Parse the response JSON
        api_response = response.json()
        
        # Берет переведенный текст из ответа
        if api_response["result"]["alternatives"]:
           Code_text = api_response["result"]["alternatives"][0]["message"]["text"]
           return f"GPT answer: {Code_text}"
        else:
            return "No response received."
        
    except requests.exceptions.RequestException as e:
        return f"Failed to send request: {e}"
    except json.JSONDecodeError:
        return "Failed to parse response."

user_text = "std::cout<<gg"
print(ask_gpt(user_text))
