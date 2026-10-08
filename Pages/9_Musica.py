from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote_plus

import requests
import streamlit as st


# ============================================================
# ⚡ KAYZAC - MASTER POKEMON
# 🎵 KAYZAC MUSIC
# Sons, trilhas, temas e descoberta sonora do universo Pokémon.
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Música Pokémon",
    page_icon="🎵",
    layout="wide",
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "https://pokeapi.co/api/v2"


def carregar_index_pokemon() -> dict[str, str]:
    caminho = BASE_DIR / "pokemon_index.json"
    if not caminho.exists():
        return {}

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, dict):
            return {str(k): str(v) for k, v in dados.items()}
    except (OSError, json.JSONDecodeError):
        pass

    return {}


INDEX_POKEMON = carregar_index_pokemon()


# ============================================================
# LINKS / BUSCAS
# ============================================================

YOUTUBE_POKEMON = "https://www.youtube.com/@Pokemon"
POKEMON_SITE = "https://www.pokemon.com/br/"


def youtube_busca(consulta: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(consulta)}"


def spotify_busca(consulta: str) -> str:
    return f"https://open.spotify.com/search/{quote_plus(consulta)}"


# ============================================================
# CACHE — POKEAPI
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def buscar_pokemon_audio(slug: str) -> dict | None:
    try:
        resposta = requests.get(
            f"{BASE_URL}/pokemon/{slug}",
            timeout=12,
        )
        resposta.raise_for_status()
        return resposta.json()
    except (requests.RequestException, ValueError):
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_lista_pokemon_api() -> list[tuple[str, str]]:
    try:
        resposta = requests.get(
            f"{BASE_URL}/pokemon?limit=1025",
            timeout=15,
        )
        resposta.raise_for_status()
        resultados = resposta.json().get("results", [])
        return [
            (str(item.get("name", "")), str(item.get("name", "")).replace("-", " ").title())
            for item in resultados
            if item.get("name")
        ]
    except (requests.RequestException, ValueError):
        return []


# ============================================================
# CATÁLOGOS AUTORAIS
# ============================================================

GERACOES_MUSICA = {
    "Geração I — Kanto": {
        "jogos": ["Pokémon Red", "Pokémon Blue", "Pokémon Yellow", "FireRed", "LeafGreen"],
        "destaques": [
            "Tema de batalha",
            "Tema de batalha de Líder de Ginásio",
            "Tema da Champion / Campeão",
            "Route 1",
            "Cidades e rotas de Kanto",
        ],
        "busca": "Pokemon Kanto game soundtrack", 
    },
    "Geração II — Johto": {
        "jogos": ["Pokémon Gold", "Silver", "Crystal", "HeartGold", "SoulSilver"],
        "destaques": [
            "Tema de batalha de Johto",
            "Tema de batalha de Líder de Ginásio",
            "Tema da Liga Pokémon",
            "New Bark Town / Pallet Town",
            "Rotas de Johto",
        ],
        "busca": "Pokemon Johto game soundtrack",
    },
    "Geração III — Hoenn": {
        "jogos": ["Pokémon Ruby", "Sapphire", "Emerald", "Omega Ruby", "Alpha Sapphire"],
        "destaques": [
            "Tema de batalha de Hoenn",
            "Team Magma / Team Aqua",
            "Battle Frontier",
            "Rotas de Hoenn",
            "Temas de cidades e mar",
        ],
        "busca": "Pokemon Hoenn game soundtrack",
    },
    "Geração IV — Sinnoh": {
        "jogos": ["Pokémon Diamond", "Pearl", "Platinum", "Brilliant Diamond", "Shining Pearl"],
        "destaques": [
            "Tema de batalha de Sinnoh",
            "Team Galactic",
            "Battle! Champion",
            "Rotas e cidades de Sinnoh",
            "Lugares nevados e montanhosos",
        ],
        "busca": "Pokemon Sinnoh game soundtrack",
    },
    "Geração V — Unova": {
        "jogos": ["Pokémon Black", "White", "Black 2", "White 2"],
        "destaques": [
            "Tema de batalha de Unova",
            "Team Plasma",
            "Temas de cidade",
            "Pokémon Center",
            "Temas de batalha especiais",
        ],
        "busca": "Pokemon Unova game soundtrack",
    },
    "Geração VI — Kalos": {
        "jogos": ["Pokémon X", "Y", "Omega Ruby", "Alpha Sapphire"],
        "destaques": [
            "Tema de batalha de Kalos",
            "Team Flare",
            "Mega Evolution",
            "Lumiose City",
            "Temas da Liga",
        ],
        "busca": "Pokemon Kalos game soundtrack",
    },
    "Geração VII — Alola": {
        "jogos": ["Pokémon Sun", "Moon", "Ultra Sun", "Ultra Moon"],
        "destaques": [
            "Tema de batalha de Alola",
            "Team Skull",
            "Totem Pokémon",
            "Island Challenge",
            "Temas de Ultra Space",
        ],
        "busca": "Pokemon Alola game soundtrack",
    },
    "Geração VIII — Galar": {
        "jogos": ["Pokémon Sword", "Shield", "Brilliant Diamond", "Shining Pearl"],
        "destaques": [
            "Tema de batalha de Galar",
            "Gym Challenge",
            "Dynamax / Max Raid Battles",
            "Wyndon",
            "League Card / Campeão",
        ],
        "busca": "Pokemon Galar game soundtrack",
    },
    "Geração IX — Paldea": {
        "jogos": ["Pokémon Scarlet", "Violet"],
        "destaques": [
            "Tema de batalha de Paldea",
            "Team Star",
            "Tera Raid Battles",
            "Área Zero",
            "Temas de viagem e academia",
        ],
        "busca": "Pokemon Paldea game soundtrack",
    },
    "Hisui / Legends: Arceus": {
        "jogos": ["Pokémon Legends: Arceus"],
        "destaques": [
            "Jubilife Village",
            "Batalhas de Noble Pokémon",
            "Hisui",
            "Área de campo",
            "Conflitos e temas ancestrais",
        ],
        "busca": "Pokemon Legends Arceus soundtrack",
    },
    "Pokémon Z-A": {
        "jogos": ["Pokémon Legends: Z-A"],
        "destaques": [
            "Lumiose City",
            "Ambiente urbano",
            "Mega Evolution",
            "Temas de batalha",
            "Exploração e transformação da cidade",
        ],
        "busca": "Pokemon Legends Z-A soundtrack",
    },
}


TEMAS_MUSICAIS = [
    {
        "nome": "🎮 Batalha Pokémon",
        "descricao": "Para momentos de confronto, pressão e decisões rápidas.",
        "busca": "Pokemon battle music",
        "cor": "🔥",
    },
    {
        "nome": "🏟️ Líder de Ginásio",
        "descricao": "Uma categoria dedicada à tensão e à identidade dos grandes desafios de ginásio.",
        "busca": "Pokemon gym leader battle music",
        "cor": "🏆",
    },
    {
        "nome": "👑 Campeão / Liga",
        "descricao": "Temas ligados às batalhas decisivas e à atmosfera da Liga Pokémon.",
        "busca": "Pokemon champion battle music",
        "cor": "👑",
    },
    {
        "nome": "😈 Equipes Vilãs",
        "descricao": "Músicas associadas a Team Rocket, Magma, Aqua, Galactic, Plasma, Flare, Skull, Star e outras organizações.",
        "busca": "Pokemon villain team music",
        "cor": "🕶️",
    },
    {
        "nome": "🌌 Lendários & Momentos Épicos",
        "descricao": "Uma coleção temática para encontros importantes, criaturas poderosas e grandes momentos da história.",
        "busca": "Pokemon legendary battle music",
        "cor": "✨",
    },
    {
        "nome": "🌿 Rotas & Exploração",
        "descricao": "Temas tranquilos, aventureiros ou contemplativos para viajar pelo mundo Pokémon.",
        "busca": "Pokemon route music",
        "cor": "🌿",
    },
    {
        "nome": "🏙️ Cidades & Lugares",
        "descricao": "Músicas que dão identidade a cidades, vilas, centros Pokémon e locais especiais.",
        "busca": "Pokemon town city music",
        "cor": "🏙️",
    },
    {
        "nome": "🎭 Anime & Performance",
        "descricao": "Temas relacionados ao anime, concursos, performances, aberturas e momentos emocionais.",
        "busca": "Pokemon anime music",
        "cor": "🎤",
    },
]


# ============================================================
# 🎤 MÚSICA GEEK — POKÉMON
# ============================================================

# O KAYZAC não hospeda nem redistribui as faixas.
# Os cards apontam para busca/streaming, priorizando os canais
# e perfis dos próprios artistas.

MUSICA_GEEK_POKEMON = [
    {
        "artista": "Chrono",
        "faixa": "Vilões (Pokémon) - CAMINHO DO PODER",
        "personagens": "Giovanni, Archie, Maxie, Cyrus, N, Ghetsis, Lysandre, Guzma, Lusamine, Piers, Rose e Volo",
        "tipo": "Projeto colaborativo",
        "descricao": "Projeto dedicado aos vilões de várias regiões de Pokémon, reunindo diferentes vozes da cena geek.",
        "busca": "Chrono Vilões Pokémon CAMINHO DO PODER",
        "url_direta": "https://www.youtube.com/watch?v=PRRBJOn_n-Y",
        "destaque": True,
    },
    {
        "artista": "Tauz",
        "faixa": "Rap do Pokemon Go | RapGame 39",
        "personagens": "Pokémon GO / universo Pokémon",
        "tipo": "Solo",
        "descricao": "Um dos lançamentos Pokémon do Tauz, ligado à fase de Pokémon GO e à cena de rap geek da década de 2010.",
        "busca": "Tauz Rap do Pokemon Go RapGame 39",
        "url_direta": "https://www.youtube.com/watch?v=23yJekTt1pc",
        "destaque": True,
    },
    {
        "artista": "TC Thunders",
        "faixa": "Catálogo Pokémon",
        "personagens": "Rayquaza, Arceus e outros Pokémon",
        "tipo": "Catálogo",
        "descricao": "Atalho para descobrir raps Pokémon associados ao artista e projetos relacionados da cena geek.",
        "busca": "TC Thunders Pokémon rap geek",
        "url_direta": None,
        "destaque": False,
    },
    {
        "artista": "M4rkim",
        "faixa": "Catálogo Pokémon",
        "personagens": "Pokémon / personagens da franquia",
        "tipo": "Catálogo / participações",
        "descricao": "Busca dedicada às músicas, participações e colaborações de M4rkim relacionadas a Pokémon.",
        "busca": "M4rkim Pokémon música rap geek",
        "url_direta": None,
        "destaque": False,
    },
    {
        "artista": "AniRap",
        "faixa": "Hypno (Pokémon: Creepypasta) | Sonho",
        "personagens": "Hypno",
        "tipo": "Solo",
        "descricao": "Faixa baseada em Hypno e em sua conhecida creepypasta, com uma abordagem mais sombria.",
        "busca": "AniRap Hypno Pokémon Sonho",
        "url_direta": "https://www.youtube.com/watch?v=nDIbWGJ2zw8",
        "destaque": True,
    },
    {
        "artista": "7 Minutoz",
        "faixa": "Catálogo Pokémon",
        "personagens": "Pokémon / universo geek",
        "tipo": "Catálogo",
        "descricao": "Busca para localizar projetos Pokémon e possíveis colaborações dentro do catálogo do 7 Minutoz.",
        "busca": "7 Minutoz Pokémon rap",
        "url_direta": None,
        "destaque": False,
    },
    {
        "artista": "Enygma",
        "faixa": "Catálogo Pokémon",
        "personagens": "Pokémon / universo geek",
        "tipo": "Catálogo / participações",
        "descricao": "Atalho para pesquisar faixas e participações de Enygma relacionadas à franquia.",
        "busca": "Enygma Pokémon rap geek",
        "url_direta": None,
        "destaque": False,
    },
    {
        "artista": "Cena Geek",
        "faixa": "Colaborações Pokémon",
        "personagens": "Vários Pokémon e treinadores",
        "tipo": "Coletânea de descoberta",
        "descricao": "Uma busca ampla para encontrar collabs, cyphers e projetos Pokémon de artistas diferentes.",
        "busca": "Pokémon rap geek brasileiro cypher collab",
        "url_direta": None,
        "destaque": False,
    },
]


REGIOES_SONORAS = {
    "Kanto": "Pokemon Kanto music",
    "Johto": "Pokemon Johto music",
    "Hoenn": "Pokemon Hoenn music",
    "Sinnoh": "Pokemon Sinnoh music",
    "Hisui": "Pokemon Legends Arceus music",
    "Unova": "Pokemon Unova music",
    "Kalos": "Pokemon Kalos music",
    "Alola": "Pokemon Alola music",
    "Galar": "Pokemon Galar music",
    "Paldea": "Pokemon Paldea music",
    "Lumiose / Z-A": "Pokemon Legends Z-A Lumiose music",
}


# ============================================================
# ESTADO
# ============================================================

if "musica_favoritos" not in st.session_state:
    st.session_state.musica_favoritos = set()

if "musica_historico" not in st.session_state:
    st.session_state.musica_historico = []

if "musica_ultimo_pokemon" not in st.session_state:
    st.session_state.musica_ultimo_pokemon = None


def registrar_escuta(nome: str) -> None:
    historico = st.session_state.musica_historico
    historico = [item for item in historico if item != nome]
    historico.insert(0, nome)
    st.session_state.musica_historico = historico[:10]


def alternar_favorito(nome: str) -> None:
    favoritos = st.session_state.musica_favoritos
    if nome in favoritos:
        favoritos.remove(nome)
    else:
        favoritos.add(nome)


# ============================================================
# UTILITÁRIOS VISUAIS
# ============================================================


def render_capa(emoji: str, titulo: str, subtitulo: str) -> None:
    st.markdown(
        f"""
        <div style="
            border:1px solid rgba(80,170,255,.35);
            border-radius:18px;
            padding:22px;
            margin-bottom:16px;
            background:linear-gradient(135deg, rgba(20,65,110,.16), rgba(20,20,28,.12));
        ">
            <div style="font-size:44px;">{emoji}</div>
            <h2 style="margin:0 0 6px 0;">{titulo}</h2>
            <p style="margin:0; opacity:.82;">{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nome_bonito(slug: str) -> str:
    return (
        slug.replace("-", " ")
        .replace(" form", " Form")
        .title()
        .replace("Mr Mime", "Mr. Mime")
        .replace("Mime Jr", "Mime Jr.")
        .replace("Nidoran F", "Nidoran♀")
        .replace("Nidoran M", "Nidoran♂")
    )


def imagem_principal(dados: dict) -> str | None:
    sprites = dados.get("sprites", {})
    official = sprites.get("other", {}).get("official-artwork", {}).get("front_default")
    showdown = sprites.get("other", {}).get("showdown", {}).get("front_default")
    pixel = sprites.get("front_default")
    return official or showdown or pixel


def mini_pokedex(slug: str, nome: str, chave: str) -> None:
    if st.button(
        "📖 Mini-Dex",
        key=f"minidex_musica_{chave}",
        use_container_width=True,
    ):
        st.session_state["pokemon_focado"] = slug
        st.switch_page("pages/1_Pokedex.py")


def card_musica_geek(item: dict, idx: int) -> None:
    titulo_favorito = f"{item['artista']} · {item['faixa']}"

    with st.container(border=True):
        st.markdown(
            f"### 🎤 {item['artista']} — {item['faixa']}"
        )
        st.caption(
            f"🎭 {item['personagens']} · 🎚️ {item['tipo']}"
        )
        st.write(item['descricao'])

        c1, c2, c3 = st.columns(3)
        with c1:
            if item.get('url_direta') and item['url_direta'] != 'https://www.youtube.com/watch?v=':
                st.link_button(
                    "▶️ Abrir faixa",
                    item['url_direta'],
                    use_container_width=True,
                )
            else:
                st.link_button(
                    "▶️ YouTube",
                    youtube_busca(item['busca']),
                    use_container_width=True,
                )
        with c2:
            st.link_button(
                "🎵 Spotify",
                spotify_busca(item['busca']),
                use_container_width=True,
            )
        with c3:
            favorito = titulo_favorito in st.session_state.musica_favoritos
            texto = "⭐ Remover" if favorito else "☆ Favoritar"
            if st.button(
                texto,
                key=f"fav_geek_{idx}",
                use_container_width=True,
            ):
                alternar_favorito(titulo_favorito)
                st.rerun()


def card_tema(item: dict, idx: int) -> None:
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"### {item['cor']} {item['nome'].split(' ', 1)[1] if ' ' in item['nome'] else item['nome']}")
            st.caption(item["descricao"])
        with col2:
            favorito = item["nome"] in st.session_state.musica_favoritos
            texto = "⭐ Remover" if favorito else "☆ Favoritar"
            if st.button(texto, key=f"fav_tema_{idx}", use_container_width=True):
                alternar_favorito(item["nome"])
                st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            st.link_button(
                "▶️ YouTube",
                youtube_busca(item["busca"]),
                use_container_width=True,
            )
        with c2:
            st.link_button(
                "🎵 Spotify",
                spotify_busca(item["busca"]),
                use_container_width=True,
            )


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🎵 KAYZAC MUSIC")
st.markdown("### 🔊 Sons, trilhas, temas e momentos que dão vida ao universo Pokémon")
st.caption(
    "Uma central sonora feita para complementar a Pokédex, as Regiões, a Mídia, o Quiz e o restante do KAYZAC."
)

st.info(
    "🎧 O KAYZAC não hospeda álbuns completos nem redistribui trilhas protegidas. "
    "A página trabalha com sons disponibilizados pela PokéAPI e com atalhos para plataformas e buscas de música."
)


# ============================================================
# TABS
# ============================================================

tab_sons, tab_trilhas, tab_geek, tab_temas, tab_regioes, tab_meu_som, tab_sobre = st.tabs(
    [
        "🔊 Sons Pokémon",
        "🎮 Trilhas dos Jogos",
        "🎤 Música Geek",
        "🎼 Temas & Climas",
        "🌎 Música por Região",
        "⭐ Meu Som",
        "ℹ️ Sobre",
    ]
)


# ============================================================
# 🔊 SONS POKÉMON
# ============================================================

with tab_sons:
    render_capa(
        "🔊",
        "Pokémon que você quer ouvir",
        "Escolha um Pokémon e reproduza seus cries disponibilizados pela PokéAPI.",
    )

    opcoes_index = list(INDEX_POKEMON.items())
    opcoes_api = [] if opcoes_index else buscar_lista_pokemon_api()

    if opcoes_index:
        mapa_pokemon = {
            slug: nome
            for slug, nome in opcoes_index
            if slug and nome
        }
    else:
        mapa_pokemon = dict(opcoes_api)

    if not mapa_pokemon:
        st.warning(
            "⚠️ Não foi possível carregar a lista local de Pokémon nem a lista da PokéAPI agora. "
            "Verifique sua conexão e tente novamente."
        )
    else:
        lista_slugs = list(mapa_pokemon.keys())
        nomes = [mapa_pokemon[slug] for slug in lista_slugs]

        nome_escolhido = st.selectbox(
            "🔎 Escolha um Pokémon",
            nomes,
            key="musica_pokemon_escolhido",
        )
        indice = nomes.index(nome_escolhido)
        slug_escolhido = lista_slugs[indice]

        dados = buscar_pokemon_audio(slug_escolhido)

        if not dados:
            st.error("❌ Não foi possível carregar os sons deste Pokémon agora.")
        else:
            registrar_escuta(nome_escolhido)
            st.session_state.musica_ultimo_pokemon = slug_escolhido

            c1, c2 = st.columns([1.15, 1.85])
            with c1:
                imagem = imagem_principal(dados)
                if imagem:
                    st.image(imagem, caption=nome_escolhido, use_container_width=True)
                mini_pokedex(slug_escolhido, nome_escolhido, slug_escolhido)

            with c2:
                st.markdown(f"## 🔊 {nome_escolhido}")
                st.caption(f"Slug/API: `{slug_escolhido}`")

                cries = dados.get("cries", {})
                latest = cries.get("latest")
                legacy = cries.get("legacy")

                if latest or legacy:
                    st.markdown("### 🎙️ Cries disponíveis")

                    if latest:
                        st.markdown("**✨ Latest**")
                        st.audio(latest)
                        if st.button(
                            "⭐ Favoritar Latest",
                            key=f"fav_cry_latest_{slug_escolhido}",
                            use_container_width=True,
                        ):
                            alternar_favorito(f"Cry · {nome_escolhido} · Latest")
                            st.rerun()

                    if legacy:
                        st.markdown("**🕹️ Legacy**")
                        st.audio(legacy)
                        if st.button(
                            "⭐ Favoritar Legacy",
                            key=f"fav_cry_legacy_{slug_escolhido}",
                            use_container_width=True,
                        ):
                            alternar_favorito(f"Cry · {nome_escolhido} · Legacy")
                            st.rerun()
                else:
                    st.warning("🔇 Este registro não retornou um cry disponível pela API.")

                st.divider()
                st.markdown("### 🎵 Procurar músicas relacionadas")
                busca_nome = f"Pokemon {nome_escolhido} music"
                b1, b2 = st.columns(2)
                with b1:
                    st.link_button(
                        "▶️ YouTube",
                        youtube_busca(busca_nome),
                        use_container_width=True,
                    )
                with b2:
                    st.link_button(
                        "🎵 Spotify",
                        spotify_busca(busca_nome),
                        use_container_width=True,
                    )

            st.divider()
            st.markdown("### 🧪 Informações rápidas")
            tipos = [item.get("type", {}).get("name", "") for item in dados.get("types", [])]
            habilidades = [item.get("ability", {}).get("name", "") for item in dados.get("abilities", [])]
            a1, a2, a3 = st.columns(3)
            with a1:
                st.metric("Número", f"#{dados.get('id', '?')}")
            with a2:
                st.metric("Tipo", "/".join(tipos).title() if tipos else "—")
            with a3:
                st.metric("Habilidades", str(len(habilidades)))


# ============================================================
# 🎮 TRILHAS DOS JOGOS
# ============================================================

with tab_trilhas:
    render_capa(
        "🎮",
        "Trilhas Sonoras dos Jogos",
        "Explore por geração, jogo e tipo de momento — sem precisar transformar o KAYZAC em um repositório de música protegida.",
    )

    busca_geracao = st.text_input(
        "🔍 Filtrar gerações / jogos",
        key="musica_busca_geracoes",
        placeholder="Ex.: Hoenn, Sinnoh, Galar...",
    )

    geracoes_filtradas = [
        (nome, dados)
        for nome, dados in GERACOES_MUSICA.items()
        if not busca_geracao
        or busca_geracao.lower() in nome.lower()
        or busca_geracao.lower() in " ".join(dados["jogos"]).lower()
    ]

    st.caption(f"{len(geracoes_filtradas)} coleções encontradas")

    for idx, (nome_geracao, dados) in enumerate(geracoes_filtradas):
        with st.container(border=True):
            st.markdown(f"### 🎵 {nome_geracao}")
            st.write("**Jogos:** " + " · ".join(dados["jogos"]))

            with st.expander("🎧 Ver destaques da coleção"):
                for destaque in dados["destaques"]:
                    st.write(f"• {destaque}")

            c1, c2 = st.columns(2)
            with c1:
                st.link_button(
                    "▶️ Pesquisar no YouTube",
                    youtube_busca(dados["busca"]),
                    use_container_width=True,
                )
            with c2:
                st.link_button(
                    "🎵 Pesquisar no Spotify",
                    spotify_busca(dados["busca"]),
                    use_container_width=True,
                )

    st.divider()
    st.markdown("### 🎧 Atalhos gerais")
    x1, x2, x3 = st.columns(3)
    with x1:
        st.link_button("▶️ Canal Pokémon", YOUTUBE_POKEMON, use_container_width=True)
    with x2:
        st.link_button("🎮 Game Music", youtube_busca("Pokemon game music"), use_container_width=True)
    with x3:
        st.link_button("🎼 Pokémon OST", spotify_busca("Pokemon Original Soundtrack"), use_container_width=True)


# ============================================================
# 🎤 MÚSICA GEEK — POKÉMON
# ============================================================

with tab_geek:
    render_capa(
        "🎤",
        "Música Geek Pokémon",
        "Raps, traps, cyphers, covers e projetos da cena geek inspirados em Pokémon.",
    )

    st.info(
        "🎧 Esta área é focada em música feita por fãs/artistas da cena geek. "
        "O KAYZAC não hospeda nem redistribui as faixas: os botões levam ao YouTube, Spotify "
        "ou à busca correspondente para encontrar a publicação do artista."
    )

    busca_geek = st.text_input(
        "🔍 Buscar artista, Pokémon ou faixa",
        key="musica_busca_geek",
        placeholder="Ex.: Lucario, Rayquaza, Chrono, M4rkim...",
    )

    artistas_geek = ["Todos"] + sorted({item["artista"] for item in MUSICA_GEEK_POKEMON})
    filtro_artista = st.selectbox(
        "🎤 Artista",
        artistas_geek,
        key="musica_filtro_artista_geek",
    )

    geek_filtrado = MUSICA_GEEK_POKEMON
    if filtro_artista != "Todos":
        geek_filtrado = [
            item for item in geek_filtrado
            if item["artista"] == filtro_artista
        ]

    if busca_geek:
        termo = busca_geek.lower()
        geek_filtrado = [
            item for item in geek_filtrado
            if termo in " ".join(
                [
                    item["artista"],
                    item["faixa"],
                    item["personagens"],
                    item["tipo"],
                    item["descricao"],
                ]
            ).lower()
        ]

    st.caption(f"{len(geek_filtrado)} item(ns) encontrado(s)")

    for idx, item in enumerate(geek_filtrado):
        card_musica_geek(item, idx)

    st.divider()
    st.markdown("### 🌟 Destaques da cena")
    st.write(
        "A música geek brasileira transformou personagens, histórias, jogos e universos de cultura pop "
        "em faixas autorais. O KAYZAC separa esse conteúdo da trilha oficial de Pokémon para deixar claro "
        "o que é música da própria franquia e o que é produção da comunidade/artistas."
    )

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("**🐲 Personagens & Pokémon**")
        st.caption("Pesquise por um Pokémon específico e descubra faixas inspiradas nele.")
    with d2:
        st.markdown("**🔥 Rap / Trap / Geek**")
        st.caption("Explore diferentes estilos usados pela cena geek ao longo dos anos.")
    with d3:
        st.markdown("**🤝 Collabs**")
        st.caption("Cyphers, teams e participações que juntam vários artistas em um mesmo projeto.")

    st.divider()
    st.markdown("### 🔎 Atalhos de descoberta")
    consultas = [
        "Pokémon rap geek brasileiro",
        "Pokémon trap geek brasileiro",
        "Pokémon cypher rap geek",
        "Lucario rap geek",
        "Rayquaza rap geek",
        "Mewtwo rap geek",
        "Team Rocket rap geek",
    ]
    for idx, consulta in enumerate(consultas):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**🎧 {consulta}**")
            with c2:
                st.link_button(
                    "Ouvir",
                    youtube_busca(consulta),
                    use_container_width=True,
                )


# ============================================================
# 🎼 TEMAS & CLIMAS
# ============================================================

with tab_temas:
    render_capa(
        "🎼",
        "Temas & Climas",
        "Em vez de organizar apenas por jogo, organize pela sensação que a música transmite.",
    )

    filtro_tema = st.multiselect(
        "🎚️ Filtrar por ambiente",
        [
            "🔥 Ação",
            "🏆 Competição",
            "😈 Vilões",
            "✨ Épico",
            "🌿 Exploração",
            "🏙️ Cidade",
            "🎤 Anime",
        ],
        default=[],
        key="musica_filtros_temas",
    )

    temas = TEMAS_MUSICAIS
    if filtro_tema:
        texto_filtro = " ".join(filtro_tema).lower()
        temas = [
            tema
            for tema in TEMAS_MUSICAIS
            if any(palavra.lower() in tema["nome"].lower() or palavra.lower() in tema["descricao"].lower() for palavra in filtro_tema for palavra in [palavra.split(" ", 1)[-1]])
            or (
                "ação" in texto_filtro and "Batalha" in tema["nome"]
            )
            or (
                "competição" in texto_filtro and ("Ginásio" in tema["nome"] or "Campeão" in tema["nome"])
            )
            or (
                "vilões" in texto_filtro and "Vilãs" in tema["nome"]
            )
            or (
                "épico" in texto_filtro and "Épicos" in tema["nome"]
            )
            or (
                "exploração" in texto_filtro and "Exploração" in tema["nome"]
            )
            or (
                "cidade" in texto_filtro and "Cidades" in tema["nome"]
            )
            or (
                "anime" in texto_filtro and "Anime" in tema["nome"]
            )
        ]

    for idx, item in enumerate(temas):
        card_tema(item, idx)

    st.divider()
    st.markdown("### 🎤 Performance, música e Pokémon")
    st.write(
        "O KAYZAC também pode usar a classificação temática de **Som**, já existente na Biblioteca, "
        "para conectar Pokémon ligados a canto, instrumentos, vibrações, ressonância e performance."
    )
    st.caption(
        "💡 As classificações temáticas de Som podem ser exploradas na Biblioteca Pokémon."
    )


# ============================================================
# 🌎 MÚSICA POR REGIÃO
# ============================================================

with tab_regioes:
    render_capa(
        "🌎",
        "Música por Região",
        "Escolha uma região e descubra rapidamente a atmosfera sonora associada a ela.",
    )

    regiao = st.selectbox(
        "🌎 Região sonora",
        list(REGIOES_SONORAS.keys()),
        key="musica_regiao",
    )

    busca = REGIOES_SONORAS[regiao]

    with st.container(border=True):
        st.markdown(f"## 🎵 {regiao}")
        st.caption("Uma busca temática para explorar trilhas, cidades, batalhas, ambientes e momentos da região.")

        c1, c2 = st.columns(2)
        with c1:
            st.link_button(
                "▶️ YouTube",
                youtube_busca(busca),
                use_container_width=True,
            )
        with c2:
            st.link_button(
                "🎵 Spotify",
                spotify_busca(busca),
                use_container_width=True,
            )

    st.markdown("### 🧭 Ideias para explorar")
    ideias = [
        f"{regiao} — temas de cidades",
        f"{regiao} — temas de rotas",
        f"{regiao} — batalha de Líder de Ginásio",
        f"{regiao} — batalha de Campeão",
        f"{regiao} — Team / organização vilã",
        f"{regiao} — Pokémon Center",
    ]

    for idx, ideia in enumerate(ideias):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{ideia}**")
            with c2:
                st.link_button(
                    "🎧 Ouvir",
                    youtube_busca(ideia),
                    use_container_width=True,
                )


# ============================================================
# ⭐ MEU SOM
# ============================================================

with tab_meu_som:
    render_capa(
        "⭐",
        "Meu Som",
        "Seção pessoal para guardar favoritos e lembrar do que você explorou nesta sessão.",
    )

    favoritos = sorted(st.session_state.musica_favoritos)
    historico = st.session_state.musica_historico

    a1, a2 = st.columns(2)
    with a1:
        st.metric("⭐ Favoritos", len(favoritos))
    with a2:
        st.metric("🕘 Últimos Pokémon ouvidos", len(historico))

    if favoritos:
        st.markdown("### ⭐ Favoritos")
        for item in favoritos:
            with st.container(border=True):
                st.write(f"⭐ **{item}**")
    else:
        st.info("Você ainda não favoritou nenhum tema ou cry.")

    st.divider()
    st.markdown("### 🕘 Histórico recente")
    if historico:
        for item in historico:
            st.write(f"🔊 {item}")
    else:
        st.info("Ainda não há histórico nesta sessão.")

    st.divider()
    if st.button("🗑️ Limpar favoritos e histórico", use_container_width=True):
        st.session_state.musica_favoritos = set()
        st.session_state.musica_historico = []
        st.rerun()


# ============================================================
# ℹ️ SOBRE
# ============================================================

with tab_sobre:
    render_capa(
        "⚡",
        "KAYZAC MUSIC",
        "A camada sonora do universo KAYZAC.",
    )

    st.markdown("### 🎯 O objetivo")
    st.write(
        "A página de Música foi pensada para complementar a experiência do projeto sem substituir plataformas oficiais. "
        "Ela conecta Pokémon, regiões, jogos, temas e sons em uma única área."
    )

    st.markdown("### 🔊 Sons Pokémon")
    st.write(
        "Os cries apresentados na aba de Sons são obtidos da PokéAPI quando o registro do Pokémon disponibiliza os arquivos."
    )

    st.markdown("### 🎼 Trilhas")
    st.write(
        "Para músicas e trilhas completas, o KAYZAC trabalha principalmente com atalhos de descoberta para plataformas como YouTube e Spotify."
    )

    st.markdown("### 🎤 Música Geek Pokémon")
    st.write(
        "A página também reúne atalhos para raps, traps, cyphers e projetos de artistas da cena geek brasileira inspirados em Pokémon, "
        "mantendo esse conteúdo separado das trilhas oficiais da franquia."
    )

    st.markdown("### 🔗 Fontes principais")
    st.link_button("🌐 Pokémon.com", POKEMON_SITE, use_container_width=True)
    st.link_button("▶️ Canal oficial Pokémon", YOUTUBE_POKEMON, use_container_width=True)
    st.link_button("🧬 PokéAPI", BASE_URL, use_container_width=True)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "⚡ KAYZAC - MASTER POKEMON · 🎵 KAYZAC MUSIC · Sons e músicas pertencem aos seus respectivos detentores."
)
