import streamlit as st
import requests
import PyPDF2
import docx
import io
import markdown as md_lib

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Syllabus Designer",
    page_icon="📚",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

.stApp {
    background: #f5f5f5;
}

.stButton button {
    width: 100%;
    height: 50px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
}

.generated-box {
    background: white;
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #dddddd;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FILE EXTRACTION ---------------- #

def extract_text_from_file(uploaded_file):

    if uploaded_file is None:
        return ""

    file_extension = uploaded_file.name.split(".")[-1].lower()

    # PDF
    if file_extension == "pdf":

        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        return text

    # DOCX
    elif file_extension in ["docx", "doc"]:

        doc = docx.Document(uploaded_file)

        text = ""

        for para in doc.paragraphs:
            text += para.text + "\n"

        return text

    # TXT
    elif file_extension == "txt":

        return uploaded_file.getvalue().decode("utf-8")

    return ""

# ---------------- PDF GENERATOR ---------------- #

def create_pdf(text):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    story = []

    lines = text.split("\n")

    for line in lines:

        p = Paragraph(line, styles["BodyText"])

        story.append(p)

        story.append(Spacer(1, 10))

    doc.build(story)

    buffer.seek(0)

    return buffer

# ---------------- BYTEZ FUNCTION ---------------- #

def ask_bytez(prompt_text):

    API_KEY = st.secrets["BYTEZ_API_KEY"]

    url = "https://api.bytez.com/models/v2/openai/v1/chat/completions"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert university syllabus designer."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "max_tokens": 1200,
        "temperature": 0.7
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    result = response.json()

    # ERROR HANDLING
    if "choices" not in result:

        return f"API Error: {result}"

    return result["choices"][0]["message"]["content"]

# ---------------- OLLAMA FUNCTION ---------------- #

def ask_ollama(prompt_text):

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "gemma:2b",
        "prompt": prompt_text,
        "stream": False
    }

    response = requests.post(
        url,
        json=payload
    )

    result = response.json()

    return result["response"]

# ---------------- HERO ---------------- #

st.title("📚 AI Syllabus Designer")

st.write(
    "Generate professional university syllabus using AI"
)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.header("⚙️ Settings")

    provider = st.selectbox(
        "AI Provider",
        [
            "Bytez Cloud",
            "Ollama Local"
        ]
    )

    university_name = st.text_input(
        "University Name"
    )

    semester = st.selectbox(
        "Semester",
        [
            "1st Semester",
            "2nd Semester",
            "3rd Semester",
            "4th Semester",
            "5th Semester",
            "6th Semester",
            "7th Semester",
            "8th Semester"
        ]
    )

    branch = st.selectbox(
        "Branch",
        [
            "Computer Science",
            "Information Technology",
            "Mechanical",
            "Civil",
            "Electrical",
            "Electronics"
        ]
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    units = st.slider(
        "Total Units",
        1,
        10,
        5
    )

# ---------------- MAIN SECTION ---------------- #

subject = st.text_input(
    "Subject Name",
    placeholder="Enter subject name"
)

description = st.text_area(
    "Course Description",
    placeholder="Describe the course"
)

uploaded_file = st.file_uploader(
    "Upload Old Syllabus",
    type=["pdf", "docx", "txt"]
)

generate = st.button(
    "Generate Syllabus"
)

# ---------------- GENERATION ---------------- #

if generate:

    if subject == "":

        st.warning(
            "Please enter subject name"
        )

    else:

        extracted_text = ""

        if uploaded_file:

            with st.spinner(
                "Extracting file..."
            ):

                extracted_text = extract_text_from_file(
                    uploaded_file
                )

        prompt = f"""
        Create a professional university syllabus.

        Subject: {subject}

        University: {university_name}

        Branch: {branch}

        Semester: {semester}

        Difficulty: {difficulty}

        Total Units: {units}

        Description:
        {description}

        Old Syllabus Reference:
        {extracted_text[:2000]}

        Generate:
        1. Course Overview
        2. Learning Outcomes
        3. Unit Wise Syllabus
        4. Practical List
        5. Recommended Books
        6. Career Outcomes

        Make it professional and detailed.
        """

        try:

            with st.spinner(
                "Generating syllabus..."
            ):

                # BYTEZ CLOUD
                if provider == "Bytez Cloud":

                    output = ask_bytez(prompt)

                # OLLAMA LOCAL
                else:

                    output = ask_ollama(prompt)

            st.success(
                "Syllabus Generated Successfully"
            )

            # PDF DOWNLOAD
            pdf_data = create_pdf(output)

            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"{subject}_syllabus.pdf",
                mime="application/pdf"
            )

            # DISPLAY OUTPUT
            html_output = md_lib.markdown(output)

            st.markdown(
                f'<div class="generated-box">{html_output}</div>',
                unsafe_allow_html=True
            )

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )