from __future__ import annotations

"""
🎲 KAYZAC - MASTER POKEMON — Gerador de Desafios

Módulo autoral para criar desafios aleatórios de Pokémon.
Tudo funciona localmente com Streamlit, sem banco de dados ou APIs externas.
"""

import random

import streamlit as st


st.set_page_config(
    page_title="KAYZAC — Desafios",
    page_icon="🎲",
    layout="wide",
)


REGIOES = [
    "Kanto", "Johto", "Hoenn", "Sinnoh", "Unova",
    "Kalos", "Alola", "Galar", "Paldea", "Qualquer região",
]

CATEGORIAS = [
    "Qualquer categoria", "Equipe", "Batalha", "Exploração",
    "Captura", "Treinamento", "Caos",
]

DIFICULDADES = ["Fácil", "Médio", "Difícil", "Extremo"]

REGRAS = {
    "Equipe": [
        "Use apenas Pokémon de um único tipo.",
        "Não repita nenhum tipo na equipe.",
        "Monte uma equipe usando apenas Pokémon encontrados antes do próximo Ginásio.",
        "Use no máximo 3 Pokémon durante a próxima grande batalha.",
        "Seu Pokémon inicial deve permanecer na equipe até o final da aventura.",
        "Escolha uma equipe sem usar Pokémon da mesma espécie.",
        "Use apenas Pokémon que ainda não foram usados em outra aventura sua.",
    ],
    "Batalha": [
        "Vença a próxima batalha sem usar itens durante o combate.",
        "Na próxima batalha importante, nenhum Pokémon pode ser trocado.",
        "Use pelo menos um golpe super efetivo com cada Pokémon que entrar em campo.",
        "Na próxima batalha de rival, use apenas três Pokémon.",
        "Vença uma batalha importante sem usar golpes do mesmo tipo duas vezes seguidas.",
        "O Pokémon que começar a batalha precisa ser o mesmo que terminar.",
    ],
    "Exploração": [
        "Explore uma área inteira antes de avançar para a próxima cidade.",
        "Visite todos os locais opcionais disponíveis antes do próximo Ginásio.",
        "Passe por uma rota usando apenas Pokémon que você encontrou nela.",
        "Encontre um item escondido antes de continuar a jornada.",
        "Complete a próxima área sem usar o Pokémon Center no caminho.",
        "Escolha um Pokémon reserva apenas com base no local onde ele foi encontrado.",
    ],
    "Captura": [
        "A próxima espécie capturada precisa entrar imediatamente na equipe.",
        "Escolha uma nova captura sem repetir nenhum tipo da sua equipe atual.",
        "Na próxima área, capture o primeiro Pokémon elegível que aparecer.",
        "Use uma Ball diferente da sua escolha habitual na próxima captura.",
        "A próxima captura deve permanecer na equipe por pelo menos um Ginásio.",
        "Capture um Pokémon que normalmente você não escolheria.",
    ],
    "Treinamento": [
        "Leve um Pokémon subutilizado ao mesmo nível do seu Pokémon mais forte.",
        "Passe uma área inteira usando apenas dois Pokémon principais.",
        "Ensine um golpe novo a um Pokémon que você quase nunca usa.",
        "Substitua temporariamente seu Pokémon mais forte por um mais fraco.",
        "Faça uma batalha importante usando pelo menos um Pokémon abaixo do nível médio da equipe.",
        "Treine um Pokémon até ele aprender um novo golpe por nível.",
    ],
    "Caos": [
        "Na próxima batalha, escolha aleatoriamente quem começa.",
        "Troque a ordem da sua equipe antes do próximo combate importante.",
        "Use um Pokémon que normalmente ficaria guardado na Box.",
        "Não poderá usar seu Pokémon favorito na próxima batalha importante.",
        "Escolha aleatoriamente um Pokémon da equipe para liderar a próxima rota.",
        "Durante uma rota, use apenas os Pokémon escolhidos por sorteio.",
    ],
}

MODIFICADORES = {
    "Fácil": [
        "Pode ser concluído durante uma única rota.",
        "Pode ser cumprido usando apenas sua equipe atual.",
        "Não exige nenhuma captura nova.",
    ],
    "Médio": [
        "Deve ser mantido até o próximo Ginásio.",
        "Precisa ser cumprido em duas áreas diferentes.",
        "Você pode tentar novamente uma vez caso falhe.",
    ],
    "Difícil": [
        "Deve ser cumprido até o próximo grande marco da história.",
        "Não pode ser ignorado depois que você começar.",
        "A falha encerra o desafio imediatamente.",
    ],
    "Extremo": [
        "Não use itens durante as batalhas relacionadas ao desafio.",
        "A falha significa reiniciar o desafio do zero.",
        "Você não pode trocar a regra depois de começar.",
    ],
}

RECOMPENSAS = [
    "🏆 +1 vitória no seu perfil de treinador",
    "⭐ Escolha um Pokémon para receber o título de MVP",
    "🎖️ Registre o desafio como concluído na sua jornada",
    "⚡ Desbloqueie um novo desafio imediatamente",
    "👑 Dê um apelido especial ao Pokémon que participou",
]


def inicializar_estado() -> None:
    if "desafio_atual" not in st.session_state:
        st.session_state.desafio_atual = None
    if "desafios_historico" not in st.session_state:
        st.session_state.desafios_historico = []
    if "desafios_concluidos" not in st.session_state:
        st.session_state.desafios_concluidos = 0


def gerar_desafio(regiao: str, categoria: str, dificuldade: str) -> dict[str, str]:
    categoria_real = (
        random.choice(list(REGRAS))
        if categoria == "Qualquer categoria"
        else categoria
    )
    return {
        "regiao": regiao,
        "categoria": categoria_real,
        "dificuldade": dificuldade,
        "regra": random.choice(REGRAS[categoria_real]),
        "modificador": random.choice(MODIFICADORES[dificuldade]),
        "recompensa": random.choice(RECOMPENSAS),
    }


def salvar_desafio(desafio: dict[str, str]) -> None:
    st.session_state.desafios_historico.insert(0, desafio)
    st.session_state.desafios_historico = st.session_state.desafios_historico[:10]


inicializar_estado()

st.markdown(
    """
    <div style="padding:1.6rem;border-radius:24px;background:linear-gradient(135deg,#101b38,#080d1d);border:1px solid rgba(90,170,255,.30);margin-bottom:1rem;">
        <h1>🎲 KAYZAC — GERADOR DE DESAFIOS</h1>
        <p>Escolha as regras. Aperte o botão. Aceite o desafio!</p>
        <b>⚡ Crie desafios para suas aventuras Pokémon.</b>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("🎯 Monte seu desafio")
col1, col2, col3 = st.columns(3)
with col1:
    regiao = st.selectbox("🌎 Região", REGIOES, key="desafio_regiao")
with col2:
    categoria = st.selectbox("🏷️ Categoria", CATEGORIAS, key="desafio_categoria")
with col3:
    dificuldade = st.selectbox("🔥 Dificuldade", DIFICULDADES, index=1, key="desafio_dificuldade")

if st.button("🎲 GERAR DESAFIO", use_container_width=True, type="primary"):
    desafio = gerar_desafio(regiao, categoria, dificuldade)
    st.session_state.desafio_atual = desafio
    salvar_desafio(desafio)


desafio_atual = st.session_state.desafio_atual
if desafio_atual:
    st.divider()
    st.subheader("⚡ Seu desafio")
    a, b, c = st.columns(3)
    a.metric("🌎 Região", desafio_atual["regiao"])
    b.metric("🏷️ Categoria", desafio_atual["categoria"])
    c.metric("🔥 Dificuldade", desafio_atual["dificuldade"])

    st.markdown(
        f"""
        <div style="padding:1.4rem;border-radius:20px;border:1px solid rgba(128,128,128,.25);margin-top:.8rem;">
            <h2>🎯 Objetivo</h2>
            <p style="font-size:1.15rem;"><b>{desafio_atual["regra"]}</b></p>
            <h3>📜 Regra adicional</h3>
            <p>{desafio_atual["modificador"]}</p>
            <h3>🏆 Recompensa sugerida</h3>
            <p>{desafio_atual["recompensa"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🎉 Concluir desafio", use_container_width=True):
            st.session_state.desafios_concluidos += 1
            st.session_state.desafio_atual = None
            st.success("🎉 Desafio concluído! Ele entrou para sua jornada.")
            st.rerun()
    with col_b:
        if st.button("🔄 Gerar outro", use_container_width=True):
            novo = gerar_desafio(
                desafio_atual["regiao"],
                desafio_atual["categoria"],
                desafio_atual["dificuldade"],
            )
            st.session_state.desafio_atual = novo
            salvar_desafio(novo)
            st.rerun()
else:
    st.info("🎲 Nenhum desafio ativo ainda. Escolha as opções acima e clique em **GERAR DESAFIO**.")


st.divider()
st.subheader("⚡ Desafios rápidos")
colunas = st.columns(3)
for indice, (icone, nome, descricao) in enumerate([
    ("🥊", "Batalha", "Vença a próxima batalha sem usar itens."),
    ("🧬", "Equipe", "Use uma equipe sem repetir tipos."),
    ("🗺️", "Exploração", "Explore completamente a próxima área."),
]):
    with colunas[indice]:
        st.markdown(f"### {icone} {nome}")
        st.write(descricao)


st.divider()
st.subheader("📖 Histórico de desafios")
if not st.session_state.desafios_historico:
    st.caption("Seus desafios gerados aparecerão aqui.")
else:
    for numero, desafio in enumerate(st.session_state.desafios_historico, start=1):
        with st.container(border=True):
            st.markdown(f"**#{numero} — {desafio['categoria']} • {desafio['dificuldade']}**")
            st.write(desafio["regra"])
            st.caption(f"🌎 {desafio['regiao']} • 📜 {desafio['modificador']}")


st.divider()
c1, c2 = st.columns(2)
c1.metric("🎲 Desafios gerados", len(st.session_state.desafios_historico))
c2.metric("🏆 Desafios concluídos", st.session_state.desafios_concluidos)

st.caption("⚡ KAYZAC - MASTER POKEMON • 14 — Gerador de Desafios")
