import json
import math
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Kayzac - Ranking Pokémon",
    page_icon="🏆",
    layout="wide"
)

API_BASE = "https://pokeapi.co/api/v2/"
BASE_DIR = Path(__file__).resolve().parent.parent
FORMAS_JSON = BASE_DIR / "formas_pokemon.json"
CACHE_RANKING = BASE_DIR / "kayzac_ranking_cache.json"

POKEAPI_CSV_BASE = (
    "https://raw.githubusercontent.com/"
    "PokeAPI/pokeapi/master/data/v2/csv/"
)

STAT_KEYS = [
    "hp",
    "attack",
    "defense",
    "special-attack",
    "special-defense",
    "speed",
]

STAT_LABELS = {
    "hp": "❤️ HP",
    "attack": "⚔️ Ataque",
    "defense": "🛡️ Defesa",
    "special-attack": "✨ Ataque Especial",
    "special-defense": "🔰 Defesa Especial",
    "speed": "💨 Velocidade",
    "base_total": "📊 Total de Status",
}

TRADUCAO_NATUREZAS = {
    "Hardy": "Hardy",
    "Lonely": "Lonely",
    "Adamant": "Adamant",
    "Naughty": "Naughty",
    "Brave": "Brave",
    "Bold": "Bold",
    "Docile": "Docile",
    "Impish": "Impish",
    "Lax": "Lax",
    "Relaxed": "Relaxed",
    "Modest": "Modest",
    "Mild": "Mild",
    "Bashful": "Bashful",
    "Rash": "Rash",
    "Quiet": "Quiet",
    "Calm": "Calm",
    "Gentle": "Gentle",
    "Careful": "Careful",
    "Quirky": "Quirky",
    "Sassy": "Sassy",
    "Timid": "Timid",
    "Hasty": "Hasty",
    "Jolly": "Jolly",
    "Naive": "Naive",
}

# Nature: (status aumentado, status reduzido)
NATURES = {
    "Hardy": (None, None),
    "Lonely": ("attack", "defense"),
    "Adamant": ("attack", "special-attack"),
    "Naughty": ("attack", "special-defense"),
    "Brave": ("attack", "speed"),
    "Bold": ("defense", "attack"),
    "Docile": (None, None),
    "Impish": ("defense", "special-attack"),
    "Lax": ("defense", "special-defense"),
    "Relaxed": ("defense", "speed"),
    "Modest": ("special-attack", "attack"),
    "Mild": ("special-attack", "defense"),
    "Bashful": (None, None),
    "Rash": ("special-attack", "special-defense"),
    "Quiet": ("special-attack", "speed"),
    "Calm": ("special-defense", "attack"),
    "Gentle": ("special-defense", "defense"),
    "Careful": ("special-defense", "special-attack"),
    "Quirky": (None, None),
    "Sassy": ("special-defense", "speed"),
    "Timid": ("speed", "attack"),
    "Hasty": ("speed", "defense"),
    "Jolly": ("speed", "special-attack"),
    "Naive": ("speed", "special-defense"),
}

STAT_ID_MAP = {
    1: "hp",
    2: "attack",
    3: "defense",
    4: "special-attack",
    5: "special-defense",
    6: "speed",
}

FORM_CATEGORIES = [
    ("mega_evolucoes", "💥 Mega Evolução"),
    ("mega_evolucoes_z", "🔵 Mega Evolução Z"),
    ("gigantamax", "🏰 Gigantamax"),
    ("formas_regionais", "🌎 Forma Regional"),
    ("transformacoes", "🌀 Transformação"),
    ("variantes", "🔄 Variante"),
    ("fusoes", "🔗 Fusão"),
    ("formas_especiais", "⭐ Forma Especial"),
    ("formas_alternativas", "🔁 Forma Alternativa"),
    ("formas", "✨ Forma"),
]

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def normalizar_nome(nome):
    return (
        str(nome)
        .strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def nome_bonito(nome):
    partes = str(nome).replace("_", "-").split("-")
    especiais = {
        "alola": "Alola",
        "alolan": "Alolan",
        "galar": "Galar",
        "galarian": "Galarian",
        "hisui": "Hisui",
        "hisuian": "Hisuian",
        "paldea": "Paldea",
        "paldean": "Paldean",
        "mega": "Mega",
        "gigantamax": "Gigantamax",
        "gmax": "G-Max",
        "tera": "Tera",
        "ash": "Ash",
        "school": "School",
        "solo": "Solo",
    }

    resultado = []
    for parte in partes:
        if parte in especiais:
            resultado.append(especiais[parte])
        else:
            resultado.append(parte.capitalize())

    return " ".join(resultado)


# ============================================================
# IMAGENS / FORMAS ESPECIAIS
# ============================================================

# Formas que podem não possuir artwork no mesmo caminho numérico
# usado pelo Pokémon base. Para essas formas consultamos primeiro
# os sprites devolvidos pela própria API e só depois usamos fallbacks.
SPRITES_ESPECIAIS = {
    "zygarde-mega": [
        # Arte encontrada no catálogo atual de Mega Zygarde.
        "https://image.pokemon-wiki.org/images_id/10301__other__official-artwork__front_default.png",
        "https://play.pokemonshowdown.com/sprites/gen9/zygarde-mega.png",
    ],

    # --------------------------------------------------------
    # KORAIDON — FORMAS DE MONTARIA
    # A PokéAPI possui as entradas das formas, mas alguns desses
    # IDs não possuem um artwork PNG utilizável no caminho
    # numérico tradicional. Usamos imagens específicas das formas
    # como fallback.
    # --------------------------------------------------------
    "koraidon-limited-build": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Limited_Build_anime.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Scarlet_Sprinting.png",
    ],
    "koraidon-sprinting-build": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Scarlet_Sprinting.png",
    ],
    "koraidon-swimming-build": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Scarlet_Swimming.png",
    ],
    "koraidon-gliding-build": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Scarlet_Gliding.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Miraidon_glide_anime.png",
    ],

    # --------------------------------------------------------
    # MIRAIDON — FORMAS DE MONTARIA
    # --------------------------------------------------------
    "miraidon-low-power-mode": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Low-Power_Mode_anime.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Low-Power_Mode_Adventures.png",
    ],
    "miraidon-drive-mode": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Violet_Drive.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Drive_Mode_anime.png",
    ],
    "miraidon-aquatic-mode": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Aquatic_Mode_Adventures.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Aquatic_Mode_anime.png",
    ],
    "miraidon-glide-mode": [
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Miraidon_Glide_Mode_Adventures.png",
        "https://archives.bulbagarden.net/wiki/Special:Redirect/file/Koraidon_Miraidon_glide_anime.png",
    ],
}

FORMAS_COM_SPRITE_API = {
    "koraidon-limited-build",
    "koraidon-sprinting-build",
    "koraidon-swimming-build",
    "koraidon-gliding-build",
    "miraidon-low-power-mode",
    "miraidon-drive-mode",
    "miraidon-aquatic-mode",
    "miraidon-glide-mode",
    "zygarde-mega",
}

# Mega Zygarde pode ainda não existir como recurso /pokemon na API em
# instalações que utilizam uma versão de dados anterior. Mantemos aqui
# os dados-base para que ele não desapareça do Ranking.
DADOS_ESPECIAIS_RANKING = {
    "zygarde-mega": {
        "id": 718,
        "types": ["dragon", "ground"],
        "hp": 216,
        "attack": 70,
        "defense": 91,
        "special-attack": 216,
        "special-defense": 85,
        "speed": 100,
        "habilidades": ["aura-break"],
        "height": 77,
        "weight": 6100,
    }
}


@st.cache_data(ttl=86400, show_spinner=False)
def baixar_sprite_especial(identificador):
    """Tenta os caminhos de imagem especiais em sequência."""
    candidatos = SPRITES_ESPECIAIS.get(
        normalizar_nome(identificador),
        []
    )

    for url in candidatos:
        try:
            resposta = requests.get(
                url,
                timeout=12,
            )
            resposta.raise_for_status()
            if resposta.content:
                return resposta.content
        except requests.RequestException:
            continue

    return None


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_pokemon_form_api(identificador):
    """Busca uma forma pelo endpoint pokemon-form quando necessário."""
    try:
        resposta = requests.get(
            f"{API_BASE}pokemon-form/{normalizar_nome(identificador)}",
            timeout=15,
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def obter_sprite_api(identificador):
    """Obtém o melhor sprite disponível diretamente da PokéAPI."""
    nome = normalizar_nome(identificador)
    dados = buscar_pokemon_api(nome)

    candidatos = []

    if dados:
        sprites = dados.get("sprites", {}) or {}
        outros = sprites.get("other", {}) or {}

        candidatos.extend([
            (outros.get("official-artwork", {}) or {}).get("front_default"),
            (outros.get("home", {}) or {}).get("front_default"),
            (outros.get("showdown", {}) or {}).get("front_default"),
            sprites.get("front_default"),
        ])

    if not any(candidatos):
        dados_forma = buscar_pokemon_form_api(nome)

        if dados_forma:
            sprites = dados_forma.get("sprites", {}) or {}
            candidatos.extend([
                sprites.get("front_default"),
                sprites.get("front_shiny"),
            ])

    for candidato in candidatos:
        if candidato:
            return candidato

    return None


def sprite_urls_numericos(pokemon_id):
    try:
        numero = int(pokemon_id)
    except (TypeError, ValueError):
        return []

    return [
        (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            "sprites/pokemon/other/official-artwork/"
            f"{numero}.png"
        ),
        (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            "sprites/pokemon/other/home/"
            f"{numero}.png"
        ),
        (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            "sprites/pokemon/"
            f"{numero}.png"
        ),
    ]


def mostrar_imagem_linha(linha, width=None):
    identificador = normalizar_nome(
        linha.get("identifier", "")
    )

    # Para as formas de montaria de Koraidon/Miraidon, usamos primeiro
    # os fallbacks específicos, pois alguns registros da API não retornam
    # um sprite visual utilizável.
    if identificador in SPRITES_ESPECIAIS:
        imagem_especial = baixar_sprite_especial(identificador)
        if imagem_especial:
            kwargs = {"use_container_width": True}
            if width is not None:
                kwargs = {"width": width}
            st.image(imagem_especial, **kwargs)
            return True

    # Depois tentamos o sprite devolvido pela PokéAPI.
    if (
        identificador in FORMAS_COM_SPRITE_API
        or not bool(linha.get("is_default", True))
    ):
        sprite_api = obter_sprite_api(identificador)
        if sprite_api:
            kwargs = {"use_container_width": True}
            if width is not None:
                kwargs = {"width": width}
            st.image(sprite_api, **kwargs)
            return True

    # Fallback adicional para formas sem artwork na API.
    imagem_especial = baixar_sprite_especial(identificador)
    if imagem_especial:
        kwargs = {"use_container_width": True}
        if width is not None:
            kwargs = {"width": width}
        st.image(imagem_especial, **kwargs)
        return True

    # Fallback numérico para o restante dos Pokémon.
    for sprite in sprite_urls_numericos(linha.get("id")):
        # O front da forma pode ser diferente do artwork oficial;
        # mantemos o primeiro caminho como prioridade visual.
        kwargs = {"use_container_width": True}
        if width is not None:
            kwargs = {"width": width}
        st.image(sprite, **kwargs)
        return True

    return False


def inferir_categoria_pokeapi(row):
    nome = normalizar_nome(row.get("identifier", ""))

    if bool(row.get("is_default", True)):
        return "⭐ Pokémon Base"

    if bool(row.get("is_mega", False)) or "mega" in nome:
        return "💥 Mega Evolução"

    if "gigantamax" in nome or "-gmax" in nome:
        return "🏰 Gigantamax"

    if any(
        termo in nome
        for termo in [
            "alola",
            "alolan",
            "galar",
            "galarian",
            "hisui",
            "hisuian",
            "paldea",
            "paldean",
        ]
    ):
        return "🌎 Forma Regional"

    if bool(row.get("is_battle_only", False)):
        return "🌀 Transformação"

    if "-fusion" in nome or "fused" in nome:
        return "🔗 Fusão"

    return "🔄 Variante / Forma"


# ============================================================
# DOWNLOAD DOS CSVs DA POKÉAPI
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def baixar_csv(nome_arquivo):
    url = POKEAPI_CSV_BASE + nome_arquivo

    resposta = requests.get(
        url,
        timeout=30
    )

    resposta.raise_for_status()

    return pd.read_csv(
        StringIO(resposta.text)
    )


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_pokemon_api(identificador):
    try:
        resposta = requests.get(
            f"{API_BASE}pokemon/{normalizar_nome(identificador)}",
            timeout=15
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None


# ============================================================
# FORMAS PERSONALIZADAS DO KAYZAC
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def carregar_mapa_formas_kayzac():
    if not FORMAS_JSON.exists():
        return {}

    try:
        with open(
            FORMAS_JSON,
            "r",
            encoding="utf-8"
        ) as arquivo:
            formas = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return {}

    mapa = {}

    for especie, dados in formas.items():
        if not isinstance(dados, dict):
            continue

        for chave, titulo in FORM_CATEGORIES:
            lista = dados.get(chave, [])
            if not isinstance(lista, list):
                continue

            for forma in lista:
                if not isinstance(forma, dict):
                    continue

                id_api = forma.get("id_api")
                if not id_api:
                    continue

                chave_api = normalizar_nome(id_api)

                mapa[chave_api] = {
                    "nome": forma.get(
                        "nome",
                        nome_bonito(id_api)
                    ),
                    "categoria": titulo,
                    "regiao": forma.get("regiao"),
                    "origem": forma.get("origem"),
                    "especie": especie,
                }

    return mapa


@st.cache_data(ttl=86400, show_spinner=False)
def carregar_dados_ranking():
    """
    Carrega os dados principais diretamente dos CSVs da PokéAPI.

    Isso evita fazer uma requisição individual para cada Pokémon.
    """

    pokemon = baixar_csv("pokemon.csv")
    stats = baixar_csv("pokemon_stats.csv")
    abilities = baixar_csv("pokemon_abilities.csv")
    abilities_catalogo = baixar_csv("abilities.csv")
    forms = baixar_csv("pokemon_forms.csv")

    # --------------------------------------------------------
    # Pokémon + informações de formas
    # --------------------------------------------------------

    pokemon = pokemon.copy()
    forms = forms.copy()

    forms_cols = [
        "pokemon_id",
        "is_default",
        "is_battle_only",
        "is_mega",
    ]

    forms_disponiveis = [
        coluna
        for coluna in forms_cols
        if coluna in forms.columns
    ]

    forms = forms[forms_disponiveis].drop_duplicates(
        subset=["pokemon_id"]
    )

    pokemon = pokemon.merge(
        forms,
        left_on="id",
        right_on="pokemon_id",
        how="left",
        suffixes=("", "_form")
    )

    pokemon["is_default"] = pokemon[
        "is_default"
    ].fillna(True).astype(bool)

    pokemon["is_battle_only"] = pokemon[
        "is_battle_only"
    ].fillna(False).astype(bool)

    pokemon["is_mega"] = pokemon[
        "is_mega"
    ].fillna(False).astype(bool)

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    stats = stats.copy()
    stats["stat_key"] = stats["stat_id"].map(STAT_ID_MAP)
    stats = stats[stats["stat_key"].notna()].copy()

    stats_pivot = stats.pivot_table(
        index="pokemon_id",
        columns="stat_key",
        values="base_stat",
        aggfunc="first"
    ).reset_index()

    for stat in STAT_KEYS:
        if stat not in stats_pivot.columns:
            stats_pivot[stat] = 0

    pokemon = pokemon.merge(
        stats_pivot,
        left_on="id",
        right_on="pokemon_id",
        how="left",
        suffixes=("", "_stats")
    )

    for stat in STAT_KEYS:
        pokemon[stat] = pokemon[stat].fillna(0).astype(int)

    pokemon["base_total"] = pokemon[STAT_KEYS].sum(axis=1)

    # --------------------------------------------------------
    # HABILIDADES
    # --------------------------------------------------------

    abilities = abilities.copy()
    abilities_catalogo = abilities_catalogo.copy()

    abilities_catalogo = abilities_catalogo[
        ["id", "identifier"]
    ].rename(
        columns={
            "id": "ability_id",
            "identifier": "ability_name",
        }
    )

    abilities = abilities.merge(
        abilities_catalogo,
        left_on="ability_id",
        right_on="ability_id",
        how="left"
    )

    habilidades_por_pokemon = (
        abilities
        .dropna(subset=["ability_name"])
        .sort_values(["pokemon_id", "slot"])
        .groupby("pokemon_id")
        .agg(
            habilidades=(
                "ability_name",
                lambda valores: list(dict.fromkeys(valores))
            )
        )
        .reset_index()
    )

    pokemon = pokemon.merge(
        habilidades_por_pokemon,
        left_on="id",
        right_on="pokemon_id",
        how="left"
    )

    pokemon["habilidades"] = pokemon["habilidades"].apply(
        lambda valor: valor if isinstance(valor, list) else []
    )

    # --------------------------------------------------------
    # CATEGORIA DA FORMA
    # --------------------------------------------------------

    pokemon["categoria_forma"] = pokemon.apply(
        inferir_categoria_pokeapi,
        axis=1
    )

    # Colunas finais
    colunas_finais = [
        "id",
        "identifier",
        "base_total",
        *STAT_KEYS,
        "habilidades",
        "categoria_forma",
        "is_default",
        "is_battle_only",
        "is_mega",
    ]

    pokemon = pokemon[colunas_finais].copy()

    # Ordenação inicial pelo total base.
    pokemon = pokemon.sort_values(
        ["base_total", "identifier"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return pokemon


# ============================================================
# FORMAS PERSONALIZADAS / IDs QUE NÃO ESTÃO NO CSV
# ============================================================


def adicionar_formas_kayzac(pokemon):
    mapa_formas = carregar_mapa_formas_kayzac()

    if not mapa_formas:
        return pokemon

    existentes = set(
        pokemon["identifier"].astype(str).map(normalizar_nome)
    )

    novos = []

    faltantes = [
        id_api
        for id_api in mapa_formas
        if id_api not in existentes
    ]

    if faltantes:
        with st.spinner(
            f"🔮 Carregando {len(faltantes)} forma(s) especial(is) do KAYZAC..."
        ):
            for id_api in faltantes:
                dados = buscar_pokemon_api(id_api)

                # Fallback manual para formas que ainda não são retornadas
                # como um recurso /pokemon pela versão de dados utilizada.
                dados_manual = DADOS_ESPECIAIS_RANKING.get(
                    normalizar_nome(id_api)
                )

                if not dados and not dados_manual:
                    continue

                if dados_manual and not dados:
                    novos.append({
                        "id": dados_manual.get("id"),
                        "identifier": id_api,
                        "base_total": sum(
                            int(dados_manual.get(stat, 0))
                            for stat in STAT_KEYS
                        ),
                        "hp": int(dados_manual.get("hp", 0)),
                        "attack": int(dados_manual.get("attack", 0)),
                        "defense": int(dados_manual.get("defense", 0)),
                        "special-attack": int(
                            dados_manual.get("special-attack", 0)
                        ),
                        "special-defense": int(
                            dados_manual.get("special-defense", 0)
                        ),
                        "speed": int(dados_manual.get("speed", 0)),
                        "habilidades": list(
                            dados_manual.get("habilidades", [])
                        ),
                        "categoria_forma": "💥 Mega Evolução",
                        "is_default": False,
                        "is_battle_only": False,
                        "is_mega": True,
                    })
                    continue

                stats = {
                    stat["stat"]["name"]: stat.get(
                        "base_stat",
                        0
                    )
                    for stat in dados.get("stats", [])
                }

                habilidades = []
                for habilidade in dados.get("abilities", []):
                    nome = (
                        habilidade
                        .get("ability", {})
                        .get("name")
                    )
                    if nome:
                        habilidades.append(nome)

                novos.append({
                    "id": dados.get("id"),
                    "identifier": dados.get("name", id_api),
                    "base_total": sum(
                        int(stats.get(stat, 0))
                        for stat in STAT_KEYS
                    ),
                    "hp": int(stats.get("hp", 0)),
                    "attack": int(stats.get("attack", 0)),
                    "defense": int(stats.get("defense", 0)),
                    "special-attack": int(
                        stats.get("special-attack", 0)
                    ),
                    "special-defense": int(
                        stats.get("special-defense", 0)
                    ),
                    "speed": int(stats.get("speed", 0)),
                    "habilidades": habilidades,
                    "categoria_forma": "✨ Forma Especial",
                    "is_default": False,
                    "is_battle_only": False,
                    "is_mega": False,
                })

    if novos:
        pokemon = pd.concat(
            [pokemon, pd.DataFrame(novos)],
            ignore_index=True
        )

    # --------------------------------------------------------
    # Sobrescreve nomes/categorias pelas informações do JSON
    # --------------------------------------------------------

    for indice, linha in pokemon.iterrows():
        chave = normalizar_nome(linha["identifier"])
        custom = mapa_formas.get(chave)

        if custom:
            pokemon.at[indice, "categoria_forma"] = custom[
                "categoria"
            ]

            # O nome do JSON é melhor para formas autorais.
            pokemon.at[indice, "nome_customizado"] = custom[
                "nome"
            ]
        else:
            pokemon.at[indice, "nome_customizado"] = ""

    pokemon["nome_exibicao"] = pokemon.apply(
        lambda linha: (
            linha["nome_customizado"]
            if str(linha.get("nome_customizado", "")).strip()
            else nome_bonito(linha["identifier"])
        ),
        axis=1
    )

    return pokemon


# ============================================================
# RANKINGS
# ============================================================


def aplicar_natureza_base(row, aumento, reducao):
    """
    Índice simplificado usando os Base Stats.

    A natureza aumenta um status em 10% e reduz outro em 10%.
    HP não é afetado.

    Isso NÃO é o stat final de uma build; IVs, EVs e nível não entram.
    """

    total = 0.0

    for stat in STAT_KEYS:
        valor = float(row.get(stat, 0))

        if stat == aumento:
            valor *= 1.10
        elif stat == reducao:
            valor *= 0.90

        total += valor

    return round(total, 2)


def preparar_ranking_status(pokemon, stat):
    ranking = pokemon.copy()
    ranking = ranking.sort_values(
        [stat, "base_total", "identifier"],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1)
    )

    return ranking


def preparar_ranking_geral(pokemon):
    ranking = pokemon.sort_values(
        ["base_total", "identifier"],
        ascending=[False, True]
    ).reset_index(drop=True)

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1)
    )

    return ranking


def preparar_ranking_natureza(pokemon, natureza):
    aumento, reducao = NATURES[natureza]

    ranking = pokemon.copy()

    ranking["nature_total"] = ranking.apply(
        aplicar_natureza_base,
        axis=1,
        aumento=aumento,
        reducao=reducao
    )

    ranking = ranking.sort_values(
        ["nature_total", "base_total", "identifier"],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1)
    )

    return ranking


def preparar_ranking_habilidade(pokemon, habilidade):
    nome = normalizar_nome(habilidade)

    ranking = pokemon[
        pokemon["habilidades"].apply(
            lambda lista: nome in {
                normalizar_nome(item)
                for item in lista
            }
        )
    ].copy()

    ranking = ranking.sort_values(
        ["base_total", "identifier"],
        ascending=[False, True]
    ).reset_index(drop=True)

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1)
    )

    return ranking


# ============================================================
# VISUAL
# ============================================================


def mostrar_cards(
    ranking,
    coluna_valor,
    quantidade=100,
    rotulo_valor=None,
    chave_paginacao="ranking",
):
    """Mostra os resultados em páginas de 20 cards, sem limitar o Top 100."""
    if ranking.empty:
        st.info("🔎 Nenhum Pokémon foi encontrado neste ranking.")
        return

    rotulo_valor = rotulo_valor or coluna_valor
    mostrar = ranking.head(quantidade).reset_index(drop=True)

    por_pagina = 20
    total_paginas = max(1, math.ceil(len(mostrar) / por_pagina))

    chave_pagina = f"{chave_paginacao}_pagina"

    pagina_atual = int(
        st.session_state.get(
            chave_pagina,
            1
        )
    )

    if pagina_atual > total_paginas:
        pagina_atual = 1
        st.session_state[chave_pagina] = 1

    pagina = st.number_input(
        "📄 Página dos cards",
        min_value=1,
        max_value=total_paginas,
        value=pagina_atual,
        step=1,
        key=chave_pagina,
    )

    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    pagina_itens = mostrar.iloc[inicio:fim]

    st.caption(
        f"Mostrando {inicio + 1}–{min(fim, len(mostrar))} de {len(mostrar)} "
        f"resultado(s) • 20 por página."
    )

    colunas = st.columns(5)

    for indice, (_, linha) in enumerate(pagina_itens.iterrows()):
        with colunas[indice % 5]:
            with st.container(border=True):
                mostrar_imagem_linha(linha)

                st.markdown(
                    f"### #{int(linha['rank'])}"
                )

                st.markdown(
                    f"**{linha['nome_exibicao']}**"
                )

                st.metric(
                    rotulo_valor,
                    f"{linha[coluna_valor]:g}"
                )

                st.caption(
                    f"📊 BST: {int(linha['base_total'])}"
                )

                st.caption(
                    linha["categoria_forma"]
                )

                if st.button(
                    "📖 Mini-Dex",
                    key=(
                        f"mini_dex_{chave_paginacao}_"
                        f"{normalizar_nome(linha['identifier'])}_"
                        f"{int(linha['rank'])}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state["ranking_mini_dex"] = (
                        normalizar_nome(linha["identifier"])
                    )
                    st.session_state["ranking_mini_dex_nome"] = (
                        linha["nome_exibicao"]
                    )
                    st.rerun()


def mostrar_mini_dex(dados):
    identificador = st.session_state.get("ranking_mini_dex")

    if not identificador:
        return

    dados_linha = dados[
        dados["identifier"].apply(normalizar_nome)
        == identificador
    ]

    if dados_linha.empty:
        st.session_state.pop("ranking_mini_dex", None)
        return

    linha = dados_linha.iloc[0]

    st.divider()
    st.header(
        f"📖 Mini-Dex • {linha['nome_exibicao']}"
    )

    if st.button(
        "✖️ Fechar Mini-Dex",
        key="fechar_ranking_mini_dex",
    ):
        st.session_state.pop("ranking_mini_dex", None)
        st.session_state.pop("ranking_mini_dex_nome", None)
        st.rerun()

    dados_api = buscar_pokemon_api(identificador)
    dados_manual = DADOS_ESPECIAIS_RANKING.get(identificador, {})

    col1, col2, col3 = st.columns([1, 1.5, 2])

    with col1:
        mostrar_imagem_linha(linha)

    with col2:
        st.subheader(
            f"#{int(linha['id']) if pd.notna(linha['id']) else '—'} "
            f"{linha['nome_exibicao']}"
        )
        st.write(
            f"**Categoria:** {linha['categoria_forma']}"
        )
        st.metric(
            "📊 BST",
            int(linha["base_total"])
        )

        if dados_api:
            tipos = [
                item.get("type", {}).get("name")
                for item in dados_api.get("types", [])
                if item.get("type", {}).get("name")
            ]
            if tipos:
                st.write(
                    "**Tipos:** "
                    + " / ".join(nome_bonito(tipo) for tipo in tipos)
                )

            altura = dados_api.get("height")
            peso = dados_api.get("weight")
            if altura is not None:
                st.write(f"**Altura:** {altura / 10:.1f} m")
            if peso is not None:
                st.write(f"**Peso:** {peso / 10:.1f} kg")
        elif dados_manual:
            tipos = dados_manual.get("types", [])
            if tipos:
                st.write(
                    "**Tipos:** "
                    + " / ".join(nome_bonito(tipo) for tipo in tipos)
                )

            altura = dados_manual.get("height")
            peso = dados_manual.get("weight")
            if altura is not None:
                st.write(f"**Altura:** {altura / 10:.1f} m")
            if peso is not None:
                st.write(f"**Peso:** {peso / 10:.1f} kg")

    with col3:
        st.subheader("📊 Base Stats")
        stats_texto = [
            ("❤️ HP", "hp"),
            ("⚔️ Ataque", "attack"),
            ("🛡️ Defesa", "defense"),
            ("✨ Atq. Esp.", "special-attack"),
            ("🔰 Def. Esp.", "special-defense"),
            ("💨 Velocidade", "speed"),
        ]

        for rotulo, chave in stats_texto:
            valor = int(linha[chave])
            st.write(f"**{rotulo}: {valor}**")
            st.progress(min(valor / 255, 1.0))

    habilidades = linha.get("habilidades", [])

    if dados_api:
        habilidades_api = []
        for habilidade in dados_api.get("abilities", []):
            nome = habilidade.get("ability", {}).get("name")
            if nome:
                habilidades_api.append(nome)
        if habilidades_api:
            habilidades = list(dict.fromkeys(habilidades_api))
    elif dados_manual.get("habilidades"):
        habilidades = list(dados_manual["habilidades"])

    if habilidades:
        st.subheader("🧬 Habilidades")
        st.write(
            ", ".join(nome_bonito(item) for item in habilidades)
        )

    st.caption(
        "Mini-Dex do Ranking: dados de Base Stats, forma, habilidades e informações básicas."
    )


def montar_tabela(ranking, valor_coluna, incluir_habilidades=True):
    tabela = pd.DataFrame({
        "#": ranking["rank"],
        "Pokémon": ranking["nome_exibicao"],
        "Forma / Categoria": ranking["categoria_forma"],
        "Valor": ranking[valor_coluna],
        "BST": ranking["base_total"],
        "HP": ranking["hp"],
        "Ataque": ranking["attack"],
        "Defesa": ranking["defense"],
        "Atq. Esp.": ranking["special-attack"],
        "Def. Esp.": ranking["special-defense"],
        "Velocidade": ranking["speed"],
    })

    if incluir_habilidades:
        tabela["Habilidades"] = ranking["habilidades"].apply(
            lambda lista: ", ".join(
                nome_bonito(item)
                for item in lista
            )
        )

    return tabela


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🏆 KAYZAC - RANKING POKÉMON")
st.write(
    "Descubra quais Pokémon — incluindo variantes e formas com dados próprios — "
    "ocupam as maiores posições em cada categoria."
)

st.info(
    "💡 Aqui, **'mais forte'** significa maior valor nos dados escolhidos. "
    "O ranking não substitui uma análise competitiva completa de golpes, itens, "
    "habilidades, IVs, EVs, nível e matchup."
)

st.divider()

# ============================================================
# CARREGAR DADOS
# ============================================================

if "ranking_carregado" not in st.session_state:
    st.session_state.ranking_carregado = False

if st.button(
    "🚀 Carregar / Atualizar Ranking",
    use_container_width=True,
    type="primary"
):
    st.session_state.ranking_carregado = True
    baixar_csv.clear()
    buscar_pokemon_api.clear()
    buscar_pokemon_form_api.clear()
    obter_sprite_api.clear()
    baixar_sprite_especial.clear()
    carregar_dados_ranking.clear()
    carregar_mapa_formas_kayzac.clear()

if not st.session_state.ranking_carregado:
    st.info(
        "👆 Clique em **Carregar / Atualizar Ranking** para buscar os dados atuais "
        "da PokéAPI."
    )
    st.stop()

try:
    with st.spinner(
        "📥 Montando banco de dados do Ranking..."
    ):
        dados = carregar_dados_ranking()
        dados = adicionar_formas_kayzac(dados)
except Exception as erro:
    st.error(
        "❌ Não foi possível carregar os dados do Ranking."
    )
    st.caption(
        f"Detalhe técnico: {erro}"
    )
    st.info(
        "💡 Verifique sua conexão com a internet e tente atualizar novamente."
    )
    st.stop()

# Garante nome de exibição para todas as linhas.
if "nome_exibicao" not in dados.columns:
    dados["nome_exibicao"] = dados["identifier"].apply(nome_bonito)
else:
    dados["nome_exibicao"] = dados.apply(
        lambda linha: (
            linha["nome_customizado"]
            if "nome_customizado" in dados.columns
            and str(linha.get("nome_customizado", "")).strip()
            else nome_bonito(linha["identifier"])
        ),
        axis=1
    )

# Remove identificadores duplicados.
dados = dados.drop_duplicates(
    subset=["identifier"]
).reset_index(drop=True)

# ============================================================
# RESUMO
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🐾 Registros",
        f"{len(dados):,}".replace(",", ".")
    )

with c2:
    st.metric(
        "🏆 Maior BST",
        int(dados["base_total"].max())
    )

with c3:
    st.metric(
        "⚡ Maior Ataque",
        int(dados["attack"].max())
    )

with c4:
    st.metric(
        "💨 Maior Velocidade",
        int(dados["speed"].max())
    )

st.divider()

# ============================================================
# MINI-DEX SELECIONADA
# ============================================================

mostrar_mini_dex(dados)

# ============================================================
# ABAS
# ============================================================

aba_geral, aba_status, aba_naturezas, aba_habilidades = st.tabs([
    "🏆 Geral",
    "📊 Status",
    "🌿 Naturezas",
    "🧬 Habilidades",
])

# ============================================================
# GERAL
# ============================================================

with aba_geral:
    st.header("🏆 Ranking geral por Base Stats")
    st.write(
        "Aqui o ranking usa a soma dos seis Base Stats — o BST — como critério."
    )

    quantidade = st.slider(
        "Quantidade de posições exibidas",
        min_value=5,
        max_value=100,
        value=100,
        step=5,
        key="ranking_geral_qtd"
    )

    ranking = preparar_ranking_geral(dados)

    mostrar_cards(
        ranking,
        "base_total",
        quantidade=quantidade,
        rotulo_valor="BST",
        chave_paginacao="ranking_geral",
    )

    st.divider()

    st.subheader(
        f"📋 Ranking completo — Top {quantidade}"
    )
    st.caption(
        "Os dados abaixo mostram até 100 Pokémon. Use a paginação acima para navegar pelos cards."
    )

    st.dataframe(
        montar_tabela(
            ranking.head(quantidade),
            "base_total"
        ),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# STATUS
# ============================================================

with aba_status:
    st.header("📊 Ranking por Status")
    st.write(
        "Escolha um status e descubra os Pokémon com os maiores valores Base nesse atributo."
    )

    status_escolhido = st.selectbox(
        "🔎 Qual status você quer ranquear?",
        STAT_KEYS,
        format_func=lambda valor: STAT_LABELS[valor],
        key="ranking_status_escolhido"
    )

    quantidade = st.slider(
        "Quantidade de posições exibidas",
        min_value=5,
        max_value=100,
        value=100,
        step=5,
        key="ranking_status_qtd"
    )

    ranking = preparar_ranking_status(
        dados,
        status_escolhido
    )

    st.subheader(
        f"{STAT_LABELS[status_escolhido]} — maior ➜ menor"
    )

    mostrar_cards(
        ranking,
        status_escolhido,
        quantidade=quantidade,
        rotulo_valor=STAT_LABELS[status_escolhido],
        chave_paginacao="ranking_status",
    )

    st.divider()

    st.caption(
        "Os dados abaixo mostram até 100 Pokémon. Use a paginação acima para navegar pelos cards."
    )

    st.dataframe(
        montar_tabela(
            ranking.head(quantidade),
            status_escolhido
        ),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# NATUREZAS
# ============================================================

with aba_naturezas:
    st.header("🌿 Ranking por Natureza")
    st.write(
        "Escolha uma Natureza. O KAYZAC recalcula um índice baseado nos Base Stats, "
        "aplicando o aumento de 10% e a redução de 10% da Natureza."
    )

    natureza_escolhida = st.selectbox(
        "🌱 Escolha a Natureza",
        list(NATURES.keys()),
        format_func=lambda valor: TRADUCAO_NATUREZAS[valor],
        key="ranking_natureza_escolhida"
    )

    aumento, reducao = NATURES[natureza_escolhida]

    if aumento is None:
        st.info(
            f"🌿 **{natureza_escolhida}** é uma Natureza neutra: "
            "não aumenta nem reduz um dos cinco atributos não-HP."
        )
    else:
        st.info(
            f"📈 Aumenta: **{STAT_LABELS[aumento]}**  •  "
            f"📉 Reduz: **{STAT_LABELS[reducao]}**"
        )

    quantidade = st.slider(
        "Quantidade de posições exibidas",
        min_value=5,
        max_value=100,
        value=100,
        step=5,
        key="ranking_natureza_qtd"
    )

    ranking = preparar_ranking_natureza(
        dados,
        natureza_escolhida
    )

    st.caption(
        "⚠️ Este é um índice comparativo de Base Stats. Ele não calcula o "
        "stat final de uma build de batalha com nível, IVs e EVs."
    )

    mostrar_cards(
        ranking,
        "nature_total",
        quantidade=quantidade,
        rotulo_valor="Índice da Natureza",
        chave_paginacao="ranking_natureza",
    )

    st.divider()

    st.caption(
        "Os dados abaixo mostram até 100 Pokémon. Use a paginação acima para navegar pelos cards."
    )

    st.dataframe(
        montar_tabela(
            ranking.head(quantidade),
            "nature_total"
        ).rename(
            columns={
                "Valor": "Índice da Natureza"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# HABILIDADES
# ============================================================

with aba_habilidades:
    st.header("🧬 Ranking por Habilidade")
    st.write(
        "Escolha uma habilidade. O Ranking mostra os Pokémon que possuem essa habilidade, "
        "do maior BST para o menor."
    )

    habilidades_set = set()

    for lista in dados["habilidades"]:
        for habilidade in lista:
            habilidades_set.add(habilidade)

    habilidades_disponiveis = sorted(
        habilidades_set,
        key=lambda valor: nome_bonito(valor).lower()
    )

    habilidade_escolhida = st.selectbox(
        "🧬 Escolha a habilidade",
        habilidades_disponiveis,
        format_func=nome_bonito,
        key="ranking_habilidade_escolhida"
    )

    quantidade = st.slider(
        "Quantidade de posições exibidas",
        min_value=5,
        max_value=100,
        value=100,
        step=5,
        key="ranking_habilidade_qtd"
    )

    ranking = preparar_ranking_habilidade(
        dados,
        habilidade_escolhida
    )

    st.metric(
        "🐾 Pokémon com esta habilidade",
        len(ranking)
    )

    if ranking.empty:
        st.warning(
            "Nenhum Pokémon possui essa habilidade nos dados carregados."
        )
    else:
        mostrar_cards(
            ranking,
            "base_total",
            quantidade=quantidade,
            rotulo_valor="BST",
            chave_paginacao="ranking_habilidade",
        )

        st.divider()

        st.caption(
            "Os dados abaixo mostram até 100 Pokémon. Use a paginação acima para navegar pelos cards."
        )

        st.dataframe(
            montar_tabela(
                ranking.head(quantidade),
                "base_total"
            ),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "🏆 KAYZAC Master Pokémon • Ranking"
)
st.caption(
    "Dados principais: PokéAPI • Formas personalizadas: formas_pokemon.json"
)
