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


def navegar_para_pokemon(identificador):
    """
    Abre diretamente um Pokémon ou uma forma na ficha completa.
    """

    if identificador:

        st.session_state.pokemon_focado = (
            normalizar_nome(identificador)
        )

        st.rerun()


def voltar_para_pokemon_selecionado():

    st.session_state.pokemon_focado = None

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

@st.cache_data(ttl=3600)
def requisicao_api(url):

    try:

        resposta = requests.get(
            url,
            timeout=10
        )

        resposta.raise_for_status()

        return resposta.json()

    except requests.exceptions.RequestException:

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

        return requisicao_api(
            valor
        )

    if valor.isdigit():

        url = (
            "https://pokeapi.co/api/v2/"
            f"pokemon/{valor}"
        )

        return requisicao_api(
            url
        )

    nome = normalizar_nome(
        valor
    )

    url = (
        "https://pokeapi.co/api/v2/"
        f"pokemon/{nome}"
    )

    return requisicao_api(
        url
    )


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
    """Carrega uma forma sem substituir seus sprites pelos da espécie-base."""
    valor = str(id_api).strip()
    if not valor:
        return None

    if valor.startswith("https://pokeapi.co/"):
        dados = requisicao_api(valor)
        if dados is None:
            return None
        if "stats" not in dados and "pokemon" in dados:
            relacionado = dados.get("pokemon", {}).get("name")
            base = buscar_pokemon(relacionado) if relacionado else None
            if base:
                resultado = dict(base)
                sprites_forma = dados.get("sprites") or {}
                resultado["sprites"] = sprites_forma
                resultado["_sprites_sao_da_forma"] = bool(sprites_forma)
                resultado["_pokemon_form"] = dados
                return resultado
        return dados

    # Procuramos primeiro o registro pokemon-form. Isso evita que uma
    # forma especial seja confundida com a espécie-base.
    dados_form = buscar_pokemon_form(valor)
    if dados_form is not None:
        relacionado = dados_form.get("pokemon", {}).get("name")
        base = buscar_pokemon(relacionado) if relacionado else None
        if base:
            resultado = dict(base)
            sprites_forma = dados_form.get("sprites") or {}
            resultado["sprites"] = sprites_forma
            resultado["_sprites_sao_da_forma"] = bool(sprites_forma)
            resultado["_pokemon_form"] = dados_form
            return resultado
        if dados_form.get("sprites"):
            return {
                "name": valor,
                "sprites": dados_form.get("sprites", {}),
                "types": [],
                "abilities": [],
                "stats": [],
                "_sprites_sao_da_forma": True,
                "_pokemon_form": dados_form,
            }

    dados = buscar_pokemon(valor)
    if dados is not None:
        resultado = dict(dados)
        resultado["_sprites_sao_da_forma"] = False
        return resultado

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

def obter_sprites(pokemon):

    sprites = pokemon.get(
        "sprites",
        {}
    )

    outros = sprites.get(
        "other",
        {}
    )

    showdown = outros.get(
        "showdown",
        {}
    )

    artwork = outros.get(
        "official-artwork",
        {}
    )

    return {

        "pixel_normal":
            sprites.get(
                "front_default"
            ),

        "pixel_normal_female":
            sprites.get(
                "front_female"
            ),

        "3d_normal":
            showdown.get(
                "front_default"
            ),

        "3d_normal_female":
            showdown.get(
                "front_female"
            ),

        "artwork_normal":
            artwork.get(
                "front_default"
            ),

        "artwork_normal_female":
            artwork.get(
                "front_female"
            ),

        "pixel_shiny":
            sprites.get(
                "front_shiny"
            ),

        "pixel_shiny_female":
            sprites.get(
                "front_shiny_female"
            ),

        "3d_shiny":
            showdown.get(
                "front_shiny"
            ),

        "3d_shiny_female":
            showdown.get(
                "front_shiny_female"
            ),

        "artwork_shiny":
            artwork.get(
                "front_shiny"
            ),

        "artwork_shiny_female":
            artwork.get(
                "front_shiny"
            )
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
        or "-f" in nome
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
                and sprites.get(
                    "pixel_normal_female"
                )
                else sprites["pixel_normal"]
            ),
            (
                "🟦 Pixel 2D ♀️"
                if femea
                else "🟦 Pixel 2D"
            ),
            180
        )

    with col2:

        mostrar_imagem(
            (
                sprites["3d_normal_female"]
                if femea
                and sprites.get(
                    "3d_normal_female"
                )
                else sprites["3d_normal"]
            ),
            (
                "🟩 3D / Showdown ♀️"
                if femea
                and sprites.get(
                    "3d_normal_female"
                )
                else "🟩 3D / Showdown"
            ),
            180
        )

    with col3:

        mostrar_imagem(
            (
                sprites["artwork_normal_female"]
                if femea
                and sprites.get(
                    "artwork_normal_female"
                )
                else sprites["artwork_normal"]
            ),
            (
                "🎨 Artwork Oficial ♀️"
                if femea
                and sprites.get(
                    "artwork_normal_female"
                )
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
                and sprites.get(
                    "pixel_shiny_female"
                )
                else sprites["pixel_shiny"]
            ),
            (
                "🟦 Pixel 2D Shiny ♀️"
                if femea
                else "🟦 Pixel 2D Shiny"
            ),
            180
        )

    with col2:

        mostrar_imagem(
            (
                sprites["3d_shiny_female"]
                if femea
                and sprites.get(
                    "3d_shiny_female"
                )
                else sprites["3d_shiny"]
            ),
            (
                "🟩 3D Shiny ♀️"
                if femea
                and sprites.get(
                    "3d_shiny_female"
                )
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
# CONDIÇÕES DE EVOLUÇÃO
# ============================================================

def formatar_condicoes(
    detalhes
):

    condicoes = []

    nivel = detalhes.get(
        "min_level"
    )

    if nivel:

        condicoes.append(
            f"📈 Nível {nivel}"
        )

    item = detalhes.get(
        "item"
    )

    if item:

        condicoes.append(
            f"🪨 {nome_bonito(item['name'])}"
        )

    item_held = detalhes.get(
        "held_item"
    )

    if item_held:

        condicoes.append(
            "🎒 Segurando "
            f"{nome_bonito(item_held['name'])}"
        )

    amizade = detalhes.get(
        "min_happiness"
    )

    if amizade:

        condicoes.append(
            f"❤️ Felicidade mínima: {amizade}"
        )

    beleza = detalhes.get(
        "min_beauty"
    )

    if beleza:

        condicoes.append(
            f"✨ Beleza mínima: {beleza}"
        )

    afeicao = detalhes.get(
        "min_affection"
    )

    if afeicao:

        condicoes.append(
            f"💖 Afeição mínima: {afeicao}"
        )

    hora = detalhes.get(
        "time_of_day"
    )

    if hora == "day":

        condicoes.append(
            "☀️ Durante o dia"
        )

    elif hora == "night":

        condicoes.append(
            "🌙 Durante a noite"
        )

    elif hora:

        condicoes.append(
            f"🕐 Horário: {hora}"
        )

    if detalhes.get(
        "trade"
    ):

        condicoes.append(
            "🔄 Por troca"
        )

    genero = detalhes.get(
        "gender"
    )

    if genero == 1:

        condicoes.append(
            "♀️ Apenas fêmea"
        )

    elif genero == 2:

        condicoes.append(
            "♂️ Apenas macho"
        )

    movimento = detalhes.get(
        "known_move"
    )

    if movimento:

        condicoes.append(
            "🥊 Conhecer "
            f"{nome_bonito(movimento['name'])}"
        )

    tipo = detalhes.get(
        "known_move_type"
    )

    if tipo:

        condicoes.append(
            "🎯 Conhecer golpe do tipo "
            f"{nome_bonito(tipo['name'])}"
        )

    local = detalhes.get(
        "location"
    )

    if local:

        condicoes.append(
            "📍 Local: "
            f"{nome_bonito(local['name'])}"
        )

    if detalhes.get(
        "turn_upside_down"
    ):

        condicoes.append(
            "🙃 Subir de nível de cabeça para baixo"
        )

    if detalhes.get(
        "needs_overworld_rain"
    ):

        condicoes.append(
            "🌧️ Durante chuva no mundo aberto"
        )

    relacao = detalhes.get(
        "relative_physical_stats"
    )

    if relacao == 1:

        condicoes.append(
            "⚔️ Ataque maior que Defesa"
        )

    elif relacao == -1:

        condicoes.append(
            "🛡️ Defesa maior que Ataque"
        )

    elif relacao == 0:

        condicoes.append(
            "⚖️ Ataque e Defesa iguais"
        )

    if not condicoes:

        return [
            "✨ Condição especial ou automática"
        ]

    return condicoes


# ============================================================
# EVOLUTION CHAIN
# ============================================================

def obter_evolucoes(
    chain
):

    def construir(
        no,
        anterior=None
    ):

        especie = no.get(
            "species",
            {}
        )

        nome = especie.get(
            "name"
        )

        filhos = [

            construir(
                filho,
                nome
            )

            for filho in no.get(
                "evolves_to",
                []
            )
        ]

        return {

            "nome": nome,

            "anterior": anterior,

            "detalhes":
                no.get(
                    "evolution_details",
                    []
                ),

            "filhos": filhos
        }

    return construir(
        chain
    )


# ============================================================
# BUSCAR POKÉMON DA EVOLUTION CHAIN
# ============================================================

@st.cache_data(ttl=3600)
def buscar_pokemon_evolucao(
    nome
):

    nome_api = normalizar_nome(
        nome
    )

    pokemon = requisicao_api(
        "https://pokeapi.co/api/v2/"
        f"pokemon/{nome_api}"
    )

    if pokemon is not None:

        return pokemon

    especie_evolucao = requisicao_api(
        "https://pokeapi.co/api/v2/"
        f"pokemon-species/{nome_api}"
    )

    if especie_evolucao is not None:

        variedades = (
            especie_evolucao.get(
                "varieties",
                []
            )
        )

        for variedade in variedades:

            if variedade.get(
                "is_default",
                False
            ):

                nome_variedade = (
                    variedade
                    .get(
                        "pokemon",
                        {}
                    )
                    .get(
                        "name"
                    )
                )

                if nome_variedade:

                    pokemon = requisicao_api(
                        "https://pokeapi.co/api/v2/"
                        f"pokemon/{nome_variedade}"
                    )

                    if pokemon is not None:

                        return pokemon

        for variedade in variedades:

            nome_variedade = (
                variedade
                .get(
                    "pokemon",
                    {}
                )
                .get(
                    "name"
                )
            )

            if nome_variedade:

                pokemon = requisicao_api(
                    "https://pokeapi.co/api/v2/"
                    f"pokemon/{nome_variedade}"
                )

                if pokemon is not None:

                    return pokemon

    return buscar_pokemon(
        nome_api
    )


# ============================================================
# MOSTRAR EVOLUÇÃO
# ============================================================

def mostrar_evolucao(
    nome,
    anterior=None,
    detalhes=None,
    destaque=False
):

    if not nome:

        return

    pokemon = buscar_pokemon_evolucao(
        nome
    )

    if pokemon is None:

        st.warning(
            f"⚠️ Não foi possível carregar "
            f"{nome_bonito(nome)}."
        )

        return

    sprites = obter_sprites(
        pokemon
    )

    numero_evolucao = pokemon.get(
        "id"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        mostrar_imagem(
            sprites["artwork_normal"]
            or sprites["pixel_normal"],
            nome_bonito(nome),
            180
        )

    with col2:

        st.subheader(
            (
                "🔰 "
                if destaque
                else "🌟 "
            )
            + nome_bonito(nome)
        )

        if numero_evolucao:

            st.write(
                f"Pokédex #{numero_evolucao:04d}"
            )

        # ====================================================
        # BOTÃO PARA ABRIR FICHA
        # ====================================================

        if st.button(
            f"📖 Abrir ficha de "
            f"{nome_bonito(nome)}",
            key=(
                "abrir_evolucao_"
                f"{normalizar_nome(nome)}_"
                f"{numero_evolucao}"
            )
        ):

            navegar_para_pokemon(
                nome
            )

        tipos = pokemon.get(
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
                )
            )

        if detalhes:

            st.markdown(
                "**Como evolui:**"
            )

            condicoes = []

            for detalhe in detalhes:

                condicoes.extend(
                    formatar_condicoes(
                        detalhe
                    )
                )

            for condicao in dict.fromkeys(
                condicoes
            ):

                st.write(
                    f"- {condicao}"
                )

        else:

            st.caption(
                "✨ Forma base desta linha evolutiva."
            )


# ============================================================
# ÁRVORE EVOLUTIVA
# ============================================================

def mostrar_no_evolucao(
    no,
    raiz=False
):

    if (
        not no
        or not no.get("nome")
    ):

        return

    mostrar_evolucao(
        no["nome"],
        no.get("anterior"),
        no.get("detalhes", []),
        destaque=raiz
    )

    filhos = no.get(
        "filhos",
        []
    )

    if not filhos:

        return

    if len(filhos) == 1:

        st.markdown(
            "### ⬇️ Evolui para"
        )

        st.divider()

        mostrar_no_evolucao(
            filhos[0]
        )

        return

    st.markdown(
        "### 🌿 Ramificações"
    )

    colunas = st.columns(
        len(filhos)
    )

    for coluna, filho in zip(
        colunas,
        filhos
    ):

        with coluna:

            detalhes = filho.get(
                "detalhes",
                []
            )

            st.markdown(
                "#### ⬇️ Evolução possível"
            )

            condicoes = []

            for detalhe in detalhes:

                condicoes.extend(
                    formatar_condicoes(
                        detalhe
                    )
                )

            for condicao in dict.fromkeys(
                condicoes
            ):

                st.caption(
                    condicao
                )

            mostrar_no_evolucao(
                filho
            )


def mostrar_arvore_evolutiva(
    cadeia
):

    raiz = obter_evolucoes(
        cadeia["chain"]
    )

    st.subheader(
        "🌳 Linha Evolutiva"
    )

    st.caption(
        "Clique em qualquer Pokémon "
        "para abrir sua ficha completa."
    )

    mostrar_no_evolucao(
        raiz,
        raiz=True
    )


# ============================================================
# FORMAS
# ============================================================

def carregar_dados_forma(
    id_api
):
    """Carrega dados da forma preservando a origem dos sprites."""
    if not id_api:
        return None
    valor = str(id_api).strip()
    if not valor:
        return None
    return buscar_forma(valor)

def carregar_imagem_local(caminho):
    """
    Converte o caminho cadastrado no JSON em um caminho
    absoluto dentro do projeto.
    """
    if not caminho:
        return None

    caminho = str(caminho).strip()

    if not caminho:
        return None

    caminho_path = Path(caminho)

    if caminho_path.is_absolute():
        return caminho_path if caminho_path.exists() else None

    candidato = BASE_DIR / caminho_path

    if candidato.exists():
        return candidato

    # Compatibilidade caso o JSON use apenas o nome do arquivo.
    candidato = BASE_DIR / "imagens" / "formas" / caminho_path.name

    if candidato.exists():
        return candidato

    pasta_formas = BASE_DIR / "imagens" / "formas"

    if pasta_formas.exists():
        stem = caminho_path.stem
        for extensao in (".png", ".webp", ".jpg", ".jpeg"):
            candidato = pasta_formas / f"{stem}{extensao}"
            if candidato.exists():
                return candidato

    return None



def obter_sprites_forma(dados):
    """Retorna apenas sprites comprovadamente pertencentes à forma."""
    if not dados or not dados.get("_sprites_sao_da_forma", False):
        return {}
    return dados.get("sprites", {}) or {}


def mostrar_sprites_forma(dados, forma):
    """Mostra somente imagens específicas da forma; nunca usa a base como fallback."""
    sprites = obter_sprites_forma(dados)

    if not sprites:
        st.info(
            "🖼️ **Imagem específica desta forma indisponível.** "
            "A Pokédex não mostrará o sprite da espécie-base no lugar. "
            "Você pode adicionar uma imagem local em `imagens/formas/`."
        )
        return

    outros = sprites.get("other", {}) or {}
    showdown = outros.get("showdown", {}) or {}
    artwork = outros.get("official-artwork", {}) or {}

    pixel = sprites.get("front_default")
    pixel_shiny = sprites.get("front_shiny")
    showdown_normal = showdown.get("front_default")
    showdown_shiny = showdown.get("front_shiny")
    artwork_normal = artwork.get("front_default")
    artwork_shiny = artwork.get("front_shiny")

    st.markdown("#### 📸 Imagens específicas da forma")
    col1, col2, col3 = st.columns(3)

    with col1:
        mostrar_imagem(pixel, "🟦 Pixel 2D", 180)
    with col2:
        mostrar_imagem(showdown_normal, "🟩 3D / Showdown", 180)
    with col3:
        mostrar_imagem(artwork_normal, "🎨 Artwork Oficial", 180)

    if pixel_shiny or showdown_shiny or artwork_shiny:
        st.markdown("#### ✨ Shiny da forma")
        col1, col2, col3 = st.columns(3)
        with col1:
            mostrar_imagem(pixel_shiny, "🟦 Pixel 2D Shiny", 180)
        with col2:
            mostrar_imagem(showdown_shiny, "🟩 3D / Showdown Shiny", 180)
        with col3:
            mostrar_imagem(artwork_shiny, "🎨 Artwork Shiny", 180)

def mostrar_sprites_local_forma(forma):
    """
    Mostra uma imagem cadastrada manualmente no JSON.
    Usado para formas que não existem na PokéAPI, como
    algumas formas especiais de projetos/spin-offs.
    """
    caminho = forma.get("imagem_local")

    if not caminho:
        return False

    imagem = carregar_imagem_local(caminho)

    if imagem is None:
        st.warning(
            "⚠️ A imagem local foi cadastrada, mas não foi "
            f"encontrada: `{caminho}`"
        )
        return False

    with st.expander("📸 Ver imagem da forma"):

        st.image(
            str(imagem),
            width=300
        )

        st.caption(
            f"Imagem local: `{caminho}`"
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
    icone="✨"
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
        # PRIMEIRO: tenta carregar pela PokéAPI.
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
        # SEGUNDO: se não existir na PokéAPI, usa os dados
        # cadastrados manualmente no formas_pokemon.json.
        # --------------------------------------------------------

        if dados is None:

            dados = dados_manuais_para_forma(
                forma
            )

            # Para formas puramente locais, não mostramos
            # erro: a imagem e os dados do JSON continuam válidos.
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

        # Formas locais/spin-off podem não ter uma ficha
        # própria na PokéAPI, então o botão só aparece
        # quando existe um Pokémon real para abrir.
        if (
            dados_vieram_da_api
            and nome_pokemon_forma
            and (
                dados.get("stats")
                or dados.get("types")
            )
        ):

            chave_botao = (
                "abrir_forma_"
                f"{normalizar_nome(nome)}_"
                f"{normalizar_nome(str(id_api or 'local'))}"
            )

            if st.button(
                f"📖 Abrir ficha completa de "
                f"{nome}",
                key=chave_botao
            ):

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
        # SPRITES / IMAGEM
        # ====================================================

        imagem_local_exibida = False

        if imagem_local:
            imagem_local_exibida = mostrar_sprites_local_forma(
                forma
            )

        if not imagem_local_exibida:
            with st.expander(
                "📸 Ver imagens específicas da forma"
            ):
                mostrar_sprites_forma(
                    dados,
                    forma
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
                icone
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


# ============================================================
# LISTA
# ============================================================

nomes_pokemons = list(
    index_pokemons.values()
)

opcoes = [
    "-- Selecione um Pokémon --"
] + nomes_pokemons


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

    st.error(
        "❌ Pokémon não encontrado: "
        f"**{identificador}**"
    )

    st.info(
        "💡 Verifique o identificador "
        "utilizado pela PokéAPI."
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


# ============================================================
# AVISO DE NAVEGAÇÃO
# ============================================================

if st.session_state.pokemon_focado:

    col_nav1, col_nav2 = st.columns(
        [4, 1]
    )

    with col_nav1:

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
        pokemon
    )


# ============================================================
# SPRITES
# ============================================================

with aba_sprites:

    st.subheader(
        "📸 Galeria de Sprites"
    )

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
