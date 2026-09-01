import ast
import re
import pandas as pd
from difflib import SequenceMatcher
from app.config import PROCESSED_DIR


class SkillService:
    def __init__(self):
        self.roles = pd.read_csv(PROCESSED_DIR / "role_skill_profiles.csv")
        self.employee_skills = pd.read_csv(
            PROCESSED_DIR / "employee_skills_demo.csv"
        )

    @staticmethod
    def _parse(value):
        """
        Convert stored skill values into a Python list.
        Supports:
        - Python lists
        - string representations of lists
        - comma-separated strings
        - single values
        """
        if isinstance(value, list):
            return value

        if value is None:
            return []

        try:
            if pd.isna(value):
                return []
        except (TypeError, ValueError):
            pass

        value = str(value).strip()

        if not value:
            return []

        # Try Python-list format first
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass

        # Support comma-separated values
        if "," in value:
            return [x.strip() for x in value.split(",") if x.strip()]

        return [value]

    @staticmethod
    def _norm(s):
        """
        Normalize skill names so small formatting differences
        don't prevent a match.
        """
        s = str(s).strip().lower()

        # Convert &, /, -, _, punctuation into spaces
        s = re.sub(r"[/&_\-]+", " ", s)
        s = re.sub(r"[^a-z0-9+#. ]+", " ", s)

        # Normalize common technology naming
        replacements = {
            "c sharp": "c#",
            "c plus plus": "c++",
            "node js": "nodejs",
            "react js": "react",
            "angular js": "angular",
            "amazon web services": "aws",
            "google cloud platform": "gcp",
            "microsoft sql server": "sql server",
            "structured query language": "sql",
        }

        for old, new in replacements.items():
            s = s.replace(old, new)

        return " ".join(s.split())

    @classmethod
    def _is_match(cls, current_skill, required_skill):
        """
        Determine whether an employee skill satisfies a required skill.

        Matching levels:
        1. Exact normalized match
        2. Known abbreviation / technology equivalence
        3. Very close textual match
        """

        current = cls._norm(current_skill)
        required = cls._norm(required_skill)

        if not current or not required:
            return False

        # Exact match
        if current == required:
            return True

        # Explicit technology equivalences
        aliases = {
            "aws": {
                "aws",
                "amazon web services",
                "amazon web services aws software",
            },
            "sql": {
                "sql",
                "sql server",
                "microsoft sql server",
                "structured query language",
            },
            "javascript": {
                "javascript",
                "js",
            },
            "typescript": {
                "typescript",
                "ts",
            },
            "python": {
                "python",
                "python programming",
            },
            "docker": {
                "docker",
                "docker containerization",
            },
            "git": {
                "git",
                "git version control",
            },
            "github": {
                "github",
                "git hub",
            },
            "c#": {
                "c#",
                "c sharp",
            },
            "c++": {
                "c++",
                "c plus plus",
            },
        }

        for group in aliases.values():
            normalized_group = {cls._norm(x) for x in group}

            if current in normalized_group and required in normalized_group:
                return True

        # If one skill contains the other, only allow this for
        # reasonably specific multi-word skills.
        if len(current.split()) >= 2 and len(required.split()) >= 2:
            if current in required or required in current:
                return True

        # Very close spelling differences
        similarity = SequenceMatcher(None, current, required).ratio()

        if similarity >= 0.92:
            return True

        return False

    def get_skill_gap(self, current_skills, target_onet_code):

        rows = self.roles[
            self.roles["O*NET-SOC Code"].astype(str).str.strip()
            == str(target_onet_code).strip()
        ]

        if rows.empty:
            raise ValueError(
                f"O*NET code {target_onet_code} not found"
            )

        row = rows.iloc[0]

        # Get required skills from both columns
        required = (
            self._parse(row["Required_Essential_Skills"])
            + self._parse(row["Required_Software_Skills"])
        )

        # Remove duplicates while preserving original display names
        required_unique = {}

        for skill in required:
            normalized = self._norm(skill)

            if normalized:
                required_unique[normalized] = str(skill).strip()

        required_skills = list(required_unique.values())

        # Parse employee skills robustly
        current = []

        for skill in self._parse(current_skills):
            skill = str(skill).strip()

            if skill:
                current.append(skill)

        # Remove duplicate employee skills
        current_unique = {}

        for skill in current:
            current_unique[self._norm(skill)] = skill

        current_skills_clean = list(current_unique.values())

        matched = []
        missing = []

        # Compare every required skill against employee skills
        for required_skill in required_skills:

            found = any(
                self._is_match(current_skill, required_skill)
                for current_skill in current_skills_clean
            )

            if found:
                matched.append(required_skill)
            else:
                missing.append(required_skill)

        # Calculate percentage correctly
        if required_skills:
            score = round(
                (len(matched) / len(required_skills)) * 100,
                2
            )
        else:
            score = 100.0

        return {
            "target_onet_code": str(target_onet_code),
            "target_title": str(row["Title"]),
            "match_score_pct": score,
            "matched_count": len(matched),
            "missing_count": len(missing),
            "matched_skills": matched[:25],
            "missing_skills": missing[:25],
        }

    def employee_gap(self, employee_id):

        emp = pd.read_csv(
            PROCESSED_DIR / "employee_attrition_processed.csv"
        )

        rows = emp[emp.EmployeeID == employee_id]

        if rows.empty:
            raise ValueError("Employee not found")

        skills = self.employee_skills[
            self.employee_skills.EmployeeID == employee_id
        ]["CurrentSkill"].tolist()

        codes = self.employee_skills[
            self.employee_skills.EmployeeID == employee_id
        ]["TargetRoleONET"].tolist()

        code = codes[0] if codes else None

        if code:
            return self.get_skill_gap(skills, code)

        return {
            "current_skills": skills,
            "missing_skills": [],
            "match_score_pct": 100.0,
            "matched_count": 0,
            "missing_count": 0,
            "matched_skills": [],
        }