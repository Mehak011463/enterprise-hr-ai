import pandas as pd

SKILLS_PATH = "data/processed/role_skill_profiles.csv"

class SkillService:
    def __init__(self):
        try:
            self.df_roles = pd.read_csv(SKILLS_PATH)
        except Exception:
            self.df_roles = None

    def get_skill_gap(self, current_skills: list, target_onet_code: str):
        if self.df_roles is None:
            return {"error": "Skill profiles database unavailable."}
        
        role_row = self.df_roles[self.df_roles['O*NET-SOC Code'] == target_onet_code]
        if role_row.empty:
            return {"error": f"Code {target_onet_code} not found."}
        
        req_essential = role_row.iloc[0]['Required_Essential_Skills']
        req_software = role_row.iloc[0]['Required_Software_Skills']
        
        if isinstance(req_essential, str):
            req_essential = eval(req_essential) if req_essential else []
        if isinstance(req_software, str):
            req_software = eval(req_software) if req_software else []

        all_required = set([s.lower() for s in req_essential + req_software])
        current_set = set([s.lower() for s in current_skills])
        
        missing = all_required - current_set
        matched = current_set.intersection(all_required)
        
        match_score = (len(matched) / len(all_required) * 100) if all_required else 100.0
        
        return {
            "target_title": role_row.iloc[0]['Title'],
            "match_score_pct": round(match_score, 2),
            "missing_skills": list(missing)[:10]
        }