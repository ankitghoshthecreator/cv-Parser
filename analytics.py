import collections
import pandas as pd

class GapAnalytics:
    @staticmethod
    def calculate_skill_gaps(jobs, students):
        """
        jobs: list of all jobs
        students: list of all students with extracted skills
        """
        employer_needs = []
        for job in jobs:
            skills = [s.strip().lower() for s in job.required_skills.split(',') if s.strip()]
            employer_needs.extend(skills)
        
        student_skills = []
        for student in students:
            if student.skills:
                skills = [s.strip().lower() for s in student.skills.split(',') if s.strip()]
                student_skills.extend(skills)

        need_counts = collections.Counter(employer_needs)
        have_counts = collections.Counter(student_skills)

        # Get all unique skills mentioned
        all_skills = set(need_counts.keys()) | set(have_counts.keys())

        gap_data = []
        for skill in all_skills:
            needed = need_counts.get(skill, 0)
            available = have_counts.get(skill, 0)
            gap = needed - available
            gap_data.append({
                "skill": skill,
                "needed": needed,
                "available": available,
                "gap": max(0, gap) # positive means employer needs more than available
            })

        # Sort by gap to show biggest deficiencies
        gap_data.sort(key=lambda x: x["gap"], reverse=True)
        return gap_data[:10] # Return top 10 gaps
