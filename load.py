import os
import re
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    WebBaseLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
)
from youtube_transcript_api import YouTubeTranscriptApi, TranslationLanguageNotAvailable

load_dotenv()
user_agent = os.getenv("USER_AGENT")


def carrega_site(url):
    loader = WebBaseLoader(url)
    lista_documentos = loader.load()
    documento = "\n\n".join(doc.page_content for doc in lista_documentos)
    return documento



def extrai_video_id(valor: str) -> str:
    """Extrai o ID do video a partir de uma URL completa, shorts ou ID puro."""
    valor = (valor or "").strip()
    if not valor:
        return ""

    parsed = urlparse(valor)
    if parsed.scheme and parsed.netloc:
        host = parsed.netloc.lower()
        path = parsed.path.strip("/")

        if host in {"youtu.be", "www.youtu.be"}:
            return path.split("?")[0].split("/")[0]

        if host.endswith("youtube.com"):
            if parsed.path.startswith("/watch"):
                return parse_qs(parsed.query).get("v", [""])[0]

            partes = [segmento for segmento in path.split("/") if segmento]
            if partes:
                if partes[0] in {"shorts", "embed", "live", "v"}:
                    return partes[1] if len(partes) > 1 else ""
                return partes[-1]

    match = re.search(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{11}(?![A-Za-z0-9_-])", valor)
    return match.group(0) if match else valor



def carrega_youtube(video_id_ou_url: str):
    video_id = extrai_video_id(video_id_ou_url)

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
    texto = "\n".join(segmento["text"] for segmento in raw)
    return texto



def carrega_csv(caminho):
    loader = CSVLoader(caminho, encoding="utf-8")
    lista_documentos = loader.load()
    documento = "\n\n".join(doc.page_content for doc in lista_documentos)
    return documento



def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = "\n\n".join(doc.page_content for doc in lista_documentos)
    return documento



def carrega_txt(caminho):
    loader = TextLoader(caminho, autodetect_encoding=True, encoding="utf-8")
    lista_documentos = loader.load()
    documento = "\n\n".join(doc.page_content for doc in lista_documentos)
    return documento
