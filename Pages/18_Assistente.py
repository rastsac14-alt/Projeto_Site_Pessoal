import os
import streamlit as st

st.set_page_config(
    page_title="KAYZAC - Assistente",
    page_icon="🤖",
    layout="wide",
)

# ============================================================
# CONFIGURAÇÃO
# ============================================================

API_KEY = None

try:
    API_KEY = st.secrets.get("OPENAI_API_KEY")
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("OPENAI_API_KEY")

try:
    MODELO = st.secrets.get("OPENAI_MODEL", "gpt-6-luna")
except Exception:
    MODELO = os.getenv("OPENAI_MODEL", "gpt-6-luna")


# ============================================================
# MAPA DO KAYZAC
# ============================================================

PAGINAS_KAYZAC = {
    "Início": {
        "arquivo": "app.py",
        "icone": "🏠",
        "descricao": "Página inicial, perfil do treinador e visão geral do projeto.",
    },
    "Pokédex": {
        "arquivo": "pages/1_Pokedex.py",
        "icone": "📖",
        "descricao": "Pesquisa de Pokémon, formas, evoluções, habilidades, golpes, estatísticas e informações relacionadas.",
    },
    "KAYZAC World": {
        "arquivo": "pages/2_Mundo.py",
        "icone": "🌎",
        "descricao": "Exploração do mundo Pokémon, regiões, locais, cidades e rotas.",
    },
    "Times": {
        "arquivo": "pages/3_Times.py",
        "icone": "⚔️",
        "descricao": "Área relacionada a times e equipes Pokémon.",
    },
    "Personagens": {
        "arquivo": "pages/4_Personagens.py",
        "icone": "👥",
        "descricao": "Personagens do universo Pokémon e informações relacionadas.",
    },
    "Biblioteca": {
        "arquivo": "pages/5_Biblioteca.py",
        "icone": "📚",
        "descricao": "Biblioteca de conteúdos e referências do projeto.",
    },
    "Mídia": {
        "arquivo": "pages/6_Midia.py",
        "icone": "🎬",
        "descricao": "Conteúdos de mídia e acompanhamento de itens.",
    },
    "Jogos": {
        "arquivo": "pages/7_Jogos.py",
        "icone": "🎮",
        "descricao": "Jogos Pokémon e conteúdos relacionados.",
    },
    "Quiz": {
        "arquivo": "pages/8_Quiz.py",
        "icone": "🧠",
        "descricao": "Quiz, perguntas, acertos, sequência e XP.",
    },
    "Música": {
        "arquivo": "pages/9_Musica.py",
        "icone": "🎵",
        "descricao": "Sons e músicas relacionados ao projeto e à franquia.",
    },
    "Cronologia": {
        "arquivo": "pages/10_Cronologia.py",
        "icone": "📜",
        "descricao": "Linha do tempo e marcos da franquia.",
    },
    "Diversidade": {
        "arquivo": "pages/11_Diversidade.py",
        "icone": "🌈",
        "descricao": "Conteúdo da página de diversidade do projeto.",
    },
    "TCG Pocket": {
        "arquivo": "pages/12_TCG.py",
        "icone": "🃏",
        "descricao": "Conteúdo de TCG Pocket.",
    },
    "Simulador de Captura": {
        "arquivo": "pages/13_Capturas.py",
        "icone": "🎯",
        "descricao": "Simulação de captura Pokémon.",
    },
    "Gerador de Desafios": {
        "arquivo": "pages/14_Desafios.py",
        "icone": "🎲",
        "descricao": "Criação e geração de desafios para jogar Pokémon.",
    },
    "Laboratório de Fusões": {
        "arquivo": "pages/15_Fusoes.py",
        "icone": "🧬",
        "descricao": "Criação e exploração de fusões entre Pokémon.",
    },
    "Rom Hacks & Fan Games": {
        "arquivo": "pages/16_Roms.py",
        "icone": "🎮",
        "descricao": "Catálogo e favoritos de ROM Hacks e Fan Games.",
    },
    "Ranqueamento": {
        "arquivo": "pages/17_Ranking.py",
        "icone": "🏆",
        "descricao": "Rankings, comparações e listas de Pokémon do projeto.",
    },
    "Assistente KAYZAC": {
        "arquivo": "pages/18_Assistente.py",
        "icone": "🤖",
        "descricao": "A IA oficial do KAYZAC.",
    },
}

RESUMO_ESTRUTURA = """
O KAYZAC - MASTER POKEMON é um projeto autoral desenvolvido em Python e Streamlit.

Arquivos importantes conhecidos:
- app.py = roteador principal e página inicial.
- pages/ = pasta das páginas.
- pokemon_index.json = índice de Pokémon.
- pokemon_1.csv = base de dados usada pelo projeto.
- formas_pokemon.json = dados de formas.
- logo.png = logo principal.
- requirements.txt = dependências do projeto.

Páginas conhecidas:
- Início
- Pokédex
- KAYZAC World
- Times
- Personagens
- Biblioteca
- Mídia
- Jogos
- Quiz
- Música
- Cronologia
- Diversidade
- TCG Pocket
- Simulador de Captura
- Gerador de Desafios
- Laboratório de Fusões
- Rom Hacks & Fan Games
- Ranqueamento
- Assistente KAYZAC
"""

INSTRUCOES_ASSISTENTE = """
Você é o Assistente KAYZAC, a IA oficial do site/app KAYZAC - MASTER POKEMON.

IDENTIDADE
- Fale em português do Brasil por padrão.
- Seja amigável, inteligente, claro, prático e levemente descontraído.
- Seu objetivo é ajudar o usuário dentro do KAYZAC e também em assuntos externos.
- Você pode ajudar com Pokémon, Python, Streamlit, escola, trabalho, futebol,
  FIFA/EA Sports FC, GTA 6, tecnologia, jogos, filmes, séries e assuntos gerais.

CONHECIMENTO DO PRÓPRIO KAYZAC
- Use o MAPA DO KAYZAC fornecido no contexto.
- Quando perguntarem "qual página?", informe o nome da página, o arquivo correspondente
  e uma breve explicação do que a página faz.
- Quando perguntarem como encontrar algo no KAYZAC, indique a página mais adequada.
- Não invente arquivos, páginas ou funções que não aparecem no contexto fornecido.
- Se uma informação específica do funcionamento interno não estiver no contexto, diga
  que você não tem esse detalhe disponível e não invente.

PERSONALIZAÇÃO
- Se houver dados do treinador no contexto da sessão, use-os de forma natural.
- Não revele dados técnicos ou segredos do sistema.
- Pode chamar o usuário pelo nome do treinador quando isso deixar a conversa mais natural.

PROGRAMAÇÃO
- Quando ensinar Python/Streamlit, prefira explicações simples e práticas.
- Mostre exemplos pequenos e fáceis de entender.
- Evite reescrever o projeto inteiro quando uma alteração menor for suficiente.
- Quando sugerir código, explique onde colocar e o que ele altera.

INFORMAÇÃO ATUAL
- Quando uma informação puder ter mudado recentemente, use busca na web quando ela
  estiver ativada e disponível.
- Isso é especialmente importante para notícias, lançamentos, jogos, GTA 6,
  EA Sports FC, preços, datas, atualizações e assuntos atuais.
- Não invente fontes nem apresente informação recente como confirmada sem verificar.

CONFIABILIDADE
- Não invente fatos.
- Em assuntos médicos, jurídicos ou financeiros importantes, deixe claro que a resposta
  é informativa e que fontes/profissionais apropriados podem ser necessários.
"""


# ============================================================
# ESTADO DA CONVERSA
# ============================================================

if "assistente_mensagens" not in st.session_state:
    st.session_state.assistente_mensagens = [
        {
            "role": "assistant",
            "content": (
                "⚡ **Olá! Eu sou o Assistente KAYZAC!**\n\n"
                "Agora eu conheço melhor a estrutura do KAYZAC. 😎\n\n"
                "Posso ajudar com o próprio site, Pokémon, Python/Streamlit, "
                "escola, trabalho, FIFA/EA Sports FC, GTA 6 e muito mais."
            ),
        }
    ]

if "assistente_buscar_web" not in st.session_state:
    st.session_state.assistente_buscar_web = True

if "assistente_pergunta_pronta" not in st.session_state:
    st.session_state.assistente_pergunta_pronta = None


# ============================================================
# FUNÇÕES
# ============================================================


def obter_cliente():
    if not API_KEY:
        return None

    try:
        from openai import OpenAI
        return OpenAI(api_key=API_KEY)
    except ImportError:
        return None


def dados_treinador_em_texto():
    nome = st.session_state.get("treinador_nome")
    titulo = st.session_state.get("treinador_titulo")
    regiao = st.session_state.get("treinador_regiao")
    pokemon = st.session_state.get("treinador_pokemon")
    estilo = st.session_state.get("treinador_estilo")

    if not nome and not pokemon:
        return "Não há dados do perfil do treinador disponíveis nesta sessão."

    return (
        f"Nome: {nome or 'não informado'}\n"
        f"Título: {titulo or 'não informado'}\n"
        f"Região: {regiao or 'não informada'}\n"
        f"Pokémon favorito: {pokemon or 'não informado'}\n"
        f"Estilo: {estilo or 'não informado'}"
    )


def mapa_em_texto():
    linhas = []

    for nome, info in PAGINAS_KAYZAC.items():
        linhas.append(
            f"- {info['icone']} {nome} | arquivo: {info['arquivo']} | "
            f"função: {info['descricao']}"
        )

    return "\n".join(linhas)


def gerar_resposta(pergunta):
    cliente = obter_cliente()

    if cliente is None:
        if not API_KEY:
            return (
                "🟡 **O Assistente está instalado, mas a IA ainda não foi conectada.**\n\n"
                "Configure `OPENAI_API_KEY` nos Secrets do Streamlit Cloud."
            )

        return (
            "⚠️ A biblioteca `openai` não está instalada. "
            "Confira o `requirements.txt`."
        )

    historico = st.session_state.assistente_mensagens[-12:]

    contexto_completo = (
        INSTRUCOES_ASSISTENTE
        + "\n\n=== ESTRUTURA DO PROJETO ===\n"
        + RESUMO_ESTRUTURA
        + "\n\n=== MAPA DETALHADO DAS PÁGINAS ===\n"
        + mapa_em_texto()
        + "\n\n=== PERFIL DO TREINADOR NESTA SESSÃO ===\n"
        + dados_treinador_em_texto()
    )

    entrada = [
        {
            "role": "developer",
            "content": contexto_completo,
        }
    ]

    for mensagem in historico:
        entrada.append(
            {
                "role": mensagem["role"],
                "content": mensagem["content"],
            }
        )

    entrada.append({"role": "user", "content": pergunta})

    argumentos = {
        "model": MODELO,
        "input": entrada,
    }

    if st.session_state.assistente_buscar_web:
        argumentos["tools"] = [{"type": "web_search"}]

    try:
        resposta = cliente.responses.create(**argumentos)
        texto = getattr(resposta, "output_text", None)

        if texto:
            return texto

        return "⚠️ A IA respondeu, mas não consegui obter o texto."

    except Exception as erro:
        detalhe = str(erro)

        if "api_key" in detalhe.lower():
            return (
                "🔑 **Problema com a chave da API.** "
                "Confira `OPENAI_API_KEY` nos Secrets do Streamlit Cloud."
            )

        return (
            "⚠️ **Não consegui falar com a IA agora.**\n\n"
            f"Detalhe: `{detalhe}`"
        )


def processar_pergunta(pergunta):
    st.session_state.assistente_mensagens.append(
        {"role": "user", "content": pergunta}
    )

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("🤖 O Assistente KAYZAC está pensando..."):
            resposta = gerar_resposta(pergunta)
        st.markdown(resposta)

    st.session_state.assistente_mensagens.append(
        {"role": "assistant", "content": resposta}
    )


def limpar_conversa():
    st.session_state.assistente_mensagens = [
        {
            "role": "assistant",
            "content": (
                "⚡ **Conversa reiniciada!**\n\n"
                "Pode mandar sua próxima pergunta. 😎"
            ),
        }
    ]


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
        background: linear-gradient(
            135deg,
            rgba(17,140,255,.12),
            rgba(128,128,128,.05)
        );
    }

    .assistente-tag {
        opacity: .78;
        font-size: 1.05rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="assistente-hero">
        <h1>🤖 Assistente KAYZAC</h1>
        <div class="assistente-tag">
            Sua IA para o universo Pokémon... e para muito além dele.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_info, col_config = st.columns([3, 1])

with col_info:
    st.write(
        "Agora o Assistente conhece a estrutura principal do **KAYZAC** e "
        "também pode ajudar com assuntos externos."
    )

with col_config:
    st.toggle(
        "🌐 Usar busca na web",
        key="assistente_buscar_web",
        help="Ative para perguntas que dependem de informações recentes.",
    )

st.divider()


# ============================================================
# ATALHOS
# ============================================================

st.markdown("### ⚡ Atalhos do Assistente")

atalhos = [
    (
        "🧭 Mapa do KAYZAC",
        "Quais são todas as páginas do KAYZAC e o que cada uma faz?",
    ),
    (
        "🧬 Fusões",
        "Qual é a página de fusões do KAYZAC e qual é o arquivo dela?",
    ),
    (
        "📖 Pokédex",
        "O que eu consigo fazer na Pokédex do KAYZAC?",
    ),
    (
        "🎲 Desafios",
        "Onde fica o Gerador de Desafios e para que ele serve?",
    ),
    (
        "🐍 Python",
        "Me ensine uma função simples em Python, passo a passo.",
    ),
    (
        "🎮 Atualidades",
        "Quais assuntos de games atuais você consegue pesquisar para mim?",
    ),
]

colunas = st.columns(3)

for i, (titulo, exemplo) in enumerate(atalhos):
    with colunas[i % 3]:
        if st.button(
            titulo,
            use_container_width=True,
            key=f"atalho_assistente_{i}",
        ):
            st.session_state.assistente_pergunta_pronta = exemplo
            st.rerun()

st.divider()


# ============================================================
# MAPA RÁPIDO
# ============================================================

with st.expander("🗺️ Ver mapa rápido do KAYZAC"):
    for nome, info in PAGINAS_KAYZAC.items():
        st.markdown(
            f"**{info['icone']} {nome}**  \n"
            f"`{info['arquivo']}` — {info['descricao']}"
        )

st.divider()


# ============================================================
# HISTÓRICO
# ============================================================

for mensagem in st.session_state.assistente_mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta_chat = st.chat_input(
    "Pergunte alguma coisa ao Assistente KAYZAC..."
)

pergunta_pronta = st.session_state.assistente_pergunta_pronta
st.session_state.assistente_pergunta_pronta = None

pergunta = pergunta_chat or pergunta_pronta

if pergunta:
    processar_pergunta(pergunta)
    st.rerun()

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "🗑️ Limpar conversa",
        use_container_width=True,
    ):
        limpar_conversa()
        st.rerun()

with col2:
    if API_KEY:
        st.caption("🟢 IA conectada")
    else:
        st.caption("🟡 Configure OPENAI_API_KEY nos Secrets")

st.caption(
    "⚡ KAYZAC - MASTER POKEMON • Assistente oficial do projeto"
)
