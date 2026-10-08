import json
import math
import re
from pathlib import Path
import requests
import streamlit as st

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Kayzac - Times Pokémon",
    page_icon="⚔️",
    layout="wide"
)

API_BASE = "https://pokeapi.co/api/v2/"

# ============================================================
# ESTADO INICIAL DO APLICATIVO
# ============================================================
# Inicializamos todo o estado usado pelas abas antes de qualquer
# leitura de st.session_state. Isso evita AttributeError na
# primeira execução e também mantém os dados entre reruns.
if "time_atual" not in st.session_state:
    st.session_state.time_atual = []
if "builds" not in st.session_state:
    st.session_state.builds = {}
if "times_salvos" not in st.session_state:
    st.session_state.times_salvos = {}
if "time_nome" not in st.session_state:
    st.session_state.time_nome = "Meu Time"
if "pokemon_comparacao_a" not in st.session_state:
    st.session_state.pokemon_comparacao_a = "Lucario"
if "pokemon_comparacao_b" not in st.session_state:
    st.session_state.pokemon_comparacao_b = "Gallade"
if "champions_times" not in st.session_state:
    st.session_state.champions_times = {}
if "champions_perfil_ativo" not in st.session_state:
    st.session_state.champions_perfil_ativo = None

BASE_DIR = Path(__file__).resolve().parent.parent
FORMAS_JSON = BASE_DIR / "formas_pokemon.json"
MAX_TEAM_SIZE = 6
STAT_KEYS = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
STAT_LABELS = {
    "hp": "❤️ HP",
    "attack": "⚔️ Ataque",
    "defense": "🛡️ Defesa",
    "special-attack": "✨ Atq. Esp.",
    "special-defense": "🔰 Def. Esp.",
    "speed": "💨 Velocidade",
}

TIPOS = [
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel", "fairy"
]

TRADUCAO_TIPOS = {
    "normal": "Normal", "fire": "Fogo", "water": "Água", "electric": "Elétrico",
    "grass": "Grama", "ice": "Gelo", "fighting": "Lutador", "poison": "Veneno",
    "ground": "Terra", "flying": "Voador", "psychic": "Psíquico", "bug": "Inseto",
    "rock": "Pedra", "ghost": "Fantasma", "dragon": "Dragão", "dark": "Sombrio",
    "steel": "Aço", "fairy": "Fada"
}

NATURES = {
    "Hardy": (None, None), "Lonely": ("attack", "defense"),
    "Adamant": ("attack", "special-attack"), "Naughty": ("attack", "special-defense"),
    "Brave": ("attack", "speed"), "Bold": ("defense", "attack"),
    "Docile": (None, None), "Impish": ("defense", "special-attack"),
    "Lax": ("defense", "special-defense"), "Relaxed": ("defense", "speed"),
    "Modest": ("special-attack", "attack"), "Mild": ("special-attack", "defense"),
    "Bashful": (None, None), "Rash": ("special-attack", "special-defense"),
    "Quiet": ("special-attack", "speed"), "Calm": ("special-defense", "attack"),
    "Gentle": ("special-defense", "defense"), "Careful": ("special-defense", "special-attack"),
    "Quirky": (None, None), "Sassy": ("special-defense", "speed"),
    "Timid": ("speed", "attack"), "Hasty": ("speed", "defense"),
    "Jolly": ("speed", "special-attack"), "Naive": ("speed", "special-defense")
}

ITENS_COMUNS = [
    "Nenhum", "Leftovers", "Life Orb", "Choice Band", "Choice Specs",
    "Choice Scarf", "Focus Sash", "Assault Vest", "Heavy-Duty Boots",
    "Expert Belt", "Sitrus Berry", "Lum Berry", "Rocky Helmet", "Eviolite",
    "Choice item", "Booster Energy", "Clear Amulet", "Covert Cloak", "Loaded Dice",
    "Light Clay", "Black Sludge", "Air Balloon", "Weakness Policy", "Safety Goggles"
]

CATEGORIAS_GOLPES = {
    "physical": "Físico", "special": "Especial", "status": "Status"
}

# ============================================================
# EFETIVIDADE DE TIPOS
# ============================================================

CHART = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
    "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying": {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "steel": 0.5, "dark": 0},
    "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
    "fairy": {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5}
}

# ============================================================
# FUNÇÕES BÁSICAS
# ============================================================

def normalizar_nome(nome):
    if not nome:
        return ""
    return str(nome).strip().lower().replace(" ", "-").replace("_", "-")


def nome_bonito(nome):
    if not nome:
        return ""
    return str(nome).replace("-", " ").replace("_", " ").title()


def traduzir_tipo(tipo):
    return TRADUCAO_TIPOS.get(normalizar_nome(tipo), nome_bonito(tipo))


def obter_tipos(dados):
    return [
        item.get("type", {}).get("name", "")
        for item in (dados or {}).get("types", [])
        if item.get("type", {}).get("name")
    ]


def obter_stats(dados):
    resultado = {}
    for item in (dados or {}).get("stats", []):
        nome = item.get("stat", {}).get("name")
        if nome in STAT_KEYS:
            resultado[nome] = item.get("base_stat", 0)
    return resultado


def multiplicador_tipo(ataque, defesa):
    return CHART.get(ataque, {}).get(defesa, 1.0)


@st.cache_data(ttl=3600, show_spinner=False)
def requisicao_api(url):
    try:
        resposta = requests.get(url, timeout=12)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_pokemon(nome):
    return requisicao_api(API_BASE + f"pokemon/{normalizar_nome(nome)}")


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_movimento(nome):
    return requisicao_api(API_BASE + f"move/{normalizar_nome(nome)}")


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_habilidade(nome):
    return requisicao_api(API_BASE + f"ability/{normalizar_nome(nome)}")


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_especie_por_url(url):
    return requisicao_api(url) if url else None


FORMAS_REGIONAIS_FALLBACK = {
    # Alola
    "rattata": ["rattata-alola"],
    "raticate": ["raticate-alola"],
    "raichu": ["raichu-alola"],
    "sandshrew": ["sandshrew-alola"],
    "sandslash": ["sandslash-alola"],
    "vulpix": ["vulpix-alola"],
    "ninetales": ["ninetales-alola"],
    "diglett": ["diglett-alola"],
    "dugtrio": ["dugtrio-alola"],
    "meowth": ["meowth-alola", "meowth-galar"],
    "persian": ["persian-alola"],
    "geodude": ["geodude-alola"],
    "graveler": ["graveler-alola"],
    "golem": ["golem-alola"],
    "grimer": ["grimer-alola"],
    "muk": ["muk-alola"],
    "exeggutor": ["exeggutor-alola"],
    "marowak": ["marowak-alola"],
    # Galar
    "ponyta": ["ponyta-galar"],
    "rapidash": ["rapidash-galar"],
    "farfetchd": ["farfetchd-galar"],
    "weezing": ["weezing-galar"],
    "mrmime": ["mr-mime-galar"],
    "mr-mime": ["mr-mime-galar"],
    "corsola": ["corsola-galar"],
    "zigzagoon": ["zigzagoon-galar"],
    "linoone": ["linoone-galar"],
    "darumaka": ["darumaka-galar"],
    "darmanitan": ["darmanitan-galar", "darmanitan-galar-standard", "darmanitan-galar-zen"],
    "yamask": ["yamask-galar"],
    "stunfisk": ["stunfisk-galar"],
    "slowpoke": ["slowpoke-galar"],
    "slowbro": ["slowbro-galar"],
    "slowking": ["slowking-galar"],
    "articuno": ["articuno-galar"],
    "zapdos": ["zapdos-galar"],
    "moltres": ["moltres-galar"],
    # Hisui
    "growlithe": ["growlithe-hisui"],
    "arcanine": ["arcanine-hisui"],
    "voltorb": ["voltorb-hisui"],
    "electrode": ["electrode-hisui"],
    "typhlosion": ["typhlosion-hisui"],
    "qwilfish": ["qwilfish-hisui"],
    "samurott": ["samurott-hisui"],
    "lilligant": ["lilligant-hisui"],
    "zorua": ["zorua-hisui"],
    "zoroark": ["zoroark-hisui"],
    "braviary": ["braviary-hisui"],
    "sliggoo": ["sliggoo-hisui"],
    "goodra": ["goodra-hisui"],
    "avalugg": ["avalugg-hisui"],
    "decidueye": ["decidueye-hisui"],
}


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_formas_pokemon(nome):
    dados = buscar_pokemon(nome)
    if not dados:
        return []

    especie_url = dados.get("species", {}).get("url")
    especie = buscar_especie_por_url(especie_url)
    variedades = (especie or {}).get("varieties", [])

    formas = []
    vistos = set()
    for variedade in variedades:
        pokemon = variedade.get("pokemon", {})
        slug = normalizar_nome(pokemon.get("name", ""))
        if not slug or slug in vistos:
            continue
        vistos.add(slug)
        formas.append({
            "nome": slug,
            "oficial": bool(variedade.get("is_default")),
            "rotulo": nome_bonito(slug)
        })

    # Fallback local para formas regionais. Isso garante que a interface
    # continue oferecendo as variantes mesmo quando a PokéAPI demora ou
    # não devolve as variedades no momento da consulta.
    base = normalizar_nome(nome)
    for slug in FORMAS_REGIONAIS_FALLBACK.get(base, []):
        if slug not in vistos:
            formas.append({
                "nome": slug,
                "oficial": False,
                "rotulo": nome_da_forma(slug, nome)
            })
            vistos.add(slug)

    # Fallback: sempre inclui a forma/base que foi pesquisada.
    if normalizar_nome(nome) and normalizar_nome(nome) not in vistos:
        formas.insert(0, {
            "nome": normalizar_nome(nome),
            "oficial": True,
            "rotulo": nome_bonito(nome)
        })

    formas.sort(key=lambda x: (not x["oficial"], x["rotulo"]))
    return formas


def carregar_formas_json(nome):
    # Opcional: aproveita o formas_pokemon.json do projeto,
    # mas o funcionamento principal não depende dele.
    if not FORMAS_JSON.exists():
        return []
    try:
        conteudo = FORMAS_JSON.read_text(encoding="utf-8")
        dados = json.loads(conteudo)
    except Exception:
        return []
    alvo = normalizar_nome(nome)
    resultado = dados.get(alvo, []) if isinstance(dados, dict) else []
    return resultado if isinstance(resultado, list) else []


def listar_formas_completas(nome):
    """Retorna formas da PokéAPI + formas extras do JSON do projeto."""
    formas = buscar_formas_pokemon(nome)
    extras = carregar_formas_json(nome)
    existentes = {normalizar_nome(f.get("nome", "")) for f in formas}

    for item in extras:
        if isinstance(item, str):
            slug = normalizar_nome(item)
        elif isinstance(item, dict):
            slug = normalizar_nome(
                item.get("name")
                or item.get("nome")
                or item.get("pokemon")
                or item.get("slug")
                or ""
            )
        else:
            slug = ""

        if slug and slug not in existentes:
            formas.append({
                "nome": slug,
                "oficial": False,
                "rotulo": nome_da_forma(slug, nome)
            })
            existentes.add(slug)

    base = normalizar_nome(nome)
    if base and base not in existentes:
        formas.insert(0, {
            "nome": base,
            "oficial": True,
            "rotulo": "Forma Base"
        })

    formas.sort(key=lambda x: (not x.get("oficial", False), x.get("rotulo", "")))
    return formas


def nome_da_forma(slug, base_nome=None):
    slug = normalizar_nome(slug)
    if not slug:
        return nome_bonito(base_nome or "")
    if base_nome and slug == normalizar_nome(base_nome):
        return "Forma Base"
    partes = slug.split("-")
    if len(partes) > 1 and normalizar_nome(base_nome or "") in slug:
        sufixo = slug.replace(normalizar_nome(base_nome), "", 1).strip("-")
        return nome_bonito(sufixo) or "Forma Base"
    return nome_bonito(slug)


def obter_dados_da_build(nome, build):
    form = normalizar_nome(build.get("form", nome)) if isinstance(build, dict) else normalizar_nome(nome)
    dados = buscar_pokemon(form)
    return dados or buscar_pokemon(nome)


def obter_sprite(dados, shiny=False):
    if not dados:
        return None
    sprites = dados.get("sprites", {})
    if shiny:
        candidatos = [
            sprites.get("other", {}).get("official-artwork", {}).get("front_shiny"),
            sprites.get("front_shiny"),
            sprites.get("other", {}).get("showdown", {}).get("front_shiny"),
            sprites.get("other", {}).get("home", {}).get("front_shiny"),
        ]
    else:
        candidatos = [
            sprites.get("other", {}).get("official-artwork", {}).get("front_default"),
            sprites.get("other", {}).get("home", {}).get("front_default"),
            sprites.get("front_default"),
            sprites.get("other", {}).get("showdown", {}).get("front_default"),
        ]
    return next((url for url in candidatos if url), None)


def obter_ability_names(dados):
    return [
        a.get("ability", {}).get("name", "")
        for a in (dados or {}).get("abilities", [])
        if a.get("ability", {}).get("name")
    ]


def build_padrao(nome, dados=None):
    habilidades = obter_ability_names(dados)
    return {
        "level": 50,
        "form": normalizar_nome(nome),
        "nature": "Hardy",
        "ability": habilidades[0] if habilidades else "",
        "item": "Nenhum",
        "tera": "auto",
        "shiny": False,
        "ivs": {stat: 31 for stat in STAT_KEYS},
        "evs": {stat: 0 for stat in STAT_KEYS},
        "moves": ["", "", "", ""]
    }


def normalizar_build(build, nome="", dados=None):
    padrao = build_padrao(nome, dados)
    if not isinstance(build, dict):
        return padrao
    resultado = padrao.copy()
    for chave in ["level", "form", "nature", "ability", "item", "tera", "shiny"]:
        if chave in build:
            resultado[chave] = build[chave]
    for grupo in ["ivs", "evs"]:
        valores = dict(padrao[grupo])
        if isinstance(build.get(grupo), dict):
            for stat in STAT_KEYS:
                if stat in build[grupo]:
                    try:
                        valores[stat] = int(build[grupo][stat])
                    except (TypeError, ValueError):
                        pass
        resultado[grupo] = valores
    if isinstance(build.get("moves"), list):
        resultado["moves"] = (list(build["moves"]) + [""] * 4)[:4]
    return resultado


def garantir_build(nome):
    chave = normalizar_nome(nome)
    dados = buscar_pokemon(nome)
    atual = st.session_state.builds.get(chave)
    normalizada = normalizar_build(atual, nome, dados)
    st.session_state.builds[chave] = normalizada
    return normalizada

# ============================================================
# STATS
# ============================================================

def calcular_stat_completo(nome_stat, base, iv, ev, level, natureza):
    level = max(1, min(100, int(level)))
    iv = max(0, min(31, int(iv)))
    ev = max(0, min(252, int(ev)))
    valor = math.floor(((2 * int(base) + iv + math.floor(ev / 4)) * level) / 100)
    if nome_stat == "hp":
        return valor + level + 10
    valor += 5
    sobe, desce = NATURES.get(natureza, (None, None))
    if sobe == nome_stat:
        valor = math.floor(valor * 1.1)
    elif desce == nome_stat:
        valor = math.floor(valor * 0.9)
    return valor


def calcular_stats_build(dados, build):
    if not dados:
        return {}
    base = obter_stats(dados)
    return {
        stat: calcular_stat_completo(
            stat,
            base.get(stat, 0),
            build["ivs"][stat],
            build["evs"][stat],
            build["level"],
            build["nature"]
        )
        for stat in STAT_KEYS
    }

# ============================================================
# MOVES DISPONÍVEIS
# ============================================================

def obter_movimentos_disponiveis(dados):
    if not dados:
        return []
    nomes = []
    for item in dados.get("moves", []):
        nome = item.get("move", {}).get("name")
        if nome:
            nomes.append(nome)
    return sorted(set(nomes))


def traduzir_metodo_movimento(move_info):
    metodo = move_info.get("damage_class", {}).get("name", "")
    return CATEGORIAS_GOLPES.get(metodo, nome_bonito(metodo))

# ============================================================
# ANÁLISES
# ============================================================

def analisar_defesas(dados_time):
    resultado = {tipo: {"fracos": 0, "resistentes": 0, "imunes": 0, "dupla": 0} for tipo in TIPOS}
    for dados in dados_time:
        tipos = obter_tipos(dados)
        for ataque in TIPOS:
            mult = 1.0
            for defesa in tipos:
                mult *= multiplicador_tipo(ataque, defesa)
            if mult == 0:
                resultado[ataque]["imunes"] += 1
            elif mult > 1:
                resultado[ataque]["fracos"] += 1
                if mult >= 4:
                    resultado[ataque]["dupla"] += 1
            elif mult < 1:
                resultado[ataque]["resistentes"] += 1
    return resultado


def analisar_cobertura(dados_time):
    resultado = {tipo: 0 for tipo in TIPOS}
    for dados in dados_time:
        for ataque in obter_tipos(dados):
            for alvo in TIPOS:
                if multiplicador_tipo(ataque, alvo) > 1:
                    resultado[alvo] += 1
    return resultado


def analisar_tipo_fisico_especial(dados_time):
    return {
        "físicos": sum(1 for d in dados_time if obter_stats(d).get("attack", 0) > obter_stats(d).get("special-attack", 0)),
        "especiais": sum(1 for d in dados_time if obter_stats(d).get("special-attack", 0) > obter_stats(d).get("attack", 0)),
        "equilibrados": sum(1 for d in dados_time if obter_stats(d).get("attack", 0) == obter_stats(d).get("special-attack", 0)),
    }


def identificar_alertas(dados_time, stats_time):
    alertas = []
    if len(dados_time) < 6:
        alertas.append(f"Seu time ainda tem {6 - len(dados_time)} vaga(s).")
    defesas = analisar_defesas(dados_time)
    for tipo, dados in sorted(defesas.items(), key=lambda x: x[1]["fracos"], reverse=True):
        if dados["fracos"] >= 4:
            alertas.append(f"🔴 {traduzir_tipo(tipo)} é uma fraqueza em {dados['fracos']} Pokémon.")
        elif dados["fracos"] >= 3:
            alertas.append(f"🟠 {traduzir_tipo(tipo)} aparece como fraqueza em {dados['fracos']} Pokémon.")
        if dados["fracos"] >= 4 and dados["imunes"] == 0:
            alertas.append(f"O time não possui imunidade a {traduzir_tipo(tipo)}.")
    if stats_time:
        media_speed = sum(s["speed"] for s in stats_time) / len(stats_time)
        media_hp = sum(s["hp"] for s in stats_time) / len(stats_time)
        if media_speed < 70:
            alertas.append("💨 A Velocidade média do time está relativamente baixa.")
        if media_hp < 75:
            alertas.append("🛡️ O HP médio está relativamente baixo.")
    fisico_especial = analisar_tipo_fisico_especial(dados_time)
    if fisico_especial["físicos"] >= 5 and fisico_especial["especiais"] == 0:
        alertas.append("⚠️ O time é quase totalmente físico; Pokémon defensivos físicos podem ser um problema.")
    if fisico_especial["especiais"] >= 5 and fisico_especial["físicos"] == 0:
        alertas.append("⚠️ O time é quase totalmente especial; Pokémon com alta Defesa podem ser um problema.")
    return alertas


def diagnostico_positivo(dados_time, stats_time):
    pontos = []
    defesas = analisar_defesas(dados_time)
    imunidades = [(t, d["imunes"]) for t, d in defesas.items() if d["imunes"]]
    coberturas = analisar_cobertura(dados_time)
    boas_coberturas = sum(1 for q in coberturas.values() if q >= 2)
    if imunidades:
        pontos.append(f"✅ O time possui {sum(q for _, q in imunidades)} imunidades somadas.")
    if boas_coberturas >= 8:
        pontos.append("✅ Boa diversidade de cobertura ofensiva por tipos.")
    if stats_time:
        media_speed = sum(s["speed"] for s in stats_time) / len(stats_time)
        if media_speed >= 90:
            pontos.append("✅ Velocidade média elevada.")
    fisico_especial = analisar_tipo_fisico_especial(dados_time)
    if fisico_especial["físicos"] and fisico_especial["especiais"]:
        pontos.append("✅ O time possui mistura de atacantes físicos e especiais.")
    return pontos


# ============================================================
# PRESETS DE JOGOS / REGIÕES
# ============================================================

JOGOS_REGIONAIS = {
    # ========================================================
    # KANTO
    # ========================================================
    "Kanto — Pokémon FireRed": {
        "regiao": "Kanto",
        "jogo": "Pokémon FireRed",
        "time_padrao": ["venusaur", "nidoking", "arcanine", "lapras", "dragonite", "gengar"],
        "builds_padrao": {
            "venusaur": {"moves": ["razor-leaf", "sleep-powder", "leech-seed", "giga-drain"], "nature": "Modest"},
            "nidoking": {"moves": ["earthquake", "rock-slide", "sludge-bomb", "brick-break"], "nature": "Adamant"},
            "arcanine": {"moves": ["flamethrower", "extreme-speed", "bite", "iron-tail"], "nature": "Adamant"},
            "lapras": {"moves": ["surf", "ice-beam", "thunderbolt", "confuse-ray"], "nature": "Modest"},
            "dragonite": {"moves": ["dragon-claw", "fly", "ice-beam", "thunderbolt"], "nature": "Naive"},
            "gengar": {"moves": ["shadow-ball", "psychic", "thunderbolt", "hypnosis"], "nature": "Timid"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Brock", "tipo": "rock", "alvos": ["rock"]},
            {"categoria": "Ginásio", "nome": "Misty", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Ginásio", "nome": "Lt. Surge", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Erika", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Ginásio", "nome": "Koga", "tipo": "poison", "alvos": ["poison"]},
            {"categoria": "Ginásio", "nome": "Sabrina", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Ginásio", "nome": "Blaine", "tipo": "fire", "alvos": ["fire"]},
            {"categoria": "Ginásio", "nome": "Giovanni", "tipo": "ground", "alvos": ["ground"]},
            {"categoria": "Elite Four", "nome": "Lorelei", "tipo": "ice", "alvos": ["ice", "water"]},
            {"categoria": "Elite Four", "nome": "Bruno", "tipo": "fighting", "alvos": ["fighting", "rock"]},
            {"categoria": "Elite Four", "nome": "Agatha", "tipo": "ghost", "alvos": ["ghost", "poison"]},
            {"categoria": "Elite Four", "nome": "Lance", "tipo": "dragon", "alvos": ["dragon", "flying"]},
            {"categoria": "Campeão", "nome": "Blue", "tipo": "mixed", "alvos": ["flying", "psychic", "ground", "water", "grass", "fire"]},
        ],
    },

    # ========================================================
    # JOHTO
    # ========================================================
    "Johto — Pokémon HeartGold": {
        "regiao": "Johto",
        "jogo": "Pokémon HeartGold",
        "time_padrao": ["feraligatr", "ampharos", "espeon", "heracross", "mamoswine", "dragonite"],
        "builds_padrao": {
            "feraligatr": {"moves": ["waterfall", "ice-fang", "crunch", "surf"], "nature": "Adamant"},
            "ampharos": {"moves": ["thunderbolt", "signal-beam", "power-gem", "thunder-wave"], "nature": "Modest"},
            "espeon": {"moves": ["psychic", "shadow-ball", "signal-beam", "calm-mind"], "nature": "Timid"},
            "heracross": {"moves": ["close-combat", "megahorn", "rock-slide", "strength"], "nature": "Adamant"},
            "mamoswine": {"moves": ["earthquake", "ice-fang", "rock-slide", "hail"], "nature": "Adamant"},
            "dragonite": {"moves": ["dragon-claw", "fly", "ice-beam", "thunderbolt"], "nature": "Naive"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Falkner", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Ginásio", "nome": "Bugsy", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Ginásio", "nome": "Whitney", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Ginásio", "nome": "Morty", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Ginásio", "nome": "Chuck", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Ginásio", "nome": "Jasmine", "tipo": "steel", "alvos": ["steel"]},
            {"categoria": "Ginásio", "nome": "Pryce", "tipo": "ice", "alvos": ["ice"]},
            {"categoria": "Ginásio", "nome": "Clair", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Elite Four", "nome": "Will", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Elite Four", "nome": "Koga", "tipo": "poison", "alvos": ["poison", "bug"]},
            {"categoria": "Elite Four", "nome": "Bruno", "tipo": "fighting", "alvos": ["fighting", "rock"]},
            {"categoria": "Elite Four", "nome": "Karen", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Campeão", "nome": "Lance", "tipo": "dragon", "alvos": ["dragon", "flying"]},
        ],
    },

    # ========================================================
    # HOENN
    # ========================================================
    "Hoenn — Pokémon Emerald": {
        "regiao": "Hoenn",
        "jogo": "Pokémon Emerald",
        "time_padrao": ["swampert", "gardevoir", "breloom", "manectric", "flygon", "aggron"],
        "builds_padrao": {
            "swampert": {"moves": ["surf", "earthquake", "ice-beam", "protect"], "nature": "Relaxed"},
            "gardevoir": {"moves": ["psychic", "thunderbolt", "calm-mind", "hypnosis"], "nature": "Modest"},
            "breloom": {"moves": ["sky-uppercut", "mach-punch", "leech-seed", "headbutt"], "nature": "Adamant"},
            "manectric": {"moves": ["thunderbolt", "thunder-wave", "bite", "strength"], "nature": "Timid"},
            "flygon": {"moves": ["earthquake", "dragon-claw", "flamethrower", "fly"], "nature": "Jolly"},
            "aggron": {"moves": ["iron-tail", "rock-tomb", "earthquake", "strength"], "nature": "Adamant"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Roxanne", "tipo": "rock", "alvos": ["rock"]},
            {"categoria": "Ginásio", "nome": "Brawly", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Ginásio", "nome": "Wattson", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Flannery", "tipo": "fire", "alvos": ["fire"]},
            {"categoria": "Ginásio", "nome": "Norman", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Ginásio", "nome": "Winona", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Ginásio", "nome": "Tate & Liza", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Ginásio", "nome": "Juan", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Elite Four", "nome": "Sidney", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Elite Four", "nome": "Phoebe", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Elite Four", "nome": "Glacia", "tipo": "ice", "alvos": ["ice", "water"]},
            {"categoria": "Elite Four", "nome": "Drake", "tipo": "dragon", "alvos": ["dragon", "flying"]},
            {"categoria": "Campeão", "nome": "Wallace", "tipo": "water", "alvos": ["water"]},
        ],
    },

    # ========================================================
    # SINNOH
    # ========================================================
    "Sinnoh — Pokémon Platinum": {
        "regiao": "Sinnoh",
        "jogo": "Pokémon Platinum",
        "time_padrao": ["infernape", "garchomp", "staraptor", "luxray", "roserade", "lucario"],
        "builds_padrao": {
            "infernape": {"moves": ["close-combat", "flamethrower", "grass-knot", "mach-punch"], "nature": "Naive"},
            "garchomp": {"moves": ["earthquake", "dragon-claw", "stone-edge", "swords-dance"], "nature": "Jolly"},
            "staraptor": {"moves": ["brave-bird", "close-combat", "fly", "return"], "nature": "Jolly"},
            "luxray": {"moves": ["spark", "thunder-wave", "crunch", "strength"], "nature": "Adamant"},
            "roserade": {"moves": ["energy-ball", "sludge-bomb", "shadow-ball", "toxic"], "nature": "Timid"},
            "lucario": {"moves": ["close-combat", "aura-sphere", "flash-cannon", "extreme-speed"], "nature": "Jolly"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Roark", "tipo": "rock", "alvos": ["rock"]},
            {"categoria": "Ginásio", "nome": "Gardenia", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Ginásio", "nome": "Maylene", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Ginásio", "nome": "Crasher Wake", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Ginásio", "nome": "Fantina", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Ginásio", "nome": "Byron", "tipo": "steel", "alvos": ["steel"]},
            {"categoria": "Ginásio", "nome": "Candice", "tipo": "ice", "alvos": ["ice"]},
            {"categoria": "Ginásio", "nome": "Volkner", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Elite Four", "nome": "Aaron", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Elite Four", "nome": "Bertha", "tipo": "ground", "alvos": ["ground"]},
            {"categoria": "Elite Four", "nome": "Flint", "tipo": "fire", "alvos": ["fire"]},
            {"categoria": "Elite Four", "nome": "Lucian", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Campeão", "nome": "Cynthia", "tipo": "mixed", "alvos": ["ghost", "water", "dragon", "ground", "fighting", "grass"]},
        ],
    },

    # ========================================================
    # UNOVA
    # ========================================================
    "Unova — Pokémon White": {
        "regiao": "Unova",
        "jogo": "Pokémon White",
        "time_padrao": ["samurott", "excadrill", "chandelure", "krookodile", "haxorus", "emolga"],
        "builds_padrao": {
            "samurott": {"moves": ["surf", "ice-beam", "megahorn", "aqua-jet"], "nature": "Modest"},
            "excadrill": {"moves": ["earthquake", "rock-slide", "x-scissor", "swords-dance"], "nature": "Jolly"},
            "chandelure": {"moves": ["shadow-ball", "flamethrower", "energy-ball", "will-o-wisp"], "nature": "Timid"},
            "krookodile": {"moves": ["earthquake", "crunch", "rock-slide", "brick-break"], "nature": "Jolly"},
            "haxorus": {"moves": ["dragon-claw", "earthquake", "brick-break", "swords-dance"], "nature": "Jolly"},
            "emolga": {"moves": ["thunderbolt", "acrobatics", "volt-switch", "roost"], "nature": "Timid"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Cress", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Ginásio", "nome": "Lenora", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Ginásio", "nome": "Burgh", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Ginásio", "nome": "Elesa", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Clay", "tipo": "ground", "alvos": ["ground"]},
            {"categoria": "Ginásio", "nome": "Skyla", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Ginásio", "nome": "Brycen", "tipo": "ice", "alvos": ["ice"]},
            {"categoria": "Ginásio", "nome": "Drayden", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Elite Four", "nome": "Shauntal", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Elite Four", "nome": "Marshal", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Elite Four", "nome": "Grimsley", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Elite Four", "nome": "Caitlin", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Campeão", "nome": "Alder", "tipo": "mixed", "alvos": ["bug", "dragon", "fire", "fighting", "psychic", "water"]},
        ],
    },

    "Unova — Pokémon Black 2": {
        "regiao": "Unova",
        "jogo": "Pokémon Black 2",
        "time_padrao": ["samurott", "lucario", "arcanine", "krookodile", "haxorus", "jolteon"],
        "builds_padrao": {
            "samurott": {"moves": ["surf", "ice-beam", "megahorn", "aqua-jet"], "nature": "Modest"},
            "lucario": {"moves": ["close-combat", "aura-sphere", "flash-cannon", "shadow-claw"], "nature": "Jolly"},
            "arcanine": {"moves": ["flamethrower", "extreme-speed", "crunch", "wild-charge"], "nature": "Adamant"},
            "krookodile": {"moves": ["earthquake", "crunch", "rock-slide", "brick-break"], "nature": "Jolly"},
            "haxorus": {"moves": ["dragon-claw", "earthquake", "brick-break", "swords-dance"], "nature": "Jolly"},
            "jolteon": {"moves": ["thunderbolt", "shadow-ball", "signal-beam", "thunder-wave"], "nature": "Timid"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Cheren", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Ginásio", "nome": "Roxie", "tipo": "poison", "alvos": ["poison"]},
            {"categoria": "Ginásio", "nome": "Burgh", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Ginásio", "nome": "Elesa", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Clay", "tipo": "ground", "alvos": ["ground"]},
            {"categoria": "Ginásio", "nome": "Skyla", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Ginásio", "nome": "Drayden", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Ginásio", "nome": "Marlon", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Elite Four", "nome": "Shauntal", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Elite Four", "nome": "Marshal", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Elite Four", "nome": "Grimsley", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Elite Four", "nome": "Caitlin", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Campeão", "nome": "Iris", "tipo": "mixed", "alvos": ["dragon", "water", "electric", "rock", "flying", "steel"]},
        ],
    },

    # ========================================================
    # KALOS
    # ========================================================
    "Kalos — Pokémon X/Y": {
        "regiao": "Kalos",
        "jogo": "Pokémon X / Pokémon Y",
        "time_padrao": ["greninja", "charizard", "lucario", "gardevoir", "tyrantrum", "raichu"],
        "builds_padrao": {
            "greninja": {"moves": ["surf", "ice-beam", "dark-pulse", "extrasensory"], "nature": "Timid"},
            "charizard": {"moves": ["flamethrower", "air-slash", "dragon-claw", "roost"], "nature": "Timid"},
            "lucario": {"moves": ["close-combat", "bullet-punch", "poison-jab", "swords-dance"], "nature": "Jolly"},
            "gardevoir": {"moves": ["psychic", "moonblast", "shadow-ball", "calm-mind"], "nature": "Modest"},
            "tyrantrum": {"moves": ["rock-slide", "dragon-claw", "earthquake", "crunch"], "nature": "Adamant"},
            "raichu": {"moves": ["thunderbolt", "thunder-wave", "grass-knot", "brick-break"], "nature": "Timid"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Viola", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Ginásio", "nome": "Grant", "tipo": "rock", "alvos": ["rock"]},
            {"categoria": "Ginásio", "nome": "Korrina", "tipo": "fighting", "alvos": ["fighting"]},
            {"categoria": "Ginásio", "nome": "Ramos", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Ginásio", "nome": "Clemont", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Valerie", "tipo": "fairy", "alvos": ["fairy"]},
            {"categoria": "Ginásio", "nome": "Olympia", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Ginásio", "nome": "Wulfric", "tipo": "ice", "alvos": ["ice"]},
            {"categoria": "Elite Four", "nome": "Malva", "tipo": "fire", "alvos": ["fire"]},
            {"categoria": "Elite Four", "nome": "Siebold", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Elite Four", "nome": "Wikstrom", "tipo": "steel", "alvos": ["steel"]},
            {"categoria": "Elite Four", "nome": "Drasna", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Campeão", "nome": "Diantha", "tipo": "mixed", "alvos": ["fairy", "rock", "dragon", "ghost", "grass", "fighting"]},
        ],
    },

    # ========================================================
    # ALOLA
    # ========================================================
    "Alola — Pokémon Ultra Sun/Ultra Moon": {
        "regiao": "Alola",
        "jogo": "Pokémon Ultra Sun / Ultra Moon",
        "time_padrao": ["incineroar", "vikavolt", "lycanroc", "mimikyu", "toxapex", "kommo-o"],
        "builds_padrao": {
            "incineroar": {"moves": ["flamethrower", "darkest-lariat", "brick-break", "thunder-punch"], "nature": "Adamant"},
            "vikavolt": {"moves": ["thunderbolt", "bug-buzz", "energy-ball", "volt-switch"], "nature": "Modest"},
            "lycanroc": {"moves": ["rock-slide", "crunch", "brick-break", "accelerock"], "nature": "Jolly"},
            "mimikyu": {"moves": ["play-rough", "shadow-claw", "wood-hammer", "swords-dance"], "nature": "Jolly"},
            "toxapex": {"moves": ["scald", "poison-jab", "toxic", "recover"], "nature": "Bold"},
            "kommo-o": {"moves": ["dragon-claw", "close-combat", "poison-jab", "swords-dance"], "nature": "Jolly"},
        },
        "desafios": [
            {"categoria": "Desafio", "nome": "Ilima", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Desafio", "nome": "Lana", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Desafio", "nome": "Mallow", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Desafio", "nome": "Kahili", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Desafio", "nome": "Acerola", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Desafio", "nome": "Nanu", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Elite Four", "nome": "Molayne", "tipo": "steel", "alvos": ["steel"]},
            {"categoria": "Elite Four", "nome": "Olivia", "tipo": "rock", "alvos": ["rock"]},
            {"categoria": "Elite Four", "nome": "Acerola", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Elite Four", "nome": "Kahili", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Campeão", "nome": "Treinador do jogador", "tipo": "mixed", "alvos": ["water", "rock", "psychic", "ghost", "dark", "flying"]},
        ],
    },

    # ========================================================
    # GALAR
    # ========================================================
    "Galar — Pokémon Sword/Shield": {
        "regiao": "Galar",
        "jogo": "Pokémon Sword / Shield",
        "time_padrao": ["inteleon", "corviknight", "toxtricity", "duraludon", "grimmsnarl", "dragapult"],
        "builds_padrao": {
            "inteleon": {"moves": ["surf", "ice-beam", "shadow-ball", "snipe-shot"], "nature": "Timid"},
            "corviknight": {"moves": ["brave-bird", "iron-head", "roost", "u-turn"], "nature": "Impish"},
            "toxtricity": {"moves": ["thunderbolt", "overdrive", "sludge-wave", "volt-switch"], "nature": "Modest"},
            "duraludon": {"moves": ["flash-cannon", "dragon-pulse", "thunderbolt", "dark-pulse"], "nature": "Modest"},
            "grimmsnarl": {"moves": ["play-rough", "spirit-break", "bulk-up", "sucker-punch"], "nature": "Adamant"},
            "dragapult": {"moves": ["dragon-darts", "shadow-ball", "u-turn", "flamethrower"], "nature": "Timid"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Milo", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Ginásio", "nome": "Nessa", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Ginásio", "nome": "Kabu", "tipo": "fire", "alvos": ["fire"]},
            {"categoria": "Ginásio", "nome": "Bea/Allister", "tipo": "fighting", "alvos": ["fighting", "ghost"]},
            {"categoria": "Ginásio", "nome": "Opal", "tipo": "fairy", "alvos": ["fairy"]},
            {"categoria": "Ginásio", "nome": "Gordie/Melony", "tipo": "rock", "alvos": ["rock", "ice"]},
            {"categoria": "Ginásio", "nome": "Piers", "tipo": "dark", "alvos": ["dark"]},
            {"categoria": "Ginásio", "nome": "Raihan", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Elite Four", "nome": "Liga de Galar", "tipo": "mixed", "alvos": ["fire", "water", "fighting", "fairy", "rock", "dragon"]},
            {"categoria": "Campeão", "nome": "Leon", "tipo": "mixed", "alvos": ["fire", "water", "flying", "ghost", "dragon", "grass"]},
        ],
    },

    # ========================================================
    # PALDEA
    # ========================================================
    "Paldea — Pokémon Scarlet/Violet": {
        "regiao": "Paldea",
        "jogo": "Pokémon Scarlet / Violet",
        "time_padrao": ["skeledirge", "clodsire", "tinkaton", "kilowattrel", "annihilape", "baxcalibur"],
        "builds_padrao": {
            "skeledirge": {"moves": ["torch-song", "shadow-ball", "earth-power", "will-o-wisp"], "nature": "Modest"},
            "clodsire": {"moves": ["earthquake", "poison-jab", "toxic", "recover"], "nature": "Careful"},
            "tinkaton": {"moves": ["gigaton-hammer", "play-rough", "knock-off", "thunder-wave"], "nature": "Adamant"},
            "kilowattrel": {"moves": ["thunderbolt", "hurricane", "volt-switch", "roost"], "nature": "Timid"},
            "annihilape": {"moves": ["rage-fist", "drain-punch", "bulk-up", "taunt"], "nature": "Jolly"},
            "baxcalibur": {"moves": ["glaive-rush", "icicle-crash", "earthquake", "dragon-dance"], "nature": "Jolly"},
        },
        "desafios": [
            {"categoria": "Ginásio", "nome": "Katy", "tipo": "bug", "alvos": ["bug"]},
            {"categoria": "Ginásio", "nome": "Brassius", "tipo": "grass", "alvos": ["grass"]},
            {"categoria": "Ginásio", "nome": "Iono", "tipo": "electric", "alvos": ["electric"]},
            {"categoria": "Ginásio", "nome": "Kofu", "tipo": "water", "alvos": ["water"]},
            {"categoria": "Ginásio", "nome": "Larry", "tipo": "normal", "alvos": ["normal"]},
            {"categoria": "Ginásio", "nome": "Ryme", "tipo": "ghost", "alvos": ["ghost"]},
            {"categoria": "Ginásio", "nome": "Tulip", "tipo": "psychic", "alvos": ["psychic"]},
            {"categoria": "Ginásio", "nome": "Grusha", "tipo": "ice", "alvos": ["ice"]},
            {"categoria": "Elite Four", "nome": "Rika", "tipo": "ground", "alvos": ["ground"]},
            {"categoria": "Elite Four", "nome": "Poppy", "tipo": "steel", "alvos": ["steel"]},
            {"categoria": "Elite Four", "nome": "Larry", "tipo": "flying", "alvos": ["flying"]},
            {"categoria": "Elite Four", "nome": "Hassel", "tipo": "dragon", "alvos": ["dragon"]},
            {"categoria": "Campeão", "nome": "Geeta", "tipo": "mixed", "alvos": ["rock", "steel", "psychic", "dark", "bug", "flying"]},
        ],
    },
}


def nome_exibicao_desafio(desafio):
    return f"{desafio['categoria']} • {desafio['nome']}"


def analisar_membro_contra_desafio(nome, build, desafio):
    dados = obter_dados_da_build(nome, build)
    if not dados:
        return {"score": -999, "ofensivo": [], "defensivo": 1.0, "dados": None}

    tipos = obter_tipos(dados)
    defesa_media = 1.0
    multiplicadores_def = []
    for alvo in desafio.get("alvos", []):
        mult = 1.0
        # Para alvos do Campeão, tratamos cada tipo como uma ameaça a ser
        # respondida. A parte defensiva continua sendo útil como heurística.
        for tipo_def in tipos:
            mult *= multiplicador_tipo(alvo, tipo_def)
        multiplicadores_def.append(mult)

    if multiplicadores_def:
        defesa_media = sum(multiplicadores_def) / len(multiplicadores_def)

    movimentos_bons = []
    for golpe in build.get("moves", []):
        if not golpe:
            continue
        info = buscar_movimento(golpe)
        if not info:
            continue
        tipo_golpe = info.get("type", {}).get("name", "")
        if not tipo_golpe:
            continue
        efetividades = [
            multiplicador_tipo(tipo_golpe, alvo)
            for alvo in desafio.get("alvos", [])
        ]
        melhor = max(efetividades, default=1.0)
        if melhor > 1:
            movimentos_bons.append({
                "golpe": golpe,
                "tipo": tipo_golpe,
                "efetividade": melhor
            })

    melhor_ofensiva = max((x["efetividade"] for x in movimentos_bons), default=1.0)
    # Score heurístico: ofensiva atual pesa mais que a defesa.
    score = (melhor_ofensiva * 4) + (sum(
        1 for tipo in tipos for alvo in desafio.get("alvos", [])
        if multiplicador_tipo(tipo, alvo) > 1
    ) * 1.5) - defesa_media

    return {
        "score": score,
        "ofensivo": movimentos_bons,
        "defensivo": defesa_media,
        "dados": dados
    }


# ============================================================
# EXPANSÃO DOS JOGOS POR GERAÇÃO / REGIÃO
# ============================================================
# Os perfis-base acima já possuem equipes, builds e desafios.
# Aqui criamos as demais versões/jogos como opções independentes
# no seletor, reaproveitando a mesma estrutura regional.

from copy import deepcopy


def adicionar_jogo_base(chave_base, chave_nova, nome_jogo):
    """Cria uma cópia independente de um perfil regional existente."""
    if chave_base not in JOGOS_REGIONAIS:
        return

    perfil = deepcopy(JOGOS_REGIONAIS[chave_base])
    perfil["jogo"] = nome_jogo
    JOGOS_REGIONAIS[chave_nova] = perfil


# ------------------------------------------------------------
# KANTO — GERAÇÃO I / REMAKES / LET'S GO
# ------------------------------------------------------------

JOGOS_REGIONAIS_EXTRAS = [
    ("Kanto — Pokémon Red", "Kanto — Pokémon Red", "Pokémon Red"),
    ("Kanto — Pokémon Blue", "Kanto — Pokémon Blue", "Pokémon Blue"),
    ("Kanto — Pokémon Yellow", "Kanto — Pokémon Yellow", "Pokémon Yellow"),
    ("Kanto — Pokémon LeafGreen", "Kanto — Pokémon LeafGreen", "Pokémon LeafGreen"),
    ("Kanto — Pokémon Let's Go, Pikachu!", "Kanto — Pokémon Let's Go, Pikachu!", "Pokémon Let's Go, Pikachu!"),
    ("Kanto — Pokémon Let's Go, Eevee!", "Kanto — Pokémon Let's Go, Eevee!", "Pokémon Let's Go, Eevee!"),

    # --------------------------------------------------------
    # JOHTO — GERAÇÃO II / REMAKES
    # --------------------------------------------------------
    ("Johto — Pokémon HeartGold", "Johto — Pokémon Gold", "Pokémon Gold"),
    ("Johto — Pokémon HeartGold", "Johto — Pokémon Silver", "Pokémon Silver"),
    ("Johto — Pokémon HeartGold", "Johto — Pokémon Crystal", "Pokémon Crystal"),
    ("Johto — Pokémon HeartGold", "Johto — Pokémon SoulSilver", "Pokémon SoulSilver"),

    # --------------------------------------------------------
    # HOENN — GERAÇÃO III / REMAKES
    # --------------------------------------------------------
    ("Hoenn — Pokémon Emerald", "Hoenn — Pokémon Ruby", "Pokémon Ruby"),
    ("Hoenn — Pokémon Emerald", "Hoenn — Pokémon Sapphire", "Pokémon Sapphire"),
    ("Hoenn — Pokémon Emerald", "Hoenn — Pokémon Omega Ruby", "Pokémon Omega Ruby"),
    ("Hoenn — Pokémon Emerald", "Hoenn — Pokémon Alpha Sapphire", "Pokémon Alpha Sapphire"),

    # --------------------------------------------------------
    # SINNOH / HISUI — GERAÇÃO IV / REMAKE / LEGENDS
    # --------------------------------------------------------
    ("Sinnoh — Pokémon Platinum", "Sinnoh — Pokémon Diamond", "Pokémon Diamond"),
    ("Sinnoh — Pokémon Platinum", "Sinnoh — Pokémon Pearl", "Pokémon Pearl"),
    ("Sinnoh — Pokémon Platinum", "Sinnoh — Pokémon Brilliant Diamond", "Pokémon Brilliant Diamond"),
    ("Sinnoh — Pokémon Platinum", "Sinnoh — Pokémon Shining Pearl", "Pokémon Shining Pearl"),
    ("Sinnoh — Pokémon Platinum", "Hisui — Pokémon Legends: Arceus", "Pokémon Legends: Arceus"),

    # --------------------------------------------------------
    # UNOVA — GERAÇÃO V
    # --------------------------------------------------------
    ("Unova — Pokémon White", "Unova — Pokémon Black", "Pokémon Black"),
    ("Unova — Pokémon White", "Unova — Pokémon White 2", "Pokémon White 2"),

    # --------------------------------------------------------
    # KALOS — GERAÇÃO VI / LEGENDS
    # --------------------------------------------------------
    ("Kalos — Pokémon X/Y", "Kalos — Pokémon X", "Pokémon X"),
    ("Kalos — Pokémon X/Y", "Kalos — Pokémon Y", "Pokémon Y"),
    ("Kalos — Pokémon X/Y", "Kalos — Pokémon Legends: Z-A", "Pokémon Legends: Z-A"),

    # --------------------------------------------------------
    # ALOLA — GERAÇÃO VII
    # --------------------------------------------------------
    ("Alola — Pokémon Ultra Sun/Ultra Moon", "Alola — Pokémon Sun", "Pokémon Sun"),
    ("Alola — Pokémon Ultra Sun/Ultra Moon", "Alola — Pokémon Moon", "Pokémon Moon"),
    ("Alola — Pokémon Ultra Sun/Ultra Moon", "Alola — Pokémon Ultra Sun", "Pokémon Ultra Sun"),
    ("Alola — Pokémon Ultra Sun/Ultra Moon", "Alola — Pokémon Ultra Moon", "Pokémon Ultra Moon"),

    # --------------------------------------------------------
    # GALAR — GERAÇÃO VIII
    # --------------------------------------------------------
    ("Galar — Pokémon Sword/Shield", "Galar — Pokémon Sword", "Pokémon Sword"),
    ("Galar — Pokémon Sword/Shield", "Galar — Pokémon Shield", "Pokémon Shield"),

    # --------------------------------------------------------
    # PALDEA — GERAÇÃO IX
    # --------------------------------------------------------
    ("Paldea — Pokémon Scarlet/Violet", "Paldea — Pokémon Scarlet", "Pokémon Scarlet"),
    ("Paldea — Pokémon Scarlet/Violet", "Paldea — Pokémon Violet", "Pokémon Violet"),
]


for chave_base, chave_nova, nome_jogo in JOGOS_REGIONAIS_EXTRAS:
    adicionar_jogo_base(
        chave_base,
        chave_nova,
        nome_jogo
    )


# ============================================================
# DADOS DO POKÉMON CHAMPIONS
# ============================================================

CHAMPIONS_REGULAMENTOS = {
    "M-C": {
        "periodo": "Regulation M-C",
        "status": "Atual / competitivo",
        "formatos": ["Singles", "Doubles"],
        "descricao": (
            "Regulation Set competitivo de Pokémon Champions. "
            "A equipe é definida pelo jogador e pode ser modificada livremente. "
            "As regras do formato devem ser consultadas conforme a regulamentação ativa."
        ),
    },
    "M-B": {
        "periodo": "Regulation M-B",
        "status": "Histórica",
        "formatos": ["Singles", "Doubles"],
        "descricao": (
            "Regulation Set anterior, mantido como referência histórica "
            "para comparação de equipes e builds."
        ),
    },
}

CHAMPIONS_PERFIS = {
    "Meu time — Singles": {
        "formato": "Singles",
        "regulacao": "M-C",
        "time_padrao": [
            "lucario", "garchomp", "rotom-wash",
            "ceruledge", "alolan-ninetales", "sceptile"
        ],
        "observacao": (
            "Perfil livre para testar uma equipe competitiva própria. "
            "Troque os seis Pokémon, formas, itens, habilidades, Tera Types "
            "e golpes conforme sua estratégia."
        ),
    },
    "Equipe teste — Singles": {
        "formato": "Singles",
        "regulacao": "M-C",
        "time_padrao": [
            "lucario", "garchomp", "dragonite",
            "rotom-wash", "ceruledge", "alolan-ninetales"
        ],
        "observacao": (
            "Preset de teste para experimentar diferentes núcleos, "
            "formas e combinações de moveset."
        ),
    },
    "Meu time — Doubles": {
        "formato": "Doubles",
        "regulacao": "M-C",
        "time_padrao": [
            "incineroar", "amoonguss", "garchomp",
            "grimmsnarl", "gardevoir", "kingambit"
        ],
        "observacao": (
            "Perfil livre para testes em batalhas Double. "
            "A análise do time continua disponível, mas estratégias específicas "
            "de posicionamento e movimentos em dupla podem ser acrescentadas depois."
        ),
    },
}

# ============================================================
# ABAS PRINCIPAIS
# ============================================================

(aba_montador, aba_builds, aba_analise, aba_jogos,
 aba_champions, aba_dano, aba_comparar, aba_salvos, aba_io) = st.tabs([
    "⚔️ Montador",
    "🧬 Builds",
    "📊 Análise",
    "🎮 Jogo / Região",
    "⚔️ Pokémon Champions",
    "🧮 Dano",
    "🔎 Comparar",
    "💾 Times Salvos",
    "📋 Importar / Exportar",
])


# ============================================================
# TIMES POR JOGO / REGIÃO
# ============================================================

with aba_jogos:
    st.header("🎮 Times por Jogo / Região")
    st.write(
        "Monte ou carregue um time temático de um jogo específico e veja quais membros do time têm melhor encaixe contra cada Ginásio, Elite Four e Campeão, usando tipagem e os golpes configurados na build."
    )

    if not JOGOS_REGIONAIS:
        st.info("Nenhum preset regional foi configurado ainda.")
    else:
        jogo_escolhido = st.selectbox(
            "🎮 Jogo / região",
            list(JOGOS_REGIONAIS.keys()),
            key="jogo_regional_selecionado_v5"
        )
        perfil_jogo = JOGOS_REGIONAIS[jogo_escolhido]

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"🌎 {perfil_jogo['regiao']} • {perfil_jogo['jogo']}")
            st.write("Time sugerido para o perfil selecionado:")
            st.code(" • ".join(nome_bonito(p) for p in perfil_jogo["time_padrao"]))
        with col2:
            if st.button(
                "📥 Carregar time sugerido",
                type="primary",
                use_container_width=True,
                key="carregar_preset_regional_v5"
            ):
                st.session_state.time_atual = list(perfil_jogo["time_padrao"])[:MAX_TEAM_SIZE]
                for nome_preset in st.session_state.time_atual:
                    dados_preset = buscar_pokemon(nome_preset)
                    build = build_padrao(nome_preset, dados_preset)
                    build.update(perfil_jogo.get("builds_padrao", {}).get(nome_preset, {}))
                    st.session_state.builds[normalizar_nome(nome_preset)] = normalizar_build(
                        build, nome_preset, dados_preset
                    )
                st.session_state.time_nome = perfil_jogo["jogo"]
                st.success("✅ Time carregado! Vá para a aba Builds para conferir formas e ajustes.")

        st.divider()
        st.subheader("🏆 Scout por Ginásio, Elite Four e Campeão")

        if not st.session_state.time_atual:
            st.info("Adicione ou carregue um time para gerar o scout.")
        else:
            filtros = st.multiselect(
                "Filtrar por categoria",
                ["Ginásio", "Elite Four", "Campeão"],
                default=["Ginásio", "Elite Four", "Campeão"],
                key="filtro_desafios_v5"
            )

            desafios_filtrados = [
                d for d in perfil_jogo["desafios"]
                if d["categoria"] in filtros
            ]

            for desafio in desafios_filtrados:
                avaliados = []
                for nome_pokemon in st.session_state.time_atual:
                    build = garantir_build(nome_pokemon)
                    avaliacao = analisar_membro_contra_desafio(
                        nome_pokemon, build, desafio
                    )
                    avaliacao["nome"] = nome_pokemon
                    avaliados.append(avaliacao)

                avaliados.sort(key=lambda x: x["score"], reverse=True)

                icone = (
                    "🏆" if desafio["categoria"] == "Ginásio"
                    else "👑" if desafio["categoria"] == "Elite Four"
                    else "🥇"
                )
                with st.expander(f"{icone} {nome_exibicao_desafio(desafio)}"):
                    alvo_texto = (
                        traduzir_tipo(desafio["tipo"])
                        if desafio["tipo"] != "mixed"
                        else "Time misto"
                    )
                    st.write(f"**Especialidade / alvo principal:** {alvo_texto}")

                    if not avaliados:
                        st.info("Nenhum Pokémon disponível no time para analisar.")
                        continue

                    cols = st.columns(min(3, len(avaliados)))
                    for i, item in enumerate(avaliados[:3]):
                        with cols[i % len(cols)]:
                            nome = item["nome"]
                            build = garantir_build(nome)
                            st.markdown(f"### {nome_bonito(nome)}")
                            if item["dados"]:
                                sprite = obter_sprite(
                                    item["dados"], build.get("shiny", False)
                                )
                                if sprite:
                                    st.image(sprite, width=130)
                                st.caption(
                                    " / ".join(
                                        traduzir_tipo(t)
                                        for t in obter_tipos(item["dados"])
                                    )
                                )
                            if item["ofensivo"]:
                                melhores = sorted(
                                    item["ofensivo"],
                                    key=lambda x: -x["efetividade"]
                                )[:3]
                                for melhor in melhores:
                                    st.write(
                                        f"🎯 {nome_bonito(melhor['golpe'])} • "
                                        f"{traduzir_tipo(melhor['tipo'])} • "
                                        f"{melhor['efetividade']}x"
                                    )
                            else:
                                st.write(
                                    "🎯 Nenhum golpe configurado aparece como "
                                    "super efetivo contra os alvos deste desafio."
                                )
                            st.caption(f"Índice heurístico: {item['score']:.1f}")

                    melhor = avaliados[0]
                    if melhor["dados"]:
                        st.success(
                            f"⭐ Melhor encaixe atual: {nome_bonito(melhor['nome'])}. "
                            "A análise considera tipagem defensiva e os golpes configurados na build."
                        )

        st.divider()
        st.subheader("💡 Como usar")
        st.info(
            "Escolha um jogo, carregue o time sugerido ou use o seu próprio time. "
            "Depois, configure golpes, itens e formas na aba Builds; o scout usa essas informações para ranquear os melhores encaixes."
        )


# ============================================================
# POKÉMON CHAMPIONS
# ============================================================

with aba_champions:
    st.header("⚔️ Pokémon Champions")
    st.write(
        "Espaço competitivo separado das campanhas. Aqui o adversário é outro jogador, "
        "então a equipe é totalmente editável e não depende de Ginásios, Elite Four ou Campeão."
    )

    regulacao = st.selectbox(
        "📜 Regulation Set",
        list(CHAMPIONS_REGULAMENTOS.keys()),
        key="champ_regulacao_v2"
    )
    dados_reg = CHAMPIONS_REGULAMENTOS[regulacao]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📅 Período", dados_reg["periodo"])
    with c2:
        st.metric("🏷️ Status", dados_reg["status"])
    with c3:
        st.metric("⚔️ Formatos", " / ".join(dados_reg["formatos"]))

    st.info(dados_reg["descricao"])

    perfil_nome = st.selectbox(
        "🎮 Perfil competitivo / preset inicial",
        list(CHAMPIONS_PERFIS.keys()),
        key="champ_perfil_v2"
    )
    perfil = CHAMPIONS_PERFIS[perfil_nome]

    # Cada perfil possui sua própria equipe editável.
    if st.session_state.champions_perfil_ativo != perfil_nome:
        st.session_state.champions_perfil_ativo = perfil_nome
        if perfil_nome not in st.session_state.champions_times:
            st.session_state.champions_times[perfil_nome] = list(perfil["time_padrao"])[:MAX_TEAM_SIZE]
            for nome_preset in st.session_state.champions_times[perfil_nome]:
                dados_preset = buscar_pokemon(nome_preset)
                build = build_padrao(nome_preset, dados_preset)
                st.session_state.builds[normalizar_nome(nome_preset)] = build

    time_champions = st.session_state.champions_times[perfil_nome]

    st.subheader(f"⚔️ {perfil['formato']} • {perfil['regulacao']}")
    st.write(perfil["observacao"])
    st.caption("💡 Troque, remova, adicione Pokémon e escolha formas regionais, Mega Evoluções, Gigantamax, variantes e outras formas disponíveis.")

    # --------------------------------------------------------
    # EQUIPE CHAMPIONS — TOTALMENTE EDITÁVEL
    # --------------------------------------------------------
    if time_champions:
        for i, nome_pokemon in enumerate(list(time_champions)):
            build = garantir_build(nome_pokemon)
            formas = listar_formas_completas(nome_pokemon)
            opcoes_formas = [f["nome"] for f in formas] or [normalizar_nome(nome_pokemon)]
            form_atual = normalizar_nome(build.get("form", nome_pokemon))
            if form_atual not in opcoes_formas:
                opcoes_formas.insert(0, form_atual)

            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    novo_nome = st.text_input(
                        f"Pokémon #{i + 1}",
                        value=nome_pokemon,
                        key=f"champ_nome_{normalizar_nome(perfil_nome)}_{i}"
                    ).strip()
                with c2:
                    forma = st.selectbox(
                        "✨ Forma / Transformação",
                        opcoes_formas,
                        index=opcoes_formas.index(form_atual),
                        format_func=lambda x, base=nome_pokemon: nome_da_forma(x, base),
                        key=f"champ_forma_{normalizar_nome(perfil_nome)}_{i}"
                    )
                with c3:
                    remover = st.button(
                        "❌ Remover",
                        key=f"champ_remover_{normalizar_nome(perfil_nome)}_{i}",
                        use_container_width=True
                    )

                if st.button(
                    "🔄 Aplicar Pokémon / forma",
                    key=f"champ_aplicar_{normalizar_nome(perfil_nome)}_{i}",
                    use_container_width=True
                ):
                    alvo = normalizar_nome(novo_nome)
                    dados_alvo = buscar_pokemon(alvo) if alvo else None
                    if not dados_alvo:
                        st.error("❌ Pokémon não encontrado.")
                    else:
                        nome_api = dados_alvo.get("name", alvo)
                        time_champions[i] = nome_api
                        st.session_state.champions_times[perfil_nome] = time_champions
                        build_nova = garantir_build(nome_api)
                        formas_novas = listar_formas_completas(nome_api)
                        slugs_novos = [f["nome"] for f in formas_novas]
                        build_nova["form"] = forma if forma in slugs_novos else normalizar_nome(nome_api)
                        dados_forma = buscar_pokemon(build_nova["form"]) or dados_alvo
                        habilidades = obter_ability_names(dados_forma)
                        if habilidades and build_nova.get("ability") not in habilidades:
                            build_nova["ability"] = habilidades[0]
                        st.session_state.builds[normalizar_nome(nome_api)] = normalizar_build(build_nova, nome_api, dados_forma)
                        st.success(f"✅ Slot {i + 1} atualizado.")

                if remover:
                    time_champions.pop(i)
                    st.session_state.champions_times[perfil_nome] = time_champions
                    st.rerun()

        st.write(f"**Equipe atual:** {len(time_champions)}/{MAX_TEAM_SIZE}")
    else:
        st.info("A equipe Champions está vazia. Adicione seus Pokémon abaixo.")

    col_add, col_btn = st.columns([4, 1])
    with col_add:
        adicionar_champions = st.text_input(
            "➕ Adicionar Pokémon à equipe Champions",
            placeholder="Ex.: Lucario, Garchomp, Dragapult...",
            key=f"champ_add_{normalizar_nome(perfil_nome)}"
        )
    with col_btn:
        st.write("")
        if st.button(
            "➕ Adicionar",
            key=f"champ_add_btn_{normalizar_nome(perfil_nome)}",
            use_container_width=True,
            disabled=len(time_champions) >= MAX_TEAM_SIZE
        ):
            nome_add = normalizar_nome(adicionar_champions)
            dados_add = buscar_pokemon(nome_add) if nome_add else None
            if not dados_add:
                st.error("❌ Pokémon não encontrado.")
            else:
                nome_api = dados_add.get("name", nome_add)
                if normalizar_nome(nome_api) in [normalizar_nome(p) for p in time_champions]:
                    st.warning("⚠️ Esse Pokémon já está na equipe.")
                else:
                    time_champions.append(nome_api)
                    st.session_state.champions_times[perfil_nome] = time_champions
                    st.session_state.builds[normalizar_nome(nome_api)] = build_padrao(nome_api, dados_add)
                    st.rerun()

    if st.button(
        "♻️ Restaurar preset deste perfil",
        key=f"champ_reset_{normalizar_nome(perfil_nome)}",
        use_container_width=True
    ):
        st.session_state.champions_times[perfil_nome] = list(perfil["time_padrao"])[:MAX_TEAM_SIZE]
        for nome_preset in st.session_state.champions_times[perfil_nome]:
            dados_preset = buscar_pokemon(nome_preset)
            st.session_state.builds[normalizar_nome(nome_preset)] = build_padrao(nome_preset, dados_preset)
        st.rerun()

    # --------------------------------------------------------
    # VISÃO DOS MEMBROS ATUAIS
    # --------------------------------------------------------
    st.divider()
    st.subheader("👥 Equipe Champions atual")
    if time_champions:
        colunas = st.columns(3)
        for i, pokemon in enumerate(time_champions):
            build = garantir_build(pokemon)
            dados = obter_dados_da_build(pokemon, build)
            with colunas[i % 3]:
                with st.container(border=True):
                    if dados:
                        sprite = obter_sprite(dados, build.get("shiny", False))
                        if sprite:
                            st.image(sprite, width=140)
                        st.markdown(f"### {nome_bonito(pokemon)}")
                        if normalizar_nome(build.get("form", pokemon)) != normalizar_nome(pokemon):
                            st.caption(f"✨ {nome_da_forma(build['form'], pokemon)}")
                        tipos = obter_tipos(dados)
                        if tipos:
                            st.caption(" / ".join(traduzir_tipo(t) for t in tipos))
                        st.write(f"🧬 {nome_bonito(build.get('ability', '')) or '—'}")
                        st.write(f"🎒 {build.get('item', 'Nenhum')}")
                        st.write(f"✨ Tera: {'Automático' if build.get('tera') == 'auto' else traduzir_tipo(build.get('tera'))}")

    # --------------------------------------------------------
    # DIAGNÓSTICO DA EQUIPE ATUAL — NÃO DO PRESET
    # --------------------------------------------------------
    st.divider()
    st.subheader("🧠 Diagnóstico competitivo da equipe atual")

    dados_time_champions = []
    for pokemon in time_champions:
        build = garantir_build(pokemon)
        dados = obter_dados_da_build(pokemon, build)
        if dados:
            dados_time_champions.append(dados)

    if dados_time_champions:
        defesas = analisar_defesas(dados_time_champions)
        fraquezas = {tipo: d["fracos"] for tipo, d in defesas.items() if d["fracos"]}
        resistencias = {tipo: d["resistentes"] for tipo, d in defesas.items() if d["resistentes"]}
        imunidades = {tipo: d["imunes"] for tipo, d in defesas.items() if d["imunes"]}

        x1, x2, x3 = st.columns(3)
        with x1:
            st.markdown("#### ⚠️ Vulnerabilidades")
            for tipo, qtd in sorted(fraquezas.items(), key=lambda p: (-p[1], p[0])):
                st.write(f"**{traduzir_tipo(tipo)}:** {qtd}/{len(dados_time_champions)}")
        with x2:
            st.markdown("#### 🛡️ Resistências")
            for tipo, qtd in sorted(resistencias.items(), key=lambda p: (-p[1], p[0])):
                st.write(f"**{traduzir_tipo(tipo)}:** {qtd}/{len(dados_time_champions)}")
        with x3:
            st.markdown("#### 🚫 Imunidades")
            for tipo, qtd in sorted(imunidades.items(), key=lambda p: (-p[1], p[0])):
                st.write(f"**{traduzir_tipo(tipo)}:** {qtd}/{len(dados_time_champions)}")

    st.divider()
    st.info(
        "No Champions, esta equipe é independente das equipes de campanha. "
        "Você pode montar uma composição totalmente própria, incluindo formas e transformações, "
        "e depois configurar EVs, IVs, Nature, Ability, Item, Tera Type e golpes na aba 🧬 Builds."
    )


# ============================================================
# DANO
# ============================================================

def calcular_dano_simples(atacante, defensor, movimento, build_atk, build_def, stats_atk, stats_def):
    if not movimento or not stats_atk or not stats_def:
        return None
    poder = movimento.get("power")
    categoria = movimento.get("damage_class", {}).get("name")
    tipo_golpe = movimento.get("type", {}).get("name")
    if not poder or categoria not in {"physical", "special"} or not tipo_golpe:
        return {"erro": "Esse golpe não possui dano direto calculável nesta versão."}
    ataque = stats_atk["attack"] if categoria == "physical" else stats_atk["special-attack"]
    defesa = stats_def["defense"] if categoria == "physical" else stats_def["special-defense"]
    level = build_atk["level"]
    base = math.floor(math.floor(2 * level / 5 + 2) * poder * ataque / max(1, defesa) / 50) + 2
    stab = 1.5 if tipo_golpe in obter_tipos(atacante) else 1.0
    efet = 1.0
    for tipo in obter_tipos(defensor):
        efet *= multiplicador_tipo(tipo_golpe, tipo)
    item = str(build_atk.get("item", "Nenhum")).lower()
    item_mult = 1.3 if item == "life orb" else 1.0
    if item == "expert belt" and efet > 1:
        item_mult = 1.2
    if build_atk.get("tera") not in {"auto", "Nenhum"} and build_atk.get("tera") == tipo_golpe:
        stab = 2.0 if tipo_golpe not in obter_tipos(atacante) else 2.0
    dano_min = math.floor(base * stab * efet * item_mult * 0.85)
    dano_max = math.floor(base * stab * efet * item_mult)
    hp = stats_def["hp"]
    pct_min = (dano_min / hp) * 100 if hp else 0
    pct_max = (dano_max / hp) * 100 if hp else 0
    return {
        "dano_min": max(0, dano_min), "dano_max": max(0, dano_max),
        "pct_min": pct_min, "pct_max": pct_max,
        "efetividade": efet, "stab": stab, "categoria": categoria,
        "tipo": tipo_golpe, "poder": poder
    }

# ============================================================
# EXPORTAR / IMPORTAR
# ============================================================

def exportar_time_showdown():
    blocos = []
    for nome in st.session_state.time_atual:
        build = garantir_build(nome)
        dados = obter_dados_da_build(nome, build)
        cabecalho = nome_bonito(nome)
        if build.get("form") and normalizar_nome(build.get("form")) != normalizar_nome(nome):
            cabecalho += f" [{nome_da_forma(build['form'], nome)}]"
        linhas = [f"{cabecalho} @ {build['item']}" if build["item"] != "Nenhum" else cabecalho]
        if build.get("ability"):
            linhas.append(f"Ability: {nome_bonito(build['ability'])}")
        if build.get("form") and normalizar_nome(build.get("form")) != normalizar_nome(nome):
            linhas.append(f"Form: {build['form']}")
        if build.get("tera") not in {None, "auto", "Nenhum"}:
            linhas.append(f"Tera Type: {nome_bonito(build['tera'])}")
        ev_texto = []
        for stat in STAT_KEYS:
            ev = int(build["evs"].get(stat, 0))
            if ev:
                abre = {"hp": "HP", "attack": "Atk", "defense": "Def", "special-attack": "SpA", "special-defense": "SpD", "speed": "Spe"}[stat]
                ev_texto.append(f"{ev} {abre}")
        if ev_texto:
            linhas.append("EVs: " + " / ".join(ev_texto))
        linhas.append(f"{build['nature']} Nature")
        for move in build.get("moves", []):
            if move:
                linhas.append(f"- {nome_bonito(move)}")
        blocos.append("\n".join(linhas))
    return "\n\n".join(blocos)


def parsear_importacao_showdown(texto):
    resultados = []
    bloco_atual = None
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("-"):
            if bloco_atual and len(bloco_atual["moves"]) < 4:
                bloco_atual["moves"].append(normalizar_nome(linha[1:].strip()))
            continue
    # Segunda passagem para atributos e golpes
    resultados = []
    blocos = re.split(r"\n\s*\n", texto)
    for bloco in blocos:
        linhas = [x.strip() for x in bloco.splitlines() if x.strip()]
        if not linhas:
            continue
        cab = linhas[0]
        if " @ " in cab:
            nome_raw, item = cab.split(" @ ", 1)
        else:
            nome_raw, item = cab, "Nenhum"
        nome = normalizar_nome(nome_raw)
        dados = buscar_pokemon(nome)
        if not dados:
            continue
        build = build_padrao(nome, dados)
        build["item"] = item.strip()
        for linha in linhas[1:]:
            lower = linha.lower()
            if lower.startswith("form:"):
                build["form"] = normalizar_nome(linha.split(":", 1)[1].strip())
            elif lower.startswith("ability:"):
                build["ability"] = normalizar_nome(linha.split(":", 1)[1].strip())
            elif lower.startswith("tera type:"):
                build["tera"] = normalizar_nome(linha.split(":", 1)[1].strip())
            elif lower.endswith("nature"):
                natureza = linha.rsplit(" ", 1)[0].strip()
                if natureza in NATURES:
                    build["nature"] = natureza
            elif lower.startswith("evs:"):
                conteudo = linha.split(":", 1)[1]
                mapa = {"hp": "hp", "atk": "attack", "def": "defense", "spa": "special-attack", "spd": "special-defense", "spe": "speed"}
                for parte in conteudo.split("/"):
                    m = re.search(r"(\d+)\s*(HP|Atk|Def|SpA|SpD|Spe)", parte, re.I)
                    if m:
                        build["evs"][mapa[m.group(2).lower()]] = int(m.group(1))
            elif linha.startswith("-"):
                if len([m for m in build["moves"] if m]) < 4:
                    build["moves"][len([m for m in build["moves"] if m])] = normalizar_nome(linha[1:].strip())
        resultados.append((nome, build))
    return resultados[:MAX_TEAM_SIZE]


# ============================================================
# MONTADOR
# ============================================================

with aba_montador:
    st.header("⚔️ Montador de Time")
    st.write(f"**Time atual: {len(st.session_state.time_atual)}/{MAX_TEAM_SIZE}**")

    col_busca, col_acoes = st.columns([4, 2])
    with col_busca:
        consulta = st.text_input("🔎 Pokémon para adicionar", placeholder="Ex.: Lucario, Pikachu, 448", key="busca_adicionar_v3")
    with col_acoes:
        st.write("")
        if st.button("➕ Adicionar", use_container_width=True, disabled=(len(st.session_state.time_atual) >= MAX_TEAM_SIZE)):
            consulta_norm = normalizar_nome(consulta)
            dados = buscar_pokemon(consulta_norm) if consulta_norm else None
            if not dados:
                st.error("❌ Pokémon não encontrado.")
            else:
                nome_api = dados.get("name", consulta_norm)
                if nome_api in [normalizar_nome(p) for p in st.session_state.time_atual]:
                    st.warning("⚠️ Esse Pokémon já está no time.")
                elif len(st.session_state.time_atual) >= MAX_TEAM_SIZE:
                    st.warning("⚠️ O time já possui 6 Pokémon.")
                else:
                    st.session_state.time_atual.append(nome_api)
                    st.session_state.builds[normalizar_nome(nome_api)] = build_padrao(nome_api, dados)
                    st.rerun()

    if st.button("🗑️ Limpar time", use_container_width=True):
        st.session_state.time_atual = []
        st.rerun()

    st.divider()

    if not st.session_state.time_atual:
        st.info("Seu time está vazio. Adicione até 6 Pokémon para começar.")
    else:
        colunas = st.columns(3)
        for i, nome in enumerate(st.session_state.time_atual):
            build = garantir_build(nome)
            dados = obter_dados_da_build(nome, build)
            with colunas[i % 3]:
                with st.container(border=True):
                    titulo = f"### #{i + 1} • {nome_bonito(nome)}"
                    if build.get("form") and normalizar_nome(build.get("form")) != normalizar_nome(nome):
                        titulo += f" • {nome_da_forma(build['form'], nome)}"
                    st.markdown(titulo)
                    sprite = obter_sprite(dados, build.get("shiny", False))
                    if sprite:
                        st.image(sprite, width=180)
                    tipos = obter_tipos(dados)
                    st.caption(" / ".join(traduzir_tipo(t) for t in tipos))
                    if build.get("ability"):
                        st.caption(f"🧬 {nome_bonito(build['ability'])}")
                    if build.get("item") and build["item"] != "Nenhum":
                        st.caption(f"🎒 {build['item']}")
                    st.write(f"**Nível:** {build['level']} • **Nature:** {build['nature']}")
                    if st.button("❌ Remover", key=f"remover_v3_{i}_{normalizar_nome(nome)}", use_container_width=True):
                        st.session_state.time_atual.pop(i)
                        st.rerun()

# ============================================================
# BUILDS
# ============================================================

with aba_builds:
    st.header("🧬 Builds Competitivas")
    if not st.session_state.time_atual:
        st.info("Adicione Pokémon ao time para configurar suas builds.")
    else:
        escolhido = st.selectbox(
            "Escolha um Pokémon do time:",
            st.session_state.time_atual,
            format_func=nome_bonito,
            key="pokemon_build_selecionado_v3"
        )
        build = garantir_build(escolhido)
        dados_base = buscar_pokemon(escolhido)
        formas_api = listar_formas_completas(escolhido)
        formas_opcoes = [f["nome"] for f in formas_api] or [normalizar_nome(escolhido)]
        if build.get("form") not in formas_opcoes:
            build["form"] = normalizar_nome(escolhido)
            st.session_state.builds[normalizar_nome(escolhido)] = build
        dados = buscar_pokemon(build.get("form", escolhido)) or dados_base
        chave = normalizar_nome(escolhido)

        col1, col2 = st.columns([1, 2])
        with col1:
            sprite = obter_sprite(dados, build.get("shiny", False))
            if sprite:
                st.image(sprite, width=220)
            st.markdown(f"### {nome_bonito(escolhido)}")
            st.caption(f"Forma: {nome_da_forma(build.get('form', escolhido), escolhido)}")
            st.caption(" / ".join(traduzir_tipo(t) for t in obter_tipos(dados)))
        with col2:
            level = st.number_input("Nível", 1, 100, int(build["level"]), key=f"level_build_{chave}")
            forma = st.selectbox(
                "✨ Forma / Transformação",
                formas_opcoes,
                index=formas_opcoes.index(build.get("form", normalizar_nome(escolhido))),
                format_func=lambda x: "Forma Base" if x == normalizar_nome(escolhido) else nome_da_forma(x, escolhido),
                key=f"forma_build_{chave}"
            )
            natureza = st.selectbox("🌿 Nature", list(NATURES.keys()), index=list(NATURES.keys()).index(build["nature"]) if build["nature"] in NATURES else 0, key=f"nature_build_{chave}")
            habilidades = obter_ability_names(dados)
            habilidade = st.selectbox("🧬 Ability", habilidades or ["Nenhuma"], index=habilidades.index(build["ability"]) if build["ability"] in habilidades else 0, format_func=nome_bonito, key=f"ability_build_{chave}")
            item = st.selectbox("🎒 Item", ITENS_COMUNS, index=ITENS_COMUNS.index(build["item"]) if build["item"] in ITENS_COMUNS else 0, key=f"item_build_{chave}")
            tera_opcoes = ["auto"] + TIPOS
            tera = st.selectbox("✨ Tera Type", tera_opcoes, index=tera_opcoes.index(build["tera"]) if build["tera"] in tera_opcoes else 0, format_func=lambda x: "Automático" if x == "auto" else traduzir_tipo(x), key=f"tera_build_{chave}")
            shiny = st.checkbox("✨ Usar sprite Shiny", value=bool(build.get("shiny", False)), key=f"shiny_build_{chave}")

        st.divider()
        st.subheader("📊 EVs e IVs")
        cols = st.columns(3)
        for idx, stat in enumerate(STAT_KEYS):
            with cols[idx % 3]:
                st.markdown(f"**{STAT_LABELS[stat]}**")
                st.number_input("EV", min_value=0, max_value=252, value=int(build["evs"].get(stat, 0)), step=4, key=f"ev_{chave}_{stat}")
                st.number_input("IV", min_value=0, max_value=31, value=int(build["ivs"].get(stat, 31)), key=f"iv_{chave}_{stat}")

        st.caption(f"Total de EVs: {sum(int(build['evs'].get(s, 0)) for s in STAT_KEYS)} / 510")
        if sum(int(build['evs'].get(s, 0)) for s in STAT_KEYS) > 510:
            st.error("❌ A soma de EVs excede 510.")
        elif any(int(build['evs'].get(s, 0)) > 252 for s in STAT_KEYS):
            st.error("❌ Um stat possui EVs acima de 252.")
        else:
            st.success("✅ Distribuição de EVs válida dentro dos limites configurados.")

        st.divider()
        st.subheader("🎯 Moveset")
        movimentos_disponiveis = obter_movimentos_disponiveis(dados)
        opcoes_movimentos = [""] + movimentos_disponiveis
        nova_lista = []
        cols = st.columns(2)
        for slot in range(4):
            valor = build["moves"][slot] if slot < len(build["moves"]) else ""
            with cols[slot % 2]:
                selecionado = st.selectbox(
                    f"Golpe {slot + 1}",
                    opcoes_movimentos,
                    index=opcoes_movimentos.index(valor) if valor in opcoes_movimentos else 0,
                    format_func=lambda x: "— Sem golpe —" if not x else nome_bonito(x),
                    key=f"move_build_{chave}_{slot}"
                )
                nova_lista.append(selecionado)
                if selecionado:
                    info_move = buscar_movimento(selecionado)
                    if info_move:
                        tipo = info_move.get("type", {}).get("name", "")
                        poder = info_move.get("power")
                        precisao = info_move.get("accuracy")
                        categoria = info_move.get("damage_class", {}).get("name", "")
                        st.caption(f"{traduzir_tipo(tipo)} • {CATEGORIAS_GOLPES.get(categoria, nome_bonito(categoria))} • Poder: {poder or '—'} • Precisão: {precisao or '—'}")

        st.divider()
        build_preview = normalizar_build({**build, "form": forma, "level": level, "nature": natureza}, escolhido, dados)
        stats = calcular_stats_build(dados, build_preview)
        st.subheader("📈 Stats calculados")
        cols = st.columns(3)
        for idx, stat in enumerate(STAT_KEYS):
            with cols[idx % 3]:
                st.metric(STAT_LABELS[stat], stats.get(stat, 0))

        if st.button("💾 Aplicar alterações nesta build", type="primary", use_container_width=True):
            st.session_state.builds[chave] = normalizar_build({
                "level": level,
                "form": forma,
                "nature": natureza,
                "ability": habilidade if habilidade != "Nenhuma" else "",
                "item": item,
                "tera": tera,
                "shiny": shiny,
                "evs": {stat: st.session_state[f"ev_{chave}_{stat}"] for stat in STAT_KEYS},
                "ivs": {stat: st.session_state[f"iv_{chave}_{stat}"] for stat in STAT_KEYS},
                "moves": nova_lista,
            }, escolhido, dados)
            st.success(f"✅ Build de {nome_bonito(escolhido)} atualizada!")

# ============================================================
# ANÁLISE
# ============================================================

with aba_analise:
    st.header("📊 Análise do Time")
    dados_time = []
    builds_time = []
    nomes_time = []
    for nome_pokemon in st.session_state.time_atual:
        build = garantir_build(nome_pokemon)
        dados = obter_dados_da_build(nome_pokemon, build)
        if dados:
            dados_time.append(dados)
            builds_time.append(build)
            nomes_time.append(nome_pokemon)

    if not dados_time:
        st.info("Adicione Pokémon ao time para gerar a análise.")
    else:
        tipos_contagem = {}
        for dados in dados_time:
            for tipo in obter_tipos(dados):
                tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1
        if tipos_contagem:
            st.subheader("📋 Composição por tipo")
            cols = st.columns(min(6, len(tipos_contagem)))
            for i, (tipo, qtd) in enumerate(sorted(tipos_contagem.items(), key=lambda x: (-x[1], x[0]))):
                with cols[i % len(cols)]:
                    st.metric(traduzir_tipo(tipo), qtd)

        st.divider()
        defesas = analisar_defesas(dados_time)
        col_f, col_r, col_i = st.columns(3)
        with col_f:
            st.subheader("⚠️ Fraquezas")
            for tipo, d in sorted(defesas.items(), key=lambda x: (-x[1]["fracos"], x[0])):
                if d["fracos"]:
                    texto = f"**{traduzir_tipo(tipo)}:** {d['fracos']}"
                    if d["dupla"]:
                        texto += f" • 🔴 {d['dupla']} com 4x+"
                    st.write(texto)
        with col_r:
            st.subheader("🛡️ Resistências")
            for tipo, d in sorted(defesas.items(), key=lambda x: (-x[1]["resistentes"], x[0])):
                if d["resistentes"]:
                    st.write(f"**{traduzir_tipo(tipo)}:** {d['resistentes']}")
        with col_i:
            st.subheader("🚫 Imunidades")
            for tipo, d in sorted(defesas.items(), key=lambda x: (-x[1]["imunes"], x[0])):
                if d["imunes"]:
                    st.write(f"**{traduzir_tipo(tipo)}:** {d['imunes']}")

        st.divider()
        st.subheader("🎯 Cobertura ofensiva por STAB")
        cobertura = analisar_cobertura(dados_time)
        for tipo, qtd in sorted(cobertura.items(), key=lambda x: (-x[1], x[0])):
            if qtd:
                st.write(f"**{traduzir_tipo(tipo)}:** {qtd} Pokémon possuem STAB super efetivo contra esse tipo")

        st.divider()
        st.subheader("📈 Médias do time")
        stats_time = [calcular_stats_build(d, b) for d, b in zip(dados_time, builds_time)]
        medias = {s: round(sum(x.get(s, 0) for x in stats_time) / len(stats_time)) for s in STAT_KEYS}
        cols = st.columns(3)
        for i, stat in enumerate(STAT_KEYS):
            with cols[i % 3]:
                st.metric(STAT_LABELS[stat], medias[stat])

        col_diag1, col_diag2 = st.columns(2)
        with col_diag1:
            st.subheader("🧠 Diagnóstico")
            alertas = identificar_alertas(dados_time, stats_time)
            if alertas:
                for alerta in alertas:
                    st.warning(alerta)
            else:
                st.success("✅ Nenhum alerta importante detectado nesta análise.")
        with col_diag2:
            st.subheader("💪 Pontos fortes")
            positivos = diagnostico_positivo(dados_time, stats_time)
            if positivos:
                for ponto in positivos:
                    st.success(ponto)
            else:
                st.info("Ainda não há pontos fortes automáticos suficientes para destacar.")

        st.divider()
        st.subheader("⚔️ Perfil físico x especial")
        perfil = analisar_tipo_fisico_especial(dados_time)
        cols = st.columns(3)
        cols[0].metric("⚔️ Físicos", perfil["físicos"])
        cols[1].metric("✨ Especiais", perfil["especiais"])
        cols[2].metric("⚖️ Equilibrados", perfil["equilibrados"])

# ============================================================
# DANO
# ============================================================

with aba_dano:
    st.header("🧮 Calculadora de Dano")
    st.caption("Estimativa simplificada. Não representa todos os modificadores de uma batalha oficial.")

    col_a, col_d = st.columns(2)
    with col_a:
        atacante_nome = st.text_input("⚔️ Atacante", placeholder="Ex.: Lucario", key="dano_atacante_v3")
    with col_d:
        defensor_nome = st.text_input("🛡️ Defensor", placeholder="Ex.: Tyranitar", key="dano_defensor_v3")

    atacante = buscar_pokemon(atacante_nome) if atacante_nome else None
    defensor = buscar_pokemon(defensor_nome) if defensor_nome else None

    if atacante and defensor:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"⚔️ {nome_bonito(atacante.get('name'))}")
            sprite = obter_sprite(atacante)
            if sprite:
                st.image(sprite, width=170)
            st.caption(" / ".join(traduzir_tipo(t) for t in obter_tipos(atacante)))
        with col2:
            st.subheader(f"🛡️ {nome_bonito(defensor.get('name'))}")
            sprite = obter_sprite(defensor)
            if sprite:
                st.image(sprite, width=170)
            st.caption(" / ".join(traduzir_tipo(t) for t in obter_tipos(defensor)))

        build_atk = build_padrao(atacante.get("name"), atacante)
        build_def = build_padrao(defensor.get("name"), defensor)
        colx, coly = st.columns(2)
        with colx:
            build_atk["level"] = st.number_input("Nível do atacante", 1, 100, 50, key="nivel_dano_atk_v3")
            build_atk["nature"] = st.selectbox("Nature atacante", list(NATURES.keys()), key="nature_dano_atk_v3")
            build_atk["item"] = st.selectbox("Item atacante", ITENS_COMUNS, key="item_dano_atk_v3")
            build_atk["tera"] = st.selectbox("Tera atacante", ["auto"] + TIPOS, format_func=lambda x: "Automático" if x == "auto" else traduzir_tipo(x), key="tera_dano_atk_v3")
        with coly:
            build_def["level"] = st.number_input("Nível do defensor", 1, 100, 50, key="nivel_dano_def_v3")
            build_def["nature"] = st.selectbox("Nature defensor", list(NATURES.keys()), key="nature_dano_def_v3")

        movimento_nome = st.text_input("🎯 Golpe", placeholder="Ex.: Close Combat", key="golpe_dano_v3")
        movimento = buscar_movimento(movimento_nome) if movimento_nome else None
        if movimento:
            categoria = movimento.get("damage_class", {}).get("name", "")
            tipo = movimento.get("type", {}).get("name", "")
            st.info(f"**{nome_bonito(movimento.get('name', movimento_nome))}** • {CATEGORIAS_GOLPES.get(categoria, nome_bonito(categoria))} • {traduzir_tipo(tipo)} • Poder: {movimento.get('power') or '—'}")
            stats_atk = calcular_stats_build(atacante, build_atk)
            stats_def = calcular_stats_build(defensor, build_def)
            resultado = calcular_dano_simples(atacante, defensor, movimento, build_atk, build_def, stats_atk, stats_def)
            if resultado and "erro" not in resultado:
                st.divider()
                cols = st.columns(4)
                cols[0].metric("Dano mínimo", resultado["dano_min"])
                cols[1].metric("Dano máximo", resultado["dano_max"])
                cols[2].metric("% HP mínimo", f"{resultado['pct_min']:.1f}%")
                cols[3].metric("% HP máximo", f"{resultado['pct_max']:.1f}%")
                if resultado["efetividade"] == 0:
                    st.error("🚫 O defensor é imune a esse golpe.")
                elif resultado["efetividade"] > 1:
                    st.success(f"⚡ Super efetivo — {resultado['efetividade']}x")
                elif resultado["efetividade"] < 1:
                    st.warning(f"🛡️ Não muito efetivo — {resultado['efetividade']}x")
                else:
                    st.info("➡️ Dano neutro — 1x")
                if resultado["pct_max"] >= 100:
                    st.success("🎯 O dano máximo ultrapassa 100% do HP estimado: possível OHKO nesta aproximação.")
            else:
                st.warning(resultado["erro"] if resultado else "Não foi possível calcular.")

# ============================================================
# COMPARAR
# ============================================================

with aba_comparar:
    st.header("🔎 Comparador de Pokémon")
    ca, cb = st.columns(2)
    with ca:
        nome_a = st.text_input("Pokémon A", value=st.session_state.pokemon_comparacao_a, key="comparar_a_v3")
    with cb:
        nome_b = st.text_input("Pokémon B", value=st.session_state.pokemon_comparacao_b, key="comparar_b_v3")
    a = buscar_pokemon(nome_a) if nome_a else None
    b = buscar_pokemon(nome_b) if nome_b else None
    if a and b:
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader(f"🔵 {nome_bonito(a.get('name'))}")
            sprite = obter_sprite(a)
            if sprite:
                st.image(sprite, width=180)
            st.caption(" / ".join(traduzir_tipo(t) for t in obter_tipos(a)))
        with col_b:
            st.subheader(f"🔴 {nome_bonito(b.get('name'))}")
            sprite = obter_sprite(b)
            if sprite:
                st.image(sprite, width=180)
            st.caption(" / ".join(traduzir_tipo(t) for t in obter_tipos(b)))

        st.subheader("📊 Comparação de Base Stats")
        stats_a = obter_stats(a)
        stats_b = obter_stats(b)
        for stat in STAT_KEYS:
            va = stats_a.get(stat, 0)
            vb = stats_b.get(stat, 0)
            vencedor = "🔵 A" if va > vb else "🔴 B" if vb > va else "⚖️ Empate"
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(STAT_LABELS[stat])
            c2.metric("A", va)
            c3.metric("B", vb)
            st.caption(f"Vantagem: {vencedor}")

        total_a = sum(stats_a.values())
        total_b = sum(stats_b.values())
        st.info(f"**BST:** {nome_bonito(a.get('name'))} = {total_a} • {nome_bonito(b.get('name'))} = {total_b}")
    elif nome_a or nome_b:
        st.warning("Digite dois Pokémon válidos para comparar.")

# ============================================================
# TIMES SALVOS
# ============================================================

with aba_salvos:
    st.header("💾 Times Salvos")
    col_nome, col_salvar = st.columns([4, 2])
    with col_nome:
        nome_time = st.text_input("Nome do time", value=st.session_state.time_nome, key="nome_time_salvar_v3")
    with col_salvar:
        st.write("")
        if st.button("💾 Salvar time atual", type="primary", use_container_width=True):
            if st.session_state.time_atual:
                pacote = {
                    "membros": list(st.session_state.time_atual),
                    "builds": {normalizar_nome(p): garantir_build(p) for p in st.session_state.time_atual}
                }
                st.session_state.times_salvos[nome_time.strip() or "Meu Time"] = pacote
                st.session_state.time_nome = nome_time.strip() or "Meu Time"
                st.success("✅ Time salvo!")
            else:
                st.warning("Adicione pelo menos um Pokémon antes de salvar.")

    st.divider()
    if not st.session_state.times_salvos:
        st.info("Você ainda não salvou nenhum time.")
    else:
        for nome_time_salvo, pacote in list(st.session_state.times_salvos.items()):
            if isinstance(pacote, list):
                membros = pacote
                builds_salvos = {}
            else:
                membros = pacote.get("membros", [])
                builds_salvos = pacote.get("builds", {})
            with st.container(border=True):
                c1, c2 = st.columns([4, 2])
                with c1:
                    st.subheader(f"⚔️ {nome_time_salvo}")
                    st.write(f"{len(membros)}/6 Pokémon")
                    st.write(" • ".join(nome_bonito(p) for p in membros))
                with c2:
                    if st.button("📥 Carregar", key=f"carregar_v3_{normalizar_nome(nome_time_salvo)}", use_container_width=True):
                        st.session_state.time_atual = list(membros)[:MAX_TEAM_SIZE]
                        for p in st.session_state.time_atual:
                            dados = buscar_pokemon(p)
                            salvo = builds_salvos.get(normalizar_nome(p), {}) if isinstance(builds_salvos, dict) else {}
                            st.session_state.builds[normalizar_nome(p)] = normalizar_build(salvo, p, dados)
                        st.session_state.time_nome = nome_time_salvo
                        st.rerun()
                    if st.button("🗑️ Excluir", key=f"excluir_v3_{normalizar_nome(nome_time_salvo)}", use_container_width=True):
                        del st.session_state.times_salvos[nome_time_salvo]
                        st.rerun()

# ============================================================
# IMPORTAR / EXPORTAR
# ============================================================

with aba_io:
    st.header("📋 Importar / Exportar Times")
    st.subheader("📤 Exportar")
    texto_exportado = exportar_time_showdown() if st.session_state.time_atual else ""
    st.text_area("Formato de texto", value=texto_exportado, height=320, key="exportacao_texto_v3")
    if texto_exportado:
        st.caption("Você pode copiar este texto para guardar ou transportar sua build.")

    st.divider()
    st.subheader("📥 Importar")
    texto_importar = st.text_area("Cole aqui um time em formato de texto", height=320, key="importacao_texto_v3")
    if st.button("📥 Importar time", use_container_width=True):
        if not texto_importar.strip():
            st.warning("Cole um time antes de importar.")
        else:
            importados = parsear_importacao_showdown(texto_importar)
            if not importados:
                st.error("❌ Não foi possível reconhecer nenhum Pokémon válido.")
            else:
                st.session_state.time_atual = [nome for nome, _ in importados]
                for nome, build in importados:
                    dados = buscar_pokemon(nome)
                    st.session_state.builds[normalizar_nome(nome)] = normalizar_build(build, nome, dados)
                st.success(f"✅ {len(importados)} Pokémon importados.")
                st.rerun()

# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption("⚔️ Kayzac Master Pokémon • Laboratório de Times")
st.caption("Monte, prepare, compare, salve e analise suas equipes Pokémon.")
