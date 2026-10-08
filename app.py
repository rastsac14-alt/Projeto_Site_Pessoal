import streamlit as st


# ==========================
# CONFIGURAÇÃO
# ==========================
st.set_page_config(
    page_title="Kayzac - Master Pokémon",
    page_icon="⚡",
    layout="wide",
)
st.sidebar.image("logo(2).png")

# ==========================
# ESTADO GLOBAL DO TREINADOR
# ==========================

def inicializar_treinador():
    """Cria o perfil do treinador na sessão, sem apagar escolhas existentes."""
    padrao = {
        "treinador_nome": "Treinador KAYZAC",
        "treinador_titulo": "Treinador Pokémon",
        "treinador_regiao": "Kanto",
        "treinador_pokemon": "Lucario",
        "treinador_estilo": "Aura / Equilibrado",
        "treinador_avatar": "⚡",
        "treinador_cor": "Azul KAYZAC",
        "treinador_personalizado": False,
    }

    for chave, valor in padrao.items():
        st.session_state.setdefault(chave, valor)

    st.session_state.setdefault("treinador_personalizacao_aberta", False)


def dados_do_treinador():
    return {
        "nome": st.session_state.get("treinador_nome", "Treinador KAYZAC"),
        "titulo": st.session_state.get("treinador_titulo", "Treinador Pokémon"),
        "regiao": st.session_state.get("treinador_regiao", "Kanto"),
        "pokemon": st.session_state.get("treinador_pokemon", "Lucario"),
        "estilo": st.session_state.get("treinador_estilo", "Aura / Equilibrado"),
        "avatar": st.session_state.get("treinador_avatar", "⚡"),
        "cor": st.session_state.get("treinador_cor", "Azul KAYZAC"),
    }


inicializar_treinador()


# ==========================
# CORES DO PERFIL
# ==========================
CORES_TREINADOR = {
    "Azul KAYZAC": "#118cff",
    "Vermelho": "#ff4b4b",
    "Roxo": "#9b59ff",
    "Verde": "#35c978",
    "Dourado": "#f0b429",
    "Ciano": "#00cfe8",
}

cor_treinador = CORES_TREINADOR.get(
    st.session_state.treinador_cor,
    CORES_TREINADOR["Azul KAYZAC"],
)

st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem;
    }}

    .kayzac-menu {{
        margin-bottom: 1rem;
    }}

    .kayzac-menu h2 {{
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }}

    .kayzac-menu p {{
        margin-bottom: 0.8rem;
    }}

    .kayzac-opcoes {{
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
    }}

    .kayzac-opcoes div {{
        font-size: 1rem;
        padding: 0.25rem 0;
    }}

    .kayzac-menu::after {{
        content: "";
        display: block;
        margin-top: 1rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.35);
    }}

    .trainer-card {{
        border: 1px solid {cor_treinador}55;
        border-radius: 18px;
        padding: 1.2rem;
        background: linear-gradient(135deg, {cor_treinador}18, rgba(128,128,128,.07));
        margin-bottom: 1rem;
    }}

    .trainer-avatar {{
        font-size: 3rem;
        width: 4.5rem;
        height: 4.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        border: 2px solid {cor_treinador}88;
        background: {cor_treinador}20;
        margin-bottom: 0.7rem;
    }}

    .trainer-name {{
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }}

    .trainer-title {{
        opacity: .75;
        margin-bottom: .7rem;
    }}

    .achievement-card {{
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 15px;
        padding: .9rem;
        margin-bottom: .65rem;
        background: rgba(128,128,128,.045);
    }}

    .achievement-unlocked {{
        border-color: {cor_treinador}80;
        background: {cor_treinador}12;
    }}

    .achievement-icon {{
        font-size: 1.6rem;
        margin-right: .35rem;
    }}

    .achievement-title {{
        font-weight: 800;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================
# CONQUISTAS
# ==========================
CONQUISTAS = [
    {
        "id": "primeira_jornada",
        "icone": "🌟",
        "titulo": "Primeira Jornada",
        "descricao": "Comece sua aventura no KAYZAC.",
        "condicao": lambda: True,
    },
    {
        "id": "primeiro_quiz",
        "icone": "🧠",
        "titulo": "Primeiro Desafio",
        "descricao": "Responda pelo menos uma pergunta no KAYZAC Quiz.",
        "condicao": lambda: st.session_state.get("quiz_total_respostas", 0) >= 1,
    },
    {
        "id": "mestre_quiz",
        "icone": "👑",
        "titulo": "Mente de Professor",
        "descricao": "Alcance 10 acertos acumulados no Quiz.",
        "condicao": lambda: st.session_state.get("quiz_total_acertos", 0) >= 10,
    },
    {
        "id": "sequencia_quiz",
        "icone": "🔥",
        "titulo": "Sequência de Aura",
        "descricao": "Consiga uma sequência de 5 acertos no Quiz.",
        "condicao": lambda: st.session_state.get("quiz_melhor_streak", 0) >= 5,
    },
    {
        "id": "xp_quiz",
        "icone": "⚡",
        "titulo": "Treinamento Intenso",
        "descricao": "Acumule 500 XP no Quiz.",
        "condicao": lambda: st.session_state.get("quiz_xp_total", 0) >= 500,
    },
    {
        "id": "midia",
        "icone": "🎬",
        "titulo": "Fã Multimídia",
        "descricao": "Marque 5 itens como concluídos na Central de Mídia.",
        "condicao": lambda: len(st.session_state.get("midia_progresso", set())) >= 5,
    },
    {
        "id": "cronologia",
        "icone": "📜",
        "titulo": "Cronista Pokémon",
        "descricao": "Marque 5 marcos da Cronologia como visitados.",
        "condicao": lambda: len(st.session_state.get("cronologia_visitados", set())) >= 5,
    },
    {
        "id": "cronologia_avancada",
        "icone": "🏛️",
        "titulo": "Guardião da História",
        "descricao": "Marque 15 marcos da Cronologia como visitados.",
        "condicao": lambda: len(st.session_state.get("cronologia_visitados", set())) >= 15,
    },
    {
        "id": "pokemon",
        "icone": "📖",
        "titulo": "Pesquisador Pokémon",
        "descricao": "Abra pelo menos um Pokémon diretamente pela Pokédex.",
        "condicao": lambda: bool(st.session_state.get("pokemon_focado")),
    },
    {
        "id": "perfil",
        "icone": "👤",
        "titulo": "Identidade de Treinador",
        "descricao": "Personalize seu perfil de treinador.",
        "condicao": lambda: bool(st.session_state.get("treinador_personalizado")),
    },
    {
        "id": "xodo",
        "icone": "💙",
        "titulo": "Pokémon Favorito",
        "descricao": "Escolha oficialmente seu Pokémon favorito no perfil.",
        "condicao": lambda: bool(st.session_state.get("treinador_pokemon")),
    },
    {
        "id": "master",
        "icone": "⚡",
        "titulo": "KAYZAC Master",
        "descricao": "Desbloqueie 7 das outras conquistas.",
        "condicao": lambda: sum(
            1
            for conquista in CONQUISTAS[:-1]
            if conquista["condicao"]()
        ) >= 7,
    },
]


def conquistas_desbloqueadas():
    return [
        conquista
        for conquista in CONQUISTAS
        if conquista["condicao"]()
    ]


def abrir_personalizacao():
    st.session_state.treinador_personalizacao_aberta = True


def salvar_personalizacao():
    st.session_state.treinador_nome = st.session_state.form_treinador_nome.strip() or "Treinador KAYZAC"
    st.session_state.treinador_titulo = st.session_state.form_treinador_titulo
    st.session_state.treinador_regiao = st.session_state.form_treinador_regiao
    st.session_state.treinador_pokemon = st.session_state.form_treinador_pokemon.strip().title() or "Lucario"
    st.session_state.treinador_estilo = st.session_state.form_treinador_estilo
    st.session_state.treinador_avatar = st.session_state.form_treinador_avatar
    st.session_state.treinador_cor = st.session_state.form_treinador_cor
    st.session_state.treinador_personalizado = True
    st.session_state.treinador_personalizacao_aberta = False


def render_card_treinador():
    dados = dados_do_treinador()
    st.markdown(
        f"""
        <div class="trainer-card">
            <div class="trainer-avatar">{dados['avatar']}</div>
            <div class="trainer-name">{dados['nome']}</div>
            <div class="trainer-title">{dados['titulo']}</div>
            <div>🌎 <b>Região:</b> {dados['regiao']}</div>
            <div>⭐ <b>Pokémon favorito:</b> {dados['pokemon']}</div>
            <div>🎯 <b>Estilo:</b> {dados['estilo']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_resumo_conquistas():
    desbloqueadas = conquistas_desbloqueadas()
    total = len(CONQUISTAS)
    quantidade = len(desbloqueadas)
    percentual = round((quantidade / total) * 100) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Desbloqueadas", f"{quantidade}/{total}")
    c2.metric("📈 Progresso", f"{percentual}%")
    c3.metric("⚡ XP do Quiz", st.session_state.get("quiz_xp_total", 0))

    st.progress(percentual / 100 if total else 0)


def render_conquistas_destaque():
    desbloqueadas = conquistas_desbloqueadas()
    restantes = [
        conquista
        for conquista in CONQUISTAS
        if conquista not in desbloqueadas
    ]

    st.markdown("### 🏆 Conquistas")
    if desbloqueadas:
        colunas = st.columns(2)
        for indice, conquista in enumerate(desbloqueadas):
            with colunas[indice % 2]:
                st.markdown(
                    f"""
                    <div class="achievement-card achievement-unlocked">
                        <span class="achievement-icon">{conquista['icone']}</span>
                        <span class="achievement-title">{conquista['titulo']}</span>
                        <div>{conquista['descricao']}</div>
                        <small>✅ Desbloqueada</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Suas primeiras conquistas aparecerão aqui conforme você explorar o KAYZAC.")

    with st.expander(f"🔒 Próximas conquistas ({len(restantes)})"):
        for conquista in restantes:
            st.markdown(
                f"**{conquista['icone']} {conquista['titulo']}** — {conquista['descricao']}"
            )

# ==========================
# PÁGINAS / NAVEGAÇÃO
# ==========================

# O app.py passa a ser o roteador principal do KAYZAC.
# A navegação nativa do Streamlit fica oculta e criamos um menu
# totalmente personalizado no sidebar, na ordem que queremos.

pagina_inicio = st.Page(
    lambda: render_inicio(),
    title="Início",
    icon="🏠",
    url_path="",
    default=True,
)

pagina_pokedex = st.Page(
    "pages/1_Pokedex.py",
    title="Pokédex",
    icon="📖",
    url_path="pokedex",
)

pagina_mundo = st.Page(
    "pages/2_Mundo.py",
    title="KAYZAC World",
    icon="🌎",
    url_path="mundo",
)

pagina_times = st.Page(
    "pages/3_Times.py",
    title="Times",
    icon="⚔️",
    url_path="times",
)

pagina_personagens = st.Page(
    "pages/4_Personagens.py",
    title="Personagens",
    icon="👥",
    url_path="personagens",
)

pagina_biblioteca = st.Page(
    "pages/5_Biblioteca.py",
    title="Biblioteca",
    icon="📚",
    url_path="biblioteca",
)

pagina_midia = st.Page(
    "pages/6_Midia.py",
    title="Mídia",
    icon="🎬",
    url_path="midia",
)

pagina_jogos = st.Page(
    "pages/7_Jogos.py",
    title="Jogos",
    icon="🎮",
    url_path="jogos",
)

pagina_quiz = st.Page(
    "pages/8_Quiz.py",
    title="Quiz",
    icon="🧠",
    url_path="quiz",
)

pagina_musica = st.Page(
    "pages/9_Musica.py",
    title="Música",
    icon="🎵",
    url_path="musica",
)

pagina_cronologia = st.Page(
    "pages/10_Cronologia.py",
    title="Cronologia",
    icon="📜",
    url_path="cronologia",
)

pagina_tcg = st.Page(
    "pages/12_TCG.py",
    title="TCG Pocket",
    icon="🃏",
    url_path="tcg",
)

pagina_diversidade = st.Page(
    "pages/11_Diversidade.py",
    title="Diversidade",
    icon="🌈",
    url_path="diversidade",
)

pagina_captura = st.Page(
    "pages/13_Capturas.py",
    title="Simulador de Captura",
    icon="🎯",
    url_path="captura",
)

pagina_desafios = st.Page(
    "pages/14_Desafios.py",
    title="Gerador de Desafios",
    icon="🎲",
    url_path="desafios",
)
pagina_fusoes = st.Page(
    "pages/15_Fusoes.py",
    title="Laboratório de Fusões",
    icon="🧬",
    url_path="fusoes",
)
pagina_fangames = st.Page(
    "pages/16_Roms.py",
    title="Rom Hacks & Fan Games", 
    icon="🎮",
    url_path="fangames",
)
pagina_ranking = st.Page(
    "pages/17_Ranking.py",
    title="Ranqueamento Pokemon", 
    icon="🏆",
    url_path="ranking",
)

pagina_assistente = st.Page(
    "pages/18_Assistente.py",
    title="Assistente KAYZAC",
    icon="🤖",
    url_path="assistente",
)

PAGINAS = {
    "inicio": pagina_inicio,
    "pokedex": pagina_pokedex,
    "mundo": pagina_mundo,
    "times": pagina_times,
    "personagens": pagina_personagens,
    "biblioteca": pagina_biblioteca,
    "midia": pagina_midia,
    "jogos": pagina_jogos,
    "quiz": pagina_quiz,
    "musica": pagina_musica,
    "cronologia": pagina_cronologia,
    "diversidade": pagina_diversidade,
    "tcg": pagina_tcg,
    "captura": pagina_captura,
    "desafios": pagina_desafios,
    "fusoes": pagina_fusoes,
    "fangames": pagina_fangames,
    "ranking": pagina_ranking,
    "assistente": pagina_assistente,
}

# A navegação nativa é escondida para que o nosso menu personalizado
# seja o único menu visível na lateral.
pagina_atual = st.navigation(
    [
        pagina_inicio,
        pagina_pokedex,
        pagina_mundo,
        pagina_times,
        pagina_personagens,
        pagina_biblioteca,
        pagina_midia,
        pagina_jogos,
        pagina_quiz,
        pagina_musica,
        pagina_cronologia,
        pagina_diversidade,
        pagina_tcg,
        pagina_captura,
        pagina_desafios,
        pagina_fusoes,
        pagina_fangames,
        pagina_ranking,
        pagina_assistente,
    ],
    position="hidden",
)


# ==========================
# MENU LATERAL PERSONALIZADO
# ==========================

with st.sidebar:
    st.markdown("## 🎯 Escolha uma opção")
    st.caption("Explore o universo KAYZAC")
    st.divider()

    st.page_link(
        PAGINAS["inicio"],
        label="Início",
        icon="🏠",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["pokedex"],
        label="Pokédex",
        icon="📖",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["mundo"],
        label="KAYZAC World",
        icon="🌎",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["times"],
        label="Times",
        icon="⚔️",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["personagens"],
        label="Personagens",
        icon="👥",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["biblioteca"],
        label="Biblioteca",
        icon="📚",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["midia"],
        label="Mídia",
        icon="🎬",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["jogos"],
        label="Jogos",
        icon="🎮",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["quiz"],
        label="Quiz",
        icon="🧠",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["musica"],
        label="Música",
        icon="🎵",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["cronologia"],
        label="Cronologia",
        icon="📜",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["diversidade"],
        label="Diversidade",
        icon="🌈",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["tcg"],
        label="TCG Pocket",
        icon="🃏",
        use_container_width=True,
    )
    st.page_link(PAGINAS["captura"], label="Simulador de Captura", icon="🎯", use_container_width=True)
    st.page_link(PAGINAS["desafios"], label="Gerador de Desafios", icon="🎲", use_container_width=True)
    st.page_link(PAGINAS["fusoes"], label="Laboratório de Fusões", icon="🧬", use_container_width=True)
    st.page_link(PAGINAS["fangames"], label="Rom Hacks & Fan Games", icon="🎮", use_container_width=True)
    st.page_link(
        PAGINAS["ranking"],
        label="Ranqueamento",
        icon="🏆",
        use_container_width=True,
    )
    st.page_link(
        PAGINAS["assistente"],
        label="Assistente KAYZAC",
        icon="🤖",
        use_container_width=True,
    )
    st.divider()

    # ==========================
    # MINI-DEX DO TREINADOR
    # ==========================
    perfil = dados_do_treinador()
    st.markdown("### ⚡ Treinador KAYZAC")
    st.caption("Mini-Dex do seu perfil")

    st.markdown(
        f"""
        <div class="trainer-card">
            <div class="trainer-avatar">{perfil['avatar']}</div>
            <div class="trainer-name">{perfil['nome']}</div>
            <div class="trainer-title">{perfil['titulo']} • {perfil['regiao']}</div>
            <div>⭐ <b>Favorito:</b> {perfil['pokemon']}</div>
            <div>🎯 <b>Estilo:</b> {perfil['estilo']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_side_1, col_side_2 = st.columns(2)
    with col_side_1:
        st.metric("🏆 Conquistas", len(conquistas_desbloqueadas()))
    with col_side_2:
        st.metric("⚡ XP", st.session_state.get("quiz_xp_total", 0))

    st.button(
        "👤 Personalizar Treinador",
        use_container_width=True,
        on_click=abrir_personalizacao,
    )

    # ==========================
    # FORMULÁRIO DE PERSONALIZAÇÃO
    # ==========================
    if st.session_state.treinador_personalizacao_aberta:
        st.divider()
        st.markdown("### ✨ Personalização")

        regioes_treinador = [
            "Kanto", "Johto", "Hoenn", "Sinnoh", "Hisui", "Unova",
            "Kalos", "Alola", "Galar", "Paldea", "Mundo Pokémon"
        ]

        estilos_treinador = [
            "Aura / Equilibrado",
            "Competitivo",
            "Explorador",
            "Colecionador",
            "Especialista em formas",
            "Pesquisador",
            "Treinador de histórias",
        ]

        avatares_treinador = [
            "⚡", "🥊", "🔥", "🌊", "🌿", "✨", "👑", "🧢", "🎮", "🧠"
        ]

        with st.form("form_personalizacao_treinador"):
            st.text_input(
                "Nome do treinador",
                value=perfil["nome"],
                key="form_treinador_nome",
            )
            st.text_input(
                "Título",
                value=perfil["titulo"],
                key="form_treinador_titulo",
            )
            st.selectbox(
                "Região",
                regioes_treinador,
                index=regioes_treinador.index(perfil["regiao"]),
                key="form_treinador_regiao",
            )
            st.text_input(
                "Pokémon favorito",
                value=perfil["pokemon"],
                key="form_treinador_pokemon",
            )
            st.selectbox(
                "Estilo de treinador",
                estilos_treinador,
                index=estilos_treinador.index(perfil["estilo"]),
                key="form_treinador_estilo",
            )
            st.selectbox(
                "Avatar",
                avatares_treinador,
                index=avatares_treinador.index(perfil["avatar"]),
                key="form_treinador_avatar",
            )
            st.selectbox(
                "Cor do perfil",
                list(CORES_TREINADOR.keys()),
                index=list(CORES_TREINADOR.keys()).index(perfil["cor"]),
                key="form_treinador_cor",
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button(
                    "💾 Salvar",
                    use_container_width=True,
                )
            with col_cancelar:
                cancelar = st.form_submit_button(
                    "↩️ Fechar",
                    use_container_width=True,
                )

            if salvar:
                salvar_personalizacao()
                st.rerun()

            if cancelar:
                st.session_state.treinador_personalizacao_aberta = False
                st.rerun()

    st.caption(
        "🏆 As conquistas e o perfil usam o estado da sessão do KAYZAC e acompanham as páginas do projeto."
    )


# ==========================
# PÁGINA INICIAL
# ==========================

def render_inicio():
    # ==========================
    # CABEÇALHO
    # ==========================
    st.title("⚡ KAYZAC - MASTER POKEMON! ⚡")
    st.subheader("🌟 Meu primeiro site 100% autoral")


    # ==========================
    # LOGO
    # ==========================
    st.image("logo.png")
    st.divider()


    # ==========================
    # PERFIL + CONQUISTAS
    # ==========================
    col_perfil, col_conquistas = st.columns([1, 2])

    with col_perfil:
        st.header("👤 Meu Treinador")
        render_card_treinador()
        st.button(
            "✨ Abrir personalização",
            use_container_width=True,
            on_click=abrir_personalizacao,
            key="inicio_abrir_personalizacao",
        )

    with col_conquistas:
        st.header("🏆 Meu Progresso")
        render_resumo_conquistas()
        st.caption("Seu perfil e suas conquistas acompanham a exploração do KAYZAC durante a sessão.")

    st.divider()


    # ==========================
    # APRESENTAÇÃO
    # ==========================
    st.write(
        """
        Bem-vindo ao **KAYZAC - MASTER POKEMON!** 🎮⚡

        Este é um projeto criado por um verdadeiro fã de Pokémon,
        reunindo informações, regiões, Pokémon, rotas, mapas e muito mais
        em um único lugar.
        """
    )

    st.info("👈 Utilize o menu lateral para começar sua jornada!")
    st.divider()


    # ==========================
    # SOBRE O PROJETO
    # ==========================
    st.header("💙 Sobre este projeto")
    st.write(
        """
        A ideia do **KAYZAC - MASTER POKEMON!** nasceu de uma coisa bem simples:
        eu gosto de Pokémon para **caramba**. 😂⚡

        Pokémon é uma franquia que sempre chamou muito a minha atenção,
        seja pelos Pokémon, pelas regiões, pelas batalhas, pelas evoluções,
        pelas formas especiais ou simplesmente pela diversão de explorar
        esse universo.

        Por isso, decidi transformar esse gosto em um projeto meu:
        uma Pokédex feita do meu jeito, com as informações que eu gostaria
        de encontrar em um único lugar.
        """
    )

    st.success("⭐ Curiosidade: este é o meu **primeiro site 100% autoral**!")
    st.write(
        """
        E talvez seja justamente isso que torna este projeto tão especial
        para mim.

        Ele começou como uma ideia simples e foi crescendo aos poucos,
        ganhando novas funções, novas páginas e cada vez mais detalhes.
        Mais do que apenas um site, o **KAYZAC - MASTER POKEMON!** é um
        projeto feito para aprender, testar ideias e, principalmente,
        colocar em prática uma franquia que eu gosto muito.
        """
    )

    st.divider()


    # ==========================
    # O QUE VOCÊ ENCONTRARÁ
    # ==========================
    st.header("🎯 O que você encontrará aqui?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📖 Pokédex")
        st.write(
            """
            Pesquise Pokémon, veja seus tipos,
            habilidades, estatísticas, golpes,
            artworks e muito mais.
            """
        )

    with col2:
        st.subheader("🌎 Regiões")
        st.write(
            """
            Explore as regiões do mundo Pokémon,
            seus professores, campeões, cidades
            e ginásios.
            """
        )

    with col3:
        st.subheader("🗺️ Mundo")
        st.write(
            """
            Explore rotas, cidades, locais importantes
            e descubra quais Pokémon podem ser encontrados
            em cada área.
            """
        )

    st.divider()


    # ==========================
    # CONQUISTAS EM DESTAQUE
    # ==========================
    render_conquistas_destaque()
    st.divider()


    # ==========================
    # MAIS DETALHES
    # ==========================
    st.header("🚀 Um projeto que continua crescendo")
    st.write(
        """
        A proposta do KAYZAC - MASTER POKEMON! não é ser apenas uma
        Pokédex comum.
        A ideia é transformar o projeto, aos poucos, em uma verdadeira
        **enciclopédia Pokémon**, com informações sobre:
        """
    )

    st.markdown(
        """
        🧬 **Linhas evolutivas**

        ✨ **Formas e transformações**

        💥 **Mega Evoluções**

        🏰 **Gigantamax**

        🥚 **Reprodução**

        📈 **Treinamento**

        ⚔️ **Golpes e habilidades**

        📖 **Histórico por geração**

        🗺️ **Regiões e locais**

        📊 **Estatísticas**

        🧠 **Quiz e conhecimento**

        🎵 **Músicas e sons**

        📜 **Cronologia da franquia**

        🏆 **Conquistas**

        👤 **Perfil e personalização do treinador**
        """
    )

    st.write(
        """
        E este é apenas o começo. 😎

        Conforme o projeto cresce, novas ideias podem aparecer,
        novas funções podem ser adicionadas e a Master Pokémon
        pode ficar cada vez mais completa.
        """
    )

    st.divider()


    # ==========================
    # CURIOSIDADE DO CRIADOR
    # ==========================
    st.header("🎮 Curiosidade do criador")
    st.write(
        """
        Uma das coisas mais legais desse projeto é que ele não nasceu
        simplesmente como um exercício de programação.

        Ele nasceu porque eu realmente gosto dessa franquia.
        Cada nova função adicionada à Master Pokémon é também uma forma
        de juntar duas coisas que eu curto muito: **Pokémon e programação**. 💙⚡

        Por isso, este site representa algo especial para mim:
        ele é o meu **primeiro site autoral**, construído aos poucos,
        experimentando ideias e transformando tudo isso em algo que
        realmente tenha a minha cara.
        """
    )

    st.success(
        "💙 Pokémon foi a inspiração. "
        "A programação foi a ferramenta. "
        "A KAYZAC - MASTER POKEMON! é o resultado!"
    )

    st.divider()


    # ==========================
    # MENSAGEM FINAL
    # ==========================
    st.header("⚡ Agora é com você!")
    st.write(
        """
        Escolha uma das opções no menu lateral e comece a explorar.
        Pegue sua Pokébola, escolha seu Pokémon favorito
        e aproveite a jornada! 🎮⚡
        """
    )

    st.success("⚡ Prepare sua Pokébola, treinador! Sua jornada começa agora!")

    st.caption(
        "💙 Feito com carinho por um fã de Pokémon, "
        "em seu primeiro projeto de site autoral."
    )


# ==========================
# EXECUÇÃO DA PÁGINA SELECIONADA
# ==========================
pagina_atual.run()
