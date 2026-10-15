
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
