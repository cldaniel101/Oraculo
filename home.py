import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from load import carrega_site, carrega_youtube, carrega_pdf, carrega_csv, carrega_txt
import tempfile

import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

TIPOS_ARQUIVOS_VALIDOS = [
    'Site', 'Youtube', 'PDF', 'Csv', 'Txt'
]

CONFIG_MODELOS = {
    'OpenAI': {
        'modelos': ['gpt-4.1-mini-2025-04-14', 'o4-mini-2025-04-16', 'gpt-4o-2024-08-06', 'o3-2025-04-16'],
        'chat': ChatOpenAI
    },
    'Groq': {
        'modelos': ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile', 'meta-llama/llama-guard-4-12b'],
        'chat': ChatGroq
    }
}

MEMORIA = ConversationBufferMemory()
MEMORIA.chat_memory.add_user_message('Olá, IA.')
MEMORIA.chat_memory.add_ai_message('Olá, Humano.')


def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo):
    kwargs = {"model": modelo, "api_key": api_key}

    # Modelos de raciocinio da OpenAI so aceitam temperature=1
    # (o1*, o3*, o4-mini*, e alguns snapshots do 4o como 2024-08-06).
    if provedor == "OpenAI" and (
        modelo.startswith(("o", "gpt-4o-2024"))
        or modelo in {"o1-preview", "o1-mini", "o3", "o4-mini"}
    ):
        kwargs["temperature"] = 1
    else:
        # Se quiser manter o "estilo" da aula, pode usar 0.7 nos demais
        # ou simplesmente nao definir temperature para herdar o default do provedor.
        kwargs["temperature"] = 0.7

    tipo_normalizado = (tipo_arquivo or "").strip().lower()
    documento = None

    def carregar_temporario(sufixo, loader):
        arquivo.seek(0)
        with tempfile.NamedTemporaryFile(suffix=sufixo, delete=False) as temp:
            temp.write(arquivo.read())
            caminho_temp = temp.name
        try:
            return loader(caminho_temp)
        finally:
            try:
                os.remove(caminho_temp)
            except OSError:
                pass

    if tipo_normalizado == 'site':
        if not arquivo:
            st.warning('Envie a URL do site antes de continuar.')
            return
        documento = carrega_site(arquivo)
    elif tipo_normalizado == 'youtube':
        if not arquivo:
            st.warning('Envie a URL do video antes de continuar.')
            return
        documento = carrega_youtube(arquivo)
    elif tipo_normalizado == 'pdf':
        if arquivo is None:
            st.warning('Envie um arquivo PDF antes de continuar.')
            return
        documento = carregar_temporario('.pdf', carrega_pdf)
    elif tipo_normalizado == 'csv':
        if arquivo is None:
            st.warning('Envie um arquivo CSV antes de continuar.')
            return
        documento = carregar_temporario('.csv', carrega_csv)
    elif tipo_normalizado == 'txt':
        if arquivo is None:
            st.warning('Envie um arquivo TXT antes de continuar.')
            return
        documento = carregar_temporario('.txt', carrega_txt)
    else:
        st.error('Tipo de arquivo nao suportado.')
        return

    if not documento:
        st.error('Nao foi possivel carregar o documento informado.')
        return
    
    # st.session_state['chat'] = CONFIG_MODELOS[provedor]['chat'](**kwargs)

def pagina_chat():
    st.header("🤖 Bem vindo ao Oráculo", divider=True)

    chat_model = st.session_state.get('chat')

    memoria = st.session_state.get('memoria', MEMORIA)

    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)
    
    input_usuario = st.chat_input('Fale com o oráculo')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chat_model.stream(input_usuario))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)

        st.session_state['memoria'] = memoria

def sidebar():
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'Site':
            arquivo = st.text_input('Digite a url do site')
        if tipo_arquivo == 'Youtube':
            arquivo = st.text_input('Digite a url do vídeo')
        if tipo_arquivo == 'PDF':
            arquivo = st.file_uploader('Faça upload do arquivo pdf', type=['.pdf'])
        if tipo_arquivo == 'Csv':
            arquivo = st.file_uploader('Faça upload do arquivo csv', type=['.csv'])
        if tipo_arquivo == 'Txt':
            arquivo = st.file_uploader('Faça upload do arquivo txt', type=['.txt'])

    with tabs[1]:
        provedor = st.selectbox('Selecione o provedor dos modelos', CONFIG_MODELOS.keys())
        modelo = st.selectbox('Selecione o modelo', CONFIG_MODELOS[provedor]['modelos'])
        api_key = st.text_input(
            f'Adi.cione a API Key para a {provedor}', 
            value=st.session_state.get(f'api_key_{provedor}')
            )

        st.session_state[f'api_key_{provedor}'] = api_key

    if st.button('Inicializar Oráculo', use_container_width=True):
        carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo)


def main():
    pagina_chat()
    with st.sidebar:
        sidebar()

if __name__ == "__main__":
    main()