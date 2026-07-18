"""
Resume Agent - Reads MugasalaRohitResume.pdf and uses the LLM to
tailor a customized summary/cover letter for each job description.
"""
import os
import logging
import PyPDF2

logger = logging.getLogger("jarvis.resume_agent")

RESUME_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "MugasalaRohitResume.pdf"
)

def read_resume_text() -> str:
    """Extract raw text from the master resume PDF."""
    if not os.path.exists(RESUME_PATH):
        logger.error(f"Resume not found at: {RESUME_PATH}")
        return ""
    try:
        with open(RESUME_PATH, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to read resume: {e}")
        return ""

def tailor_resume(job_title: str, company: str, job_description: str, router) -> str:
    """
    Use the HybridRouter LLM to tailor a short professional summary
    and highlight relevant skills from the master resume for the given JD.
    Returns a tailored text block suitable for pasting into an application form.
    """
    resume_text = read_resume_text()
    if not resume_text:
        return "Unable to read resume. Please check MugasalaRohitResume.pdf."

    prompt = (
        f"You are a professional career consultant helping Rohit Mugasala apply for a job.\n\n"
        f"JOB TITLE: {job_title}\n"
        f"COMPANY: {company}\n"
        f"JOB DESCRIPTION:\n{job_description[:3000]}\n\n"
        f"ROHIT'S MASTER RESUME:\n{resume_text[:3000]}\n\n"
        f"Task: Write a concise, powerful 3-4 sentence professional summary for Rohit that:\n"
        f"1. Directly addresses the key skills/requirements mentioned in the JD.\n"
        f"2. Highlights Rohit's most relevant experience from his resume.\n"
        f"3. Uses confident, professional language.\n"
        f"4. Ends with why he is the right fit for {company}.\n\n"
        f"ONLY output the professional summary text. No headers, no bullet points, no extra commentary."
    )

    logger.info(f"[ResumeAgent] Tailoring resume for '{job_title}' at {company}...")
    tailored = router.execute(prompt)
    return tailored

def generate_cover_note(job_title: str, company: str, job_description: str, router) -> str:
    """Generate a short cover note / 'Why do you want to work here?' answer."""
    resume_text = read_resume_text()
    prompt = (
        f"You are helping Rohit Mugasala write a cover note for a job application.\n"
        f"JOB: {job_title} at {company}\n"
        f"JD SNIPPET: {job_description[:1500]}\n"
        f"RESUME: {resume_text[:2000]}\n\n"
        f"Write a compelling 2-3 sentence answer to 'Why do you want this role?' "
        f"Make it sound human, genuine, and specific to this company. "
        f"No generic fluff. Output only the answer text."
    )
    logger.info(f"[ResumeAgent] Generating cover note for '{job_title}'...")
    return router.execute(prompt)
