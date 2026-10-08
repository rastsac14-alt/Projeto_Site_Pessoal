from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
import streamlit as st


# ============================================================
# ⚡ KAYZAC - MASTER POKEMON
# 🧠 PÁGINA 8 — KAYZAC QUIZ
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Quiz Pokémon",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# 🎨 ESTILO
# ============================================================

st.markdown(
    """
    <style>
        .quiz-hero {
            padding: 26px;
            border-radius: 22px;
            margin-bottom: 18px;
            background:
                radial-gradient(circle at 12% 12%, rgba(0,145,255,.18), transparent 28%),
                radial-gradient(circle at 88% 18%, rgba(70,210,255,.11), transparent 25%),
                linear-gradient(180deg, #070b10 0%, #05070a 100%);
            border: 1px solid rgba(82,184,255,.35);
            box-shadow: 0 18px 50px rgba(0,0,0,.28);
        }
        .quiz-title { font-size: 2.2rem; font-weight: 900; letter-spacing: .4px; }
        .quiz-subtitle { margin-top: 7px; color: #aebdcc; font-size: 1rem; line-height: 1.5; }
        .question-box {
            padding: 24px;
            border-radius: 20px;
            background: linear-gradient(180deg, #0c131b 0%, #080d13 100%);
            border: 1px solid rgba(82,184,255,.24);
            margin: 14px 0 18px 0;
        }
        .question-number {
            color: #76caff; font-weight: 800; font-size: .88rem;
            text-transform: uppercase; letter-spacing: .6px;
        }
        .question-text { margin-top: 10px; font-size: 1.45rem; font-weight: 800; line-height: 1.35; }
        .feedback-good {
            padding: 14px 16px; border-radius: 14px;
            background: rgba(80,220,145,.09); border: 1px solid rgba(80,220,145,.30);
        }
        .feedback-bad {
            padding: 14px 16px; border-radius: 14px;
            background: rgba(255,90,90,.08); border: 1px solid rgba(255,90,90,.28);
        }
        @media (max-width: 700px) {
            .quiz-title { font-size: 1.7rem; }
            .question-text { font-size: 1.2rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 📚 BANCO DE QUESTÕES
# ============================================================

@dataclass(frozen=True)
class Pergunta:
    pergunta: str
    opcoes: tuple[str, str, str, str]
    correta: int
    categoria: str
    dificuldade: str
    explicacao: str
    imagem: Optional[str] = None
    imagem_alt: str = ""
    imagem_slug: Optional[str] = None
    mostrar_imagem_antes: bool = False
    revelacao_base_slug: Optional[str] = None
    revelacao_forma_slug: Optional[str] = None
    revelacao_base_nome: str = ""
    revelacao_forma_nome: str = ""
    mini_dex_base_slug: Optional[str] = None
    mini_dex_forma_slug: Optional[str] = None
    # Relações genéricas para evoluções, Megas, variantes, formas etc.
    # Cada item é (slug, nome exibido).
    revelacao_linha: Optional[tuple[tuple[str, str], ...]] = None
    # Cada ramo é uma sequência independente de (slug, nome exibido).
    revelacao_ramos: Optional[tuple[tuple[tuple[str, str], ...], ...]] = None


def img_pokemon(numero: int) -> str:
    return (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        f"sprites/pokemon/other/official-artwork/{numero}.png"
    )


@st.cache_data(ttl=86400, show_spinner=False)
def imagem_por_slug(slug: str) -> Optional[str]:
    """Obtém a melhor arte disponível de um Pokémon ou de uma forma específica."""
    slug = str(slug or "").strip().lower()
    if not slug:
        return None

    # Alguns nomes exibidos pelo KAYZAC não são os slugs reais da PokéAPI.
    aliases = {
        "ninetales-de-alola": "ninetales-alola",
        "lycanroc-midday-form": "lycanroc-midday",
        "lycanroc-midnight-form": "lycanroc-midnight",
        "lycanroc-dusk-form": "lycanroc-dusk",
        "ursaluna-bloodmoon": "ursaluna-bloodmoon",
        "bloodmoon-ursaluna": "ursaluna-bloodmoon",
        "mega-lucario": "lucario-mega",
        "mega-charizard-x": "charizard-mega-x",
        "mega-charizard-y": "charizard-mega-y",
    }
    slug_api = aliases.get(slug, slug)

    try:
        resposta = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{slug_api}",
            timeout=10,
            headers={"User-Agent": "KAYZAC-Master-Pokemon/Quiz/2.0"},
        )
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.RequestException:
        return None

    sprites = dados.get("sprites", {}) or {}
    outros = sprites.get("other", {}) or {}
    official = outros.get("official-artwork", {}) or {}
    home = outros.get("home", {}) or {}
    showdown = outros.get("showdown", {}) or {}

    return (
        official.get("front_default")
        or home.get("front_default")
        or showdown.get("front_default")
        or sprites.get("front_default")
    )



def encontrar_pagina_pokedex() -> Optional[str]:
    """Localiza a página da Pokédex dentro de pages/."""
    base_dir = Path(__file__).resolve().parent.parent
    pasta_pages = base_dir / "pages"

    candidatos = [
        "1_Pokedex.py",
        "1_Pokedex_COMPLETA.py",
        "1_Pokedex_COMPLETA_formas_evolucoes.py",
        "pokedex.py",
    ]

    for nome in candidatos:
        caminho = pasta_pages / nome
        if caminho.exists():
            return f"pages/{nome}"

    encontrados = sorted(
        caminho
        for caminho in pasta_pages.glob("*.py")
        if "pokedex" in caminho.stem.lower()
    )

    if encontrados:
        return f"pages/{encontrados[0].name}"

    return None


def abrir_pokemon_na_pokedex(slug: str) -> None:
    """Abre a Pokédex focando a espécie ou a forma revelada."""
    slug = str(slug or "").strip().lower().replace(" ", "-")

    if not slug:
        st.warning("⚠️ Não foi possível identificar o Pokémon para a Mini-Dex.")
        return

    st.session_state["pokemon_focado"] = slug
    pagina = encontrar_pagina_pokedex()

    if pagina:
        st.switch_page(pagina)
    else:
        st.warning("⚠️ Não encontrei a página da Pokédex em `pages/`.")


def _mostrar_card_relacao_pokemon(slug: str, nome: str, key: str) -> None:
    """Mostra imagem + Mini-Dex de um nó da relação."""
    imagem = imagem_por_slug(slug)

    st.markdown(
        f"<div style='text-align:center;font-weight:800;font-size:1.02rem'>{nome}</div>",
        unsafe_allow_html=True,
    )

    if imagem:
        st.image(imagem, width=210)
    else:
        st.info("Imagem indisponível.")

    if st.button(
        "📖 Mini-Dex",
        use_container_width=True,
        key=key,
    ):
        abrir_pokemon_na_pokedex(slug)


def mostrar_relacao_especie_forma(pergunta: Pergunta) -> None:
    """
    Mostra a correção visual de uma relação Pokémon.

    Exemplos:
        Ninetales -> Ninetales de Alola
        Charmander -> Charmeleon -> Charizard
        Lucario -> Mega Lucario

    Também aceita ramos:
        Charizard -> Mega Charizard X
                 -> Mega Charizard Y
    """

    st.markdown("### 🧬 Relação visual")

    # --------------------------------------------------------
    # 🔀 RAMOS — ótimo para Megas com múltiplas formas e
    # formas alternativas/variantes.
    # --------------------------------------------------------
    if pergunta.revelacao_ramos:
        for ramo_indice, ramo in enumerate(pergunta.revelacao_ramos):
            if not ramo:
                continue

            colunas = []
            for item_indice in range(len(ramo)):
                colunas.append(1.15)
                if item_indice < len(ramo) - 1:
                    colunas.append(0.32)

            cols = st.columns(colunas)

            cursor = 0
            for item_indice, (slug, nome) in enumerate(ramo):
                with cols[cursor]:
                    _mostrar_card_relacao_pokemon(
                        slug,
                        nome,
                        key=(
                            f"mini_dex_ramo_{ramo_indice}_{item_indice}_"
                            f"{slug}_{abs(hash(pergunta.pergunta))}"
                        ),
                    )

                cursor += 1

                if item_indice < len(ramo) - 1:
                    with cols[cursor]:
                        st.markdown(
                            """
                            <div style="
                                min-height:235px;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                font-size:2.2rem;
                                font-weight:900;
                                color:#76caff;
                            ">→</div>
                            """,
                            unsafe_allow_html=True,
                        )
                    cursor += 1

            if ramo_indice < len(pergunta.revelacao_ramos) - 1:
                st.markdown("###")

        return

    # --------------------------------------------------------
    # 🔗 LINHA — evoluções e relações lineares.
    # --------------------------------------------------------
    linha = pergunta.revelacao_linha

    if linha:
        colunas = []
        for item_indice in range(len(linha)):
            colunas.append(1.15)
            if item_indice < len(linha) - 1:
                colunas.append(0.32)

        cols = st.columns(colunas)
        cursor = 0

        for item_indice, (slug, nome) in enumerate(linha):
            with cols[cursor]:
                _mostrar_card_relacao_pokemon(
                    slug,
                    nome,
                    key=(
                        f"mini_dex_linha_{item_indice}_"
                        f"{slug}_{abs(hash(pergunta.pergunta))}"
                    ),
                )

            cursor += 1

            if item_indice < len(linha) - 1:
                with cols[cursor]:
                    st.markdown(
                        """
                        <div style="
                            min-height:235px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-size:2.2rem;
                            font-weight:900;
                            color:#76caff;
                        ">→</div>
                        """,
                        unsafe_allow_html=True,
                    )
                cursor += 1

        return

    # --------------------------------------------------------
    # 🧩 COMPATIBILIDADE — relações antigas base -> forma.
    # --------------------------------------------------------
    base_slug = pergunta.revelacao_base_slug
    forma_slug = pergunta.revelacao_forma_slug

    if not base_slug or not forma_slug:
        return

    nome_base = pergunta.revelacao_base_nome or base_slug.replace("-", " ").title()
    nome_forma = pergunta.revelacao_forma_nome or forma_slug.replace("-", " ").title()

    col_base, col_seta, col_forma = st.columns([1.15, 0.32, 1.15])

    with col_base:
        _mostrar_card_relacao_pokemon(
            base_slug,
            nome_base,
            key=f"mini_dex_base_{base_slug}_{abs(hash(pergunta.pergunta))}",
        )

    with col_seta:
        st.markdown(
            """
            <div style="
                min-height:235px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:2.2rem;
                font-weight:900;
                color:#76caff;
            ">→</div>
            """,
            unsafe_allow_html=True,
        )

    with col_forma:
        _mostrar_card_relacao_pokemon(
            forma_slug,
            nome_forma,
            key=f"mini_dex_forma_{forma_slug}_{abs(hash(pergunta.pergunta))}",
        )


PERGUNTAS = [
    # 🐾 POKÉMON
    Pergunta("Qual Pokémon é conhecido como o mascote principal da franquia?", ("Pikachu", "Eevee", "Lucario", "Charizard"), 0, "Pokémon", "Fácil", "Pikachu é o principal mascote da franquia Pokémon.", img_pokemon(25), "Pikachu"),
    Pergunta("Qual é o número da Pokédex Nacional do Bulbasaur?", ("001", "004", "007", "025"), 0, "Pokémon", "Fácil", "Bulbasaur é o número #001 da Pokédex Nacional.", img_pokemon(1), "Bulbasaur"),
    Pergunta(
        "Qual destes Pokémon evolui de Magikarp?",
        ("Gyarados", "Milotic", "Sharpedo", "Whiscash"),
        0, "Pokémon", "Fácil",
        "Magikarp evolui para Gyarados.",
        revelacao_linha=(
            ("magikarp", "Magikarp"),
            ("gyarados", "Gyarados"),
        ),
    ),
    Pergunta(
        "Qual é a evolução final de Charmander?",
        ("Charmeleon", "Charizard", "Blastoise", "Arcanine"),
        1, "Pokémon", "Fácil",
        "A linha é Charmander → Charmeleon → Charizard.",
        revelacao_linha=(
            ("charmander", "Charmander"),
            ("charmeleon", "Charmeleon"),
            ("charizard", "Charizard"),
        ),
    ),
    Pergunta("Qual destes Pokémon é do tipo Fantasma/Veneno?", ("Gengar", "Haunter", "Gastly", "Todos os três"), 3, "Pokémon", "Fácil", "Gastly, Haunter e Gengar possuem os tipos Fantasma/Veneno na série principal.", img_pokemon(94), "Gengar"),
    Pergunta("Qual é a espécie #448?", ("Lucario", "Riolu", "Gallade", "Mega Lucario"), 0, "Pokémon", "Fácil", "Lucario é o Pokémon #448 da Pokédex Nacional.", img_pokemon(448), "Lucario"),
    Pergunta(
        "Qual destes Pokémon pertence à linha evolutiva de Ralts?",
        ("Gardevoir", "Mismagius", "Gothitelle", "Delphox"),
        0, "Pokémon", "Médio",
        "Ralts pode evoluir para Kirlia e depois Gardevoir ou Gallade em condições específicas.",
        revelacao_linha=(
            ("ralts", "Ralts"),
            ("kirlia", "Kirlia"),
            ("gardevoir", "Gardevoir"),
        ),
    ),
    Pergunta("Qual destes Pokémon não pertence à Geração I?", ("Scizor", "Dragonite", "Lapras", "Gengar"), 0, "Pokémon", "Médio", "Scizor foi introduzido na Geração II.", img_pokemon(212), "Scizor"),
    Pergunta("Qual destes Pokémon é um pseudolendário?", ("Garchomp", "Haxorus", "Tyrantrum", "Kingdra"), 0, "Pokémon", "Médio", "Garchomp pertence a uma linha de pseudolendários.", img_pokemon(445), "Garchomp"),
    Pergunta(
        "Qual é a evolução de Pawniard?",
        ("Bisharp", "Kingambit", "Mabosstiff", "Kleavor"),
        0, "Pokémon", "Médio",
        "Pawniard evolui para Bisharp; Bisharp pode posteriormente evoluir para Kingambit.",
        revelacao_linha=(
            ("pawniard", "Pawniard"),
            ("bisharp", "Bisharp"),
            ("kingambit", "Kingambit"),
        ),
    ),
    Pergunta(
        "Qual Pokémon possui uma forma de Alola?",
        ("Ninetales", "Lucario", "Garchomp", "Greninja"),
        0,
        "Pokémon",
        "Médio",
        "Ninetales possui uma Forma de Alola do tipo Gelo/Fada.",
        revelacao_base_slug="ninetales",
        revelacao_forma_slug="ninetales-alola",
        revelacao_base_nome="Ninetales",
        revelacao_forma_nome="Ninetales de Alola",
        mini_dex_base_slug="ninetales",
        mini_dex_forma_slug="ninetales-alola",
    ),
    Pergunta("Qual é o número da Pokédex Nacional de Zygarde?", ("716", "717", "718", "719"), 2, "Pokémon", "Difícil", "Zygarde é o Pokémon #718.", img_pokemon(718), "Zygarde"),
    Pergunta(
        "Qual destes Pokémon possui uma forma Bloodmoon oficial?",
        ("Ursaluna", "Lunala", "Lunatone", "Bloodmoon Lycanroc"),
        0,
        "Pokémon",
        "Difícil",
        "Ursaluna possui a forma Bloodmoon em Pokémon Scarlet e Violet — The Teal Mask.",
        revelacao_base_slug="ursaluna",
        revelacao_forma_slug="ursaluna-bloodmoon",
        revelacao_base_nome="Ursaluna",
        revelacao_forma_nome="Ursaluna Bloodmoon",
        mini_dex_base_slug="ursaluna",
        mini_dex_forma_slug="ursaluna-bloodmoon",
    ),
    Pergunta("Qual Pokémon é #774 na Pokédex Nacional?", ("Minior", "Cosmoem", "Solrock", "Meteorbit"), 0, "Pokémon", "Difícil", "Minior é o Pokémon #774.", img_pokemon(774), "Minior"),
    Pergunta(
        "Qual destes Pokémon pode evoluir para Gallade?",
        ("Kirlia macho", "Kirlia fêmea", "Ralts macho", "Gardevoir macho"),
        0, "Pokémon", "Difícil",
        "Kirlia macho pode evoluir para Gallade usando Dawn Stone.",
        revelacao_linha=(
            ("kirlia", "Kirlia"),
            ("gallade", "Gallade"),
        ),
    ),

    # 🔎 IDENTIFICAÇÃO VISUAL
    # Aqui a imagem é propositalmente mostrada ANTES da resposta.
    Pergunta(
        "🔎 Quem é este Pokémon?",
        ("Lucario", "Zoroark", "Gallade", "Riolu"),
        0,
        "Identificação",
        "Fácil",
        "A imagem mostra Lucario, o Pokémon Aura #448.",
        imagem_slug="lucario",
        imagem_alt="Lucario",
        mostrar_imagem_antes=True,
    ),
    Pergunta(
        "🔎 Quem é este Pokémon?",
        ("Charizard", "Dragonite", "Salamence", "Tyrantrum"),
        0,
        "Identificação",
        "Fácil",
        "A imagem mostra Charizard, a evolução final de Charmeleon.",
        imagem_slug="charizard",
        imagem_alt="Charizard",
        mostrar_imagem_antes=True,
    ),
    Pergunta(
        "🔎 Quem é este Pokémon?",
        ("Gengar", "Haunter", "Mismagius", "Cofagrigus"),
        0,
        "Identificação",
        "Fácil",
        "A imagem mostra Gengar, a evolução final de Gastly e Haunter.",
        imagem_slug="gengar",
        imagem_alt="Gengar",
        mostrar_imagem_antes=True,
    ),
    Pergunta(
        "🌎 Qual Pokémon/forma está sendo mostrada?",
        ("Ninetales de Alola", "Ninetales normal", "Vulpix de Alola", "Froslass"),
        0,
        "Identificação",
        "Médio",
        "A forma mostrada é Ninetales de Alola, cuja tipagem oficial é Gelo/Fada.",
        imagem_slug="ninetales-alola",
        imagem_alt="Ninetales de Alola",
        mostrar_imagem_antes=True,
        revelacao_base_slug="ninetales",
        revelacao_forma_slug="ninetales-alola",
        revelacao_base_nome="Ninetales",
        revelacao_forma_nome="Ninetales de Alola",
        mini_dex_base_slug="ninetales",
        mini_dex_forma_slug="ninetales-alola",
    ),
    Pergunta(
        "🌙 Qual forma de Lycanroc está sendo mostrada?",
        ("Dusk Form", "Midday Form", "Midnight Form", "Bloodmoon Form"),
        0,
        "Identificação",
        "Médio",
        "A imagem mostra Lycanroc Dusk Form.",
        imagem_slug="lycanroc-dusk",
        imagem_alt="Lycanroc Dusk Form",
        mostrar_imagem_antes=True,
        revelacao_base_slug="rockruff",
        revelacao_forma_slug="lycanroc-dusk",
        revelacao_base_nome="Rockruff",
        revelacao_forma_nome="Lycanroc Dusk Form",
        mini_dex_base_slug="rockruff",
        mini_dex_forma_slug="lycanroc-dusk",
    ),
    Pergunta(
        "🩸 Qual forma de Ursaluna está sendo mostrada?",
        ("Bloodmoon", "Hisui", "Alpha", "Shadow"),
        0,
        "Identificação",
        "Difícil",
        "A imagem mostra Ursaluna Bloodmoon, uma forma especial introduzida em Scarlet e Violet — The Teal Mask.",
        imagem_slug="ursaluna-bloodmoon",
        imagem_alt="Ursaluna Bloodmoon",
        mostrar_imagem_antes=True,
        revelacao_base_slug="ursaluna",
        revelacao_forma_slug="ursaluna-bloodmoon",
        revelacao_base_nome="Ursaluna",
        revelacao_forma_nome="Ursaluna Bloodmoon",
        mini_dex_base_slug="ursaluna",
        mini_dex_forma_slug="ursaluna-bloodmoon",
    ),

    # 🌈 TIPOS
    Pergunta("Qual tipo é supereficaz contra Água?", ("Elétrico", "Fogo", "Terrestre", "Pedra"), 0, "Tipos", "Fácil", "Ataques Elétricos são supereficazes contra Água."),
    Pergunta("Qual tipo é imune a ataques Normal?", ("Fantasma", "Fada", "Inseto", "Gelo"), 0, "Tipos", "Fácil", "Pokémon do tipo Fantasma são imunes a movimentos do tipo Normal."),
    Pergunta("Qual é a tipagem de Lucario?", ("Lutador/Aço", "Aço/Psíquico", "Lutador/Ferro", "Aço/Noturno"), 0, "Tipos", "Fácil", "Lucario possui os tipos Lutador e Aço.", img_pokemon(448), "Lucario"),
    Pergunta("Qual tipo foi introduzido na Geração VI?", ("Fada", "Som", "Luz", "Cósmico"), 0, "Tipos", "Médio", "O tipo Fada foi introduzido na Geração VI."),
    Pergunta("Qual tipo é imune a ataques Elétricos?", ("Terra", "Água", "Voador", "Aço"), 0, "Tipos", "Médio", "Pokémon do tipo Terra são imunes a movimentos Elétricos."),
    Pergunta("Qual tipo possui imunidade a Normal e Lutador?", ("Fantasma", "Dragão", "Grama", "Fogo"), 0, "Tipos", "Difícil", "Fantasma possui imunidade a Normal e Lutador."),

    # 🥊 MOVIMENTOS
    Pergunta("Qual movimento é associado de forma clássica ao Pikachu?", ("Thunderbolt", "Flamethrower", "Ice Beam", "Earthquake"), 0, "Movimentos", "Fácil", "Thunderbolt é um dos golpes mais icônicos de Pikachu.", img_pokemon(25), "Pikachu"),
    Pergunta("Qual movimento aumenta o Ataque do usuário em 2 estágios?", ("Swords Dance", "Growl", "Tail Whip", "Leer"), 0, "Movimentos", "Médio", "Swords Dance aumenta o Attack em dois estágios."),
    Pergunta("Qual movimento é especialmente associado a Lucario?", ("Aura Sphere", "Surf", "Leaf Blade", "Moonblast"), 0, "Movimentos", "Médio", "Aura Sphere é um golpe muito associado a Lucario e à temática de aura.", img_pokemon(448), "Lucario"),
    Pergunta("Qual destes golpes é do tipo Fada?", ("Moonblast", "Dark Pulse", "Dragon Claw", "Psychic"), 0, "Movimentos", "Fácil", "Moonblast é um golpe do tipo Fada."),
    Pergunta("Qual movimento remove hazards como Stealth Rock e Spikes do lado do usuário?", ("Rapid Spin", "Protect", "Roar", "Snatch"), 0, "Movimentos", "Difícil", "Rapid Spin remove entry hazards do lado do usuário e também possui efeito sobre Speed nas gerações modernas."),
    Pergunta("Qual destes golpes tem prioridade positiva?", ("Quick Attack", "Hyper Beam", "Earth Power", "Focus Blast"), 0, "Movimentos", "Médio", "Quick Attack possui prioridade +1 em condições normais."),

    # 🧬 HABILIDADES
    Pergunta("Qual habilidade normalmente impede redução de Accuracy?", ("Keen Eye", "Intimidate", "Synchronize", "Levitate"), 0, "Habilidades", "Médio", "Keen Eye impede a redução da Accuracy do usuário."),
    Pergunta("Qual habilidade concede imunidade a ataques do tipo Terra em condições normais?", ("Levitate", "Sturdy", "Overgrow", "Pressure"), 0, "Habilidades", "Fácil", "Levitate concede imunidade a movimentos do tipo Terra em situações normais."),
    Pergunta("Qual habilidade reduz o Attack dos adversários ao entrar em batalha?", ("Intimidate", "Moxie", "Guts", "Torrent"), 0, "Habilidades", "Fácil", "Intimidate reduz o Attack dos adversários ao entrar em campo."),
    Pergunta("Qual habilidade é tradicionalmente associada a Swampert?", ("Torrent", "Blaze", "Overgrow", "Shield Dust"), 0, "Habilidades", "Fácil", "Swampert possui Torrent como habilidade padrão.", img_pokemon(260), "Swampert"),
    Pergunta("Qual habilidade aumenta a potência de golpes de Fogo quando o HP está baixo?", ("Blaze", "Torrent", "Overgrow", "Swarm"), 0, "Habilidades", "Médio", "Blaze aumenta a potência de movimentos de Fogo quando o HP está baixo."),

    # 🌎 REGIÕES
    Pergunta("Qual é a primeira região da série principal?", ("Kanto", "Johto", "Hoenn", "Sinnoh"), 0, "Regiões", "Fácil", "Kanto é a região da primeira geração."),
    Pergunta("Qual região é formada por ilhas e introduziu os Island Trials?", ("Alola", "Kalos", "Galar", "Paldea"), 0, "Regiões", "Fácil", "Alola substitui a estrutura tradicional de ginásios pelos Island Trials."),
    Pergunta("Qual região introduziu a Mega Evolução?", ("Kalos", "Hoenn", "Alola", "Sinnoh"), 0, "Regiões", "Médio", "A Mega Evolução foi introduzida em Pokémon X e Y, ambientados em Kalos."),
    Pergunta("Qual região introduziu as formas regionais?", ("Alola", "Galar", "Hisui", "Paldea"), 0, "Regiões", "Médio", "As formas regionais estrearam nos jogos de Alola."),
    Pergunta("Qual região é fortemente inspirada na Península Ibérica?", ("Paldea", "Kalos", "Galar", "Unova"), 0, "Regiões", "Médio", "Paldea é fortemente inspirada na Península Ibérica."),
    Pergunta("Qual é o nome histórico da região que depois ficou conhecida como Sinnoh?", ("Hisui", "Sinnoh", "Unova", "Johto"), 0, "Regiões", "Fácil", "Hisui é o nome histórico da região de Pokémon Legends: Arceus."),
    Pergunta("Qual região está associada à Dynamaxização?", ("Galar", "Kalos", "Alola", "Hoenn"), 0, "Regiões", "Fácil", "Galar é a região de Sword e Shield e da mecânica Dynamax/Gigantamax."),

    # 👥 PERSONAGENS
    Pergunta("Quem é o rival clássico de Red em Kanto?", ("Blue", "Silver", "Barry", "Hau"), 0, "Personagens", "Fácil", "Blue é o rival de Red nos jogos clássicos de Kanto."),
    Pergunta("Quem é a Campeã associada a Sinnoh nos jogos principais?", ("Cynthia", "Iris", "Diantha", "Lance"), 0, "Personagens", "Fácil", "Cynthia é a Campeã de Sinnoh nos jogos principais."),
    Pergunta("Quem lidera a Team Rocket nos jogos principais?", ("Giovanni", "Guzma", "Cyrus", "Ghetsis"), 0, "Personagens", "Fácil", "Giovanni é o chefe da Team Rocket."),
    Pergunta("Quem é o Campeão de Galar em Sword e Shield?", ("Leon", "Hop", "Bede", "Mustard"), 0, "Personagens", "Fácil", "Leon é apresentado como o Campeão de Galar."),
    Pergunta("Quem é o professor e fundador da Liga de Alola?", ("Professor Kukui", "Professor Oak", "Professor Sycamore", "Professor Elm"), 0, "Personagens", "Médio", "Professor Kukui é uma figura central na criação da Liga de Alola."),
    Pergunta("Quem é o primeiro Campeão da Liga de Alola no anime?", ("Ash", "Gladion", "Kukui", "Hau"), 0, "Personagens", "Médio", "No anime, Ash vence a primeira Conferência de Manalo e torna-se Campeão da Liga de Alola."),
    Pergunta("Quem é a Campeã de Kalos?", ("Diantha", "Nemona", "Geeta", "Alder"), 0, "Personagens", "Médio", "Diantha é a Campeã de Kalos nos jogos principais."),
    Pergunta("Quem ocupa o papel de rival recorrente em Hoenn dependendo do protagonista escolhido?", ("Brendan/May", "Silver", "N", "Gladion"), 0, "Personagens", "Médio", "Brendan e May podem atuar como protagonista ou rival conforme a escolha do jogador."),

    # 🌈 FORMAS
    Pergunta("Qual mecânica foi introduzida em X e Y?", ("Mega Evolução", "Z-Moves", "Dynamax", "Terastalização"), 0, "Formas", "Fácil", "X e Y introduziram a Mega Evolução."),
    Pergunta("Qual mecânica foi introduzida em Sun e Moon?", ("Z-Moves", "Mega Evolução", "Dynamax", "Terastalização"), 0, "Formas", "Fácil", "Sun e Moon introduziram Z-Moves."),
    Pergunta("Qual mecânica foi introduzida em Sword e Shield?", ("Dynamax/Gigantamax", "Terastalização", "Z-Moves", "Mega Evolução"), 0, "Formas", "Fácil", "Sword e Shield introduziram Dynamax e Gigantamax."),
    Pergunta("Qual mecânica pode alterar o tipo de um Pokémon em Scarlet e Violet?", ("Terastalização", "Mega Evolução", "Dynamax", "Z-Move"), 0, "Formas", "Fácil", "A Terastalização pode alterar o Pokémon para seu Tera Type."),
    Pergunta(
        "Qual Pokémon possui Mega Lucario?",
        ("Lucario", "Riolu", "Zeraora", "Gallade"),
        0, "Formas", "Fácil",
        "Mega Lucario é a Mega Evolução de Lucario.",
        revelacao_linha=(
            ("lucario", "Lucario"),
            ("lucario-mega", "Mega Lucario"),
        ),
    ),
    Pergunta(
        "Qual Pokémon possui Mega Charizard X e Mega Charizard Y?",
        ("Charizard", "Charmeleon", "Dragonite", "Salamence"),
        0, "Formas", "Fácil",
        "Charizard possui duas Mega Evoluções: X e Y.",
        revelacao_ramos=(
            (("charizard", "Charizard"), ("charizard-mega-x", "Mega Charizard X")),
            (("charizard", "Charizard"), ("charizard-mega-y", "Mega Charizard Y")),
        ),
    ),
    Pergunta(
        "Qual destas é uma forma regional oficial?",
        ("Ninetales de Alola", "Lucario de Kanto", "Gengar de Johto", "Garchomp de Unova"),
        0,
        "Formas",
        "Médio",
        "Ninetales de Alola é uma forma regional oficial.",
        revelacao_base_slug="ninetales",
        revelacao_forma_slug="ninetales-alola",
        revelacao_base_nome="Ninetales",
        revelacao_forma_nome="Ninetales de Alola",
        mini_dex_base_slug="ninetales",
        mini_dex_forma_slug="ninetales-alola",
    ),
    Pergunta(
        "Quais formas pertencem a Lycanroc?",
        ("Midday, Midnight e Dusk", "Sun, Moon e Eclipse", "Dawn e Dusk", "Day e Night"),
        0, "Formas", "Médio",
        "Lycanroc possui as formas Midday, Midnight e Dusk.",
        revelacao_ramos=(
            (("rockruff", "Rockruff"), ("lycanroc-midday", "Midday Form")),
            (("rockruff", "Rockruff"), ("lycanroc-midnight", "Midnight Form")),
            (("rockruff", "Rockruff"), ("lycanroc-dusk", "Dusk Form")),
        ),
    ),
    Pergunta(
        "🪨 Como Rockruff pode evoluir para as diferentes formas de Lycanroc?",
        (
            "Midday durante o dia, Midnight à noite e Dusk com Own Tempo no período de crepúsculo",
            "Midday com pedra solar, Midnight com pedra lunar e Dusk com Dawn Stone",
            "As três formas dependem apenas do tipo de Poké Bola usada",
            "Rockruff só pode evoluir para Midday; as outras formas são exclusivas de eventos",
        ),
        0,
        "Formas",
        "Difícil",
        "Rockruff pode seguir caminhos diferentes: a Midday Form é associada ao dia, a Midnight Form à noite, e a Dusk Form exige um Rockruff com Own Tempo durante o período específico de crepúsculo permitido pelo jogo. As condições exatas de horário podem variar entre os títulos.",
        revelacao_ramos=(
            (("rockruff", "Rockruff"), ("lycanroc-midday", "Lycanroc Midday Form")),
            (("rockruff", "Rockruff"), ("lycanroc-midnight", "Lycanroc Midnight Form")),
            (("rockruff", "Rockruff"), ("lycanroc-dusk", "Lycanroc Dusk Form")),
        ),
    ),

    # ⚡ KAYZAC
    Pergunta("Qual Pokémon é conhecido como o 'Rei de Kanto' na identidade do KAYZAC?", ("Nidoking", "Nidoqueen", "Charizard", "Dragonite"), 0, "KAYZAC", "Difícil", "Dentro do projeto KAYZAC, Nidoking está associado ao conceito de 'Rei de Kanto'.", img_pokemon(34), "Nidoking"),
    Pergunta("Qual Pokémon é o parceiro/favorito absoluto da identidade KAYZAC?", ("Lucario", "Garchomp", "Metagross", "Greninja"), 0, "KAYZAC", "Mestre", "Lucario ocupa o papel de parceiro central da identidade KAYZAC.", img_pokemon(448), "Lucario"),
    Pergunta("Qual Pokémon ficou associado ao conceito de 'Rei de Hoenn' dentro do KAYZAC?", ("Swampert", "Blaziken", "Salamence", "Metagross"), 0, "KAYZAC", "Difícil", "Swampert é associado ao conceito de 'Rei de Hoenn' no projeto KAYZAC.", img_pokemon(260), "Swampert"),
    Pergunta("Qual Pokémon funciona como símbolo de aura na identidade do KAYZAC?", ("Lucario", "Persian", "Ditto", "Delibird"), 0, "KAYZAC", "Mestre", "A identidade KAYZAC usa Lucario como protagonista e símbolo de aura.", img_pokemon(448), "Lucario"),
]


# ============================================================
# 🎚️ CONFIGURAÇÕES
# ============================================================

DIFICULDADES = ["Todas", "Fácil", "Médio", "Difícil", "Mestre"]
CATEGORIAS = [
    "Todas", "Pokémon", "Identificação", "Tipos", "Movimentos", "Habilidades",
    "Regiões", "Personagens", "Formas", "KAYZAC"
]

DIFICULDADE_PESO = {"Fácil": 100, "Médio": 150, "Difícil": 225, "Mestre": 350}
NIVEIS_TREINADOR = [
    (0, "🌱 Novato"),
    (500, "🔵 Treinador"),
    (1500, "🥈 Especialista"),
    (3000, "🥇 Mestre"),
    (5000, "👑 Mestre Pokémon"),
    (8000, "⚡ KAYZAC Master"),
]


def inicializar_estado() -> None:
    defaults = {
        "quiz_ativo": False,
        "quiz_finalizado": False,
        "quiz_perguntas": [],
        "quiz_indice": 0,
        "quiz_pontuacao": 0,
        "quiz_acertos": 0,
        "quiz_streak": 0,
        "quiz_melhor_streak": 0,
        "quiz_resposta": None,
        "quiz_escolha_atual": None,
        "quiz_historico": [],
        "quiz_xp_total": 0,
        "quiz_melhor_pontuacao": 0,
        "quiz_total_respostas": 0,
        "quiz_total_acertos": 0,
        "quiz_perfil_nivel": "🌱 Novato",
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


inicializar_estado()


def nivel_por_xp(xp: int) -> str:
    nivel = NIVEIS_TREINADOR[0][1]
    for limite, nome in NIVEIS_TREINADOR:
        if xp >= limite:
            nivel = nome
    return nivel


def dificuldade_multiplicador(dificuldade: str) -> float:
    return {"Fácil": 1.0, "Médio": 1.15, "Difícil": 1.35, "Mestre": 1.65}.get(dificuldade, 1.0)


def calcular_xp(pergunta: Pergunta, streak: int) -> int:
    base = DIFICULDADE_PESO.get(pergunta.dificuldade, 100)
    bonus_streak = min(max(streak - 1, 0) * 25, 200)
    return int((base + bonus_streak) * dificuldade_multiplicador(pergunta.dificuldade))


def filtrar_perguntas(categoria: str, dificuldade: str) -> list[Pergunta]:
    resultado = PERGUNTAS
    if categoria != "Todas":
        resultado = [p for p in resultado if p.categoria == categoria]
    if dificuldade != "Todas":
        resultado = [p for p in resultado if p.dificuldade == dificuldade]
    return resultado


def iniciar_quiz(categoria: str, dificuldade: str, quantidade: int, modo: str) -> bool:
    banco = filtrar_perguntas(categoria, dificuldade)
    if not banco:
        st.error("❌ Não encontrei perguntas para essa combinação.")
        return False
    quantidade_real = min(quantidade, len(banco))
    st.session_state.quiz_ativo = True
    st.session_state.quiz_finalizado = False
    st.session_state.quiz_perguntas = random.sample(banco, quantidade_real)
    st.session_state.quiz_indice = 0
    st.session_state.quiz_pontuacao = 0
    st.session_state.quiz_acertos = 0
    st.session_state.quiz_streak = 0
    st.session_state.quiz_melhor_streak = 0
    st.session_state.quiz_resposta = None
    st.session_state.quiz_escolha_atual = None
    st.session_state.quiz_historico = []
    st.session_state.quiz_modo = modo
    return True


def responder(pergunta: Pergunta, escolha: int) -> None:
    if st.session_state.quiz_resposta is not None:
        return

    acertou = escolha == pergunta.correta
    st.session_state.quiz_resposta = pergunta.correta
    st.session_state.quiz_escolha_atual = escolha
    st.session_state.quiz_total_respostas += 1

    if acertou:
        st.session_state.quiz_acertos += 1
        st.session_state.quiz_total_acertos += 1
        st.session_state.quiz_streak += 1
        st.session_state.quiz_melhor_streak = max(
            st.session_state.quiz_melhor_streak,
            st.session_state.quiz_streak,
        )
        xp = calcular_xp(pergunta, st.session_state.quiz_streak)
        st.session_state.quiz_pontuacao += xp
        st.session_state.quiz_xp_total += xp
    else:
        st.session_state.quiz_streak = 0
        xp = 0

    st.session_state.quiz_historico.append(
        {
            "pergunta": pergunta.pergunta,
            "sua_resposta": pergunta.opcoes[escolha],
            "resposta_correta": pergunta.opcoes[pergunta.correta],
            "acertou": acertou,
            "xp": xp,
            "dificuldade": pergunta.dificuldade,
            "explicacao": pergunta.explicacao,
        }
    )
    st.session_state.quiz_perfil_nivel = nivel_por_xp(st.session_state.quiz_xp_total)


def proxima_pergunta() -> None:
    indice = st.session_state.quiz_indice
    if indice + 1 >= len(st.session_state.quiz_perguntas):
        finalizar_quiz()
        return
    st.session_state.quiz_indice += 1
    st.session_state.quiz_resposta = None
    st.session_state.quiz_escolha_atual = None


def finalizar_quiz() -> None:
    st.session_state.quiz_ativo = False
    st.session_state.quiz_finalizado = True
    st.session_state.quiz_melhor_pontuacao = max(
        st.session_state.quiz_melhor_pontuacao,
        st.session_state.quiz_pontuacao,
    )
    st.session_state.quiz_perfil_nivel = nivel_por_xp(st.session_state.quiz_xp_total)


def reiniciar_para_menu() -> None:
    st.session_state.quiz_ativo = False
    st.session_state.quiz_finalizado = False
    st.session_state.quiz_perguntas = []
    st.session_state.quiz_indice = 0
    st.session_state.quiz_pontuacao = 0
    st.session_state.quiz_acertos = 0
    st.session_state.quiz_streak = 0
    st.session_state.quiz_melhor_streak = 0
    st.session_state.quiz_resposta = None
    st.session_state.quiz_escolha_atual = None
    st.session_state.quiz_historico = []


# ============================================================
# 🏠 CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="quiz-hero">
        <div class="quiz-title">🧠 KAYZAC QUIZ</div>
        <div class="quiz-subtitle">
            Teste seus conhecimentos sobre Pokémon, tipos, movimentos, habilidades,
            regiões, personagens, formas e até o próprio universo KAYZAC.
            Cada acerto gera XP e já prepara o futuro Perfil do Treinador.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 📊 STATUS
# ============================================================

c1, c2, c3, c4 = st.columns(4)
c1.metric("⚡ XP", st.session_state.quiz_xp_total)
c2.metric("🏆 Melhor pontuação", st.session_state.quiz_melhor_pontuacao)
c3.metric("✅ Acertos", st.session_state.quiz_total_acertos)
c4.metric("👑 Nível", st.session_state.quiz_perfil_nivel)

st.divider()


# ============================================================
# 🎮 RODADA ATIVA
# ============================================================

if st.session_state.quiz_ativo:
    perguntas = st.session_state.quiz_perguntas
    indice = st.session_state.quiz_indice
    pergunta = perguntas[indice]

    st.progress((indice + 1) / len(perguntas), text=f"Pergunta {indice + 1} de {len(perguntas)}")

    m1, m2, m3 = st.columns(3)
    m1.caption(f"🏷️ Categoria: **{pergunta.categoria}**")
    m2.caption(f"🎚️ Dificuldade: **{pergunta.dificuldade}**")
    m3.caption(f"🔥 Sequência: **{st.session_state.quiz_streak}**")

    st.markdown(
        f"""
        <div class="question-box">
            <div class="question-number">QUESTÃO {indice + 1}</div>
            <div class="question-text">{pergunta.pergunta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Imagem só aparece antes da resposta quando a pergunta é realmente
    # de identificação visual. Nas perguntas de conhecimento, a imagem é
    # revelada somente na correção para não entregar a resposta.
    if pergunta.mostrar_imagem_antes:
        imagem_previa = pergunta.imagem or (
            imagem_por_slug(pergunta.imagem_slug)
            if pergunta.imagem_slug
            else None
        )
        if imagem_previa:
            st.image(
                imagem_previa,
                caption=pergunta.imagem_alt or "🔎 Observe o Pokémon",
                width=260,
            )

    if st.session_state.quiz_resposta is None:
        colunas = st.columns(2)
        for opcao_indice, opcao in enumerate(pergunta.opcoes):
            with colunas[opcao_indice % 2]:
                letra = chr(65 + opcao_indice)
                if st.button(
                    f"{letra}) {opcao}",
                    key=f"quiz_resposta_{indice}_{opcao_indice}",
                    use_container_width=True,
                ):
                    responder(pergunta, opcao_indice)
                    st.rerun()
    else:
        escolha = st.session_state.quiz_escolha_atual
        acertou = escolha == pergunta.correta

        if acertou:
            st.markdown(
                f"""
                <div class="feedback-good">
                    <strong>✅ CORRETO!</strong><br>
                    Você acertou! 🔥<br>
                    XP recebido: <strong>{st.session_state.quiz_historico[-1]['xp']}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="feedback-bad">
                    <strong>❌ QUASE!</strong><br>
                    Sua resposta: <strong>{pergunta.opcoes[escolha]}</strong><br>
                    Resposta correta: <strong>{pergunta.opcoes[pergunta.correta]}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------
        # 🖼️ REVELAÇÃO VISUAL DA CORREÇÃO
        # ----------------------------------------------------
        # Qualquer pergunta que possua uma relação cadastrada
        # (linha evolutiva, ramo de Mega/variante ou base → forma)
        # recebe o painel visual completo, com imagens e Mini-Dex.
        tem_relacao = bool(
            pergunta.revelacao_linha
            or pergunta.revelacao_ramos
            or (
                pergunta.revelacao_base_slug
                and pergunta.revelacao_forma_slug
            )
        )

        if tem_relacao:
            mostrar_relacao_especie_forma(pergunta)
        else:
            imagem_correcao = pergunta.imagem or (
                imagem_por_slug(pergunta.imagem_slug)
                if pergunta.imagem_slug
                else None
            )

            if imagem_correcao:
                st.markdown("### 🖼️ Pokémon revelado")
                st.image(
                    imagem_correcao,
                    caption=(
                        f"✅ Resposta: {pergunta.opcoes[pergunta.correta]}"
                        if pergunta.imagem_alt
                        else "✅ Visual da resposta"
                    ),
                    width=280,
                )
                if pergunta.imagem_alt:
                    st.caption(
                        f"🔎 Referência visual: **{pergunta.imagem_alt}**"
                    )

        st.markdown("### 💡 Explicação")
        st.write(pergunta.explicacao)

        if st.button(
            "➡️ Próxima pergunta",
            type="primary",
            use_container_width=True,
            key=f"proxima_{indice}",
        ):
            proxima_pergunta()
            st.rerun()


# ============================================================
# 🏁 RESULTADO
# ============================================================

elif st.session_state.quiz_finalizado:
    total = len(st.session_state.quiz_perguntas)
    acertos = st.session_state.quiz_acertos
    porcentagem = (acertos / total * 100) if total else 0

    st.markdown("## 🏆 Resultado da Rodada")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("✅ Acertos", f"{acertos}/{total}")
    r2.metric("📊 Aproveitamento", f"{porcentagem:.0f}%")
    r3.metric("⚡ XP na rodada", st.session_state.quiz_pontuacao)
    r4.metric("🔥 Melhor sequência", st.session_state.quiz_melhor_streak)

    if porcentagem == 100:
        st.success("👑 PERFEITO! Você acertou todas as perguntas da rodada!")
    elif porcentagem >= 80:
        st.success("🔥 Excelente! Sua jornada de treinador está avançando.")
    elif porcentagem >= 60:
        st.info("💪 Bom trabalho! Mais algumas batalhas e esse conhecimento sobe de nível.")
    else:
        st.warning("🌱 Todo Mestre Pokémon começou aprendendo. Tente outra rodada!")

    st.markdown("### 📜 Revisão da rodada")
    for numero, registro in enumerate(st.session_state.quiz_historico, start=1):
        simbolo = "✅" if registro["acertou"] else "❌"
        with st.expander(f"{simbolo} {numero}. {registro['pergunta']}"):
            st.write(f"**Sua resposta:** {registro['sua_resposta']}")
            st.write(f"**Resposta correta:** {registro['resposta_correta']}")
            st.write(f"**Dificuldade:** {registro['dificuldade']}")
            if registro["xp"]:
                st.write(f"**XP:** +{registro['xp']}")
            st.write(f"**Explicação:** {registro['explicacao']}")

    if st.button("🧠 Nova rodada", type="primary", use_container_width=True):
        reiniciar_para_menu()
        st.rerun()


# ============================================================
# 🎯 MENU
# ============================================================

else:
    st.markdown("## 🎯 Escolha seu desafio")

    col1, col2 = st.columns(2)
    with col1:
        categoria = st.selectbox("🏷️ Categoria", CATEGORIAS, key="quiz_menu_categoria")
        dificuldade = st.selectbox("🎚️ Dificuldade", DIFICULDADES, key="quiz_menu_dificuldade")

    with col2:
        modo = st.selectbox(
            "🎮 Modo",
            ["🎯 Desafio por rodada", "🔥 Maratona de conhecimento"],
            key="quiz_menu_modo",
        )
        if modo == "🎯 Desafio por rodada":
            quantidade = st.select_slider(
                "📚 Número de perguntas",
                options=[5, 10, 15, 20],
                value=10,
                key="quiz_menu_quantidade",
            )
        else:
            quantidade = 20

    banco_disponivel = filtrar_perguntas(categoria, dificuldade)
    b1, b2, b3 = st.columns(3)
    b1.metric("📚 Perguntas disponíveis", len(banco_disponivel))
    b2.metric("⚡ XP total acumulado", st.session_state.quiz_xp_total)
    b3.metric("🔥 Melhor sequência", st.session_state.quiz_melhor_streak)

    if quantidade > len(banco_disponivel):
        st.warning(
            f"⚠️ Esta configuração possui apenas {len(banco_disponivel)} perguntas. "
            "O Quiz usará todas elas."
        )

    st.divider()
    st.markdown("### 🎮 Como funciona")
    a, b, c = st.columns(3)
    a.markdown("#### 🧠 Responda\nEscolha uma entre quatro alternativas.")
    b.markdown("#### 🔥 Faça sequências\nAcertos seguidos aumentam o bônus de XP.")
    c.markdown("#### 🏆 Suba de nível\nSeu XP fica guardado nesta sessão e prepara o Perfil do Treinador.")

    st.divider()
    st.markdown("### 🏅 Dificuldades")
    st.markdown("**🌱 Fácil** → conhecimento básico  \n**🔵 Médio** → detalhes de jogos e mecânicas  \n**🔥 Difícil** → detalhes específicos  \n**👑 Mestre** → para quem realmente conhece Pokémon")

    if st.button("🚀 COMEÇAR QUIZ", type="primary", use_container_width=True):
        if iniciar_quiz(categoria, dificuldade, quantidade, modo):
            st.rerun()


# ============================================================
# 🧩 INTEGRAÇÕES FUTURAS
# ============================================================

with st.expander("🧩 Integrações futuras do KAYZAC"):
    st.write(
        "Esta página já mantém XP, melhores sequências, acertos e desempenho em "
        "st.session_state para facilitar a futura integração com Perfil do Treinador e Conquistas."
    )
    st.write(
        "Próximas evoluções possíveis: cronômetro por questão, banco maior pela Pokédex, "
        "modo sem fim, identificação visual, categorias especiais KAYZAC, ranking pessoal, "
        "conquistas e sons para respostas certas/erradas."
    )


# ============================================================
# 🏁 RODAPÉ
# ============================================================

st.divider()
st.caption("⚡ KAYZAC - MASTER POKEMON · 🧠 KAYZAC QUIZ · Uma experiência feita por fãs para fãs.")
