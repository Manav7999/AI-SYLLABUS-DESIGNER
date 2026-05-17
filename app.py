import streamlit as st
import requests
import PyPDF2
import docx
import io
import markdown as md_lib
import ollama

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
    background-color: #f5f5f5;
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
    padding: 25px;
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

        document = docx.Document(uploaded_file)

        text = ""

        for para in document.paragraphs:
            text += para.text + "\n"

        return text

    # TXT
    elif file_extension == "txt":

        return uploaded_file.getvalue().decode("utf-8")

    return ""

# ---------------- PDF CREATION ---------------- #

def create_pdf(text):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    story = []

    lines = text.split("\n")

    for line in lines:

        paragraph = Paragraph(
            line,
            styles["BodyText"]
        )

        story.append(paragraph)

        story.append(Spacer(1, 10))

    document.build(story)

    buffer.seek(0)

    return buffer

# ---------------- OLLAMA FUNCTION ---------------- #

def ask_ollama(prompt_text):

    try:

        response = ollama.chat(

            model="gemma:2b",

            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:

        return f"API Error: {str(e)}"

# ---------------- OPENROUTER FUNCTION ---------------- #

def ask_openrouter(prompt_text):

    API_KEY = st.secrets["OPENROUTER_API_KEY"]

    models = [

        "mistralai/mistral-7b-instruct:free",

        "google/gemma-2-9b-it:free",

        "meta-llama/llama-3.2-3b-instruct:free"

    ]

    headers = {

        "Authorization": f"Bearer {API_KEY}",

        "HTTP-Referer": "https://streamlit.io",

        "X-Title": "AI Syllabus Designer"

    }

    for model_name in models:

        try:

            payload = {

                "model": model_name,

                "messages": [

                    {
                        "role": "system",
                        "content": "You are an expert university syllabus designer."
                    },

                    {
                        "role": "user",
                        "content": prompt_text
                    }

                ]

            }

            response = requests.post(

                url="https://openrouter.ai/api/v1/chat/completions",

                headers=headers,

                json=payload,

                timeout=120

            )

            result = response.json()

            # SUCCESS
            if "choices" in result:

                return result["choices"][0]["message"]["content"]

        except:
            pass

    return "API Error: All free OpenRouter models are currently busy. Please try again in 1 minute."

# ---------------- TITLE ---------------- #

st.title("📚 AI Syllabus Designer")

st.write(
    "Generate professional university syllabus using AI"
)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.header("⚙️ Settings")

    ai_provider = st.selectbox(

        "Select AI Provider",

        [
            "OpenRouter Cloud",
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

# ---------------- MAIN UI ---------------- #

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

# ---------------- GENERATE ---------------- #

if generate:

    if subject.strip() == "":

        st.warning(
            "Please enter subject name"
        )

    else:

        extracted_text = ""

        # FILE EXTRACTION
        if uploaded_file:

            with st.spinner(
                "Extracting old syllabus..."
            ):

                extracted_text = extract_text_from_file(
                    uploaded_file
                )

        # PROMPT
        prompt = f"""
Create a professional university syllabus.

Subject: {subject}

University Name: {university_name}

Semester: {semester}

Branch: {branch}

Difficulty Level: {difficulty}

Total Units: {units}

Course Description:
{description}

Reference Old Syllabus:
{extracted_text[:2000]}

Generate:

1. Course Overview

2. Learning Outcomes

3. Unit Wise Topics

4. Practical List

5. Recommended Books

6. Career Opportunities

Make the syllabus detailed, professional and properly structured.
"""

        # AI GENERATION
        with st.spinner(
            "Generating syllabus..."
        ):

            # OPENROUTER
            if ai_provider == "OpenRouter Cloud":

                output = ask_openrouter(prompt)

            # OLLAMA
            else:

                output = ask_ollama(prompt)

        # ERROR
        if output.startswith("API Error"):

            st.error(output)

        else:

            # SUCCESS
            st.success(
                "Syllabus Generated Successfully"
            )

            # PDF
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