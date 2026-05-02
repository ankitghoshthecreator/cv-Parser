from fastapi import FastAPI, UploadFile, File, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import shutil

from models import SessionLocal, init_db, User, Job, UserRole, OTP
from auth import (
    hash_password, verify_password, create_access_token, 
    generate_otp, validate_indian_phone, validate_email
)
from extractor import CVExtractor
from matcher import JobMatcher
from analytics import GapAnalytics
from reporter import PDFReporter

app = FastAPI()

# Initialization
init_db()
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

extractor = CVExtractor()
matcher = JobMatcher()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Auth Endpoints ---

@app.post("/api/register")
async def register(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    # Validation
    if not validate_email(data['email']):
        return JSONResponse({"error": "Only @gmail.com addresses are allowed."}, 400)
    if not validate_indian_phone(data['phone']):
        return JSONResponse({"error": "Invalid Indian phone number."}, 400)
    if data['password'] != data['confirm_password']:
        return JSONResponse({"error": "Passwords do not match."}, 400)
    
    # Check if user exists
    if db.query(User).filter(User.email == data['email']).first():
        return JSONResponse({"error": "Email already registered."}, 400)

    # Create OTP
    otp_code = generate_otp()
    new_otp = OTP(email=data['email'], code=otp_code)
    db.add(new_otp)
    db.commit()
    
    # In a real app, send SMS/Email. Here we print to console.
    print(f"\n--- [OTP VERIFICATION] ---\nEmail: {data['email']}\nCode: {otp_code}\n--------------------------\n")
    
    # Temporary user storage (or just return data to client to send back with OTP)
    # For this prototype, we return the OTP in the response for the "Toast" demo.
    return {"message": "OTP sent!", "email": data['email'], "debug_otp": otp_code}

@app.post("/api/verify-otp")
async def verify_otp(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    otp_record = db.query(OTP).filter(OTP.email == data['email'], OTP.code == data['otp']).first()
    
    if not otp_record:
        return JSONResponse({"error": "Invalid OTP."}, 400)
    
    # Register the actual user now
    new_user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        password_hash=hash_password(data['password']),
        role=UserRole(data['role']),
        is_verified=True
    )
    db.add(new_user)
    db.delete(otp_record)
    db.commit()
    
    return {"message": "Registration successful! You can now login."}

@app.post("/api/login")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = db.query(User).filter(User.email == data['email']).first()
    
    if not user or not verify_password(data['password'], user.password_hash):
        return JSONResponse({"error": "Invalid credentials."}, 401)
    
    token = create_access_token({"sub": user.email, "role": user.role.value, "id": user.id})
    return {"token": token, "role": user.role.value, "name": user.name}

# --- Employer Routes ---

@app.post("/api/jobs")
async def post_job(request: Request, db: Session = Depends(get_db)):
    # In real app, verify token for employer role
    data = await request.json()
    new_job = Job(
        title=data['title'],
        category=data['category'],
        description=data['description'],
        required_skills=data['required_skills'],
        employer_id=data['employer_id']
    )
    db.add(new_job)
    db.commit()
    return {"message": "Job posted successfully!"}

# --- Student Routes ---

@app.post("/api/upload-cv")
async def upload_cv(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    text = ""
    if file.filename.endswith(".pdf"):
        text = extractor.extract_text_from_pdf(contents)
    else:
        text = extractor.extract_text_from_docx(contents)
    
    info = extractor.extract_info(text)
    
    user = db.query(User).filter(User.id == user_id).first()
    user.cv_text = text
    user.skills = ",".join(info['skills'])
    db.commit()
    
    return {"message": "CV uploaded and processed!", "skills": info['skills']}

@app.get("/api/matches/{user_id}")
async def get_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user.cv_text:
        return JSONResponse({"error": "Please upload CV first."}, 400)
    
    all_jobs = db.query(Job).all()
    matches = matcher.get_top_matches(user.cv_text, all_jobs)
    return matches

# --- Management Routes ---

@app.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    gap_data = GapAnalytics.calculate_skill_gaps(jobs, students)
    return gap_data

@app.get("/api/report")
async def download_report(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    gap_data = GapAnalytics.calculate_skill_gaps(jobs, students)
    
    pdf_content = PDFReporter.generate_gap_report(gap_data)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=skill_gap_report.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
