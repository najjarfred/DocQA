###### Import Section ######
# Importing necessary libraries and modules to create the Streamlit app, process PDFs and images
import streamlit as st
import PyPDF2
import pandas as pd
import os
import tempfile
import io
import base64
import fitz 
from PIL import Image  


###### Storage Class ######
class Storage:
    """ 
    
    A class that provides methods for file handling, used to provide a list of files and retrieve the content of a file.
    
    """
    
    def list(self):
        return ['Healthcare.pdf', 'Education.pdf']

    def get(self, name):
        try:
            with open(os.path.join(os.getcwd(), f"Files\{name}"), 'rb') as file:
                return file.read()
        except Exception as e:
            st.warning(f"Error retrieving the file {name}: {e}")
            return None

###### Extract Content Function ######
def extract_content_from_uploaded_file(file_content, file_type):
    """
    Extracts text from an uploaded file's content if it is a PDF file.

    This function reads the content of an uploaded file using PyPDF2 if the file is identified as a PDF by its MIME type ('application/pdf').
    It iterates through each page of the PDF and extracts the text, concatenating it into a single string. If an error occurs during the extraction process, a warning is displayed with the error message.

    Args:
        file_content: The content of the uploaded file in bytes, typically read from a file upload handler.
        file_type: The MIME type of the file, used to verify if the file is a PDF.

    Returns:
        A string containing the concatenated text extracted from the PDF file. If the file is not a PDF or an error occurs, returns an empty string.
    """

    context = ""
    if file_type == "application/pdf":
        try:
            file_stream = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(file_stream)
            for page in pdf_reader.pages:
                context += page.extract_text()
        except Exception as e:
            st.warning(f"Error extracting content: {e}")
    return context


###### Upload or Select Document Function ######
def upload_or_select_document(tab):
    """
    Provides an interface for uploading a new PDF document or selecting an existing one.
    
    This function is part of a Streamlit interface. Depending on the 'tab' argument, it either
     presents a file uploader for the user to upload a PDF file or displays a dropdown to select
     from previously uploaded PDF files. The function saves the uploaded file to a temporary location
     or retrieves the content of a selected file. It also updates the session state to track the user's
     last action ('upload' or 'select').

    Args:
        tab: Determines the mode of the function. Should be 'UPLOAD' or 'SELECT'.
             'UPLOAD' mode provides a file uploader for the user to upload a PDF.
             'SELECT' mode shows a dropdown to select from a list of available PDF files.

    Returns:
        A pair where the first element is a string containing the extracted content
         from the uploaded or selected PDF file, and the second element is the file path
         where the PDF file is saved on the server. The file path is None if no file was
         uploaded or selected.

    Note:
        - The function relies on Streamlit's session state to keep track of the last action.
        - For 'UPLOAD', the uploaded file is temporarily saved using Python's `tempfile` module.
        - For 'SELECT', the file content is retrieved from a custom `Storage` class, which is
            assumed to provide `list` and `get` methods for file handling.
        - The 'extract_content_from_uploaded_file' function is used to process the PDF file and
            extract its content; it's assumed to be defined elsewhere in the codebase.
    """
    
    
    context = ""
    file_path = None
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None

    if tab == 'UPLOAD':
        uploaded_file = st.file_uploader(label='Upload a PDF file', 
                                         type='pdf', label_visibility='hidden', 
                                         key="upload", 
                                         accept_multiple_files=False, 
                                         help="Upload a PDF file for processing.")
        if uploaded_file:
            st.session_state.last_action = "upload"
            file_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            context = extract_content_from_uploaded_file(uploaded_file.read(), uploaded_file.type)
    elif tab == 'SELECT':
        filenames = ['']
        storage = Storage()  
        filenames += storage.list()
        selected_file = st.selectbox(label='Select a file', options=filenames, index=0)
        if selected_file and selected_file != filenames[0]:
            st.session_state.last_action = "select"
            file_content = storage.get(selected_file)
            if file_content:
                context = extract_content_from_uploaded_file(file_content, "application/pdf")
                file_path = os.path.join(os.getcwd(), "Files", selected_file)
    return context, file_path


###### Display PDF Function ######
def displayPDF(file):
    
    """
    Embeds a PDF file in a Streamlit application for display.

    This function takes a file path to a PDF document, reads the document in binary mode, encodes it to base64, and then
    generates an HTML iframe that is embedded in the Streamlit app to display the PDF.

    Args:
        file: The file path to the PDF document to be displayed.
    """
    
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

###### Get Question List Function ######
def get_question_list(uploaded_file_name):
    
    """
    Extracts a list of questions from a CSV file that match the given document name.

    This function reads from a CSV file named 'question_list.csv', filters the rows where the
    'Document Name' column matches the basename of the 'uploaded_file_name', and returns a list
    of questions associated with that document.

    Args:
        uploaded_file_name: The full path or name of the uploaded file for which the question list is to be retrieved.

    Returns:
        list: A list of strings where each string is a question related to the document name provided. 
        If the CSV cannot be read, or if another exception occurs, an empty list is returned.

    Exceptions:
        Prints an error message to the console if an exception occurs while reading the CSV file.
    """
    try:
        df = pd.read_csv("question_list.csv")
        file_name = os.path.basename(uploaded_file_name) 
        filtered_df = df[df['Document Name'] == file_name]
        return filtered_df["Question"].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
    
    
###### Get Highlighted Image Function ######
def get_highlighted_image(pdf_path, search_sentence, answer):
    """
    Generates images with highlighted sections from a PDF that match the given search sentence and answer. 
    The function opens a PDF document, searches each page for the specified search sentence and answer, 
    and highlights the answer when it is in close proximity to the search sentence. If only the search 
    sentence is found, it highlights an area around this sentence. Finally, it extracts and returns 
    images of the highlighted areas.

    Args:
        pdf_path: Path to the PDF document that needs to be processed.
        search_sentence: The sentence or phrase to search for within the document, which helps to 
                          locate the context in which the answer should be highlighted.
        answer: The exact text of the answer that needs to be highlighted within the document.

    Returns:
        list: A list of tuples, each containing an image object of the highlighted area and the page 
              number where the highlight was made.
    """
    
    pdf_document = fitz.open(pdf_path)
    images = []
    proximity_threshold = 5 
    
    ## Loop through each page in the PDF document ##
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        rects_search_term = page.search_for(search_sentence)
        rects_answer = page.search_for(answer)
        
        
        if rects_search_term and rects_answer:
            for rect_search in rects_search_term:
                for rect_answer in rects_answer:
                    if abs(rect_search.y0 - rect_answer.y0) <= proximity_threshold:
                        highlight = page.add_highlight_annot(rect_answer)
                        
        ## If the search term is not found, highlight the answer ##
        if rects_search_term:  
            combined_rect = fitz.Rect(rects_search_term[0].top_left, rects_search_term[-1].bottom_right)
            combined_rect.y0 -= 50
            combined_rect.y1 += 50
            combined_rect.x0 = 0
            combined_rect.x1 = page.rect.width
            mat = fitz.Matrix(4.0, 4.0)
            pix = page.get_pixmap(clip=combined_rect, matrix=mat, dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append((img, page_number + 1))

    pdf_document.close()
    return images    
