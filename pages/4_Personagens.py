from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ALVO = ROOT / "pages" / "4_Personagens.py"
MARCADOR = "# KAYZAC_PERSONAGENS_PERFORMANCE_V1"

if not ALVO.is_file():
    print("ERRO: não encontrei pages/4_Personagens.py.")
    print("Coloque este arquivo na raiz do projeto, ao lado de app.py, e execute novamente.")
    sys.exit(1)

codigo = ALVO.read_text(encoding="utf-8")
if MARCADOR in codigo:
    print("A otimização de desempenho já está instalada. Nada foi alterado.")
    sys.exit(0)

# 1) Substitui a busca remota por uma versão curta: uma consulta à API e no máximo
# dois downloads de imagem. A busca só será chamada quando o usuário pedir as artes.
inicio_arte = '@st.cache_data(ttl=86400, show_spinner=False)\ndef buscar_arte_personagem(nome: str):'
fim_arte = '\n\ndef imagem_personagem(personagem: dict):'
if codigo.count(inicio_arte) != 1 or codigo.count(fim_arte) < 1:
    print("ERRO: não localizei com segurança a função buscar_arte_personagem().")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)

novo_bloco_arte = r'''@st.cache_data(ttl=86400, show_spinner=False)
def buscar_arte_personagem(nome: str):
    """Busca a arte só quando solicitada; usa timeouts curtos e poucos candidatos."""
    nome = str(nome or "").strip()
    if not nome:
        return None

    endpoint = "https://archives.bulbagarden.net/w/api.php"
    headers = {
        "User-Agent": "KAYZAC-Master-Pokemon/2.0 (Streamlit; character gallery)",
        "Accept": "application/json,image/*,*/*;q=0.8",
    }

    try:
        resposta = requests.get(
            endpoint,
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f'"{nome}" artwork',
                "gsrnamespace": 6,
                "gsrlimit": 12,
                "prop": "imageinfo",
                "iiprop": "url|mime|size",
                "format": "json",
                "formatversion": 2,
            },
            timeout=(3.05, 6),
            headers=headers,
        )
        resposta.raise_for_status()
        dados = resposta.json()
    except Exception:
        return None

    paginas = dados.get("query", {}).get("pages", [])
    if not isinstance(paginas, list):
        return None

    nome_lower = nome.lower()
    candidatos = []
    for pagina in paginas:
        titulo = str(pagina.get("title", ""))
        titulo_lower = titulo.lower()
        infos = pagina.get("imageinfo", [])
        if not infos or not isinstance(infos[0], dict):
            continue

        metadados = infos[0]
        url = metadados.get("url")
        mime = str(metadados.get("mime", "")).lower()
        if not url or not mime.startswith("image/"):
            continue

        score = 0
        if nome_lower in titulo_lower:
            score += 20
        if "official" in titulo_lower:
            score += 8
        if "artwork" in titulo_lower:
            score += 8
        if "character" in titulo_lower:
            score += 5
        if "sugimori" in titulo_lower:
            score += 4
        if "concept" in titulo_lower:
            score += 2
        if any(termo in titulo_lower for termo in ("sprite", "icon", "badge")):
            score -= 12
        if any(termo in titulo_lower for termo in ("anime", "tcg")):
            score -= 6
        candidatos.append((score, url, mime))

    candidatos.sort(key=lambda item: item[0], reverse=True)

    # Antes eram até 4 pesquisas e 12 downloads de até 20 segundos cada.
    # Agora só tentamos os 2 candidatos mais relevantes, com timeout limitado.
    for _, url, mime in candidatos[:2]:
        try:
            imagem = requests.get(
                url,
                timeout=(3.05, 5),
                headers={
                    "User-Agent": headers["User-Agent"],
                    "Referer": "https://archives.bulbagarden.net/",
                },
            )
            imagem.raise_for_status()
            dados_imagem = imagem.content
            if not dados_imagem or len(dados_imagem) < 500:
                continue

            try:
                with Image.open(io.BytesIO(dados_imagem)) as img:
                    img.load()
                    formato_saida = "RGBA" if "A" in img.getbands() else "RGB"
                    img_convertida = img.convert(formato_saida)
                    saida = io.BytesIO()
                    img_convertida.save(saida, format="PNG")
                    return saida.getvalue()
            except Exception:
                if mime.startswith("image/"):
                    return dados_imagem
        except Exception:
            continue

    return None


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_artes_em_lote(nomes: tuple):
    """Busca artes em paralelo, apenas para os personagens atualmente exibidos."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    nomes_unicos = tuple(dict.fromkeys(str(n).strip() for n in nomes if str(n).strip()))
    if not nomes_unicos:
        return {}

    resultados = {}
    with ThreadPoolExecutor(max_workers=min(8, len(nomes_unicos))) as executor:
        tarefas = {
            executor.submit(buscar_arte_personagem, nome): nome
            for nome in nomes_unicos
        }
        for tarefa in as_completed(tarefas):
            nome = tarefas[tarefa]
            try:
                resultados[nome] = tarefa.result()
            except Exception:
                resultados[nome] = None
    return resultados
'''
a = codigo.index(inicio_arte)
b = codigo.index(fim_arte, a)
codigo = codigo[:a] + novo_bloco_arte + codigo[b:]

# 2) Faz cada card usar apenas imagens já buscadas pela tarefa em lote.
inicio_card = 'def card_personagem(personagem: dict, indice: int):'
fim_card = '\n\n# ============================================================\n# CABEÇALHO'
if codigo.count(inicio_card) != 1 or codigo.count(fim_card) < 1:
    print("ERRO: não localizei com segurança a função card_personagem().")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)

novo_card = r'''def card_personagem(
    personagem: dict,
    indice: int,
    artes=None,
    carregar_arte: bool = False,
):
    """Desenha o card sem fazer chamadas de rede durante a montagem da página."""
    with st.container(border=True):
        col_img, col_info = st.columns([1, 2])

        with col_img:
            imagem = (artes or {}).get(personagem.get("nome")) if carregar_arte else None
            if imagem:
                st.image(imagem, use_container_width=True)
            else:
                st.markdown("## 👤")
                if carregar_arte:
                    st.caption("Arte não encontrada nesta fonte.")
                else:
                    st.caption("Arte online sob demanda.")

        with col_info:
            st.markdown(f"### 👤 {personagem['nome']}")
            st.caption(f"{personagem['regiao']} • {personagem['categoria']}")
            st.write(personagem["papel"])
            st.markdown(f"**🎮 Jogos:** {personagem['jogo']}")

            if personagem.get("ace"):
                st.markdown(f"**⭐ Pokémon de destaque:** {nome_bonito(personagem['ace'])}")
                if st.button(
                    "📖 Abrir Pokémon na Pokédex",
                    key=f"personagem_pokedex_{indice}_{personagem['nome']}",
                    use_container_width=True,
                ):
                    abrir_pokedex(personagem["ace"])
'''
a = codigo.index(inicio_card)
b = codigo.index(fim_card, a)
codigo = codigo[:a] + novo_card + codigo[b:]

# 3) Inseri controle de imagem sob demanda e paginação limitada a 12 cards.
marcador_metricas = "m1, m2, m3 = st.columns(3)"
if codigo.count(marcador_metricas) != 1:
    print("ERRO: não localizei com segurança a seção de métricas dos resultados.")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)

bloco_performance = r'''

# KAYZAC_PERSONAGENS_PERFORMANCE_V1
# A galeria deixou de pesquisar imagens de todos os personagens automaticamente.
CARDS_POR_PAGINA = 12
_assinatura_filtros = (
    regiao,
    categoria,
    st.session_state.get("personagens_origem", "Todas"),
    busca,
)
if st.session_state.get("_personagens_filtros_rapidos") != _assinatura_filtros:
    st.session_state["_personagens_filtros_rapidos"] = _assinatura_filtros
    st.session_state["personagens_pagina_rapida"] = 1

total_paginas = max(1, (len(resultados) + CARDS_POR_PAGINA - 1) // CARDS_POR_PAGINA)
st.session_state["personagens_pagina_rapida"] = min(
    max(1, int(st.session_state.get("personagens_pagina_rapida", 1))),
    total_paginas,
)
carregar_artes_resultados = st.toggle(
    "🖼️ Carregar artes online dos resultados desta página",
    value=False,
    key="personagens_carregar_artes_resultados_rapido",
    help="Desligado por padrão para abrir a página imediatamente. Ao ativar, busca as artes dos até 12 personagens visíveis.",
)
'''
indice_metricas = codigo.index(marcador_metricas)
codigo = codigo[:indice_metricas] + bloco_performance + "\n\n" + codigo[indice_metricas:]

marcador_depois_divider = '\nst.divider()\n\nif not resultados:'
if codigo.count(marcador_depois_divider) != 1:
    print("ERRO: não localizei com segurança o início da lista de resultados.")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)

bloco_paginacao = r'''
st.divider()

if resultados and total_paginas > 1:
    pag_col_esq, pag_col_meio, pag_col_dir = st.columns([1, 2, 1])
    with pag_col_esq:
        if st.button(
            "⬅️ Página anterior",
            disabled=st.session_state["personagens_pagina_rapida"] <= 1,
            use_container_width=True,
            key="personagens_pagina_anterior_rapida",
        ):
            st.session_state["personagens_pagina_rapida"] -= 1
            st.rerun()
    with pag_col_meio:
        st.markdown(
            f"<div style='text-align:center;padding:.45rem 0'>Página "
            f"<b>{st.session_state['personagens_pagina_rapida']}</b> de "
            f"<b>{total_paginas}</b> · {len(resultados)} personagens</div>",
            unsafe_allow_html=True,
        )
    with pag_col_dir:
        if st.button(
            "Próxima página ➡️",
            disabled=st.session_state["personagens_pagina_rapida"] >= total_paginas,
            use_container_width=True,
            key="personagens_proxima_pagina_rapida",
        ):
            st.session_state["personagens_pagina_rapida"] += 1
            st.rerun()

_indice_inicio = (st.session_state["personagens_pagina_rapida"] - 1) * CARDS_POR_PAGINA
resultados_pagina = resultados[_indice_inicio:_indice_inicio + CARDS_POR_PAGINA]

if not resultados:'''
codigo = codigo.replace(marcador_depois_divider, bloco_paginacao, 1)

# Replace the old loop only once. Network requests now happen in one opt-in batch.
bloco_loop_antigo = '''    colunas = st.columns(2)
    for indice, personagem in enumerate(resultados):
        with colunas[indice % 2]:
            card_personagem(personagem, indice)'''
bloco_loop_novo = r'''    artes_resultados = {}
    if carregar_artes_resultados and resultados_pagina:
        with st.spinner("🖼️ Carregando as artes dos personagens desta página..."):
            artes_resultados = buscar_artes_em_lote(
                tuple(personagem["nome"] for personagem in resultados_pagina)
            )

    colunas = st.columns(2)
    for indice, personagem in enumerate(resultados_pagina):
        with colunas[indice % 2]:
            card_personagem(
                personagem,
                _indice_inicio + indice,
                artes=artes_resultados,
                carregar_arte=carregar_artes_resultados,
            )'''
if codigo.count(bloco_loop_antigo) != 1:
    print("ERRO: não localizei com segurança o loop antigo de cards.")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)
codigo = codigo.replace(bloco_loop_antigo, bloco_loop_novo, 1)

# 4) Os destaques também faziam buscas remotas em toda renderização: tornam-se opt-in.
inicio_destaques = 'buscas_destaque = ["Cynthia", "Giovanni", "N", "Lillie", "Leon", "Nemona"]'
fim_destaques = '\n\n\n# ============================================================\n# KALOS / LEGENDS Z-A'
if codigo.count(inicio_destaques) != 1 or codigo.count(fim_destaques) != 1:
    print("ERRO: não localizei com segurança o bloco de destaques.")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(2)

novo_bloco_destaques = r'''buscas_destaque = ["Cynthia", "Giovanni", "N", "Lillie", "Leon", "Nemona"]
destaques = [p for p in PERSONAGENS if p["nome"] in buscas_destaque]
carregar_artes_destaques = st.toggle(
    "🖼️ Carregar artes dos personagens em destaque",
    value=False,
    key="personagens_carregar_artes_destaques_rapido",
    help="Busca separadamente as artes dos seis destaques, somente quando você solicitar.",
)
artes_destaques = {}
if carregar_artes_destaques and destaques:
    with st.spinner("🖼️ Carregando artes dos destaques..."):
        artes_destaques = buscar_artes_em_lote(
            tuple(personagem["nome"] for personagem in destaques)
        )

dest_cols = st.columns(3)
for indice, personagem in enumerate(destaques):
    with dest_cols[indice % 3]:
        imagem = artes_destaques.get(personagem["nome"]) if carregar_artes_destaques else None
        if imagem:
            st.image(imagem, width=130)
        elif not carregar_artes_destaques:
            st.caption("Arte online sob demanda")
        st.markdown(f"### {personagem['nome']}")
        st.caption(f"{personagem['regiao']} • {personagem['categoria']}")
        st.write(personagem["papel"])'''
pos_ini = codigo.index(inicio_destaques)
pos_fim = codigo.index(fim_destaques, pos_ini)
codigo = codigo[:pos_ini] + novo_bloco_destaques + codigo[pos_fim:]

try:
    compile(codigo, str(ALVO), "exec")
except SyntaxError as erro:
    print(f"ERRO de sintaxe na versão preparada: {erro}")
    print("Nenhuma alteração foi gravada; o arquivo original continua intacto.")
    sys.exit(3)

backup = ALVO.with_suffix(ALVO.suffix + ".bak")
if not backup.exists():
    shutil.copy2(ALVO, backup)
ALVO.write_text(codigo, encoding="utf-8")
print("Otimização aplicada com sucesso!")
print(f"Arquivo atualizado: {ALVO}")
print(f"Backup criado (se ainda não existia): {backup}")
print("A página agora abre sem buscas de imagem automáticas, mostra até 12 cards por página e carrega artes em paralelo sob demanda.")
