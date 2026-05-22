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
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors

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

# ---------------- PROFESSIONAL PDF CREATION ---------------- #

def create_pdf(
    text,
    college_name,
    subject_name,
    branch,
    subject_code,
    year,
    semester
):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # ---------- CUSTOM STYLES ---------- #

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=24,
        leading=30,
        alignment=1,
        textColor=colors.darkblue,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#003366"),
        spaceBefore=16,
        spaceAfter=10
    )

    subheading_style = ParagraphStyle(
        'SubHeadingStyle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#444444"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontName='Times-Roman',
        fontSize=12,
        leading=20,
        textColor=colors.black,
        spaceAfter=10
    )

    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.black,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        leading=18,
        leftIndent=20,
        bulletIndent=10,
        textColor=colors.black,
        spaceAfter=6
    )

    # ---------- STORY ---------- #

    story = []

    # TITLE
    story.append(
        Paragraph(
            college_name.upper(),
            title_style
        )
    )

    # SUBJECT DETAILS
    details = f"""
    <b>SUBJECT NAME :</b> {subject_name}<br/>
    <b>BRANCH :</b> {branch}<br/>
    <b>SUBJECT CODE :</b> {subject_code}<br/>
    <b>YEAR :</b> {year}<br/>
    <b>SEMESTER :</b> {semester}
    """

    story.append(
        Paragraph(
            details,
            info_style
        )
    )

    story.append(Spacer(1, 20))

    # MAIN CONTENT
    lines = text.split("\n")

    for line in lines:

        clean_line = line.strip()

        if clean_line == "":
            continue

        # MAIN HEADINGS
        if (
            "Course Overview" in clean_line
            or "Learning Outcomes" in clean_line
            or "Practical" in clean_line
            or "Books" in clean_line
            or "Career" in clean_line
        ):

            story.append(
                Paragraph(
                    clean_line,
                    heading_style
                )
            )

        # UNIT HEADINGS
        elif (
            clean_line.startswith("Unit")
            or clean_line.startswith("UNIT")
        ):

            story.append(
                Paragraph(
                    clean_line,
                    subheading_style
                )
            )

        # BULLETS
        elif (
            clean_line.startswith("-")
            or clean_line.startswith("•")
            or clean_line.startswith("*")
        ):

            bullet_text = clean_line.replace("-", "").replace("•", "").replace("*", "").strip()

            story.append(
                Paragraph(
                    f"• {bullet_text}",
                    bullet_style
                )
            )

        # NORMAL TEXT
        else:

            story.append(
                Paragraph(
                    clean_line,
                    body_style
                )
            )

    # ---------- OVERVIEW SECTION ---------- #

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "SYLLABUS OVERVIEW",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "This syllabus is designed to provide students with theoretical understanding and practical exposure in the selected subject area. The curriculum focuses on conceptual clarity, practical implementation, industry-oriented learning, and academic excellence.",
            body_style
        )
    )

    # ---------- TABLE SECTION ---------- #

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "SYLLABUS COMPLETION TABLE",
            heading_style
        )
    )

    table_data = [

        ["UNIT", "TOPIC", "EXPECTED COMPLETION"],

        ["Unit 1", "Introduction & Fundamentals", "Week 1-2"],

        ["Unit 2", "Core Concepts", "Week 3-4"],

        ["Unit 3", "Advanced Concepts", "Week 5-6"],

        ["Unit 4", "Applications", "Week 7-8"],

        ["Unit 5", "Projects & Practical Learning", "Week 9-10"]

    ]

    table = Table(
        table_data,
        colWidths=[120, 220, 150]
    )

    table.setStyle(

        TableStyle([

            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),

            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('FONTSIZE', (0, 0), (-1, 0), 12),

            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),

            ('FONTSIZE', (0, 1), (-1, -1), 11),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER')

        ])
    )

    story.append(table)

    # ---------- BUILD PDF ---------- #

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

# ---------------- GROQ FUNCTION ---------------- #

def ask_groq(prompt_text):

    try:

        API_KEY = st.secrets["GROQ_API_KEY"]

        headers = {

            "Authorization": f"Bearer {API_KEY}",

            "Content-Type": "application/json"

        }

        payload = {

            "model": "llama-3.3-70b-versatile",

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

            "temperature": 0.7

        }

        response = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers=headers,

            json=payload,

            timeout=120

        )

        result = response.json()

        if "choices" in result:

            return result["choices"][0]["message"]["content"]

        elif "error" in result:

            return f"API Error: {result['error']['message']}"

        else:

            return f"Unexpected Response: {result}"

    except Exception as e:

        return f"API Error: {str(e)}"

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
            "Groq Cloud",
            "Ollama Local"
        ]
    )

    university_name = st.text_input(
        "College / University Name"
    )

    subject_code = st.text_input(
        "Subject Code",
        value="CS101"
    )

    year = st.text_input(
        "Academic Year",
        value="2026"
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

        if uploaded_file:

            with st.spinner(
                "Extracting old syllabus..."
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

Make the syllabus detailed, professional and properly structured.
"""

        with st.spinner(
            "Generating syllabus..."
        ):

            if ai_provider == "Groq Cloud":

                output = ask_groq(prompt)

            else:

                output = ask_ollama(prompt)

        if output.startswith("API Error"):

            st.error(output)

        else:

            st.success(
                "Syllabus Generated Successfully"
            )

            pdf_data = create_pdf(
                output,
                university_name,
                subject,
                branch,
                subject_code,
                year,
                semester
            )

            st.download_button(
                label="Download Professional PDF",
                data=pdf_data,
                file_name=f"{subject}_syllabus.pdf",
                mime="application/pdf"
            )

            html_output = md_lib.markdown(output)

            st.markdown(
                f'<div class="generated-box">{html_output}</div>',
                unsafe_allow_html=True
            )