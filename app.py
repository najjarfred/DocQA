import streamlit as st
from document_uploader import upload_or_select_document, displayPDF, get_highlighted_image, get_question_list
from qa_system import get_answer, display_results
import io
import time   
import base64
from PIL import Image
import pandas as pd

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
        
        model_dict = {
            "BigBird RoBERTa Base": "FredNajjar/bigbird-QA-squad_v2.2",
            "DeBERTa-V3 Large": "deepset/deberta-v3-large-squad2",
            "RoBERTa Base": "deepset/roberta-base-squad2",
            "ALBERT-V2 Base": "squirro/albert-base-v2-squad_v2",
        }

        ###### Model Selection ######
        selected_model_name = st.sidebar.selectbox(
            label="Select a Model",
            options=list(model_dict.keys()),
            index=0,  
            key="model_selection", 
            help="Select a model for question answering.")
        selected_model = model_dict[selected_model_name]

        ###### Upload or Select Document ######
        sub_text = '<p class="section-title">2- Upload or select your PDF file</p>'
        st.markdown(sub_text, unsafe_allow_html=True)
        tab = st.radio(
            label="Upload or select your PDF file",
            options=['UPLOAD', 'SELECT'],
            key="tab",
            index=0,
            help="Select or Upload a Document for processing.")
        new_context, uploaded_file_path = upload_or_select_document(tab)
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
    tab_1, tab_2 = st.tabs(["ASK", "SELECT"]) 
    
    with tab_1:
        question = st.text_input(label=" ", 
                                 placeholder="Type your question here...")

    with tab_2:
        reverse_model_dict = {v: k for k, v in model_dict.items()}
        selected_model_name = reverse_model_dict.get(selected_model, selected_model)
        question_records = get_question_list(st.session_state.uploaded_file_path, selected_model_name)
        if question_records:
            selected_record = st.selectbox(
                label="Select a question",
                options=question_records,
                format_func=lambda record: record["Question"],
                index=0,
                key="question_selection"
            )
            # Access record elements as dictionary keys
            question = selected_record["Question"]
            gold_answer = selected_record["Gold Answer"]
            selected_model = selected_record["Model Name"] 
            confidence = selected_record["Confidence"]
            time_taken = selected_record["Time"]
            search_sentence = selected_record["Search Sentence"]
            # Check if the gold answer is not nan or empty
            if not pd.notna(gold_answer) or not gold_answer.strip():
                st.error(f"The answer to the question \"{question}\" cannot be found in the given document.")
                return  # Stop further execution for this tab

        else:
            st.error("There are no questions ready for this document.")

    ###### Question Answering System ######

    if st.button(label="Submit", type="primary"):
        if not st.session_state.context:
            st.warning("Upload a document first...")
        elif not question:
            st.warning("Ask a question first...")
        else:
            start_time = time.time()
            if st.session_state.tab == "SELECT":
                mock_answer = {
                    'answer': gold_answer
                }
                display_results(mock_answer, question, confidence=confidence)
                search_term = search_sentence  # Use the 'Search Sentence' from the selected record

            else:
                with st.spinner("Processing..."):
                    result = get_answer(st.session_state.context, question, selected_model)
                    if result:
                        original_answer, search_term = result
                        display_results(original_answer, question)
                        mock_answer = original_answer  # Use the original answer for highlighting
                    else:
                        st.error(f"The answer to the question \"{question}\" cannot be found in the given document.")
                        return
    
            # Highlighting in the PDF
            if st.session_state.uploaded_file_path:
                with st.expander("Click to Unreveal Evidence"):
                    search_term_str = str(search_term) if search_term else ""
                    images = get_highlighted_image(st.session_state.uploaded_file_path, search_term_str, mock_answer['answer'].strip())
                    for img, page_number in images:
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        st.image(img_byte_arr.getvalue(), caption=f'Highlighted Page (Page {page_number})', use_column_width=True)

            end_time = time.time()  
            processing_time = end_time - start_time  


            
            if time_taken:
                if time_taken > 60:
                    processing_time_minutes = time_taken / 60
                    st.markdown(f"<small class='processing-time'>Query processed in {processing_time_minutes:.2f} mins</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<small class='processing-time'>Query processed in {time_taken:.2f} secs</small>", unsafe_allow_html=True)
                    
            elif processing_time > 60:
                processing_time_minutes = processing_time / 60
                st.markdown(f"<small class='processing-time'>Query processed in {processing_time_minutes:.2f} mins</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small class='processing-time'>Query processed in {processing_time:.2f} secs</small>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()

