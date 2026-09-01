import os
import requests
import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Enterprise HR Intelligence",
    page_icon="💼",
    layout="wide"
)


# ---------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------

API = os.getenv(
    "HR_API_URL",
    "http://127.0.0.1:8000"
)

KEY = os.getenv(
    "HR_API_KEY",
    ""
)

HEAD = {
    "X-API-Key": KEY
} if KEY else {}


# ---------------------------------------------------------
# APPLICATION HEADER
# ---------------------------------------------------------

st.title("💼 Enterprise Workforce Intelligence Platform")

st.caption(
    "Decision-support demo — predictions require HR governance and human review."
)


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

menu = st.sidebar.radio(
    "Module",
    [
        "Workforce Overview",
        "Employee Intelligence",
        "Skill Gap Analyzer",
        "HR Policy Search"
    ]
)


# ---------------------------------------------------------
# API HELPERS
# ---------------------------------------------------------

def get(path):
    response = requests.get(
        API + path,
        headers=HEAD,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def post(path, payload):
    response = requests.post(
        API + path,
        json=payload,
        headers=HEAD,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# WORKFORCE OVERVIEW
# =========================================================

if menu == "Workforce Overview":

    try:
        summary = get(
            "/api/v1/dashboard/summary"
        )

        a, b, c, d = st.columns(4)

        a.metric(
            "Employees",
            summary["total_employees"]
        )

        b.metric(
            "High Risk",
            summary["high_risk_employees"]
        )

        c.metric(
            "Medium Risk",
            summary["medium_risk_employees"]
        )

        d.metric(
            "Avg Satisfaction",
            summary["average_satisfaction"]
        )

        # -------------------------------------------------
        # ATTRITION BY DEPARTMENT
        # -------------------------------------------------

        st.subheader(
            "Average Attrition Risk by Department"
        )

        department_data = get(
            "/api/v1/dashboard/attrition-by-department"
        )["data"]

        dep = pd.DataFrame(department_data)

        if not dep.empty:
            st.bar_chart(
                dep.set_index("Department")[
                    "Attrition_Risk_Score"
                ]
            )
        else:
            st.info(
                "No department attrition data available."
            )

        # -------------------------------------------------
        # SKILL GAPS
        # -------------------------------------------------

        st.subheader(
            "Critical Skill Gaps"
        )

        gap_data = get(
            "/api/v1/dashboard/skill-gaps"
        )["data"]

        gaps = pd.DataFrame(gap_data).head(15)

        if not gaps.empty:
            st.dataframe(
                gaps,
                use_container_width=True
            )
        else:
            st.info(
                "No skill-gap data available."
            )

    except Exception as e:

        st.error(
            f"Unable to load workforce overview: {e}"
        )


# =========================================================
# EMPLOYEE INTELLIGENCE
# =========================================================

elif menu == "Employee Intelligence":

    eid = st.number_input(
        "Employee ID",
        min_value=1,
        step=1,
        value=1
    )

    if st.button("Load employee"):

        try:

            employee = get(
                f"/api/v1/employees/{eid}"
            )

            a, b, c = st.columns(3)

            a.metric(
                "Attrition Risk",
                f'{employee["Attrition_Risk_Score"]:.1%}'
            )

            b.metric(
                "Risk",
                employee["Risk_Category"]
            )

            c.metric(
                "Skill Match",
                f'{employee.get("Skill_Match_Pct", 0):.1f}%'
            )

            st.write(
                "**Role:**",
                employee["JobRole"]
            )

            st.write(
                "**Skill gap:**",
                employee.get(
                    "Skill_Gap",
                    "None"
                )
            )

            st.write(
                "**HR action:**",
                employee["Automated_HR_Action"]
            )

            # -------------------------------------------------
            # AGENT RECOMMENDATION PLAN
            # -------------------------------------------------

            plan = get(
                f"/api/v1/agents/employee/{eid}/plan"
            )

            st.subheader(
                "Recommended Courses"
            )

            recommended_courses = plan.get(
                "recommended_courses",
                []
            )

            if recommended_courses:

                st.dataframe(
                    pd.DataFrame(
                        recommended_courses
                    ),
                    use_container_width=True
                )

            else:

                st.info(
                    "No recommended courses available."
                )

        except Exception as e:

            st.error(
                f"Unable to load employee information: {e}"
            )


# =========================================================
# SKILL GAP ANALYZER
# =========================================================

elif menu == "Skill Gap Analyzer":

    st.subheader(
        "🎯 Skill Gap Analyzer"
    )

    st.write(
        "Compare your current skills with the skills "
        "required for the target role."
    )

    # -----------------------------------------------------
    # TARGET ROLE
    # -----------------------------------------------------

    code = st.text_input(
        "Target O*NET-SOC Code",
        "15-1252.00"
    )

    # -----------------------------------------------------
    # DEFAULT SKILLS
    # -----------------------------------------------------
    #
    # These are only DEFAULT demo values.
    # The user can completely replace them.
    #
    # -----------------------------------------------------

    skills = st.text_area(
        "Current skills",
        "Communication, Problem Solving, Git, Docker, JavaScript, SQL"
    )

    if st.button("Analyze"):

        try:

            # -------------------------------------------------
            # Convert comma-separated skills into a list
            # -------------------------------------------------

            current_skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

            if not current_skills:

                st.warning(
                    "Please enter at least one skill."
                )

                st.stop()

            # -------------------------------------------------
            # GAP ANALYSIS
            # -------------------------------------------------

            output = post(
                "/api/v1/skills/gap-analysis",
                {
                    "current_skills": current_skills,
                    "target_onet_code": code
                }
            )

            # -------------------------------------------------
            # SKILL MATCH
            # -------------------------------------------------

            match_score = output.get(
                "match_score_pct",
                0
            )

            st.metric(
                "Skill Match",
                f"{match_score:.1f}%"
            )

            # -------------------------------------------------
            # TARGET ROLE
            # -------------------------------------------------

            st.write(
                "**Target:**",
                output.get(
                    "target_title",
                    "Unknown"
                )
            )

            # -------------------------------------------------
            # MATCHED SKILLS
            # -------------------------------------------------

            matched_skills = output.get(
                "matched_skills",
                []
            )

            st.write(
                "**Matched Skills:**",
                ", ".join(matched_skills)
                if matched_skills
                else "None"
            )

            # -------------------------------------------------
            # MISSING SKILLS
            # -------------------------------------------------

            missing_skills = output.get(
                "missing_skills",
                []
            )

            st.write(
                "**Missing:**",
                ", ".join(missing_skills)
                if missing_skills
                else "None"
            )

            # -------------------------------------------------
            # RECOMMENDED LEARNING
            # -------------------------------------------------

            if missing_skills:

                st.subheader(
                    "📚 Suggested Learning"
                )

                recommendation_output = post(
                    "/api/v1/recommendations",
                    {
                        "missing_skills": missing_skills,
                        "limit": 5
                    }
                )

                recommendations = recommendation_output.get(
                    "recommendations",
                    []
                )

                if recommendations:

                    st.dataframe(
                        pd.DataFrame(
                            recommendations
                        ),
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No courses found for the identified skill gaps."
                    )

            else:

                st.success(
                    "🎉 No skill gaps identified for this target role."
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the FastAPI backend. "
                "Make sure the backend is running on port 8000."
            )

        except requests.exceptions.HTTPError as e:

            st.error(
                f"API error: {e}"
            )

        except Exception as e:

            st.error(
                f"Skill gap analysis failed: {e}"
            )


# =========================================================
# HR POLICY SEARCH
# =========================================================

else:

    st.subheader(
        "📚 HR Policy Search"
    )

    q = st.text_input(
        "Ask about an HR policy",
        "What is the training budget?"
    )

    if st.button("Search policy"):

        try:

            output = post(
                "/api/v1/policy/search",
                {
                    "query": q,
                    "top_k": 5
                }
            )

            results = output.get(
                "results",
                []
            )

            if results:

                for result in results:

                    st.info(
                        f'**{result["category"]} — '
                        f'{result["policy_id"]}**\n\n'
                        f'{result["text"]}'
                    )

            else:

                st.warning(
                    "No grounded policy passage found."
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the FastAPI backend."
            )

        except Exception as e:

            st.error(
                f"Policy search failed: {e}"
            )