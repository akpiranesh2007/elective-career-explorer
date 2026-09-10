import streamlit as st
import pandas as pd
from pathlib import Path
from itertools import combinations

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Elective Career Explorer",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# BASIC STYLING
# ============================================================

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
    }

    .title {
        font-size: 38px;
        font-weight: 700;
        color: #17365D;
    }

    .subtitle {
        font-size: 18px;
        color: #555555;
    }

    .card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 12px;
    }

    .good {
        background: #eaf7ea;
        padding: 12px;
        border-radius: 8px;
    }

    .warning {
        background: #fff5d6;
        padding: 12px;
        border-radius: 8px;
    }

    .danger {
        background: #ffeaea;
        padding: 12px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    courses = pd.read_csv(DATA_DIR / "courses.csv")
    prerequisites = pd.read_csv(DATA_DIR / "prerequisites.csv")
    schedules = pd.read_csv(DATA_DIR / "schedules.csv")
    careers = pd.read_csv(DATA_DIR / "career_pathways.csv")
    outcomes = pd.read_csv(DATA_DIR / "course_outcomes.csv")
    students = pd.read_csv(DATA_DIR / "students.csv")

    return courses, prerequisites, schedules, careers, outcomes, students


try:
    courses, prerequisites, schedules, careers, outcomes, students = load_data()

except Exception as e:
    st.error("Unable to load the dataset files.")
    st.code(str(e))
    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_completed_courses(student_id):
    row = students[students["student_id"] == student_id]

    if row.empty:
        return []

    value = row.iloc[0]["completed_courses"]

    if pd.isna(value):
        return []

    return [x.strip() for x in str(value).split(",") if x.strip()]


def get_student_skills(student_id):
    row = students[students["student_id"] == student_id]

    if row.empty:
        return []

    value = row.iloc[0]["skills"]

    if pd.isna(value):
        return []

    return [x.strip().lower() for x in str(value).split(",") if x.strip()]


def check_single_prerequisite(prerequisite, completed, skills):

    prerequisite = str(prerequisite).strip()

    if prerequisite.lower() == "none":
        return True

    # Direct course prerequisite
    if prerequisite in completed:
        return True

    # Foundational prerequisite interpretation
    p = prerequisite.lower()

    if "programming" in p:
        return "c01" in [x.lower() for x in completed] or "python" in skills or "java" in skills

    if "mathematics" in p or "math" in p:
        return (
            "mathematics" in skills
            or "statistics" in skills
            or "c07" in [x.lower() for x in completed]
        )

    if "database" in p:
        return (
            "sql" in skills
            or "database" in skills
            or "c04" in [x.lower() for x in completed]
        )

    if "networking" in p or "network" in p:
        return (
            "networking" in skills
            or "computer networks" in skills
            or "c12" in [x.lower() for x in completed]
        )

    # Unknown prerequisite = unsafe to assume
    return False


def check_prerequisites(course_id, completed, skills):

    rows = prerequisites[
        prerequisites["course_id"] == course_id
    ]

    if rows.empty:
        return True, []

    missing = []

    for _, row in rows.iterrows():

        prereq = str(row["prerequisite"]).strip()

        if not check_single_prerequisite(
            prereq,
            completed,
            skills
        ):
            missing.append(prereq)

    return len(missing) == 0, missing


def get_schedule(course_id):

    rows = schedules[
        schedules["course_id"] == course_id
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


def schedules_conflict(course_a, course_b):

    a = get_schedule(course_a)
    b = get_schedule(course_b)

    if a is None or b is None:
        return False

    if a["day"] != b["day"]:
        return False

    start_a = str(a["start_time"])
    end_a = str(a["end_time"])

    start_b = str(b["start_time"])
    end_b = str(b["end_time"])

    return (
        start_a < end_b
        and start_b < end_a
    )


def find_schedule_conflicts(course_list):

    conflicts = []

    for a, b in combinations(course_list, 2):

        if schedules_conflict(a, b):

            name_a = courses.loc[
                courses["course_id"] == a,
                "course_name"
            ].iloc[0]

            name_b = courses.loc[
                courses["course_id"] == b,
                "course_name"
            ].iloc[0]

            conflicts.append(
                f"{name_a} ↔ {name_b}"
            )

    return conflicts


def career_score(course_id, career_goal):

    rows = careers[
        (careers["course_id"] == course_id)
        &
        (careers["career_goal"] == career_goal)
    ]

    if rows.empty:
        return 0

    return float(rows.iloc[0]["match_score"])


def get_outcome(course_id):

    rows = outcomes[
        outcomes["course_id"] == course_id
    ]

    if rows.empty:
        return "Learning outcome information unavailable."

    return str(rows.iloc[0]["learning_outcome"])


def get_skills(course_id):

    rows = outcomes[
        outcomes["course_id"] == course_id
    ]

    if rows.empty:
        return "Not available"

    return str(rows.iloc[0]["skills"])


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def generate_recommendations(student_id, career_goal):

    completed = get_completed_courses(student_id)
    skills = get_student_skills(student_id)

    results = []

    for _, course in courses.iterrows():

        course_id = course["course_id"]

        # Do not recommend already completed courses
        if course_id in completed:
            continue

        prerequisite_ok, missing = check_prerequisites(
            course_id,
            completed,
            skills
        )

        career_match = career_score(
            course_id,
            career_goal
        )

        if career_match == 0:
            continue

        # Score components
        prerequisite_score = 100 if prerequisite_ok else 0
        career_component = career_match * 20

        # Learning outcome score
        outcome = get_outcome(course_id)

        learning_score = 100 if outcome else 0

        # Overall transparent score
        total_score = (
            prerequisite_score * 0.40
            + career_component * 0.30
            + learning_score * 0.20
            + 100 * 0.10
        )

        results.append({
            "course_id": course_id,
            "course_name": course["course_name"],
            "difficulty": course["difficulty"],
            "credits": course["credits"],
            "career_match": career_match,
            "prerequisite_ok": prerequisite_ok,
            "missing_prerequisites": ", ".join(missing),
            "score": round(total_score, 1),
            "outcome": outcome,
            "skills": get_skills(course_id)
        })

    result_df = pd.DataFrame(results)

    if not result_df.empty:
        result_df = result_df.sort_values(
            by=["prerequisite_ok", "score"],
            ascending=[False, False]
        )

    return result_df


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🎓 Elective Career Explorer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'A responsible decision-support prototype for choosing electives '
    'based on prerequisites, schedules and career pathways.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Student Profile")

student_ids = students["student_id"].tolist()

student_id = st.sidebar.selectbox(
    "Select Student",
    student_ids
)

student_row = students[
    students["student_id"] == student_id
].iloc[0]

career_options = sorted(
    careers["career_goal"].unique().tolist()
)

default_career = student_row["career_goal"]

if default_career in career_options:
    default_index = career_options.index(default_career)
else:
    default_index = 0

career_goal = st.sidebar.selectbox(
    "Career Goal",
    career_options,
    index=default_index
)

completed = get_completed_courses(student_id)
skills = get_student_skills(student_id)

st.sidebar.write("### Completed Courses")

if completed:
    st.sidebar.write(", ".join(completed))
else:
    st.sidebar.write("No completed courses recorded.")

st.sidebar.write("### Skills")

if skills:
    st.sidebar.write(", ".join(skills))
else:
    st.sidebar.write("No skills recorded.")


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Recommendations",
    "🔍 Prerequisite Checker",
    "🕒 Schedule Checker",
    "📊 Evaluation",
    "🛡️ Responsible AI"
])


# ============================================================
# TAB 1 - RECOMMENDATIONS
# ============================================================

with tab1:

    st.header("Recommended Electives")

    recommendations = generate_recommendations(
        student_id,
        career_goal
    )

    if recommendations.empty:

        st.warning(
            "No suitable recommendation was found for this profile."
        )

    else:

        st.write(
            "The system checks career relevance and prerequisites "
            "before presenting recommendations."
        )

        for _, row in recommendations.head(8).iterrows():

            with st.container():

                st.markdown(
                    f"### {row['course_id']} — {row['course_name']}"
                )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Recommendation Score",
                    f"{row['score']:.1f}"
                )

                col2.metric(
                    "Career Match",
                    f"{row['career_match']}/5"
                )

                col3.metric(
                    "Difficulty",
                    row["difficulty"]
                )

                col4.metric(
                    "Credits",
                    row["credits"]
                )

                if row["prerequisite_ok"]:

                    st.success(
                        "✅ Prerequisites satisfied"
                    )

                else:

                    st.warning(
                        "⚠️ Missing prerequisite: "
                        + row["missing_prerequisites"]
                    )

                st.write(
                    "**Why this course?** "
                    + str(row["outcome"])
                )

                st.write(
                    "**Skills gained:** "
                    + str(row["skills"])
                )

                st.divider()


# ============================================================
# TAB 2 - PREREQUISITE CHECKER
# ============================================================

with tab2:

    st.header("Prerequisite Checker")

    selected_course = st.selectbox(
        "Choose a course",
        courses["course_id"].tolist(),
        format_func=lambda x:
            f"{x} - "
            + courses.loc[
                courses["course_id"] == x,
                "course_name"
            ].iloc[0]
    )

    ok, missing = check_prerequisites(
        selected_course,
        completed,
        skills
    )

    if ok:

        st.success(
            "✅ The student satisfies the known prerequisites."
        )

    else:

        st.error(
            "❌ The student should not directly select this course."
        )

        st.write("Missing prerequisite(s):")

        for item in missing:
            st.write(f"- {item}")

        st.info(
            "Human advisor review is recommended when prerequisite "
            "information is incomplete or uncertain."
        )


# ============================================================
# TAB 3 - SCHEDULE CHECKER
# ============================================================

with tab3:

    st.header("Schedule Conflict Checker")

    selected_courses = st.multiselect(
        "Select electives to test",
        courses["course_id"].tolist(),
        format_func=lambda x:
            f"{x} - "
            + courses.loc[
                courses["course_id"] == x,
                "course_name"
            ].iloc[0]
    )

    if selected_courses:

        conflicts = find_schedule_conflicts(
            selected_courses
        )

        if conflicts:

            st.error(
                f"❌ {len(conflicts)} schedule conflict(s) found."
            )

            for conflict in conflicts:
                st.write(f"- {conflict}")

        else:

            st.success(
                "✅ No schedule conflicts detected."
            )

        st.subheader("Selected Schedule")

        schedule_view = schedules[
            schedules["course_id"].isin(selected_courses)
        ].copy()

        st.dataframe(
            schedule_view,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Select at least two courses to test schedule conflicts."
        )


# ============================================================
# TAB 4 - EVALUATION
# ============================================================

with tab4:

    st.header("Prototype Evaluation")

    st.write(
        "The prototype is compared with a simple baseline "
        "that considers only career matching."
    )

    total_cases = 0
    baseline_conflicts = 0
    prototype_conflicts = 0
    valid_prototype_choices = 0
    total_prototype_choices = 0

    evaluation_rows = []

    for _, student in students.iterrows():

        sid = student["student_id"]
        goal = student["career_goal"]

        student_completed = get_completed_courses(sid)
        student_skills = get_student_skills(sid)

        # -------------------------------
        # BASELINE
        # Career-only recommendation
        # -------------------------------

        baseline = careers[
            careers["career_goal"] == goal
        ]

        baseline_courses = [
            x for x in baseline["course_id"].tolist()
            if x not in student_completed
        ]

        baseline_conflicts_list = find_schedule_conflicts(
            baseline_courses
        )

        baseline_prereq_conflicts = 0

        for cid in baseline_courses:

            ok, _ = check_prerequisites(
                cid,
                student_completed,
                student_skills
            )

            if not ok:
                baseline_prereq_conflicts += 1

        # -------------------------------
        # PROTOTYPE
        # -------------------------------

        proto = generate_recommendations(
            sid,
            goal
        )

        proto_courses = proto[
            proto["prerequisite_ok"] == True
        ]["course_id"].tolist()

        proto_conflicts_list = find_schedule_conflicts(
            proto_courses
        )

        proto_prereq_conflicts = 0

        for cid in proto_courses:

            ok, _ = check_prerequisites(
                cid,
                student_completed,
                student_skills
            )

            if not ok:
                proto_prereq_conflicts += 1

        total_cases += 1

        baseline_conflicts += (
            baseline_prereq_conflicts
            + len(baseline_conflicts_list)
        )

        prototype_conflicts += (
            proto_prereq_conflicts
            + len(proto_conflicts_list)
        )

        total_prototype_choices += len(proto)

        valid_prototype_choices += len(proto_courses)

        evaluation_rows.append({
            "Student": sid,
            "Career Goal": goal,
            "Baseline Prerequisite Conflicts":
                baseline_prereq_conflicts,
            "Baseline Schedule Conflicts":
                len(baseline_conflicts_list),
            "Prototype Prerequisite Conflicts":
                proto_prereq_conflicts,
            "Prototype Schedule Conflicts":
                len(proto_conflicts_list)
        })

    if baseline_conflicts > 0:

        conflict_reduction = (
            (baseline_conflicts - prototype_conflicts)
            / baseline_conflicts
        ) * 100

    else:

        conflict_reduction = 100.0

    if total_prototype_choices > 0:

        choice_quality = (
            valid_prototype_choices
            / total_prototype_choices
        ) * 100

    else:

        choice_quality = 0

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Student Cases Tested",
        total_cases
    )

    col2.metric(
        "Course Choice Quality",
        f"{choice_quality:.1f}%"
    )

    col3.metric(
        "Conflict Reduction",
        f"{conflict_reduction:.1f}%"
    )

    st.subheader("Baseline vs Prototype")

    comparison = pd.DataFrame({
        "Metric": [
            "Prerequisite/Schedule Conflicts",
            "Valid Prototype Choices"
        ],
        "Baseline": [
            baseline_conflicts,
            "-"
        ],
        "Prototype": [
            prototype_conflicts,
            valid_prototype_choices
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Detailed Test Results")

    st.dataframe(
        pd.DataFrame(evaluation_rows),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "These values are calculated from the synthetic dataset "
        "included in this prototype."
    )

    st.subheader("Target")

    st.write(
        "Target: at least 85% valid course-choice quality and "
        "a substantial reduction in prerequisite/schedule conflicts."
    )


# ============================================================
# TAB 5 - RESPONSIBLE AI
# ============================================================

with tab5:

    st.header("Responsible AI & Maintenance")

    st.subheader("1. Human decision support")

    st.write(
        "The system provides recommendations but does not automatically "
        "enroll a student in a course. Final decisions remain with the "
        "student and academic advisor."
    )

    st.subheader("2. Explainability")

    st.write(
        "Each recommendation shows its career match, prerequisite status, "
        "learning outcome, skills and recommendation score."
    )

    st.subheader("3. Privacy")

    st.write(
        "The prototype uses synthetic student data. Real sensitive "
        "information should not be required for elective recommendations."
    )

    st.subheader("4. Fairness")

    st.write(
        "The system should not assume that a student is suitable for a "
        "course based on sensitive characteristics or stereotypes."
    )

    st.subheader("5. Human override")

    st.write(
        "An advisor can review or override a recommendation when the "
        "dataset is incomplete or the student's situation is different "
        "from the available rules."
    )

    st.subheader("6. Maintenance")

    st.write(
        "Course prerequisites, schedules, career pathways and learning "
        "outcomes must be reviewed whenever the academic curriculum changes."
    )

    st.subheader("7. Environmental consideration")

    st.write(
        "This prototype uses a lightweight rule-based approach rather than "
        "training a large machine-learning model, reducing unnecessary "
        "computational requirements."
    )

    st.subheader("8. Stakeholder Trade-off")

    st.write(
        "**Student:** wants electives that support an interesting career."
    )

    st.write(
        "**School/Advisor:** wants students to satisfy prerequisites and "
        "avoid timetable conflicts."
    )

    st.write(
        "The prototype makes this trade-off visible. For example, a student "
        "may want Machine Learning for an AI career, but the system can show "
        "that Statistics or programming prerequisites should be completed first."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Elective Career Explorer | Field-Ready Prototype | "
    "Responsible decision-support system"
)
