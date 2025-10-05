# 🔮 Oráculo — Chat que conversa com *meus* dados

Um app simples em **Streamlit** que permite conversar com conteúdos próprios (site, vídeo do YouTube, PDF, CSV e TXT) usando modelos de linguagem via **LangChain**.  
Este projeto foi desenvolvido como prática a partir do material da Asimov Academy: *Oráculo – criando um chat que conversa com meus dados*.

> Referência do projeto-curso: [Asimov Academy — Oráculo](https://hub.asimov.academy/projeto/oraculo-criando-um-chat-que-conversa-com-meus-dados/)

---

## 🎬 Demonstração

![Demonstração do Oráculo](arquivos/Demonstração%20do%20Oráculo.gif)

---

## ✨ Funcionalidades

- **Chat com memória**: histórico mantido durante a sessão (LangChain `ConversationBufferMemory`).
- **Fontes de conhecimento** (carregamento via `load.py`):
  - **Site (URL)** — `WebBaseLoader` (obtém o HTML da página).
  - **YouTube** — via `youtube-transcript-api` (usa a transcrição do vídeo).
  - **PDF** — `PyPDFLoader` (extrai texto de todas as páginas).
  - **CSV** — `CSVLoader` (lê colunas e linhas como texto base).
  - **TXT** — `TextLoader` (texto puro).
- **Escolha de provedor e modelo** (definido em `home.py`):
  - **OpenAI** (`langchain_openai.ChatOpenAI`) — requer `OPENAI_API_KEY`.
  - **Groq** (`langchain_groq.ChatGroq`) — requer `GROQ_API_KEY`.  
    Exemplos citados no código: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile` e `meta-llama/llama-guard-4-12b`.
- **Interface amigável** em Streamlit com:
  - Inicialização do Oráculo com a fonte escolhida;
  - Botão para **“Apagar Histórico de Conversa”**.

> ⚠️ Observação: o projeto de exemplo é didático. O conteúdo carregado é enviado como **contexto** para o modelo responder; não há banco vetorial/embeddings por padrão. Em documentos muito grandes, pode ocorrer **estouro de tokens** — veja “Limitações” e “Como evoluir”.

---

## 🗂 Estrutura do projeto

```
Oraculo-main/
├─ home.py               # App Streamlit: UI, seleção de provedor/modelo e chat
├─ load.py               # Funções de carregamento: site, YouTube, PDF, CSV e TXT
├─ arquivos/             # Exemplos de dados
│  ├─ RoteiroViagemEgito.pdf
│  ├─ knowledge_base.csv
│  └─ knowledge_base.txt
├─ requirements.txt
└─ .gitignore
```

---

## 🚀 Como rodar

### 1) Pré‑requisitos
- **Python 3.10+**
- `pip` atualizado
- Opcional: `virtualenv`

### 2) Clonar / obter o projeto
Caso ainda não tenha o diretório do projeto, extraia o zip ou clone seu repositório.

### 3) Criar e ativar o ambiente
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4) Instalar as dependências
```bash
pip install -r requirements.txt
```

> 💡 O `requirements.txt` é didático e **extenso**. Se quiser acelerar, instale apenas o essencial para rodar o app (Streamlit + LangChain + loaders usados + provedores), porém o arquivo já lista tudo que foi usado nas aulas/labs.

### 5) Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto (`Oraculo-main/.env`) com **pelo menos um** dos provedores:

```ini
# Use um dos provedores abaixo (ou ambos, se quiser alternar)

# OpenAI
OPENAI_API_KEY=coloque_sua_chave_aqui

# Groq
GROQ_API_KEY=coloque_sua_chave_aqui

# (opcional) LangChain
LANGCHAIN_TRACING_V2=false
```

### 6) Iniciar o app
```bash
streamlit run home.py
```
Acesse no navegador: <http://localhost:8501>

---

## 🧠 Como usar (passo a passo)

1. **Abra a barra lateral** do Streamlit.
2. **Escolha o provedor e o modelo** (OpenAI ou Groq).
3. **Selecione o tipo de fonte** a ser carregada:
   - **Site (URL)**: informe a URL completa (começando com `http`/`https`).  
     > *Dica:* `WebBaseLoader` não executa JavaScript; páginas muito dinâmicas podem retornar vazio ou conteúdo parcial.
   - **YouTube**: cole a URL do vídeo. O app tentará obter a **transcrição** automaticamente.
   - **PDF**: envie o arquivo. O sistema concatenará o texto de todas as páginas.
   - **CSV**: envie o arquivo. O conteúdo textual (células) vira contexto.
   - **TXT**: envie o arquivo. O texto inteiro entra no contexto.
4. Clique em **“Inicializar Oráculo”**.
5. **Converse** no campo de chat principal.
6. Se quiser, use **“Apagar Histórico de Conversa”** para limpar a memória da sessão.

---

## ⚙️ Como funciona por baixo dos panos (resumo)

- `home.py`
  - Monta a interface em Streamlit;
  - Gerencia a memória com `ConversationBufferMemory` (LangChain);
  - Constrói o **prompt** do chat (via `ChatPromptTemplate` e `MessagesPlaceholder`);
  - Encaminha **conteúdo carregado** + **histórico** para o modelo escolhido responder.
- `load.py`
  - `carrega_site(url)`: usa `WebBaseLoader` para baixar e transformar a página em texto.
  - `carrega_youtube(url)`: usa `youtube-transcript-api` para obter a transcrição do vídeo.
  - `carrega_pdf(caminho)`: usa `PyPDFLoader` para extrair texto de todas as páginas.
  - `carrega_csv(caminho)`: usa `CSVLoader` para ler o conteúdo do CSV.
  - `carrega_txt(caminho)`: usa `TextLoader` para ler o arquivo de texto.
- **Modelos**: selecionados a partir de um dicionário de configuração em `home.py` (ex.: alguns modelos Groq).

---

## 🛟 Solução de problemas (FAQ)

**1) “TranslationLanguageNotAvailable” ao carregar YouTube**  
- Significa que **a tradução automática** para o idioma solicitado **não está disponível** para aquele vídeo.  
- Tente:
  - Usar o **idioma original** do vídeo, se souber; ou
  - Escolher **outro vídeo** com transcrição liberada; ou
  - Ajustar a função em `load.py` para **não forçar tradução**, caindo no idioma disponível.

**2) O site não carrega texto suficiente**  
- Páginas SPA/JS‑pesadas podem não renderizar via `WebBaseLoader`.  
- Alternativas: salvar o HTML e carregar como TXT, ou usar um loader que renderize JavaScript (ex.: Playwright, não incluído por padrão).

**3) “Out of tokens” / respostas truncadas**  
- O conteúdo do documento pode ser **grande** demais para o contexto do modelo.  
- Dicas:
  - Resuma partes antes de conversar;
  - Use documentos menores;
  - (Evolução) implementar **embeddings + busca** (FAISS/Chroma) para enviar **apenas** trechos relevantes.

**4) Erro 401 (chave inválida)**  
- Verifique se `OPENAI_API_KEY`/`GROQ_API_KEY` estão corretas no `.env` e se o **modelo** escolhido existe para a sua conta.

---

## 🧭 Como evoluir o projeto

- **RAG de verdade**: adicionar **embeddings** (OpenAI, Jina, Voyage, etc.) e um **vetor DB** (FAISS/Chroma) para buscar só os trechos relevantes.
- **Suporte a múltiplos arquivos** e mesclagem de fontes (ex.: vários PDFs).
- **Controle de memória**: resumos parciais do histórico para não estourar contexto.
- **Boas práticas**: logs estruturados, testes de unidade e `Makefile` com comandos úteis.
- **Autenticação** no Streamlit para proteger o app.
- **Dockerfile** para empacotamento.

---

## 📚 Créditos e referência

- Curso/projeto: **Asimov Academy — Oráculo**  
  <https://hub.asimov.academy/projeto/oraculo-criando-um-chat-que-conversa-com-meus-dados/>
