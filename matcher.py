from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

#from shared_data import JOB_DESCRIPTION

JOB_DESCRIPTION = """
We are looking for a Software Engineer with experience in Python,
Java, SQL, REST APIs, Git, Linux, Docker, AWS and problem solving.
Experience with Machine Learning is a plus.
"""

# Loads once and stays in memory
model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_match_score(resume_text: str) -> float:
    # Cosine similarity
    embeddings = model.encode(
        [JOB_DESCRIPTION, resume_text],
        convert_to_numpy=True
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]
    return round(float(similarity) * 100, 2)


def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: candidate["match_score"],
        reverse=True,
    )


if __name__ == "__main__":
    from parser import extract_text_from_pdf
    resume = extract_text_from_pdf("resumes/sample1.pdf")
    score = compute_match_score(resume)
    print(f"JD Match Score: {score}%")