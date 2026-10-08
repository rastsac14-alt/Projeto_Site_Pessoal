from __future__ import annotations

"""🃏 KAYZAC - MASTER POKEMON — Pokémon TCG Pocket

Catálogo completo carregado sob demanda a partir do dataset público
PocketDecks/pokemon-tcg-pocket-cards. As imagens são exibidas pelas URLs
fornecidas pelo próprio dataset; o KAYZAC não precisa armazenar milhares de
imagens localmente.
"""

import json
import random
from pathlib import Path
from typing import Any

import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_DATA_FILE = BASE_DIR / "tcg_pocket_cards.json"
DATA_URL = "https://raw.githubusercontent.com/PocketDecks/pokemon-tcg-pocket-cards/main/data/v5/cards.json"

st.set_page_config(page_title="KAYZAC — TCG Pocket", page_icon="🃏", layout="wide")

st.markdown("""
<style>
.tcg-hero{padding:1.6rem;border-radius:24px;background:linear-gradient(135deg,#101b38,#080d1d);border:1px solid rgba(90,170,255,.3);margin-bottom:1rem;box-shadow:0 12px 40px rgba(0,0,0,.22)}
.tcg-card{border:1px solid rgba(120,160,220,.25);border-radius:18px;padding:.7rem;background:rgba(15,20,35,.78);height:100%}
.tcg-mini{color:#9aa8c2;font-size:.84rem}.tcg-rarity{font-weight:800;font-size:1.05rem;margin:.25rem 0}
.tcg-pack{border-radius:20px;padding:1.2rem;min-height:190px;border:1px solid rgba(255,255,255,.12);background:linear-gradient(145deg,#111827,#172554)}
.tcg-source{font-size:.82rem;color:#94a3b8}
</style>
""", unsafe_allow_html=True)

TIPOS = ["Todos", "Grass", "Fire", "Water", "Lightning", "Psychic", "Fighting", "Darkness", "Metal", "Colorless", "Dragon", "Colorless"]
RARIDADES = ["Todas", "♦", "♦♦", "♦♦♦", "♦♦♦♦", "☆", "☆☆", "☆☆☆", "Crown", "👑"]


def _normalizar_carta(c: dict[str, Any]) -> dict[str, Any]:
    cid = str(c.get("id") or c.get("deckBuilderNr") or "")
    set_code = str(c.get("set") or cid.split("-")[0] if "-" in cid else c.get("set") or "—")
    if isinstance(c.get("set"), dict):
        set_code = str(c["set"].get("code") or c["set"].get("id") or "—")
    rarity = str(c.get("rarity") or c.get("raridade") or "—")
    image = c.get("image") or c.get("imageUrl") or c.get("image_url")
    name = str(c.get("name") or c.get("nome") or "Carta")
    health = c.get("health") or c.get("hp") or "—"
    element = c.get("element") or c.get("type") or c.get("tipo") or "—"
    category = c.get("category") or c.get("categoryName") or c.get("categoria") or "Carta"
    pack = c.get("pack") or c.get("packs") or "—"
    if isinstance(pack, list):
        pack = ", ".join(map(str, pack))
    number = c.get("number") or c.get("numero") or (cid.split("-")[-1] if "-" in cid else "")
    return {
        **c,
        "id": cid,
        "nome": name,
        "tipo": str(element),
        "raridade": rarity,
        "expansao": set_code,
        "hp": health,
        "categoria": str(category),
        "pack": str(pack),
        "numero": str(number),
        "image": image,
    }


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def carregar_catalogo_remoto() -> list[dict[str, Any]]:
    resposta = requests.get(DATA_URL, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()
    if isinstance(dados, dict):
        dados = dados.get("cards", [])
    return [_normalizar_carta(x) for x in dados if isinstance(x, dict)]


@st.cache_data(show_spinner=False)
def carregar_catalogo_local() -> list[dict[str, Any]]:
    if not LOCAL_DATA_FILE.exists():
        return []
    try:
        dados = json.loads(LOCAL_DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(dados, list):
            return [_normalizar_carta(x) for x in dados if isinstance(x, dict)]
    except Exception:
        pass
    return []


def carregar_catalogo() -> tuple[list[dict[str, Any]], str]:
    try:
        dados = carregar_catalogo_remoto()
        if dados:
            return dados, "online"
    except Exception:
        pass
    local = carregar_catalogo_local()
    if local:
        return local, "local"
    return [], "offline"


def init() -> None:
    defaults = {
        "tcg_colecao": {},
        "tcg_favoritos": [],
        "tcg_aberturas": 0,
        "tcg_cartas": 0,
        "tcg_xp": 0,
        "tcg_deck": [],
        "tcg_historico": [],
        "tcg_ultimo": [],
        "tcg_pagina": 1,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def add_card(cid: str) -> None:
    st.session_state.tcg_colecao[cid] = st.session_state.tcg_colecao.get(cid, 0) + 1
    st.session_state.tcg_cartas += 1


def choose_card(cat: list[dict[str, Any]]) -> dict[str, Any]:
    if not cat:
        return {}
    pesos = []
    for card in cat:
        rarity = str(card.get("raridade", "♦"))
        pesos.append({"♦": 55, "♦♦": 28, "♦♦♦": 11, "♦♦♦♦": 4, "☆": 2, "☆☆": 1, "☆☆☆": .5, "👑": .1}.get(rarity, 3))
    return random.choices(cat, weights=pesos, k=1)[0]


def open_pack(cat: list[dict[str, Any]], pack_name: str, expansion: str | None = None) -> list[dict[str, Any]]:
    pool = [c for c in cat if expansion is None or c.get("expansao") == expansion]
    if not pool:
        pool = cat
    cards = []
    for _ in range(5):
        card = choose_card(pool)
        if card:
            cards.append(card)
            add_card(str(card.get("id")))
    st.session_state.tcg_aberturas += 1
    st.session_state.tcg_xp += 25
    st.session_state.tcg_historico.insert(0, {"pacote": pack_name, "cartas": [c.get("nome", "?") for c in cards]})
    return cards


def is_pokemon_card(c: dict[str, Any]) -> bool:
    """Retorna True somente para cartas que representam Pokémon.

    Cartas de Treinador, Apoiador, Item, Ferramenta e Energia não
    devem oferecer atalho para a Pokédex, porque não são espécies.
    """
    categoria = str(c.get("categoria", "")).strip().lower()
    return categoria.startswith(("pokemon", "pokémon"))


def open_dex(name: str) -> None:
    slug = name.lower().replace(" ex", "").replace("'", "").replace(".", "").replace(" ", "-")
    st.session_state["pokemon_focado"] = slug
    try:
        st.switch_page("pages/1_Pokedex.py")
    except Exception:
        st.info("Abra a Pokédex pelo menu lateral.")


def card(c: dict[str, Any], key: str | int, buttons: bool = True, show_image: bool = True) -> None:
    cid = str(c.get("id", "???"))
    fav = cid in st.session_state.tcg_favoritos
    image = c.get("image")

    # Não usamos um <div> HTML aberto ao redor do st.image():
    # componentes Streamlit são renderizados fora do fluxo HTML do markdown,
    # o que criava aquele enorme cartão vazio acima da imagem.
    with st.container(border=True):
        if show_image and image:
            try:
                st.image(
                    image,
                    use_container_width=True,
                    caption=f"{c.get('nome', 'Carta')} • {cid}",
                )
            except Exception:
                st.warning("Imagem indisponível para esta carta.")
        elif show_image:
            st.info("Imagem não disponível no catálogo.")

        st.markdown(
            f"<b style='font-size:1.18rem'>{c.get('nome','Carta')}</b>"
            f"<div class='tcg-rarity'>{c.get('raridade','—')}</div>"
            f"<div class='tcg-mini'>{cid} • #{c.get('numero','—')} • {c.get('tipo','—')} • HP {c.get('hp','—')}</div>"
            f"<div class='tcg-mini'>Expansão: {c.get('expansao','—')} • {c.get('categoria','Carta')}</div>"
            f"<div class='tcg-mini'>Pack: {c.get('pack','—')}</div>",
            unsafe_allow_html=True,
        )

    if buttons:
        # Cartas de Treinador/Item/Energia não representam Pokémon e,
        # portanto, não devem mostrar o botão da Pokédex.
        if is_pokemon_card(c):
            a, b = st.columns(2)
            with a:
                if st.button("⭐ Remover favorito" if fav else "☆ Favoritar", key=f"fav_{cid}_{key}", use_container_width=True):
                    if fav:
                        st.session_state.tcg_favoritos.remove(cid)
                    else:
                        st.session_state.tcg_favoritos.append(cid)
                    st.rerun()
            with b:
                if st.button("📖 Pokédex", key=f"dex_{cid}_{key}", use_container_width=True):
                    open_dex(str(c.get("nome", "")))
        else:
            if st.button("⭐ Remover favorito" if fav else "☆ Favoritar", key=f"fav_{cid}_{key}", use_container_width=True):
                if fav:
                    st.session_state.tcg_favoritos.remove(cid)
                else:
                    st.session_state.tcg_favoritos.append(cid)
                st.rerun()


def filtros(cat: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    expansions = sorted({str(c.get("expansao")) for c in cat if c.get("expansao") not in {None, "", "—"}})
    types = sorted({str(c.get("tipo")) for c in cat if c.get("tipo") not in {None, "", "—"}})
    rarities = sorted({str(c.get("raridade")) for c in cat if c.get("raridade") not in {None, "", "—"}})

    q = st.text_input("🔎 Buscar carta ou Pokémon", key=f"{prefix}_q", placeholder="Ex.: Lucario, Pikachu ex, Team Rocket...")
    a, b, c = st.columns(3)
    with a:
        typ = st.selectbox("Tipo", ["Todos"] + types, key=f"{prefix}_tipo")
    with b:
        rar = st.selectbox("Raridade", ["Todas"] + rarities, key=f"{prefix}_rar")
    with c:
        exp = st.selectbox("Expansão", ["Todas"] + expansions, key=f"{prefix}_exp")

    result = []
    for item in cat:
        text = " ".join(str(item.get(k, "")) for k in ("nome", "id", "pack", "expansao")).lower()
        if q and q.lower() not in text:
            continue
        if typ != "Todos" and str(item.get("tipo")) != typ:
            continue
        if rar != "Todas" and str(item.get("raridade")) != rar:
            continue
        if exp != "Todas" and str(item.get("expansao")) != exp:
            continue
        result.append(item)
    return result


def mostrar_grade(cards: list[dict[str, Any]], prefix: str, por_pagina: int = 24) -> None:
    total = len(cards)
    if not total:
        st.info("Nenhuma carta encontrada com esses filtros.")
        return

    paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina = st.number_input("📄 Página", min_value=1, max_value=paginas, value=min(st.session_state.get(f"pagina_{prefix}", 1), paginas), step=1, key=f"pagina_{prefix}")
    inicio = (int(pagina) - 1) * por_pagina
    fim = min(inicio + por_pagina, total)
    subset = cards[inicio:fim]
    st.caption(f"Mostrando {inicio + 1}–{fim} de {total} cartas • {paginas} página(s)")

    for start in range(0, len(subset), 4):
        cols = st.columns(min(4, len(subset) - start))
        for i, item in enumerate(subset[start:start + 4]):
            with cols[i]:
                card(item, f"{prefix}_{inicio + start + i}")


def collection(cat: list[dict[str, Any]]) -> None:
    st.subheader("📚 Minha Coleção")
    st.caption("O catálogo completo fica disponível para pesquisa; sua coleção registra quantas cópias você obteve.")
    out = filtros(cat, "colecao")
    out.sort(key=lambda x: (str(x.get("expansao", "")), str(x.get("numero", ""))))
    mostrar_grade(out, "colecao")


def boosters(cat: list[dict[str, Any]]) -> None:
    st.subheader("🎴 Simulador de Boosters")
    st.warning("Simulação recreativa do KAYZAC. As probabilidades usadas aqui não representam necessariamente as taxas oficiais de Pokémon TCG Pocket.")
    expansions = sorted({str(c.get("expansao")) for c in cat})
    if not expansions:
        st.info("Nenhuma expansão disponível.")
        return

    exp = st.selectbox("Expansão do booster", expansions, key="booster_exp")
    pool = [c for c in cat if c.get("expansao") == exp]
    packs = sorted({str(c.get("pack")) for c in pool if c.get("pack") not in {"", "—", "None"}})
    pack = st.selectbox("Arte/Pack", ["Aleatório"] + packs, key="booster_pack")
    if st.button("📦 Abrir 5 cartas", key="abrir_booster", use_container_width=True):
        if pack != "Aleatório":
            pool_pack = [c for c in pool if pack in str(c.get("pack"))]
            st.session_state.tcg_ultimo = open_pack(pool_pack or pool, f"{exp} — {pack}", exp)
        else:
            st.session_state.tcg_ultimo = open_pack(pool, f"{exp}", exp)
        st.rerun()

    ultimo = st.session_state.get("tcg_ultimo", [])
    if ultimo:
        st.markdown("---")
        st.subheader("✨ Último Booster")
        cols = st.columns(min(5, len(ultimo)))
        for i, item in enumerate(ultimo):
            with cols[i]:
                card(item, f"pack_result_{i}")


def decks(cat: list[dict[str, Any]]) -> None:
    st.subheader("⚔️ Deck Builder")
    q = st.text_input("🔎 Procurar carta Pokémon", key="deck_q")
    cand = [c for c in cat if ("pokemon" in str(c.get("categoria", "")).lower() or "pokémon" in str(c.get("categoria", "")).lower()) and (not q or q.lower() in str(c.get("nome", "")).lower())]
    cand = cand[:500]
    if cand:
        name = st.selectbox("Carta", [c["nome"] for c in cand], key="deck_sel")
        chosen = next(x for x in cand if x["nome"] == name)
        if st.button("➕ Adicionar ao deck", key="deck_add"):
            if len(st.session_state.tcg_deck) < 20:
                st.session_state.tcg_deck.append(str(chosen["id"]))
            else:
                st.warning("Limite experimental de 20 cartas atingido.")
            st.rerun()
    st.markdown("### 🧾 Meu deck")
    if not st.session_state.tcg_deck:
        st.info("Seu deck ainda está vazio.")
        return
    for i, cid in enumerate(st.session_state.tcg_deck):
        item = next((x for x in cat if str(x.get("id")) == cid), None)
        if item:
            a, b, d = st.columns([4, 2, 1])
            a.write(f"**{i + 1}. {item['nome']}** — {item.get('tipo')} — {item.get('raridade')}")
            b.caption(str(item.get("expansao", "—")))
            if d.button("🗑️", key=f"deck_del_{i}"):
                st.session_state.tcg_deck.pop(i)
                st.rerun()
    if st.button("🧹 Limpar deck", key="deck_clear"):
        st.session_state.tcg_deck.clear()
        st.rerun()


def app() -> None:
    init()
    cat, fonte = carregar_catalogo()

    if not cat:
        st.error("Não foi possível carregar o catálogo TCG Pocket. Conecte-se à internet ou coloque um tcg_pocket_cards.json na raiz do projeto.")
        return

    total = len(cat)
    collected_unique = len(st.session_state.tcg_colecao)
    pct = collected_unique / total if total else 0
    fonte_label = "🌐 catálogo online completo" if fonte == "online" else "💾 catálogo local"

    st.markdown(
        f"<div class='tcg-hero'><h1>🃏 KAYZAC — TCG POCKET</h1>"
        f"<p>Central de coleção, <b>todas as cartas</b>, imagens, boosters, favoritos e decks do Pokémon Estampas Ilustradas Pocket.</p>"
        f"<b>📚 {collected_unique}/{total} cartas • 🎴 {st.session_state.tcg_aberturas} boosters • 🃏 {st.session_state.tcg_cartas} cartas obtidas</b><br>"
        f"<span class='tcg-source'>{fonte_label} • imagens carregadas sob demanda</span></div>",
        unsafe_allow_html=True,
    )
    st.progress(min(pct, 1), text=f"Progresso da coleção: {pct * 100:.1f}%")

    if st.button("🔄 Atualizar catálogo", key="refresh_catalog"):
        carregar_catalogo_remoto.clear()
        st.rerun()

    tabs = st.tabs(["🏠 Início", "📚 Todas as Cartas", "🎴 Boosters", "⚔️ Decks", "⭐ Favoritos", "🕘 Histórico", "🌐 Oficial"])

    with tabs[0]:
        st.subheader("🏠 Central TCG Pocket")
        a, b, c, d = st.columns(4)
        a.metric("📚 Catálogo", f"{total:,}")
        b.metric("📖 Colecionadas", collected_unique)
        c.metric("🎴 Boosters", st.session_state.tcg_aberturas)
        d.metric("⭐ Favoritos", len(st.session_state.tcg_favoritos))
        st.success("As imagens das cartas agora são carregadas diretamente do catálogo completo. Você pode navegar por todas elas sem precisar salvar milhares de arquivos na pasta do projeto.")
        st.info("O catálogo é fornecido pelo projeto aberto PocketDecks, que publica os dados do Pokémon TCG Pocket em JSON e inclui URLs de imagens. citeturn0search0turn0search1")
        st.markdown("### 🚀 Atalhos")
        x, y = st.columns(2)
        with x:
            if st.button("🃏 Explorar todas as cartas", key="home_cards", use_container_width=True):
                st.session_state["tcg_tab_hint"] = 1
                st.rerun()
        with y:
            if st.button("📦 Abrir um booster", key="home_pack", use_container_width=True):
                st.session_state.tcg_ultimo = open_pack(cat, "KAYZAC Pack")
                st.rerun()
        if st.session_state.tcg_ultimo:
            st.subheader("✨ Último Booster")
            cols = st.columns(min(5, len(st.session_state.tcg_ultimo)))
            for i, item in enumerate(st.session_state.tcg_ultimo):
                with cols[i]:
                    card(item, f"home_{i}")

    with tabs[1]:
        st.subheader("📚 Todas as Cartas")
        st.caption("Catálogo completo com imagens. A grade é paginada para não travar o navegador carregando milhares de imagens de uma vez.")
        out = filtros(cat, "todas")
        out.sort(key=lambda x: (str(x.get("expansao", "")), str(x.get("numero", ""))))
        mostrar_grade(out, "todas")

    with tabs[2]:
        boosters(cat)

    with tabs[3]:
        decks(cat)

    with tabs[4]:
        st.subheader("⭐ Meus Favoritos")
        fav = [c for c in cat if str(c.get("id")) in st.session_state.tcg_favoritos]
        mostrar_grade(fav, "favoritos") if fav else st.info("Você ainda não favoritou nenhuma carta.")

    with tabs[5]:
        st.subheader("🕘 Histórico")
        if not st.session_state.tcg_historico:
            st.info("Nenhuma abertura registrada ainda.")
        for item in st.session_state.tcg_historico[:30]:
            st.write(f"**{item['pacote']}** — " + " • ".join(item["cartas"]))

    with tabs[6]:
        st.subheader("🌐 Recursos")
        st.link_button("🌐 Pokémon TCG Pocket", "https://tcgpocket.pokemon.com/", use_container_width=True)
        st.link_button("🆘 Suporte oficial", "https://support.pokemon.com/hc/en-us/categories/19331422065172", use_container_width=True)
        st.link_button("📰 Notícias Pokémon", "https://www.pokemon.com/br/noticias-pokemon/", use_container_width=True)
        st.markdown("### 📡 Fonte do catálogo")
        st.write("PocketDecks / pokemon-tcg-pocket-cards — dataset aberto voltado a sites, coleções e fan tools. O README informa que o payload completo inclui todos os prints e imagens. citeturn0search0turn0search1")
        st.link_button("📦 Ver dataset no GitHub", "https://github.com/PocketDecks/pokemon-tcg-pocket-cards", use_container_width=True)
        st.caption("As cartas e suas imagens pertencem aos respectivos detentores de direitos. O KAYZAC apenas referencia os dados/imagens fornecidos pela fonte para fins de consulta de fã.")

    st.markdown("---")
    st.caption("⚡ KAYZAC - MASTER POKEMON • Página 12 — TCG Pocket")


if __name__ == "__main__":
    app()
