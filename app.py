import streamlit as st
from document_uploader import upload_or_select_document, displayPDF, get_highlighted_image, get_question_list
from qa_system import get_answer, display_results
import io
import time   
import base64
from PIL import Image

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
        st.session_state.tab = "SELECT"

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
            "DeBERTa-V3 Large": "deepset/deberta-v3-large-squad2",
            "RoBERTa Base": "deepset/roberta-base-squad2",
            "ALBERT-V2 Base": "squirro/albert-base-v2-squad_v2",
            "BigBird RoBERTa Base": "FredNajjar/bigbird-QA-squad_v2.2"
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
            options=['SELECT', 'UPLOAD'],
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
        questions = get_question_list(st.session_state.uploaded_file_path)
        if questions:
            question = st.selectbox(label=" ", 
                                    options=questions, 
                                    index=0, 
                                    key="question_selection")
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

            with st.spinner("Processing..."):
                result = get_answer(st.session_state.context, question, selected_model)
                if result:
                    original_answer, search_term = result  
                    display_results(original_answer, question)
                    if st.session_state.uploaded_file_path:
                        with st.expander("Click to Unreveal Evidence"):  
                            images = get_highlighted_image(st.session_state.uploaded_file_path, search_term, original_answer['answer'].strip())
                            for img, page_number in images:
                                img_byte_arr = io.BytesIO()
                                img.save(img_byte_arr, format='PNG')
                                st.image(img_byte_arr.getvalue(), caption=f'Highlighted Page (Page {page_number})', use_column_width=True)
                else:
                    answer_text = f'The answer to the question "{question}" cannot be found in the given document.'
                    st.error(answer_text)

            end_time = time.time()  
            processing_time = end_time - start_time  

            if processing_time > 60:
                processing_time_minutes = processing_time / 60
                st.markdown(f"<small class='processing-time'>Query processed in {processing_time_minutes:.2f} mins</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small class='processing-time'>Query processed in {processing_time:.2f} secs</small>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()

