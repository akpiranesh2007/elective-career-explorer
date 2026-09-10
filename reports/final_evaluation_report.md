Project Title

Prerequisite and Career-Consequence Explorer for Elective Selection

1. Problem Analysis

In schools, students have different learning speeds, interests and career goals. When students select elective courses, they may not always understand the prerequisites required for a course or how that choice can affect their future career options.

For example, a student may choose an advanced course because it is related to their desired career. However, they may not have completed the prerequisite course needed to understand it properly. There can also be timetable conflicts between courses.

Because of this, students need a system that can show the prerequisites, course outcomes, schedules and possible career connections before they make an elective choice.

Our project aims to develop a Prerequisite and Career-Consequence Explorer that helps students understand these factors before selecting an elective.

2. Proposed Solution

We are developing a web-based prototype using Python, Pandas and Streamlit.

The system takes information about:

Student goals
Completed courses
Course outcomes
Prerequisites
Course schedules
Career pathways

The system then checks the available courses and provides recommendations along with explanations.

The basic workflow is:

Student Goal → Course Selection → Prerequisite Check → Schedule Check → Career Connection → Recommendation

The system is designed to support students and teachers rather than automatically make decisions for them.

3. User and Workflow

The main user of the system is a student selecting an elective course.

Workflow

Step 1: Student selects their career goal.

Step 2: The system checks the student's completed courses.

Step 3: Available elective courses are checked for prerequisites.

Step 4: The system checks the course schedule for possible conflicts.

Step 5: The system checks how the course is connected to the student's career goal.

Step 6: The system gives a recommendation score and explanation.

Step 7: The student or teacher can review the recommendation before making the final decision.

4. Dataset

For the current prototype, we created a synthetic dataset for testing.

The dataset contains the following information:

Dataset	Purpose
students.csv	Student goals and completed courses
courses.csv	Available elective courses
prerequisites.csv	Prerequisites required for courses
schedules.csv	Course days and timings
career_pathways.csv	Relationship between courses and careers
course_outcomes.csv	Learning outcomes and skills from courses

The data is synthetic, so real student personal information is not required.

5. Working Prototype

A working Streamlit prototype has been developed.

The current prototype includes:

Prerequisite Explorer

It checks whether the student has completed the prerequisite required for a course.

Career Explorer

It shows how strongly a course is connected to a selected career pathway.

Course Recommendation

The system gives a score to courses based on different factors.

Schedule Checker

It identifies possible timetable conflicts between courses.

Explanation Layer

The system provides information about why a course is recommended or why there may be a problem with selecting it.

6. Recommendation Approach

We selected a simple and transparent rule-based approach for the prototype.

The current scoring considers:

Factor	Weight
Prerequisite compatibility	40%
Career match	30%
Learning outcome	20%
Schedule compatibility	10%

We chose this approach because it is easy to understand and explain.

Since this project is being used to support student decisions, we felt that a transparent approach is more suitable for the initial prototype than using a complex model whose decisions may be difficult to explain.

7. Stakeholder Trade-off

There are two main stakeholder groups with different objectives.

Students

Students may want to choose courses based on:

Personal interest
Future career
New skills
Preferred subjects
Teachers / Academic Advisors

Teachers or advisors may focus on:

Required prerequisites
Student readiness
Avoiding timetable conflicts
Suitable academic progression

These objectives can sometimes conflict.

For example, a student may want to immediately select Machine Learning because they want an AI-related career. However, the advisor may suggest completing Statistics first because it is an important prerequisite.

The system makes this trade-off visible instead of simply accepting or rejecting the student's choice.

8. Responsible AI Considerations

Since the project is intended for a school environment, responsible AI is an important part of the design.

The current approach considers:

Human Decision-Making

The system provides suggestions but does not make the final decision for the student.

Explainability

The recommendation is based on visible factors such as prerequisites, career matching and schedules.

Privacy

Synthetic data is being used during the prototype stage instead of real student information.

Fairness

The system does not use sensitive personal characteristics to decide which course a student should take.

Fallback

If the system cannot confidently recommend a course because information is missing or conflicting, the student can discuss the choice with a teacher or academic advisor.

9. Failure Cases Tested

We have started testing realistic situations where the recommendation may not be straightforward.

Failure Case 1 — Missing Prerequisite

A student selects a course without completing the required prerequisite.

Expected result:
The system identifies the missing prerequisite and explains the issue.

Failure Case 2 — Schedule Conflict

Two courses have overlapping class timings.

Expected result:
The system identifies the timetable conflict.

Failure Case 3 — Weak Career Connection

A course has little connection with the student's selected career.

Expected result:
The system gives a lower career-match score instead of treating every course as equally suitable.

Failure Case 4 — Missing Information

Some course or career information may not be available.

Expected result:
The system should avoid making unsupported assumptions and allow the student or advisor to review the decision.

10. Baseline

A simple baseline is planned for comparison with our prototype.

The baseline will mainly recommend courses based on the student's career goal.

It will not give the same level of consideration to prerequisites and schedule conflicts.

Our prototype improves on this by considering:

Career + Prerequisites + Schedule + Learning Outcomes

This comparison will help us measure whether adding these factors improves the quality of course choices.

11. Evaluation Plan

The main evaluation will measure:

Course Choice Quality

Whether the recommended course is actually suitable based on the available course information.

Prerequisite Conflict Reduction

Whether the prototype reduces recommendations where the student has not completed the required prerequisite.

Baseline Comparison

The prototype will be compared against the simple career-based baseline.

The evaluation will use synthetic student cases and measure the results using numerical values.

The final target and measured results will be documented after completing the detailed evaluation.

12. Environmental Considerations

We selected a lightweight rule-based approach for the initial prototype.

The system uses Python, Pandas and Streamlit and does not require a large AI model for every recommendation.

This keeps the computational requirements relatively low and makes the prototype easier to run and maintain.

13. Maintenance Considerations

The information used by the system can change over time.

For example:

New courses may be introduced.
Prerequisites may change.
Course timings may change.
Career pathways may change.
Learning outcomes may be updated.

Therefore, the datasets need to be reviewed and updated regularly.

The system should also be tested again whenever important course or prerequisite information changes.

14. Current Progress
Completed
Problem analysis
User workflow design
Synthetic dataset preparation
Course information
Prerequisite information
Schedule information
Career pathway information
Course outcomes
Working Streamlit prototype
Prerequisite checking
Career matching
Schedule checking
Recommendation scoring
Explanation layer
Initial failure-case testing
Remaining Work
Complete baseline comparison
Complete measurable evaluation
Detailed error analysis
Short stakeholder/user validation
Final improvements
Three-minute demonstration video
Final evaluation report
15. Conclusion

The current stage of the project has produced a working prototype for helping students understand elective course choices.

The prototype does more than simply recommend a course based on a career goal. It also checks prerequisites, schedules and course outcomes and provides an explanation for the recommendation.

The current work provides the foundation for the next stage, where we will compare the prototype with the baseline, complete the evaluation, collect stakeholder feedback and improve the system.
