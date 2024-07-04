import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import base64
import streamlit as st
import io
from PIL import Image 
import pdf2image
from google.generativeai import GenerativeModel

# Configure API key
api_key = os.getenv("GOOGLE_API_KEY")

# Function to convert PDF to images and base64 encode
def convert_pdf_to_images(uploaded_file):
    poppler_path = r"C:\Users\agrsm\Downloads\poppler-24.07.0\bin"  # Update with your Poppler bin path
    images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)
    pdf_parts = []
    for img in images:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        pdf_parts.append({
            "image": img,  # Store image object for display
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
        })
    return pdf_parts

# Function to get response from GenerativeModel
def get_gemini_response(input_text, pdf_content, prompt):
    model = GenerativeModel('gemini-pro-vision', api_key=api_key)
    response = model.generate_content([input_text, pdf_content[0]['data'], prompt])
    return response.text

# Main Streamlit App
def main():
    # Streamlit App settings
    st.set_page_config(page_title="ATS Resume Expert", page_icon=":memo:")
    st.title("ATS Tracking System")

    # Sidebar for user options
    st.sidebar.title("Options")
    input_text = st.sidebar.text_area("Job Description:", key="input")
    show_images = st.sidebar.checkbox("Show Resume Images")
    show_analysis = st.sidebar.checkbox("Show Analysis Results")

    # Resume upload
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    # Display uploaded file message
    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")

    # Button to analyze resume against job description
    if st.button("Analyse Resume"):
        if not input_text:
            st.error("Please enter a job description.")
        elif uploaded_file is None:
            st.error("Please upload a resume.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Convert PDF to images and base64 encode
                    pdf_content = convert_pdf_to_images(uploaded_file)

                    # Get response from GenerativeModel
                    response = get_gemini_response(input_text, pdf_content, input_text)

                    # Display resume images if checkbox is checked
                    if show_images:
                        st.subheader("Resume Pages:")
                        for page in pdf_content:
                            st.image(page['image'])

                    # Display analysis results if checkbox is checked
                    if show_analysis:
                        st.subheader("Analysis Results:")
                        st.write(response)

                    # Additional features - Keyword highlighting, skill analysis, summary
                    st.subheader("Additional Features:")
                    if st.checkbox("Keyword Highlighting"):
                        st.write("Keyword highlighting feature coming soon...")

                    if st.checkbox("Skill Analysis"):
                        st.write("Skill analysis feature coming soon...")

                    if st.checkbox("Summary and Recommendations"):
                        st.write("Summary and recommendations feature coming soon...")

                except pdf2image.exceptions.PDFPageCountError:
                    st.error("Error: Unable to read the PDF. Please make sure the PDF is not corrupted or protected.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Footer
    st.markdown("---")
    st.markdown("Created with ❤️ by Aditya")

# Run the main function to start the Streamlit app
if __name__ == "__main__":
    main()
