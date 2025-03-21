import re
import ast
from groq import Groq
import os
import json
from openai import OpenAI
from pymongo import MongoClient
import requests
from dotenv import load_dotenv

def extract_candidate_data(xxo):
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "From this I want you to extract entities as following and return in JSON \nCandidate Name Exact Name Word To Word But Capitalized\nDate Of Birth: DD/MM\nGender:\nEducation:\nUniversity:\nTotal Experience: (in int)\nState: (Abbr)\nTechnology:\nEnd Client:\nInterview Round:\nJob Title:\nEmail ID:\nContact No:\nDate of Interview:\nStart Time Of Interview: (IN EASTERN TIME ZONE CONVERTED)\nEnd Time Of Interview: (IN EASTERN TIME ZONE COVNERTED) If NOt available add duration into Start time\n"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": xxo
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=1,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )
    # print(response)
    x = response.output[0].content[0].text
    print(x)
    clean_text = x.strip("```json\n").strip("```").strip()
    print(clean_text)
    # Convert JSON string to Python dictionary
    data = json.loads(clean_text)
    print(data)
    return data

load_dotenv()

MOCK_API_URL = os.getenv("MOCK_API_URL")
MONGODB_URI = os.getenv("MONGODB_URI")

def process_mock_api_data():
    if not MOCK_API_URL or not MONGODB_URI:
        print("Missing MOCK_API_URL or MONGODB_URI in environment variables.")
        return

    try:
        response = requests.get(MOCK_API_URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error fetching data from mock API:", e)
        return

    client = MongoClient(MONGODB_URI)
    db = client['interviewSupport']
    taskBody = db['taskBody']

    for i in data:
        try:
            n_url = f"{MOCK_API_URL}/{i['id']}"
            candidate_data = extract_candidate_data(i['body'])
            final = {**i, **candidate_data}
            taskBody.insert_one(final)
            requests.delete(n_url)
        except Exception as e:
            print(f"Error processing item with ID {i['id']}: {e}")
