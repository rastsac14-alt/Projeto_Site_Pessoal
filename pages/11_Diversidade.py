from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import streamlit as st


# ============================================================
# ⚡ KAYZAC - MASTER POKEMON
# 🌈 LABORATÓRIO DE FORMAS / DIVERSIDADE
#
# A página complementa a Pokédex:
# - não substitui as fichas completas;
# - explora formas, variantes, transformações e fusões;
# - permite comparar duas formas;
# - mostra galeria visual;
# - organiza estatísticas, tipos e outras diferenças.
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Diversidade Pokémon",
    page_icon="🌈",
    layout="wide",
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_FORMAS = BASE_DIR / "formas_pokemon.json"
ARQUIVO_FORMAS_FALLBACK = BASE_DIR / "formas_pokemon_corrigido.json"
BASE_URL = "https://pokeapi.co/api/v2"


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .diversidade-hero {
        border: 1px solid rgba(83,183,255,.35);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 16px;
        background: linear-gradient(
            135deg,
            rgba(17,140,255,.12),
            rgba(128,72,255,.08)
        );
    }

    .diversidade-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .diversidade-subtitle {
        opacity: .82;
        font-size: 1rem;
    }

    .forma-chip {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        border: 1px solid rgba(128,128,128,.35);
        border-radius: 999px;
        font-size: .82rem;
    }

    .mini-stat {
        font-size: .9rem;
        opacity: .8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MODELOS
# ============================================================

@dataclass(frozen=True)
class FormaEntry:
    base_slug: str
    base_nome: str
    categoria_chave: str
    categoria: str
    nome: str
    id_api: str
    regiao: str = ""
    origem: str = ""
    jogo: str = ""
    descricao: str = ""
    apelido: str = ""
    imagem_local: str = ""
    tipo_manual: tuple[str, ...] = ()

    @property
    def chave(self) -> str:
        return f"{self.base_slug}|{self.categoria_chave}|{self.id_api}|{self.nome}"


# ============================================================
# ESTADO
# ============================================================

if "diversidade_favoritos" not in st.session_state:
    st.session_state.diversidade_favoritos = set()


# ============================================================
# HELPERS
# ============================================================

TRADUCAO_CATEGORIAS = {
    "mega_evolucoes": "Mega Evolução",
    "mega_evolucoes_z": "Mega Evolução / Mega Z",
    "gigantamax": "Gigantamax",
    "formas_regionais": "Forma Regional",
    "formas_especiais": "Forma Especial",
    "outras_formas": "Outras Formas",
    "variantes": "Variante",
    "formas": "Forma",
    "fusoes": "Fusão",
    "transformacoes": "Transformação",
}


def bonito(texto: Any) -> str:
    valor = str(texto or "")
    valor = valor.replace("-", " ").replace("_", " ")
    return valor.strip().title()


def normalizar(texto: Any) -> str:
    return (
        str(texto or "")
        .strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def categoria_legivel(chave: str) -> str:
    return TRADUCAO_CATEGORIAS.get(chave, bonito(chave))


def buscar_primeiro_campo(dados: dict[str, Any], *campos: str) -> str:
    for campo in campos:
        valor = dados.get(campo)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
    return ""


@st.cache_data(ttl=86400, show_spinner=False)
def api_get(url_or_endpoint: str) -> dict[str, Any] | None:
    url = url_or_endpoint
    if not url.startswith("http"):
        url = f"{BASE_URL}/{url.lstrip('/')}"

    try:
        resposta = requests.get(
            url,
            timeout=12,
            headers={"User-Agent": "KAYZAC-Master-Pokemon/1.0"},
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None
    except ValueError:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def carregar_numeracao_pokedex() -> dict[str, int]:
    """
    Carrega a numeração nacional da Pokédex em uma única requisição.
    Isso permite alternar entre ordem alfabética e numérica sem fazer
    centenas de chamadas individuais à PokéAPI.
    """
    dados = api_get("pokemon?limit=2000&offset=0")
    if not dados:
        return {}

    numeros: dict[str, int] = {}

    for item in dados.get("results", []):
        nome = normalizar(item.get("name", ""))
        url = str(item.get("url", ""))

        try:
            numero = int(url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            continue

        if nome:
            numeros[nome] = numero

    return numeros


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_pokemon(slug: str) -> dict[str, Any] | None:
    return api_get(f"pokemon/{normalizar(slug)}")


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_pokemon_form(slug: str) -> dict[str, Any] | None:
    return api_get(f"pokemon-form/{normalizar(slug)}")


@st.cache_data(ttl=86400, show_spinner=False)
def obter_dados_forma(slug: str) -> dict[str, Any] | None:
    """
    Resolve primeiro /pokemon/, depois /pokemon-form/.
    Isso ajuda com formas que são identificadas de maneiras diferentes na API.
    """
    dados = buscar_pokemon(slug)
    if dados:
        return dados

    dados_form = buscar_pokemon_form(slug)
    if not dados_form:
        return None

    pokemon_relacionado = (
        dados_form.get("pokemon", {}) or {}
    ).get("name")

    if pokemon_relacionado:
        return buscar_pokemon(pokemon_relacionado)

    return None


def url_imagem_por_id(numero: int, artwork: bool = True) -> str:
    if artwork:
        return (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/other/official-artwork/{numero}.png"
        )
    return (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        f"sprites/pokemon/{numero}.png"
    )


def extrair_imagem_api(dados: dict[str, Any] | None) -> str | None:
    if not dados:
        return None

    sprites = dados.get("sprites", {}) or {}
    outros = sprites.get("other", {}) or {}
    artwork = outros.get("official-artwork", {}) or {}
    showdown = outros.get("showdown", {}) or {}

    return (
        artwork.get("front_default")
        or showdown.get("front_default")
        or sprites.get("front_default")
    )


def resolver_imagem(forma: FormaEntry) -> str | None:
    # Formas especiais do projeto podem apontar para imagens locais.
    if forma.imagem_local:
        candidatos = [
            BASE_DIR / forma.imagem_local,
            BASE_DIR.parent / forma.imagem_local,
        ]
        for caminho in candidatos:
            if caminho.exists():
                return str(caminho)

    dados = obter_dados_forma(forma.id_api)
    imagem = extrair_imagem_api(dados)
    if imagem:
        return imagem

    return None


def nome_exibicao_forma(forma: FormaEntry) -> str:
    return forma.nome or bonito(forma.id_api)


def slug_para_pokedex(slug: str) -> str:
    aliases = {
        "sirfetchd": "sirfetchd",
        "mr-mime": "mr-mime",
        "porygon-z": "porygon-z",
        "ursaluna-bloodmoon": "ursaluna-bloodmoon",
        "bloodmoon-ursaluna": "ursaluna-bloodmoon",
    }
    return aliases.get(normalizar(slug), normalizar(slug))


def abrir_na_pokedex(slug: str) -> None:
    st.session_state["pokemon_focado"] = slug_para_pokedex(slug)
    try:
        st.switch_page("pages/1_Pokedex.py")
    except Exception:
        st.info(
            "📖 A Pokédex não pôde ser aberta automaticamente. "
            "Use o menu lateral para abrir a Pokédex."
        )


def toggle_favorito(chave: str) -> None:
    favoritos = st.session_state.diversidade_favoritos
    if chave in favoritos:
        favoritos.remove(chave)
    else:
        favoritos.add(chave)


# ============================================================
# CARREGAR JSON
# ============================================================

def carregar_catalogo_formas() -> dict[str, Any]:
    caminhos = [ARQUIVO_FORMAS, ARQUIVO_FORMAS_FALLBACK]

    for caminho in caminhos:
        if not caminho.exists():
            continue
        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, dict):
                return dados
        except (OSError, json.JSONDecodeError):
            continue

    return {}


catalogo_bruto = carregar_catalogo_formas()


# ============================================================
# NORMALIZAR CATÁLOGO
# ============================================================

# Não usamos st.cache_data aqui porque o retorno contém instâncias
# de FormaEntry, uma classe definida nesta página. Em páginas do
# Streamlit isso pode causar falha de serialização do cache (pickle).
def normalizar_catalogo_json(catalogo_serializado: str) -> list[FormaEntry]:
    catalogo = json.loads(catalogo_serializado)
    entradas: list[FormaEntry] = []

    for base_slug, dados_base in catalogo.items():
        if not isinstance(dados_base, dict):
            continue

        base_nome = bonito(base_slug)

        for categoria_chave, lista in dados_base.items():
            if not isinstance(lista, list):
                continue

            for item in lista:
                if not isinstance(item, dict):
                    continue

                id_api = buscar_primeiro_campo(item, "id_api", "slug", "id")
                nome = buscar_primeiro_campo(item, "nome", "name") or bonito(id_api)

                if not id_api:
                    # Alguns blocos especiais podem ter apenas um nome.
                    id_api = normalizar(nome)

                tipo_manual = item.get("tipo", [])
                if isinstance(tipo_manual, str):
                    tipo_manual = (tipo_manual,)
                elif isinstance(tipo_manual, list):
                    tipo_manual = tuple(str(x) for x in tipo_manual)
                else:
                    tipo_manual = ()

                entradas.append(
                    FormaEntry(
                        base_slug=normalizar(base_slug),
                        base_nome=base_nome,
                        categoria_chave=categoria_chave,
                        categoria=categoria_legivel(categoria_chave),
                        nome=nome,
                        id_api=id_api,
                        regiao=buscar_primeiro_campo(item, "regiao", "região"),
                        origem=buscar_primeiro_campo(item, "origem"),
                        jogo=buscar_primeiro_campo(item, "jogo", "jogos"),
                        descricao=buscar_primeiro_campo(item, "descricao", "descrição"),
                        apelido=buscar_primeiro_campo(item, "apelido"),
                        imagem_local=buscar_primeiro_campo(item, "imagem_local"),
                        tipo_manual=tipo_manual,
                    )
                )

    return entradas


formas = normalizar_catalogo_json(json.dumps(catalogo_bruto, ensure_ascii=False, sort_keys=True))


# ============================================================
# DADOS DERIVADOS
# ============================================================

FORMAS_POR_CHAVE: dict[str, list[FormaEntry]] = {}
for forma in formas:
    FORMAS_POR_CHAVE.setdefault(forma.base_slug, []).append(forma)


BASES_DISPONIVEIS = sorted(
    {forma.base_slug for forma in formas},
    key=lambda x: bonito(x).lower(),
)


def ordenar_bases(bases: list[str], modo: str) -> list[str]:
    """Ordena Pokémon-base alfabeticamente ou pela Pokédex Nacional."""
    if modo == "🔢 Numérica (Pokédex)":
        numeros = carregar_numeracao_pokedex()
        return sorted(
            bases,
            key=lambda slug: (
                numeros.get(normalizar(slug), 99999),
                bonito(slug).lower(),
            ),
        )

    return sorted(
        bases,
        key=lambda slug: bonito(slug).lower(),
    )


def rotulo_base_pokedex(slug: str, modo: str) -> str:
    """Cria o texto exibido no seletor de Pokémon-base."""
    nome = bonito(slug)

    if modo != "🔢 Numérica (Pokédex)":
        return nome

    numero = carregar_numeracao_pokedex().get(normalizar(slug))
    if numero is None:
        return f"#??? {nome}"

    return f"#{numero:03d} {nome}"


CATEGORIAS_DISPONIVEIS = [
    "Todas",
    *sorted({forma.categoria for forma in formas}, key=str.lower),
]

REGIOES_DISPONIVEIS = [
    "Todas",
    *sorted(
        {forma.regiao for forma in formas if forma.regiao},
        key=str.lower,
    ),
]


# ============================================================
# FUNÇÕES DE DADOS DA FORMA
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def dados_resumo_forma(slug: str) -> dict[str, Any]:
    dados = obter_dados_forma(slug)
    if not dados:
        return {}

    tipos = [
        bonito(x.get("type", {}).get("name"))
        for x in dados.get("types", [])
        if x.get("type", {}).get("name")
    ]

    habilidades = [
        bonito(x.get("ability", {}).get("name"))
        for x in dados.get("abilities", [])
        if x.get("ability", {}).get("name")
    ]

    stats = {
        x.get("stat", {}).get("name", ""): x.get("base_stat", 0)
        for x in dados.get("stats", [])
    }

    return {
        "nome_api": dados.get("name", slug),
        "tipos": tipos,
        "habilidades": habilidades,
        "stats": stats,
        "total": sum(stats.values()),
        "imagem": extrair_imagem_api(dados),
        "id": dados.get("id"),
    }


def stat_total_formatado(stats: dict[str, int]) -> str:
    ordem = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    valores = [int(stats.get(chave, 0)) for chave in ordem]
    return f"HP {valores[0]} · ATK {valores[1]} · DEF {valores[2]} · SPA {valores[3]} · SPD {valores[4]} · SPE {valores[5]}"


def render_chips(valores: list[str]) -> None:
    if not valores:
        return
    html = "".join(f'<span class="forma-chip">{valor}</span>' for valor in valores)
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# CARD
# ============================================================

def card_forma(forma: FormaEntry, prefixo: str, mostrar_stats: bool = True) -> None:
    dados = dados_resumo_forma(forma.id_api)
    imagem = resolver_imagem(forma)
    favorito = forma.chave in st.session_state.diversidade_favoritos

    with st.container(border=True):
        col_img, col_info = st.columns([1.15, 2.85])

        with col_img:
            if imagem:
                st.image(imagem, use_container_width=True)
            else:
                st.info("🖼️ Imagem indisponível")

            label_fav = "⭐ Favorito" if favorito else "☆ Favoritar"
            if st.button(
                label_fav,
                key=f"{prefixo}_fav_{forma.chave}",
                use_container_width=True,
            ):
                toggle_favorito(forma.chave)
                st.rerun()

        with col_info:
            st.markdown(f"### {forma.nome}")
            st.caption(
                f"🐾 {forma.base_nome} · 🌈 {forma.categoria}"
            )

            if forma.regiao:
                st.write(f"🌎 **Região:** {forma.regiao}")
            if forma.origem:
                st.write(f"🧭 **Origem:** {forma.origem}")
            if forma.jogo:
                st.write(f"🎮 **Jogo:** {forma.jogo}")
            if forma.apelido:
                st.write(f"🏷️ **Apelido:** {forma.apelido}")

            if forma.tipo_manual:
                st.markdown("**Tipos registrados no catálogo:**")
                render_chips(list(forma.tipo_manual))

            if dados:
                if dados.get("tipos"):
                    st.markdown("**Tipos na PokéAPI:**")
                    render_chips(dados["tipos"])

                if mostrar_stats and dados.get("stats"):
                    st.caption(stat_total_formatado(dados["stats"]))
                    st.progress(min(dados["total"] / 720, 1.0))

            if forma.descricao:
                st.write(forma.descricao)

        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "📖 Abrir na Pokédex",
                key=f"{prefixo}_dex_{forma.chave}",
                use_container_width=True,
            ):
                abrir_na_pokedex(forma.id_api)
        with c2:
            with st.expander("⚙️ Detalhes técnicos"):
                st.write(f"**Slug:** `{forma.id_api}`")
                if dados.get("habilidades"):
                    st.write("**Habilidades:** " + ", ".join(dados["habilidades"]))
                if dados.get("stats"):
                    st.json(dados["stats"])


# ============================================================
# LINHA DE TRANSFORMAÇÃO
# ============================================================

def render_relacao_base(forma: FormaEntry) -> None:
    st.markdown("### 🔗 Relação com a espécie-base")

    base = FormaEntry(
        base_slug=forma.base_slug,
        base_nome=forma.base_nome,
        categoria_chave="base",
        categoria="Espécie-base",
        nome=forma.base_nome,
        id_api=forma.base_slug,
    )

    col1, col2, col3 = st.columns([1, .25, 1])
    with col1:
        imagem_base = resolver_imagem(base)
        if imagem_base:
            st.image(imagem_base, width=230)
        st.markdown(f"**{forma.base_nome}**")
    with col2:
        st.markdown("## →")
    with col3:
        imagem_forma = resolver_imagem(forma)
        if imagem_forma:
            st.image(imagem_forma, width=230)
        st.markdown(f"**{forma.nome}**")

    st.caption(
        "A página visualiza a relação entre a espécie-base e a forma/variante registrada no catálogo."
    )


# ============================================================
# CAPA
# ============================================================

st.markdown(
    """
    <div class="diversidade-hero">
        <div class="diversidade-title">🌈 KAYZAC • DIVERSIDADE POKÉMON</div>
        <div class="diversidade-subtitle">
            O laboratório de formas do KAYZAC — compare Mega Evoluções, formas regionais,
            Gigantamax, variantes, fusões, transformações e outras mudanças sem duplicar a ficha da Pokédex.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not formas:
    st.error(
        "❌ Nenhuma forma foi carregada. Verifique se `formas_pokemon.json` "
        "está na pasta principal do projeto."
    )
    st.stop()


# ============================================================
# RESUMO
# ============================================================

total_formas = len(formas)
total_bases = len(BASES_DISPONIVEIS)
total_categorias = len(CATEGORIAS_DISPONIVEIS) - 1
favoritos = len(st.session_state.diversidade_favoritos)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🐾 Espécies-base", total_bases)
c2.metric("🌈 Formas catalogadas", total_formas)
c3.metric("🧩 Categorias", total_categorias)
c4.metric("⭐ Favoritos", favoritos)


# ============================================================
# TABS
# ============================================================

tab_explorar, tab_comparar, tab_galeria, tab_relacoes, tab_favoritos = st.tabs(
    [
        "🔬 Explorar",
        "⚖️ Comparar",
        "🖼️ Galeria",
        "🔗 Transformações",
        "⭐ Meus Favoritos",
    ]
)


# ============================================================
# 🔬 EXPLORAR
# ============================================================

with tab_explorar:
    st.markdown("## 🔬 Explorador de formas")
    st.write(
        "Selecione uma espécie-base e filtre pelas diferentes maneiras pelas quais ela pode aparecer, "
        "mudar ou receber uma forma registrada no KAYZAC."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        modo_ordem = st.selectbox(
            "📚 Ordem da consulta",
            [
                "🔤 Alfabética (A–Z)",
                "🔢 Numérica (Pokédex)",
            ],
            key="diversidade_ordem_bases",
        )

    bases_ordenadas = ordenar_bases(BASES_DISPONIVEIS, modo_ordem)

    with col2:
        especie_escolhida = st.selectbox(
            "🐾 Pokémon-base",
            bases_ordenadas,
            format_func=lambda slug: rotulo_base_pokedex(slug, modo_ordem),
            key="diversidade_especie",
        )

    with col3:
        categoria_escolhida = st.selectbox(
            "🌈 Categoria",
            CATEGORIAS_DISPONIVEIS,
            key="diversidade_categoria",
        )

    if modo_ordem == "🔤 Alfabética (A–Z)":
        st.caption(
            "🔤 Consulta alfabética: Absol, Alcremie, Arbok..."
        )
    else:
        st.caption(
            "🔢 Consulta numérica: #001 Bulbasaur → #002 Ivysaur → #003 Venusaur..."
        )

    termo = st.text_input(
        "🔎 Buscar dentro das formas",
        placeholder="Ex.: Mega, Alola, Galar, Gigantamax, Shadow...",
        key="diversidade_busca",
    ).strip().lower()

    resultados = FORMAS_POR_CHAVE.get(especie_escolhida, [])

    if categoria_escolhida != "Todas":
        resultados = [x for x in resultados if x.categoria == categoria_escolhida]

    if termo:
        resultados = [
            x
            for x in resultados
            if termo in " ".join(
                [
                    x.nome,
                    x.categoria,
                    x.regiao,
                    x.origem,
                    x.jogo,
                    x.descricao,
                    x.id_api,
                ]
            ).lower()
        ]

    st.caption(f"{len(resultados)} forma(s) encontrada(s) para {bonito(especie_escolhida)}")

    for indice, forma in enumerate(resultados):
        card_forma(forma, prefixo=f"explorar_{indice}")

    if not resultados:
        st.info("Nenhuma forma corresponde aos filtros atuais.")


# ============================================================
# ⚖️ COMPARAR
# ============================================================

with tab_comparar:
    st.markdown("## ⚖️ Comparador de formas")
    st.write(
        "Escolha duas formas do mesmo catálogo para visualizar lado a lado tipos, região, categoria "
        "e estatísticas disponíveis na PokéAPI."
    )

    opcoes = sorted(formas, key=lambda x: (x.base_nome.lower(), x.nome.lower()))

    mapa_opcoes = {
        forma.chave: f"{forma.base_nome} → {forma.nome} ({forma.categoria})"
        for forma in opcoes
    }

    selecionadas = st.multiselect(
        "🔬 Selecione exatamente duas formas",
        list(mapa_opcoes.keys()),
        max_selections=2,
        format_func=lambda chave: mapa_opcoes[chave],
        key="diversidade_comparacao",
    )

    if len(selecionadas) != 2:
        st.info("Escolha duas formas para iniciar a comparação.")
    else:
        forma_a = next(x for x in formas if x.chave == selecionadas[0])
        forma_b = next(x for x in formas if x.chave == selecionadas[1])

        dados_a = dados_resumo_forma(forma_a.id_api)
        dados_b = dados_resumo_forma(forma_b.id_api)

        c1, c2 = st.columns(2)

        for coluna, forma, dados, rotulo in [
            (c1, forma_a, dados_a, "A"),
            (c2, forma_b, dados_b, "B"),
        ]:
            with coluna:
                st.markdown(f"### {rotulo} • {forma.nome}")
                imagem = resolver_imagem(forma)
                if imagem:
                    st.image(imagem, use_container_width=True)
                st.caption(f"🐾 Base: {forma.base_nome}")
                st.write(f"🌈 **Categoria:** {forma.categoria}")
                if forma.regiao:
                    st.write(f"🌎 **Região:** {forma.regiao}")
                if dados.get("tipos"):
                    st.write("**Tipos:** " + " / ".join(dados["tipos"]))
                if dados.get("stats"):
                    st.write(f"**Base Stats Total:** {dados['total']}")
                    st.dataframe(
                        {
                            "Atributo": [
                                "HP",
                                "Attack",
                                "Defense",
                                "Sp. Attack",
                                "Sp. Defense",
                                "Speed",
                            ],
                            "Valor": [
                                dados["stats"].get("hp", 0),
                                dados["stats"].get("attack", 0),
                                dados["stats"].get("defense", 0),
                                dados["stats"].get("special-attack", 0),
                                dados["stats"].get("special-defense", 0),
                                dados["stats"].get("speed", 0),
                            ],
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

        st.divider()
        st.markdown("### 🧠 O que mudou?")
        st.write(
            "A ferramenta não tenta decidir qual forma é 'melhor'. Ela apenas coloca os dados lado a lado "
            "para você observar diferenças de design, tipo, contexto e estatísticas."
        )


# ============================================================
# 🖼️ GALERIA
# ============================================================

with tab_galeria:
    st.markdown("## 🖼️ Galeria visual")
    st.write("Uma visão rápida das formas catalogadas no projeto.")

    col1, col2, col3 = st.columns(3)
    with col1:
        galeria_cat = st.selectbox(
            "🌈 Categoria",
            CATEGORIAS_DISPONIVEIS,
            key="galeria_categoria",
        )
    with col2:
        galeria_regiao = st.selectbox(
            "🌎 Região",
            REGIOES_DISPONIVEIS,
            key="galeria_regiao",
        )
    with col3:
        limite_galeria = st.slider(
            "🖼️ Quantidade",
            6,
            min(48, max(6, len(formas))),
            18,
            step=6,
            key="galeria_limite",
        )

    galeria = formas

    if galeria_cat != "Todas":
        galeria = [x for x in galeria if x.categoria == galeria_cat]
    if galeria_regiao != "Todas":
        galeria = [x for x in galeria if x.regiao == galeria_regiao]

    galeria = galeria[:limite_galeria]

    colunas = st.columns(3)
    for indice, forma in enumerate(galeria):
        with colunas[indice % 3]:
            with st.container(border=True):
                imagem = resolver_imagem(forma)
                if imagem:
                    st.image(imagem, use_container_width=True)
                else:
                    st.info("🖼️ Sem imagem")
                st.markdown(f"### {forma.nome}")
                st.caption(f"{forma.base_nome} · {forma.categoria}")
                if forma.regiao:
                    st.caption(f"🌎 {forma.regiao}")
                if st.button(
                    "📖 Pokédex",
                    key=f"galeria_dex_{indice}_{forma.chave}",
                    use_container_width=True,
                ):
                    abrir_na_pokedex(forma.id_api)

    if not galeria:
        st.info("Nenhuma forma encontrada para essa galeria.")


# ============================================================
# 🔗 TRANSFORMAÇÕES
# ============================================================

with tab_relacoes:
    st.markdown("## 🔗 Relação entre espécie e transformação")
    st.write(
        "Aqui a ideia é enxergar visualmente a mudança, sem substituir a seção de evoluções da Pokédex. "
        "Escolha uma forma para ver sua relação com o Pokémon-base."
    )

    forma_relacao = st.selectbox(
        "Escolha uma forma",
        sorted(formas, key=lambda x: (x.base_nome.lower(), x.nome.lower())),
        format_func=lambda x: f"{x.base_nome} → {x.nome}",
        key="diversidade_relacao_forma",
    )

    render_relacao_base(forma_relacao)

    st.divider()
    st.markdown("### 🧩 O que esta página entende como diversidade")

    explicacoes = {
        "Mega Evolução": "Alterações especiais ligadas à Mega Evolução.",
        "Gigantamax": "Formas Gigantamax registradas no catálogo.",
        "Forma Regional": "Variações ligadas a regiões específicas.",
        "Forma Especial": "Variações especiais, eventos, bonés ou outras apresentações.",
        "Fusão": "Mudanças em que diferentes elementos/espécies são combinados.",
        "Transformação": "Estados transformativos registrados pelo projeto.",
        "Outras Formas": "Formas especiais que não se encaixam nas categorias anteriores.",
    }

    for categoria, descricao in explicacoes.items():
        quantidade = sum(1 for forma in formas if forma.categoria == categoria)
        if quantidade:
            st.write(f"**{categoria}:** {quantidade} · {descricao}")


# ============================================================
# ⭐ FAVORITOS
# ============================================================

with tab_favoritos:
    st.markdown("## ⭐ Meus favoritos")
    st.write("Formas que você marcou durante esta sessão do KAYZAC.")

    favoritos_formas = [
        forma
        for forma in formas
        if forma.chave in st.session_state.diversidade_favoritos
    ]

    if not favoritos_formas:
        st.info("Você ainda não favoritou nenhuma forma.")
    else:
        st.success(f"⭐ {len(favoritos_formas)} forma(s) favorita(s)")
        for indice, forma in enumerate(favoritos_formas):
            card_forma(forma, prefixo=f"favoritos_{indice}", mostrar_stats=False)

        st.divider()
        if st.button(
            "🗑️ Limpar favoritos",
            key="diversidade_limpar_favoritos",
            use_container_width=True,
        ):
            st.session_state.diversidade_favoritos = set()
            st.rerun()


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "⚡ KAYZAC - MASTER POKEMON · 🌈 DIVERSIDADE · "
    "O laboratório visual para explorar a variedade de formas do universo Pokémon."
)
