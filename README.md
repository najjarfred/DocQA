 # DocQA: Document Question Answering System

 DocQA is an interactive web application built using Streamlit, designed to provide question-answering capabilities on uploaded documents. It utilizes pre-trained language models from Hugging Face's Transformers library to extract answers from PDF documents.

 # Features
 
 - **Model Selection**: Allows to copy any Extractive QA model from Hugging Face [link](https://huggingface.co/models?pipeline_tag=question-answering&sort=trending).
 - **Document Upload**: Users can upload PDF documents to the system.
 - **Interactive Q&A**: Users can ask questions and receive answers based on the content of the uploaded document.
 - **Highlighted Answers**: The application highlights answers directly in the uploaded document for better context.

# Demo

A demo of the system functionalities can be found [here](https://www.youtube.com/watch?v=E1wZno7TTo8&t=3s&ab_channel=FredNajjar)

 # Installation

 1. **Clone the Repository**

    ```bash
    git clone https://github.com/najjarfred/DocQA.git
    cd DocQA
    ```

 2. **Install Dependencies**

    Ensure you have Python 3.6+ installed, then run:

    ```bash
    pip install -r requirements.txt
    ```

    This will install Transfomers, Pinecone, Streamlit, PyPDF2, Pandas, and other necessary libraries.

 # Usage

 To run the application:

 ```bash
 streamlit run app.py
 ```

 Navigate to the local URL provided by Streamlit, typically `http://localhost:8501`.

 # How It Works

 - **Upload a PDF**: Start by uploading a PDF file.
 - **Select a Model**: Choose a question-answering model from the sidebar.
 - **Ask Questions**: Type your question into the input box.
 - **View Answers**: The application processes the document and displays the answer, highlighting the relevant section in the document.

 # File Structure

 - `app.py`: Main Streamlit application script.
 - `document_uploader.py`: Handles document uploading and processing.
 - `qa_system.py`: Contains the logic for the question-answering system using Hugging Face models.
 - `requirements.txt`: Lists all the Python libraries that the project depends on.
 - `style.css`: Contains custom CSS for styling the Streamlit app.

 # Contributing

 Contributions to DocQA are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

 # Acknowledgements

 - [BigBird](https://arxiv.org/abs/2007.14062) for the pre-trained QA model.
 - [Streamlit](https://www.streamlit.io/) for the web framework.
 - [Hugging Face's Transformers](https://huggingface.co/transformers/) for pre-trained models.
 - [PyPDF2](https://pythonhosted.org/PyPDF2/) for handling PDF files.

