from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate

from constants import TEMPLATE, MAX_TOKENS, PATH_TO_PDF


prompt_template = PromptTemplate(template=TEMPLATE, input_variables=['question'])


def parse_document(file_name):
    reader = PdfReader(open(file_name, "rb"))
    raw_text = ""
    # if document has more than one page
    for _, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text
    return raw_text


def get_splitter():
    splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return splitter


def create_docsearch(splitter, raw_text):
    texts = splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch


def get_qa_chain():
    qa_chain = load_qa_chain(
        ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=MAX_TOKENS), chain_type="stuff")
    return qa_chain


def create_answer(question):
    pars_doc = parse_document(PATH_TO_PDF)
    splitter = get_splitter()
    docsearch = create_docsearch(splitter, pars_doc)
    docs = docsearch.similarity_search(question)
    return get_qa_chain().run(question=question, input_documents=docs, prompt=prompt_template)
