import os
from dotenv import load_dotenv

load_dotenv()
from langchain_community.document_loaders import (
    WebBaseLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
)
from youtube_transcript_api import YouTubeTranscriptApi, TranslationLanguageNotAvailable

import os
from dotenv import load_dotenv

load_dotenv()
user_agent = os.getenv("USER_AGENT")


def carrega_site(url):
    loader = WebBaseLoader(url)
    lista_documentos = loader.load()
    documento = "\n\n".join([doc.page_content for doc in lista_documentos])
    return documento


def carrega_youtube(video_id: str):
    ytt = YouTubeTranscriptApi()
    tl = ytt.list(video_id)
    try:
        fetched = ytt.fetch(video_id, languages=["pt", "pt-BR", "en"])
        raw = fetched.to_raw_data()
    except TranslationLanguageNotAvailable:
        tr = tl.find_transcript(["en"])
        if tr.is_translatable:
            fetched = tr.translate("pt").fetch()
            raw = fetched.to_raw_data()
        else:
            raw = tr.fetch().to_raw_data()
    texto = "\n".join(s["text"] for s in raw)
    return texto


def carrega_csv(caminho):
    loader = CSVLoader(caminho, encoding="utf-8")
    lista_documentos = loader.load()
    documento = "\n\n".join([doc.page_content for doc in lista_documentos])
    return documento


def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = "\n\n".join([doc.page_content for doc in lista_documentos])
    return documento


def carrega_txt(caminho):
    loader = TextLoader(caminho, autodetect_encoding=True, encoding="utf-8")
    lista_documentos = loader.load()
    documento = "\n\n".join([doc.page_content for doc in lista_documentos])
    return documento


# Exemplo de uso da nova função:
doc = "arquivos/knowledge_base.txt"
print(carrega_txt(doc))
