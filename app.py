import streamlit as st
from PIL import Image
import io
import os
import base64
import config
from groq import Groq

# Set up the Groq API client
client = Groq(api_key=config.api_key)

# Page Configuration
st.set_page_config(
    page_title="LaTeX OCR with Llama 3.2 Vision",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and Description
st.title("🦙 LaTeX OCR with Llama 3.2 Vision")
st.markdown(
    '<p style="margin-top: -10px;">Extract LaTeX code from images using Llama 3.2 Vision!</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Sidebar Upload Section
with st.sidebar:
    st.header("Upload Image 📷")
    uploaded_file = st.file_uploader(
        "Choose an image...", type=["png", "jpg", "jpeg"]
    )

# Clear Button to reset the app state
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear 🗑️"):
        st.session_state.pop("ocr_result", None)
        st.session_state.pop("uploaded_image", None)
        st.rerun()

# If an image is uploaded
if uploaded_file:
    st.markdown("### Uploaded Image")
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Uploaded Image", use_container_width=True)

    # Convert image to base64 to send to the API
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Extract LaTeX Button
    if st.button("Extract LaTeX 🔍"):
        with st.spinner("Processing image..."):
            try:
                # API call to Groq Llama 3.2 Vision
                completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", 
                                 "text": """Understand the mathematical equation in the provided image and output the corresponding LaTeX code.
                                        Here are some guidelines you MUST follow or you will be penalized:
                                        - NEVER include any additional text or explanations.
                                        - DON'T add dollar signs ($) around the LaTeX code.
                                        - DO NOT extract simplified versions of the equations.
                                        - NEVER add documentclass, packages or begindocument.
                                        - DO NOT explain the symbols used in the equation.
                                        - Output only the LaTeX code corresponding to the mathematical 
                                        equations in the image."""},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                )

                # Store the LaTeX result in session state
                st.session_state["ocr_result"] = completion.choices[0].message.content

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display Results
if "ocr_result" in st.session_state:
    st.markdown("### Extracted LaTeX Code")
    st.markdown("###### Please remember to remove the first two symbols from first and last of the output")
    st.code(st.session_state["ocr_result"], language="latex")

    # Render LaTeX (cleaned)
    st.markdown("### Rendered Output")
    cleaned_latex = st.session_state["ocr_result"].replace("\\[", "").replace("\\]", "")
    st.latex(cleaned_latex)

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using Llama 3.2 Vision | [Report an Issue](mailto:alwin.rajkumar@louisville.edu)"
)
