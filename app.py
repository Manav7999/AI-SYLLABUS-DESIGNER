import streamlit as st
import ollama
import PyPDF2
import docx
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Syllabus Designer",
    page_icon="📚",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');

/* Main Background */
.stApp {
    background-color: #000000;
    background-image: 
        radial-gradient(at 0% 0%, rgba(255, 255, 255, 0.03) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(255, 255, 255, 0.03) 0px, transparent 50%);
    background-attachment: fixed;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}

/* Remove Streamlit Default Header */
header[data-testid="stHeader"] { background: transparent !important; }
header[data-testid="stHeader"] button { color: #ffffff !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Entry Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Cards & Containers (Targeting Streamlit Columns) */
div[data-testid="column"] {
    background: rgba(18, 18, 18, 0.8);
    padding: 40px;
    border-radius: 32px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 25px;
    animation: fadeInUp 1s ease-out forwards;
}

div[data-testid="column"]:hover {
    border-color: rgba(255, 255, 255, 0.2);
    border-radius: 36px;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #121212 0%, #000000 100%);
    padding: 60px 40px;
    border-radius: 40px;
    margin-bottom: 40px;
    text-align: center;
    border: 2px solid rgba(255, 255, 255, 0.1);
    animation: fadeInUp 0.8s ease-out;
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 64px;
    font-weight: 800;
    background: linear-gradient(to right, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 15px;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 20px;
    color: #475569;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto;
}

/* Input Labels */
label {
    font-family: 'Outfit', sans-serif !important;
    color: #64748b !important;
    font-weight: 600 !important;
}

/* Text Inputs & Text Areas */
.stTextInput input, .stTextArea textarea {
    background-color: rgba(18, 18, 18, 1) !important;
    color: #ffffff !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 20px 24px !important;
    font-size: 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
}

.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #334155 !important;
    opacity: 1 !important;
}

.stTextInput input:hover, .stTextArea textarea:hover {
    background-color: #262626 !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    background-color: #000000 !important;
    border-color: #ffffff !important;
    outline: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0a0a0a;
    border-right: 4px solid #ffffff !important;
    border-top: 4px solid #ffffff !important;
    border-bottom: 4px solid #ffffff !important;
    padding-top: 0 !important;
    border-top-right-radius: 40px;
    border-bottom-right-radius: 40px;
    margin: 10px 0;
    height: calc(100vh - 20px);
    width: 400px !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 0;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Sidebar Title */
.sidebar-header {
    margin-top: -30px;
    margin-bottom: 20px;
    padding: 0;
}

.sidebar-header h2 {
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
    font-size: 2.2rem;
    margin: 0;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.1;
}

/* Sidebar Controls */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: rgba(18, 18, 18, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
}

/* Sidebar Info Box with Corner Design */
.sidebar-info {
    margin-top: 40px;
    padding: 20px;
    background: rgba(18, 18, 18, 0.4);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
    font-size: 0.85rem;
    color: #64748b;
}

.sidebar-info::before {
    content: "";
    position: absolute;
    top: -1px;
    right: 20px;
    width: 30px;
    height: 3px;
    background: #ffffff;
    border-radius: 0 0 4px 4px;
}

/* Button */
.stButton button {
    display: block;
    margin: 0 auto !important;
    width: 100%;
    max-width: 400px;
    background: linear-gradient(135deg, #262626 0%, #000000 100%);
    color: white;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    padding: 20px 40px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.stButton button:hover {
    transform: translateY(-5px) scale(1.05);
    background: #ffffff;
    color: #000000;
    border-color: #ffffff;
}

.stButton button:active {
    transform: translateY(0) scale(0.98);
}

/* Generated Output */
@keyframes glow {
    0% { border-color: rgba(255, 255, 255, 0.1); box-shadow: 0 0 5px rgba(255, 255, 255, 0.05); }
    50% { border-color: rgba(255, 255, 255, 0.3); box-shadow: 0 0 20px rgba(255, 255, 255, 0.1); }
    100% { border-color: rgba(255, 255, 255, 0.1); box-shadow: 0 0 5px rgba(255, 255, 255, 0.05); }
}

.generated-box {
    background: #0a0a0a;
    padding: 45px;
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
    animation: fadeInUp 0.8s ease-out, glow 4s infinite ease-in-out;
    line-height: 1.6;
}

.generated-box h1, .generated-box h2, .generated-box h3 {
    color: #ffffff;
    font-family: 'Outfit', sans-serif;
    margin-top: 25px;
}

/* Download Button Specific Styling */
.stDownloadButton button {
    background: #ffffff !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border-radius: 15px !important;
    padding: 15px 30px !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton button:hover {
    transform: scale(1.02) translateY(-2px) !important;
    box-shadow: 0 10px 20px rgba(255, 255, 255, 0.15) !important;
}

/* Scrollbar */
::-webkit-scrollbar-thumb { background: #334155; }

/* Remove Streamlit Default Header */
header[data-testid="stHeader"] { background: transparent !important; }
header[data-testid="stHeader"] button { color: white !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Entry Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Cards & Containers (Targeting Streamlit Columns) */
div[data-testid="column"] {
    background: rgba(15, 23, 42, 0.4);
    padding: 40px;
    border-radius: 32px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 25px;
    animation: fadeInUp 1s ease-out forwards;
}

div[data-testid="column"]:hover {
    border-color: rgba(59, 130, 246, 0.2);
    border-radius: 36px;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #121212 0%, #000000 100%);
    padding: 60px 40px;
    border-radius: 40px;
    margin-bottom: 40px;
    text-align: center;
    border: 2px solid rgba(255, 255, 255, 0.1);
    animation: fadeInUp 0.8s ease-out;
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 64px;
    font-weight: 800;
    background: linear-gradient(to right, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 15px;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 20px;
    color: #64748b;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto;
}

/* Cards */
.card {
    background: rgba(15, 23, 42, 0.6);
    padding: 35px;
    border-radius: 24px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeInUp 1s ease-out forwards;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    border-color: rgba(59, 130, 246, 0.2);
}

/* Input Labels */
label {
    font-family: 'Outfit', sans-serif !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* Text Inputs & Text Areas */
.stTextInput input, .stTextArea textarea {
    background-color: rgba(15, 23, 42, 0.4) !important;
    color: #ffffff !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 20px 24px !important;
    font-size: 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
}

.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #475569 !important;
    opacity: 1 !important;
}

.stTextInput input:hover, .stTextArea textarea:hover {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-color: rgba(59, 130, 246, 0.4) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    background-color: rgba(18, 18, 18, 0.8) !important;
    border-color: #ffffff !important;
    outline: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0a0a0a;
    border-right: 4px solid #ffffff !important;
    border-top: 4px solid #ffffff !important;
    border-bottom: 4px solid #ffffff !important;
    padding-top: 0 !important;
    border-top-right-radius: 40px;
    border-bottom-right-radius: 40px;
    margin: 10px 0;
    height: calc(100vh - 20px);
    width: 400px !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 0;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Sidebar Title */
.sidebar-header {
    margin-top: -30px;
    margin-bottom: 20px;
    padding: 0;
}

.sidebar-header h2 {
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
    font-size: 2.2rem;
    margin: 0;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.1;
}

/* Sidebar Controls */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
}

/* Sidebar Info Box with Corner Design */
.sidebar-info {
    margin-top: 40px;
    padding: 20px;
    background: rgba(15, 23, 42, 0.4);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
    font-size: 0.85rem;
    color: #94a3b8;
}

.sidebar-info::before {
    content: "";
    position: absolute;
    top: -1px;
    right: 20px;
    width: 30px;
    height: 3px;
    background: #ffffff;
    border-radius: 0 0 4px 4px;
}

/* Feature Box */
.feature-box {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
    padding: 30px;
    border-radius: 24px;
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.feature-box h3 {
    font-family: 'Outfit', sans-serif;
    color: #f1f5f9;
}

.feature-item {
    color: #94a3b8;
}

/* Button */
.stButton button {
    display: block;
    margin: 0 auto !important;
    width: 100%;
    max-width: 400px;
    background: linear-gradient(135deg, #262626 0%, #000000 100%);
    color: white;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    padding: 20px 40px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.stButton button:hover {
    transform: translateY(-5px) scale(1.05);
    background: #ffffff;
    color: #000000;
    border-color: #ffffff;
}

.stButton button:active {
    transform: translateY(0) scale(0.98);
}

/* Generated Output */
.generated-box {
    background: #0f172a;
    padding: 45px;
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
}

.generated-box h1, .generated-box h2, .generated-box h3 {
    color: #ffffff;
}

/* Scrollbar */
::-webkit-scrollbar-thumb { background: #334155; }

/* Hero Inner Layout */
.hero-inner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
}

.hero-text {
    text-align: left;
    flex: 1;
    min-width: 260px;
}

.hero-char-img {
    height: 220px;
    width: auto;
    object-fit: contain;
    border-radius: 24px;
    filter: drop-shadow(0 8px 32px rgba(255,255,255,0.10));
    animation: fadeInUp 0.8s ease-out;
    flex-shrink: 0;
}

@media (max-width: 700px) {
    .hero-inner { flex-direction: column; gap: 20px; }
    .hero-text { text-align: center; }
    .hero-char-img { height: 150px; }
}

/* File Uploader Custom Styling */
[data-testid="stFileUploader"] {
    background-color: rgba(18, 18, 18, 1);
    border: 2px dashed rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 30px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-top: 10px;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(255, 255, 255, 0.3);
    background-color: rgba(255, 255, 255, 0.02);
    transform: translateY(-2px);
}

[data-testid="stFileUploader"] section {
    background-color: transparent !important;
    padding: 0 !important;
}

[data-testid="stFileUploader"] label {
    display: none;
}

[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%) !important;
    color: #000000 !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    padding: 12px 24px !important;
    font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"] button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2) !important;
}

[data-testid="stFileUploaderDropzone"] {
    border: none !important;
}

[data-testid="stFileUploaderDropzone"] div div {
    color: #94a3b8 !important;
    font-family: 'Inter', sans-serif !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ---------------- #

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
            
    elif file_extension in ['docx', 'doc']:
        try:
            doc = docx.Document(uploaded_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            return f"Error reading Word document: {e}"
            
    elif file_extension == 'txt':
        try:
            return uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            return f"Error reading text file: {e}"
            
    return "Unsupported file format"

def create_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor("#000000"),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=HexColor("#333333"),
        alignment=TA_LEFT,
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor("#444444"),
        alignment=TA_LEFT,
        leading=14,
        spaceAfter=6
    )

    story = []
    
    # Very basic Markdown-ish parsing for PDF
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue
            
        if line.startswith('# '):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith('## ') or line.startswith('### '):
            story.append(Paragraph(line.lstrip('#').strip(), heading_style))
        else:
            # Handle basic bolding (simple regex replacement)
            import re
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(line, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------- HERO SECTION ---------------- #

# Load character image as base64
import os
_img_b64_path = os.path.join(os.path.dirname(__file__), "img_base64.txt")
try:
    with open(_img_b64_path, "r") as _f:
        _img_b64 = _f.read().strip()
    _img_tag = f'<img src="data:image/webp;base64,{_img_b64}" class="hero-char-img" alt="AI Teacher Character"/>'
except Exception:
    _img_tag = ""

st.markdown(f"""
<div class="hero">
    <div class="hero-inner">
        {_img_tag}
        <div class="hero-text">
            <div class="hero-title">AI Syllabus Designer</div>
            <div class="hero-subtitle">
                Generate comprehensive, professional university syllabi in seconds using state-of-the-art AI.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>AI Syllabus Designer</h2>
    </div>
    """, unsafe_allow_html=True)

    semester = st.selectbox(
        "Target Semester",
        [
            "1st Semester", "2nd Semester", "3rd Semester", "4th Semester",
            "5th Semester", "6th Semester", "7th Semester", "8th Semester"
        ]
    )

    class_name = st.selectbox(
        "Class / Year",
        ["First Year (FY)", "Second Year (SY)", "Third Year (TY)", "Final Year (LY)"]
    )

    branch = st.selectbox(
        "Academic Branch",
        ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical", "Other"]
    )

    difficulty = st.selectbox(
        "Academic Rigor",
        ["Beginner", "Intermediate", "Advanced"]
    )

    units = st.slider(
        "Total Modules / Units",
        1, 10, 5
    )



# ---------------- MAIN LAYOUT ---------------- #

# Using a single centered column for a cleaner look
_, col, _ = st.columns([1, 4, 1])

with col:

    st.markdown("""
    <div style="margin-bottom: 30px; border-left: 4px solid #ffffff; padding-left: 20px;">
        <h3 style="font-family: 'Outfit', sans-serif; color: #ffffff; margin: 0; font-size: 1.6rem; letter-spacing: -0.5px;">Subject Configuration</h3>
        <p style="color: #64748b; font-size: 0.95rem; margin: 5px 0 0 0;">Define the core details of your educational curriculum</p>
    </div>
    """, unsafe_allow_html=True)

    subject = st.text_input(
        "Subject Name",
        placeholder="e.g. Advanced Machine Learning"
    )

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    course_description = st.text_area(
        "Course Description",
        placeholder="Briefly describe the course objectives and target audience..."
    )

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 10px;">
        <h3 style="font-family: 'Outfit', sans-serif; color: #ffffff; margin: 0; font-size: 1.2rem;">Modernize Existing Syllabus (Optional)</h3>
        <p style="color: #64748b; font-size: 0.85rem; margin: 5px 0 15px 0;">Upload an old syllabus to improve and align with current curriculum</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload old syllabus (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    extracted_content = ""
    if uploaded_file:
        with st.spinner("Extracting content from uploaded syllabus..."):
            extracted_content = extract_text_from_file(uploaded_file)
            if "Error" in extracted_content:
                st.error(extracted_content)
                extracted_content = ""
            else:
                st.success(f"Successfully extracted content from {uploaded_file.name}")

    # ---------------- BUTTON ---------------- #
    st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
    generate = st.button("🚀 Generate Syllabus")

# ---------------- AI GENERATION ---------------- #

if generate:

    if subject == "":
        st.warning("Please enter subject name")

    else:

        if uploaded_file:
            prompt = f"""
            You are an expert academic curriculum designer. I am providing you with an existing, possibly outdated university syllabus for the subject '{subject}'.
            
            Your task is to MODERNIZE and IMPROVE this syllabus to align with current industry standards and academic rigor.
            
            Context Parameters:
            - Target Class: {class_name}
            - Branch: {branch}
            - Semester: {semester}
            - Target Difficulty: {difficulty}
            - Total Modules/Units: {units}
            
            Original Syllabus Content:
            ---
            {extracted_content[:4000]} # Limit to 4000 chars to avoid token issues
            ---
            
            Additional Course Description/Objectives:
            {course_description}
            
            Instructions:
            1. Keep the core foundational topics from the original syllabus.
            2. Update outdated technologies or methodologies with current state-of-the-art equivalents.
            3. Enhance the 'Learning Outcomes' and 'Practical Work' sections to be more industry-relevant.
            4. Re-organize the content into exactly {units} units as specified.
            5. Use Markdown headers (e.g., #, ##, ###) and bolding (**text**) for structure.
            6. Provide the output in a highly professional, ready-to-print academic format.
            
            Structure:
            # [Subject Name] Syllabus
            ## Course Overview
            ...
            ## Learning Outcomes (Mapped to Bloom's Taxonomy)
            ...
            ## Unit-wise Content ({units} Units)
            ...
            ## Practical & Laboratory Work
            ...
            ## Assignments & Evaluation
            ...
            ## Mini Projects
            ...
            ## Recommended Resources & Bibliography
            """
        else:
            prompt = f"""
            Generate a high-quality, professional university syllabus for the subject '{subject}'.
    
            Context:
            - Subject: {subject}
            - Class: {class_name}
            - Branch: {branch}
            - Semester: {semester}
            - Difficulty Level: {difficulty}
            - Total Units: {units}
    
            Course Description/Intent:
            {course_description}
    
            Formatting Guidelines:
            - Use Markdown headers (# for Title, ## for Sections, ### for Subsections).
            - Use bullet points for lists.
            - Ensure a balanced distribution of topics across {units} units.
            - The tone should be academic, rigorous, and inspiring.
    
            Include these exact sections:
            # {subject} - Syllabus
            ## 1. Course Description
            ## 2. Learning Objectives
            ## 3. Unit-wise Detailed Content (Total {units} Units)
            ## 4. Laboratory / Practical Work
            ## 5. Assessment & Assignment Strategy
            ## 6. Mini-Project Ideas
            ## 7. Course Learning Outcomes
            ## 8. Suggested Textbooks & Reference Materials (Latest Editions)
            """
        
        prompt += "\nMake it highly professional."

        with st.spinner("Generating professional syllabus..."):

            try:

                response = ollama.chat(
                    model="gemma:2b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                result = response["message"]["content"]

                st.success("✅ Syllabus Generated Successfully!")

                # PDF Generation
                pdf_data = create_pdf(result)
                
                st.download_button(
                    label="📥 Download Syllabus as PDF",
                    data=pdf_data,
                    file_name=f"{subject.replace(' ', '_')}_Syllabus.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.markdown(
                    f"""
                    <div class="generated-box">
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:

                st.error(f"Error during generation: {e}")