from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import json
import pandas as pd
import torch
import re
import requests

# Dictionary mapping MBTI types to recommended careers
mbti_job_recommendations = {
    "ENTJ": ["Management Consultant", "Project Manager", "Entrepreneur"],
    "ENTP": ["Inventor", "Marketing Strategist", "Software Developer"],
    "ENFJ": ["Human Resources Manager", "Teacher", "Counselor"],
    "ENFP": ["Public Relations Specialist", "Creative Director", "Journalist"],
    "ESTJ": ["Operations Manager", "Accountant", "Military Officer"],
    "ESTP": ["Stock Trader", "Paramedic", "Real Estate Agent"],
    "ESFJ": ["Nurse", "Event Planner", "Customer Service Manager"],
    "ESFP": ["Actor", "Sales Representative", "Tour Guide"],
    "INTJ": ["Data Scientist", "Architect", "Research Analyst"],
    "INTP": ["Philosopher", "Software Engineer", "Mathematician"],
    "INFJ": ["Writer", "Psychologist", "Mediator"],
    "INFP": ["Author", "Graphic Designer", "Counselor"],
    "ISTJ": ["Auditor", "Librarian", "Logistics Manager"],
    "ISTP": ["Mechanic", "Surgeon", "Forensic Scientist"],
    "ISFJ": ["Nurse", "Administrative Assistant", "Social Worker"],
    "ISFP": ["Chef", "Artist", "Interior Designer"]
}

def run_analysis_with_token(access_token):
    if not access_token:
        raise ValueError("No Facebook access token provided.")

    def fetch_all_messages(url):
        all_messages = []
        while url:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error fetching data: {response.json()}")
                break

            data = response.json()
            posts = data.get('data', [])
            messages = [post.get('message', '') for post in posts if 'message' in post]
            all_messages.extend(messages)

            url = data.get('paging', {}).get('next')

        return all_messages

    # Fetch Facebook posts
    fb_url = f"https://graph.facebook.com/v21.0/me/feed?access_token={access_token}"
    all_user_messages = fetch_all_messages(fb_url)

    if not all_user_messages:
        print("No messages fetched. Check your Facebook access token or permissions.")
        return None, []

    # Save messages to messages.json
    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(all_user_messages, f, ensure_ascii=False, indent=4)

    # Load messages
    with open("messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)

    df = pd.DataFrame(messages, columns=['message'])

    # Sentiment pipeline
    sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model=sentiment_model_name,
        tokenizer=sentiment_model_name
    )

    results = sentiment_analyzer(df['message'].tolist())
    df['sentiment_label'] = [r['label'] for r in results]
    df['sentiment_score'] = [r['score'] for r in results]

    # Combine text for MBTI
    combined_text = " ".join(df['message'])
    combined_text = re.sub(r"[^a-zA-Z\s]", "", combined_text).strip()

    mbti_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
    mbti_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)

    inputs = mbti_tokenizer(combined_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = mbti_model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

    mbti_types = ["ENTJ","ENTP","ENFJ","ENFP","ESTJ","ESTP","ESFJ","ESFP","INTJ","INTP","INFJ","INFP","ISTJ","ISTP","ISFJ","ISFP"]
    predicted_mbti = mbti_types[predicted_class]
    recommended_jobs = mbti_job_recommendations.get(predicted_mbti, [])

    return predicted_mbti, recommended_jobs
