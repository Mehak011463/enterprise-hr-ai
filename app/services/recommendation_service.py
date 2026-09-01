import re
import pandas as pd
from app.config import PROCESSED_DIR


class RecommendationService:

    # Common aliases used in HR / technology skill data
    SKILL_ALIASES = {
        "aws": "amazon web services",
        "amazon web services aws software": "amazon web services",
        "amazon web services": "amazon web services",

        "ms office": "microsoft office software",
        "microsoft office": "microsoft office software",
        "microsoft office software": "microsoft office software",

        "css": "cascading style sheets css",
        "cascading style sheets": "cascading style sheets css",

        "jira": "atlassian jira",
        "atlassian jira": "atlassian jira",

        "js": "javascript",
        "javascript": "javascript",

        "ts": "typescript",
        "typescript": "typescript",

        "k8s": "kubernetes",
        "kubernetes": "kubernetes",

        "genai": "generative ai",
        "generative ai": "generative ai",

        "llm": "large language models",
        "llms": "large language models",
        "large language models": "large language models",

        "rag": "retrieval augmented generation",
        "retrieval augmented generation": "retrieval augmented generation",

        "mlops": "mlops",
        "machine learning operations": "mlops",

        "deep learning": "deep learning",
        "pytorch": "pytorch",
        "docker": "docker",
        "sql": "sql",
        "python": "python",
        "communication": "communication",
        "writing": "writing",
    }

    def __init__(self):
        catalog_path = PROCESSED_DIR / "course_catalog.csv"

        if not catalog_path.exists():
            raise FileNotFoundError(
                f"Course catalog not found: {catalog_path}"
            )

        self.courses = pd.read_csv(catalog_path)

        required_columns = {
            "course_name",
            "skill",
            "description",
            "difficulty",
            "duration_hours",
        }

        missing_columns = required_columns - set(self.courses.columns)

        if missing_columns:
            raise ValueError(
                f"course_catalog.csv is missing columns: {missing_columns}"
            )

        # Clean catalog
        self.courses["skill"] = self.courses["skill"].fillna("").astype(str)
        self.courses["description"] = (
            self.courses["description"].fillna("").astype(str)
        )
        self.courses["course_name"] = (
            self.courses["course_name"].fillna("").astype(str)
        )

        self.courses["duration_hours"] = pd.to_numeric(
            self.courses["duration_hours"],
            errors="coerce"
        ).fillna(0)

    @staticmethod
    def normalize(text):
        """
        Normalize skill/course text so matching is not dependent
        on capitalization, punctuation or small formatting differences.
        """
        text = str(text).lower().strip()

        text = text.replace("&", " and ")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def canonical_skill(self, skill):
        """
        Convert different names for the same skill into one form.
        """
        normalized = self.normalize(skill)

        return self.SKILL_ALIASES.get(
            normalized,
            normalized
        )

    def skill_tokens(self, text):
        return set(self.normalize(text).split())

    def calculate_score(self, missing_skill, course):
        """
        Calculate how strongly a course matches a missing skill.

        Higher score = better recommendation.
        """

        missing = self.canonical_skill(missing_skill)

        course_skill = self.canonical_skill(course["skill"])

        course_text = self.normalize(
            f"{course['skill']} {course['course_name']} {course['description']}"
        )

        # ---------------------------------------------------------
        # 1. Exact canonical skill match
        # ---------------------------------------------------------
        if course_skill == missing:
            return 100

        # ---------------------------------------------------------
        # 2. Skill appears directly in course text
        # ---------------------------------------------------------
        if missing in course_text:
            return 90

        # ---------------------------------------------------------
        # 3. Token overlap
        # ---------------------------------------------------------
        missing_tokens = self.skill_tokens(missing)
        course_tokens = self.skill_tokens(course_text)

        if not missing_tokens:
            return 0

        overlap = len(missing_tokens & course_tokens)

        if overlap > 0:
            return 50 + (overlap * 10)

        # ---------------------------------------------------------
        # 4. Related technology mappings
        # ---------------------------------------------------------

        related_skills = {
            "machine learning": [
                "deep learning",
                "mlops",
                "pytorch",
            ],
            "deep learning": [
                "pytorch",
                "machine learning",
            ],
            "pytorch": [
                "deep learning",
                "machine learning",
            ],
            "generative ai": [
                "retrieval augmented generation",
                "large language models",
            ],
            "large language models": [
                "generative ai",
                "retrieval augmented generation",
            ],
            "retrieval augmented generation": [
                "generative ai",
                "large language models",
            ],
            "amazon web services": [
                "cloud",
            ],
            "cloud": [
                "amazon web services",
            ],
            "docker": [
                "kubernetes",
            ],
            "kubernetes": [
                "docker",
            ],
            "communication": [
                "writing",
            ],
            "writing": [
                "communication",
            ],
        }

        related = related_skills.get(missing, [])

        for related_skill in related:
            if related_skill in course_text:
                return 40

        return 0

    def recommend(self, missing_skills, limit=5):

        # ---------------------------------------------------------
        # Clean incoming skills
        # ---------------------------------------------------------

        if missing_skills is None:
            return []

        if isinstance(missing_skills, str):
            missing_skills = [
                x.strip()
                for x in missing_skills.split(",")
                if x.strip()
            ]

        missing_skills = [
            str(skill).strip()
            for skill in missing_skills
            if str(skill).strip()
        ]

        if not missing_skills:
            return []

        recommendations = []

        # ---------------------------------------------------------
        # Score every course against every missing skill
        # ---------------------------------------------------------

        for _, course in self.courses.iterrows():

            best_score = 0
            best_skill = None

            for missing_skill in missing_skills:

                score = self.calculate_score(
                    missing_skill,
                    course
                )

                if score > best_score:
                    best_score = score
                    best_skill = missing_skill

            if best_score > 0:

                result = course.to_dict()

                # Internal ranking metadata
                result["_match_score"] = best_score
                result["_matched_skill"] = best_skill

                recommendations.append(result)

        # ---------------------------------------------------------
        # Sort:
        # 1. strongest skill match
        # 2. shorter course
        # ---------------------------------------------------------

        recommendations.sort(
            key=lambda x: (
                -x["_match_score"],
                x["duration_hours"]
            )
        )

        # ---------------------------------------------------------
        # Remove internal metadata before returning API response
        # ---------------------------------------------------------

        final_results = []

        for recommendation in recommendations[:limit]:

            recommendation = {
                key: value
                for key, value in recommendation.items()
                if not key.startswith("_")
            }

            final_results.append(recommendation)

        # ---------------------------------------------------------
        # IMPORTANT:
        # If no exact/related course exists, return the best
        # available courses rather than an empty UI.
        # ---------------------------------------------------------

        if not final_results:

            fallback = self.courses.sort_values(
                by="duration_hours"
            ).head(limit)

            final_results = fallback.to_dict(
                orient="records"
            )

        return final_results