import os
import re
import streamlit as st

st.set_page_config(
    page_title="KAYZAC - Assistente",
    page_icon="🤖",
    layout="wide",
)

# ============================================================
# CONFIGURAÇÃO DA API E DO USO DE TOKENS
# ============================================================

def configurar(nome, padrao=None):
    """Lê primeiro o Secret do Streamlit e depois a variável de ambiente."""
    try:
        valor = st.secrets.get(nome)
        if valor not in (None, ""):
            return valor
    except Exception:
        pass
    return os.getenv(nome, padrao)


API_KEY = configurar("OPENAI_API_KEY")
MODELO = str(configurar("OPENAI_MODEL", "gpt-6-luna")).strip()

try:
    TOKEN_PADRAO = int(configurar("OPENAI_MAX_OUTPUT_TOKENS", "1200"))
except (TypeError, ValueError):
    TOKEN_PADRAO = 1200
TOKEN_PADRAO = max(400, min(TOKEN_PADRAO, 2400))

# Limites internos para controlar o tamanho do contexto de cada chamada.
MAX_HISTORICO_MENSAGENS = 8  # mensagens anteriores; não inclui a pergunta atual
MAX_HISTORICO_CARACTERES = 7000
MAX_MENSAGENS_TELA = 41


@st.cache_resource(show_spinner=False)
def _criar_cliente_openai(chave):
    from openai import OpenAI
    return OpenAI(api_key=chave)


def obter_cliente():
    if not API_KEY:
        return None
    try:
        return _criar_cliente_openai(API_KEY)
    except ImportError:
        return "biblioteca_ausente"


# ============================================================
# MAPA DO KAYZAC
# ============================================================
PAGINAS_KAYZAC = {
    "Início": {"arquivo": "app.py", "icone": "🏠", "descricao": "Página inicial, perfil do treinador e visão geral."},
    "Pokédex": {"arquivo": "pages/1_Pokedex.py", "icone": "📖", "descricao": "Pesquisa de Pokémon, formas, evoluções, habilidades, golpes e estatísticas."},
    "KAYZAC World": {"arquivo": "pages/2_Mundo.py", "icone": "🌎", "descricao": "Regiões, locais, cidades e rotas do mundo Pokémon."},
    "Times": {"arquivo": "pages/3_Times.py", "icone": "⚔️", "descricao": "Área de equipes e times Pokémon."},
    "Personagens": {"arquivo": "pages/4_Personagens.py", "icone": "👥", "descricao": "Personagens do universo Pokémon."},
    "Biblioteca": {"arquivo": "pages/5_Biblioteca.py", "icone": "📚", "descricao": "Biblioteca de conteúdos e referências."},
    "Mídia": {"arquivo": "pages/6_Midia.py", "icone": "🎬", "descricao": "Conteúdos de mídia."},
    "Jogos": {"arquivo": "pages/7_Jogos.py", "icone": "🎮", "descricao": "Jogos Pokémon e conteúdos relacionados."},
    "Quiz": {"arquivo": "pages/8_Quiz.py", "icone": "🧠", "descricao": "Perguntas, acertos, sequência e XP."},
    "Música": {"arquivo": "pages/9_Musica.py", "icone": "🎵", "descricao": "Sons e músicas relacionados ao projeto e à franquia."},
    "Cronologia": {"arquivo": "pages/10_Cronologia.py", "icone": "📜", "descricao": "Linha do tempo e marcos da franquia."},
    "Diversidade": {"arquivo": "pages/11_Diversidade.py", "icone": "🌈", "descricao": "Conteúdo de diversidade do projeto."},
    "TCG Pocket": {"arquivo": "pages/12_TCG.py", "icone": "🃏", "descricao": "Conteúdo de TCG Pocket."},
    "Simulador de Captura": {"arquivo": "pages/13_Capturas.py", "icone": "🎯", "descricao": "Simulação de captura Pokémon."},
    "Gerador de Desafios": {"arquivo": "pages/14_Desafios.py", "icone": "🎲", "descricao": "Criação e geração de desafios para jogar Pokémon."},
    "Laboratório de Fusões": {"arquivo": "pages/15_Fusoes.py", "icone": "🧬", "descricao": "Criação e exploração de fusões entre Pokémon."},
    "Rom Hacks & Fan Games": {"arquivo": "pages/16_Roms.py", "icone": "🎮", "descricao": "Catálogo e favoritos de ROM Hacks e Fan Games."},
    "Ranqueamento": {"arquivo": "pages/17_Ranking.py", "icone": "🏆", "descricao": "Rankings, comparações e listas de Pokémon."},
    "Assistente KAYZAC": {"arquivo": "pages/18_Assistente.py", "icone": "🤖", "descricao": "A IA oficial do KAYZAC."},
}

INSTRUCOES_ASSISTENTE = """
Você é o Assistente KAYZAC, a IA do projeto KAYZAC - MASTER POKEMON.
- Responda em português brasileiro por padrão, de forma amigável, clara e prática.
- Ajude com KAYZAC, Pokémon, Python, Streamlit, escola, jogos, tecnologia e assuntos gerais.
- Para perguntas sobre páginas do KAYZAC, use o mapa fornecido e indique o nome, o arquivo e sua função.
- Não invente páginas, arquivos, funcionalidades ou detalhes internos ausentes no contexto.
- Ao ensinar programação, prefira soluções incrementais, exemplos simples e indique onde colocar o código.
- Seja direto em perguntas simples; aprofunde quando o usuário pedir explicações, pesquisa ou código completo.
- Para informações atuais, use a busca na web somente quando ela estiver disponível na chamada; se não pesquisar, deixe a incerteza explícita.
- Não invente fatos, citações, fontes ou resultados de execução. Em temas médicos, jurídicos ou financeiros importantes, explique limites e recomende fontes/profissionais adequados.
""".strip()


def mapa_em_texto():
    return "\n".join(
        f"- {dados['icone']} {nome} | {dados['arquivo']} | {dados['descricao']}"
        for nome, dados in PAGINAS_KAYZAC.items()
    )


def dados_treinador_em_texto():
    campos = {
        "Nome": st.session_state.get("treinador_nome"),
        "Título": st.session_state.get("treinador_titulo"),
        "Região": st.session_state.get("treinador_regiao"),
        "Pokémon favorito": st.session_state.get("treinador_pokemon"),
        "Estilo": st.session_state.get("treinador_estilo"),
    }
    disponiveis = [(k, v) for k, v in campos.items() if v not in (None, "")]
    if not disponiveis:
        return "Perfil do treinador não informado nesta sessão."
    return "\n".join(f"{k}: {v}" for k, v in disponiveis)


def contexto_do_projeto(pergunta):
    """Só envia mapa e perfil completos quando ajudam a responder a pergunta."""
    texto = pergunta.casefold()
    contexto_projeto = (
        "kayzac", "meu site", "meu app", "meu projeto", "no site", "no app",
        "página", "páginas", "arquivo", "repositório", "estrutura", "pokédex do",
        "fusões", "desafios", "rom hacks", "tcg", "ranking", "biblioteca",
        "quiz", "personagens", "cronologia", "simulador de captura", "kayzac world",
    )
    blocos = [INSTRUCOES_ASSISTENTE]
    if any(termo in texto for termo in contexto_projeto):
        # O mapa já contém a lista de páginas; não repetimos outro resumo equivalente.
        blocos.append(
            "ESTRUTURA CONHECIDA: app.py, pasta pages/, pokemon_index.json, "
            "pokemon_1.csv, formas_pokemon.json, logo.png e requirements.txt."
            "\nMAPA DE PÁGINAS:\n" + mapa_em_texto()
        )
    else:
        blocos.append(
            "O contexto detalhado das páginas do KAYZAC não foi incluído nesta pergunta "
            "para economizar tokens. Se o usuário pedir um detalhe interno do projeto, "
            "não adivinhe; informe que será necessário consultar o mapa do projeto."
        )

    termos_perfil = ("meu perfil", "meu treinador", "meu pokémon", "meu pokemon", "meu time", "minha equipe", "minha região", "favorito")
    if any(termo in texto for termo in termos_perfil):
        blocos.append("PERFIL DO TREINADOR:\n" + dados_treinador_em_texto())
    return "\n\n".join(blocos)


# ============================================================
# CONTROLE DE HISTÓRICO E BUSCA
# ============================================================
def limitar_historico_para_api(mensagens, pergunta_atual):
    """Evita duplicar a pergunta atual e limita o histórico enviado à API."""
    anteriores = list(mensagens)
    if (
        anteriores
        and anteriores[-1].get("role") == "user"
        and str(anteriores[-1].get("content", "")) == pergunta_atual
    ):
        anteriores.pop()  # a pergunta atual será anexada exatamente uma vez abaixo

    anteriores = [
        m for m in anteriores
        if m.get("role") in {"user", "assistant"} and isinstance(m.get("content"), str)
    ][-MAX_HISTORICO_MENSAGENS:]

    # Preserva as mensagens mais recentes e, se necessário, corta a parte antiga.
    selecionadas = []
    caracteres_restantes = MAX_HISTORICO_CARACTERES
    for mensagem in reversed(anteriores):
        if caracteres_restantes <= 0:
            break
        texto = mensagem["content"]
        if len(texto) > caracteres_restantes:
            if caracteres_restantes <= 80:
                texto = texto[-caracteres_restantes:]
            else:
                texto = "[trecho antigo reduzido]\n" + texto[-(caracteres_restantes - 25):]
        if texto:
            selecionadas.append({"role": mensagem["role"], "content": texto})
            caracteres_restantes -= len(texto)
    return list(reversed(selecionadas))


def pergunta_precisa_de_web(pergunta):
    """Heurística simples para só anexar a ferramenta web em perguntas atuais."""
    texto = pergunta.casefold()
    gatilhos = (
        "hoje", "agora", "atualmente", "atualizado", "atualização", "última notícia",
        "últimas notícias", "notícias", "lançamento", "quando sai", "quando lança",
        "data de lançamento", "preço atual", "quanto custa", "cotação", "clima", "previsão do tempo",
        "placar", "resultado de hoje", "partida de hoje", "jogo de hoje", "tabela atual",
        "classificação atual", "eleição", "presidente atual", "confirmado", "mais recente",
        "último episódio", "versão atual", "gta 6", "ea sports fc", "fifa 26", "fifa 27",
        "pokemon champions", "pokémon champions", "2026", "2027", "2028",
    )
    return any(gatilho in texto for gatilho in gatilhos)


def gerar_resposta(pergunta):
    cliente = obter_cliente()
    if cliente is None:
        return (
            "🟡 **A IA ainda não foi conectada.** Configure `OPENAI_API_KEY` "
            "nos Secrets do Streamlit Cloud."
        )
    if cliente == "biblioteca_ausente":
        return "⚠️ A biblioteca `openai` não está instalada. Confira o `requirements.txt`."

    historico = limitar_historico_para_api(
        st.session_state.assistente_mensagens,
        pergunta,
    )
    entrada = [{"role": "developer", "content": contexto_do_projeto(pergunta)}]
    entrada.extend(historico)
    entrada.append({"role": "user", "content": pergunta})

    argumentos = {
        "model": MODELO,
        "input": entrada,
        "max_output_tokens": int(st.session_state.assistente_max_output_tokens),
    }

    # GPT-6 Luna suporta effort='none', reduzindo raciocínio desnecessário
    # em perguntas comuns. Se o modelo for trocado nos Secrets, não forçamos esse parâmetro.
    if MODELO == "gpt-6-luna":
        argumentos["reasoning"] = {"effort": "none"}

    # Mesmo com o botão ligado, só adiciona a ferramenta em perguntas com indício de atualidade.
    if st.session_state.assistente_buscar_web and pergunta_precisa_de_web(pergunta):
        argumentos["tools"] = [{"type": "web_search"}]

    try:
        resposta = cliente.responses.create(**argumentos)
        texto = getattr(resposta, "output_text", None)
        if texto and texto.strip():
            return texto.strip()
        return "⚠️ A IA respondeu, mas não retornou texto legível. Tente reformular a pergunta."
    except Exception as erro:
        detalhe = str(erro)
        if "api_key" in detalhe.lower() or "authentication" in detalhe.lower() or "401" in detalhe:
            return "🔑 **Problema na chave da API.** Confira `OPENAI_API_KEY` nos Secrets do Streamlit Cloud."
        if "model" in detalhe.lower() and ("not found" in detalhe.lower() or "does not exist" in detalhe.lower()):
            return f"⚠️ O modelo `{MODELO}` não está disponível para esta chave/projeto. Confira `OPENAI_MODEL` nos Secrets."
        return "⚠️ Não consegui falar com a IA agora.\n\nDetalhe técnico: `" + detalhe[:350].replace("`", "'") + "`"


def adicionar_mensagem(role, content):
    st.session_state.assistente_mensagens.append({"role": role, "content": content})
    # Deixa a conversa visível leve, mantendo a mensagem inicial e as mais recentes.
    if len(st.session_state.assistente_mensagens) > MAX_MENSAGENS_TELA:
        primeira = st.session_state.assistente_mensagens[0]
        recentes = st.session_state.assistente_mensagens[-(MAX_MENSAGENS_TELA - 1):]
        st.session_state.assistente_mensagens = [primeira] + recentes


def processar_pergunta(pergunta):
    adicionar_mensagem("user", pergunta)
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        with st.spinner("🤖 O Assistente KAYZAC está pensando..."):
            resposta = gerar_resposta(pergunta)
        st.markdown(resposta)
    adicionar_mensagem("assistant", resposta)


def limpar_conversa():
    st.session_state.assistente_mensagens = [{
        "role": "assistant",
        "content": "⚡ **Conversa reiniciada!**\n\nPode mandar sua próxima pergunta. 😎",
    }]


# ============================================================
# ESTADO DA CONVERSA
# ============================================================
if "assistente_mensagens" not in st.session_state:
    st.session_state.assistente_mensagens = [{
        "role": "assistant",
        "content": (
            "⚡ **Olá! Eu sou o Assistente KAYZAC!**\n\n"
            "Posso ajudar com o próprio site, Pokémon, Python/Streamlit, escola, trabalho, "
            "jogos, tecnologia e assuntos gerais. 😎"
        ),
    }]
if "assistente_buscar_web" not in st.session_state:
    st.session_state.assistente_buscar_web = True
if "assistente_pergunta_pronta" not in st.session_state:
    st.session_state.assistente_pergunta_pronta = None
if "assistente_max_output_tokens" not in st.session_state:
    st.session_state.assistente_max_output_tokens = TOKEN_PADRAO


# ============================================================
# VISUAL
# ============================================================
st.markdown(
    """
    <style>
    .assistente-hero {
        border: 1px solid rgba(17,140,255,.35);
        border-radius: 22px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        background: linear-gradient(135deg, rgba(17,140,255,.12), rgba(128,128,128,.05));
    }
    .assistente-tag { opacity: .78; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="assistente-hero">
        <h1>🤖 Assistente KAYZAC</h1>
        <div class="assistente-tag">Sua IA para o universo Pokémon... e para muito além dele.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_info, col_config = st.columns([3, 1])
with col_info:
    st.write("O Assistente conhece o mapa principal do **KAYZAC** e também ajuda com assuntos externos.")
with col_config:
    st.toggle(
        "🌐 Permitir busca na web",
        key="assistente_buscar_web",
        help="Quando ativada, a busca só é anexada a perguntas que parecem depender de informações recentes.",
    )

with st.expander("⚙️ Eficiência e limite de tokens"):
    st.slider(
        "Máximo de tokens de saída por resposta",
        min_value=400,
        max_value=2400,
        step=200,
        key="assistente_max_output_tokens",
        help="Limita o tamanho máximo da resposta. Aumente para respostas longas ou código; reduza para economizar tokens.",
    )
    st.caption(
        f"Modelo: `{MODELO}` · limite atual: **{st.session_state.assistente_max_output_tokens:,} tokens de saída**. "
        f"O histórico enviado à API fica limitado às últimas {MAX_HISTORICO_MENSAGENS} mensagens anteriores e a cerca de {MAX_HISTORICO_CARACTERES:,} caracteres."
    )
    st.caption("O limite de tokens controla o máximo permitido, não obriga a IA a usar todos eles.")

st.divider()

# Atalhos
st.markdown("### ⚡ Atalhos do Assistente")
atalhos = [
    ("🧭 Mapa do KAYZAC", "Quais são as páginas do KAYZAC e o que cada uma faz?"),
    ("🧬 Fusões", "Qual é a página de fusões do KAYZAC e qual é o arquivo dela?"),
    ("📖 Pokédex", "O que eu consigo fazer na Pokédex do KAYZAC?"),
    ("🎲 Desafios", "Onde fica o Gerador de Desafios e para que ele serve?"),
    ("🐍 Python", "Me ensine uma função simples em Python, passo a passo."),
    ("🎮 Atualidades", "Quais assuntos de games atuais você consegue pesquisar para mim?"),
]
colunas = st.columns(3)
for i, (titulo, exemplo) in enumerate(atalhos):
    with colunas[i % 3]:
        if st.button(titulo, use_container_width=True, key=f"atalho_assistente_{i}"):
            st.session_state.assistente_pergunta_pronta = exemplo
            st.rerun()

with st.expander("🗺️ Ver mapa rápido do KAYZAC"):
    for nome, info in PAGINAS_KAYZAC.items():
        st.markdown(f"**{info['icone']} {nome}**  \n`{info['arquivo']}` — {info['descricao']}")

st.divider()

# Renderiza o histórico salvo
for mensagem in st.session_state.assistente_mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta_chat = st.chat_input("Pergunte alguma coisa ao Assistente KAYZAC...")
pergunta_pronta = st.session_state.assistente_pergunta_pronta
st.session_state.assistente_pergunta_pronta = None
pergunta = pergunta_chat or pergunta_pronta

if pergunta:
    processar_pergunta(pergunta)
    st.rerun()

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        limpar_conversa()
        st.rerun()
with col2:
    if API_KEY:
        st.caption(f"🟢 API configurada · modelo `{MODELO}`")
    else:
        st.caption("🟡 Configure `OPENAI_API_KEY` nos Secrets")

st.caption("⚡ KAYZAC - MASTER POKEMON • Assistente oficial do projeto")

