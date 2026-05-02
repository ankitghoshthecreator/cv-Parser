from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class JobMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def get_top_matches(self, student_cv: str, jobs: list, top_n: int = 20):
        """
        student_cv: string of extracted CV text
        jobs: list of Job objects from database
        """
        if not jobs:
            return []

        # Prepare corpus: CV text + job descriptions
        job_texts = [f"{j.title} {j.category} {j.description} {j.required_skills}" for j in jobs]
        corpus = [student_cv] + job_texts

        # Vectorize
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # Calculate cosine similarity between CV (index 0) and all jobs
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        # Combine with job data
        results = []
        for idx, score in enumerate(similarities):
            results.append({
                "job_id": jobs[idx].id,
                "title": jobs[idx].title,
                "category": jobs[idx].category,
                "score": round(float(score) * 100, 2)
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_n]
