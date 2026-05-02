import re
import pdfplumber
from docx import Document
import io

class CVExtractor:
    def __init__(self):
        self.skills_list = [
            'Python', 'Java', 'C++', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
            'Node.js', 'Express', 'Flask', 'Django', 'FastAPI', 'SQL', 'NoSQL', 'MongoDB',
            'PostgreSQL', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Machine Learning',
            'Deep Learning', 'NLP', 'Computer Vision', 'Data Science', 'Pandas', 'NumPy',
            'Scikit-learn', 'TensorFlow', 'PyTorch', 'Git', 'CI/CD', 'Agile', 'Scrum'
        ]

    def extract_text_from_pdf(self, file_bytes):
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def extract_text_from_docx(self, file_bytes):
        doc = Document(io.BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def extract_info(self, text):
        info = {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "links": self.extract_links(text),
            "raw_text": text[:1000] + "..." if len(text) > 1000 else text
        }
        return info

    def extract_name(self, text):
        # Heuristic: Name is often in the first few lines, uppercase or Title Case
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return None
        
        # Simple heuristic: look for 2-3 words in the first few lines that don't look like common headers
        for line in lines[:5]:
            if re.match(r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}$', line):
                return line
        return lines[0] if lines else "Unknown"

    def extract_email(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None

    def extract_skills(self, text):
        found_skills = []
        for skill in self.skills_list:
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                found_skills.append(skill)
        return found_skills

    def extract_links(self, text):
        links = {
            "linkedin": None,
            "github": None
        }
        linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9-]+', text)
        if linkedin_match:
            links["linkedin"] = linkedin_match.group(0)
            
        github_match = re.search(r'github\.com/[a-zA-Z0-9-]+', text)
        if github_match:
            links["github"] = github_match.group(0)
            
        return links
