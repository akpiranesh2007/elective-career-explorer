# Prerequisite and Career-Consequence Explorer

## Project Overview

Students have different learning speeds, interests and career goals. When selecting elective courses, students may not always understand the prerequisites required for a course or how the course can help with their future career.

This project is a web-based prototype that helps students explore elective courses by considering prerequisites, course outcomes, schedules, career pathways and student goals.

The system provides recommendations with simple explanations so that students can understand why a course may or may not be suitable.

This project is designed as a decision-support system. It does not make the final decision for the student.

---

## Problem Statement

Students sometimes select courses without understanding their prerequisites and possible career consequences.

The objective of this project is to create a prerequisite and career-consequence explorer for elective selection.

The system considers:

- Course outcomes
- Prerequisites
- Course schedules
- Career pathways
- Student goals

The project also considers responsible AI, environmental impact, ethical issues and future maintenance requirements.

---

## Objectives

The main objectives are:

1. Help students understand course prerequisites.
2. Show the relationship between courses and career pathways.
3. Identify possible schedule conflicts.
4. Provide understandable course recommendations.
5. Explain the reason behind recommendations.
6. Compare the prototype with a simple baseline.
7. Test realistic failure cases.
8. Measure the quality of course choices and prerequisite conflict reduction.

---

## Technology Used

- Python
- Pandas
- Streamlit
- CSV datasets

The prototype uses a transparent rule-based recommendation approach instead of a complex machine-learning model.

---

## System Workflow

```text
Student Profile
      |
      v
Career Goal
      |
      v
Course Information
      |
      +----> Prerequisite Check
      |
      +----> Schedule Check
      |
      +----> Career Match
      |
      +----> Course Outcomes
      |
      v
Recommendation Score
      |
      v
Explanation
      |
      v
Student / Advisor Decision
