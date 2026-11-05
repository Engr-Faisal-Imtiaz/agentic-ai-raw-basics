import datetime
import os
import json
import http
from tkinter import messagebox, ttk
import requests
import tkinter as tk

from pydantic import ValidationError
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
url="https://api.groq.com/openai/v1"
api=os.getenv("GROQ_API_KEY")
client=OpenAI(
    base_url=url,
    api_key=api
)
if api is None:
    print("Failed to Fetch API Key")
    exit(0)
print("Setup Done")

def get_weather(city_name: str):
    """Gets the current weather for a given city."""
    api=str(os.getenv("WEATHER_API_KEY"))
    w_url="https://api.openweathermap.org/data/2.5/weather"
    params={'q': city_name,'appid':api,'units':'metric'}
    try:
        response=requests.get(w_url,params=params)
        if response.status_code!=200:
            return {"error": f"Failed to fetch data (Status {response.status_code})"}
        data = response.json()
        return {
            "city": data['name'],
            "temperature": f"{data['main']['temp']}°C",
            "condition": data['weather'][0]['description']
        }
    except Exception as e:
        return {'error': str(e)}
def get_current_time():
    """Gets the current date and time."""
    now=datetime.datetime.now()
    return {"current_time": now.strftime("%Y-%m-%d %H:%M:%S")}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description":"Gets the current weather for a given city.",
            "parameters":{
                "type": "object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"The name of the city, e.g., Lahore or Karachi"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "get_current_time",
            "description": "Gets the current date and time.",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    }
]
root=tk.Tk()
msg_label=tk.Label(root, text="User Message: ")
msg_label.pack(anchor="w", padx=5, pady=5)
input_row = tk.Frame(root)
input_row.pack(fill="x", padx=5, pady=5)
msg_field = tk.Text(input_row, height=3, width=50)
msg_field.pack(padx=(0, 5), side="left")
output=""
def process_tools():
    
    user_prompt = msg_field.get("1.0",tk.END).strip()

    messages=[
            {"role":"user","content":user_prompt}
        ]
    while True:
        res=client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools
        )

        message=res.choices[0].message
        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                func_name=tool_call.function.name
                arguments=json.loads(tool_call.function.arguments)
                if func_name=="get_weather":
                    result=get_weather(arguments["city"])

                elif func_name=="get_current_time":
                    result=get_current_time()
                #print(f"Executed {func_name} -> result = {result}")
                messages.append(
                    {
                        "role":"tool",
                        "tool_call_id":tool_call.id,
                        "content": json.dumps(result)
                    }
                )
        else:
            output_label=tk.Label(root, text=message.content)
            output_label.pack(padx=5, pady=5, side="bottom")
            break

def main():
    fetch_btn=ttk.Button(input_row, text="->", command=process_tools)
    fetch_btn.pack(side="left")
    root.mainloop()
if __name__=="__main__":
    main()
