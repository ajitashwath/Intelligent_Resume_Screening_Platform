# shared_data.py
# Maps each category to a dict of { "match_pattern": "Display Name" }.
# - match_pattern: the lowercased phrase to search for in resume text.
# - Display Name: the properly-cased name shown in results.
#
# Rules for adding new skills:
#   1. match_pattern must be lowercase.
#   2. Avoid single common English words (e.g. "go", "c", "r") — use
#      disambiguated forms like "golang", "c programming", "r language".
#   3. Keep Display Name in its canonical casing (e.g. "AWS", "Node.js").

SKILL_KEYWORDS = {
    "Programming Languages": {
        "python": "Python",
        "java": "Java",
        "c programming": "C",
        "c++": "C++",
        "c#": "C#",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "golang": "Go",
        "rust": "Rust",
        "php": "PHP",
        "ruby": "Ruby",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "scala": "Scala",
        "perl": "Perl",
        "r language": "R",
        "matlab": "MATLAB",
        "dart": "Dart",
    },

    "Web Development": {
        "html": "HTML",
        "css": "CSS",
        "react": "React",
        "angular": "Angular",
        "vue": "Vue",
        "next.js": "Next.js",
        "nuxt": "Nuxt",
        "svelte": "Svelte",
        "node.js": "Node.js",
        "express": "Express",
        "flask": "Flask",
        "django": "Django",
        "fastapi": "FastAPI",
        "spring boot": "Spring Boot",
        "ruby on rails": "Ruby on Rails",
        "graphql": "GraphQL",
        "rest api": "REST API",
        "bootstrap": "Bootstrap",
        "tailwind": "Tailwind CSS",
        "sass": "SASS",
        "webpack": "Webpack",
    },

    "Databases": {
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",
        "sqlite": "SQLite",
        "oracle": "Oracle",
        "redis": "Redis",
        "cassandra": "Cassandra",
        "elasticsearch": "Elasticsearch",
        "dynamodb": "DynamoDB",
        "firebase": "Firebase",
    },

    "Cloud & DevOps": {
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "jenkins": "Jenkins",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "linux": "Linux",
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "ci/cd": "CI/CD",
        "nginx": "Nginx",
        "heroku": "Heroku",
        "vercel": "Vercel",
    },

    "Data Science & AI": {
        "numpy": "NumPy",
        "pandas": "Pandas",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "scikit-learn": "Scikit-learn",
        "tensorflow": "TensorFlow",
        "keras": "Keras",
        "pytorch": "PyTorch",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "natural language processing": "NLP",
        "nlp": "NLP",
        "computer vision": "Computer Vision",
        "data analysis": "Data Analysis",
        "data visualization": "Data Visualization",
        "statistics": "Statistics",
        "opencv": "OpenCV",
        "hugging face": "Hugging Face",
        "langchain": "LangChain",
        "llm": "LLM",
    },

    "Analytics & Tools": {
        "power bi": "Power BI",
        "tableau": "Tableau",
        "excel": "Excel",
        "looker": "Looker",
        "google analytics": "Google Analytics",
        "jupyter": "Jupyter",
    },

    "Soft Skills & Methodologies": {
        "agile": "Agile",
        "scrum": "Scrum",
        "jira": "Jira",
        "kanban": "Kanban",
        "leadership": "Leadership",
        "communication": "Communication",
        "problem solving": "Problem Solving",
        "team management": "Team Management",
        "project management": "Project Management",
    },
}