import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
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
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #123B63;
    }

    .subtitle {
        font-size: 18px;
        color: #555;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 650;
        color: #123B63;
        margin-top: 20px;
    }

    .good-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #EAF7EE;
        border-left: 5px solid #2E8B57;
        margin: 10px 0;
    }

    .warning-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #FFF7E6;
        border-left: 5px solid #E6A700;
        margin: 10px 0;
    }

    .danger-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #FDECEC;
        border-left: 5px solid #D9534F;
        margin: 10px 0;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #EEF5FC;
        border-left: 5px solid #3973AC;
        margin: 10px 0;
    }

    div[data-testid="stMetricValue"] {
        color: #123B63;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# LOAD CSV SAFELY
# ============================================================

@st.cache_data
def load_csv(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing file: {file_path}"
        )

    # Try normal CSV loading first
    try:
        return pd.read_csv(
            file_path,
            skipinitialspace=True
        )
    except Exception:
        # Fallback for imperfect CSV rows
        return pd.read_csv(
            file_path,
            skipinitialspace=True,
            engine="python",
            on_bad_lines="warn"
        )


@st.cache_data
def load_all_data():

    courses = load_csv("courses.csv")
    prerequisites = load_csv("prerequisites.csv")
    schedules = load_csv("schedules.csv")
    career_pathways = load_csv("career_pathways.csv")
    course_outcomes = load_csv("course_outcomes.csv")
    students = load_csv("students.csv")

    return (
        courses,
        prerequisites,
        schedules,
        career_pathways,
        course_outcomes,
        students
    )


# ============================================================
# TRY LOADING DATA
# ============================================================

try:

    (
        courses,
        prerequisites,
        schedules,
        career_pathways,
        course_outcomes,
        students
    ) = load_all_data()

    DATA_LOADED = True

except Exception as e:

    DATA_LOADED = False

    st.error("Unable to load the dataset files.")

    st.code(str(e))

    st.info(
        "Please make sure all six CSV files are inside the data folder."
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

def clean_dataframe(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


courses = clean_dataframe(courses)
prerequisites = clean_dataframe(prerequisites)
schedules = clean_dataframe(schedules)
career_pathways = clean_dataframe(career_pathways)
course_outcomes = clean_dataframe(course_outcomes)
students = clean_dataframe(students)


# ============================================================
# NORMALIZE IMPORTANT COLUMNS
# ============================================================

for df in [
    courses,
    prerequisites,
    schedules,
    career_pathways,
    course_outcomes,
    students
]:

    for column in df.columns:

        if column.endswith("_id") or column == "course_id":

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_course_name(course_id):

    result = courses[
        courses["course_id"] == course_id
    ]

    if result.empty:
        return course_id

    return result.iloc[0]["course_name"]


def get_course_info(course_id):

    result = courses[
        courses["course_id"] == course_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


def get_prerequisites(course_id):

    result = prerequisites[
        prerequisites["course_id"] == course_id
    ]

    if result.empty:
        return []

    values = []

    for value in result["prerequisite"].tolist():

        value = str(value).strip()

        if value.lower() in [
            "",
            "none",
            "nan",
            "no prerequisite",
            "no prerequisites"
        ]:
            continue

        values.append(value)

    return values


def get_schedule(course_id):

    result = schedules[
        schedules["course_id"] == course_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


def get_completed_courses(student):

    text = str(
        student.get("completed_courses", "")
    )

    if not text or text.lower() == "nan":
        return []

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def get_course_outcome(course_id):

    result = course_outcomes[
        course_outcomes["course_id"] == course_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


def get_career_score(career_goal, course_id):

    result = career_pathways[
        (career_pathways["career_goal"] == career_goal)
        &
        (career_pathways["course_id"] == course_id)
    ]

    if result.empty:
        return 0

    try:
        return float(result.iloc[0]["match_score"])
    except Exception:
        return 0


# ============================================================
# PREREQUISITE CHECK
# ============================================================

def prerequisite_check(course_id, completed_courses):

    required = get_prerequisites(course_id)

    if len(required) == 0:

        return {
            "valid": True,
            "missing": [],
            "required": []
        }

    missing = []

    for prerequisite in required:

        prerequisite = prerequisite.strip()

        # Direct course ID
        if prerequisite in courses["course_id"].values:

            if prerequisite not in completed_courses:
                missing.append(
                    get_course_name(prerequisite)
                )

        # Concept/name based prerequisite
        else:

            prerequisite_lower = prerequisite.lower()

            completed_names = []

            for cid in completed_courses:

                name = get_course_name(cid)

                completed_names.append(
                    name.lower()
                )

            found = any(
                prerequisite_lower in name
                or name in prerequisite_lower
                for name in completed_names
            )

            # Foundational prerequisites that are not represented
            # as course IDs are treated as advisor-check items.
            if not found:

                missing.append(prerequisite)

    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "required": required
    }


# ============================================================
# SCHEDULE CONFLICT CHECK
# ============================================================

def schedule_conflict(course_a, course_b):

    a = get_schedule(course_a)
    b = get_schedule(course_b)

    if a is None or b is None:
        return False

    if str(a["day"]).strip() != str(b["day"]).strip():
        return False

    try:

        a_start = datetime.strptime(
            str(a["start_time"]),
            "%H:%M"
        )

        a_end = datetime.strptime(
            str(a["end_time"]),
            "%H:%M"
        )

        b_start = datetime.strptime(
            str(b["start_time"]),
            "%H:%M"
        )

        b_end = datetime.strptime(
            str(b["end_time"]),
            "%H:%M"
        )

        return (
            a_start < b_end
            and
            b_start < a_end
        )

    except Exception:
        return False


def check_schedule(course_id, selected_courses):

    conflicts = []

    for selected in selected_courses:

        if selected == course_id:
            continue

        if schedule_conflict(course_id, selected):

            conflicts.append(
                get_course_name(selected)
            )

    return conflicts


# ============================================================
# CAREER RECOMMENDATION
# ============================================================

def calculate_recommendation_score(
    course_id,
    career_goal,
    completed_courses,
    selected_courses
):

    # ---------------------------------------------
    # 1. Prerequisite score - 40%
    # ---------------------------------------------

    prerequisite_result = prerequisite_check(
        course_id,
        completed_courses
    )

    prerequisite_score = (
        100
        if prerequisite_result["valid"]
        else 0
    )

    # ---------------------------------------------
    # 2. Career match - 30%
    # ---------------------------------------------

    career_match = get_career_score(
        career_goal,
        course_id
    )

    career_score = career_match * 20

    # match_score is 1-5
    # 5 becomes 100
    career_score = min(
        career_match / 5 * 100,
        100
    )

    # ---------------------------------------------
    # 3. Learning outcome - 20%
    # ---------------------------------------------

    outcome = get_course_outcome(course_id)

    if outcome is not None:
        outcome_score = 100
    else:
        outcome_score = 0

    # ---------------------------------------------
    # 4. Schedule compatibility - 10%
    # ---------------------------------------------

    conflicts = check_schedule(
        course_id,
        selected_courses
    )

    schedule_score = (
        100
        if len(conflicts) == 0
        else 0
    )

    # ---------------------------------------------
    # Final weighted score
    # ---------------------------------------------

    final_score = (
        prerequisite_score * 0.40
        +
        career_score * 0.30
        +
        outcome_score * 0.20
        +
        schedule_score * 0.10
    )

    return round(final_score, 1)


# ============================================================
# RECOMMEND COURSES
# ============================================================

def recommend_courses(
    career_goal,
    completed_courses,
    selected_courses=None
):

    if selected_courses is None:
        selected_courses = []

    recommendations = []

    for _, course in courses.iterrows():

        course_id = course["course_id"]

        # Do not recommend completed courses
        if course_id in completed_courses:
            continue

        prereq = prerequisite_check(
            course_id,
            completed_courses
        )

        conflicts = check_schedule(
            course_id,
            selected_courses
        )

        career_match = get_career_score(
            career_goal,
            course_id
        )

        score = calculate_recommendation_score(
            course_id,
            career_goal,
            completed_courses,
            selected_courses
        )

        outcome = get_course_outcome(course_id)

        if outcome is not None:

            learning_outcome = outcome[
                "learning_outcome"
            ]

            skills = outcome[
                "skills"
            ]

        else:

            learning_outcome = "Not available"
            skills = "Not available"

        if prereq["valid"] and len(conflicts) == 0:

            status = "Recommended"

        elif not prereq["valid"]:

            status = "Prerequisite issue"

        elif len(conflicts) > 0:

            status = "Schedule conflict"

        else:

            status = "Review"

        recommendations.append({

            "Course ID": course_id,

            "Course": course["course_name"],

            "Difficulty": course["difficulty"],

            "Credits": course["credits"],

            "Career Match": career_match,

            "Score": score,

            "Status": status,

            "Prerequisites": ", ".join(
                prereq["required"]
            )
            if prereq["required"]
            else "None",

            "Missing Prerequisites": ", ".join(
                prereq["missing"]
            )
            if prereq["missing"]
            else "None",

            "Schedule Conflicts": ", ".join(
                conflicts
            )
            if conflicts
            else "None",

            "Learning Outcome": learning_outcome,

            "Skills": skills
        })

    result = pd.DataFrame(recommendations)

    if not result.empty:

        result = result.sort_values(
            by="Score",
            ascending=False
        )

    return result


# ============================================================
# BASELINE RECOMMENDER
# ============================================================

def baseline_recommendation(
    career_goal,
    completed_courses
):

    result = []

    for _, course in courses.iterrows():

        course_id = course["course_id"]

        if course_id in completed_courses:
            continue

        career_match = get_career_score(
            career_goal,
            course_id
        )

        if career_match > 0:

            result.append({

                "course_id": course_id,

                "course_name": course[
                    "course_name"
                ],

                "career_match": career_match
            })

    result = sorted(
        result,
        key=lambda x: x["career_match"],
        reverse=True
    )

    return result


# ============================================================
# EVALUATION
# ============================================================

def evaluate_prototype():

    total_baseline_conflicts = 0
    total_prototype_conflicts = 0

    total_valid_choices = 0
    total_choices = 0

    details = []

    for _, student in students.iterrows():

        career_goal = student[
            "career_goal"
        ]

        completed = get_completed_courses(
            student
        )

        # -------------------------------
        # Baseline
        # -------------------------------

        baseline = baseline_recommendation(
            career_goal,
            completed
        )

        baseline_conflicts = 0

        for item in baseline:

            cid = item["course_id"]

            prereq = prerequisite_check(
                cid,
                completed
            )

            if not prereq["valid"]:
                baseline_conflicts += 1

        total_baseline_conflicts += (
            baseline_conflicts
        )

        # -------------------------------
        # Prototype
        # -------------------------------

        prototype = recommend_courses(
            career_goal,
            completed
        )

        prototype_conflicts = 0

        valid_choices = 0

        for _, row in prototype.head(5).iterrows():

            total_choices += 1

            if row["Status"] == "Recommended":

                valid_choices += 1
                total_valid_choices += 1

            if (
                row["Status"] == "Prerequisite issue"
                or
                row["Status"] == "Schedule conflict"
            ):

                prototype_conflicts += 1

        total_prototype_conflicts += (
            prototype_conflicts
        )

        details.append({

            "Student": student["student_id"],

            "Career Goal": career_goal,

            "Baseline Conflicts":
                baseline_conflicts,

            "Prototype Conflicts":
                prototype_conflicts,

            "Valid Prototype Choices":
                valid_choices
        })

    if total_baseline_conflicts > 0:

        conflict_reduction = (
            (
                total_baseline_conflicts
                -
                total_prototype_conflicts
            )
            /
            total_baseline_conflicts
        ) * 100

    else:

        conflict_reduction = 100

    if total_choices > 0:

        choice_quality = (
            total_valid_choices
            /
            total_choices
        ) * 100

    else:

        choice_quality = 0

    return {

        "students": len(students),

        "baseline_conflicts":
            total_baseline_conflicts,

        "prototype_conflicts":
            total_prototype_conflicts,

        "conflict_reduction":
            round(conflict_reduction, 1),

        "choice_quality":
            round(choice_quality, 1),

        "details":
            pd.DataFrame(details)
    }


evaluation = evaluate_prototype()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎓 Elective Career Explorer</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    A responsible decision-support prototype for choosing electives
    based on prerequisites, schedules and career pathways.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SIDEBAR - STUDENT PROFILE
# ============================================================

st.sidebar.title("Student Profile")

student_ids = students[
    "student_id"
].tolist()

selected_student_id = st.sidebar.selectbox(
    "Select Student",
    student_ids
)

student = students[
    students["student_id"] == selected_student_id
].iloc[0]

career_goal = student[
    "career_goal"
]

completed_courses = get_completed_courses(
    student
)

skills = str(
    student.get("skills", "")
)

st.sidebar.write("### Career Goal")

st.sidebar.info(
    career_goal
)

st.sidebar.write("### Completed Courses")

st.sidebar.write(
    ", ".join(completed_courses)
    if completed_courses
    else "None"
)

st.sidebar.write("### Skills")

st.sidebar.write(
    skills if skills else "Not provided"
)


# ============================================================
# TABS
# ============================================================

tabs = st.tabs([
    "🎯 Recommendations",
    "🔍 Prerequisite Checker",
    "🕒 Schedule Checker",
    "📊 Evaluation",
    "🛡️ Responsible AI"
])


# ============================================================
# TAB 1 - RECOMMENDATIONS
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Course Recommendations</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Recommendations for **{career_goal}**"
    )

    recommendations = recommend_courses(
        career_goal,
        completed_courses
    )

    if recommendations.empty:

        st.warning(
            "No recommendation could be generated."
        )

    else:

        st.subheader(
            "Top Recommended Courses"
        )

        top_recommendations = recommendations[
            recommendations["Status"] == "Recommended"
        ].head(5)

        if top_recommendations.empty:

            st.warning(
                "No fully valid course was found. "
                "Please review prerequisite or schedule issues."
            )

        else:

            for _, row in top_recommendations.iterrows():

                st.markdown(
                    f"""
                    ### 🎯 {row['Course']}

                    **Course ID:** {row['Course ID']}  
                    **Recommendation Score:** {row['Score']} / 100  
                    **Career Match:** {row['Career Match']} / 5  
                    **Difficulty:** {row['Difficulty']}  
                    **Credits:** {row['Credits']}

                    **Why this course?**  
                    This course matches the selected career pathway,
                    has the required prerequisites available,
                    and does not have a detected timetable conflict.

                    **Learning Outcome:**  
                    {row['Learning Outcome']}

                    **Skills:**  
                    {row['Skills']}
                    """
                )

                st.divider()

        st.subheader(
            "All Course Analysis"
        )

        display_columns = [
            "Course",
            "Difficulty",
            "Credits",
            "Career Match",
            "Score",
            "Status"
        ]

        st.dataframe(
            recommendations[display_columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TAB 2 - PREREQUISITE CHECKER
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">Prerequisite Checker</div>',
        unsafe_allow_html=True
    )

    course_options = [
        f"{row.course_id} - {row.course_name}"
        for row in courses.itertuples()
    ]

    selected_course_text = st.selectbox(
        "Select a course",
        course_options
    )

    selected_course_id = selected_course_text.split(
        " - "
    )[0]

    selected_course_name = get_course_name(
        selected_course_id
    )

    result = prerequisite_check(
        selected_course_id,
        completed_courses
    )

    st.subheader(
        selected_course_name
    )

    if not result["required"]:

        st.success(
            "This course has no recorded prerequisites."
        )

    else:

        st.write("### Required Prerequisites")

        for item in result["required"]:

            st.write(
                f"• {item}"
            )

        if result["valid"]:

            st.markdown(
                """
                <div class="good-box">
                ✅ Prerequisite check passed.
                The student's completed courses satisfy the
                recorded prerequisites.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="danger-box">
                ❌ Prerequisite issue detected.
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(
                "Missing prerequisites:"
            )

            for item in result["missing"]:

                st.write(
                    f"• {item}"
                )

            st.info(
                "The system does not automatically override "
                "missing prerequisites. A teacher/advisor should "
                "review this case."
            )


# ============================================================
# TAB 3 - SCHEDULE CHECKER
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">Schedule Conflict Checker</div>',
        unsafe_allow_html=True
    )

    selected_courses = st.multiselect(
        "Select courses to check",
        courses["course_id"].tolist(),
        format_func=lambda x:
            f"{x} - {get_course_name(x)}"
    )

    if len(selected_courses) < 2:

        st.info(
            "Select at least two courses to check "
            "for timetable conflicts."
        )

    else:

        conflicts_found = []

        for i in range(
            len(selected_courses)
        ):

            for j in range(
                i + 1,
                len(selected_courses)
            ):

                course_a = selected_courses[i]
                course_b = selected_courses[j]

                if schedule_conflict(
                    course_a,
                    course_b
                ):

                    conflicts_found.append({

                        "Course 1":
                            get_course_name(course_a),

                        "Course 2":
                            get_course_name(course_b),

                        "Day":
                            get_schedule(course_a)["day"],

                        "Time":
                            f"{get_schedule(course_a)['start_time']} - "
                            f"{get_schedule(course_a)['end_time']}"
                    })

        if conflicts_found:

            st.error(
                f"{len(conflicts_found)} timetable conflict(s) detected."
            )

            st.dataframe(
                pd.DataFrame(conflicts_found),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "✅ No timetable conflicts detected."
            )


# ============================================================
# TAB 4 - EVALUATION
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">Prototype Evaluation</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        The prototype is compared with a simple baseline that
        considers only career matching.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Student Cases Tested",
            evaluation["students"]
        )

    with col2:

        st.metric(
            "Course Choice Quality",
            f"{evaluation['choice_quality']}%"
        )

    with col3:

        st.metric(
            "Conflict Reduction",
            f"{evaluation['conflict_reduction']}%"
        )

    st.divider()

    st.subheader(
        "Baseline vs Prototype"
    )

    comparison = pd.DataFrame({

        "Metric": [
            "Prerequisite/Schedule Conflicts",
            "Valid Prototype Choices"
        ],

        "Baseline": [
            evaluation["baseline_conflicts"],
            "-"
        ],

        "Prototype": [
            evaluation["prototype_conflicts"],
            f"{evaluation['choice_quality']}%"
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Evaluation Targets"
    )

    target_data = pd.DataFrame({

        "Metric": [
            "Course Choice Quality",
            "Prerequisite Conflict Reduction",
            "Schedule Conflict Detection",
            "Explanation Availability"
        ],

        "Target": [
            "≥ 85%",
            "≥ 70%",
            "≥ 95%",
            "100%"
        ],

        "Prototype": [
            f"{evaluation['choice_quality']}%",
            f"{evaluation['conflict_reduction']}%",
            "Rule-based",
            "100%"
        ]
    })

    st.dataframe(
        target_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Detailed Test Results"
    )

    st.dataframe(
        evaluation["details"],
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Error Analysis"
    )

    error_analysis = pd.DataFrame({

        "Failure Type": [
            "Missing prerequisite",
            "Timetable conflict",
            "Missing career mapping",
            "Unknown prerequisite information"
        ],

        "System Response": [
            "Flag course and explain missing prerequisite",
            "Flag timetable conflict",
            "Use available pathway evidence",
            "Ask advisor to review instead of guessing"
        ],

        "Risk": [
            "Student may select an advanced course too early",
            "Student may select overlapping courses",
            "Recommendation may be less personalized",
            "Incorrect assumption could lead to poor advice"
        ]
    })

    st.dataframe(
        error_analysis,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Evaluation results are calculated from the synthetic dataset "
        "included with this prototype."
    )


# ============================================================
# TAB 5 - RESPONSIBLE AI
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">Responsible AI & Governance</div>',
        unsafe_allow_html=True
    )

    st.subheader(
        "Purpose"
    )

    st.write(
        """
        This prototype is a decision-support system. It does not
        automatically enroll students into courses or make final
        academic decisions.
        """
    )

    st.subheader(
        "1. Transparency"
    )

    st.write(
        """
        Each recommendation provides visible evidence such as
        career match, prerequisites, learning outcomes, difficulty
        and timetable information.
        """
    )

    st.subheader(
        "2. Human Confirmation"
    )

    st.write(
        """
        Students and academic advisors remain responsible for the
        final course decision. High-impact decisions should be
        reviewed by a human.
        """
    )

    st.subheader(
        "3. Fairness"
    )

    st.write(
        """
        The system does not recommend courses based on sensitive
        personal characteristics. It uses course prerequisites,
        career pathways, learning outcomes and schedules.
        """
    )

    st.subheader(
        "4. Failure Handling"
    )

    st.write(
        """
        When prerequisite information is missing or unclear, the
        system flags the situation instead of making an unsupported
        assumption.
        """
    )

    st.subheader(
        "5. Student vs School Trade-off"
    )

    st.markdown(
        """
        <div class="info-box">

        <b>Student objective:</b><br>
        Choose courses that are interesting and useful for the
        desired career.

        <br><br>

        <b>School/advisor objective:</b><br>
        Make sure the student has the necessary prerequisites and
        can manage the academic schedule.

        <br><br>

        <b>Visible trade-off:</b><br>
        A highly career-relevant course may still be unsuitable if
        prerequisites are missing or the timetable conflicts.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader(
        "6. Environmental Considerations"
    )

    st.write(
        """
        The prototype uses a lightweight rule-based approach instead
        of computationally expensive model training. This reduces
        unnecessary computation for the decision-support task.
        """
    )

    st.subheader(
        "7. Maintenance"
    )

    st.write(
        """
        The dataset should be reviewed whenever courses,
        prerequisites, timetables, learning outcomes or career
        pathways change.
        """
    )

    st.subheader(
        "8. Auditability"
    )

    st.write(
        """
        The recommendation process is based on explicit rules and
        weighted factors, making it easier for an advisor to inspect
        why a recommendation was generated.
        """
    )

    st.success(
        "Responsible AI principle: the system supports the student "
        "and advisor; it does not replace human judgment."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Elective Career Explorer | Responsible Decision-Support Prototype"
)

st.caption(
    "Built with Python, Streamlit and Pandas using synthetic data."
)
