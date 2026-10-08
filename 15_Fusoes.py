# ============================================================
# 🧬 KAYZAC - MASTER POKEMON
# LABORATÓRIO DE FUSÕES
# ============================================================

import html
import io
import json
import random
import re
from pathlib import Path
from urllib.parse import unquote, urljoin

import pandas as pd
import requests
import streamlit as st
from PIL import Image


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="KAYZAC — Fusões",
    page_icon="🧬",
    layout="wide",
)


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_INDEX = BASE_DIR / "pokemon_index.json"
ARQUIVO_CSV = BASE_DIR / "pokemon_1.csv"
ARQUIVO_FORMAS = BASE_DIR / "formas_pokemon.json"

# Favoritos do Laboratório
ARQUIVO_FAVORITAS = BASE_DIR / "fusoes_favoritas.json"
PASTA_FAVORITAS = BASE_DIR / "assets" / "fusoes_favoritas"


# ============================================================
# FONTES
# ============================================================

POKEAPI_BASE = (
    "https://pokeapi.co/api/v2/"
)

# Fonte atual de sprites customizados.
URL_CUSTOM_OFICIAL = (
    "https://infinitefusion.net/CustomBattlers/"
)

# Fonte tradicional do catálogo Aegide.
URL_CUSTOM_GITHUB = (
    "https://raw.githubusercontent.com/"
    "Aegide/custom-fusion-sprites/"
    "main/CustomBattlers/"
)

# Cópia/proxy conhecida dos sprites.
URL_CUSTOM_BITBUCKET = (
    "https://bitbucket.org/"
    "infinitefusionsprites/customsprites/"
    "raw/main/CustomBattlers/"
)

# Autogens.
URL_AUTOGEN_GITHUB = (
    "https://raw.githubusercontent.com/"
    "Aegide/autogen-fusion-sprites/"
    "master/Battlers/"
)

# Espelho atualizado do catálogo autogen do Japeal.
URL_AUTOGEN_GITHUB_ATUALIZADO = (
    "https://raw.githubusercontent.com/"
    "Z1R343L/autogen-fusion-sprites/"
    "main/Battlers/"
)

# Proxy usado por ferramentas de cálculo de fusão.
URL_FUSIONCALC_CUSTOM = (
    "https://fusioncalc.com/"
    "wp-content/themes/twentytwentyone/"
    "pokemon/custom-fusion-sprites-main/"
    "CustomBattlers/"
)

URL_FUSIONCALC_AUTOGEN = (
    "https://fusioncalc.com/"
    "wp-content/themes/twentytwentyone/"
    "pokemon/autogen-fusion-sprites-master/"
    "Battlers/"
)


# Páginas de fallback para encontrar sprites que não estejam
# disponíveis diretamente nas fontes de PNG acima.
URL_FUSIONCALC_PAGE = (
    "https://www.fusioncalc.com/fusion/"
)

URL_FUSIONDEX_PAGE = (
    "https://www.fusiondex.org/sprite/pif/"
)

# ============================================================
# TIPOS
# ============================================================

TIPOS_PT = {
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
    "fairy": "Fada",
}


# ============================================================
# ESTILOS
# ============================================================

ESTILOS = [
    "Equilibrada",
    "Ofensiva",
    "Defensiva",
    "Velocidade",
    "Ataque Especial",
    "Caótica",
]


PREFIXOS = [
    "Mega",
    "Ultra",
    "Neo",
    "Omega",
    "Hyper",
    "Shadow",
    "Prime",
]


SUFIXOS = [
    "X",
    "Z",
    "EX",
    "Burst",
    "Nova",
    "Core",
    "GX",
]


# ============================================================
# ESTADO
# ============================================================

def inicializar_estado():
    if "fusao_atual" not in st.session_state:
        st.session_state.fusao_atual = None

    if "fusoes_historico" not in st.session_state:
        st.session_state.fusoes_historico = []

    if "fusoes_favoritas" not in st.session_state:
        st.session_state.fusoes_favoritas = carregar_favoritos()


# ============================================================
# TEXTO
# ============================================================

def normalizar_nome(nome):
    return (
        str(nome)
        .strip()
        .lower()
        .replace("_", "-")
        .replace(" ", "-")
    )


def nome_bonito(nome):
    return (
        str(nome)
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def nome_sem_acentos(texto):
    tabela = str.maketrans(
        {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
        }
    )

    resultado = (
        str(texto)
        .lower()
        .translate(tabela)
    )

    return re.sub(
        r"[^a-z0-9]",
        "",
        resultado,
    )


# ============================================================
# JSON / CSV
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def carregar_json(caminho):
    caminho = Path(caminho)

    if not caminho.exists():
        return {}

    try:
        with caminho.open(
            "r",
            encoding="utf-8",
        ) as arquivo:
            return json.load(arquivo)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {}


@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def carregar_csv(caminho):
    caminho = Path(caminho)

    if not caminho.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(
            caminho,
            dtype=str,
        )

    except (
        OSError,
        pd.errors.ParserError,
    ):
        return pd.DataFrame()


INDEX_JSON = carregar_json(
    ARQUIVO_INDEX
)

CSV_POKEMON = carregar_csv(
    ARQUIVO_CSV
)

FORMAS_JSON = carregar_json(
    ARQUIVO_FORMAS
)


# ============================================================
# CARREGAR INDEX
# ============================================================

def criar_catalogo_index(dados):
    catalogo = {}

    # Seu pokemon_index.json atual usa:
    #
    # {
    #     "1": "bulbasaur",
    #     "2": "ivysaur",
    #     ...
    # }

    if isinstance(
        dados,
        dict,
    ):

        for chave, valor in dados.items():

            if isinstance(
                valor,
                str,
            ):

                try:
                    numero = int(
                        chave
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    numero = None

                nome = valor

                catalogo[
                    normalizar_nome(nome)
                ] = {
                    "nome": nome,
                    "id": numero,
                }

    elif isinstance(
        dados,
        list,
    ):

        for item in dados:

            if isinstance(
                item,
                str,
            ):

                catalogo[
                    normalizar_nome(
                        item
                    )
                ] = {
                    "nome": item,
                    "id": None,
                }

            elif isinstance(
                item,
                dict,
            ):

                nome = (
                    item.get("name")
                    or item.get("nome")
                    or item.get("pokemon")
                )

                identificador = (
                    item.get("id")
                    or item.get("ID")
                    or item.get("dex")
                )

                if not nome:
                    continue

                try:
                    identificador = int(
                        identificador
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    identificador = None

                catalogo[
                    normalizar_nome(
                        nome
                    )
                ] = {
                    "nome": str(nome),
                    "id": identificador,
                }

    return catalogo


POKEMONS = criar_catalogo_index(
    INDEX_JSON
)


# ============================================================
# CSV COMO COMPLEMENTO
# ============================================================

def aplicar_dados_csv(
    catalogo,
    dataframe,
):
    if dataframe.empty:
        return catalogo

    colunas = {
        str(coluna).strip().lower(): coluna
        for coluna in dataframe.columns
    }

    coluna_id = (
        colunas.get("id")
        or colunas.get("pokemon_id")
        or colunas.get("dex")
    )

    coluna_nome = (
        colunas.get("name")
        or colunas.get("nome")
    )

    coluna_geracao = (
        colunas.get("generation")
        or colunas.get("geracao")
    )

    if coluna_id is None:
        return catalogo

    for _, linha in dataframe.iterrows():

        valor_id = linha.get(
            coluna_id
        )

        if (
            valor_id is None
            or pd.isna(valor_id)
        ):
            continue

        try:
            identificador = int(
                float(valor_id)
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        nome = None

        if coluna_nome:

            valor_nome = linha.get(
                coluna_nome
            )

            if (
                valor_nome is not None
                and not pd.isna(
                    valor_nome
                )
                and str(
                    valor_nome
                ).strip()
            ):
                nome = str(
                    valor_nome
                ).strip()

        chave_encontrada = None

        for chave, item in catalogo.items():

            if item.get("id") == identificador:
                chave_encontrada = chave
                break

        if nome:

            chave_nome = normalizar_nome(
                nome
            )

            if chave_encontrada:

                catalogo[
                    chave_encontrada
                ]["nome"] = nome

                catalogo[
                    chave_encontrada
                ]["id"] = identificador

                destino = catalogo[
                    chave_encontrada
                ]

            else:

                catalogo[
                    chave_nome
                ] = {
                    "nome": nome,
                    "id": identificador,
                }

                destino = catalogo[
                    chave_nome
                ]

        elif chave_encontrada:

            destino = catalogo[
                chave_encontrada
            ]

        else:

            destino = None

        if (
            destino is not None
            and coluna_geracao
        ):

            geracao = linha.get(
                coluna_geracao
            )

            if (
                geracao is not None
                and not pd.isna(
                    geracao
                )
            ):

                destino[
                    "geracao"
                ] = str(
                    geracao
                )

    return catalogo


POKEMONS = aplicar_dados_csv(
    POKEMONS,
    CSV_POKEMON,
)


# ============================================================
# FORMAS
# ============================================================

def adicionar_formas_recursivo(
    objeto,
    especie_pai=None,
    resultado=None,
):
    if resultado is None:
        resultado = []

    if isinstance(
        objeto,
        dict,
    ):

        for chave, valor in (
            objeto.items()
        ):

            chave_texto = str(
                chave
            )

            # ------------------------------------------------
            # Uma entrada direta de forma
            # ------------------------------------------------

            if (
                isinstance(
                    valor,
                    dict,
                )
                and (
                    "id_api" in valor
                    or "api_id" in valor
                )
                and (
                    "nome" in valor
                    or "name" in valor
                )
            ):

                nome = (
                    valor.get("nome")
                    or valor.get("name")
                    or chave_texto
                )

                resultado.append(
                    {
                        "nome": str(
                            nome
                        ),
                        "especie": str(
                            especie_pai
                            or chave_texto
                        ),
                        "dados": valor,
                    }
                )

                continue

            # ------------------------------------------------
            # Descobrir espécie-pai
            # ------------------------------------------------

            novo_pai = especie_pai

            if isinstance(
                valor,
                dict,
            ):

                categorias_formas = (
                    "mega_evolucoes",
                    "mega_evolucoes_z",
                    "gigantamax",
                    "formas_regionais",
                    "formas_especiais",
                    "variantes",
                    "fusoes",
                    "formas",
                )

                if any(
                    chave_forma in valor
                    for chave_forma in categorias_formas
                ):
                    novo_pai = chave_texto

                elif novo_pai is None:
                    novo_pai = chave_texto

            adicionar_formas_recursivo(
                valor,
                novo_pai,
                resultado,
            )

    elif isinstance(
        objeto,
        list,
    ):

        for item in objeto:

            adicionar_formas_recursivo(
                item,
                especie_pai,
                resultado,
            )

    return resultado


FORMAS_TEMP = (
    adicionar_formas_recursivo(
        FORMAS_JSON
    )
)


def criar_catalogo_formas(
    formas,
):
    resultado = []

    vistos = set()

    for item in formas:

        dados = item.get(
            "dados",
            {},
        )

        especie = item.get(
            "especie",
            "",
        )

        nome = item.get(
            "nome",
            "",
        )

        chave = (
            normalizar_nome(especie),
            normalizar_nome(nome),
        )

        if chave in vistos:
            continue

        vistos.add(chave)

        especie_normalizada = (
            normalizar_nome(
                especie
            )
        )

        base = POKEMONS.get(
            especie_normalizada,
            {},
        )

        id_base = base.get(
            "id"
        )

        id_api = (
            dados.get("id_api")
            or dados.get("api_id")
        )

        imagem_local = (
            dados.get("imagem")
            or dados.get("image")
            or dados.get("sprite")
            or dados.get("sprite_url")
        )

        fusion_id = (
            dados.get("fusion_id")
            or dados.get("id_fusao")
            or dados.get("id_sprite_fusao")
        )

        try:

            if fusion_id is not None:
                fusion_id = int(
                    fusion_id
                )

        except (
            TypeError,
            ValueError,
        ):

            fusion_id = None

        if fusion_id is None:
            fusion_id = id_base

        resultado.append(
            {
                "nome": str(
                    nome
                ),
                "especie": str(
                    especie
                ),
                "id_base": id_base,
                "id_api": id_api,
                "fusion_id": fusion_id,
                "imagem_local": imagem_local,
                "dados": dados,
            }
        )

    return resultado


FORMAS = criar_catalogo_formas(
    FORMAS_TEMP
)


# ============================================================
# OPÇÕES DA INTERFACE
# ============================================================

def criar_opcoes():
    opcoes = []

    # --------------------------------------------------------
    # Pokémon normais
    # --------------------------------------------------------

    for item in sorted(
        POKEMONS.values(),
        key=lambda x: (
            x.get("id")
            if x.get("id") is not None
            else 99999
        ),
    ):

        nome = item.get(
            "nome"
        )

        if not nome:
            continue

        identificador = item.get(
            "id"
        )

        if identificador is not None:

            rotulo = (
                f"#{int(identificador):03d} — "
                f"{nome_bonito(nome)}"
            )

        else:

            rotulo = nome_bonito(
                nome
            )

        opcoes.append(
            {
                "rotulo": rotulo,
                "nome": str(nome),
                "id": identificador,
                "tipo": "pokemon",
                "especie": str(nome),
            }
        )

    # --------------------------------------------------------
    # Formas
    # --------------------------------------------------------

    for forma in sorted(
        FORMAS,
        key=lambda x: (
            x.get("especie", ""),
            x.get("nome", ""),
        ),
    ):

        especie = forma.get(
            "especie"
        )

        nome = forma.get(
            "nome"
        )

        if not nome:
            continue

        identificador = forma.get(
            "id_base"
        )

        if identificador is not None:

            rotulo = (
                f"#{int(identificador):03d} — "
                f"{nome_bonito(especie)} "
                f"• {nome_bonito(nome)}"
            )

        else:

            rotulo = (
                f"FORMA — "
                f"{nome_bonito(especie)} "
                f"• {nome_bonito(nome)}"
            )

        opcoes.append(
            {
                "rotulo": rotulo,
                "nome": str(nome),
                "id": identificador,
                "tipo": "forma",
                "especie": str(
                    especie
                ),
                "forma": forma,
            }
        )

    return opcoes


OPCOES = criar_opcoes()


# ============================================================
# POKÉAPI
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def buscar_api(
    identificador,
):
    if not identificador:
        return None

    url = (
        f"{POKEAPI_BASE}"
        f"pokemon/{identificador}"
    )

    try:

        resposta = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": (
                    "KAYZAC-MASTER-POKEMON"
                )
            },
        )

        if resposta.status_code != 200:
            return None

        return resposta.json()

    except (
        requests.RequestException,
        ValueError,
    ):
        return None


# ============================================================
# IMAGEM LOCAL
# ============================================================

def tentar_imagem_local(
    caminho,
):
    if not caminho:
        return None

    caminho = Path(
        str(caminho)
    )

    candidatos = []

    if caminho.is_absolute():

        candidatos.append(
            caminho
        )

    else:

        candidatos.extend(
            [
                BASE_DIR / caminho,
                BASE_DIR / "assets" / caminho,
                BASE_DIR / "images" / caminho,
                BASE_DIR / "sprites" / caminho,
                BASE_DIR / "formas" / caminho,
            ]
        )

    for candidato in candidatos:

        if not candidato.exists():
            continue

        try:

            return Image.open(
                candidato
            ).convert(
                "RGBA"
            )

        except OSError:
            pass

    return None


# ============================================================
# BAIXAR IMAGEM REMOTA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def baixar_imagem(
    url,
):
    if not url:
        return None

    try:

        resposta = requests.get(
            url,
            timeout=4,
            headers={
                "User-Agent": (
                    "KAYZAC-MASTER-POKEMON/1.0"
                )
            },
        )

        if resposta.status_code != 200:
            return None

        if not resposta.content:
            return None

        return Image.open(
            io.BytesIO(
                resposta.content
            )
        ).convert(
            "RGBA"
        )

    except (
        requests.RequestException,
        OSError,
    ):
        return None


# ============================================================
# SPRITE NORMAL
# ============================================================

def urls_sprite_base(identificador):
    """Monta URLs diretas de fallback para um Pokémon base."""

    try:
        numero = int(identificador)
    except (TypeError, ValueError):
        return []

    return [
        (
            "PokeAPI sprite",
            "https://raw.githubusercontent.com/"
            "PokeAPI/sprites/master/sprites/pokemon/"
            f"{numero}.png",
        ),
        (
            "PokeAPI artwork",
            "https://raw.githubusercontent.com/"
            "PokeAPI/sprites/master/sprites/pokemon/"
            "other/official-artwork/"
            f"{numero}.png",
        ),
    ]


def obter_sprite_base_url(opcao):
    """Retorna uma URL direta para o sprite base quando possível."""

    if opcao["tipo"] == "forma":
        forma = opcao["forma"]

        if forma.get("imagem_local"):
            return None

        id_api = forma.get("id_api")
        urls = urls_sprite_base(id_api)

        if urls:
            return urls[0][1]

        id_base = forma.get("id_base")
        urls = urls_sprite_base(id_base)

        if urls:
            return urls[0][1]

        return None

    urls = urls_sprite_base(opcao.get("id"))

    if urls:
        return urls[0][1]

    return None


def obter_sprite_base(
    opcao,
):
    if opcao["tipo"] == "forma":

        forma = opcao["forma"]

        imagem = tentar_imagem_local(
            forma.get("imagem_local")
        )

        if imagem is not None:
            return imagem

        id_api = forma.get("id_api")

        if id_api:
            dados = buscar_api(id_api)

            if dados:
                sprites = dados.get("sprites", {})
                sprite = (
                    sprites.get("front_default")
                    or sprites.get("other", {})
                    .get("official-artwork", {})
                    .get("front_default")
                )

                if sprite:
                    imagem = baixar_imagem(sprite)
                    if imagem is not None:
                        return imagem

        id_base = forma.get("id_base")

    else:
        id_base = opcao.get("id")

    if id_base is None:
        return None

    # FALLBACK DIRETO: mesmo quando a API não responder,
    # tentamos os sprites públicos da PokeAPI pelo número da Dex.
    for _, url in urls_sprite_base(id_base):
        imagem = baixar_imagem(url)
        if imagem is not None:
            return imagem

    dados = buscar_api(id_base)

    if not dados:
        return None

    sprites = dados.get("sprites", {})
    sprite = (
        sprites.get("front_default")
        or sprites.get("other", {})
        .get("official-artwork", {})
        .get("front_default")
    )

    if not sprite:
        return None

    return baixar_imagem(sprite)


# ============================================================
# ID USADO NO SPRITE DE FUSÃO
# ============================================================

def obter_fusion_id(
    opcao,
):
    if opcao["tipo"] == "forma":

        forma = opcao[
            "forma"
        ]

        fusion_id = forma.get(
            "fusion_id"
        )

        if fusion_id is not None:

            try:
                return int(
                    fusion_id
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

        id_base = forma.get(
            "id_base"
        )

        if id_base is not None:
            return int(
                id_base
            )

    identificador = opcao.get(
        "id"
    )

    if identificador is not None:
        return int(
            identificador
        )

    return None


# ============================================================
# URLS DE FUSÃO
# ============================================================

def criar_urls_fusao(
    head_id,
    body_id,
):
    nome_arquivo = (
        f"{head_id}.{body_id}.png"
    )

    return [
        (
            "Custom oficial",
            f"{URL_CUSTOM_OFICIAL}"
            f"{nome_arquivo}",
        ),

        (
            "Custom GitHub",
            f"{URL_CUSTOM_GITHUB}"
            f"{nome_arquivo}",
        ),

        (
            "Custom Bitbucket",
            f"{URL_CUSTOM_BITBUCKET}"
            f"{nome_arquivo}",
        ),

        (
            "Custom FusionCalc",
            f"{URL_FUSIONCALC_CUSTOM}"
            f"{nome_arquivo}",
        ),

        (
            "Autogen GitHub",
            f"{URL_AUTOGEN_GITHUB}"
            f"{head_id}/"
            f"{nome_arquivo}",
        ),

        (
            "Autogen FusionCalc",
            f"{URL_FUSIONCALC_AUTOGEN}"
            f"{head_id}/"
            f"{nome_arquivo}",
        ),
    ]


# ============================================================
# LOCALIZAR SPRITE DE FUSÃO
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def extrair_sprite_de_pagina(
    pagina_url,
    head_id,
    body_id,
):
    """Procura o sprite da fusão dentro de uma página de fallback."""

    try:
        resposta = requests.get(
            pagina_url,
            timeout=8,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 KAYZAC-MASTER-POKEMON"
                )
            },
        )

        if resposta.status_code != 200:
            return None

        texto = unquote(resposta.text)

    except requests.RequestException:
        return None

    padrao_id = re.escape(f"{head_id}.{body_id}")
    candidatos = []

    padroes = [
        r'''(?:src|href|content)=["']([^"']+?\.(?:png|webp|jpg|jpeg|gif)(?:\?[^"']*)?)["']''',
        r'''https?://[^\s"'<>]+?\.(?:png|webp|jpg|jpeg|gif)(?:\?[^\s"'<>]*)?''',
    ]

    for padrao in padroes:
        for encontrado in re.findall(
            padrao,
            texto,
            flags=re.IGNORECASE,
        ):
            if isinstance(encontrado, tuple):
                encontrado = encontrado[0]

            url = str(encontrado)

            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = urljoin(
                    pagina_url,
                    url,
                )
            else:
                url = urljoin(
                    pagina_url,
                    url,
                )

            if not url.startswith("http"):
                continue

            if url not in candidatos:
                candidatos.append(url)

    # Nunca aceitar a primeira imagem da página.
    # O arquivo precisa ser exatamente algo como 1.2.png, 6.3.png etc.
    padrao_arquivo = (
        rf"^{re.escape(f'{head_id}.{body_id}')}[A-Za-z]*\.(?:png|webp|jpg|jpeg|gif)$"
    )

    sprites_reais = []

    for url in candidatos:
        nome_arquivo = (
            url.split("?", 1)[0]
            .rsplit("/", 1)[-1]
        )

        if re.fullmatch(
            padrao_arquivo,
            nome_arquivo,
            flags=re.IGNORECASE,
        ):
            sprites_reais.append(url)

    for url in sprites_reais[:30]:
        imagem = baixar_imagem(url)

        if imagem is not None:
            return {
                "imagem": imagem,
                "url": url,
                "fonte": "FusionCalc (fallback seguro)",
                "bytes": imagem_para_bytes(imagem),
                "sprite_encontrado": True,
            }

    return None


def localizar_sprite_em_fallbacks(
    head_id,
    body_id,
):
    """Procura o sprite em páginas que indexam as fusões."""

    paginas = [
        (
            "FusionCalc (fallback)",
            f"{URL_FUSIONCALC_PAGE}{head_id}.{body_id}?noReveal=1",
        ),
    ]

    for fonte, pagina in paginas:
        resultado = extrair_sprite_de_pagina(
            pagina,
            head_id,
            body_id,
        )

        if resultado is not None:
            resultado["fonte"] = fonte
            return resultado

    return None


@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def localizar_sprite_fusao(
    head_id,
    body_id,
):
    if (
        head_id is None
        or body_id is None
    ):
        return None

    urls = criar_urls_fusao(
        head_id,
        body_id,
    )

    for fonte, url in urls:

        imagem = baixar_imagem(
            url
        )

        if imagem is not None:

            return {
                "imagem": imagem,
                "url": url,
                "fonte": fonte,
                "bytes": imagem_para_bytes(
                    imagem
                ),
            }

    # --------------------------------------------------------
    # FALLBACK 2: página do FusionCalc.
    # O scraper só aceita o arquivo exato head.body, nunca
    # um banner/fundo da página.
    # --------------------------------------------------------

    fallback_pagina = localizar_sprite_em_fallbacks(
        head_id,
        body_id,
    )

    if fallback_pagina is not None:
        fallback_pagina["urls"] = urls
        return fallback_pagina

    # --------------------------------------------------------
    # Nenhum servidor respondeu ao Python.
    #
    # Mesmo assim devolvemos a primeira URL para permitir
    # carregamento pelo navegador.
    # --------------------------------------------------------

    return {
        "imagem": None,
        "url": None,
        "fonte": "Nenhum sprite encontrado",
        "bytes": None,
        "urls": urls,
        "sprite_encontrado": False,
    }


# ============================================================
# MOSTRAR IMAGEM REMOTA PELO NAVEGADOR
# ============================================================

def mostrar_imagem_remota(
    url,
    alt="Sprite",
):
    if not url:
        return

    url_segura = html.escape(
        str(url),
        quote=True,
    )

    alt_seguro = html.escape(
        str(alt),
        quote=True,
    )

    st.markdown(
        f"""
        <div style="
            width:100%;
            display:flex;
            justify-content:center;
            align-items:center;
            padding:12px;
        ">
            <img
                src="{url_segura}"
                alt="{alt_seguro}"
                style="
                    max-width:100%;
                    height:auto;
                    image-rendering:auto;
                    object-fit:contain;
                "
            >
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TIPOS
# ============================================================

def obter_tipos(
    opcao,
):
    # --------------------------------------------------------
    # Forma cadastrada localmente
    # --------------------------------------------------------

    if opcao["tipo"] == "forma":

        forma = opcao[
            "forma"
        ]

        valor = (
            forma["dados"].get(
                "tipo"
            )
            if "dados" in forma
            else None
        )

        if valor is None:

            valor = (
                forma["dados"].get(
                    "tipos"
                )
                if "dados" in forma
                else None
            )

        if isinstance(
            valor,
            str,
        ):
            valor = [
                valor
            ]

        if isinstance(
            valor,
            list,
        ):

            tipos = []

            for item in valor:

                if isinstance(
                    item,
                    str,
                ):
                    tipos.append(
                        item.lower()
                    )

                elif isinstance(
                    item,
                    dict,
                ):

                    nome_tipo = (
                        item.get(
                            "name"
                        )
                        or item.get(
                            "tipo"
                        )
                    )

                    if nome_tipo:
                        tipos.append(
                            str(
                                nome_tipo
                            ).lower()
                        )

            if tipos:
                return tipos

        # Busca a forma real pela API.
        id_api = forma.get(
            "id_api"
        )

        if id_api:

            dados = buscar_api(
                id_api
            )

            if dados:
                return [
                    item["type"]["name"]
                    for item in dados.get(
                        "types",
                        [],
                    )
                    if item.get(
                        "type"
                    )
                ]

    # --------------------------------------------------------
    # Pokémon normal
    # --------------------------------------------------------

    identificador = (
        obter_fusion_id(
            opcao
        )
    )

    dados = buscar_api(
        identificador
    )

    if not dados:
        return []

    return [
        item["type"]["name"]
        for item in dados.get(
            "types",
            [],
        )
        if item.get(
            "type"
        )
    ]


# ============================================================
# STATS
# ============================================================

def obter_stats(
    opcao,
):
    # --------------------------------------------------------
    # Forma local
    # --------------------------------------------------------

    if opcao["tipo"] == "forma":

        dados_forma = (
            opcao["forma"]["dados"]
        )

        stats = dados_forma.get(
            "stats"
        )

        if isinstance(
            stats,
            list,
        ):

            resultado = []

            for item in stats:

                if isinstance(
                    item,
                    dict,
                ):

                    valor = (
                        item.get(
                            "base_stat"
                        )
                        or item.get(
                            "base"
                        )
                        or item.get(
                            "valor"
                        )
                    )

                    if valor is not None:

                        try:
                            resultado.append(
                                int(
                                    valor
                                )
                            )
                        except (
                            TypeError,
                            ValueError,
                        ):
                            pass

            if len(
                resultado
            ) >= 6:

                return resultado[:6]

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    dados = buscar_api(
        obter_fusion_id(
            opcao
        )
    )

    if not dados:
        return [
            0,
            0,
            0,
            0,
            0,
            0,
        ]

    resultado = []

    for item in dados.get(
        "stats",
        [],
    ):

        try:

            resultado.append(
                int(
                    item.get(
                        "base_stat",
                        0,
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            resultado.append(
                0
            )

    while len(
        resultado
    ) < 6:

        resultado.append(
            0
        )

    return resultado[:6]


# ============================================================
# COMBINAR TIPOS
# ============================================================

def combinar_tipos(
    opcao_a,
    opcao_b,
):
    tipos_a = obter_tipos(
        opcao_a
    )

    tipos_b = obter_tipos(
        opcao_b
    )

    tipos = list(
        dict.fromkeys(
            tipos_a + tipos_b
        )
    )

    if len(tipos) <= 2:
        return tipos

    return random.sample(
        tipos,
        2,
    )


# ============================================================
# COMBINAR STATS
# ============================================================

def combinar_stats(
    opcao_a,
    opcao_b,
    estilo,
):
    stats_a = obter_stats(
        opcao_a
    )

    stats_b = obter_stats(
        opcao_b
    )

    resultado = [
        round(
            (
                a + b
            ) / 2
        )
        for a, b in zip(
            stats_a,
            stats_b,
        )
    ]

    if estilo == "Ofensiva":

        resultado[1] += 12
        resultado[3] += 8

    elif estilo == "Defensiva":

        resultado[2] += 12
        resultado[4] += 8

    elif estilo == "Velocidade":

        resultado[5] += 18

    elif estilo == "Ataque Especial":

        resultado[3] += 18

    elif estilo == "Caótica":

        indice = random.randrange(
            6
        )

        resultado[
            indice
        ] += random.randint(
            10,
            25,
        )

    return [
        min(
            255,
            max(
                1,
                int(valor),
            ),
        )
        for valor in resultado
    ]


# ============================================================
# NOME
# ============================================================

def criar_nome_fusao(
    nome_a,
    nome_b,
    estilo,
):
    a = nome_sem_acentos(
        nome_a
    )

    b = nome_sem_acentos(
        nome_b
    )

    corte_a = max(
        2,
        len(a) // 2,
    )

    corte_b = max(
        2,
        len(b) // 2,
    )

    nome = (
        a[:corte_a]
        + b[corte_b:]
    ).capitalize()

    if estilo == "Caótica":

        nome = (
            f"{random.choice(PREFIXOS)} "
            f"{nome}"
        )

    elif random.random() < 0.20:

        nome += random.choice(
            SUFIXOS
        )

    return nome


# ============================================================
# HABILIDADE
# ============================================================

def criar_habilidade(
    estilo,
):
    habilidades = {
        "Equilibrada": [
            "Síntese Adaptativa",
            "Dupla Aura",
            "Instinto Híbrido",
        ],
        "Ofensiva": [
            "Fúria Combinada",
            "Impacto Supremo",
            "Ruptura de Núcleo",
        ],
        "Defensiva": [
            "Carapaça Híbrida",
            "Escudo de Fusão",
            "Resiliência Dupla",
        ],
        "Velocidade": [
            "Passo Relâmpago",
            "Impulso Duplo",
            "Velocidade Sincronizada",
        ],
        "Ataque Especial": [
            "Canalização Prismática",
            "Pulso Arcano",
            "Núcleo Especial",
        ],
        "Caótica": [
            "Instabilidade Genética",
            "Caos de Núcleos",
            "Reação Selvagem",
        ],
    }

    return random.choice(
        habilidades[estilo]
    )


# ============================================================
# DESCRIÇÃO
# ============================================================

def criar_descricao(
    head,
    body,
    fonte,
):
    if fonte == "Custom oficial":
        return (
            f"Fusão customizada de "
            f"{head} + {body}."
        )

    if fonte in {
        "Custom GitHub",
        "Custom Bitbucket",
        "Custom FusionCalc",
    }:

        return (
            f"Fusão customizada de "
            f"{head} + {body}, "
            f"carregada de uma fonte "
            f"externa de sprites."
        )

    return (
        f"Fusão automática de "
        f"{head} + {body}."
    )


# ============================================================
# CRIAR DADOS DA FUSÃO
# ============================================================

def criar_dados_fusao(
    opcao_a,
    opcao_b,
    estilo,
    sprite_info,
    variante,
):
    if variante == 1:

        head = opcao_a
        body = opcao_b

    else:

        head = opcao_b
        body = opcao_a

    nome_head = head[
        "nome"
    ]

    nome_body = body[
        "nome"
    ]

    tipos = combinar_tipos(
        head,
        body,
    )

    return {
        "nome": criar_nome_fusao(
            nome_head,
            nome_body,
            estilo,
        ),
        "pokemon_a": opcao_a[
            "rotulo"
        ],
        "pokemon_b": opcao_b[
            "rotulo"
        ],
        "head": nome_head,
        "body": nome_body,
        "head_id": obter_fusion_id(
            head
        ),
        "body_id": obter_fusion_id(
            body
        ),
        "tipos": tipos,
        "tipos_pt": [
            TIPOS_PT.get(
                tipo,
                tipo.title(),
            )
            for tipo in tipos
        ],
        "estilo": estilo,
        "habilidade": criar_habilidade(
            estilo
        ),
        "stats": combinar_stats(
            head,
            body,
            estilo,
        ),
        "descricao": criar_descricao(
            nome_head,
            nome_body,
            sprite_info[
                "fonte"
            ],
        ),
        "categoria": (
            "Fusão Customizada"
            if "Custom"
            in sprite_info["fonte"]
            else "Fusão Automática"
        ),
        "fonte": sprite_info[
            "fonte"
        ],
        "url": sprite_info[
            "url"
        ],
        "imagem": sprite_info[
            "imagem"
        ],
        "bytes": sprite_info[
            "bytes"
        ],
        "sprite_encontrado": sprite_info.get(
            "sprite_encontrado",
            sprite_info.get("imagem") is not None,
        ),
        "variante": variante,
    }


# ============================================================
# GERAR FUSÕES
# ============================================================

def gerar_fusoes(
    opcao_a,
    opcao_b,
    estilo,
):
    variantes = []

    id_a = obter_fusion_id(
        opcao_a
    )

    id_b = obter_fusion_id(
        opcao_b
    )

    if (
        id_a is None
        or id_b is None
    ):
        return variantes

    # --------------------------------------------------------
    # A = CABEÇA / B = CORPO
    # --------------------------------------------------------

    sprite_ab = localizar_sprite_fusao(
        id_a,
        id_b,
    )

    if sprite_ab:

        variantes.append(
            criar_dados_fusao(
                opcao_a,
                opcao_b,
                estilo,
                sprite_ab,
                1,
            )
        )

    # --------------------------------------------------------
    # B = CABEÇA / A = CORPO
    # --------------------------------------------------------

    if id_a != id_b:

        sprite_ba = localizar_sprite_fusao(
            id_b,
            id_a,
        )

        if sprite_ba:

            variantes.append(
                criar_dados_fusao(
                    opcao_a,
                    opcao_b,
                    estilo,
                    sprite_ba,
                    2,
                )
            )

    return variantes


# ============================================================
# DOWNLOAD
# ============================================================

def imagem_para_bytes(
    imagem,
):
    buffer = io.BytesIO()

    imagem.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


# ============================================================
# HISTÓRICO
# ============================================================

def salvar_fusao(
    resultado,
):
    st.session_state.fusoes_historico.insert(
        0,
        resultado,
    )

    st.session_state.fusoes_historico = (
        st.session_state.fusoes_historico[
            :8
        ]
    )


# ============================================================
# FUSÕES FAVORITAS
# ============================================================

def chave_favorita(fusao):
    """Cria uma chave estável para identificar uma fusão favorita."""
    return (
        f"{fusao.get('head_id', 'x')}_"
        f"{fusao.get('body_id', 'x')}_"
        f"{fusao.get('variante', 'x')}"
    )


def carregar_favoritos():
    """Carrega as fusões favoritas salvas no JSON."""
    if not ARQUIVO_FAVORITAS.exists():
        return []

    try:
        with ARQUIVO_FAVORITAS.open(
            "r",
            encoding="utf-8",
        ) as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return dados

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return []


def salvar_favoritos_arquivo(favoritos):
    """Persiste as favoritas no disco."""
    try:
        ARQUIVO_FAVORITAS.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with ARQUIVO_FAVORITAS.open(
            "w",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                favoritos,
                arquivo,
                ensure_ascii=False,
                indent=4,
            )

        return True

    except OSError:
        return False


def salvar_imagem_favorita(fusao):
    """
    Guarda uma cópia PNG da imagem da fusão.
    Retorna o caminho relativo salvo ou None.
    """
    dados = fusao.get("bytes")

    if not dados:
        return None

    try:
        PASTA_FAVORITAS.mkdir(
            parents=True,
            exist_ok=True,
        )

        nome_base = nome_sem_acentos(
            str(
                fusao.get(
                    "nome",
                    "fusao",
                )
            )
        )

        nome_arquivo = (
            f"{nome_base}_"
            f"{chave_favorita(fusao)}.png"
        )

        caminho = (
            PASTA_FAVORITAS
            / nome_arquivo
        )

        caminho.write_bytes(
            dados
        )

        try:
            return str(
                caminho.relative_to(
                    BASE_DIR
                )
            )
        except ValueError:
            return str(
                caminho
            )

    except OSError:
        return None


def criar_registro_favorito(fusao):
    """Converte uma fusão em um registro seguro para o JSON."""
    arquivo_imagem = salvar_imagem_favorita(
        fusao
    )

    return {
        "chave": chave_favorita(fusao),
        "nome": fusao.get(
            "nome",
            "Fusão",
        ),
        "pokemon_a": fusao.get(
            "pokemon_a",
            "",
        ),
        "pokemon_b": fusao.get(
            "pokemon_b",
            "",
        ),
        "head": fusao.get(
            "head",
            "",
        ),
        "body": fusao.get(
            "body",
            "",
        ),
        "head_id": fusao.get(
            "head_id"
        ),
        "body_id": fusao.get(
            "body_id"
        ),
        "tipos": fusao.get(
            "tipos",
            [],
        ),
        "tipos_pt": fusao.get(
            "tipos_pt",
            [],
        ),
        "estilo": fusao.get(
            "estilo",
            "",
        ),
        "habilidade": fusao.get(
            "habilidade",
            "",
        ),
        "stats": fusao.get(
            "stats",
            [0, 0, 0, 0, 0, 0],
        ),
        "descricao": fusao.get(
            "descricao",
            "",
        ),
        "categoria": fusao.get(
            "categoria",
            "",
        ),
        "fonte": fusao.get(
            "fonte",
            "",
        ),
        "url": fusao.get(
            "url"
        ),
        "variante": fusao.get(
            "variante"
        ),
        "arquivo_imagem": arquivo_imagem,
    }


def adicionar_favorito(fusao):
    """Adiciona uma fusão aos favoritos, evitando duplicatas."""
    chave = chave_favorita(
        fusao
    )

    for item in (
        st.session_state.fusoes_favoritas
    ):
        if item.get(
            "chave"
        ) == chave:
            return False

    favorito = criar_registro_favorito(
        fusao
    )

    st.session_state.fusoes_favoritas.insert(
        0,
        favorito,
    )

    if not salvar_favoritos_arquivo(
        st.session_state.fusoes_favoritas
    ):
        st.session_state.fusoes_favoritas.pop(
            0
        )
        return False

    return True


def remover_favorito(chave):
    """Remove uma favorita e sua cópia local de imagem."""
    favoritos_novos = []

    for favorito in (
        st.session_state.fusoes_favoritas
    ):
        if favorito.get(
            "chave"
        ) != chave:
            favoritos_novos.append(
                favorito
            )
            continue

        arquivo_imagem = favorito.get(
            "arquivo_imagem"
        )

        if arquivo_imagem:
            try:
                caminho = Path(
                    arquivo_imagem
                )

                if not caminho.is_absolute():
                    caminho = (
                        BASE_DIR
                        / caminho
                    )

                if caminho.exists():
                    caminho.unlink()

            except OSError:
                pass

    st.session_state.fusoes_favoritas = (
        favoritos_novos
    )

    salvar_favoritos_arquivo(
        st.session_state.fusoes_favoritas
    )


def imagem_local_favorita(favorito):
    """Abre a cópia local da imagem de uma favorita."""
    arquivo_imagem = favorito.get(
        "arquivo_imagem"
    )

    if not arquivo_imagem:
        return None

    try:
        caminho = Path(
            arquivo_imagem
        )

        if not caminho.is_absolute():
            caminho = (
                BASE_DIR
                / caminho
            )

        if not caminho.exists():
            return None

        return Image.open(
            caminho
        ).convert(
            "RGBA"
        )

    except OSError:
        return None


def bytes_imagem_favorita(favorito):
    """Retorna os bytes da imagem favorita, quando ela está salva localmente."""
    arquivo_imagem = favorito.get(
        "arquivo_imagem"
    )

    if not arquivo_imagem:
        return None

    try:
        caminho = Path(
            arquivo_imagem
        )

        if not caminho.is_absolute():
            caminho = (
                BASE_DIR
                / caminho
            )

        if not caminho.exists():
            return None

        return caminho.read_bytes()

    except OSError:
        return None


def favorita_ja_salva(fusao):
    """Verifica se aquela variante já está entre as favoritas."""
    chave = chave_favorita(
        fusao
    )

    return any(
        item.get(
            "chave"
        ) == chave
        for item in (
            st.session_state.fusoes_favoritas
        )
    )


# ============================================================
# INICIALIZAÇÃO
# ============================================================

inicializar_estado()


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🧬 KAYZAC — LABORATÓRIO DE FUSÕES"
)

st.write(
    "Combine dois Pokémon usando o sistema "
    "de cabeça + corpo."
)

st.caption(
    "⚡ O laboratório usa o índice, CSV e "
    "formas do próprio KAYZAC."
)


# ============================================================
# STATUS DOS ARQUIVOS
# ============================================================

with st.expander(
    "🔧 Status dos arquivos do laboratório"
):

    st.write(
        "📖 pokemon_index.json:",
        "✅" if ARQUIVO_INDEX.exists()
        else "❌",
    )

    st.write(
        "📄 pokemon_1.csv:",
        "✅" if ARQUIVO_CSV.exists()
        else "❌",
    )

    st.write(
        "✨ formas_pokemon.json:",
        "✅" if ARQUIVO_FORMAS.exists()
        else "❌",
    )

    st.write(
        f"📖 Pokémon carregados: "
        f"**{len(POKEMONS)}**"
    )

    st.write(
        f"✨ Formas carregadas: "
        f"**{len(FORMAS)}**"
    )


# ============================================================
# SELEÇÃO
# ============================================================

if not OPCOES:

    st.error(
        "❌ Nenhum Pokémon foi encontrado "
        "no pokemon_index.json."
    )

    st.stop()


st.subheader(
    "🔬 Escolha os dois Pokémon"
)

rotulos = [
    item["rotulo"]
    for item in OPCOES
]


coluna_a, coluna_b = st.columns(
    2
)


with coluna_a:

    indice_a = st.selectbox(
        "🧬 Pokémon A",
        range(
            len(rotulos)
        ),
        format_func=lambda i: (
            rotulos[i]
        ),
        key="fusao_a",
    )

    opcao_a = OPCOES[
        indice_a
    ]


with coluna_b:

    indice_b = st.selectbox(
        "🧬 Pokémon B",
        range(
            len(rotulos)
        ),
        index=(
            1
            if len(rotulos) > 1
            else 0
        ),
        format_func=lambda i: (
            rotulos[i]
        ),
        key="fusao_b",
    )

    opcao_b = OPCOES[
        indice_b
    ]


# ============================================================
# INFORMAÇÃO DAS FORMAS
# ============================================================

if opcao_a["tipo"] == "forma":

    st.caption(
        f"✨ A é uma forma de "
        f"{opcao_a['especie']}."
    )


if opcao_b["tipo"] == "forma":

    st.caption(
        f"✨ B é uma forma de "
        f"{opcao_b['especie']}."
    )


# ============================================================
# ESTILO
# ============================================================

estilo = st.selectbox(
    "🎨 Estilo da fusão",
    ESTILOS,
    key="fusao_estilo",
)


st.caption(
    "💡 A + B e B + A são combinações diferentes."
)


# ============================================================
# FUSIONAR
# ============================================================

if st.button(
    "🧬 FUSIONAR!",
    use_container_width=True,
    type="primary",
):

    with st.spinner(
        "🧪 Procurando a fusão..."
    ):

        variantes = gerar_fusoes(
            opcao_a,
            opcao_b,
            estilo,
        )

    if variantes:

        resultado = {
            "pokemon_a": opcao_a[
                "rotulo"
            ],
            "pokemon_b": opcao_b[
                "rotulo"
            ],
            "estilo": estilo,
            "variantes": variantes,
        }

        st.session_state.fusao_atual = (
            resultado
        )

        salvar_fusao(
            resultado
        )

    else:

        st.session_state.fusao_atual = None

        st.warning(
            "⚠️ A combinação foi reconhecida, "
            "mas não consegui obter o sprite "
            "de fusão automaticamente."
        )

        st.info(
            "Veja abaixo as fontes candidatas "
            "para conferir se a arte existe."
        )

        id_a = obter_fusion_id(
            opcao_a
        )

        id_b = obter_fusion_id(
            opcao_b
        )

        if (
            id_a is not None
            and id_b is not None
        ):

            candidatos = criar_urls_fusao(
                id_a,
                id_b,
            )

            st.write(
                f"🔎 Cabeça: `{id_a}`"
            )

            st.write(
                f"🫀 Corpo: `{id_b}`"
            )

            for fonte, url in candidatos:

                st.markdown(
                    f"**{fonte}**"
                )

                st.link_button(
                    "🔗 Abrir sprite",
                    url,
                    use_container_width=True,
                )


# ============================================================
# RESULTADO
# ============================================================

fusao_atual = (
    st.session_state.fusao_atual
)


if fusao_atual:

    st.divider()

    st.subheader(
        "⚡ Resultado"
    )


    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.metric(
            "🧬 Pokémon A",
            fusao_atual[
                "pokemon_a"
            ],
        )


    with c2:

        st.metric(
            "🧬 Pokémon B",
            fusao_atual[
                "pokemon_b"
            ],
        )


    with c3:

        st.metric(
            "🎨 Estilo",
            fusao_atual[
                "estilo"
            ],
        )


    # ========================================================
    # ORIGINAIS
    # ========================================================

    st.markdown(
        "### 🧬 Pokémon utilizados"
    )


    orig_a, orig_b = st.columns(
        2
    )


    with orig_a:

        st.markdown(
            f"#### "
            f"{nome_bonito(opcao_a['nome'])}"
        )

        imagem_a = obter_sprite_base(
            opcao_a
        )

        if imagem_a:

            st.image(
                imagem_a,
                width=220,
            )

        else:

            url_base = obter_sprite_base_url(
                opcao_a
            )

            if url_base:
                mostrar_imagem_remota(
                    url_base,
                    f"Sprite de {opcao_a['nome']}",
                )
            else:
                st.info(
                    "Sprite normal não disponível."
                )


    with orig_b:

        st.markdown(
            f"#### "
            f"{nome_bonito(opcao_b['nome'])}"
        )

        imagem_b = obter_sprite_base(
            opcao_b
        )

        if imagem_b:

            st.image(
                imagem_b,
                width=220,
            )

        else:

            url_base = obter_sprite_base_url(
                opcao_b
            )

            if url_base:
                mostrar_imagem_remota(
                    url_base,
                    f"Sprite de {opcao_b['nome']}",
                )
            else:
                st.info(
                    "Sprite normal não disponível."
                )


    # ========================================================
    # FUSÕES
    # ========================================================

    st.divider()

    st.markdown(
        "### 🧬 Fusão encontrada"
    )


    for fusao in (
        fusao_atual[
            "variantes"
        ]
    ):

        st.markdown(
            f"## Fusão {fusao['variante']}"
        )


        # ----------------------------------------------------
        # IMAGEM
        # ----------------------------------------------------

        if fusao["imagem"] is not None:

            st.image(
                fusao["imagem"],
                width=360,
            )

        else:

            if fusao.get("sprite_encontrado", True) and fusao.get("url"):
                mostrar_imagem_remota(
                    fusao["url"],
                    fusao["nome"],
                )
            else:
                st.warning(
                    "🖼️ O sprite desta combinação não foi encontrado "
                    "nas fontes de Infinite Fusion. Nenhuma imagem genérica "
                    "será exibida no lugar da fusão."
                )


        # ----------------------------------------------------
        # DADOS
        # ----------------------------------------------------

        col_info_1, col_info_2 = (
            st.columns(2)
        )


        with col_info_1:

            st.markdown(
                f"### ⚡ "
                f"{fusao['nome']}"
            )

            st.write(
                f"**Cabeça:** "
                f"{fusao['head']}"
            )

            st.write(
                f"**Corpo:** "
                f"{fusao['body']}"
            )

            st.write(
                f"**Fonte:** "
                f"{fusao['fonte']}"
            )


        with col_info_2:

            st.write(
                f"**Categoria:** "
                f"{fusao['categoria']}"
            )

            st.write(
                f"**Tipos:** "
                f"{' / '.join(fusao['tipos_pt'])}"
            )

            st.write(
                f"**Habilidade:** "
                f"{fusao['habilidade']}"
            )


        # ----------------------------------------------------
        # DOWNLOAD + FAVORITOS
        # ----------------------------------------------------

        botao_download, botao_favorito = (
            st.columns(2)
        )

        with botao_download:

            if fusao["bytes"] is not None:

                nome_arquivo = (
                    nome_sem_acentos(
                        fusao["nome"]
                    )
                )

                st.download_button(
                    "⬇️ Baixar fusão PNG",
                    data=fusao[
                        "bytes"
                    ],
                    file_name=(
                        f"{nome_arquivo}_"
                        "fusao.png"
                    ),
                    mime="image/png",
                    use_container_width=True,
                    key=(
                        "download_"
                        f"{fusao['variante']}_"
                        f"{fusao['head_id']}_"
                        f"{fusao['body_id']}"
                    ),
                )

            else:

                url_sprite = fusao.get("url")

                if (
                    isinstance(url_sprite, str)
                    and url_sprite.startswith(("http://", "https://"))
                ):

                    st.link_button(
                        "⬇️ Abrir / baixar sprite",
                        url_sprite,
                        use_container_width=True,
                    )

                else:

                    st.info(
                        "🖼️ O sprite desta fusão não foi encontrado nas fontes disponíveis."
                    )

        with botao_favorito:

            if favorita_ja_salva(
                fusao
            ):

                st.button(
                    "⭐ Já está nas favoritas",
                    use_container_width=True,
                    disabled=True,
                    key=(
                        "favoritada_"
                        f"{fusao['variante']}_"
                        f"{fusao['head_id']}_"
                        f"{fusao['body_id']}"
                    ),
                )

            else:

                if st.button(
                    "⭐ Adicionar aos favoritos",
                    use_container_width=True,
                    key=(
                        "favoritar_"
                        f"{fusao['variante']}_"
                        f"{fusao['head_id']}_"
                        f"{fusao['body_id']}"
                    ),
                ):

                    if adicionar_favorito(
                        fusao
                    ):

                        st.success(
                            "⭐ Fusão salva nas suas favoritas!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Não foi possível salvar esta fusão."
                        )


        # ----------------------------------------------------
        # DESCRIÇÃO
        # ----------------------------------------------------

        st.write(
            f"**Descrição:** "
            f"{fusao['descricao']}"
        )


        # ----------------------------------------------------
        # STATS
        # ----------------------------------------------------

        st.markdown(
            "### 📊 Stats experimentais"
        )


        hp, atk, defesa, spatk, spdef, speed = (
            fusao["stats"]
        )


        estatisticas = {
            "❤️ HP": hp,
            "⚔️ Ataque": atk,
            "🛡️ Defesa": defesa,
            "✨ Atq. Esp.": spatk,
            "🔮 Def. Esp.": spdef,
            "💨 Velocidade": speed,
        }


        colunas_stats = st.columns(
            3
        )


        for indice, (
            nome_stat,
            valor,
        ) in enumerate(
            estatisticas.items()
        ):

            with colunas_stats[
                indice % 3
            ]:

                st.metric(
                    nome_stat,
                    valor,
                )

                st.progress(
                    min(
                        1.0,
                        valor / 255,
                    )
                )


        st.metric(
            "📈 Total de Base Stats",
            sum(
                fusao["stats"]
            ),
        )


        st.divider()


    # ========================================================
    # NOVA FUSÃO
    # ========================================================

    if st.button(
        "🔄 Fazer outra fusão",
        use_container_width=True,
    ):

        st.session_state.fusao_atual = None

        st.rerun()


# ============================================================
# HISTÓRICO
# ============================================================

st.divider()

st.subheader(
    "📚 Histórico do Laboratório"
)


if st.session_state.fusoes_historico:

    for indice, resultado in enumerate(
        st.session_state.fusoes_historico,
        start=1,
    ):

        with st.container(
            border=True
        ):

            st.markdown(
                f"### #{indice} — "
                f"{resultado['pokemon_a']} "
                "× "
                f"{resultado['pokemon_b']}"
            )

            st.caption(
                f"🎨 "
                f"{resultado['estilo']}"
            )

            for variante in (
                resultado[
                    "variantes"
                ]
            ):

                if variante["imagem"] is not None:

                    st.image(
                        variante[
                            "imagem"
                        ],
                        width=180,
                    )

                else:

                    mostrar_imagem_remota(
                        variante[
                            "url"
                        ],
                        variante[
                            "nome"
                        ],
                    )

                st.write(
                    f"**{variante['nome']}**"
                )

                st.caption(
                    f"👤 Cabeça: "
                    f"{variante['head']}"
                    " • "
                    f"🫀 Corpo: "
                    f"{variante['body']}"
                )


else:

    st.caption(
        "Suas fusões aparecerão aqui."
    )


# ============================================================
# FUSÕES FAVORITAS
# ============================================================

st.divider()

st.subheader(
    "⭐ Fusões Favoritas"
)

if not st.session_state.fusoes_favoritas:

    st.caption(
        "Você ainda não salvou nenhuma fusão. "
        "Quando encontrar uma que gostar, clique em "
        "**⭐ Adicionar aos favoritos**."
    )

else:

    st.caption(
        f"❤️ Você tem "
        f"**{len(st.session_state.fusoes_favoritas)}** "
        "fusão(ões) salva(s)."
    )

    for indice, favorito in enumerate(
        st.session_state.fusoes_favoritas,
        start=1,
    ):

        with st.container(
            border=True
        ):

            col_img, col_info = st.columns(
                [1, 2]
            )

            with col_img:

                imagem_favorita = (
                    imagem_local_favorita(
                        favorito
                    )
                )

                if imagem_favorita is not None:

                    st.image(
                        imagem_favorita,
                        width=220,
                    )

                elif favorito.get(
                    "url"
                ):

                    mostrar_imagem_remota(
                        favorito[
                            "url"
                        ],
                        favorito.get(
                            "nome",
                            "Fusão favorita",
                        ),
                    )

                else:

                    st.info(
                        "🖼️ Imagem da favorita "
                        "não disponível."
                    )

            with col_info:

                st.markdown(
                    f"### ⭐ #{indice} — "
                    f"{favorito.get('nome', 'Fusão')}"
                )

                st.write(
                    f"🧬 **{favorito.get('head', '')}** "
                    f"× "
                    f"**{favorito.get('body', '')}**"
                )

                st.write(
                    f"🎨 **Estilo:** "
                    f"{favorito.get('estilo', '-')}"
                )

                tipos_pt = favorito.get(
                    "tipos_pt",
                    [],
                )

                if tipos_pt:

                    st.write(
                        f"🔮 **Tipos:** "
                        f"{' / '.join(tipos_pt)}"
                    )

                if favorito.get(
                    "habilidade"
                ):

                    st.write(
                        f"✨ **Habilidade:** "
                        f"{favorito['habilidade']}"
                    )

                if favorito.get(
                    "descricao"
                ):

                    st.caption(
                        favorito[
                            "descricao"
                        ]
                    )

                botoes_favorito = st.columns(
                    2
                )

                with botoes_favorito[0]:

                    dados_favorita = (
                        bytes_imagem_favorita(
                            favorito
                        )
                    )

                    if dados_favorita is not None:

                        st.download_button(
                            "⬇️ Baixar favorita",
                            data=dados_favorita,
                            file_name=(
                                f"{nome_sem_acentos(favorito.get('nome', 'fusao'))}_"
                                "favorita.png"
                            ),
                            mime="image/png",
                            use_container_width=True,
                            key=(
                                "download_favorita_"
                                f"{favorito.get('chave', indice)}"
                            ),
                        )

                    elif favorito.get(
                        "url"
                    ):

                        st.link_button(
                            "⬇️ Abrir / baixar",
                            favorito[
                                "url"
                            ],
                            use_container_width=True,
                        )

                with botoes_favorito[1]:

                    if st.button(
                        "🗑️ Remover dos favoritos",
                        use_container_width=True,
                        key=(
                            "remover_favorita_"
                            f"{favorito.get('chave', indice)}"
                        ),
                    ):

                        remover_favorito(
                            favorito.get(
                                "chave"
                            )
                        )

                        st.success(
                            "🗑️ Fusão removida das favoritas."
                        )

                        st.rerun()


# ============================================================
# DESAFIOS
# ============================================================

st.divider()

st.subheader(
    "🎯 Ideias para experimentar"
)


colunas = st.columns(
    3
)


ideias = [
    (
        "🥊",
        "Dupla de combate",
        "Combine dois Pokémon conhecidos "
        "por seu poder.",
    ),
    (
        "🔥",
        "Tipos diferentes",
        "Misture Pokémon de tipos bem diferentes.",
    ),
    (
        "🧬",
        "Fusão invertida",
        "Compare A + B com B + A.",
    ),
]


for indice, (
    icone,
    titulo,
    descricao,
) in enumerate(
    ideias
):

    with colunas[indice]:

        st.markdown(
            f"### {icone} {titulo}"
        )

        st.write(
            descricao
        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "⚡ KAYZAC - MASTER POKEMON • "
    "15 — Laboratório de Fusões • "
    "⭐ Fusões Favoritas"
)