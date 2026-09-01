import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import PROCESSED_DIR

class PolicyService:
    def __init__(self):
        self.df=pd.read_csv(PROCESSED_DIR/"hr_policy_knowledge_base.csv")
        self.vectorizer=TfidfVectorizer(stop_words="english")
        self.matrix=self.vectorizer.fit_transform((self.df["category"].fillna("")+" "+self.df["text"].fillna("")))
    def search(self, query, top_k=3):
        q=self.vectorizer.transform([query])
        scores=cosine_similarity(q,self.matrix).ravel()
        idx=scores.argsort()[::-1][:top_k]
        return [{"policy_id":self.df.iloc[i].policy_id,"category":self.df.iloc[i].category,
                 "text":self.df.iloc[i].text,"score":round(float(scores[i]),4)} for i in idx if scores[i]>0]
