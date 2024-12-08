from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import json
import pandas as pd
import torch
import re
import requests

# Dictionary mapping MBTI types to recommended careers
mbti_job_recommendations = {
    "ENTJ": [
        {
            "job": "Management Consultant",
            "reasons": [
                "Thrives on strategic problem-solving and leadership.",
                "Strong decision-making skills, crucial for consulting roles.",
                "Natural ability to inspire and direct teams toward success."
            ]
        },
        {
            "job": "Project Manager",
            "reasons": [
                "Highly organized and excels in planning and execution.",
                "Enjoys taking charge and motivating teams to achieve goals.",
                "Analytical and goal-oriented, ensuring project efficiency."
            ]
        },
        {
            "job": "Entrepreneur",
            "reasons": [
                "Visionary mindset ideal for creating innovative businesses.",
                "Strong leadership skills, perfect for managing teams.",
                "Comfortable with risk-taking and ambitious endeavors."
            ]
        }
    ],
    "ENTP": [
        {
            "job": "Inventor",
            "reasons": [
                "Naturally innovative and loves brainstorming new ideas.",
                "Curious and resourceful, ideal for problem-solving.",
                "Thrives in unstructured, creative environments."
            ]
        },
        {
            "job": "Marketing Strategist",
            "reasons": [
                "Excels in persuasive communication and creative thinking.",
                "Loves analyzing trends to craft unique campaigns.",
                "Energetic and adaptable, essential for dynamic markets."
            ]
        },
        {
            "job": "Software Developer",
            "reasons": [
                "Strong logical and analytical skills, perfect for coding.",
                "Thrives on problem-solving and creating new solutions.",
                "Curious and innovative, great for exploring emerging tech."
            ]
        }
    ],
    "ENFJ": [
        {
            "job": "Human Resources Manager",
            "reasons": [
                "Empathetic and skilled at understanding people's needs.",
                "Excellent communication, vital for conflict resolution.",
                "Thrives in roles that build harmony and collaboration."
            ]
        },
        {
            "job": "Teacher",
            "reasons": [
                "Passionate about helping others grow and learn.",
                "Skilled at motivating and inspiring students.",
                "Strong interpersonal skills, ideal for diverse classrooms."
            ]
        },
        {
            "job": "Counselor",
            "reasons": [
                "Deeply empathetic, perfect for understanding clients' emotions.",
                "Skilled at fostering trust and meaningful conversations.",
                "Enjoys guiding others to achieve personal growth."
            ]
        }
    ],
    "ENFP": [
        {
            "job": "Public Relations Specialist",
            "reasons": [
                "Charismatic and excellent at building relationships.",
                "Thrives on creativity and crafting compelling stories.",
                "Flexible and adaptable, crucial for dynamic PR campaigns."
            ]
        },
        {
            "job": "Creative Director",
            "reasons": [
                "Visionary with a flair for original concepts.",
                "Energetic leader who inspires creative teams.",
                "Loves turning abstract ideas into tangible results."
            ]
        },
        {
            "job": "Journalist",
            "reasons": [
                "Inquisitive and passionate about uncovering truths.",
                "Strong communication skills for impactful storytelling.",
                "Thrives in fast-paced, ever-changing environments."
            ]
        }
    ],
    "ESTJ": [
        {
            "job": "Operations Manager",
            "reasons": [
                "Organized and efficient, excels at streamlining processes.",
                "Strong leadership skills, ideal for overseeing teams.",
                "Thrives in structured, goal-oriented environments."
            ]
        },
        {
            "job": "Accountant",
            "reasons": [
                "Detail-oriented and precise, essential for financial accuracy.",
                "Logical thinker, adept at analyzing complex data.",
                "Values stability and consistency in work."
            ]
        },
        {
            "job": "Military Officer",
            "reasons": [
                "Strong sense of duty and commitment to structure.",
                "Thrives in leadership roles with clear objectives.",
                "Values discipline and accountability in teams."
            ]
        }
    ],
    "ESTP": [
        {
            "job": "Stock Trader",
            "reasons": [
                "Thrives in high-energy, fast-paced environments.",
                "Natural risk-taker, comfortable with quick decisions.",
                "Analytical and competitive, ideal for market strategies."
            ]
        },
        {
            "job": "Paramedic",
            "reasons": [
                "Calm under pressure and quick-thinking in emergencies.",
                "Thrives on dynamic, hands-on problem-solving.",
                "Compassionate, ensuring excellent patient care."
            ]
        },
        {
            "job": "Real Estate Agent",
            "reasons": [
                "Charismatic and skilled at building client relationships.",
                "Energetic and thrives on closing deals.",
                "Adaptable, perfect for navigating diverse property markets."
            ]
        }
    ],
    "ESFJ": [
        {
            "job": "Nurse",
            "reasons": [
                "Deeply empathetic, ensuring compassionate patient care.",
                "Organized and thrives in collaborative medical teams.",
                "Values structure, essential for following healthcare protocols."
            ]
        },
        {
            "job": "Event Planner",
            "reasons": [
                "Exceptional organizational and multitasking skills.",
                "Thrives on creating memorable, well-orchestrated events.",
                "Skilled at building relationships with clients and vendors."
            ]
        },
        {
            "job": "Customer Service Manager",
            "reasons": [
                "Empathetic and patient in resolving customer concerns.",
                "Thrives in leadership roles focused on team improvement.",
                "Values creating positive, customer-first experiences."
            ]
        }
    ],
    "ESFP": [
        {
            "job": "Actor",
            "reasons": [
                "Naturally expressive and thrives in the spotlight.",
                "Energetic and adaptable, essential for dynamic roles.",
                "Loves storytelling and connecting with audiences."
            ]
        },
        {
            "job": "Sales Representative",
            "reasons": [
                "Charismatic and persuasive, perfect for closing deals.",
                "Thrives in high-energy, people-focused environments.",
                "Motivated by achieving goals and helping clients."
            ]
        },
        {
            "job": "Tour Guide",
            "reasons": [
                "Enthusiastic and skilled at engaging diverse groups.",
                "Naturally curious and enjoys sharing knowledge.",
                "Energetic and adaptable, ideal for dynamic settings."
            ]
        }
    ],
    "INTJ": [
        {
            "job": "Data Scientist",
            "reasons": [
                "Analytical and logical, thrives on problem-solving.",
                "Enjoys working with complex datasets to uncover insights.",
                "Visionary, perfect for identifying innovative trends."
            ]
        },
        {
            "job": "Architect",
            "reasons": [
                "Visionary thinker, ideal for designing structures.",
                "Thrives on long-term, strategic planning.",
                "Strong problem-solving skills, essential for complex designs."
            ]
        },
        {
            "job": "Research Analyst",
            "reasons": [
                "Enjoys digging deep into data for insights.",
                "Logical thinker, perfect for interpreting trends.",
                "Values accuracy and strategic applications."
            ]
        }
    ],
    "INTP": [
        {
            "job": "Philosopher",
            "reasons": [
                "Enjoys abstract thinking and exploring complex ideas.",
                "Analytical and logical, perfect for deep theoretical discussions.",
                "Thrives on intellectual curiosity and lifelong learning."
            ]
        },
        {
            "job": "Software Engineer",
            "reasons": [
                "Logical and detail-oriented, ideal for solving coding challenges.",
                "Enjoys working on innovative, tech-focused projects.",
                "Independent thinker, excels in problem-solving."
            ]
        },
        {
            "job": "Mathematician",
            "reasons": [
                "Naturally analytical, thrives on solving complex problems.",
                "Logical and detail-oriented, perfect for abstract thinking.",
                "Passionate about theoretical and applied mathematics."
            ]
        }
    ],
    "INFJ": [
        {
            "job": "Writer",
            "reasons": [
                "Passionate about storytelling and sharing ideas.",
                "Empathetic, creating works that resonate emotionally.",
                "Values introspection, ideal for thoughtful writing."
            ]
        },
        {
            "job": "Psychologist",
            "reasons": [
                "Deeply empathetic, understanding clients’ inner worlds.",
                "Skilled at fostering trust and meaningful conversations.",
                "Values personal growth and helping others achieve it."
            ]
        },
        {
            "job": "Mediator",
            "reasons": [
                "Natural peacemaker, skilled at resolving conflicts.",
                "Deep understanding of emotions and motivations.",
                "Thrives on fostering harmony and understanding."
            ]
        }
    ],
    "INFP": [
        {
            "job": "Author",
            "reasons": [
                "Creative and imaginative, thrives on storytelling.",
                "Values authenticity and emotional depth in work.",
                "Enjoys introspection, perfect for developing characters."
            ]
        },
        {
            "job": "Graphic Designer",
            "reasons": [
                "Artistic and innovative, ideal for creating visual content.",
                "Passionate about expressing ideas through design.",
                "Enjoys freedom and flexibility in creative work."
            ]
        },
        {
            "job": "Counselor",
            "reasons": [
                "Empathetic and passionate about helping others.",
                "Skilled at building trust and fostering growth.",
                "Values making a meaningful difference in others’ lives."
            ]
        }
    ],
    "ISTJ": [
        {
            "job": "Auditor",
            "reasons": [
                "Highly detail-oriented, ideal for financial accuracy.",
                "Thrives on structure and adherence to regulations.",
                "Logical thinker, perfect for identifying discrepancies."
            ]
        },
        {
            "job": "Librarian",
            "reasons": [
                "Organized and systematic, essential for cataloging.",
                "Thrives in quiet, focused environments.",
                "Passionate about knowledge and learning."
            ]
        },
        {
            "job": "Logistics Manager",
            "reasons": [
                "Analytical and efficient, great for overseeing operations.",
                "Enjoys planning and ensuring seamless processes.",
                "Values structure and consistency in workflows."
            ]
        }
    ],
    "ISTP": [
        {
            "job": "Mechanic",
            "reasons": [
                "Hands-on problem solver, enjoys fixing systems.",
                "Analytical and logical, perfect for diagnosing issues.",
                "Thrives in dynamic, practical environments."
            ]
        },
        {
            "job": "Surgeon",
            "reasons": [
                "Calm under pressure, ideal for high-stakes decisions.",
                "Enjoys working with precision and attention to detail.",
                "Thrives in hands-on, impactful roles."
            ]
        },
        {
            "job": "Forensic Scientist",
            "reasons": [
                "Analytical and detail-oriented, great for investigations.",
                "Logical thinker, excels in solving mysteries.",
                "Enjoys working independently and systematically."
            ]
        }
    ],
    "ISFJ": [
        {
            "job": "Nurse",
            "reasons": [
                "Compassionate and deeply empathetic, perfect for patient care.",
                "Thrives in structured environments with clear protocols.",
                "Values making a positive difference in others’ lives."
            ]
        },
        {
            "job": "Administrative Assistant",
            "reasons": [
                "Organized and detail-oriented, ideal for managing tasks.",
                "Thrives on creating order and supporting teams.",
                "Values reliability and consistency in work."
            ]
        },
        {
            "job": "Social Worker",
            "reasons": [
                "Empathetic and dedicated to helping vulnerable populations.",
                "Skilled at understanding and resolving personal challenges.",
                "Thrives in roles that make a tangible difference in society."
            ]
        }
    ],
    "ISFP": [
        {
            "job": "Chef",
            "reasons": [
                "Creative and passionate about crafting unique dishes.",
                "Enjoys hands-on work in dynamic environments.",
                "Values personal expression through culinary art."
            ]
        },
        {
            "job": "Artist",
            "reasons": [
                "Deeply creative, perfect for self-expression through art.",
                "Thrives on freedom and flexibility in creative work.",
                "Passionate about producing meaningful and inspiring pieces."
            ]
        },
        {
            "job": "Interior Designer",
            "reasons": [
                "Artistic and detail-oriented, ideal for creating beautiful spaces.",
                "Enjoys translating clients’ visions into reality.",
                "Thrives on balancing aesthetics with functionality."
            ]
        }
    ]
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
