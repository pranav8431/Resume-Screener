SCORING_WEIGHTS = {
    "skill_match": 40,
    "experience_match": 25,
    "semantic_similarity": 20,
    "location_match": 10,
    "education_match": 5,
}

RECOMMENDATION_THRESHOLDS = {
    "call_first": 80,
    "backup": 60,
}

SENTENCE_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TFIDF_WEIGHT = 0.4
EMBEDDING_WEIGHT = 0.6

NOTICE_PERIOD_SCORE = {
    "immediate": 10,
    "15": 9,
    "30": 8,
    "45": 7,
    "60": 5,
    "90": 3,
    "unknown": 5,
}

INDIAN_CITIES = [
    "mumbai",
    "navi mumbai",
    "thane",
    "delhi",
    "delhi ncr",
    "ncr",
    "bangalore",
    "bengaluru",
    "hyderabad",
    "pune",
    "chennai",
    "kolkata",
    "ahmedabad",
    "jaipur",
    "surat",
    "lucknow",
    "noida",
    "greater noida",
    "gurgaon",
    "gurugram",
    "chandigarh",
    "bhopal",
    "indore",
    "nagpur",
    "nashik",
    "aurangabad",
    "coimbatore",
    "mysore",
    "mysuru",
    "mangalore",
    "hubli",
    "belgaum",
    "vadodara",
    "rajkot",
    "kochi",
    "thiruvananthapuram",
    "vizag",
    "visakhapatnam",
    "patna",
    "ranchi",
    "jodhpur",
    "udaipur",
    "bhubaneswar",
    "guwahati",
    "dehradun",
    "shimla",
    "jammu",
    "srinagar",
    "remote",
]

EDUCATION_KEYWORDS = {
    "btech": ["b.tech", "btech", "b tech", "bachelor of technology", "be", "b.e"],
    "mtech": ["m.tech", "mtech", "m tech", "master of technology", "me", "m.e"],
    "mba": ["mba", "master of business administration", "pgdm"],
    "bsc": ["b.sc", "bsc", "bachelor of science"],
    "msc": ["m.sc", "msc", "master of science"],
    "bca": ["bca", "bachelor of computer applications"],
    "mca": ["mca", "master of computer applications"],
    "phd": ["phd", "ph.d", "doctorate"],
    "diploma": ["diploma", "polytechnic"],
}

USE_OPENAI = False
