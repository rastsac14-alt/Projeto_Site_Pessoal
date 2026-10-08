from __future__ import annotations

"""🎯 KAYZAC - MASTER POKEMON — Simulador de Capturas

Página autoral de captura inspirada nas mecânicas clássicas de Pokémon.
A simulação não pretende reproduzir um jogo específico 1:1.
"""

import random
from datetime import datetime
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="KAYZAC — Capturas",
    page_icon="🎯",
    layout="wide",
)

API = "https://pokeapi.co/api/v2"

REGIOES = {
    "Kanto": (1, 151),
    "Johto": (152, 251),
    "Hoenn": (252, 386),
    "Sinnoh": (387, 493),
    "Unova": (494, 649),
    "Kalos": (650, 721),
    "Alola": (722, 809),
    "Galar": (810, 905),
    "Paldea": (906, 1025),
    "Mundo Pokémon": (1, 1025),
}

POKEBALLS = {
    "Poké Ball": {"preco": 200, "modificador": 1.0, "icone": "🔴", "descricao": "A Poké Ball clássica."},
    "Great Ball": {"preco": 600, "modificador": 1.5, "icone": "🔵", "descricao": "Uma Ball mais eficiente."},
    "Ultra Ball": {"preco": 1200, "modificador": 2.0, "icone": "🟡", "descricao": "Alta taxa de captura."},
    "Premier Ball": {"preco": 200, "modificador": 1.0, "icone": "⚪", "descricao": "Uma Ball especial para colecionadores."},
    "Luxury Ball": {"preco": 1000, "modificador": 1.0, "icone": "🖤", "descricao": "Captura normal, mas com estilo."},
    "Net Ball": {"preco": 1000, "modificador": 1.0, "icone": "🕸️", "descricao": "Bônus para Pokémon Bug ou Water."},
    "Dive Ball": {"preco": 1000, "modificador": 1.0, "icone": "🌊", "descricao": "Bônus para Pokémon ligados à água."},
    "Dusk Ball": {"preco": 1000, "modificador": 1.0, "icone": "🌙", "descricao": "Bônus em ambientes escuros ou à noite."},
    "Quick Ball": {"preco": 1000, "modificador": 5.0, "icone": "⚡", "descricao": "Muito mais eficiente no primeiro turno."},
    "Repeat Ball": {"preco": 1000, "modificador": 1.0, "icone": "🔁", "descricao": "Bônus para espécies já registradas."},
    "Timer Ball": {"preco": 1000, "modificador": 1.0, "icone": "⏱️", "descricao": "Fica mais eficiente conforme a batalha demora."},
    "Master Ball": {"preco": 0, "modificador": 255.0, "icone": "🟣", "descricao": "Captura garantida na simulação."},
}

STATUS = {
    "Nenhum": 1.0,
    "Paralisado": 1.5,
    "Envenenado": 1.5,
    "Queimado": 1.5,
    "Adormecido": 2.5,
    "Congelado": 2.5,
}

TIPO_ICONE = {
    "normal": "⚪", "fire": "🔥", "water": "💧", "electric": "⚡", "grass": "🌿",
    "ice": "❄️", "fighting": "🥊", "poison": "☠️", "ground": "🟤", "flying": "🪽",
    "psychic": "🔮", "bug": "🐛", "rock": "🪨", "ghost": "👻", "dragon": "🐉",
    "dark": "🌑", "steel": "⚙️", "fairy": "🧚",
}


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_pokemon(nome_ou_id: str | int) -> dict[str, Any] | None:
    try:
        resposta = requests.get(f"{API}/pokemon/{nome_ou_id}", timeout=10)
        if resposta.status_code != 200:
            return None
        return resposta.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_especie(nome_ou_id: str | int) -> dict[str, Any] | None:
    try:
        resposta = requests.get(f"{API}/pokemon-species/{nome_ou_id}", timeout=10)
        if resposta.status_code != 200:
            return None
        return resposta.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def nomes_nacionais(inicio: int, fim: int) -> list[dict[str, Any]]:
    """Carrega apenas nomes/IDs para sortear encontros sem baixar todos os detalhes."""
    resultado = []
    for numero in range(inicio, fim + 1):
        resultado.append({"id": numero, "slug": str(numero)})
    return resultado


def nome_bonito(nome: str) -> str:
    return nome.replace("-", " ").title()


def inicializar():
    padroes = {
        "captura_dinheiro": 5000,
        "captura_balls": {
            "Poké Ball": 20,
            "Great Ball": 10,
            "Ultra Ball": 5,
            "Premier Ball": 3,
            "Luxury Ball": 2,
            "Net Ball": 2,
            "Dive Ball": 2,
            "Dusk Ball": 2,
            "Quick Ball": 3,
            "Repeat Ball": 2,
            "Timer Ball": 2,
            "Master Ball": 1,
        },
        "captura_encontro": None,
        "captura_turno": 0,
        "captura_hp_atual": None,
        "captura_status": "Nenhum",
        "captura_historico": [],
        "captura_registradas": {},
        "captura_ultimo_resultado": None,
        "captura_filtros_regiao": "Kanto",
        "captura_pokedex_capturados": set(),
        "captura_total_lancamentos": 0,
        "captura_total_capturas": 0,
        "captura_total_fugas": 0,
        "captura_shinies": 0,
        "captura_masterballs": 0,
        "captura_charm": False,
        "captura_modo_noite": False,
        "captura_bioma": "Campo",
    }
    for chave, valor in padroes.items():
        st.session_state.setdefault(chave, valor)


def tipo_slug(pokemon: dict[str, Any]) -> list[str]:
    return [x["type"]["name"] for x in pokemon.get("types", [])]


def hp_maximo(pokemon: dict[str, Any], nivel: int) -> int:
    base = next((x["base_stat"] for x in pokemon.get("stats", []) if x["stat"]["name"] == "hp"), 50)
    return max(1, int(((2 * base) * nivel / 100) + nivel + 10))


def chance_shiny() -> bool:
    denominador = 4096
    numerador = 3 if st.session_state.get("captura_charm") else 1
    return random.randrange(denominador) < numerador


def modificar_ball(pokemon: dict[str, Any], ball: str, turno: int) -> float:
    dados = POKEBALLS[ball]
    modificador = dados["modificador"]
    tipos = tipo_slug(pokemon)

    if ball == "Net Ball" and ("bug" in tipos or "water" in tipos):
        modificador = 3.5
    elif ball == "Dive Ball" and ("water" in tipos or "water-" in tipos):
        modificador = 3.5
    elif ball == "Dusk Ball" and st.session_state.get("captura_modo_noite"):
        modificador = 3.5
    elif ball == "Repeat Ball" and pokemon["name"] in st.session_state.get("captura_pokedex_capturados", set()):
        modificador = 3.5
    elif ball == "Timer Ball":
        modificador = min(4.0, 1.0 + 0.3 * turno)
    elif ball == "Quick Ball" and turno > 1:
        modificador = 1.0

    return modificador


def calcular_chance_captura(pokemon: dict[str, Any], ball: str, hp_atual: int, hp_max: int, status: str, turno: int) -> float:
    especie = buscar_especie(pokemon["id"])
    catch_rate = int(especie.get("capture_rate", 45)) if especie else 45
    ball_mod = modificar_ball(pokemon, ball, turno)
    status_mod = STATUS.get(status, 1.0)

    # Fórmula aproximada inspirada na família de fórmulas clássicas
    # dos jogos principais. O objetivo aqui é simulação, não reprodução
    # exata de uma versão específica.
    hp_max = max(1, hp_max)
    hp_atual = max(1, min(hp_atual, hp_max))
    fator_hp = (3 * hp_max - 2 * hp_atual) / (3 * hp_max)
    valor = catch_rate * fator_hp * ball_mod * status_mod

    if ball == "Master Ball":
        return 100.0

    # Converte o valor para uma chance intuitiva, mantendo raros
    # Pokémon com catch rate baixo difíceis de capturar.
    chance = 1 - pow(max(0.0, 1 - min(1.0, valor / 255.0)), 1.0)
    return max(1.0, min(99.9, chance * 100))


def escolher_encontro(regiao: str, nivel_min: int, nivel_max: int, apenas_favoritos: bool = False):
    inicio, fim = REGIOES[regiao]
    numero = random.randint(inicio, fim)
    pokemon = buscar_pokemon(numero)
    if not pokemon:
        return None

    nivel = random.randint(nivel_min, nivel_max)
    max_hp = hp_maximo(pokemon, nivel)
    shiny = chance_shiny()
    tipos = tipo_slug(pokemon)

    # Bioma influencia apenas o conjunto de mensagens/balls na simulação.
    bioma = st.session_state.get("captura_bioma", "Campo")
    return {
        "pokemon": pokemon,
        "nivel": nivel,
        "hp_max": max_hp,
        "hp_atual": max_hp,
        "status": "Nenhum",
        "shiny": shiny,
        "turno": 1,
        "bioma": bioma,
        "encontrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "fugiu": False,
        "capturado": False,
        "tipos": tipos,
    }


def novo_encontro():
    regiao = st.session_state.captura_filtros_regiao
    nivel_min = int(st.session_state.get("captura_nivel_min", 5))
    nivel_max = int(st.session_state.get("captura_nivel_max", 30))
    encontro = escolher_encontro(regiao, nivel_min, nivel_max)
    st.session_state.captura_encontro = encontro
    st.session_state.captura_turno = 1
    st.session_state.captura_hp_atual = encontro["hp_atual"] if encontro else None
    st.session_state.captura_status = "Nenhum"
    st.session_state.captura_ultimo_resultado = None


def dados_encontro():
    encontro = st.session_state.get("captura_encontro")
    if not encontro:
        return None
    return encontro


def registrar_historico(encontro, evento: str, ball: str | None = None):
    pokemon = encontro["pokemon"]
    item = {
        "hora": datetime.now().strftime("%H:%M:%S"),
        "evento": evento,
        "pokemon": nome_bonito(pokemon["name"]),
        "id": pokemon["id"],
        "nivel": encontro["nivel"],
        "shiny": encontro["shiny"],
        "ball": ball or "—",
    }
    st.session_state.captura_historico.insert(0, item)
    st.session_state.captura_historico = st.session_state.captura_historico[:50]


def lançar_bola(ball: str):
    encontro = dados_encontro()
    if not encontro:
        st.warning("Primeiro encontre um Pokémon!")
        return

    quantidade = st.session_state.captura_balls.get(ball, 0)
    if quantidade <= 0:
        st.error(f"Você não possui {ball}.")
        return

    st.session_state.captura_balls[ball] -= 1
    st.session_state.captura_total_lancamentos += 1
    encontro["turno"] = max(1, int(encontro.get("turno", 1)))

    hp_atual = int(st.session_state.captura_hp_atual or encontro["hp_atual"])
    chance = calcular_chance_captura(
        encontro["pokemon"],
        ball,
        hp_atual,
        encontro["hp_max"],
        st.session_state.captura_status,
        encontro["turno"],
    )

    capturou = ball == "Master Ball" or random.random() * 100 < chance
    nome = nome_bonito(encontro["pokemon"]["name"])

    if capturou:
        encontro["capturado"] = True
        st.session_state.captura_total_capturas += 1
        st.session_state.captura_pokedex_capturados.add(encontro["pokemon"]["name"])
        st.session_state.captura_registradas[encontro["pokemon"]["name"]] = st.session_state.captura_registradas.get(encontro["pokemon"]["name"], 0) + 1
        if encontro["shiny"]:
            st.session_state.captura_shinies += 1
        if ball == "Master Ball":
            st.session_state.captura_masterballs += 1
        st.session_state.captura_ultimo_resultado = {
            "tipo": "sucesso",
            "mensagem": f"🎉 Você capturou {('✨ ' if encontro['shiny'] else '')}{nome}!",
            "chance": chance,
        }
        registrar_historico(encontro, "Capturado", ball)
    else:
        encontro["turno"] += 1
        st.session_state.captura_ultimo_resultado = {
            "tipo": "falha",
            "mensagem": f"💨 {nome} escapou da {ball}!",
            "chance": chance,
        }
        registrar_historico(encontro, "Escapou da Ball", ball)

        # Pequena perda de HP temática após uma tentativa.
        dano = max(1, int(encontro["hp_max"] * random.uniform(0.04, 0.12)))
        st.session_state.captura_hp_atual = max(1, hp_atual - dano)

        if random.random() < 0.08:
            encontro["fugiu"] = True
            st.session_state.captura_total_fugas += 1
            st.session_state.captura_ultimo_resultado = {
                "tipo": "fuga",
                "mensagem": f"🏃 {nome} fugiu para a área selvagem!",
                "chance": chance,
            }
            registrar_historico(encontro, "Fugiu")


def aplicar_status(status: str):
    encontro = dados_encontro()
    if not encontro or encontro.get("capturado") or encontro.get("fugiu"):
        return
    st.session_state.captura_status = status
    encontro["status"] = status
    encontro["turno"] = int(encontro.get("turno", 1)) + 1


def enfraquecer():
    encontro = dados_encontro()
    if not encontro or encontro.get("capturado") or encontro.get("fugiu"):
        return
    atual = int(st.session_state.captura_hp_atual or encontro["hp_max"])
    dano = max(1, int(encontro["hp_max"] * random.uniform(0.10, 0.25)))
    st.session_state.captura_hp_atual = max(1, atual - dano)
    encontro["turno"] = int(encontro.get("turno", 1)) + 1
    st.session_state.captura_ultimo_resultado = {
        "tipo": "batalha",
        "mensagem": f"⚔️ O Pokémon foi enfraquecido! HP restante: {st.session_state.captura_hp_atual}/{encontro['hp_max']}",
        "chance": None,
    }


def comprar_ball(ball: str, quantidade: int):
    preco = POKEBALLS[ball]["preco"] * quantidade
    if st.session_state.captura_dinheiro < preco:
        st.error("💸 Dinheiro insuficiente!")
        return
    st.session_state.captura_dinheiro -= preco
    st.session_state.captura_balls[ball] = st.session_state.captura_balls.get(ball, 0) + quantidade
    st.success(f"🛒 Comprado: {quantidade}x {ball} por ₽{preco:,}".replace(",", "."))


def imagem_pokemon(encontro):
    pokemon = encontro["pokemon"]
    sprites = pokemon.get("sprites", {})
    if encontro.get("shiny"):
        return sprites.get("other", {}).get("official-artwork", {}).get("front_shiny") or sprites.get("front_shiny")
    return sprites.get("other", {}).get("official-artwork", {}).get("front_default") or sprites.get("front_default")


def render_encontro():
    encontro = dados_encontro()
    if not encontro:
        st.info("🎯 Nenhum Pokémon apareceu ainda. Clique em **Procurar Pokémon** para começar.")
        return

    pokemon = encontro["pokemon"]
    nome = nome_bonito(pokemon["name"])
    hp_atual = int(st.session_state.captura_hp_atual or encontro["hp_max"])
    hp_max = encontro["hp_max"]
    chance_ball = st.session_state.get("captura_ball_selecionada", "Ultra Ball")
    chance = calcular_chance_captura(
        pokemon,
        chance_ball,
        hp_atual,
        hp_max,
        st.session_state.captura_status,
        encontro.get("turno", 1),
    )

    col_img, col_info = st.columns([1, 2])
    with col_img:
        imagem = imagem_pokemon(encontro)
        if imagem:
            st.image(imagem, caption=f"{'✨ SHINY • ' if encontro['shiny'] else ''}{nome}", use_container_width=True)

    with col_info:
        st.markdown(f"## {'✨ ' if encontro['shiny'] else ''}{nome}")
        st.caption(f"Pokédex Nacional #{pokemon['id']:03d} • Nível {encontro['nivel']} • {encontro['bioma']}")
        tipos = "  ".join(f"{TIPO_ICONE.get(t, '🔹')} {t.title()}" for t in tipo_slug(pokemon))
        st.markdown(tipos)
        st.progress(hp_atual / hp_max, text=f"❤️ HP: {hp_atual}/{hp_max}")
        st.info(f"🎯 Chance estimada com **{chance_ball}**: **{chance:.1f}%**")
        st.caption("A chance é uma estimativa recreativa baseada em catch rate, HP, status e modificador da Ball.")

        especie = buscar_especie(pokemon["id"])
        if especie:
            st.write(f"**Catch Rate:** {especie.get('capture_rate', '—')} • **Turno:** {encontro.get('turno', 1)} • **Status:** {st.session_state.captura_status}")

    if st.session_state.captura_ultimo_resultado:
        resultado = st.session_state.captura_ultimo_resultado
        if resultado["tipo"] == "sucesso":
            st.success(resultado["mensagem"])
        elif resultado["tipo"] == "fuga":
            st.error(resultado["mensagem"])
        elif resultado["tipo"] == "falha":
            st.warning(resultado["mensagem"])
        else:
            st.info(resultado["mensagem"])

    if encontro.get("capturado"):
        st.success("📖 Pokémon registrado no seu Mini-Dex de Capturas!")
    elif encontro.get("fugiu"):
        st.warning("O encontro terminou. Procure outro Pokémon para continuar.")
    else:
        st.markdown("### ⚔️ Preparar a captura")
        a, b, c = st.columns(3)
        with a:
            if st.button("⚔️ Enfraquecer", use_container_width=True, key="captura_enfraquecer"):
                enfraquecer()
                st.rerun()
        with b:
            status = st.selectbox("Estado", list(STATUS.keys()), key="captura_status_select")
            if st.button("🧪 Aplicar status", use_container_width=True, key="captura_aplicar_status"):
                aplicar_status(status)
                st.rerun()
        with c:
            ball = st.selectbox("Poké Ball", list(POKEBALLS.keys()), key="captura_ball_selecionada")
            qtd = st.session_state.captura_balls.get(ball, 0)
            st.caption(f"Você possui: {qtd}x")
            if st.button(f"{POKEBALLS[ball]['icone']} Lançar {ball}", use_container_width=True, key="captura_lancar"):
                lançar_bola(ball)
                st.rerun()


def render_inicio():
    st.title("🎯 KAYZAC — Simulador de Capturas")
    st.subheader("A Pokébola está na sua mão. O Pokémon está diante de você.")
    st.markdown(
        "Uma experiência de captura inspirada nos jogos Pokémon: escolha a região, encontre uma espécie, "
        "enfraqueça, aplique status e tente capturá-la."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎯 Lançamentos", st.session_state.captura_total_lancamentos)
    c2.metric("📦 Capturas", st.session_state.captura_total_capturas)
    c3.metric("✨ Shinies", st.session_state.captura_shinies)
    c4.metric("🏃 Fugas", st.session_state.captura_total_fugas)

    st.divider()

    st.markdown("### 🧭 Preparar encontro")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("🌎 Região", list(REGIOES.keys()), key="captura_filtros_regiao")
    with c2:
        st.slider("Nível mínimo", 1, 80, 5, key="captura_nivel_min")
    with c3:
        st.slider("Nível máximo", 1, 100, 30, key="captura_nivel_max")

    st.selectbox("🌿 Bioma", ["Campo", "Floresta", "Caverna", "Montanha", "Lago", "Oceano", "Cidade", "Zona Misteriosa"], key="captura_bioma")

    if st.button("🌟 Procurar Pokémon", type="primary", use_container_width=True, key="captura_novo_encontro"):
        novo_encontro()
        st.rerun()

    render_encontro()


def render_bolas():
    st.subheader("🎒 Mochila de Poké Balls")
    st.metric("💰 Pokédólares", f"₽{st.session_state.captura_dinheiro:,}".replace(",", "."))

    for inicio in range(0, len(POKEBALLS), 3):
        cols = st.columns(3)
        for i, (nome, dados) in enumerate(list(POKEBALLS.items())[inicio:inicio + 3]):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"## {dados['icone']} {nome}")
                    st.write(dados["descricao"])
                    st.metric("Quantidade", st.session_state.captura_balls.get(nome, 0))
                    if dados["preco"]:
                        st.caption(f"Preço simulado: ₽{dados['preco']:,}".replace(",", "."))
                        quantidade = st.selectbox("Comprar", [1, 5, 10], key=f"qtd_{nome}")
                        if st.button("🛒 Comprar", key=f"comprar_{nome}", use_container_width=True):
                            comprar_ball(nome, quantidade)
                            st.rerun()
                    else:
                        st.caption("Não é vendida — já existe 1 na mochila inicial.")


def render_capturados():
    st.subheader("📖 Meu Mini-Dex de Capturas")
    registros = st.session_state.captura_registradas
    if not registros:
        st.info("Você ainda não capturou nenhum Pokémon.")
        return

    busca = st.text_input("🔎 Buscar Pokémon capturado", key="captura_busca_dex")
    itens = []
    for slug, quantidade in registros.items():
        if busca and busca.lower() not in slug.lower():
            continue
        pokemon = buscar_pokemon(slug)
        if pokemon:
            itens.append((pokemon, quantidade))

    for inicio in range(0, len(itens), 4):
        cols = st.columns(4)
        for i, (pokemon, quantidade) in enumerate(itens[inicio:inicio + 4]):
            with cols[i]:
                with st.container(border=True):
                    imagem = pokemon.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
                    if imagem:
                        st.image(imagem, use_container_width=True)
                    st.markdown(f"**#{pokemon['id']:03d} {nome_bonito(pokemon['name'])}**")
                    st.caption(f"Capturas: {quantidade}x")
                    tipos = " • ".join(t.title() for t in tipo_slug(pokemon))
                    st.caption(tipos)
                    if st.button("📖 Abrir na Pokédex", key=f"dex_cap_{pokemon['id']}", use_container_width=True):
                        st.session_state["pokemon_focado"] = pokemon["name"]
                        st.switch_page("pages/1_Pokedex.py")


def render_historico():
    st.subheader("🕘 Diário de Capturas")
    historico = st.session_state.captura_historico
    if not historico:
        st.info("Nenhum encontro registrado ainda.")
        return

    for item in historico[:30]:
        shiny = "✨ " if item["shiny"] else ""
        st.markdown(
            f"**{item['hora']}** — {shiny}**{item['pokemon']}** Lv.{item['nivel']} "
            f"— {item['evento']} — {item['ball']}"
        )


def render_config():
    st.subheader("⚙️ Configurações da simulação")
    st.checkbox("✨ Ativar bônus do Shiny Charm", key="captura_charm")
    st.checkbox("🌙 É noite", key="captura_modo_noite")
    st.caption("O Shiny Charm é tratado como uma regra recreativa da simulação; a página não representa um jogo específico.")

    st.markdown("### 🎲 Regras")
    st.write("• Master Ball captura automaticamente.")
    st.write("• HP menor aumenta a chance de captura.")
    st.write("• Sono/Congelamento recebem bônus maiores que outros status.")
    st.write("• Quick Ball recebe bônus apenas no primeiro turno.")
    st.write("• Timer Ball aumenta o modificador conforme os turnos avançam.")
    st.write("• Net, Dive, Dusk e Repeat possuem condições temáticas.")

    if st.button("🧹 Limpar sessão de capturas", use_container_width=True, key="captura_limpar"):
        chaves = [
            "captura_encontro", "captura_historico", "captura_registradas",
            "captura_pokedex_capturados", "captura_ultimo_resultado",
            "captura_total_lancamentos", "captura_total_capturas",
            "captura_total_fugas", "captura_shinies", "captura_masterballs",
        ]
        for chave in chaves:
            if chave in {"captura_historico"}:
                st.session_state[chave] = []
            elif chave in {"captura_registradas"}:
                st.session_state[chave] = {}
            elif chave in {"captura_pokedex_capturados"}:
                st.session_state[chave] = set()
            elif chave in {"captura_encontro", "captura_ultimo_resultado"}:
                st.session_state[chave] = None
            else:
                st.session_state[chave] = 0
        st.rerun()


def app():
    inicializar()

    st.markdown(
        """
        <style>
        .capture-hero {
            padding: 1.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #101b38, #080d1d);
            border: 1px solid rgba(90,170,255,.30);
            margin-bottom: 1rem;
        }
        .capture-note {
            padding: 1rem;
            border-radius: 16px;
            border: 1px solid rgba(128,128,128,.25);
            background: rgba(128,128,128,.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="capture-hero">
            <h1>🎯 KAYZAC — CAPTURAS</h1>
            <p>Encontre. Enfraqueça. Escolha a Ball. Capture.</p>
            <b>⚡ Uma experiência autoral de captura para o KAYZAC - MASTER POKEMON!</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "🎯 Capturar",
        "🎒 Mochila",
        "📖 Capturados",
        "🕘 Histórico",
        "⚙️ Configurações",
    ])

    with tabs[0]:
        render_inicio()
    with tabs[1]:
        render_bolas()
    with tabs[2]:
        render_capturados()
    with tabs[3]:
        render_historico()
    with tabs[4]:
        render_config()

    st.divider()
    st.caption("⚡ KAYZAC - MASTER POKEMON • Página 13 — Simulador de Capturas")
    st.caption("Pokémon e suas marcas pertencem aos respectivos detentores. Esta é uma experiência de fã e simulação.")


if __name__ == "__main__":
    app()
