import streamlit as st
import PyPDF2
import docx
import io
import markdown as md_lib

from huggingface_hub import InferenceClient

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

# ---------------- PDF GENERATOR ---------------- #

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

# ---------------- HUGGING FACE FUNCTION ---------------- #

def ask_huggingface(prompt_text):

    try:

        HF_TOKEN = st.secrets["HF_API_KEY"]

        client = InferenceClient(
            provider="hf-inference",
            api_key=HF_TOKEN
        )

        response = client.chat.completions.create(

            model="HuggingFaceTB/SmolLM2-1.7B-Instruct",

            messages=[
                {
                    "role": "system",
                    "content": "You are an expert university syllabus designer."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],

            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"API Error: {str(e)}"

# ---------------- HERO SECTION ---------------- #

st.title("📚 AI Syllabus Designer")

st.write(
    "Generate professional university syllabus using AI"
)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.header("⚙️ Settings")

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

# ---------------- GENERATE SYLLABUS ---------------- #

if generate:

    if subject.strip() == "":

        st.warning(
            "Please enter subject name"
        )

    else:

        extracted_text = ""

        if uploaded_file:

            with st.spinner(
                "Extracting syllabus file..."
            ):

                extracted_text = extract_text_from_file(
                    uploaded_file
                )

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

Make the syllabus detailed and professional.
"""

        with st.spinner(
            "Generating syllabus..."
        ):

            output = ask_huggingface(prompt)

        # ERROR
        if output.startswith("API Error"):

            st.error(output)

        # SUCCESS
        else:

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

            # SHOW OUTPUT
            html_output = md_lib.markdown(output)

            st.markdown(
                f'<div class="generated-box">{html_output}</div>',
                unsafe_allow_html=True
            )