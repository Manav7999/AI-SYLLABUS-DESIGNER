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

def create_pdf(text, university="", session="", year="", branch="", semester="", subject_name=""):
    import re as _re
    from reportlab.platypus import Table, TableStyle, HRFlowable, BaseDocTemplate, PageTemplate, Frame
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

    LM, RM, TM, BM = 54, 54, 58, 46
    PW, PH = letter
    CW = PW - LM - RM

    buffer = io.BytesIO()

    NAVY  = HexColor("#0d1b4b")
    DGREY = HexColor("#2d2d2d")
    LGREY = HexColor("#f3f4f8")
    ACC   = HexColor("#1a3a8f")

    def _on_page(canv, doc):
        canv.saveState()
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(0.5)
        canv.line(LM, PH - 34, PW - RM, PH - 34)
        if university:
            canv.setFont("Helvetica", 7)
            canv.setFillColor(HexColor("#666666"))
            canv.drawRightString(PW - RM, PH - 26, university.upper())
        canv.line(LM, BM - 6, PW - RM, BM - 6)
        canv.setFont("Helvetica", 8)
        canv.setFillColor(HexColor("#999999"))
        canv.drawRightString(PW - RM, BM - 17, "Page %d" % doc.page)
        if subject_name:
            canv.setFont("Helvetica-Oblique", 7.5)
            canv.setFillColor(HexColor("#999999"))
            canv.drawString(LM, BM - 17, subject_name)
        canv.restoreState()

    frame = Frame(LM, BM, CW, PH - TM - BM, id="main", showBoundary=0)
    pt    = PageTemplate(id="std", frames=[frame], onPage=_on_page)
    doc2  = BaseDocTemplate(
        buffer, pagesize=letter,
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
        pageTemplates=[pt]
    )

    sty = getSampleStyleSheet()
    def _ps(name, **kw):
        parent = kw.pop("parent", sty["Normal"])
        return ParagraphStyle(name, parent=parent, **kw)

    P = {
        "college": _ps("_coll", fontSize=21, fontName="Helvetica-Bold",
                        textColor=NAVY, alignment=TA_CENTER, leading=25),
        "meta_l":  _ps("_ml",   fontSize=9.5, fontName="Helvetica",
                        textColor=DGREY, alignment=TA_LEFT,  leading=15),
        "meta_r":  _ps("_mr",   fontSize=9.5, fontName="Helvetica",
                        textColor=DGREY, alignment=TA_RIGHT, leading=15),
        "subj":    _ps("_sub",  fontSize=13,  fontName="Helvetica-Bold",
                        textColor=colors.white, alignment=TA_CENTER, leading=17),
        "sec":     _ps("_sec",  fontSize=11.5, fontName="Helvetica-Bold",
                        textColor=NAVY, alignment=TA_LEFT, leading=15, leftIndent=10),
        "h3":      _ps("_h3",   fontSize=10.5, fontName="Helvetica-Bold",
                        textColor=ACC,  alignment=TA_LEFT, leading=14,
                        spaceBefore=8, spaceAfter=3),
        "body":    _ps("_body", fontSize=10, fontName="Helvetica",
                        textColor=DGREY, alignment=TA_JUSTIFY, leading=15.5, spaceAfter=5),
        "prac":    _ps("_prac", fontSize=10, fontName="Helvetica",
                        textColor=DGREY, alignment=TA_LEFT, leading=15,
                        spaceAfter=5, leftIndent=20, firstLineIndent=-20),
        "bull":    _ps("_bull", fontSize=10, fontName="Helvetica",
                        textColor=DGREY, alignment=TA_LEFT, leading=14,
                        spaceAfter=3, leftIndent=14),
    }

    def _c(t):
        t = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
        t = _re.sub(r'\*(.*?)\*',     r'<i>\1</i>', t)
        t = t.replace('`', '').replace('&', '&amp;')
        return t

    def _sh(txt):
        tbl = Table([[Paragraph(_c(txt), P["sec"])]], colWidths=[CW])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), LGREY),
            ("LINEBEFORE",    (0, 0), (0,  -1), 4, NAVY),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ]))
        return tbl

    story = []
    story.append(Spacer(1, 2))
    story.append(Paragraph(university.upper() if university else "UNIVERSITY SYLLABUS", P["college"]))
    story.append(Spacer(1, 7))
    story.append(HRFlowable(width="100%", thickness=2.5, color=NAVY, spaceAfter=9))

    L, R = [], []
    if branch:   L.append("<b>Branch   :</b>  " + branch)
    if semester: L.append("<b>Semester :</b>  " + semester)
    if session:  L.append("<b>Session  :</b>  " + session)
    if year:     R.append("<b>Year :</b>  " + year)

    itbl = Table(
        [[Paragraph("<br/>".join(L) or "&nbsp;", P["meta_l"]),
          Paragraph("<br/>".join(R) or "&nbsp;", P["meta_r"])]],
        colWidths=[CW * 0.62, CW * 0.38]
    )
    itbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(itbl)
    story.append(Spacer(1, 9))
    story.append(HRFlowable(width="100%", thickness=0.7, color=HexColor("#c0c0c0"), spaceAfter=10))

    if subject_name:
        stbl = Table([[Paragraph(subject_name.upper(), P["subj"])]], colWidths=[CW])
        stbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))
        story.append(stbl)
        story.append(Spacer(1, 14))

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            story.append(Spacer(1, 3)); i += 1; continue

        if s.startswith("|") and i + 1 < len(lines) and lines[i+1].strip().startswith("|---"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(_re.fullmatch(r"[-: ]+", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                nc = max(len(r) for r in rows)
                rows = [r + [""] * (nc - len(r)) for r in rows]
                cw2 = CW / nc
                tbl = Table(rows, colWidths=[cw2] * nc, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ("BACKGROUND",     (0, 0), (-1, 0),  NAVY),
                    ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
                    ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
                    ("FONTSIZE",       (0, 0), (-1, -1), 8.5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LGREY, colors.white]),
                    ("GRID",           (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
                    ("ALIGN",          (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING",     (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
                    ("LEFTPADDING",    (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
                ]))
                story.append(Spacer(1, 4))
                story.append(tbl)
                story.append(Spacer(1, 6))
            continue

        if s.startswith("# ") and not s.startswith("## "):
            i += 1; continue
        elif s.startswith("## "):
            story.append(Spacer(1, 5))
            story.append(_sh(s[3:]))
            story.append(Spacer(1, 5))
        elif s.startswith("### "):
            story.append(Paragraph(_c(s[4:]), P["h3"]))
        elif _re.match(r"^\d+[.)]\s", s):
            story.append(Paragraph(_c(s), P["prac"]))
        elif s[:2] in ("- ", "* "):
            story.append(Paragraph("\u2022  " + _c(s[2:]), P["bull"]))
        else:
            story.append(Paragraph(_c(s), P["body"]))
        i += 1

    doc2.build(story)
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

    university_name = st.text_input(
        "University / College Name",
        placeholder="e.g. University of Mumbai"
    )
    academic_session = st.text_input(
        "Academic Session",
        placeholder="e.g. 2024 - 2025"
    )

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
        st.warning("Please enter a subject name before generating.")

    else:

        univ_line    = ("University: " + university_name) if university_name else ""
        session_line = ("Session: " + academic_session)   if academic_session else ""
        ctx = (
            "Subject: " + subject + " | " + branch + " | " + semester +
            " | " + class_name + " | Difficulty: " + difficulty + "\n" +
            univ_line + "\n" + session_line + "\n" +
            "Course intent: " + (course_description or "Standard university course.")
        )
        old_syl = ("\nOLD SYLLABUS REFERENCE:\n" + extracted_content[:1400]) if (uploaded_file and extracted_content) else ""

        def ask(prompt_text, tokens=600):
            r = ollama.chat(
                model="gemma:2b",
                messages=[{"role": "user", "content": prompt_text}],
                options={
                    "num_predict":    tokens,
                    "num_ctx":        4096,
                    "temperature":    0.65,
                    "repeat_penalty": 1.3,
                    "repeat_last_n":  64,
                }
            )
            return r["message"]["content"].strip()

        total_steps = 1 + units + 2   # overview + N units + practicals + summary
        step        = 0
        parts       = []
        bar         = st.progress(0, text="Starting generation...")

        try:
            # PASS 1: Course Overview  (3 rich paragraphs)
            bar.progress(step / total_steps, text="Writing Course Overview...")
            ov = ask(
                "Write a detailed Course Overview for the university subject '" + subject + "'.\n" +
                ctx + old_syl + "\n\n" +
                "Write exactly 3 paragraphs in formal academic English:\n"
                "Paragraph 1: Describe the subject scope, its place in the curriculum, and what makes it important.\n"
                "Paragraph 2: List and explain the key themes and concepts students will study.\n"
                "Paragraph 3: Describe prerequisites, target audience, and real-world career applications.\n"
                "No bullet points. No headings. Minimum 250 words total.",
                tokens=700
            )
            parts.append("## Course Overview\n\n" + ov)
            step += 1

            # PASS 2: One API call per unit
            for u in range(1, units + 1):
                bar.progress(step / total_steps, text="Writing Unit " + str(u) + " of " + str(units) + "...")
                ut = ask(
                    "Write Unit " + str(u) + " of " + str(units) +
                    " for a university syllabus on '" + subject + "'.\n" + ctx + "\n\n" +
                    "Start with: ## UNIT " + str(u) + " - [descriptive academic title]\n" +
                    "Then write a rich, detailed academic description of this unit in 200-250 words. "
                    "Cover: the main topics and subtopics, key theories and concepts, "
                    "important algorithms or methodologies, and how these connect to real-world applications. "
                    "Write as continuous academic prose. No bullet points. No sub-headings.",
                    tokens=700
                )

                # ── Normalize the unit heading to ensure correct order ──────
                import re as _re2
                ut_lines = ut.split("\n")
                heading_found = False
                fixed_lines = []
                for ln in ut_lines:
                    if not heading_found and ln.strip().startswith("##"):
                        heading_found = True
                        # Extract the title text after any existing "UNIT N" prefix
                        raw_title = ln.strip().lstrip("#").strip()
                        raw_title = _re2.sub(
                            r"^(?:unit|u)\s*\d+\s*[-:.–]?\s*",
                            "", raw_title, flags=_re2.IGNORECASE
                        ).strip()
                        if not raw_title:
                            raw_title = "Core Concepts and Principles"
                        fixed_lines.append("## UNIT " + str(u) + " - " + raw_title)
                    else:
                        fixed_lines.append(ln)
                if not heading_found:
                    # Model gave no heading — insert one
                    fixed_lines.insert(0, "## UNIT " + str(u) + " - Unit " + str(u) + " Content")
                ut = "\n".join(fixed_lines)
                # ───────────────────────────────────────────────────────────

                parts.append(ut)
                step += 1


            # PASS 3a: Laboratory Practicals (dedicated call for full detail)
            bar.progress(step / total_steps, text="Writing Laboratory Practicals...")
            prac = ask(
                "Write 12 Laboratory Practicals for the university subject '" + subject + "'.\n" +
                ctx + "\n\n" +
                "Number each practical 1 to 12. For each practical write:\n"
                "[Number]. [Practical Title]\n"
                "Aim: [One clear sentence stating what the student will achieve.]\n"
                "Procedure: [Two to three sentences describing the steps involved, tools used, and expected output.]\n\n"
                "Start immediately with '## Laboratory Practicals' then list all 12.",
                tokens=1300
            )
            parts.append(prac)
            step += 1

            # PASS 3b: Summary (separate call so it is never cut off)
            bar.progress(step / total_steps, text="Writing Summary...")
            summ = ask(
                "Write a Syllabus Summary for the university subject '" + subject + "'.\n" +
                ctx + "\n\n" +
                "Start with the heading: ## Summary\n"
                "Then write 2 solid paragraphs in formal academic English:\n"
                "Paragraph 1: Summarise what students will learn across all units and practicals.\n"
                "Paragraph 2: Explain the career outcomes, industry relevance, and higher study pathways this subject enables.\n"
                "No bullet points. Minimum 150 words.",
                tokens=450
            )
            parts.append(summ)
            bar.progress(1.0, text="Done!")

            result = "\n\n".join(parts)
            st.success("Syllabus Generated Successfully!")

            pdf_data = create_pdf(
                result,
                university   = university_name,
                session      = academic_session,
                year         = class_name,
                branch       = branch,
                semester     = semester,
                subject_name = subject
            )
            st.download_button(
                label="Download Syllabus as PDF",
                data=pdf_data,
                file_name=subject.replace(" ", "_") + "_Syllabus.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            import markdown as md_lib
            result_html = md_lib.markdown(result, extensions=["tables", "fenced_code", "nl2br"])
            st.markdown('<div class="generated-box">' + result_html + '</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("Error during generation: " + str(e))
