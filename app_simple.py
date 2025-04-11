import streamlit as st
import pandas as pd
import re
import json
from PIL import Image
import docx2txt
import PyPDF2
import io

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text() + '\n'
    return text

def extract_text_from_docx(file):
    text = docx2txt.process(file)
    return text

def extract_information(text):
    # Define regex patterns for information extraction
    patterns = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'education': r'(?i)\b(?:education|qualification|degree|bachelor|master|phd)\b[^.]*\.',
        'experience': r'(?i)\b(?:experience|work|employment)\b[^.]*\.',
        'skills': r'(?i)\b(?:skills|expertise|proficiency)\b[^.]*\.'
    }
    
    results = {}
    for key, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.MULTILINE)
        results[key] = [match.group(0).strip() for match in matches]
    
    return results

# Set up the Streamlit page
st.set_page_config(page_title="Resume Parser", layout="wide")

# Main title and description
st.title("📄 Quick Resume Parser")
st.markdown("""
<div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
    <h4>Upload your resume and extract key information instantly!</h4>
    <p>Supported formats: PDF, DOCX, TXT</p>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'])

if uploaded_file is not None:
    # Display file info
    st.write("### File Details")
    st.write(f"Filename: {uploaded_file.name}")
    
    # Process the file
    with st.spinner("Processing resume..."):
        try:
            # Extract text based on file type
            file_type = uploaded_file.name.split('.')[-1].lower()
            if file_type == 'pdf':
                text = extract_text_from_pdf(uploaded_file)
            elif file_type == 'docx':
                text = extract_text_from_docx(uploaded_file)
            else:  # txt file
                text = uploaded_file.getvalue().decode()
            
            # Extract information
            info = extract_information(text)
            
            # Display results
            st.write("### Extracted Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### 📧 Email Addresses")
                for email in info['email']:
                    st.write(f"- {email}")
                    
                st.write("#### 📱 Phone Numbers")
                for phone in info['phone']:
                    st.write(f"- {phone}")
            
            with col2:
                st.write("#### 🎓 Education")
                for edu in info['education']:
                    st.write(f"- {edu}")
                
                st.write("#### 💼 Experience")
                for exp in info['experience']:
                    st.write(f"- {exp}")
            
            st.write("#### 🔧 Skills")
            for skill in info['skills']:
                st.write(f"- {skill}")
            
            # Export option
            if st.button("Export as JSON"):
                export_data = {
                    'filename': uploaded_file.name,
                    'extracted_info': info
                }
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"resume_data_{uploaded_file.name}.json",
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """<div style='text-align: center; color: #666;'>
    Made with ❤️ by Indosakura
    </div>""",
    unsafe_allow_html=True
)
