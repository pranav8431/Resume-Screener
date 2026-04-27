from __future__ import annotations

import re
from typing import Dict, List, Set

SKILL_DICTIONARY: Dict[str, List[str]] = {
    "python": ["python", "py", "python 3", "python3"],
    "javascript": ["javascript", "js", "es6", "es2015", "ecmascript"],
    "java": [
        "java",
        "core java",
        "java 8",
        "java8",
        "java 11",
        "java11",
        "maven",
        "gradle",
    ],
    "typescript": ["typescript"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", "c sharp", ".net"],
    "php": ["php", "php7", "php8"],
    "ruby": ["ruby", "ruby on rails"],
    "golang": ["golang", "go", "go lang"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "swift ios", "swift programming"],
    "r": ["r", "r language", "r programming"],
    "scala": ["scala"],

    "django": ["django", "django rest", "django rest framework", "drf"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "nodejs": ["nodejs", "node.js", "node js", "expressjs", "express.js", "express"],
    "spring boot": ["spring boot", "springboot", "spring"],
    "microservices": [
        "microservices",
        "micro services",
        "microservice",
        "distributed systems",
        "service mesh",
    ],
    "rest api": [
        "rest api",
        "rest apis",
        "restful",
        "restful api",
        "api development",
        "api integration",
        "web api",
        "backend api",
    ],
    "websocket": [
        "websocket",
        "websockets",
        "ws",
        "socket.io",
        "real-time api",
        "real time communication",
    ],
    "async": ["async", "asyncio", "asynchronous", "async programming", "concurrent", "concurrency"],
    "graphql": ["graphql", "graph ql"],

    "sql": ["sql", "structured query language", "pl/sql"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"],
    "redis": ["redis", "cache", "caching"],
    "elasticsearch": ["elasticsearch", "elastic search", "elk", "opensearch"],

    "aws": [
        "aws",
        "amazon web services",
        "ec2",
        "s3",
        "lambda",
        "rds",
        "sagemaker",
        "bedrock",
        "aws cloud",
    ],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "dockerfile", "docker-compose", "containerization", "container"],
    "kubernetes": ["kubernetes", "k8s", "container orchestration"],
    "ci/cd": [
        "ci/cd",
        "cicd",
        "continuous integration",
        "continuous deployment",
        "github actions",
        "gitlab ci",
        "jenkins",
        "jenkins pipeline",
    ],
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "linux": ["linux", "ubuntu", "centos", "unix", "bash", "shell scripting", "bash scripting"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],

    "machine learning": [
        "machine learning",
        "ml",
        "sklearn",
        "scikit-learn",
        "scikit learn",
        "ml models",
        "model training",
        "supervised learning",
        "unsupervised learning",
        "classification",
        "regression",
        "clustering",
    ],
    "deep learning": [
        "deep learning",
        "dl",
        "neural network",
        "neural networks",
        "cnn",
        "rnn",
        "lstm",
        "transformer model",
        "backpropagation",
        "fine-tuning",
        "fine tuning",
    ],
    "data science": [
        "data science",
        "data scientist",
        "exploratory data analysis",
        "eda",
        "feature engineering",
        "model evaluation",
    ],
    "computer vision": [
        "computer vision",
        "image processing",
        "object detection",
        "yolo",
        "opencv",
        "cv2",
        "image recognition",
        "image classification",
        "segmentation",
    ],
    "nlp": [
        "nlp",
        "natural language processing",
        "spacy",
        "nltk",
        "text mining",
        "text classification",
        "named entity recognition",
        "ner",
        "sentiment analysis",
        "text extraction",
    ],
    "llm": [
        "llm",
        "llms",
        "large language model",
        "large language models",
        "langchain",
        "gpt",
        "chatgpt",
        "claude api",
        "openai api",
        "foundation model",
        "generative ai",
        "gen ai",
        "genai",
    ],
    "langchain": ["langchain", "lang chain"],
    "rag": ["rag", "retrieval augmented generation", "retrieval-augmented"],
    "prompt engineering": [
        "prompt engineering",
        "prompt design",
        "prompt optimization",
        "few-shot",
        "zero-shot",
        "chain of thought",
        "agentic workflow",
        "agentic workflows",
        "tool use",
        "function calling",
    ],
    "ollama": ["ollama", "local llm", "on-premise llm", "self-hosted llm"],
    "faiss": [
        "faiss",
        "vector search",
        "vector store",
        "vector database",
        "pinecone",
        "weaviate",
        "chroma",
        "chromadb",
        "qdrant",
        "semantic search",
        "similarity search",
        "embedding search",
    ],
    "transformers": [
        "transformers",
        "huggingface",
        "hugging face",
        "sentence transformers",
        "sentence-transformers",
        "bert",
        "gpt",
        "t5",
        "bart",
        "roberta",
    ],

    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib", "seaborn", "plotly", "visualization", "data visualization"],
    "jupyter": ["jupyter", "jupyter notebook", "ipython", "colab", "google colab"],

    "react": ["react", "reactjs", "react.js"],
    "nextjs": ["nextjs", "next.js", "next js"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss", "tailwind", "tailwindcss"],

    "spark": ["apache spark", "pyspark", "spark"],
    "kafka": ["kafka", "apache kafka", "message queue", "event streaming"],
    "airflow": ["airflow", "apache airflow", "workflow orchestration", "data pipeline", "etl pipeline"],
    "data engineering": ["data engineering", "data engineer", "etl", "data pipeline", "data warehouse"],

    "pytest": ["pytest", "unittest", "unit testing", "test driven", "tdd", "integration testing"],
    "selenium": ["selenium", "selenium webdriver", "web scraping", "browser automation"],

    "agile": ["agile", "scrum", "kanban", "jira", "sprint"],
}

ALIAS_EXCEPTIONS = {
    "r",
    "c",
    "c#",
    "c++",
    "js",
    "ml",
    "dl",
    "ai",
    "qa",
    "ui",
    "ux",
    "ws",
    "tf",
}


def _is_valid_alias(alias: str) -> bool:
    token = alias.strip().lower()
    if not token:
        return False
    if len(token) < 2 and token not in ALIAS_EXCEPTIONS:
        return False
    return True


def _alias_to_pattern(alias: str) -> re.Pattern[str]:
    cleaned = alias.strip().lower()

    if " " in cleaned:
        words = [re.escape(w) for w in cleaned.split()]
        inner = r"[\s\-]+".join(words)
    else:
        inner = re.escape(cleaned)

    return re.compile(rf"(?<![a-zA-Z0-9_]){inner}(?![a-zA-Z0-9_])", re.IGNORECASE)


ALIAS_TO_SKILL: Dict[str, str] = {}
SKILL_PATTERNS: Dict[str, List[re.Pattern[str]]] = {}

for canonical, aliases in SKILL_DICTIONARY.items():
    canonical_key = canonical.lower()
    unique_aliases = {a.strip().lower() for a in aliases + [canonical] if _is_valid_alias(a)}

    SKILL_PATTERNS[canonical_key] = [_alias_to_pattern(alias) for alias in unique_aliases]
    for alias in unique_aliases:
        ALIAS_TO_SKILL[alias] = canonical_key


def normalize_skill(text: str) -> str:
    if not text:
        return ""

    token = text.strip().lower()
    if token in ALIAS_TO_SKILL:
        return ALIAS_TO_SKILL[token]

    for canonical, patterns in SKILL_PATTERNS.items():
        if any(pattern.search(token) for pattern in patterns):
            return canonical

    return token


def extract_skills_from_text(text: str) -> List[str]:
    if not text:
        return []

    normalized_text = text.lower()
    found: Set[str] = set()

    for canonical, patterns in SKILL_PATTERNS.items():
        if any(pattern.search(normalized_text) for pattern in patterns):
            found.add(canonical)

    return sorted(found)