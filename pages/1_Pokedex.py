import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Master Pokémon",
    page_icon="⚡",
    layout="wide"
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_INDEX = BASE_DIR / "pokemon_index.json"
ARQUIVO_CSV = BASE_DIR / "pokemon_1.csv"
ARQUIVO_FORMAS = BASE_DIR / "formas_pokemon.json"
ARQUIVO_HISTORICO = BASE_DIR / "historico_pokemon.json"


# ============================================================
# CABEÇALHO
# ============================================================

st.title("⚡ KAYZAC - MASTER POKEMON ⚡")
st.write("A Pokédex feita por um verdadeiro treinador!")

st.divider()


# ============================================================
# ESTADO DE NAVEGAÇÃO
# ============================================================

if "pokemon_focado" not in st.session_state:

    st.session_state.pokemon_focado = None

if "forma_focada_id" not in st.session_state:

    st.session_state.forma_focada_id = None

if "forma_focada_dados" not in st.session_state:

    st.session_state.forma_focada_dados = None


def navegar_para_pokemon(identificador):
    """
    Abre diretamente um Pokémon ou uma forma na ficha completa.
    """

    if identificador:

        st.session_state.pokemon_focado = (
            normalizar_nome(identificador)
        )

        st.rerun()


def navegar_para_forma(forma, especie_base):
    """Abre a ficha da espécie-base mantendo a forma selecionada."""

    if not isinstance(forma, dict):
        return

    id_api = forma.get("id_api")

    if id_api:

        st.session_state.pokemon_focado = normalizar_nome(especie_base)
        st.session_state.forma_focada_id = normalizar_nome(id_api)
        st.session_state.forma_focada_dados = dict(forma)
        st.rerun()


def voltar_para_pokemon_selecionado():

    st.session_state.pokemon_focado = None
    st.session_state.forma_focada_id = None
    st.session_state.forma_focada_dados = None

    st.rerun()


# ============================================================
# CARREGAR ARQUIVOS
# ============================================================

try:

    with open(
        ARQUIVO_INDEX,
        "r",
        encoding="utf-8"
    ) as arquivo:

        index_pokemons = json.load(
            arquivo
        )

except FileNotFoundError:

    st.error(
        "❌ O arquivo pokemon_index.json não foi encontrado."
    )

    st.stop()


try:

    df = pd.read_csv(
        ARQUIVO_CSV
    )

except FileNotFoundError:

    df = None

    st.sidebar.warning(
        "⚠️ pokemon_1.csv não encontrado."
    )


try:

    with open(
        ARQUIVO_FORMAS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        formas_pokemon = json.load(
            arquivo
        )

except FileNotFoundError:

    formas_pokemon = {}

    st.sidebar.warning(
        "⚠️ formas_pokemon.json não encontrado."
    )


# ============================================================
# HISTÓRICO MANUAL
# ============================================================

@st.cache_data(ttl=3600)
def carregar_historico_json():

    try:

        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(
                arquivo
            )

    except FileNotFoundError:

        return {}

    except json.JSONDecodeError:

        return {}


historico_manual = carregar_historico_json()


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

    return (
        str(nome)
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


# ============================================================
# POKÉAPI
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def requisicao_api(url):

    headers = {
        "User-Agent": "KAYZAC-Master-Pokemon/1.0"
    }

    for _ in range(3):
        try:
            resposta = requests.get(
                url,
                headers=headers,
                timeout=15
            )
            resposta.raise_for_status()
            return resposta.json()
        except requests.exceptions.RequestException:
            continue

    return None


# ============================================================
# BUSCAR POKÉMON
# ============================================================

@st.cache_data(ttl=3600)
def buscar_pokemon(identificador):

    valor = str(
        identificador
    ).strip()

    if valor.startswith(
        "https://pokeapi.co/"
    ):

        dados = requisicao_api(
            valor
        )

        if dados is not None:
            return dados

        try:
            return dados_fallback_pokemon(valor)
        except NameError:
            return None

    if valor.isdigit():

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon/{valor}"
        )

        dados = requisicao_api(
            url
        )

        if dados is not None:
            return dados

        try:
            return dados_fallback_pokemon(valor)
        except NameError:
            return None

    nome = normalizar_nome(
        valor
    )

    url = (
        "https://pokeapi.co/api/v2/"
        f"pokemon/{nome}"
    )

    dados = requisicao_api(
        url
    )

    if dados is not None:
        return dados

    try:
        return dados_fallback_pokemon(nome)
    except NameError:
        return None


# ============================================================
# FALLBACK LOCAL
# ============================================================

DADOS_FALLBACK_POKEMON = {
    "zygarde": {
        "id": 718,
        "name": "zygarde",
        "species": {"name": "zygarde"},
        "height": 50,
        "weight": 3050,
        "base_experience": 114,
        "types": [
            {"slot": 1, "type": {"name": "dragon"}},
            {"slot": 2, "type": {"name": "ground"}},
        ],
        "abilities": [
            {"ability": {"name": "aura-break"}, "is_hidden": False, "slot": 1},
            {"ability": {"name": "power-construct"}, "is_hidden": True, "slot": 3},
        ],
        "stats": [
            {"base_stat": 108, "stat": {"name": "hp"}},
            {"base_stat": 100, "stat": {"name": "attack"}},
            {"base_stat": 121, "stat": {"name": "defense"}},
            {"base_stat": 81, "stat": {"name": "special-attack"}},
            {"base_stat": 95, "stat": {"name": "special-defense"}},
            {"base_stat": 95, "stat": {"name": "speed"}},
        ],
        "sprites": {
            "front_default": "https://play.pokemonshowdown.com/sprites/home/zygarde.png",
            "front_shiny": "https://play.pokemonshowdown.com/sprites/home/zygarde.png",
            "other": {
                "home": {
                    "front_default": "https://play.pokemonshowdown.com/sprites/home/zygarde.png"
                },
                "official-artwork": {
                    "front_default": "https://play.pokemonshowdown.com/sprites/home/zygarde.png"
                },
                "showdown": {
                    "front_default": "zygarde.png"
                },
            },
        },
        "cries": {},
    }
}


def dados_fallback_pokemon(identificador):
    chave = normalizar_nome(identificador)
    dados = DADOS_FALLBACK_POKEMON.get(chave)
    if dados is None and chave == "zygarde-50-power-construct":
        dados = DADOS_FALLBACK_POKEMON.get("zygarde")
    return dict(dados) if dados else None


# ============================================================
# BUSCAR ESPÉCIE
# ============================================================

@st.cache_data(ttl=3600)
def buscar_especie(nome):

    identificador = str(
        nome
    ).strip()

    if identificador.startswith(
        "https://pokeapi.co/"
    ):

        return requisicao_api(
            identificador
        )

    if identificador.isdigit():

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-species/{identificador}"
        )

    else:

        nome_api = normalizar_nome(
            identificador
        )

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-species/{nome_api}"
        )

    return requisicao_api(
        url
    )


# ============================================================
# BUSCAR EVOLUTION CHAIN
# ============================================================

@st.cache_data(ttl=3600)
def buscar_evolution_chain(url):

    return requisicao_api(
        url
    )


# ============================================================
# BUSCAR POKÉMON-FORM
# ============================================================

@st.cache_data(ttl=3600)
def buscar_pokemon_form(id_api):

    valor = str(
        id_api
    ).strip()

    if valor.startswith(
        "https://pokeapi.co/"
    ):

        return requisicao_api(
            valor
        )

    if valor.isdigit():

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-form/{valor}"
        )

    else:

        nome = normalizar_nome(
            valor
        )

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-form/{nome}"
        )

    return requisicao_api(
        url
    )


# ============================================================
# BUSCAR FORMA
# ============================================================

@st.cache_data(ttl=3600)
def buscar_forma(id_api):
    """
    Busca a forma no endpoint pokemon-form.

    IMPORTANTE: não transforma automaticamente a forma na espécie-base.
    A ficha base pode continuar sendo buscada separadamente, mas os
    sprites da forma ficam preservados em _sprites_forma.
    """

    if not id_api:
        return None

    valor = str(
        id_api
    ).strip()

    if not valor:
        return None

    # URL direta para pokemon-form.
    if valor.startswith(
        "https://pokeapi.co/api/v2/pokemon-form/"
    ):

        return requisicao_api(
            valor
        )

    nome = valor.rstrip("/").split("/")[-1]

    if nome.isdigit():

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-form/{nome}"
        )

    else:

        nome = normalizar_nome(
            nome
        )

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon-form/{nome}"
        )

    return requisicao_api(
        url
    )


# ============================================================
# CARREGAR DADOS DA FORMA
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dados_forma(id_api):
    """
    Carrega os dados gerais necessários para exibir uma forma sem
    perder os sprites específicos dela.

    A PokéAPI normalmente representa a forma em /pokemon-form/ e
    relaciona essa forma à espécie-base em ``pokemon``. Portanto:
    - os dados gerais vêm da espécie-base;
    - os sprites do endpoint pokemon-form ficam preservados em
      ``_sprites_forma``;
    - quando a forma ainda não possui endpoint na PokéAPI, usamos
      a espécie-base como fallback para dados de texto/stats.
    """

    if not id_api:
        return None

    valor = str(id_api).strip()

    if not valor:
        return None

    # --------------------------------------------------------
    # 1) Tenta obter o registro específico de pokemon-form.
    # --------------------------------------------------------

    dados_forma = buscar_forma(valor)
    sprites_forma = extrair_sprites_forma_api(dados_forma)

    relacionado = None

    if dados_forma:
        relacionado = (
            dados_forma
            .get("pokemon", {})
            .get("name")
        )

    # --------------------------------------------------------
    # 2) Busca a espécie-base relacionada.
    # --------------------------------------------------------

    if relacionado:
        base = buscar_pokemon(relacionado)

        if base is not None:
            dados = dict(base)
            dados["_sprites_forma"] = sprites_forma
            dados["_forma_api"] = dados_forma
            return dados

    # --------------------------------------------------------
    # 3) Algumas formas novas ainda não têm pokemon-form na
    #    versão de dados utilizada pela PokéAPI. Tenta descobrir
    #    a espécie-base pelo próprio identificador.
    # --------------------------------------------------------

    slug = normalizar_nome(valor)

    candidatos_base = []

    def adicionar_candidato(nome):
        nome = normalizar_nome(nome)
        if nome and nome not in candidatos_base:
            candidatos_base.append(nome)

    # Mega X/Y/Z e Mega normal.
    for sufixo in (
        "-mega-z",
        "-mega-x",
        "-mega-y",
        "-mega",
    ):
        if slug.endswith(sufixo):
            adicionar_candidato(
                slug[:-len(sufixo)]
            )

    # Formas comuns com sufixos.
    for sufixo in (
        "-gigantamax",
        "-gmax",
        "-eternal",
        "-f",
        "-female",
        "-m",
        "-male",
        "-blade",
        "-shield",
        "-rapid-strike",
        "-single-strike",
        "-combat-breed",
        "-blaze-breed",
        "-aqua-breed",
        "-heart",
        "-diamond",
        "-star",
        "-pharaoh",
        "-kabuki",
        "-matron",
        "-dandy",
        "-debutante",
        "-la-reine",
        "-diamond",
        "-detective",
        "-cosplay",
    ):
        if slug.endswith(sufixo):
            adicionar_candidato(
                slug[:-len(sufixo)]
            )

    # Casos em que há várias palavras depois da espécie-base.
    partes = slug.split("-")

    if len(partes) >= 2:
        adicionar_candidato(partes[0])

    # Zygarde é mantido mesmo quando a PokéAPI usada pelo app estiver
    # temporariamente sem o registro esperado.
    if slug.startswith("zygarde"):
        adicionar_candidato("zygarde")

    for candidato in candidatos_base:
        base = buscar_pokemon(candidato)

        if base is not None:
            dados = dict(base)
            dados["_sprites_forma"] = sprites_forma
            dados["_forma_api"] = dados_forma
            return dados

        fallback = dados_fallback_pokemon(candidato)

        if fallback is not None:
            fallback["_sprites_forma"] = sprites_forma
            fallback["_forma_api"] = dados_forma
            return fallback

    # --------------------------------------------------------
    # 4) Se o endpoint pokemon-form retornou algo útil mesmo sem
    #    espécie relacionada, preserva o resultado.
    # --------------------------------------------------------

    if dados_forma:
        dados = dict(dados_forma)
        dados["_sprites_forma"] = sprites_forma
        dados["_forma_api"] = dados_forma
        return dados

    return None


# ============================================================
# BUSCAR LOCAIS
# ============================================================

@st.cache_data(ttl=3600)
def buscar_locais(url):

    return requisicao_api(
        url
    ) or []


# ============================================================
# BUSCAR MOVIMENTO
# ============================================================

@st.cache_data(ttl=3600)
def buscar_movimento(url):

    return requisicao_api(
        url
    )


# ============================================================
# BUSCAR HABILIDADE
# ============================================================

@st.cache_data(ttl=3600)
def buscar_habilidade(url):

    return requisicao_api(
        url
    )


# ============================================================
# BUSCAR EGG GROUP
# ============================================================

@st.cache_data(ttl=3600)
def buscar_egg_group(nome):

    nome_api = normalizar_nome(
        nome
    )

    url = (
        "https://pokeapi.co/api/v2/"
        f"egg-group/{nome_api}"
    )

    return requisicao_api(
        url
    )


@st.cache_data(ttl=3600)
def buscar_lista_pokemon_egg_group(nome):

    dados = buscar_egg_group(
        nome
    )

    if not dados:

        return []

    return dados.get(
        "pokemon_species",
        []
    )


# ============================================================
# IDIOMAS E TRADUÇÕES
# ============================================================

IDIOMAS_PREFERIDOS = (
    "pt-br",
    "pt",
    "en"
)


def obter_texto_localizado(
    entradas,
    campo="effect",
    idiomas=IDIOMAS_PREFERIDOS
):

    if not entradas:

        return None

    for idioma in idiomas:

        for entrada in entradas:

            idioma_entrada = (
                entrada
                .get(
                    "language",
                    {}
                )
                .get(
                    "name",
                    ""
                )
                .lower()
            )

            if idioma_entrada == idioma:

                texto = entrada.get(
                    campo,
                    ""
                )

                if texto:

                    return texto

    return None


def limpar_texto_api(texto):

    if not texto:

        return ""

    return (
        str(texto)
        .replace("\\n", " ")
        .replace("\\f", " ")
        .replace("\n", " ")
        .replace("\f", " ")
        .replace("  ", " ")
        .strip()
    )


def traduzir_tipo(tipo):

    tipos = {

        "normal": "Normal",
        "fire": "Fogo",
        "water": "Água",
        "electric": "Elétrico",
        "grass": "Grama",
        "ice": "Gelo",
        "fighting": "Lutador",
        "poison": "Veneno",
        "ground": "Terrestre",
        "flying": "Voador",
        "psychic": "Psíquico",
        "bug": "Inseto",
        "rock": "Pedra",
        "ghost": "Fantasma",
        "dragon": "Dragão",
        "dark": "Sombrio",
        "steel": "Aço",
        "fairy": "Fada"
    }

    return tipos.get(
        str(tipo).lower(),
        nome_bonito(tipo)
    )


def traduzir_categoria_golpe(categoria):

    categorias = {

        "physical": "Físico",
        "special": "Especial",
        "status": "Status"
    }

    return categorias.get(
        str(categoria).lower(),
        nome_bonito(categoria)
    )


def traduzir_metodo_aprendizado(metodo):

    metodos = {

        "level-up": "Por nível",
        "machine": "MT / TM",
        "tutor": "Tutor",
        "egg": "Movimento de Ovo",
        "stadium-surfing-pikachu": "Evento / Stadium",
        "light-ball-egg": "Movimento de Ovo",
        "colosseum-purification": "Purificação / Colosseum",
        "xd-shadow": "Shadow / Pokémon XD",
        "xd-purification": "Purificação / Pokémon XD",
        "form-change": "Mudança de forma",
        "zygarde-cube": "Cubo de Zygarde",
        "spent-on-move": "Método especial"
    }

    return metodos.get(
        str(metodo).lower(),
        nome_bonito(metodo)
    )


# ============================================================
# DESCRIÇÕES DE HABILIDADES
# ============================================================

def obter_descricao_ability(dados):

    if not dados:

        return "Descrição não disponível."

    texto = obter_texto_localizado(
        dados.get(
            "effect_entries",
            []
        ),
        campo="effect"
    )

    if not texto:

        texto = obter_texto_localizado(
            dados.get(
                "flavor_text_entries",
                []
            ),
            campo="flavor_text"
        )

    return (
        limpar_texto_api(
            texto
        )
        or "Descrição não disponível."
    )


def obter_resumo_ability(dados):

    if not dados:

        return "Descrição curta não disponível."

    texto = obter_texto_localizado(
        dados.get(
            "effect_entries",
            []
        ),
        campo="short_effect"
    )

    return (
        limpar_texto_api(
            texto
        )
        or "Descrição curta não disponível."
    )


# ============================================================
# DESCRIÇÕES DE GOLPES
# ============================================================

def obter_descricao_movimento(
    dados,
    curta=False
):

    if not dados:

        return "Descrição não disponível."

    campo = (
        "short_effect"
        if curta
        else "effect"
    )

    texto = obter_texto_localizado(
        dados.get(
            "effect_entries",
            []
        ),
        campo=campo
    )

    if not texto:

        texto = obter_texto_localizado(
            dados.get(
                "flavor_text_entries",
                []
            ),
            campo="flavor_text"
        )

    texto = limpar_texto_api(
        texto
    )

    chance = dados.get(
        "effect_chance"
    )

    if (
        texto
        and chance is not None
        and "$effect_chance" in texto
    ):

        texto = texto.replace(
            "$effect_chance",
            str(chance)
        )

    return (
        texto
        or "Descrição não disponível."
    )


def obter_metodos_aprendizado(
    movimento
):

    detalhes = movimento.get(
        "version_group_details",
        []
    )

    resultados = []

    for detalhe in detalhes:

        metodo = (
            detalhe
            .get(
                "move_learn_method",
                {}
            )
            .get(
                "name"
            )
        )

        if not metodo:

            continue

        texto_metodo = (
            traduzir_metodo_aprendizado(
                metodo
            )
        )

        nivel = detalhe.get(
            "level_learned_at",
            0
        )

        if (
            metodo == "level-up"
            and nivel
        ):

            texto_metodo += (
                f" — Nível {nivel}"
            )

        versao = (
            detalhe
            .get(
                "version_group",
                {}
            )
            .get(
                "name"
            )
        )

        resultados.append(
            (
                texto_metodo,
                (
                    nome_bonito(
                        versao
                    )
                    if versao
                    else None
                )
            )
        )

    unicos = []

    vistos = set()

    for item in resultados:

        if item in vistos:

            continue

        vistos.add(item)

        unicos.append(
            item
        )

    return unicos


# ============================================================
# SPRITES
# ============================================================

def _texto_url(valor):

    if valor is None:
        return None

    valor = str(valor).strip()

    return valor if valor else None


def obter_sprites(pokemon):
    """
    Sprites do Pokémon principal.

    Esta função continua usando os dados normais da PokéAPI.
    Para FORMAS, existe uma função separada abaixo que nunca
    herda silenciosamente o sprite da espécie-base.
    """

    sprites = pokemon.get(
        "sprites",
        {}
    ) or {}

    outros = sprites.get(
        "other",
        {}
    ) or {}

    showdown = outros.get(
        "showdown",
        {}
    ) or {}

    artwork = outros.get(
        "official-artwork",
        {}
    ) or {}

    return {
        "pixel_normal": _texto_url(sprites.get("front_default")),
        "pixel_normal_female": _texto_url(sprites.get("front_female")),
        "3d_normal": _texto_url(showdown.get("front_default")),
        "3d_normal_female": _texto_url(showdown.get("front_female")),
        "artwork_normal": _texto_url(artwork.get("front_default")),
        "artwork_normal_female": _texto_url(artwork.get("front_female")),
        "pixel_shiny": _texto_url(sprites.get("front_shiny")),
        "pixel_shiny_female": _texto_url(sprites.get("front_shiny_female")),
        "3d_shiny": _texto_url(showdown.get("front_shiny")),
        "3d_shiny_female": _texto_url(showdown.get("front_shiny_female")),
        "artwork_shiny": _texto_url(artwork.get("front_shiny")),
        "artwork_shiny_female": _texto_url(artwork.get("front_shiny_female")),
    }


def eh_femea(pokemon):

    nome = (
        pokemon
        .get(
            "name",
            ""
        )
        .lower()
    )

    return (
        "female" in nome
        or nome.endswith("-f")
        or "-f-" in nome
    )


def mostrar_imagem(
    url,
    legenda,
    largura=180
):

    st.caption(
        legenda
    )

    if url:

        st.image(
            url,
            width=largura
        )

    else:

        st.info(
            "Imagem indisponível."
        )


def mostrar_sprites(pokemon):
    """
    Galeria normal de um Pokémon.

    Esta função pode usar os sprites normais/femininos da espécie.
    NÃO deve ser usada para uma forma especial que tenha sido
    carregada apenas através do pokemon-form.
    """

    sprites = obter_sprites(
        pokemon
    )

    femea = eh_femea(
        pokemon
    )

    # ========================================================
    # NORMAL
    # ========================================================

    st.markdown(
        "### 🌟 Forma Normal"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        mostrar_imagem(
            (
                sprites["pixel_normal_female"]
                if femea
                and sprites.get("pixel_normal_female")
                else sprites["pixel_normal"]
            ),
            (
                "🟦 Pixel 2D ♀️"
                if femea
                and sprites.get("pixel_normal_female")
                else "🟦 Pixel 2D"
            ),
            180
        )

    with col2:

        mostrar_imagem(
            (
                sprites["3d_normal_female"]
                if femea
                and sprites.get("3d_normal_female")
                else sprites["3d_normal"]
            ),
            (
                "🟩 3D / Showdown ♀️"
                if femea
                and sprites.get("3d_normal_female")
                else "🟩 3D / Showdown"
            ),
            180
        )

    with col3:

        mostrar_imagem(
            (
                sprites["artwork_normal_female"]
                if femea
                and sprites.get("artwork_normal_female")
                else sprites["artwork_normal"]
            ),
            (
                "🎨 Artwork Oficial ♀️"
                if femea
                and sprites.get("artwork_normal_female")
                else "🎨 Artwork Oficial"
            ),
            180
        )

    # ========================================================
    # SHINY
    # ========================================================

    st.markdown(
        "### ✨ Forma Shiny"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        mostrar_imagem(
            (
                sprites["pixel_shiny_female"]
                if femea
                and sprites.get("pixel_shiny_female")
                else sprites["pixel_shiny"]
            ),
            (
                "🟦 Pixel 2D Shiny ♀️"
                if femea
                and sprites.get("pixel_shiny_female")
                else "🟦 Pixel 2D Shiny"
            ),
            180
        )

    with col2:

        mostrar_imagem(
            (
                sprites["3d_shiny_female"]
                if femea
                and sprites.get("3d_shiny_female")
                else sprites["3d_shiny"]
            ),
            (
                "🟩 3D Shiny ♀️"
                if femea
                and sprites.get("3d_shiny_female")
                else "🟩 3D Shiny"
            ),
            180
        )

    with col3:

        mostrar_imagem(
            sprites["artwork_shiny"],
            "🎨 Artwork Shiny",
            180
        )


# ============================================================
# SPRITES ESPECÍFICOS DE FORMAS
# ============================================================

def extrair_sprites_forma_api(dados_forma):
    """
    Extrai EXCLUSIVAMENTE os sprites do recurso pokemon-form.

    Isso é importante porque o recurso pokemon-form pode apontar
    para a espécie-base em "pokemon". O sprite, porém, pertence
    à própria forma e não deve ser substituído pelo da espécie-base.
    """

    if not dados_forma:
        return {}

    sprites = dados_forma.get(
        "sprites",
        {}
    ) or {}

    return {
        "pixel_normal": _texto_url(sprites.get("front_default")),
        "pixel_normal_female": _texto_url(sprites.get("front_female")),
        "pixel_shiny": _texto_url(sprites.get("front_shiny")),
        "pixel_shiny_female": _texto_url(sprites.get("front_shiny_female")),
        "back_normal": _texto_url(sprites.get("back_default")),
        "back_shiny": _texto_url(sprites.get("back_shiny")),
    }


def _slug_forma_showdown(valor):
    """Cria nomes compatíveis com os arquivos de sprites do Showdown."""

    if not valor:
        return []

    slug = normalizar_nome(valor)
    candidatos = []

    def adicionar(item):
        item = normalizar_nome(item)
        if item and item not in candidatos:
            candidatos.append(item)

    # Para formas com nomenclatura diferente, priorizamos primeiro
    # o nome real do arquivo no Showdown e só depois o ID original.

    # "Mega Lucario Z" / "lucario-mega-z" -> lucario-megaz
    partes = slug.split("-")
    if len(partes) >= 2 and partes[0] == "mega":
        base = "-".join(partes[1:])
        if base.endswith("-z"):
            adicionar(base[:-2] + "-megaz")
        elif base.endswith("-x"):
            adicionar(base[:-2] + "-megax")
        elif base.endswith("-y"):
            adicionar(base[:-2] + "-megay")
        else:
            adicionar(base + "-mega")

    # Mega X / Y / Z.
    adicionar(slug.replace("-mega-x", "-megax"))
    adicionar(slug.replace("-mega-y", "-megay"))
    adicionar(slug.replace("-mega-z", "-megaz"))

    # Meowstic Mega.
    adicionar(slug.replace("-mega-m", "-mmega"))
    adicionar(slug.replace("-mega-f", "-fmega"))

    # Furfrou: "heart-trim" -> "heart" etc.
    adicionar(slug.replace("-trim", ""))
    adicionar(slug.replace("-form", ""))

    # G-Max.
    adicionar(slug.replace("-gigantamax", "-gmax"))
    adicionar(slug.replace("-gmax", "-gigantamax"))

    # Sexo / feminino.
    adicionar(slug.replace("-female", "-f"))
    adicionar(slug.replace("-male", "-m"))

    # Nome original por último, como fallback.
    adicionar(slug)

    return candidatos


SHOWDOWN_HOME_BASE = "https://play.pokemonshowdown.com/sprites/home/"
SHOWDOWN_HOME_CENTERED_BASE = "https://play.pokemonshowdown.com/sprites/home-centered/"
SHOWDOWN_DEX_BASE = "https://play.pokemonshowdown.com/sprites/dex/"
SHOWDOWN_2D_BASE = "https://play.pokemonshowdown.com/sprites/gen5/"
SHOWDOWN_ANIM_BASE = "https://play.pokemonshowdown.com/sprites/ani/"


FORMAS_FONTES_ESPECIAIS = {"lucario-mega-z": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0448Lucario-Mega_Z_ZA.png", "visual_3d": None, "animado": None, "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0448Lucario-Mega_Z_ZA.png"}, "garchomp-mega-z": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0445Garchomp-Mega_Z_ZA.png", "visual_3d": None, "animado": None, "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0445Garchomp-Mega_Z_ZA.png"}, "absol-mega-z": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0359Absol-Mega_Z.png", "visual_3d": None, "animado": None}, "zygarde-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0718Zygarde-Mega.png", "visual_3d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0718M.png", "animado": None, "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0718M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0718M_s.png"}, "floette-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0670Floette-Mega.png", "visual_3d": None, "animado": None, "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0670M.png", "home_shiny": None}, "raichu-mega-x": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0026Raichu-Mega_X_ZA.png", "visual_3d": None, "animado": None, "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0026Raichu-Mega_X_ZA.png"}, "raichu-mega-y": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0026Raichu-Mega_Y_ZA.png", "visual_3d": None, "animado": None, "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0026Raichu-Mega_Y_ZA.png"}, "dragonite-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0149Dragonite-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0149Dragonite-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0149M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0149M_s.png"}, "victreebel-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0071Victreebel-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0071Victreebel-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0071M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0071M_s.png"}, "starmie-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0121Starmie-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0121M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0121M_s.png"}, "clefable-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0036Clefable-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0036M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0036M_s.png"}, "meganium-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0154Meganium-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0154Meganium-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0154M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0154M_s.png"}, "feraligatr-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0160Feraligatr-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0160Feraligatr-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0160M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0160M_s.png"}, "skarmory-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0227Skarmory-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0227M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0227M_s.png"}, "chimecho-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0358Chimecho-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0358M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0358M_s.png"}, "staraptor-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0398Staraptor-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0398M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0398M_s.png"}, "froslass-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0478Froslass-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0478M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0478M_s.png"}, "heatran-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0485Heatran-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0485M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0485M_s.png"}, "darkrai-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0491Darkrai-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0491M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0491M_s.png"}, "emboar-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0500Emboar-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0500Emboar-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0500M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0500M_s.png"}, "excadrill-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0530Excadrill-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0530M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0530M_s.png"}, "scolipede-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0545Scolipede-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0545M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0545M_s.png"}, "scrafty-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0560Scrafty-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0560M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0560M_s.png"}, "eelektross-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0604Eelektross-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0604Eelektross-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0604M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0604M_s.png"}, "chandelure-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0609Chandelure-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0609M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0609M_s.png"}, "golurk-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0623Golurk-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0623M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0623M_s.png"}, "chesnaught-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0652Chesnaught-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0652Chesnaught-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0652M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0652M_s.png"}, "delphox-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0655Delphox-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0655Delphox-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0655M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0655M_s.png"}, "greninja-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0658Greninja-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0658Greninja-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0658M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0658M_s.png"}, "pyroar-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0668Pyroar-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0668M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0668M_s.png"}, "meowstic-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0678Meowstic-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M_s.png"}, "meowstic-m-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0678Meowstic-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M_s.png"}, "meowstic-f-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0678Meowstic-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0678M_s.png"}, "malamar-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0687Malamar-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0687Malamar-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0687M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0687M_s.png"}, "barbaracle-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0689Barbaracle-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0689M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0689M_s.png"}, "dragalge-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0691Dragalge-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0691M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0691M_s.png"}, "hawlucha-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0701Hawlucha-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0701Hawlucha-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0701M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0701M_s.png"}, "crabominable-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0740Crabominable-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0740M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0740M_s.png"}, "golisopod-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0768Golisopod-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0768M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0768M_s.png"}, "drampa-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0780Drampa-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0780M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0780M_s.png"}, "magearna-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0801Magearna-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0801M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0801M_s.png"}, "magearna-original-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0801Magearna-Original_Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0801M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0801M_s.png"}, "zeraora-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0807Zeraora-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0807Zeraora-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0807M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0807M_s.png"}, "falinks-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0870Falinks-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0870M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0870M_s.png"}, "scovillain-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0952Scovillain-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0952M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0952M_s.png"}, "glimmora-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0970Glimmora-Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0970M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0970M_s.png"}, "tatsugiri-curly-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0978Tatsugiri-Curly_Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M_s.png"}, "tatsugiri-droopy-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0978Tatsugiri-Droopy_Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M_s.png"}, "tatsugiri-stretchy-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0978Tatsugiri-Stretchy_Mega.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0978M_s.png"}, "baxcalibur-mega": {"2d": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0998Baxcalibur-Mega_ZA.png", "2d_high": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/0998Baxcalibur-Mega_ZA.png", "home": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0998M.png", "home_shiny": "https://archives.bulbagarden.net/wiki/Special:Redirect/file/HOME0998M_s.png"}}

@st.cache_data(ttl=86400, show_spinner=False)
def url_imagem_disponivel(url):
    """Confirma que a URL responde com um arquivo de imagem."""
    if not url:
        return False

    try:
        resposta = requests.get(
            url,
            timeout=12,
            stream=True,
            headers={"User-Agent": "KAYZAC-Master-Pokemon/1.0"},
            allow_redirects=True,
        )
        content_type = resposta.headers.get("content-type", "").lower()
        ok = resposta.status_code == 200 and (
            content_type.startswith("image/")
            or url.lower().split("?")[0].endswith((".png", ".gif", ".jpg", ".jpeg", ".webp"))
        )
        resposta.close()
        return ok
    except requests.RequestException:
        return False


@st.cache_data(ttl=21600, show_spinner=False)
def resolver_fontes_forma(id_api, nome_forma):
    """
    Resolve canais visuais de uma forma SEM fallback genérico.

    Ordem:
    1) fonte especial explicitamente cadastrada;
    2) sprites do próprio pokemon-form da PokéAPI;
    3) imagem local explícita.

    O Showdown não entra nesta resolução para formas especiais.
    """
    chave = normalizar_nome(id_api or nome_forma or "")
    especiais = FORMAS_FONTES_ESPECIAIS.get(chave, {})

    resultado = {
        "2d": especiais.get("2d"),
        "2d_high": especiais.get("2d_high"),
        "home": especiais.get("home"),
        "home_shiny": especiais.get("home_shiny"),
        "shiny": especiais.get("shiny"),
        "animado": especiais.get("animado"),
        "slug": chave,
    }

    # Verifica as fontes especiais em separado. Uma fonte quebrada não
    # bloqueia as demais.
    for campo in ("2d", "2d_high", "home", "home_shiny", "shiny", "animado"):
        url = resultado.get(campo)
        if url and not url_imagem_disponivel(url):
            resultado[campo] = None

    return resultado


def obter_fontes_forma(id_api, nome_forma, dados=None):
    """Combina fonte especial com sprites EXCLUSIVOS de pokemon-form."""
    fontes = resolver_fontes_forma(id_api, nome_forma)
    sprites_forma = (dados.get("_sprites_forma", {}) if dados else {}) or {}

    # Os sprites da API são específicos da forma e têm prioridade sobre
    # qualquer fallback externo para 2D/shiny.
    if sprites_forma.get("pixel_normal"):
        fontes["2d_api"] = sprites_forma.get("pixel_normal")
    else:
        fontes["2d_api"] = None

    if sprites_forma.get("pixel_shiny"):
        fontes["shiny_api"] = sprites_forma.get("pixel_shiny")
    else:
        fontes["shiny_api"] = None

    if sprites_forma.get("pixel_normal_female"):
        fontes["2d_api_female"] = sprites_forma.get("pixel_normal_female")
    else:
        fontes["2d_api_female"] = None

    if sprites_forma.get("pixel_shiny_female"):
        fontes["shiny_api_female"] = sprites_forma.get("pixel_shiny_female")
    else:
        fontes["shiny_api_female"] = None

    return fontes


def mostrar_sprites_forma(forma, dados, id_api, nome):
    """Galeria completa da forma sem usar imagens da espécie-base."""

    imagem_local = forma.get("imagem_local")
    caminho_local = carregar_imagem_local(imagem_local)

    fontes = obter_fontes_forma(id_api, nome, dados)

    if caminho_local is not None:
        with st.expander("📸 Imagem local da forma", expanded=True):
            st.image(str(caminho_local), width=520)
            st.caption("🖼️ Imagem local específica desta forma.")

    # --------------------------------------------------------
    # 2D / ARTWORK
    # --------------------------------------------------------
    st.markdown("### 🟦 2D da forma")

    url_2d = (
        fontes.get("2d_api_female")
        or fontes.get("2d_api")
        or fontes.get("2d_high")
        or fontes.get("2d")
    )

    if url_2d:
        mostrar_imagem(
            url_2d,
            "🟦 2D específico da forma",
            420,
        )
    else:
        st.info("🟦 2D específico desta forma indisponível.")

    # --------------------------------------------------------
    # HOME / RENDER
    # --------------------------------------------------------
    st.markdown("### 🏠 Pokémon HOME")

    home = fontes.get("home")
    if home:
        mostrar_imagem(
            home,
            "🏠 Render específico da forma • Pokémon HOME",
            360,
        )
    else:
        st.info("🏠 Render específico desta forma no HOME indisponível.")

    # --------------------------------------------------------
    # SHINY
    # --------------------------------------------------------
    st.markdown("### ✨ Shiny da forma")

    shiny = (
        fontes.get("shiny_api_female")
        or fontes.get("shiny_api")
        or fontes.get("shiny")
    )

    if shiny:
        mostrar_imagem(
            shiny,
            "✨ Shiny específico da forma",
            420,
        )
    else:
        st.info(
            "✨ Ainda não existe uma imagem Shiny específica "
            "disponível nas fontes utilizadas para esta forma."
        )

    # --------------------------------------------------------
    # HOME SHINY
    # --------------------------------------------------------
    st.markdown("### 🌟 Pokémon HOME — Shiny")

    home_shiny = fontes.get("home_shiny")
    if home_shiny:
        mostrar_imagem(
            home_shiny,
            "🌟 Render Shiny específico da forma • Pokémon HOME",
            360,
        )
    else:
        st.info(
            "🌟 Render Shiny específico desta forma no HOME indisponível."
        )

    # --------------------------------------------------------
    # ANIMADO
    # --------------------------------------------------------
    st.markdown("### 🎞️ Animado")

    animado = fontes.get("animado")
    if animado:
        st.image(animado, width=420)
        st.caption("🎞️ Sprite/animação específica da forma.")
    else:
        st.info("🎞️ Animação específica desta forma indisponível.")




def carregar_imagem_local(caminho):
    """
    Converte o caminho cadastrado no JSON em um caminho absoluto dentro
    do projeto.
    """

    if not caminho:
        return None

    caminho = str(
        caminho
    ).strip()

    if not caminho:
        return None

    caminho_path = Path(
        caminho
    )

    if caminho_path.is_absolute():

        return (
            caminho_path
            if caminho_path.exists()
            else None
        )

    candidato = BASE_DIR / caminho_path

    if candidato.exists():
        return candidato

    candidato = (
        BASE_DIR
        / "imagens"
        / "formas"
        / caminho_path.name
    )

    if candidato.exists():
        return candidato

    return None


def procurar_imagem_local_forma(
    id_api,
    nome_forma
):
    """Procura somente arquivos locais com o identificador da forma."""

    valores = [id_api] if id_api else [nome_forma]
    candidatos = []

    for valor in valores:
        for slug in _slug_forma_showdown(valor):
            if slug not in candidatos:
                candidatos.append(slug)

    extensoes = (
        ".png",
        ".webp",
        ".jpg",
        ".jpeg",
        ".gif",
    )

    pastas = (
        BASE_DIR / "imagens" / "formas",
        BASE_DIR / "imagens",
    )

    for pasta in pastas:
        for slug in candidatos:
            for extensao in extensoes:
                caminho = pasta / (slug + extensao)
                if caminho.exists():
                    return caminho

    return None


def mostrar_sprites_local_forma(forma):
    """Compatibilidade com chamadas antigas."""

    caminho = carregar_imagem_local(
        forma.get("imagem_local")
    )

    if caminho is None:
        return False

    with st.expander(
        "📸 Ver imagem da forma"
    ):

        st.image(
            str(caminho),
            width=300
        )

        st.caption(
            "🖼️ Imagem local específica desta forma."
        )

    return True


def dados_manuais_para_forma(forma):
    """
    Cria uma estrutura mínima compatível com a exibição
    da Pokédex quando a forma não possui registro na PokéAPI.
    """
    tipos = []

    for tipo in forma.get("tipo", forma.get("tipos", [])):

        if isinstance(tipo, str):

            tipos.append(
                {
                    "type": {
                        "name": tipo.lower()
                    }
                }
            )

    return {
        "name": forma.get(
            "id_api",
            normalizar_nome(
                forma.get(
                    "nome",
                    "forma-especial"
                )
            )
        ),
        "types": tipos,
        "abilities": [],
        "stats": [],
        "sprites": {}
    }


def mostrar_forma(
    forma,
    icone="✨",
    especie_base=None
):

    nome = forma.get(
        "nome",
        "Forma desconhecida"
    )

    id_api = forma.get(
        "id_api"
    )

    categoria = forma.get(
        "categoria",
        "Forma Especial"
    )

    regiao = forma.get(
        "regiao"
    )

    origem = forma.get(
        "origem"
    )

    descricao = forma.get(
        "descricao"
    )

    imagem_local = forma.get(
        "imagem_local"
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"### {icone} {nome}"
        )

        c1, c2 = st.columns(
            2
        )

        with c1:

            st.write(
                f"**Categoria:** {categoria}"
            )

            if regiao:

                st.write(
                    f"**Região:** {regiao}"
                )

        with c2:

            if origem:

                st.write(
                    f"**Origem:** {origem}"
                )

            if id_api:

                st.caption(
                    f"API: `{id_api}`"
                )

            if imagem_local:

                st.caption(
                    f"Imagem local: `{imagem_local}`"
                )

        if descricao:

            st.info(
                f"📖 {descricao}"
            )

        dados = None
        dados_vieram_da_api = False

        # --------------------------------------------------------
        # PRIMEIRO: tenta carregar a forma mantendo os sprites dela.
        # --------------------------------------------------------

        if id_api:

            with st.spinner(
                f"🔮 Carregando {nome}..."
            ):

                dados = carregar_dados_forma(
                    id_api
                )

            if dados is not None:
                dados_vieram_da_api = True

        # --------------------------------------------------------
        # SEGUNDO: se não existir na API, usa o JSON local.
        # --------------------------------------------------------

        if dados is None:

            dados = dados_manuais_para_forma(
                forma
            )

            if not imagem_local and not forma.get("tipo") and not forma.get("tipos"):

                st.warning(
                    f"⚠️ Não foi possível carregar "
                    f"a forma **{nome}** pela PokéAPI."
                )

                if id_api:

                    st.caption(
                        f"Identificador utilizado: `{id_api}`"
                    )

        # ====================================================
        # BOTÃO PARA ABRIR FICHA COMPLETA
        # ====================================================

        nome_pokemon_forma = dados.get(
            "name"
        )

        if (
            id_api
            and nome_pokemon_forma
        ):

            chave_botao = (
                "abrir_forma_"
                f"{normalizar_nome(nome)}_"
                f"{normalizar_nome(str(id_api or 'local'))}"
            )

            if st.button(
                f"📖 Abrir ficha de {nome}",
                key=chave_botao
            ):

                if especie_base:
                    navegar_para_forma(
                        forma,
                        especie_base
                    )
                else:
                    navegar_para_pokemon(
                        nome_pokemon_forma
                    )

        # ====================================================
        # TIPOS
        # ====================================================

        tipos = dados.get(
            "types",
            []
        )

        if tipos:

            st.write(
                "**Tipos:** "
                + " / ".join(
                    traduzir_tipo(
                        tipo["type"]["name"]
                    )
                    for tipo in tipos
                    if tipo.get("type", {}).get("name")
                )
            )

        # ====================================================
        # HABILIDADES
        # ====================================================

        habilidades = dados.get(
            "abilities",
            []
        )

        if habilidades:

            nomes_habilidades = []

            for habilidade in habilidades:

                nome_habilidade = (
                    habilidade
                    .get(
                        "ability",
                        {}
                    )
                    .get(
                        "name"
                    )
                )

                if nome_habilidade:

                    nomes_habilidades.append(
                        nome_bonito(
                            nome_habilidade
                        )
                    )

            if nomes_habilidades:

                st.write(
                    "**Habilidades:** "
                    + ", ".join(
                        nomes_habilidades
                    )
                )

        # ====================================================
        # STATUS TOTAL
        # ====================================================

        stats = dados.get(
            "stats",
            []
        )

        if stats:

            st.metric(
                "📊 Total de atributos base",
                sum(
                    x.get(
                        "base_stat",
                        0
                    )
                    for x in stats
                )
            )

        # ====================================================
        # SPRITES / IMAGEM DA FORMA
        # ====================================================

        mostrar_sprites_forma(
            forma,
            dados,
            id_api,
            nome
        )


def obter_categorias_formas(
    dados_formas
):

    categorias = [

        (
            "formas",
            "✨ Formas",
            "✨"
        ),

        (
            "formas_regionais",
            "🌎 Formas Regionais",
            "🌎"
        ),

        (
            "mega_evolucoes",
            "💥 Mega Evoluções",
            "💥"
        ),

        (
            "mega_evolucoes_z",
            "🔵 Mega Evoluções Z",
            "🔵"
        ),

        (
            "gigantamax",
            "🏰 Gigantamax",
            "🏰"
        ),

        (
            "formas_especiais",
            "⭐ Formas Especiais",
            "⭐"
        ),

        (
            "variantes",
            "🔄 Variantes",
            "🔄"
        ),

        (
            "fusoes",
            "🔗 Fusões",
            "🔗"
        ),

        (
            "transformacoes",
            "🌀 Transformações",
            "🌀"
        ),

        (
            "formas_alternativas",
            "🔁 Formas Alternativas",
            "🔁"
        ),

        # --------------------------------------------------------
        # NOVO:
        # Outras formas é usada para formas de spin-offs,
        # classificações especiais e formas que não entram
        # nas categorias tradicionais acima.
        # --------------------------------------------------------

        (
            "outras_formas",
            "🌑 Outras Formas",
            "🌑"
        )
    ]

    return [

        categoria

        for categoria in categorias

        if dados_formas.get(
            categoria[0]
        )
    ]


def mostrar_catalogo_formas(
    nome_especie,
    nome_pokemon_atual=None
):

    # Primeiro tenta a espécie-base.
    chaves_tentativa = [
        normalizar_nome(nome_especie)
    ]

    # Depois tenta o nome real do Pokémon atual.
    # Isso ajuda em formas/navegação interna.
    if nome_pokemon_atual:
        chave_atual = normalizar_nome(nome_pokemon_atual)

        if chave_atual not in chaves_tentativa:
            chaves_tentativa.append(chave_atual)

    dados_formas = {}

    for chave in chaves_tentativa:

        dados_teste = formas_pokemon.get(
            chave,
            {}
        )

        if dados_teste:
            dados_formas = dados_teste
            break

    # Garantia do Mega Floette.
    if normalizar_nome(nome_especie) == "floette":

        dados_formas = dict(dados_formas)
        lista_mega = list(
            dados_formas.get("mega_evolucoes", []) or []
        )

        if not any(
            normalizar_nome(item.get("id_api", "")) == "floette-mega"
            for item in lista_mega
        ):

            lista_mega.append({
                "nome": "Mega Floette",
                "categoria": "Mega Evolução",
                "regiao": "Kalos / Lumiose",
                "origem": "Pokémon Legends: Z-A",
                "id_api": "floette-mega"
            })

        dados_formas["mega_evolucoes"] = lista_mega

    if not dados_formas:

        st.info(
            "✨ Este Pokémon ainda não possui "
            "formas cadastradas."
        )

        return

    encontrou = False

    for chave, titulo, icone in (
        obter_categorias_formas(
            dados_formas
        )
    ):

        lista = dados_formas.get(
            chave,
            []
        )

        if not lista:

            continue

        encontrou = True

        st.subheader(
            titulo
        )

        for indice, forma in enumerate(lista):

            mostrar_forma(
                forma,
                icone,
                nome_especie
            )

            st.divider()

    if not encontrou:

        st.info(
            "✨ Este Pokémon ainda não possui "
            "formas cadastradas."
        )


# ============================================================
# REPRODUÇÃO
# ============================================================

def buscar_pokemon_egg_group(
    nome
):

    especie = buscar_especie(
        nome
    )

    if not especie:

        return []

    grupos = especie.get(
        "egg_groups",
        []
    )

    if not grupos:

        return []

    resultados = {}

    for grupo in grupos:

        nome_grupo = grupo.get(
            "name"
        )

        if not nome_grupo:

            continue

        lista = buscar_lista_pokemon_egg_group(
            nome_grupo
        )

        for pokemon_egg in lista:

            nome_pokemon = pokemon_egg.get(
                "name"
            )

            if nome_pokemon:

                resultados[
                    nome_pokemon
                ] = True

    resultados.pop(
        normalizar_nome(nome),
        None
    )

    return sorted(
        resultados.keys()
    )


def obter_egg_moves(
    pokemon
):

    movimentos = pokemon.get(
        "moves",
        []
    )

    resultados = []

    for movimento in movimentos:

        detalhes = movimento.get(
            "version_group_details",
            []
        )

        for detalhe in detalhes:

            metodo = (
                detalhe
                .get(
                    "move_learn_method",
                    {}
                )
                .get(
                    "name"
                )
            )

            if metodo == "egg":

                nome = (
                    movimento
                    .get(
                        "move",
                        {}
                    )
                    .get(
                        "name"
                    )
                )

                if nome:

                    resultados.append(
                        nome
                    )

                break

    return sorted(
        set(resultados)
    )


def mostrar_reproducao(
    pokemon,
    especie,
    nome_especie
):

    st.subheader(
        "🥚 Reprodução"
    )

    # ========================================================
    # EGG GROUPS
    # ========================================================

    st.markdown(
        "### 🥚 Egg Groups"
    )

    grupos = especie.get(
        "egg_groups",
        []
    )

    if grupos:

        st.write(
            " • ".join(
                nome_bonito(
                    grupo.get(
                        "name"
                    )
                )
                for grupo in grupos
            )
        )

    else:

        st.info(
            "Este Pokémon não possui Egg Groups."
        )

    # ========================================================
    # GÊNERO
    # ========================================================

    st.markdown(
        "### ⚥ Gênero"
    )

    gender_rate = especie.get(
        "gender_rate"
    )

    if gender_rate == -1:

        st.info(
            "⚪ Este Pokémon não possui gênero."
        )

    elif gender_rate is not None:

        femea = gender_rate * 12.5
        macho = 100 - femea

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.metric(
                "♂️ Macho",
                f"{macho:.1f}%"
            )

        with col2:

            st.metric(
                "♀️ Fêmea",
                f"{femea:.1f}%"
            )

    # ========================================================
    # CHOCAR
    # ========================================================

    st.markdown(
        "### 🐣 Chocar o ovo"
    )

    hatch_counter = especie.get(
        "hatch_counter"
    )

    if hatch_counter is not None:

        passos = hatch_counter * 255

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.metric(
                "🔄 Ciclos",
                hatch_counter
            )

        with col2:

            st.metric(
                "👣 Passos aproximados",
                f"{passos:,}".replace(
                    ",",
                    "."
                )
            )

    else:

        st.info(
            "Dados de incubação indisponíveis."
        )

    # ========================================================
    # COMPATIBILIDADE
    # ========================================================

    st.markdown(
        "### 💕 Pokémon que podem cruzar"
    )

    if gender_rate == -1:

        st.info(
            "Este Pokémon não pode cruzar normalmente."
        )

    else:

        with st.spinner(
            "🥚 Procurando Pokémon compatíveis..."
        ):

            compatibilidade = (
                buscar_pokemon_egg_group(
                    nome_especie
                )
            )

        if compatibilidade:

            st.write(
                f"Encontrados **"
                f"{len(compatibilidade)} Pokémon** "
                "nos mesmos Egg Groups."
            )

            filtro = st.text_input(
                "🔎 Filtrar Pokémon compatíveis:",
                key=f"filtro_egg_{numero}",
                placeholder="Ex.: pikachu, char..."
            ).strip().lower()

            lista = compatibilidade

            if filtro:

                lista = [

                    nome

                    for nome in lista

                    if filtro
                    in nome.lower()
                ]

            limite = 100

            for nome_compat in lista[:limite]:

                st.write(
                    f"🥚 {nome_bonito(nome_compat)}"
                )

            if len(lista) > limite:

                st.caption(
                    "Mostrando os primeiros 100 "
                    "resultados."
                )

        else:

            st.info(
                "Nenhum Pokémon compatível encontrado."
            )

    # ========================================================
    # EGG MOVES
    # ========================================================

    st.markdown(
        "### 🥊 Egg Moves"
    )

    egg_moves = obter_egg_moves(
        pokemon
    )

    if egg_moves:

        st.write(
            f"📚 Total: **{len(egg_moves)} Egg Moves**"
        )

        colunas = st.columns(
            3
        )

        for indice, movimento in enumerate(
            egg_moves
        ):

            with colunas[
                indice % 3
            ]:

                st.write(
                    f"🥊 {nome_bonito(movimento)}"
                )

    else:

        st.info(
            "Nenhum Egg Move encontrado."
        )


# ============================================================
# TREINAMENTO
# ============================================================

def calcular_exp_nivel_100(
    crescimento
):

    valores = {

        "slow": 1250000,

        "medium-slow": 1059860,

        "medium": 1000000,

        "fast": 800000,

        "erratic": 600000,

        "fluctuating": 1640000
    }

    return valores.get(
        crescimento
    )


def mostrar_treinamento(
    pokemon,
    especie
):

    st.subheader(
        "📈 Experiência e Treinamento"
    )

    exp_base = pokemon.get(
        "base_experience"
    )

    amizade = especie.get(
        "base_happiness"
    )

    catch_rate = especie.get(
        "capture_rate"
    )

    growth = (
        especie
        .get(
            "growth_rate",
            {}
        )
        .get(
            "name"
        )
    )

    exp_100 = calcular_exp_nivel_100(
        growth
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "⭐ EXP Base",
            (
                exp_base
                if exp_base is not None
                else "-"
            )
        )

        st.metric(
            "❤️ Base Friendship",
            (
                amizade
                if amizade is not None
                else "-"
            )
        )

    with col2:

        st.metric(
            "🎯 Catch Rate",
            (
                catch_rate
                if catch_rate is not None
                else "-"
            )
        )

        st.metric(
            "🏆 EXP até nível 100",
            (
                f"{exp_100:,}".replace(
                    ",",
                    "."
                )
                if exp_100 is not None
                else "-"
            )
        )

    with col3:

        st.metric(
            "📈 Growth Rate",
            (
                nome_bonito(
                    growth
                )
                if growth
                else "Desconhecido"
            )
        )

    st.divider()

    st.markdown(
        "### 📚 Guia de treinamento"
    )

    st.write(
        "**EXP Base:** experiência concedida "
        "quando este Pokémon é derrotado."
    )

    st.write(
        "**Base Friendship:** valor inicial "
        "de amizade."
    )

    st.write(
        "**Catch Rate:** valor usado pela "
        "mecânica de captura."
    )

    st.write(
        "**Growth Rate:** curva de experiência "
        "utilizada para os níveis."
    )


# ============================================================
# HISTÓRICO
# ============================================================

def descobrir_geracao_por_versao(
    versao
):

    versoes = {

        1: [
            "red",
            "blue",
            "yellow"
        ],

        2: [
            "gold",
            "silver",
            "crystal"
        ],

        3: [
            "ruby",
            "sapphire",
            "emerald",
            "firered",
            "leafgreen"
        ],

        4: [
            "diamond",
            "pearl",
            "platinum",
            "heartgold",
            "soulsilver"
        ],

        5: [
            "black",
            "white",
            "black-2",
            "white-2"
        ],

        6: [
            "x",
            "y",
            "omega-ruby",
            "alpha-sapphire"
        ],

        7: [
            "sun",
            "moon",
            "ultra-sun",
            "ultra-moon",
            "lets-go-pikachu",
            "lets-go-eevee"
        ],

        8: [
            "sword",
            "shield",
            "brilliant-diamond",
            "shining-pearl",
            "legends-arceus"
        ],

        9: [
            "scarlet",
            "violet"
        ]
    }

    for numero, lista in versoes.items():

        if versao in lista:

            return numero

    return None


def mostrar_historico(
    nome,
    especie
):

    st.subheader(
        "📖 Histórico por geração"
    )

    # ========================================================
    # GERAÇÃO DE ORIGEM
    # ========================================================

    historico = []

    geracao_origem = (
        especie
        .get(
            "generation",
            {}
        )
        .get(
            "name"
        )
    )

    if geracao_origem:

        historico.append(
            {
                "geracao":
                    nome_bonito(
                        geracao_origem
                    ),

                "evento":
                    "🆕 Pokémon introduzido "
                    "nesta geração."
            }
        )

    # ========================================================
    # ENTRADAS DA POKÉDEX
    # ========================================================

    entradas = especie.get(
        "flavor_text_entries",
        []
    )

    historico_por_geracao = {}

    for entrada in entradas:

        idioma = (
            entrada
            .get(
                "language",
                {}
            )
            .get(
                "name"
            )
        )

        if idioma != "en":

            continue

        texto = (
            entrada
            .get(
                "flavor_text",
                ""
            )
        )

        texto = limpar_texto_api(
            texto
        )

        versao = (
            entrada
            .get(
                "version",
                {}
            )
            .get(
                "name"
            )
        )

        numero_geracao = (
            descobrir_geracao_por_versao(
                versao
            )
        )

        if numero_geracao:

            historico_por_geracao.setdefault(
                numero_geracao,
                []
            )

            if texto not in (
                historico_por_geracao[
                    numero_geracao
                ]
            ):

                historico_por_geracao[
                    numero_geracao
                ].append(
                    texto
                )

    # ========================================================
    # HISTÓRICO MANUAL
    # ========================================================

    dados_manual = historico_manual.get(
        normalizar_nome(nome),
        []
    )

    if dados_manual:

        historico.extend(
            dados_manual
        )

    # ========================================================
    # MOSTRAR
    # ========================================================

    if historico:

        for evento in historico:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### 📅 "
                    f"{evento.get('geracao', 'Especial')}"
                )

                st.write(
                    evento.get(
                        "evento",
                        "Evento não informado."
                    )
                )

    else:

        st.info(
            "Nenhum evento histórico encontrado."
        )

    # ========================================================
    # ENTRADAS DA POKÉDEX
    # ========================================================

    if historico_por_geracao:

        st.divider()

        st.markdown(
            "### 📚 Entradas da Pokédex"
        )

        for numero_geracao in sorted(
            historico_por_geracao.keys()
        ):

            with st.expander(
                f"📖 Geração {numero_geracao}"
            ):

                for texto in (
                    historico_por_geracao[
                        numero_geracao
                    ][:5]
                ):

                    st.write(
                        f"📖 {texto}"
                    )


def encontrar_forma_cadastrada(id_api):
    """Procura uma forma cadastrada em qualquer espécie do JSON."""

    alvo = normalizar_nome(id_api or "")
    if not alvo:
        return None

    for dados_especie in formas_pokemon.values():
        if not isinstance(dados_especie, dict):
            continue

        for chave in (
            "formas",
            "formas_regionais",
            "mega_evolucoes",
            "mega_evolucoes_z",
            "gigantamax",
            "formas_especiais",
            "variantes",
            "fusoes",
            "transformacoes",
            "formas_alternativas",
            "outras_formas",
        ):
            for forma in dados_especie.get(chave, []) or []:
                if normalizar_nome(forma.get("id_api", "")) == alvo:
                    return forma

    return None


# ============================================================
# LISTA
# ============================================================

nomes_pokemons = list(
    index_pokemons.values()
)

opcoes = [
    "-- Selecione um Pokémon --"
] + nomes_pokemons

if "Zygarde" not in opcoes:
    opcoes.append("Zygarde")


# ============================================================
# DESCOBRIR IDENTIFICADOR
# ============================================================

def descobrir_identificador(
    selecionado
):

    for chave, valor in index_pokemons.items():

        if (
            str(valor).strip()
            ==
            str(selecionado).strip()
        ):

            return chave

    return selecionado


# ============================================================
# SELECTBOX
# ============================================================

# ------------------------------------------------------------
# Se estamos navegando para uma forma que NÃO está no
# pokemon_index.json, o selectbox continua disponível,
# mas não interfere na navegação.
# ------------------------------------------------------------

indice_padrao = 0

if (
    st.session_state.pokemon_focado is None
    and len(opcoes) > 1
):

    indice_padrao = 0


nome_selecionado = st.selectbox(
    "🔎 Escolha um Pokémon:",
    opcoes,
    index=indice_padrao,
    key="selecao_pokemon"
)


# ============================================================
# DEFINIR O IDENTIFICADOR ATUAL
# ============================================================

if st.session_state.pokemon_focado:

    # ========================================================
    # NAVEGAÇÃO INTERNA
    # ========================================================

    identificador = (
        st.session_state.pokemon_focado
    )

else:

    # ========================================================
    # SELEÇÃO NORMAL
    # ========================================================

    if nome_selecionado == (
        "-- Selecione um Pokémon --"
    ):

        st.info(
            "👆 Escolha um Pokémon para começar."
        )

        st.stop()

    identificador = descobrir_identificador(
        nome_selecionado
    )


# ============================================================
# BUSCA DO POKÉMON ATUAL
# ============================================================

with st.spinner(
    "🔎 Carregando Pokémon..."
):

    pokemon = buscar_pokemon(
        identificador
    )


# ============================================================
# FALLBACK
# ============================================================

if pokemon is None:

    if not st.session_state.pokemon_focado:

        pokemon = buscar_pokemon(
            nome_selecionado
        )


# ============================================================
# ERRO
# ============================================================

if pokemon is None:

    pokemon = dados_fallback_pokemon(identificador)

if pokemon is None:

    pokemon = buscar_pokemon(nome_selecionado)

if pokemon is None:

    st.error(
        "❌ Pokémon não encontrado: "
        f"**{identificador}**"
    )

    st.info(
        "💡 Verifique o identificador utilizado pela PokéAPI ou atualize a página."
    )

    st.stop()


# ============================================================
# DADOS
# ============================================================

numero = pokemon.get(
    "id",
    0
)

nome_pokemon = pokemon.get(
    "name",
    normalizar_nome(
        identificador
    )
)


# ============================================================
# ESPÉCIE
# ============================================================

nome_especie = (
    pokemon
    .get(
        "species",
        {}
    )
    .get(
        "name"
    )
)

if not nome_especie:

    nome_especie = nome_pokemon


especie = buscar_especie(
    nome_especie
)

if especie is None and normalizar_nome(nome_especie) == "zygarde":
    especie = {
        "name": "zygarde",
        "gender_rate": -1,
        "egg_groups": [],
        "varieties": [],
    }


forma_focada = st.session_state.get("forma_focada_dados")
dados_forma_focada = None

if forma_focada is None and st.session_state.get("forma_focada_id"):

    forma_focada = encontrar_forma_cadastrada(
        st.session_state.forma_focada_id
    )

if forma_focada:

    id_forma_focada = forma_focada.get("id_api")

    if id_forma_focada:

        dados_forma_focada = carregar_dados_forma(
            id_forma_focada
        )


# ============================================================
# AVISO DE NAVEGAÇÃO
# ============================================================

if st.session_state.pokemon_focado:

    col_nav1, col_nav2 = st.columns(
        [4, 1]
    )

    with col_nav1:

        if forma_focada:
            st.info(
                "✨ Ficha da forma: "
                f"**{forma_focada.get('nome', 'Forma especial')}**"
                "\n\n"
                "Os dados gerais abaixo continuam vinculados à espécie-base "
                "quando a fonte não possui uma ficha própria para a forma."
            )
        else:
            st.info(
                "🔗 Você navegou para "
                f"**{nome_bonito(nome_pokemon)}** "
                "através da Pokédex."
            )

    with col_nav2:

        if st.button(
            "🔙 Voltar",
            key=f"voltar_{numero}"
        ):

            voltar_para_pokemon_selecionado()


# ============================================================
# TÍTULO
# ============================================================

if forma_focada:

    st.header(
        f"#{numero:04d} "
        f"{forma_focada.get('nome', 'Forma especial')}"
    )

    st.caption(
        f"Espécie-base: {nome_bonito(nome_especie)}"
    )

else:

    st.header(
        f"#{numero:04d} "
        f"{nome_bonito(nome_pokemon)}"
    )

    if nome_especie != nome_pokemon:

        st.caption(
            f"Espécie-base: "
            f"{nome_bonito(nome_especie)}"
        )


# ============================================================
# ALTURA / PESO
# ============================================================

altura = (
    pokemon.get(
        "height",
        0
    ) / 10
)

peso = (
    pokemon.get(
        "weight",
        0
    ) / 10
)

if altura > 0:

    imc = round(
        peso / (altura ** 2),
        2
    )

else:

    imc = 0


# ============================================================
# INFORMAÇÕES PRINCIPAIS
# ============================================================

col1, col2, col3 = st.columns(
    3
)


with col1:

    if forma_focada:

        urls_forma = urls_showdown_forma(
            forma_focada.get("id_api"),
            forma_focada.get("nome")
        )

        if urls_forma.get("2d"):
            st.caption("🟦 2D específico da forma")
            st.image(urls_forma["2d"], width=420)
        else:
            st.info("🟦 2D específico desta forma indisponível.")

        if urls_forma.get("visual_3d"):
            st.caption("🎮 Render / modelo específico da forma")
            st.image(urls_forma["visual_3d"], width=420)
        else:
            st.info("🎮 Render / modelo específico desta forma indisponível.")

        if urls_forma.get("animado"):
            st.caption("🎞️ Sprite animado específico da forma")
            st.image(urls_forma["animado"], width=420)

    else:

        sprites = obter_sprites(
            pokemon
        )

        femea = eh_femea(
            pokemon
        )

        sprite_3d = (
            sprites["3d_normal_female"]
            if (
                femea
                and sprites.get(
                    "3d_normal_female"
                )
            )
            else sprites["3d_normal"]
        )

        mostrar_imagem(
            sprite_3d,
            (
                "🟩 Sprite 3D ♀️"
                if femea
                else "🟩 Sprite 3D"
            ),
            220
        )

    st.metric(
        "Altura",
        f"{altura:.1f} m"
    )


with col2:

    st.subheader(
        "🔊 Cry"
    )

    cry = pokemon.get(
        "cries",
        {}
    ).get(
        "latest"
    )

    if cry:

        st.audio(
            cry
        )

    else:

        st.info(
            "Cry indisponível."
        )

    if (
        df is not None
        and "name" in df.columns
        and "generation" in df.columns
    ):

        nomes_csv = (
            df["name"]
            .astype(str)
            .str.lower()
        )

        resultado = df[
            nomes_csv
            == nome_especie.lower()
        ]

        if not resultado.empty:

            geracao = resultado[
                "generation"
            ].iloc[0]

            st.metric(
                "Geração",
                str(geracao)
            )

    st.metric(
        "IMC",
        imc
    )


with col3:

    if forma_focada:

        st.caption("🎨 Artwork específico da forma")
        st.info(
            "O artwork da espécie-base não será usado como se fosse o artwork da forma."
        )

    else:

        artwork_principal = (
            sprites["artwork_normal_female"]
            if (
                femea
                and sprites.get(
                    "artwork_normal_female"
                )
            )
            else sprites["artwork_normal"]
        )

        mostrar_imagem(
            artwork_principal,
            (
                "🎨 Artwork Oficial ♀️"
                if femea
                else "🎨 Artwork Oficial"
            ),
            220
        )

    st.metric(
        "Peso",
        f"{peso:.1f} kg"
    )


st.divider()


# ============================================================
# EFETIVIDADE DE TIPOS
# ============================================================

@st.cache_data(ttl=3600)
def buscar_efetividade_tipo(
    tipo
):

    nome_tipo = normalizar_nome(
        tipo
    )

    url = (
        "https://pokeapi.co/api/v2/"
        f"type/{nome_tipo}"
    )

    return requisicao_api(
        url
    )


def calcular_efetividade(
    pokemon
):

    tipos = pokemon.get(
        "types",
        []
    )

    resultado = {

        "4x": [],
        "2x": [],
        "1x": [],
        "0.5x": [],
        "0.25x": [],
        "0x": []
    }

    if not tipos:

        return resultado

    todos_tipos = [

        "normal",
        "fire",
        "water",
        "electric",
        "grass",
        "ice",
        "fighting",
        "poison",
        "ground",
        "flying",
        "psychic",
        "bug",
        "rock",
        "ghost",
        "dragon",
        "dark",
        "steel",
        "fairy"
    ]

    multiplicadores = {
        tipo: 1.0
        for tipo in todos_tipos
    }

    for tipo_pokemon in tipos:

        nome_tipo = (
            tipo_pokemon
            .get(
                "type",
                {}
            )
            .get(
                "name"
            )
        )

        if not nome_tipo:

            continue

        dados_tipo = buscar_efetividade_tipo(
            nome_tipo
        )

        if not dados_tipo:

            continue

        relacoes = dados_tipo.get(
            "damage_relations",
            {}
        )

        for atacante in relacoes.get(
            "double_damage_from",
            []
        ):

            nome = atacante.get(
                "name"
            )

            if nome in multiplicadores:

                multiplicadores[
                    nome
                ] *= 2

        for atacante in relacoes.get(
            "half_damage_from",
            []
        ):

            nome = atacante.get(
                "name"
            )

            if nome in multiplicadores:

                multiplicadores[
                    nome
                ] *= 0.5

        for atacante in relacoes.get(
            "no_damage_from",
            []
        ):

            nome = atacante.get(
                "name"
            )

            if nome in multiplicadores:

                multiplicadores[
                    nome
                ] = 0

    for tipo, multiplicador in (
        multiplicadores.items()
    ):

        if multiplicador == 4:

            resultado["4x"].append(
                tipo
            )

        elif multiplicador == 2:

            resultado["2x"].append(
                tipo
            )

        elif multiplicador == 1:

            resultado["1x"].append(
                tipo
            )

        elif multiplicador == 0.5:

            resultado["0.5x"].append(
                tipo
            )

        elif multiplicador == 0.25:

            resultado["0.25x"].append(
                tipo
            )

        elif multiplicador == 0:

            resultado["0x"].append(
                tipo
            )

    return resultado


def calcular_vantagens_ofensivas(
    pokemon
):

    tipos = pokemon.get(
        "types",
        []
    )

    resultado = {

        "2x": set(),
        "0.5x": set(),
        "0x": set()
    }

    if not tipos:

        return resultado

    for tipo_pokemon in tipos:

        nome_tipo = (
            tipo_pokemon
            .get(
                "type",
                {}
            )
            .get(
                "name"
            )
        )

        if not nome_tipo:

            continue

        dados_tipo = buscar_efetividade_tipo(
            nome_tipo
        )

        if not dados_tipo:

            continue

        relacoes = dados_tipo.get(
            "damage_relations",
            {}
        )

        for alvo in relacoes.get(
            "double_damage_to",
            []
        ):

            nome = alvo.get(
                "name"
            )

            if nome:

                resultado[
                    "2x"
                ].add(
                    nome
                )

        for alvo in relacoes.get(
            "half_damage_to",
            []
        ):

            nome = alvo.get(
                "name"
            )

            if nome:

                resultado[
                    "0.5x"
                ].add(
                    nome
                )

        for alvo in relacoes.get(
            "no_damage_to",
            []
        ):

            nome = alvo.get(
                "name"
            )

            if nome:

                resultado[
                    "0x"
                ].add(
                    nome
                )

    for chave in resultado:

        resultado[
            chave
        ] = sorted(
            resultado[chave]
        )

    return resultado


def mostrar_efetividade(
    pokemon
):

    resultado = calcular_efetividade(
        pokemon
    )

    ofensiva = calcular_vantagens_ofensivas(
        pokemon
    )

    nomes_tipos = {

        "normal": "Normal",
        "fire": "Fogo",
        "water": "Água",
        "electric": "Elétrico",
        "grass": "Grama",
        "ice": "Gelo",
        "fighting": "Lutador",
        "poison": "Veneno",
        "ground": "Terrestre",
        "flying": "Voador",
        "psychic": "Psíquico",
        "bug": "Inseto",
        "rock": "Pedra",
        "ghost": "Fantasma",
        "dragon": "Dragão",
        "dark": "Sombrio",
        "steel": "Aço",
        "fairy": "Fada"
    }

    def mostrar_tipos(lista):

        if not lista:

            st.write(
                "Nenhum tipo."
            )

            return

        st.write(
            " • ".join(
                nomes_tipos.get(
                    tipo,
                    tipo.title()
                )
                for tipo in lista
            )
        )

    st.subheader(
        "⚔️ Efetividade de Tipos"
    )

    tipos_pokemon = pokemon.get(
        "types",
        []
    )

    if tipos_pokemon:

        nomes_pokemon = [
            traduzir_tipo(
                tipo["type"]["name"]
            )
            for tipo in tipos_pokemon
        ]

        st.write(
            "**Tipos do Pokémon:** "
            + " / ".join(
                nomes_pokemon
            )
        )

    st.markdown(
        "## 🗡️ Vantagens Ofensivas"
    )

    st.markdown(
        "### 💥 Super efetivo (2×)"
    )

    mostrar_tipos(
        ofensiva["2x"]
    )

    st.markdown(
        "### 🛡️ Pouco efetivo (½×)"
    )

    mostrar_tipos(
        ofensiva["0.5x"]
    )

    st.markdown(
        "### 🚫 Sem efeito (0×)"
    )

    mostrar_tipos(
        ofensiva["0x"]
    )

    st.divider()

    st.markdown(
        "## 🛡️ Defesa"
    )

    if resultado["4x"]:

        st.markdown(
            "### 🔥 4× Super Efetivo"
        )

        mostrar_tipos(
            resultado["4x"]
        )

        st.divider()

    if resultado["2x"]:

        st.markdown(
            "### 🔴 2× Super Efetivo"
        )

        mostrar_tipos(
            resultado["2x"]
        )

        st.divider()

    if resultado["1x"]:

        with st.expander(
            "⚪ 1× Dano Normal"
        ):

            mostrar_tipos(
                resultado["1x"]
            )

    if resultado["0.5x"]:

        st.markdown(
            "### 🟢 ½× Resistente"
        )

        mostrar_tipos(
            resultado["0.5x"]
        )

        st.divider()

    if resultado["0.25x"]:

        st.markdown(
            "### 🟢 ¼× Muito Resistente"
        )

        mostrar_tipos(
            resultado["0.25x"]
        )

        st.divider()

    if resultado["0x"]:

        st.markdown(
            "### ⚫ 0× Imune"
        )

        mostrar_tipos(
            resultado["0x"]
        )


# ============================================================
# ABAS
# ============================================================

(
    aba_pokedex,
    aba_tipos,
    aba_efetividade,
    aba_sprites,
    aba_status,
    aba_golpes,
    aba_locais,
    aba_habilidades,
    aba_formas,
    aba_evolucoes,
    aba_reproducao,
    aba_treinamento,
    aba_historico
) = st.tabs(
    [

        "📖 Pokedex",
        "🔥 Tipos",
        "⚔️ Efetividade",
        "📸 Sprites",
        "📊 Status",
        "🥊 Golpes",
        "🗺️ Locais",
        "🧬 Habilidades",
        "✨ Formas",
        "🔄 Evoluções",
        "🥚 Reprodução",
        "📈 Treinamento",
        "📖 Histórico"
    ]
)


# ============================================================
# POKÉDEX
# ============================================================

with aba_pokedex:

    if especie:

        entradas = especie.get(
            "flavor_text_entries",
            []
        )

        descricao = None

        for entrada in entradas:

            idioma = (
                entrada
                .get(
                    "language",
                    {}
                )
                .get(
                    "name"
                )
            )

            if idioma == "pt":

                descricao = entrada.get(
                    "flavor_text"
                )

                break

        if not descricao:

            for entrada in entradas:

                idioma = (
                    entrada
                    .get(
                        "language",
                        {}
                    )
                    .get(
                        "name"
                    )
                )

                if idioma == "en":

                    descricao = entrada.get(
                        "flavor_text"
                    )

                    break

        descricao = limpar_texto_api(
            descricao
        )

        if descricao:

            st.info(
                f"📖 {descricao}"
            )

        else:

            st.info(
                "📖 Descrição não disponível."
            )

        st.divider()

        genera = especie.get(
            "genera",
            []
        )

        categoria = "Desconhecida"

        for genero in genera:

            if (
                genero
                .get(
                    "language",
                    {}
                )
                .get(
                    "name"
                )
                == "pt"
            ):

                categoria = (
                    genero
                    .get(
                        "genus",
                        ""
                    )
                )

                break

        habitat = (
            nome_bonito(
                especie["habitat"]["name"]
            )
            if especie.get(
                "habitat"
            )
            else "Desconhecido"
        )

        cor = (
            nome_bonito(
                especie["color"]["name"]
            )
            if especie.get(
                "color"
            )
            else "Desconhecida"
        )

        col1, col2, col3 = st.columns(
            3
        )

        with col1:

            st.metric(
                "🏷️ Categoria",
                categoria
            )

            st.metric(
                "🌎 Habitat",
                habitat
            )

        with col2:

            st.metric(
                "🎨 Cor",
                cor
            )

            st.metric(
                "🎯 Catch Rate",
                especie.get(
                    "capture_rate",
                    "-"
                )
            )

        with col3:

            st.metric(
                "❤️ Base Friendship",
                especie.get(
                    "base_happiness",
                    "-"
                )
            )

            growth = (
                especie
                .get(
                    "growth_rate",
                    {}
                )
                .get(
                    "name",
                    "Desconhecido"
                )
            )

            st.metric(
                "📈 Growth Rate",
                nome_bonito(
                    growth
                )
            )


# ============================================================
# TIPOS
# ============================================================

with aba_tipos:

    st.subheader(
        "🔥 Tipos"
    )

    tipos = pokemon.get(
        "types",
        []
    )

    if tipos:

        for tipo in tipos:

            nome_tipo = (
                tipo
                .get(
                    "type",
                    {}
                )
                .get(
                    "name"
                )
            )

            st.markdown(
                f"### 🔹 "
                f"{traduzir_tipo(nome_tipo)}"
            )

    else:

        st.info(
            "Tipos não encontrados."
        )


# ============================================================
# EFETIVIDADE
# ============================================================

with aba_efetividade:

    mostrar_efetividade(
        dados_forma_focada if forma_focada and dados_forma_focada and dados_forma_focada.get("types") else pokemon
    )


# ============================================================
# SPRITES
# ============================================================

with aba_sprites:

    st.subheader(
        "📸 Galeria de Sprites"
    )

    if forma_focada:
        mostrar_sprites_forma(
            forma_focada,
            dados_forma_focada or pokemon,
            forma_focada.get("id_api"),
            forma_focada.get("nome", "Forma especial")
        )
    else:
        mostrar_sprites(
            pokemon
        )


# ============================================================
# STATUS
# ============================================================

with aba_status:

    st.subheader(
        "📊 Estatísticas Base"
    )

    stats = pokemon.get(
        "stats",
        []
    )

    nomes_stats = [

        "HP",
        "Ataque",
        "Defesa",
        "Ataque Esp.",
        "Defesa Esp.",
        "Velocidade"
    ]

    colunas = st.columns(
        6
    )

    total_status = 0

    for i, stat in enumerate(
        stats
    ):

        if i >= len(
            nomes_stats
        ):

            break

        valor = stat.get(
            "base_stat",
            0
        )

        total_status += valor

        with colunas[i]:

            st.metric(
                nomes_stats[i],
                valor
            )

            st.progress(
                min(
                    valor / 255,
                    1.0
                )
            )

    st.divider()

    st.metric(
        "📊 Total de Base Stats",
        total_status
    )


# ============================================================
# GOLPES
# ============================================================

with aba_golpes:

    st.subheader(
        "🥊 Golpes"
    )

    golpes = pokemon.get(
        "moves",
        []
    )

    st.caption(
        f"Total de golpes: {len(golpes)}"
    )

    filtro_golpes = st.text_input(
        "🔎 Filtrar golpes:",
        placeholder="Ex.: aura, thunder, punch...",
        key=f"filtro_golpes_{numero}"
    ).strip().lower()

    golpes_filtrados = []

    for movimento in golpes:

        nome_raw = (
            movimento
            .get(
                "move",
                {}
            )
            .get(
                "name",
                ""
            )
        )

        if (
            filtro_golpes
            and filtro_golpes
            not in nome_raw.lower()
        ):

            continue

        golpes_filtrados.append(
            movimento
        )

    st.write(
        f"🔍 Exibindo "
        f"**{len(golpes_filtrados)}** golpes."
    )

    for movimento in golpes_filtrados:

        nome_raw = (
            movimento
            .get(
                "move",
                {}
            )
            .get(
                "name",
                ""
            )
        )

        nome_movimento = nome_bonito(
            nome_raw
        )

        url_movimento = (
            movimento
            .get(
                "move",
                {}
            )
            .get(
                "url"
            )
        )

        metodos = obter_metodos_aprendizado(
            movimento
        )

        with st.expander(
            f"🥊 {nome_movimento}"
        ):

            dados_movimento = (
                buscar_movimento(
                    url_movimento
                )
                if url_movimento
                else None
            )

            if not dados_movimento:

                st.warning(
                    "⚠️ Não foi possível carregar "
                    "os dados completos."
                )

                continue

            tipo = (
                dados_movimento
                .get(
                    "type",
                    {}
                )
                .get(
                    "name",
                    "?"
                )
            )

            categoria = (
                dados_movimento
                .get(
                    "damage_class",
                    {}
                )
                .get(
                    "name",
                    "?"
                )
            )

            poder = dados_movimento.get(
                "power"
            )

            precisao = dados_movimento.get(
                "accuracy"
            )

            pp = dados_movimento.get(
                "pp"
            )

            prioridade = dados_movimento.get(
                "priority",
                0
            )

            chance = dados_movimento.get(
                "effect_chance"
            )

            col1, col2, col3, col4 = st.columns(
                4
            )

            with col1:

                st.metric(
                    "🎯 Tipo",
                    traduzir_tipo(
                        tipo
                    )
                )

            with col2:

                st.metric(
                    "⚔️ Categoria",
                    traduzir_categoria_golpe(
                        categoria
                    )
                )

            with col3:

                st.metric(
                    "💥 Poder",
                    (
                        poder
                        if poder is not None
                        else "-"
                    )
                )

            with col4:

                st.metric(
                    "🎯 Precisão",
                    (
                        f"{precisao}%"
                        if precisao is not None
                        else "-"
                    )
                )

            col5, col6, col7 = st.columns(
                3
            )

            with col5:

                st.metric(
                    "🔋 PP",
                    (
                        pp
                        if pp is not None
                        else "-"
                    )
                )

            with col6:

                st.metric(
                    "⚡ Prioridade",
                    prioridade
                )

            with col7:

                st.metric(
                    "🎲 Chance",
                    (
                        f"{chance}%"
                        if chance is not None
                        else "-"
                    )
                )

            st.markdown(
                "#### 📖 Descrição"
            )

            st.info(
                obter_descricao_movimento(
                    dados_movimento
                )
            )

            if metodos:

                st.markdown(
                    "#### 📚 Como aprende"
                )

                for metodo, versao in metodos:

                    if versao:

                        st.write(
                            f"• **{metodo}** — "
                            f"{versao}"
                        )

                    else:

                        st.write(
                            f"• **{metodo}**"
                        )


# ============================================================
# LOCAIS
# ============================================================

with aba_locais:

    st.subheader(
        "🗺️ Locais"
    )

    if st.button(
        "🗺️ Carregar locais",
        key=f"locais_{numero}"
    ):

        url = pokemon.get(
            "location_area_encounters"
        )

        if url:

            with st.spinner(
                "🗺️ Carregando locais..."
            ):

                locais = buscar_locais(
                    url
                )

            if locais:

                for local in locais:

                    nome_local = (
                        local
                        .get(
                            "location_area",
                            {}
                        )
                        .get(
                            "name",
                            ""
                        )
                    )

                    if nome_local:

                        st.write(
                            "🗺️ "
                            f"{nome_bonito(nome_local)}"
                        )

            else:

                st.info(
                    "Nenhum local registrado."
                )

        else:

            st.info(
                "Nenhum local registrado."
            )


# ============================================================
# HABILIDADES
# ============================================================

with aba_habilidades:

    st.subheader(
        "🧬 Habilidades"
    )

    habilidades = pokemon.get(
        "abilities",
        []
    )

    if habilidades:

        for habilidade in habilidades:

            dados_habilidade = habilidade.get(
                "ability",
                {}
            )

            nome_raw = dados_habilidade.get(
                "name",
                ""
            )

            url_habilidade = dados_habilidade.get(
                "url"
            )

            nome_habilidade = nome_bonito(
                nome_raw
            )

            oculta = habilidade.get(
                "is_hidden",
                False
            )

            rotulo = (
                "🌟 "
                if oculta
                else "🔹 "
            ) + nome_habilidade

            if oculta:

                rotulo += (
                    " — Habilidade Oculta"
                )

            with st.expander(
                rotulo
            ):

                dados_habilidade_api = (
                    buscar_habilidade(
                        url_habilidade
                    )
                    if url_habilidade
                    else None
                )

                if not dados_habilidade_api:

                    st.warning(
                        "Descrição indisponível."
                    )

                    continue

                st.markdown(
                    "#### 📝 Resumo"
                )

                st.write(
                    obter_resumo_ability(
                        dados_habilidade_api
                    )
                )

                st.markdown(
                    "#### 📖 Descrição completa"
                )

                st.info(
                    obter_descricao_ability(
                        dados_habilidade_api
                    )
                )

    else:

        st.info(
            "Nenhuma habilidade encontrada."
        )


# ============================================================
# FORMAS
# ============================================================

with aba_formas:

    st.header(
        "✨ Formas & Transformações"
    )

    st.write(
        "Todas as formas, variantes, Mega Evoluções, "
        "Gigantamax, fusões e transformações cadastradas "
        "para este Pokémon."
    )

    # --------------------------------------------------------
    # O botão original dependia do retorno momentâneo de
    # st.button(). Em Streamlit, qualquer rerun faz esse valor
    # voltar para False. Guardamos o estado para que o catálogo
    # continue aberto.
    # --------------------------------------------------------

    chave_estado_formas = (
        f"formas_carregadas_{normalizar_nome(nome_especie)}_"
        f"{numero}"
    )

    if chave_estado_formas not in st.session_state:
        st.session_state[chave_estado_formas] = False

    if st.button(
        "🔮 Carregar formas",
        key=f"formas_{numero}"
    ):

        st.session_state[chave_estado_formas] = True

    if st.session_state[chave_estado_formas]:

        with st.spinner(
            "✨ Carregando formas cadastradas..."
        ):

            mostrar_catalogo_formas(
                nome_especie,
                nome_pokemon_atual=nome_pokemon
            )


# ============================================================
# EVOLUÇÕES
# ============================================================

with aba_evolucoes:

    st.header(
        "🔄 Linha Evolutiva"
    )

    st.write(
        "Clique em qualquer Pokémon da linha evolutiva "
        "para abrir sua ficha completa."
    )

    if st.button(
        "🌳 Carregar linha evolutiva",
        key=f"evolucoes_{numero}"
    ):

        especie_evolucao = buscar_especie(
            nome_especie
        )

        if especie_evolucao is None:

            st.error(
                "❌ Não foi possível encontrar "
                f"a espécie **{nome_especie}**."
            )

        else:

            url_chain = (
                especie_evolucao
                .get(
                    "evolution_chain",
                    {}
                )
                .get(
                    "url"
                )
            )

            if not url_chain:

                st.info(
                    "Este Pokémon não possui "
                    "uma cadeia evolutiva registrada."
                )

            else:

                with st.spinner(
                    "🌳 Montando árvore evolutiva..."
                ):

                    cadeia = buscar_evolution_chain(
                        url_chain
                    )

                if cadeia:

                    mostrar_arvore_evolutiva(
                        cadeia
                    )

                else:

                    st.error(
                        "❌ Não foi possível carregar "
                        "a linha evolutiva."
                    )


# ============================================================
# REPRODUÇÃO
# ============================================================

with aba_reproducao:

    especie_reproducao = buscar_especie(
        nome_especie
    )

    if especie_reproducao:

        st.write(
            "Dados de reprodução carregados "
            "somente quando solicitado."
        )

        if st.button(
            "🥚 Carregar dados de reprodução",
            key=f"reproducao_{numero}"
        ):

            with st.spinner(
                "🥚 Carregando reprodução..."
            ):

                mostrar_reproducao(
                    pokemon,
                    especie_reproducao,
                    nome_especie
                )

    else:

        st.error(
            "❌ Não foi possível carregar "
            "os dados de reprodução."
        )


# ============================================================
# TREINAMENTO
# ============================================================

with aba_treinamento:

    especie_treinamento = buscar_especie(
        nome_especie
    )

    if especie_treinamento:

        st.write(
            "Dados de experiência e treinamento "
            "carregados sob demanda."
        )

        if st.button(
            "📈 Carregar dados de treinamento",
            key=f"treinamento_{numero}"
        ):

            with st.spinner(
                "📈 Carregando treinamento..."
            ):

                mostrar_treinamento(
                    pokemon,
                    especie_treinamento
                )

    else:

        st.error(
            "❌ Não foi possível carregar "
            "os dados de treinamento."
        )


# ============================================================
# HISTÓRICO
# ============================================================

with aba_historico:

    especie_historico = buscar_especie(
        nome_especie
    )

    if especie_historico:

        st.write(
            "Histórico baseado nos dados da espécie "
            "e no arquivo opcional "
            "`historico_pokemon.json`."
        )

        if st.button(
            "📖 Carregar histórico",
            key=f"historico_{numero}"
        ):

            with st.spinner(
                "📖 Montando histórico..."
            ):

                mostrar_historico(
                    nome_especie,
                    especie_historico
                )

    else:

        st.error(
            "❌ Não foi possível carregar "
            "o histórico deste Pokémon."
        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "⚡ Kayzac Master Pokémon • Pokémon Master Dex"
)

st.caption(
    "Dados obtidos através da PokéAPI."
)
