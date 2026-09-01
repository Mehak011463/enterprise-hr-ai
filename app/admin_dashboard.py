import os
import requests
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HR Admin Dashboard",
    page_icon="🔐",
    layout="wide"
)


# =========================================================
# CONFIGURATION
# =========================================================

API = os.getenv(
    "HR_API_URL",
    "http://127.0.0.1:8000"
)

API_KEY = os.getenv(
    "HR_API_KEY",
    ""
)

API_HEADERS = {
    "X-API-Key": API_KEY
} if API_KEY else {}


# =========================================================
# SESSION STATE
# =========================================================

if "admin_token" not in st.session_state:
    st.session_state.admin_token = None

if "admin_username" not in st.session_state:
    st.session_state.admin_username = None


# =========================================================
# API HELPERS
# =========================================================

def admin_headers():

    headers = dict(API_HEADERS)

    if st.session_state.admin_token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.admin_token}"
        )

    return headers


def get_api(path):

    response = requests.get(
        API + path,
        headers=admin_headers(),
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# LOGIN
# =========================================================

def login():

    st.title("🔐 HR Administrator Login")

    st.caption(
        "Secure access to the Enterprise Workforce Intelligence Platform"
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        username = st.text_input(
            "Username",
            placeholder="Enter administrator username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter administrator password"
        )

        login_button = st.button(
            "🔑 Sign In",
            use_container_width=True
        )

        if login_button:

            if not username or not password:

                st.error(
                    "Please enter username and password."
                )

                return

            try:

                response = requests.post(
                    API + "/api/v1/admin/login",
                    data={
                        "username": username,
                        "password": password
                    },
                    headers={
                        "Content-Type":
                        "application/x-www-form-urlencoded"
                    },
                    timeout=15
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.admin_token = (
                        data["access_token"]
                    )

                    st.session_state.admin_username = (
                        username
                    )

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            "Invalid credentials"
                        )
                    except Exception:
                        detail = "Invalid credentials"

                    st.error(detail)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to HR API. "
                    "Make sure FastAPI is running."
                )

            except Exception as e:

                st.error(str(e))


# =========================================================
# DASHBOARD
# =========================================================

def dashboard():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns([5, 1])

    with col1:

        st.title(
            "🏢 Enterprise HR Admin Dashboard"
        )

        st.caption(
            "Workforce intelligence, risk monitoring and "
            "HR decision support"
        )

    with col2:

        st.write("")

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.admin_token = None
            st.session_state.admin_username = None

            st.rerun()

    st.divider()


    # -----------------------------------------------------
    # ADMIN INFORMATION
    # -----------------------------------------------------

    try:

        admin = get_api(
            "/api/v1/admin/me"
        )

        st.success(
            f"Authenticated as {admin['username']} "
            f"({admin['role']})"
        )

    except Exception:

        st.error(
            "Your admin session is invalid or expired."
        )

        st.session_state.admin_token = None
        st.session_state.admin_username = None

        st.rerun()


    # -----------------------------------------------------
    # LOAD DASHBOARD DATA
    # -----------------------------------------------------

    try:

        summary = get_api(
            "/api/v1/dashboard/summary"
        )

        department_data = get_api(
            "/api/v1/dashboard/attrition-by-department"
        )

        skill_gap_data = get_api(
            "/api/v1/dashboard/skill-gaps"
        )

        recommendation_data = get_api(
            "/api/v1/dashboard/recommendations"
        )

    except requests.exceptions.HTTPError as e:

        st.error(
            f"API request failed: {e}"
        )

        return

    except Exception as e:

        st.error(
            f"Could not load dashboard data: {e}"
        )

        return


    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    st.subheader("📊 Workforce Overview")

    total_employees = summary.get(
        "total_employees",
        0
    )

    high_risk = summary.get(
        "high_risk_employees",
        0
    )

    medium_risk = summary.get(
        "medium_risk_employees",
        0
    )

    avg_satisfaction = summary.get(
        "average_satisfaction",
        0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "👥 Total Employees",
        total_employees
    )

    c2.metric(
        "🔴 High Risk",
        high_risk
    )

    c3.metric(
        "🟠 Medium Risk",
        medium_risk
    )

    c4.metric(
        "😊 Avg Satisfaction",
        avg_satisfaction
    )


    st.divider()


    # -----------------------------------------------------
    # DEPARTMENT ATTRITION
    # -----------------------------------------------------

    st.subheader(
        "📈 Attrition Risk by Department"
    )

    departments = pd.DataFrame(
        department_data.get("data", [])
    )

    if not departments.empty:

        if (
            "Department" in departments.columns
            and
            "Attrition_Risk_Score"
            in departments.columns
        ):

            chart_data = departments.set_index(
                "Department"
            )[
                "Attrition_Risk_Score"
            ]

            st.bar_chart(chart_data)

        else:

            st.dataframe(
                departments,
                use_container_width=True
            )

    else:

        st.info(
            "No department attrition data available."
        )


    # -----------------------------------------------------
    # TWO COLUMN SECTION
    # -----------------------------------------------------

    left, right = st.columns(2)


    # -----------------------------------------------------
    # SKILL GAPS
    # -----------------------------------------------------

    with left:

        st.subheader(
            "🎯 Critical Skill Gaps"
        )

        gaps = pd.DataFrame(
            skill_gap_data.get(
                "data",
                []
            )
        )

        if not gaps.empty:

            st.dataframe(
                gaps.head(15),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No skill gap data available."
            )


    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    with right:

        st.subheader(
            "📚 Recommended Learning"
        )

        recommendations = pd.DataFrame(
            recommendation_data.get(
                "data",
                []
            )
        )

        if not recommendations.empty:

            st.dataframe(
                recommendations.head(15),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No recommendation data available."
            )


    st.divider()


    # -----------------------------------------------------
    # EMPLOYEE LOOKUP
    # -----------------------------------------------------

    st.subheader(
        "👤 Employee Intelligence"
    )

    employee_id = st.number_input(
        "Employee ID",
        min_value=1,
        step=1,
        value=1
    )

    if st.button(
        "🔎 View Employee",
        use_container_width=False
    ):

        try:

            employee = get_api(
                f"/api/v1/employees/{employee_id}"
            )

            st.success(
                "Employee information loaded."
            )

            a, b, c = st.columns(3)

            risk_score = employee.get(
                "Attrition_Risk_Score",
                0
            )

            a.metric(
                "Attrition Risk",
                f"{float(risk_score):.1%}"
            )

            b.metric(
                "Risk Category",
                employee.get(
                    "Risk_Category",
                    "Unknown"
                )
            )

            skill_match = employee.get(
                "Skill_Match_Pct",
                0
            )

            c.metric(
                "Skill Match",
                f"{float(skill_match):.1f}%"
            )

            st.write(
                "**Job Role:**",
                employee.get(
                    "JobRole",
                    "Not available"
                )
            )

            st.write(
                "**Skill Gap:**",
                employee.get(
                    "Skill_Gap",
                    "None"
                )
            )

            st.write(
                "**HR Action:**",
                employee.get(
                    "Automated_HR_Action",
                    "No action available"
                )
            )

        except requests.exceptions.HTTPError:

            st.error(
                f"Employee {employee_id} was not found."
            )

        except Exception as e:

            st.error(str(e))


    st.divider()


    # -----------------------------------------------------
    # SYSTEM STATUS
    # -----------------------------------------------------

    st.subheader(
        "🖥️ System Status"
    )

    try:

        system = get_api(
            "/api/v1/admin/system-status"
        )

        a, b, c = st.columns(3)

        a.metric(
            "System",
            system.get(
                "status",
                "Unknown"
            ).upper()
        )

        b.metric(
            "Service",
            system.get(
                "service",
                "Unknown"
            )
        )

        c.metric(
            "Admin",
            system.get(
                "admin",
                "Unknown"
            )
        )

    except Exception as e:

        st.error(
            f"Unable to retrieve system status: {e}"
        )


    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    st.divider()

    st.caption(
        "⚠️ Decision-support system. "
        "AI predictions require HR governance and human review."
    )


# =========================================================
# APPLICATION
# =========================================================

if st.session_state.admin_token is None:

    login()

else:

    dashboard()