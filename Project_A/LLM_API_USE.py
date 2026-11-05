import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Check if the Gemini key is present
if not os.getenv("GEMINI_API_KEY"):
    print("Failed to Load: GEMINI_API_KEY is missing from your .env file.")
    exit(0)

print("API Loaded")

# Initialize client using Google's OpenAI-compatible layer
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
user_prompt=input("Ask Gemini: ")
# Trigger the chat completion with the updated model name
response = client.chat.completions.create(
    model="gemini-3.6-flash",  # UPDATED HERE
    messages=[
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

print(user_prompt)
# Output the text response
print("\nResponse from Gemini:")
#  Correct (Indexes the first option in the list)
print(response.choices[0].message.content)