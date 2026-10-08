from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote_plus

import streamlit as st


# ============================================================
# ⚡ KAYZAC - MASTER POKEMON
# 📜 KAYZAC CRONOLOGIA
# A jornada da franquia: jogos, gerações, regiões, mecânicas e mídia.
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Cronologia Pokémon",
    page_icon="📜",
    layout="wide",
)


# ============================================================
# MODELO DE DADOS
# ============================================================

@dataclass(frozen=True)
class Evento:
    ano: str
    titulo: str
    categoria: str
    subtitulo: str
    descricao: str
    regiao: str = ""
    destaque: str = ""
    ordem: int = 0


# ============================================================
# CRONOLOGIA PRINCIPAL DOS JOGOS
# ============================================================

JOGOS_PRINCIPAIS: list[Evento] = [
    Evento(
        "1996",
        "Pokémon Red & Green",
        "Jogo principal",
        "O começo da jornada nos videogames",
        "Lançados no Japão em 1996 e responsáveis por iniciar a série principal de jogos Pokémon.",
        "Kanto",
        "Primeira geração",
        1,
    ),
    Evento(
        "1998",
        "Pokémon Yellow",
        "Versão especial",
        "Pikachu ganha o centro do palco",
        "Versão especial de Kanto inspirada em elementos da série animada e com Pikachu como companheiro inicial.",
        "Kanto",
        "Pikachu como parceiro",
        2,
    ),
    Evento(
        "1999",
        "Pokémon Gold & Silver",
        "Jogo principal",
        "A expansão para Johto",
        "A segunda geração amplia a fórmula com novos Pokémon e novas mecânicas, além de conectar Johto a Kanto.",
        "Johto",
        "Dia/noite, breeding e itens segurados",
        3,
    ),
    Evento(
        "2000",
        "Pokémon Crystal",
        "Versão especial",
        "A edição aprimorada de Johto",
        "Versão especial de Gold e Silver com conteúdo adicional e foco maior em Suicune.",
        "Johto",
        "Suicune e Battle Tower",
        4,
    ),
    Evento(
        "2002",
        "Pokémon Ruby & Sapphire",
        "Jogo principal",
        "Uma nova geração em Hoenn",
        "A terceira geração leva a série para Hoenn e introduz sistemas como Habilidades, Naturezas e batalhas em dupla.",
        "Hoenn",
        "Habilidades + Naturezas",
        5,
    ),
    Evento(
        "2004",
        "Pokémon FireRed & LeafGreen",
        "Remake",
        "Kanto retorna no Game Boy Advance",
        "Remakes de Red e Green/Blue que recontam a aventura de Kanto com recursos da terceira geração.",
        "Kanto",
        "Primeiro grande remake da série",
        6,
    ),
    Evento(
        "2004",
        "Pokémon Emerald",
        "Versão especial",
        "A terceira versão de Hoenn",
        "Versão aprimorada de Ruby e Sapphire, com Battle Frontier e um papel central para Rayquaza.",
        "Hoenn",
        "Battle Frontier",
        7,
    ),
    Evento(
        "2006",
        "Pokémon Diamond & Pearl",
        "Jogo principal",
        "Sinnoh e a Nintendo DS",
        "A quarta geração introduz Sinnoh, novas evoluções e uma das mudanças de batalha mais importantes da série.",
        "Sinnoh",
        "Separação físico/especial por golpe",
        8,
    ),
    Evento(
        "2008",
        "Pokémon Platinum",
        "Versão especial",
        "A versão definitiva de Sinnoh",
        "Versão aprimorada de Diamond e Pearl com a Distortion World e destaque para Giratina.",
        "Sinnoh",
        "Giratina + Distortion World",
        9,
    ),
    Evento(
        "2009",
        "Pokémon HeartGold & SoulSilver",
        "Remake",
        "Johto volta em grande estilo",
        "Remakes de Gold e Silver com o conteúdo moderno da quarta geração e forte foco na ligação com Kanto.",
        "Johto / Kanto",
        "Pokémon seguindo o treinador",
        10,
    ),
    Evento(
        "2010",
        "Pokémon Black & White",
        "Jogo principal",
        "Uma nova identidade em Unova",
        "A quinta geração apresenta Unova e uma história mais centrada no conflito entre ideais, verdade e a relação entre humanos e Pokémon.",
        "Unova",
        "Estações + história de N",
        11,
    ),
    Evento(
        "2012",
        "Pokémon Black 2 & White 2",
        "Continuação",
        "Uma sequência direta",
        "Primeira continuação direta de um par de jogos principais, ambientada dois anos após Black e White.",
        "Unova",
        "Sequência direta",
        12,
    ),
    Evento(
        "2013",
        "Pokémon X & Y",
        "Jogo principal",
        "A estreia da sexta geração",
        "Kalos leva a série para o Nintendo 3DS, introduz o tipo Fada e inaugura a Mega Evolução nos jogos principais.",
        "Kalos",
        "Mega Evolução + Tipo Fada",
        13,
    ),
    Evento(
        "2014",
        "Pokémon Omega Ruby & Alpha Sapphire",
        "Remake",
        "Hoenn revisitada em 3D",
        "Remakes de Ruby e Sapphire que incorporam elementos da sexta geração e expandem a Mega Evolução.",
        "Hoenn",
        "Delta Episode",
        14,
    ),
    Evento(
        "2016",
        "Pokémon Sun & Moon",
        "Jogo principal",
        "A ruptura com os ginásios tradicionais",
        "Alola introduz Island Trials, formas regionais e Z-Moves como novas peças centrais da aventura.",
        "Alola",
        "Formas de Alola + Z-Moves",
        15,
    ),
    Evento(
        "2017",
        "Pokémon Ultra Sun & Ultra Moon",
        "Versão especial",
        "Uma versão expandida de Alola",
        "Versões aprimoradas de Sun e Moon, com novos acontecimentos, Pokémon e conteúdo envolvendo Necrozma.",
        "Alola",
        "Ultra Beasts + Necrozma",
        16,
    ),
    Evento(
        "2018",
        "Pokémon Let's Go, Pikachu! & Eevee!",
        "Remake / derivado",
        "Kanto com uma nova porta de entrada",
        "Reimaginação de Yellow que usa captura baseada em Pokémon GO e integração com o ecossistema do Nintendo Switch.",
        "Kanto",
        "Pikachu / Eevee como parceiros",
        17,
    ),
    Evento(
        "2019",
        "Pokémon Sword & Shield",
        "Jogo principal",
        "Galar chega ao Nintendo Switch",
        "A oitava geração apresenta Galar e a mecânica Dynamax, incluindo formas Gigantamax para espécies específicas.",
        "Galar",
        "Dynamax + Gigantamax",
        18,
    ),
    Evento(
        "2022",
        "Pokémon Brilliant Diamond & Shining Pearl",
        "Remake",
        "Sinnoh retorna",
        "Remakes de Diamond e Pearl para Nintendo Switch, mantendo a estrutura principal de Sinnoh com uma apresentação renovada.",
        "Sinnoh",
        "Remake de quarta geração",
        19,
    ),
    Evento(
        "2022",
        "Pokémon Legends: Arceus",
        "Spin-off / ação-RPG",
        "Uma visita ao passado de Sinnoh",
        "A aventura em Hisui explora um período antigo ligado à Sinnoh conhecida nos jogos modernos e muda profundamente a forma de explorar e capturar Pokémon.",
        "Hisui",
        "Captura em campo + Estilos Agile/Strong",
        20,
    ),
    Evento(
        "2022",
        "Pokémon Scarlet & Violet",
        "Jogo principal",
        "Paldea e a estrutura de mundo aberto",
        "A nona geração traz Paldea, múltiplos caminhos narrativos e a Teracristalização como sua grande mecânica de batalha.",
        "Paldea",
        "Teracristalização + mundo aberto",
        21,
    ),
    Evento(
        "2025",
        "Pokémon Legends: Z-A",
        "Spin-off / ação-RPG",
        "O retorno a Lumiose City",
        "A aventura em Kalos acontece na Cidade de Lumiose durante um processo de reurbanização e traz batalhas em tempo real e nova exploração baseada em zonas selvagens.",
        "Kalos",
        "Mega Evolução + Z-A Royale",
        22,
    ),
    Evento(
        "2025",
        "Pokémon Legends: Z-A — Mega Dimension",
        "Conteúdo adicional",
        "A aventura continua",
        "Conteúdo adicional de história lançado após a campanha principal, com distorções de hyperspace, Hoopa e novas Mega Evoluções.",
        "Kalos / Hyperspace",
        "Mega Raichu X e Mega Raichu Y",
        23,
    ),
]


# ============================================================
# OUTROS MARCOS IMPORTANTES
# ============================================================

MARCOS_FRANQUIA: list[Evento] = [
    Evento("1996", "Pokémon Trading Card Game", "TCG", "As cartas ampliam o universo Pokémon", "O Pokémon Estampas Ilustradas expande a franquia para um jogo de cartas colecionáveis.", "Mundo Pokémon", "TCG", 1),
    Evento("1997", "Pokémon — Série de TV", "Anime", "Ash e Pikachu chegam à televisão", "A série animada estreia no Japão e se torna um dos grandes pilares da franquia.", "Kanto", "Anime", 2),
    Evento("1997", "Pokémon Adventures / Special", "Mangá", "A aventura em quadrinhos ganha sua própria identidade", "Pokémon Adventures inaugura uma linha de mangá fortemente ligada aos jogos e suas regiões.", "Kanto", "Mangá", 3),
    Evento("1998", "Pokémon Stadium", "Spin-off", "Batalhas 3D no Nintendo 64", "A série ganha uma experiência focada em batalhas 3D, conectando-se aos jogos da primeira geração.", "Kanto", "Nintendo 64", 4),
    Evento("2003", "Pokémon Colosseum", "Spin-off", "A era Orre começa", "Um RPG no Nintendo GameCube com batalhas em dupla e o conceito de Pokémon Shadow.", "Orre", "Pokémon Shadow", 5),
    Evento("2005", "Pokémon XD: Gale of Darkness", "Spin-off", "A continuação de Orre", "A segunda grande aventura de Orre aprofunda o tema dos Pokémon Shadow e das batalhas em dupla.", "Orre", "Shadow Lugia", 6),
    Evento("2005", "Pokémon Mystery Dungeon", "Spin-off", "Pokémon como protagonistas", "A série Mystery Dungeon coloca o jogador no papel de um Pokémon e cria histórias próprias em mundos de exploração por masmorras.", "Mundo Pokémon", "Pokémon protagonizam a aventura", 7),
    Evento("2016", "Pokémon GO", "Mobile", "Pokémon chega ao mundo real", "O jogo mobile baseado em localização leva captura, coleta e exploração para ambientes do mundo real.", "Mundo real / Pokémon", "Realidade aumentada", 8),
    Evento("2021", "Pokémon UNITE", "MOBA", "Batalhas em equipes", "A franquia entra no gênero MOBA com batalhas estratégicas em equipes e partidas online.", "Mundo Pokémon", "5 contra 5", 9),
    Evento("2023", "Pokémon Sleep", "Mobile", "Um novo jeito de acompanhar Pokémon", "Aplicativo que transforma o acompanhamento do sono em uma experiência de pesquisa e coleção Pokémon.", "Mundo Pokémon", "Sono", 10),
]


# ============================================================
# EVOLUÇÃO DAS MECÂNICAS
# ============================================================

MECANICAS = [
    {
        "geracao": "Geração I",
        "anos": "1996–1999",
        "regiao": "Kanto",
        "emoji": "🌱",
        "titulo": "A fórmula original",
        "itens": ["150 Pokémon originais", "Ginásios e Liga Pokémon", "Pokédex e captura", "TM / HM"],
        "descricao": "A base que definiu a estrutura clássica da série principal.",
    },
    {
        "geracao": "Geração II",
        "anos": "1999–2002",
        "regiao": "Johto",
        "emoji": "🌙",
        "titulo": "Mais vida ao mundo",
        "itens": ["Dia e noite", "Pokémon bebês e breeding", "Itens segurados", "Shiny Pokémon", "Tipos Dark e Steel"],
        "descricao": "A série começa a simular um mundo mais vivo e conectado ao tempo.",
    },
    {
        "geracao": "Geração III",
        "anos": "2002–2006",
        "regiao": "Hoenn",
        "emoji": "🧬",
        "titulo": "Personalidade e habilidades",
        "itens": ["Habilidades", "Naturezas", "Batalhas em dupla", "Concursos", "PokéNav"],
        "descricao": "Os Pokémon passam a ter mais personalidade mecânica e estratégica.",
    },
    {
        "geracao": "Geração IV",
        "anos": "2006–2010",
        "regiao": "Sinnoh",
        "emoji": "⚔️",
        "titulo": "A grande mudança de golpes",
        "itens": ["Separação físico/especial por golpe", "Conectividade online", "Wi-Fi Battles", "Pokétch"],
        "descricao": "A separação entre físico e especial por movimento muda profundamente a estratégia de batalha.",
    },
    {
        "geracao": "Geração V",
        "anos": "2010–2013",
        "regiao": "Unova",
        "emoji": "🌓",
        "titulo": "Narrativa e novas batalhas",
        "itens": ["Seasons", "Triple Battles", "Rotation Battles", "Hidden Abilities", "Dream World"],
        "descricao": "Unova experimenta formatos de batalha e dá forte destaque ao conflito de ideias.",
    },
    {
        "geracao": "Geração VI",
        "anos": "2013–2016",
        "regiao": "Kalos",
        "emoji": "✨",
        "titulo": "Mega Evolução",
        "itens": ["Tipo Fada", "Mega Evolução", "Pokémon-Amie", "Super Training", "Batalhas em 3D"],
        "descricao": "A franquia entra definitivamente na era 3D dos jogos principais e resgata formas temporárias de transformação.",
    },
    {
        "geracao": "Geração VII",
        "anos": "2016–2019",
        "regiao": "Alola",
        "emoji": "🌺",
        "titulo": "Regiões e formas regionais",
        "itens": ["Formas Regionais", "Z-Moves", "Island Trials", "Totem Pokémon", "Ride Pokémon"],
        "descricao": "A própria identidade de uma região passa a alterar a aparência e a forma de funcionamento de espécies conhecidas.",
    },
    {
        "geracao": "Geração VIII",
        "anos": "2019–2022",
        "regiao": "Galar",
        "emoji": "🏟️",
        "titulo": "Gigantamax",
        "itens": ["Dynamax", "Gigantamax", "Wild Area", "Max Raid Battles", "Pokémon acampando"],
        "descricao": "A escala das batalhas aumenta e a exploração começa a assumir áreas mais abertas.",
    },
    {
        "geracao": "Geração IX",
        "anos": "2022–atual",
        "regiao": "Paldea",
        "emoji": "💎",
        "titulo": "Mundo aberto e Teracristal",
        "itens": ["Teracristalização", "Múltiplas rotas narrativas", "Exploração aberta", "Pokémon no mundo", "Cooperação online"],
        "descricao": "Scarlet e Violet consolidam uma estrutura aberta de aventura com múltiplas linhas narrativas.",
    },
    {
        "geracao": "Legends",
        "anos": "2022 / 2025",
        "regiao": "Hisui / Kalos",
        "emoji": "⏳",
        "titulo": "Ação e novas abordagens",
        "itens": ["Captura em campo", "Estilos Agile e Strong", "Exploração em ação-RPG", "Batalhas em tempo real em Z-A", "Wild Zones"],
        "descricao": "Legends: Arceus e Legends: Z-A exploram fórmulas diferentes da linha principal tradicional.",
    },
]


# ============================================================
# REGIÕES / GERAÇÕES
# ============================================================

REGIOES = [
    ("I", "Kanto", "1996", "Red & Green / Blue / Yellow", "🌱", "O ponto de partida da franquia."),
    ("II", "Johto", "1999", "Gold / Silver / Crystal", "🌙", "A região conectada a Kanto e marcada pelo ciclo dia/noite."),
    ("III", "Hoenn", "2002", "Ruby / Sapphire / Emerald", "🌊", "Uma região de oceanos, vulcões, clima e duas equipes rivais."),
    ("IV", "Sinnoh", "2006", "Diamond / Pearl / Platinum", "⛰️", "Uma região montanhosa ligada a mitos de criação do mundo Pokémon."),
    ("Hisui", "Hisui", "2022", "Legends: Arceus", "⏳", "A forma antiga da região que futuramente seria conhecida como Sinnoh."),
    ("V", "Unova", "2010", "Black / White / B2W2", "🗽", "Uma região marcada por grandes cidades e pelo conflito ideológico de N."),
    ("VI", "Kalos", "2013", "X / Y / Legends: Z-A", "🗼", "A região francesa onde a Mega Evolução se tornou um dos maiores símbolos da série."),
    ("VII", "Alola", "2016", "Sun / Moon / USUM", "🌺", "Arquipélago de ilhas com Trials e formas regionais."),
    ("VIII", "Galar", "2019", "Sword / Shield", "🏟️", "Região inspirada no Reino Unido e marcada pelos grandes estádios Pokémon."),
    ("IX", "Paldea", "2022", "Scarlet / Violet", "💎", "Região aberta com múltiplas histórias e Teracristalização."),
]


# ============================================================
# ESTADO
# ============================================================

if "cronologia_visitados" not in st.session_state:
    st.session_state.cronologia_visitados = set()

if "cronologia_filtro_ano" not in st.session_state:
    st.session_state.cronologia_filtro_ano = "Todos"


# ============================================================
# HELPERS
# ============================================================

def youtube_busca(texto: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(texto)}"


def pokemon_site_busca(texto: str) -> str:
    return f"https://www.pokemon.com/br/search/?q={quote_plus(texto)}"


def marcar_evento(chave: str) -> None:
    if chave in st.session_state.cronologia_visitados:
        st.session_state.cronologia_visitados.remove(chave)
    else:
        st.session_state.cronologia_visitados.add(chave)


def card_evento(evento: Evento, indice: int, prefixo: str = "evento") -> None:
    chave = f"{prefixo}|{evento.titulo}|{evento.ano}"
    visitado = chave in st.session_state.cronologia_visitados

    with st.container(border=True):
        esquerda, centro, direita = st.columns([1.15, 5.8, 1.4])

        with esquerda:
            st.markdown(f"## {evento.ano}")
            st.caption(evento.regiao or "Franquia Pokémon")

        with centro:
            st.markdown(f"### {evento.titulo}")
            st.caption(f"**{evento.categoria}** · {evento.subtitulo}")
            st.write(evento.descricao)
            if evento.destaque:
                st.markdown(f"⭐ **Marco:** {evento.destaque}")

        with direita:
            label = "✅ Visitado" if visitado else "📌 Marcar"
            if st.button(label, key=f"marcar_{prefixo}_{evento.ordem}_{evento.ano}_{evento.titulo}", use_container_width=True):
                marcar_evento(chave)
                st.rerun()

            st.link_button(
                "▶️ YouTube",
                youtube_busca(f"Pokémon {evento.titulo} soundtrack"),
                use_container_width=True,
            )


def render_lista_eventos(eventos: Iterable[Evento], busca: str = "", categoria: str = "Todos", ano: str = "Todos", prefixo: str = "evento") -> None:
    eventos_lista = list(eventos)
    termo = busca.strip().lower()

    filtrados: list[Evento] = []
    for evento in eventos_lista:
        texto = " ".join(
            [evento.ano, evento.titulo, evento.categoria, evento.subtitulo, evento.descricao, evento.regiao, evento.destaque]
        ).lower()
        if termo and termo not in texto:
            continue
        if categoria != "Todos" and evento.categoria != categoria:
            continue
        if ano != "Todos" and evento.ano != ano:
            continue
        filtrados.append(evento)

    st.caption(f"{len(filtrados)} marco(s) encontrado(s)")

    for indice, evento in enumerate(filtrados, 1):
        card_evento(evento, indice, prefixo=prefixo)

    if not filtrados:
        st.info("Nenhum marco corresponde aos filtros atuais.")


# ============================================================
# CAPA
# ============================================================

st.title("📜 KAYZAC • CRONOLOGIA POKÉMON")
st.markdown("### A jornada da franquia, geração por geração")
st.caption(
    "Um passeio pela história de Pokémon: jogos principais, spin-offs, anime, mangá, regiões e evolução das mecânicas."
)

st.info(
    "🧭 **Importante:** esta página prioriza a cronologia de lançamento dos produtos e a evolução da franquia. "
    "A ordem dos lançamentos não deve ser confundida com uma única cronologia interna dos acontecimentos do mundo Pokémon."
)


# ============================================================
# RESUMO SUPERIOR
# ============================================================

c1, c2, c3, c4 = st.columns(4)
c1.metric("🎮 Jogos principais", len([e for e in JOGOS_PRINCIPAIS if e.categoria == "Jogo principal"]))
c2.metric("🌎 Regiões / eras", len(REGIOES))
c3.metric("🧩 Gerações de mecânicas", 9)
c4.metric("🏁 Marcos catalogados", len(JOGOS_PRINCIPAIS) + len(MARCOS_FRANQUIA))


# ============================================================
# TABS
# ============================================================

tab_jogos, tab_regioes, tab_mecanicas, tab_midia, tab_progresso = st.tabs(
    [
        "🎮 Linha dos Jogos",
        "🌎 Regiões & Gerações",
        "🧩 Evolução das Mecânicas",
        "🎬 Anime, Mangá & Spin-offs",
        "🏆 Minha Linha do Tempo",
    ]
)


# ============================================================
# 🎮 JOGOS
# ============================================================

with tab_jogos:
    st.markdown("## 🎮 Linha do tempo dos jogos")
    st.write("Da estreia japonesa em 1996 até Pokémon Legends: Z-A e seu conteúdo adicional.")

    col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
    with col_f1:
        busca = st.text_input("🔍 Buscar na cronologia", key="cronologia_busca_jogos", placeholder="Ex.: Mega, Sinnoh, remake...")
    with col_f2:
        categorias = ["Todos"] + sorted({e.categoria for e in JOGOS_PRINCIPAIS})
        categoria = st.selectbox("🏷️ Categoria", categorias, key="cronologia_categoria_jogos")
    with col_f3:
        anos = ["Todos"] + sorted({e.ano for e in JOGOS_PRINCIPAIS}, key=int)
        ano = st.selectbox("📅 Ano", anos, key="cronologia_ano_jogos")

    st.divider()
    render_lista_eventos(JOGOS_PRINCIPAIS, busca=busca, categoria=categoria, ano=ano, prefixo="jogo")

    st.divider()
    st.markdown("### 🔗 Fontes e buscas rápidas")
    a, b = st.columns(2)
    with a:
        st.link_button("🌐 Pokémon.com", "https://www.pokemon.com/br/", use_container_width=True)
    with b:
        st.link_button("▶️ Pokémon no YouTube", "https://www.youtube.com/@Pokemon", use_container_width=True)


# ============================================================
# 🌎 REGIÕES
# ============================================================

with tab_regioes:
    st.markdown("## 🌎 Regiões e gerações")
    st.write("Uma visão rápida de como a geografia do mundo Pokémon foi crescendo ao longo dos anos.")

    for numero, regiao, ano, jogos, emoji, descricao in REGIOES:
        with st.container(border=True):
            a, b, c = st.columns([1.1, 3.2, 2.6])
            with a:
                st.markdown(f"## {emoji}")
                st.caption(f"Geração {numero}")
            with b:
                st.markdown(f"### {regiao}")
                st.markdown(f"📅 **Estreia:** {ano}")
                st.caption(jogos)
            with c:
                st.write(descricao)
                if st.button("🌐 Explorar no KAYZAC", key=f"regiao_{numero}_{regiao}", use_container_width=True):
                    st.session_state["regiao_atual"] = regiao
                    st.info(f"A região **{regiao}** pode ser aprofundada na página de Regiões do KAYZAC.")

    st.divider()
    st.markdown("### 🧭 Uma leitura rápida da evolução")
    st.write(
        "Kanto estabelece a fórmula; Johto expande o mundo; Hoenn aprofunda as batalhas; Sinnoh moderniza a estratégia; "
        "Unova experimenta a narrativa; Kalos populariza a Mega Evolução; Alola transforma a estrutura de progressão; "
        "Galar enfatiza o espetáculo das batalhas; Paldea abre a estrutura narrativa; Hisui e Z-A exploram abordagens diferentes."
    )


# ============================================================
# 🧩 MECÂNICAS
# ============================================================

with tab_mecanicas:
    st.markdown("## 🧩 Como Pokémon mudou ao longo das gerações")
    st.write("Aqui a cronologia não acompanha apenas jogos: ela mostra o que mudou na forma de jogar.")

    for item in MECANICAS:
        with st.container(border=True):
            a, b = st.columns([1.1, 5.9])
            with a:
                st.markdown(f"## {item['emoji']}")
                st.caption(item["anos"])
            with b:
                st.markdown(f"### {item['geracao']} — {item['titulo']}")
                st.caption(f"🌎 {item['regiao']}")
                st.write(item["descricao"])
                st.markdown(" · ".join(f"**{x}**" for x in item["itens"]))

    st.divider()
    st.success(
        "⚡ No KAYZAC, essa evolução também conversa com a Pokédex, Biblioteca e Times: tipos, habilidades, movimentos, "
        "formas, estratégias e sistemas de cada geração podem ser estudados em conjunto."
    )


# ============================================================
# 🎬 MÍDIA / SPIN-OFFS
# ============================================================

with tab_midia:
    st.markdown("## 🎬 Marcos além da linha principal")
    st.write("Pokémon cresceu para muito além dos RPGs principais.")

    col_f1, col_f2 = st.columns([4, 2])
    with col_f1:
        busca_midia = st.text_input("🔍 Buscar marco", key="cronologia_busca_midia", placeholder="Ex.: anime, Orre, TCG...")
    with col_f2:
        categorias_midia = ["Todos"] + sorted({e.categoria for e in MARCOS_FRANQUIA})
        categoria_midia = st.selectbox("🏷️ Categoria", categorias_midia, key="cronologia_categoria_midia")

    st.divider()
    render_lista_eventos(MARCOS_FRANQUIA, busca=busca_midia, categoria=categoria_midia, prefixo="midia")

    st.divider()
    st.markdown("### 📺 Grandes eras do anime")
    eras_anime = [
        ("1997", "Série Original", "Kanto → Ilhas Laranja → Johto", "Ash e Pikachu iniciam a jornada televisiva."),
        ("2002", "Advanced Generation", "Hoenn → Battle Frontier", "A animação acompanha a passagem para a terceira geração."),
        ("2006", "Diamond & Pearl", "Sinnoh", "Dawn e a competição em Sinnoh ganham destaque."),
        ("2010", "Black & White", "Unova", "Unova apresenta uma nova equipe de viagem e novos conflitos."),
        ("2013", "XY / XYZ", "Kalos", "Mega Evolução e Greninja ganham grande espaço na narrativa."),
        ("2016", "Sun & Moon", "Alola", "Uma estrutura escolar e um cotidiano diferente entram em cena."),
        ("2019", "Journeys", "Mundo Pokémon", "A série passa a viajar por várias regiões."),
        ("2023", "Horizontes", "Paldea / Mundo Pokémon", "Liko e Rain assumem o centro da nova fase do anime."),
    ]

    for ano, titulo, regiao, descricao in eras_anime:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 4])
            with c1:
                st.markdown(f"### {ano}")
            with c2:
                st.markdown(f"**📺 {titulo}**")
                st.caption(regiao)
            with c3:
                st.write(descricao)

    st.caption("Os marcos de mídia são apresentados como linha editorial de lançamento e não como uma cronologia única dos acontecimentos internos.")


# ============================================================
# 🏆 PROGRESSO
# ============================================================

with tab_progresso:
    st.markdown("## 🏆 Minha Linha do Tempo")
    progresso = st.session_state.cronologia_visitados

    total = len(JOGOS_PRINCIPAIS) + len(MARCOS_FRANQUIA)
    concluidos = len(progresso)
    percentual = int((concluidos / total) * 100) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("📌 Marcos marcados", concluidos)
    c2.metric("📚 Total catalogado", total)
    c3.metric("⚡ Progresso", f"{percentual}%")

    st.progress(percentual / 100 if total else 0)

    if not progresso:
        st.info("Você ainda não marcou nenhum marco. Explore a cronologia e vá construindo sua própria jornada pelo universo Pokémon.")
    else:
        st.markdown("### ✅ O que você já marcou")
        # Mostramos nomes de forma estável sem depender da estrutura interna das chaves.
        todos = JOGOS_PRINCIPAIS + MARCOS_FRANQUIA
        for evento in sorted(todos, key=lambda x: (int(x.ano) if x.ano.isdigit() else 9999, x.ordem)):
            chave_jogo = f"jogo|{evento.titulo}|{evento.ano}"
            chave_midia = f"midia|{evento.titulo}|{evento.ano}"
            if chave_jogo in progresso or chave_midia in progresso:
                st.write(f"✅ **{evento.ano}** — {evento.titulo}")

        st.divider()
        if st.button("🗑️ Limpar meu progresso da sessão", use_container_width=True):
            st.session_state.cronologia_visitados = set()
            st.rerun()


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "⚡ KAYZAC - MASTER POKEMON · 📜 KAYZAC CRONOLOGIA · Uma linha do tempo feita por fãs para fãs."
)

st.caption(
    "Fontes de referência: Pokémon.com / site oficial de Pokémon / páginas oficiais de Pokémon Legends: Z-A. "
    "A página usa descrições editoriais para organizar a história da franquia."
)
