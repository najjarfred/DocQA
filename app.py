import streamlit as st
from document_uploader import upload_or_select_document, displayPDF, get_highlighted_image, get_question_list
from qa_system import get_answer, display_results
import io
import time
import base64
from PIL import Image
import pandas as pd
import re

###### Setup UI Function ######
def setup_ui():
    st.set_page_config(page_title="Capstone DATA5709 - Doc QA",
                       page_icon="logo.ico")

###### Main Function ######
def main():

    ###### Session State ######
    if 'context' not in st.session_state:
        st.session_state.context = ""

    if 'uploaded_file_path' not in st.session_state:
        st.session_state['uploaded_file_path'] = None

    if 'tab' not in st.session_state:
        st.session_state.tab = "UPLOAD"

    ###### Setup UI ######
    setup_ui()

    ###### Read CSS ######
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    ###### Sidebar ######
    with st.sidebar:
        st.markdown(
            '<p class="original-title">Document Question Answering</p>', 
            unsafe_allow_html=True)

        st.markdown(
            '<p class="credit-text">Capstone DATA5709 by <a href="https://www.linkedin.com/in/frednajjar/" target="https://www.linkedin.com/in/frednajjar/" class="credit-link">Fred Najjar</a></p>', 
            unsafe_allow_html=True)

        sub_text = (
            '<p class="sub-text">Document Question Answering is a tool that allows you '
            'to ask questions about a document and get answers. The tool uses a pre-trained '
            'large language model to extract answers from a given document. You can upload a '
            'PDF file or select a file from the list of available files.</p>')
        st.markdown(sub_text, unsafe_allow_html=True)
        
        sub_text = '<p class="section-title">1- Select a Model</p>'
        st.markdown(sub_text, unsafe_allow_html=True)

        ###### Model Selection ######
        selected_model = st.sidebar.text_input(
            label="Enter a Model Name",
            value="FredNajjar/bigbird-QA-squad_v2.2",  # Default value
            key="model_selection",
            help="You can enter any QA model from Hugging Face hub"
        )

        if not selected_model:
            st.sidebar.error("Invalid model name. Try another QA model.")
        
        st.markdown("", unsafe_allow_html=True)
        
        ###### Upload a Document ######
        sub_text = '<p class="section-title">2- Upload your PDF file</p>'
        st.markdown(sub_text, unsafe_allow_html=True)

        new_context, uploaded_file_path = upload_or_select_document('UPLOAD')
        if new_context:
            st.session_state.context = new_context
        if uploaded_file_path:
            st.session_state.uploaded_file_path = uploaded_file_path


        ###### Logo ######
        with open("logo.png", "rb") as f:
            logo_data = f.read()
        logo_data_url = f"data:image/png;base64,{base64.b64encode(logo_data).decode()}"

        st.markdown(
            f'''
            <div class="logo-container">
                <img src="{logo_data_url}" alt="Logo" class="logo-image">
            </div>
            ''',
            unsafe_allow_html=True)

    ###### Main Area ######
    if st.session_state.uploaded_file_path:
        displayPDF(st.session_state.uploaded_file_path)

    ###### Question Input ######
    question = st.text_input(label=" ", 
                             placeholder="Type your question here...")

    ###### Question Answering System ######

    if st.button(label="Submit", type="primary"):
        if not selected_model:
            st.error("Please type in a model name first...")
        elif not st.session_state.context:
            st.warning("Upload a document first...")
        elif not question:
            st.warning("Ask a question first...")
        else:
            try: 
                start_time = time.time()
                with st.spinner("Processing..."):
                    result = get_answer(st.session_state.context, question, selected_model)
                    if result:
                        original_answer, search_term = result
                        display_results(original_answer, question)
                    else:
                        st.error(f"The answer to the question \"{question}\" cannot be found in the given document.")
                        return

                # Highlighting in the PDF
                if st.session_state.uploaded_file_path:
                    with st.expander("Click to Unreveal Evidence"):
                        search_term_str = str(search_term) if search_term else ""
                        images = get_highlighted_image(st.session_state.uploaded_file_path, search_term_str, original_answer['answer'].strip())
                        for img, page_number in images:
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            st.image(img_byte_arr.getvalue(), caption=f'Highlighted Page (Page {page_number})', use_column_width=True)

                end_time = time.time()  
                processing_time = end_time - start_time

                if processing_time > 60:
                    processing_time_minutes = processing_time / 60
                    st.markdown(f"<small class='processing-time'>Query processed in {processing_time_minutes:.2f} mins</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<small class='processing-time'>Query processed in {processing_time:.2f} secs</small>", unsafe_allow_html=True)

            except ValueError as ve:
                st.error(f'The model "{selected_model}" is not compatible. Try another model.')
            except OSError as oe:
                st.error(f"Error with the model: {selected_model}. Make sure it's a valid model identifier or try another model.")
            except Exception as e:
                # General catch-all for other unforeseen errors
                st.error(f'An error occurred when loading "{selected_model}". Please Try another model.')


if __name__ == "__main__":
    main()
