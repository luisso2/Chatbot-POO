import streamlit as st
import os
import json
import time
from typing import TypedDict, Annotated, Optional, Literal
from pydantic import BaseModel, Field

# --- LangChain/LangGraph Imports ---
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# ATENÇÃO: Use a biblioteca local da sua LLM, ou defina-a.
# No seu notebook, você usou ChatOpenAI.
from langchain_openai import ChatOpenAI 

# =========================================================
# I. Configuração e Inicialização (Fora do Grafo)
# =========================================================

# --- 1. Credenciais (Adapte conforme sua necessidade) ---
# O Streamlit lida melhor com secrets ou variáveis de ambiente.
# Use st.secrets["OPENAI_API_KEY"] em um app real.
os.environ["OPENAI_API_KEY"] = "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" # Substitua pela sua chave REAL


# --- 2. LLM Base ---
# Usando o modelo que você mencionou
LLM_MODEL = "gpt-5-nano" # Ajuste para um modelo acessível, como "gpt-3.5-turbo"
llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

# =========================================================
# II. LangGraph: Definições de Estado e LLM Estruturada
# =========================================================

class AgentState(TypedDict):
    """Representa o estado do nosso agente aluno."""
    messages: Annotated[list, add_messages]
    codigo_atual: Optional[str]
    modo_atual: Literal["help_receiver", "questioner"]
    contador_turnos: int

class RespostaAgente(BaseModel):
    """Estrutura de saída forçada da LLM."""
    comentario: str = Field(description="Sua resposta em texto conversacional para o professor.")
    codigo_python: Optional[str] = Field(description="O conteúdo COMPLETO e ATUALIZADO do arquivo Python.", default=None)

llm_estruturada = llm.with_structured_output(RespostaAgente)

# =========================================================
# III. LangGraph: Prompts e Lógica de Mode-Shifting
# =========================================================

PROMPT_HELP_RECEIVER = PROMPT_HELP_RECEIVER = """
### MODO: RECEPTOR PASSIVO (Help-Receiver) 🎓
Você é um aluno iniciante aprendendo Orientação a Objetos.

### SUA MEMÓRIA (RESTRIÇÃO ABSOLUTA):
1. **Você sofre de amnésia total sobre programação.** Você esqueceu como se escreve Python.
2. **Sua ÚNICA fonte de conhecimento é esta conversa.** Você só sabe o que o Professor te explicou.

### REGRAS DE COMPORTAMENTO:
- **Não Complete:** Se não sabe a sintaxe, pergunte: *"Professor, como escrevo isso?"*
- **Aprenda e Repita:** Aceite como verdade absoluta o que o professor ensinar.
- **Não Invente:** Jamais use conhecimento prévio para assumir sintaxes não explicadas.

### IMPORTANTE:
- Use o campo `comentario` para fazer perguntas de esclarecimento.
- Use o campo `codigo_python` APENAS quando aprender código novo do professor.

### OBJETIVO:
Absorver conhecimento passivamente e consolidar o que foi ensinado.
"""

PROMPT_QUESTIONER = """
### MODO: QUESTIONADOR ATIVO (Questioner) 🤔
Você é um aluno iniciante aprendendo Orientação a Objetos com pensamento crítico.

### SUA MEMÓRIA (RESTRIÇÃO ABSOLUTA):
1. **Você sofre de amnésia total sobre programação.**
2. **Sua ÚNICA fonte de conhecimento é esta conversa.**

### REGRAS DE COMPORTAMENTO:
- **Faça Perguntas Proativas:** Você DEVE fazer perguntas de "por quê" sobre os conceitos ensinados.
- **Questione a Implementação:** Pergunte sobre alternativas, casos extremos e por que uma abordagem é melhor.
- **Exija Exemplos:** Peça exemplos reais e contraexemplos para entender melhor.
- **Teste o Entendimento:** Formule perguntas para validar se compreendeu corretamente.

### TIPOS DE PERGUNTAS A FAZER:
- **Escolha apenas uma dessas perguntas e de forma que seja uma pergunta curta mas profunda**
1. **Perguntas de Conceito:** *"Por que precisamos usar essa sintaxe e não outra?"*
2. **Perguntas de Aplicação:** *"Como isso funcionaria se..."*
3. **Perguntas de Validação:** *"Então, se eu entendi, isso significa que..."*
4. **Perguntas de Aprofundamento:** *"E se mudarmos esse parâmetro, o que acontece?"*

### IMPORTANTE:
- Use o campo `comentario` para fazer perguntas desafiadoras mas respeitosas.
- Use o campo `codigo_python` APENAS se o professor enviou código novo.

### OBJETIVO:
Construir conhecimento ativo através de pensamento crítico e questionamento construtivo.
"""

def determinar_modo(contador_turnos: int) -> Literal["help_receiver", "questioner"]:
    """Alterna entre modos a cada 3 turnos."""
    ciclo = contador_turnos % 6
    return "help_receiver" if ciclo < 3 else "questioner"

def agent_node(state: AgentState):
    """Nó principal que processa a entrada e alterna o modo."""
    messages = state["messages"]
    contador = state.get("contador_turnos", 0)

    # 1. Determina o próximo modo
    novo_modo = determinar_modo(contador)

    # 2. Seleciona o prompt
    system_prompt_base = PROMPT_HELP_RECEIVER if novo_modo == "help_receiver" else PROMPT_QUESTIONER
    codigo_contexto = state.get("codigo_atual", "Nenhum código criado ainda.")
    
    # Monta as mensagens
    modo_texto = "🎓 RECEPTOR PASSIVO (Help-Receiver)" if novo_modo == "help_receiver" else "🤔 QUESTIONADOR ATIVO (Questioner)"
    
    prompt_msgs = [
        SystemMessage(content=system_prompt_base),
        SystemMessage(content=f"### MODO ATUAL: {modo_texto}\n### ESTADO DO CÓDIGO:\n{codigo_contexto}")
    ]
    prompt_msgs.extend(messages)

    # 3. Chama a LLM
    resposta: RespostaAgente = llm_estruturada.invoke(prompt_msgs)

    # 4. Prepara o retorno do novo estado
    updates = {}
    updates["messages"] = [AIMessage(content=resposta.comentario)]
    updates["modo_atual"] = novo_modo
    updates["contador_turnos"] = contador + 1

    if resposta.codigo_python:
        updates["codigo_atual"] = resposta.codigo_python

    return updates

# =========================================================
# IV. LangGraph: Montagem e Compilação
# =========================================================

@st.cache_resource
def setup_langgraph_app():
    """Configura o workflow do LangGraph uma única vez."""
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    # Usamos MemorySaver para armazenar o estado da conversa por thread_id
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

# =========================================================
# V. Streamlit Interface
# =========================================================

def reset_conversation():
    # Isso invalida o thread_id antigo e força uma nova thread
    st.session_state["thread_id"] = "streamlit_session_" + str(time.time())

# Inicializa o app LangGraph
app = setup_langgraph_app()

st.title("🧑‍💻 Agente Aluno Mode-Shifting")
st.caption("Um aluno iniciante em POO com amnésia, alternando entre modos Receptor e Questionador.")

# --- 1. Inicialização do Estado (usando st.session_state) ---

# Gera um ID de Thread único para a sessão do Streamlit
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "streamlit_session_" + str(time.time())

config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# Carrega o estado atual (se existir)
try:
    snapshot = app.get_state(config)
    # Se o estado estiver vazio (início da conversa), inicializa com o estado padrão
    if not snapshot.values.get("messages"):
        initial_state = {
            "messages": [AIMessage(content="Oi, Professor! Meu nome é Luís. Estou pronto para começar a aula de Orientação a Objetos. Você pode me dar o primeiro conceito?")],
            "codigo_atual": None,
            "modo_atual": "help_receiver",
            "contador_turnos": 0
        }
        # Inicia a thread com a mensagem inicial e estado base
        app.update_state(config, initial_state)
except Exception:
    # Em caso de erro ao carregar, tente novamente na próxima interação
    pass


# --- 2. Exibição do Histórico e Painel de Código ---

# Recupera o estado atual para exibição
current_state = app.get_state(config)
all_messages = current_state.values.get("messages", [])
current_code = current_state.values.get("codigo_atual")
current_mode = current_state.values.get("modo_atual", "help_receiver")
current_counter = current_state.values.get("contador_turnos", 0)

# Modo para exibição no front-end
mode_emoji = "🎓" if current_mode == "help_receiver" else "🤔"
mode_name = "Receptor Passivo" if current_mode == "help_receiver" else "Questionador Ativo"

st.sidebar.header("Estado do Agente")
st.sidebar.markdown(f"**Modo Atual:** {mode_emoji} {mode_name}")
st.sidebar.markdown(f"**Turnos Completos:** {current_counter}")
st.sidebar.button("🔄 Iniciar Nova Conversa", on_click=reset_conversation)

# --- 1. Exibição da Conversa (Ocupa a largura total) ---

st.subheader("Conversa com Luís (Agente Aluno)")
# Renderiza o histórico de mensagens
for message in all_messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# --- 2. Exibição do Código (Abaixo da conversa, ocupando a largura total) ---

if current_code:
    st.subheader("📝 Arquivo Python")
    st.code(current_code, language="python")
#else:
#    st.info("Nenhum código foi ensinado ainda.")

# --- 3. Tratamento da Entrada do Usuário ---

# --- 3. Tratamento da Entrada do Usuário ---

if prompt := st.chat_input("👨‍🏫 Professor: Digite sua lição ou pergunta."):
    # A mensagem do usuário deve ser exibida no corpo principal, sem referenciar colunas.
    # O Streamlit lida automaticamente com o re-render do histórico.
    
    # Cria o input para o LangGraph (e a mensagem será exibida após o rerun)
    inputs = {"messages": [HumanMessage(content=prompt)]}
    
    # Invoca o LangGraph
    with st.spinner("🤖 Luís está pensando..."):
        # A invocação já atualiza o estado via MemorySaver
        app.invoke(inputs, config=config)

    # Força o Streamlit a re-executar e mostrar o novo estado
    st.rerun()


# --- FIM ---

