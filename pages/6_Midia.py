from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Mídia Pokémon",
    page_icon="🎬",
    layout="wide",
)


# ============================================================
# IDENTIDADE
# ============================================================

st.title("🎬 KAYZAC MEDIA")
st.markdown(
    "### 📚 Leia, assista, descubra e acompanhe o universo Pokémon"
)
st.caption(
    "Um hub de mídia dentro do KAYZAC: mangás, anime, filmes, especiais, curtas e progresso."
)

st.info(
    "📌 O KAYZAC não hospeda scans completos, episódios pirateados nem traduções integrais de obras protegidas. "
    "Quando houver conteúdo oficial gratuito, ele pode ser aberto ou incorporado; nos demais casos, o site direciona "
    "para a fonte oficial, preview ou página de distribuição correspondente."
)


# ============================================================
# LINKS OFICIAIS
# ============================================================

LINKS_OFICIAIS = {
    "pokemon": "https://www.pokemon.com/br/",
    "youtube_pokemon": "https://www.youtube.com/@Pokemon",
    "pokemon_horizons": "https://horizons.pokemon.com/pt-br/",
    "pokemon_horizons_episodios": "https://www.pokemon.com/br/animacoes/horizontes/1/",
    "viz": "https://www.viz.com/",
    "viz_emerald_26": "https://www.viz.com/manga-books/manga/pokemon-adventures-volume-26/product/2410/digital",
    "viz_emerald_29": "https://www.viz.com/manga-books/manga/pokemon-adventures-volume-29-0/product/2413/digital",
    "youtube_ep1": "https://www.youtube.com/watch?v=z3hMX65Khtg",
}


# ============================================================
# DADOS — MANGÁ
# ============================================================

MANGAS = {
    "Pokémon Adventures / Special": {
        "descricao": (
            "Principal linha de mangá baseada nos jogos, conhecida no Ocidente como Pokémon Adventures. "
            "Os arcos acompanham diferentes protagonistas, regiões e conflitos."
        ),
        "categoria": "Mangá principal",
        "regiao": "Kanto → Paldea",
        "arcos": [
            ("Red, Green & Blue", "Kanto", "Primeiros anos de Pokémon Adventures"),
            ("Yellow", "Kanto", "Arco centrado na Yellow e no desenvolvimento de Red"),
            ("Gold, Silver & Crystal", "Johto", "Johto, Suicune, Lugia, Ho-Oh e Team Rocket"),
            ("Ruby & Sapphire", "Hoenn", "Competição, coordenação e o conflito Aqua/Magma"),
            ("Emerald", "Hoenn", "Battle Frontier, Jirachi e o desafio de Emerald"),
            ("FireRed & LeafGreen", "Kanto", "Retorno a Kanto e o arco pós-Hoenn"),
            ("Diamond & Pearl / Platinum", "Sinnoh", "Sinnoh, Team Galactic e Battle Zone"),
            ("HeartGold & SoulSilver", "Johto", "Retorno de Gold, Silver e Crystal"),
            ("Black & White", "Unova", "Black, White e Team Plasma"),
            ("Black 2 & White 2", "Unova", "Continuação do conflito em Unova"),
            ("X & Y", "Kalos", "Mega Evolution, Team Flare e os treinadores de Vaniville"),
            ("Omega Ruby & Alpha Sapphire", "Hoenn", "Novo arco de Hoenn e crise de grande escala"),
            ("Sun & Moon", "Alola", "Ilhas, Ultra Beasts e o cotidiano de Alola"),
            ("Sword & Shield", "Galar", "Galar, Gym Challenge e fenômeno Dynamax"),
            ("Scarlet & Violet", "Paldea", "Paldea, Academia e as aventuras mais recentes da linha"),
        ],
        "fontes": [
            ("🌐 VIZ", LINKS_OFICIAIS["viz"]),
        ],
    },
    "Pokémon Adventures — Emerald": {
        "descricao": (
            "Arco de Hoenn focado em Emerald e na Battle Frontier. A página de mídia do KAYZAC oferece "
            "atalhos para previews oficiais disponíveis na VIZ, sem reproduzir as páginas protegidas."
        ),
        "categoria": "Pokémon Adventures",
        "regiao": "Hoenn",
        "arcos": [
            ("Volume 26", "Emerald", "Início do arco; Emerald chega à Battle Frontier e enfrenta os desafios iniciais."),
            ("Volume 27", "Emerald", "Continuação do arco de Battle Frontier."),
            ("Volume 28", "Emerald", "Continuação das batalhas e do conflito de Hoenn."),
            ("Volume 29", "Emerald", "Confronto final do arco envolvendo Jirachi e os heróis de Hoenn."),
        ],
        "fontes": [
            ("📖 Preview oficial — Vol. 26", LINKS_OFICIAIS["viz_emerald_26"]),
            ("📖 Preview oficial — Vol. 29", LINKS_OFICIAIS["viz_emerald_29"]),
            ("🌐 VIZ", LINKS_OFICIAIS["viz"]),
        ],
    },
    "Outros mangás Pokémon": {
        "descricao": "Linhas derivadas e adaptações diferentes da série Adventures.",
        "categoria": "Mangás derivados",
        "regiao": "Variada",
        "arcos": [
            ("Pokémon Pocket Monsters", "Diversas", "Mangá cômico de longa duração com uma abordagem própria."),
            ("Magical Pokémon Journey", "Diversas", "Aventura de tom mais leve e fantástico."),
            ("Pokémon Mystery Dungeon", "Mundos Pokémon", "Histórias baseadas nos jogos Mystery Dungeon."),
            ("Pokémon Diamond & Pearl Adventure!", "Sinnoh", "Outra adaptação da geração de Sinnoh."),
            ("Pokémon Journeys", "Mundo Pokémon", "Adaptação em mangá da fase Journeys do anime."),
        ],
        "fontes": [
            ("🌐 VIZ", LINKS_OFICIAIS["viz"]),
        ],
    },
}


# ============================================================
# DADOS — ANIME PRINCIPAL
# ============================================================

ANIME_SERIES = {
    "Pokémon — Série Original": {
        "regioes": "Kanto / Ilhas Laranja / Johto",
        "era": "1997–2002",
        "descricao": "A jornada clássica de Ash e Pikachu, começando em Pallet Town e avançando por Kanto, Orange Islands e Johto.",
        "personagens": ["Ash", "Pikachu", "Misty", "Brock", "Jessie", "James"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon Advanced Generation": {
        "regioes": "Hoenn / Battle Frontier",
        "era": "2002–2006",
        "descricao": "Ash viaja por Hoenn e depois retorna à Kanto para enfrentar a Battle Frontier.",
        "personagens": ["Ash", "Pikachu", "May", "Max", "Brock"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon Diamond & Pearl": {
        "regioes": "Sinnoh",
        "era": "2006–2010",
        "descricao": "A jornada de Ash em Sinnoh ao lado de Dawn e Brock, com destaque para batalhas, concursos e o conflito de Team Galactic.",
        "personagens": ["Ash", "Pikachu", "Dawn", "Brock", "Paul"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon Black & White": {
        "regioes": "Unova",
        "era": "2010–2013",
        "descricao": "A aventura de Ash por Unova e os encontros com Iris, Cilan e os conflitos envolvendo Team Plasma.",
        "personagens": ["Ash", "Pikachu", "Iris", "Cilan", "N"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon XY / XYZ": {
        "regioes": "Kalos",
        "era": "2013–2016",
        "descricao": "Kalos, Mega Evolution, Greninja e uma das fases mais focadas em batalhas e crescimento do Ash.",
        "personagens": ["Ash", "Pikachu", "Serena", "Clemont", "Bonnie", "Alain"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon Sun & Moon": {
        "regioes": "Alola",
        "era": "2016–2019",
        "descricao": "Ash estuda na Escola Pokémon em Alola e participa de desafios insulares enquanto constrói novas amizades.",
        "personagens": ["Ash", "Pikachu", "Lillie", "Kiawe", "Mallow", "Sophocles", "Lana"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon Journeys": {
        "regioes": "Todas as regiões",
        "era": "2019–2023",
        "descricao": "Ash e Goh exploram o mundo Pokémon enquanto investigam Pokémon de várias regiões e enfrentam o projeto de pesquisa do Professor Cerise.",
        "personagens": ["Ash", "Pikachu", "Goh", "Chloe", "Professor Cerise"],
        "tipo": "Série principal",
        "fonte": ("▶️ Canal oficial Pokémon", LINKS_OFICIAIS["youtube_pokemon"]),
    },
    "Pokémon: Horizontes": {
        "regioes": "Paldea / Mundo Pokémon",
        "era": "2023–atual",
        "descricao": "Nova protagonista, Liko, e Rain entram em uma aventura sem Ash como protagonista, acompanhados por Sprigatito, Fuecoco e os Trovonautas.",
        "personagens": ["Liko", "Rain", "Sprigatito", "Fuecoco", "Friede", "Capitão Pikachu"],
        "tipo": "Série principal",
        "fonte": ("📺 Guia oficial de episódios", LINKS_OFICIAIS["pokemon_horizons_episodios"]),
    },
}


# ============================================================
# DADOS — ESPECIAIS / SÉRIES CURTAS
# ============================================================

ESPECIAIS_ANIMADOS = {
    "Pokémon Origins": {
        "tipo": "Especial",
        "descricao": "Minissérie que acompanha Red em uma adaptação mais próxima dos jogos Pokémon Red, Green, Blue e FireRed/LeafGreen.",
        "regiao": "Kanto",
    },
    "Pokémon Generations": {
        "tipo": "Minissérie",
        "descricao": "Episódios curtos que exploram acontecimentos do mundo Pokémon por vários pontos de vista.",
        "regiao": "Diversas",
    },
    "Pokémon Evolutions": {
        "tipo": "Minissérie",
        "descricao": "Histórias curtas ambientadas nas regiões da série principal, com foco em personagens e momentos marcantes.",
        "regiao": "Kanto → Galar",
    },
    "Pokémon Twilight Wings": {
        "tipo": "Minissérie",
        "descricao": "Curtas ambientados em Galar, explorando personagens e suas relações com Pokémon.",
        "regiao": "Galar",
    },
    "Pokémon: Hisuian Snow": {
        "tipo": "Minissérie",
        "descricao": "Aventura em Hisui protagonizada por Alec e seu relacionamento com Pokémon em uma região ainda em formação.",
        "regiao": "Hisui",
    },
    "Pokémon: Paldean Winds": {
        "tipo": "Minissérie",
        "descricao": "História original em Paldea acompanhando jovens personagens e seus Pokémon.",
        "regiao": "Paldea",
    },
    "Pokémon: Path to the Peak": {
        "tipo": "Minissérie",
        "descricao": "A jornada de Ava e seu Pikachu no universo competitivo do Pokémon Estampas Ilustradas.",
        "regiao": "Mundo Pokémon",
    },
    "POKÉTOON": {
        "tipo": "Curtas",
        "descricao": "Coleção de animações independentes e curtas, normalmente com foco em uma pequena história e um ou mais Pokémon.",
        "regiao": "Mundo Pokémon",
    },
}


# ============================================================
# DADOS — FILMES
# ============================================================

FILMES = [
    ("Pokémon — Mewtwo Contra-Ataca", 1998, "Mewtwo"),
    ("Pokémon 2000 — O Poder de Um", 1999, "Lugia"),
    ("Pokémon 3 — O Feitiço dos Unown", 2000, "Entei / Unown"),
    ("Pokémon 4Ever — Celebi, a Voz da Floresta", 2001, "Celebi"),
    ("Pokémon Heróis — Latias & Latios", 2002, "Latias / Latios"),
    ("Pokémon: Jirachi — Realizador de Desejos", 2003, "Jirachi"),
    ("Pokémon: Deoxys, o Destino", 2004, "Deoxys"),
    ("Pokémon: Lucario e o Mistério de Mew", 2005, "Lucario / Mew"),
    ("Pokémon Ranger e o Templo do Mar", 2006, "Manaphy"),
    ("Pokémon: O Pesadelo de Darkrai", 2007, "Darkrai"),
    ("Pokémon: Giratina e o Cavaleiro do Céu", 2008, "Giratina / Shaymin"),
    ("Pokémon: Arceus e a Joia da Vida", 2009, "Arceus"),
    ("Pokémon: Zoroark — Mestre das Ilusões", 2010, "Zoroark"),
    ("Pokémon, o Filme: Branco — Victini e Zekrom", 2011, "Victini / Zekrom"),
    ("Pokémon, o Filme: Preto — Victini e Reshiram", 2011, "Victini / Reshiram"),
    ("Pokémon, o Filme: Kyurem contra a Espada da Justiça", 2012, "Kyurem / Keldeo"),
    ("Pokémon, o Filme: Genesect e a Lenda Revelada", 2013, "Genesect / Mewtwo"),
    ("Pokémon, o Filme: Diancie e o Casulo da Destruição", 2014, "Diancie / Yveltal"),
    ("Pokémon, o Filme: Hoopa e o Duelo Lendário", 2015, "Hoopa"),
    ("Pokémon, o Filme: Volcanion e a Engenhosa Magiana", 2016, "Volcanion / Magearna"),
    ("Pokémon, o Filme: Eu Escolho Você!", 2017, "Pikachu / Ash"),
    ("Pokémon, o Filme: O Poder de Todos", 2018, "Lugia / vários Pokémon"),
    ("Pokémon: Mewtwo Contra-Ataca — Evolução", 2019, "Mewtwo"),
    ("Pokémon: Segredos da Selva", 2020, "Zarude"),
]

FILMES_LIVE_ACTION = [
    ("Pokémon: Detetive Pikachu", 2019, "Detetive Pikachu / Mewtwo"),
]


# ============================================================
# DADOS — POKÉTOON / CURTAS RECENTES
# ============================================================

POKETOON_2026 = [
    ("Pawmi, Pawmo, Pawmot", "Um curta com os três Pokémon elétricos e uma história de amizade em família."),
    ("Cante! Dance! Altaria!", "Swablu encontra uma garota que também ama cantar e busca um parceiro para o palco."),
    ("Aparição em Massa de Clodsire", "Wooper e Clodsire de Paldea aparecem em uma aventura com uma jovem e sua pelúcia de Wooper."),
    ("Minha Jornada Gogoat", "Um garoto e um Gogoat misterioso embarcam em uma aventura pela cidade."),
    ("A Lenda de Capsakid", "Uma jovem e seu Capsakid atravessam uma amizade cheia de energia e batalhas."),
    ("Diário de um Primeape Furioso", "Um jovem treinador tenta entender por que seu Primeape está sempre irritado."),
]


# ============================================================
# ESTADO DE PROGRESSO
# ============================================================

if "midia_progresso" not in st.session_state:
    st.session_state.midia_progresso = set()


def chave_progresso(tipo: str, nome: str, item: str) -> str:
    return f"{tipo}|{nome}|{item}"


def alternar_progresso(chave: str) -> None:
    if chave in st.session_state.midia_progresso:
        st.session_state.midia_progresso.remove(chave)
    else:
        st.session_state.midia_progresso.add(chave)


# ============================================================
# COMPONENTES
# ============================================================


def botao_progresso(chave: str, texto: str = "✅ Marcar como concluído") -> None:
    concluido = chave in st.session_state.midia_progresso
    label = "↩️ Desmarcar" if concluido else texto
    if st.button(label, key=f"progresso_{chave}", use_container_width=True):
        alternar_progresso(chave)
        st.rerun()


def render_fontes(fontes: list[tuple[str, str]]) -> None:
    st.markdown("#### 🔗 Fontes / plataformas")
    for texto, url in fontes:
        st.link_button(texto, url, use_container_width=True)


def render_capa_midia(emoji: str, titulo: str, subtitulo: str) -> None:
    st.markdown(
        f"""
        <div style="border:1px solid rgba(128,128,128,.35); border-radius:16px; padding:20px; margin-bottom:14px;">
            <div style="font-size:42px;">{emoji}</div>
            <h2 style="margin:0 0 6px 0;">{titulo}</h2>
            <p style="margin:0; opacity:.8;">{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TABS PRINCIPAIS
# ============================================================

tab_manga, tab_anime, tab_filmes, tab_curta, tab_progresso, tab_sobre = st.tabs(
    [
        "📚 Mangá",
        "📺 Anime",
        "🎬 Filmes & Especiais",
        "🎞️ Curtas",
        "🏆 Meu Progresso",
        "ℹ️ Sobre",
    ]
)


# ============================================================
# 📚 MANGÁ
# ============================================================

with tab_manga:
    render_capa_midia(
        "📚",
        "Central de Mangás Pokémon",
        "Explore séries, arcos e previews oficiais sem hospedar scans protegidos.",
    )

    escolha_manga = st.selectbox(
        "📖 Escolha uma linha de mangá",
        list(MANGAS.keys()),
        key="midia_manga_escolhido",
    )
    dados = MANGAS[escolha_manga]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Categoria", dados["categoria"])
    with col2:
        st.metric("Região", dados["regiao"])
    with col3:
        st.metric("Arcos/volumes", len(dados["arcos"]))

    st.write(dados["descricao"])
    st.divider()

    st.markdown("### 📑 Arcos / volumes")
    for idx, (titulo, regiao, descricao) in enumerate(dados["arcos"]):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{titulo}**")
                st.caption(f"🌎 {regiao} · {descricao}")
            with c2:
                botao_progresso(chave_progresso("manga", escolha_manga, titulo))

    st.divider()
    render_fontes(dados["fontes"])

    if escolha_manga == "Pokémon Adventures — Emerald":
        st.divider()
        st.markdown("### 🎯 Destaque: Emerald")
        st.success(
            "Os volumes 26 e 29 possuem páginas de preview disponibilizadas oficialmente pela VIZ. "
            "O KAYZAC abre esses previews diretamente na fonte oficial."
        )
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("📖 Ler preview oficial — Vol. 26", LINKS_OFICIAIS["viz_emerald_26"], use_container_width=True)
        with c2:
            st.link_button("📖 Ler preview oficial — Vol. 29", LINKS_OFICIAIS["viz_emerald_29"], use_container_width=True)


# ============================================================
# 📺 ANIME
# ============================================================

with tab_anime:
    render_capa_midia(
        "📺",
        "Central do Anime",
        "Séries principais, regiões, personagens e atalhos para distribuição oficial.",
    )

    escolha_anime = st.selectbox(
        "📺 Escolha uma série",
        list(ANIME_SERIES.keys()),
        key="midia_anime_escolhido",
    )
    dados = ANIME_SERIES[escolha_anime]

    a1, a2, a3 = st.columns(3)
    with a1:
        st.metric("Tipo", dados["tipo"])
    with a2:
        st.metric("Região / cenário", dados["regioes"])
    with a3:
        st.metric("Era", dados["era"])

    st.write(dados["descricao"])

    st.markdown("### 👥 Personagens em destaque")
    st.write(" • ".join(dados["personagens"]))

    st.divider()
    st.markdown("### 🔗 Onde acompanhar oficialmente")
    st.link_button(dados["fonte"][0], dados["fonte"][1], use_container_width=True)

    if escolha_anime == "Pokémon — Série Original":
        st.divider()
        st.markdown("### ▶️ Episódio oficial em destaque")
        st.caption("Exemplo de episódio completo disponibilizado pelo canal oficial Pokémon TV no YouTube.")
        try:
            st.video(LINKS_OFICIAIS["youtube_ep1"])
        except Exception:
            st.link_button("▶️ Abrir episódio oficial", LINKS_OFICIAIS["youtube_ep1"], use_container_width=True)

    if escolha_anime == "Pokémon: Horizontes":
        st.divider()
        st.markdown("### 📑 Guia oficial de episódios")
        st.link_button(
            "📺 Abrir enciclopédia oficial de episódios",
            LINKS_OFICIAIS["pokemon_horizons_episodios"],
            use_container_width=True,
        )
        st.caption(
            "O guia oficial apresenta títulos e episódios por temporada e também reúne informações sobre a série."
        )

    botao_progresso(chave_progresso("anime", escolha_anime, "Série concluída"), "🏆 Marcar série como concluída")


# ============================================================
# 🎬 FILMES & ESPECIAIS
# ============================================================

with tab_filmes:
    render_capa_midia(
        "🎬",
        "Filmes & Especiais",
        "Catálogo histórico, ordem de lançamento e especiais de animação.",
    )

    subtabs = st.tabs(["🎞️ Filmes animados", "🕵️ Live-action", "⭐ Especiais"])

    with subtabs[0]:
        busca = st.text_input("🔍 Filtrar filmes", key="midia_busca_filmes")
        filmes_filtrados = [x for x in FILMES if not busca or busca.lower() in " ".join(map(str, x)).lower()]
        st.caption(f"{len(filmes_filtrados)} filmes encontrados")
        for titulo, ano, destaque in filmes_filtrados:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"**{ano} — {titulo}**")
                    st.caption(f"⭐ Destaque: {destaque}")
                with c2:
                    botao_progresso(chave_progresso("filme", "Filmes animados", titulo))

    with subtabs[1]:
        for titulo, ano, destaque in FILMES_LIVE_ACTION:
            with st.container(border=True):
                st.markdown(f"**{ano} — {titulo}**")
                st.caption(f"⭐ Destaque: {destaque}")
                botao_progresso(chave_progresso("filme", "Live-action", titulo))

    with subtabs[2]:
        for nome, dados_especial in ESPECIAIS_ANIMADOS.items():
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"**{nome}**")
                    st.caption(
                        f"🎞️ {dados_especial['tipo']} · 🌎 {dados_especial['regiao']} · {dados_especial['descricao']}"
                    )
                with c2:
                    botao_progresso(chave_progresso("especial", "Especiais", nome))

    st.divider()
    st.link_button("🌐 Visitar Pokémon.com", LINKS_OFICIAIS["pokemon"], use_container_width=True)


# ============================================================
# 🎞️ CURTAS / POKÉTOON
# ============================================================

with tab_curta:
    render_capa_midia(
        "🎞️",
        "Curtas Pokémon",
        "POKÉTOON e outras animações curtas: histórias menores, estilos diferentes e muita criatividade.",
    )

    st.markdown("### 📺 POKÉTOON — destaques recentes")
    for titulo, descricao in POKETOON_2026:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"**{titulo}**")
                st.caption(descricao)
            with c2:
                botao_progresso(chave_progresso("poketoon", "POKÉTOON", titulo))

    st.divider()
    st.markdown("### 🔗 Canal oficial")
    st.link_button("▶️ Pokémon no YouTube", LINKS_OFICIAIS["youtube_pokemon"], use_container_width=True)

    st.caption(
        "A Pokémon Company vem disponibilizando POKÉTOON no canal oficial; a disponibilidade dos vídeos pode variar por região e período."
    )


# ============================================================
# 🏆 PROGRESSO
# ============================================================

with tab_progresso:
    render_capa_midia(
        "🏆",
        "Meu Progresso Pokémon",
        "Marque o que você já leu ou assistiu. O progresso fica salvo durante a sessão do site.",
    )

    progresso = st.session_state.midia_progresso

    if not progresso:
        st.info("Você ainda não marcou nenhum conteúdo. Comece explorando Mangá, Anime, Filmes ou Curtas.")
    else:
        st.metric("Itens concluídos nesta sessão", len(progresso))
        for item in sorted(progresso):
            tipo, nome, item_nome = item.split("|", 2)
            st.write(f"✅ **{tipo.title()}** — {nome} → {item_nome}")

        st.divider()
        if st.button("🗑️ Limpar meu progresso da sessão", use_container_width=True):
            st.session_state.midia_progresso = set()
            st.rerun()


# ============================================================
# ℹ️ SOBRE
# ============================================================

with tab_sobre:
    render_capa_midia(
        "⚡",
        "KAYZAC MEDIA",
        "Uma camada de mídia para complementar a Pokédex, as Regiões, Personagens, Times e a Biblioteca.",
    )

    st.markdown("### 🎯 Objetivo")
    st.write(
        "A proposta é tornar o KAYZAC mais abrangente: o usuário pode descobrir uma obra, conhecer sua região, "
        "relacionar personagens e Pokémon e então seguir para a fonte oficial para ler ou assistir."
    )

    st.markdown("### 📚 Mangá")
    st.write(
        "Quando uma editora ou plataforma disponibiliza um preview oficial, o KAYZAC oferece um atalho para esse preview. "
        "As páginas completas de obras protegidas não são copiadas para o projeto."
    )

    st.markdown("### 📺 Anime")
    st.write(
        "A página prioriza players e páginas oficiais. O Pokémon TV como aplicativo foi encerrado em 2024; a própria Pokémon "
        "informa que conteúdos continuam sendo distribuídos por outras plataformas oficiais."
    )

    st.markdown("### 🌐 Idiomas")
    st.selectbox(
        "🌐 Idioma da interface / pesquisa",
        ["🇧🇷 Português", "🇺🇸 English", "🇯🇵 日本語", "🇪🇸 Español", "🇫🇷 Français"],
        key="midia_idioma",
    )
    st.caption(
        "O idioma selecionado organiza a interface e futuras integrações. A disponibilidade de áudio, legenda, tradução ou edição "
        "oficial depende da obra e da região."
    )

    st.markdown("### 🔗 Fontes principais")
    st.link_button("🌐 Pokémon", LINKS_OFICIAIS["pokemon"], use_container_width=True)
    st.link_button("▶️ Pokémon no YouTube", LINKS_OFICIAIS["youtube_pokemon"], use_container_width=True)
    st.link_button("📖 VIZ", LINKS_OFICIAIS["viz"], use_container_width=True)
    st.link_button("📺 Pokémon: Horizontes", LINKS_OFICIAIS["pokemon_horizons"], use_container_width=True)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "⚡ KAYZAC - MASTER POKEMON · KAYZAC MEDIA · Conteúdo e marcas de Pokémon pertencem aos seus respectivos detentores."
)
