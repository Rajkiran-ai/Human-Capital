import streamlit as st
import pandas as pd
import re
import json
from PIL import Image
import docx2txt
import PyPDF2
import io

# Now import the installed packages
import pandas as pd
import numpy as np
import re
import json
from PIL import Image
import docx2txt
import pdfplumber
from PyPDF2 import PdfReader
# Initialize NLP components
try:
    import spacy
    import nltk
    from langdetect import detect
    
    # Suppress warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    # Download NLTK data silently
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
    
    # Load spaCy model
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        st.error("Error loading spaCy model. Please restart the application.")
        nlp = None
        
except Exception as e:
    st.error(f"Error initializing NLP components: {str(e)}")
    nlp = None

# Initialize EasyOCR reader
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'])

def extract_text_from_image(image):
    reader = load_ocr_reader()
    results = reader.readtext(np.array(image))
    return ' '.join([text[1] for text in results])

def process_resume(file, file_type):
    try:
        if file_type in ['jpg', 'jpeg', 'png']:
            # Process image files
            image = Image.open(file)
            text = extract_text_from_image(image)
        elif file_type == 'pdf':
            # Process PDF files
            pdf = PdfReader(file)
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        elif file_type == 'docx':
            # Process DOCX files
            text = docx2txt.process(file)
        elif file_type == 'txt':
            # Process text files
            text = file.getvalue().decode('utf-8')
        else:
            return None, 'Unsupported file format'

        # Process extracted text with spaCy
        if nlp is not None:
            doc = nlp(text)
            # Extract entities
            entities = {
                'names': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
                'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
                'locations': [ent.text for ent in doc.ents if ent.label_ == 'GPE'],
                'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            }
            return text, entities
        return text, None
    except Exception as e:
        return None, str(e)

# Streamlit UI setup
st.set_page_config(
    page_title="Indosakura HCM - Resume Parser",
    page_icon="📄",
    layout="wide"
)

# Main page header
st.title("📄 Indosakura Human Capital Management")
st.markdown("""<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
    <h4>Welcome to the Resume Management System</h4>
    <p>Upload resumes in various formats and extract key information automatically.</p>
    </div>""", unsafe_allow_html=True)

# File upload section
st.write("")
st.subheader("Upload Resume")
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Supported formats: PDF, DOCX, TXT, and Images (JPG, PNG)",
        type=["pdf", "docx", "txt", "jpg", "jpeg", "png"]
    )

with col2:
    st.markdown("""<div style='background-color: #e8f4ea; padding: 15px; border-radius: 5px;'>
        <h5>Features:</h5>
        <ul>
            <li>Multiple format support</li>
            <li>Text extraction</li>
            <li>Entity recognition</li>
            <li>Data export</li>
        </ul>
        </div>""", unsafe_allow_html=True)

# Process uploaded file
if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    st.write("---")
    
    # Show file details
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("### File Details")
        st.write(f"**Name:** {uploaded_file.name}")
        st.write(f"**Type:** {file_type.upper()}")
        st.write(f"**Size:** {uploaded_file.size/1024:.2f} KB")
    
    # Process the file
    with st.spinner('Processing resume...'):
        extracted_text, entities = process_resume(uploaded_file, file_type)
        
        if extracted_text is not None:
            # Show extracted text
            with st.expander("View Extracted Text", expanded=False):
                st.text_area("Content", extracted_text, height=200)
            
            # Show entities if available
            if entities:
                st.write("### Extracted Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("#### Names Found")
                    for name in entities['names']:
                        st.write(f"- {name}")
                    
                    st.write("#### Organizations")
                    for org in entities['organizations']:
                        st.write(f"- {org}")
                
                with col2:
                    st.write("#### Locations")
                    for loc in entities['locations']:
                        st.write(f"- {loc}")
                    
                    st.write("#### Dates")
                    for date in entities['dates']:
                        st.write(f"- {date}")
                
                # Export option
                if st.button("Export Data as JSON"):
                    export_data = {
                        'file_name': uploaded_file.name,
                        'extracted_entities': entities,
                        'full_text': extracted_text
                    }
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"resume_data_{uploaded_file.name}.json",
                        mime="application/json"
                    )
        else:
            st.error(f"Error processing file: {entities}")

# Footer
st.markdown("---")
st.markdown(
    """<div style='text-align: center; color: #666;'>
    © 2025 Indosakura Human Capital Management. All rights reserved.
    </div>""",
    unsafe_allow_html=True
)

with col2:
    if uploaded_file is not None:
        # Display file details
        file_details = {
            "Filename": uploaded_file.name,
            "File type": uploaded_file.type,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("### File Details:")
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")

# Handle uploaded file
if uploaded_file is not None:
    try:
        # Open and display the image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Resume', use_column_width=True)
        
        # Process the image
        with st.spinner('Extracting information from image...'):
            extracted_info = process_resume_image(image)
        
        # Display extracted information
        st.write("### Extracted Information")
        
        # Create two columns for information display
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Personal Details")
            st.write(f"**Name:** {extracted_info['name']}")
            st.write(f"**Email:** {extracted_info['email']}")
            st.write(f"**Phone:** {extracted_info['phone']}")
        
        with col2:
            st.write("#### Professional Details")
            st.write(f"**Education:** {extracted_info['education']}")
            st.write(f"**Experience:** {extracted_info['experience']}")
            st.write(f"**Skills:** {extracted_info['skills']}")
        
        # Export option
        if st.button("Export as JSON"):
            json_data = json.dumps(extracted_info, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"resume_data_{uploaded_file.name}.json",
                mime="application/json"
            )
            
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: grey;'>
    © 2025 Indosakura Human Capital Management. All rights reserved.
</div>
""", unsafe_allow_html=True)