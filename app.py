import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages, extract_text
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import HuggingFaceHub

from htmlTemplates import css, bot_template, user_template


load_dotenv()


# def get_pdf_text(pdf_docs):
#     """
#     Extract text from uploaded PDF documents.
#     If there's any error in reading a PDF, an appropriate message will be displayed.
#     """
#     text = ""
#     for pdf in pdf_docs:
#         try:
#             pdf_reader = PdfReader(pdf)
#             for page in pdf_reader.pages:
#                 extracted_text = page.extract_text()
#                 if extracted_text:  # Check if text extraction was successful
#                     text += extracted_text
#                 else:  # Sometimes, PyPDF2 may not be able to extract text
#                     st.warning(
#                         f"Failed to extract text from one of the pages in {pdf.name}."
#                     )
#         except Exception as e:
#             st.error(f"Error reading the PDF {pdf.name}: {str(e)}")
#     return text


def get_pdf_text(pdf_docs):
    """
    Extract text from uploaded PDF documents.
    If there's any error in reading a PDF, an appropriate message will be displayed.
    """
    text = ""
    for pdf in pdf_docs:
        try:
            text = extract_text(pdf)
        except Exception as e:
            st.error(f"Error reading the PDF {pdf.name}: {str(e)}")
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = ChatOpenAI(model="gpt-4")

    # llm = HuggingFaceHub(
    #     repo_id="google/flan-t5-xxl",
    #     model_kwargs={"temperature": 0.5, "max_length": 512},
    # )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.write("Please upload and process a PDF before asking a question.")
        return

    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(
                user_template.replace("{{MSG}}", message.content),
                unsafe_allow_html=True,
            )
        else:
            st.write(
                bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True
            )


def setup():
    """
    Set up the streamlit app.
    """
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    # Initialize session state variables
    if "conversation" not in st.session_state or st.session_state.conversation is None:
        default_text = "This is some default text to start the conversation."
        text_chunks = get_text_chunks(default_text)
        vectorstore = get_vectorstore(text_chunks)
        st.session_state.conversation = get_conversation_chain(vectorstore)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def display_chat_ui():
    """
    Display the main chat UI with a submit button.
    """
    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if st.button("Submit Question") and user_question:
        handle_userinput(user_question)


def sidebar_documents_upload():
    """
    Handle the document uploads in the sidebar.
    """
    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True
        )
        if st.button("Process"):
            if not pdf_docs:
                st.warning("Please upload PDF documents first.")
                return

            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)

            st.success("PDF documents processed successfully!")


def main():
    setup()
    display_chat_ui()
    sidebar_documents_upload()


if __name__ == "__main__":
    main()
