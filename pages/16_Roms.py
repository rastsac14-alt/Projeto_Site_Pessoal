from __future__ import annotations

"""
🎮 KAYZAC - MASTER POKEMON
16 — ROM HACKS & FAN GAMES

Catálogo de ROM Hacks, Fan Games e portais da comunidade Pokémon.

A página:
- pesquisa e filtra projetos;
- abre uma ficha completa usando expanders;
- permite favoritos persistentes;
- reúne portais/comunidades para encontrar projetos;
- não hospeda ROMs comerciais.
"""

import json
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="KAYZAC — ROM Hacks & Fan Games",
    page_icon="🎮",
    layout="wide",
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_FAVORITOS = (
    BASE_DIR / "roms_fan_games_favoritos.json"
)


# ============================================================
# PORTAIS / COMUNIDADES
# ============================================================

PORTAIS = [
    {
        "nome": "PokeBat",
        "categoria": "Portal brasileiro de ROM Hacks",
        "descricao": (
            "Portal em português voltado à divulgação de "
            "hack-roms Pokémon, com fichas, notícias e biblioteca."
        ),
        "url": "https://pokebat.net/",
        "emoji": "🦇",
    },
    {
        "nome": "HEY!PIKACHU",
        "categoria": "Biblioteca brasileira de ROM Hacks",
        "descricao": (
            "Portal brasileiro com uma biblioteca de ROM Hacks "
            "e atualizações de projetos, incluindo páginas de ficha."
        ),
        "url": "https://midias.heypikachu.com/",
        "emoji": "⚡",
    },
    {
        "nome": "PokéHarbor",
        "categoria": "Portal internacional",
        "descricao": (
            "Portal com categorias de ROM Hacks e Fan Games, "
            "incluindo filtros por plataforma e região."
        ),
        "url": "https://www.pokeharbor.com/",
        "emoji": "⚓",
    },
    {
        "nome": "PokéCommunity",
        "categoria": "Comunidade / desenvolvimento",
        "descricao": (
            "Uma das principais comunidades para showcases, "
            "desenvolvimento de ROM Hacks, Fan Games e recursos."
        ),
        "url": "https://www.pokecommunity.com/",
        "emoji": "🌐",
    },
    {
        "nome": "RainbowDevs",
        "categoria": "Projetos e desenvolvimento",
        "descricao": (
            "Equipe/comunidade associada a projetos como "
            "Pokémon Prism e outras iniciativas de fangame/hacking."
        ),
        "url": "https://rainbowdevs.com/",
        "emoji": "🌈",
    },
]


# ============================================================
# CATÁLOGO DE PROJETOS
# ============================================================

PROJETOS = [
    {
        "nome": "Pokémon Unbound",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Borrius",
        "dificuldade": "Difícil",
        "status": "Concluído",
        "emoji": "🔥",
        "descricao": (
            "ROM Hack de FireRed com uma campanha própria, "
            "região de Borrius, puzzles, conteúdo pós-jogo "
            "e sistemas adicionais."
        ),
        "recursos": [
            "História própria",
            "Região nova",
            "Puzzles",
            "Pós-jogo",
            "Grande variedade de Pokémon",
        ],
        "fonte": "PokéCommunity — tópico do projeto",
        "url": (
            "https://www.pokecommunity.com/threads/"
            "pokemon-unbound-completed.382178/"
        ),
    },
    {
        "nome": "Pokémon Gaia",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Orbtus",
        "dificuldade": "Média",
        "status": "Remake em desenvolvimento",
        "emoji": "🌍",
        "descricao": (
            "ROM Hack de FireRed ambientado na região de Orbtus, "
            "com história própria, novos locais e sistemas adicionais."
        ),
        "recursos": [
            "Região Orbtus",
            "História própria",
            "Novos locais",
            "Mega Evolução",
            "Conteúdo próprio",
        ],
        "fonte": "PokéCommunity — tópico do projeto",
        "url": (
            "https://www.pokecommunity.com/threads/"
            "pokemon-gaia-version.326118/"
        ),
    },
    {
        "nome": "Pokémon Radical Red",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Kanto",
        "dificuldade": "Muito difícil",
        "status": "Versão 4.1 documentada",
        "emoji": "☠️",
        "descricao": (
            "ROM Hack de FireRed focado em desafio, "
            "rebalanço e sistemas modernos."
        ),
        "recursos": [
            "Dificuldade elevada",
            "Rebalanceamento",
            "Pokémon de várias gerações",
            "Sistemas modernos",
            "Customização",
        ],
        "fonte": "PokéCommunity — tópico do projeto",
        "url": (
            "https://www.pokecommunity.com/threads/"
            "pokemon-radical-red-version-4-1-released-gen-9-dlc-"
            "pokemon-character-customization-now-available.437688/"
        ),
    },
    {
        "nome": "Pokémon Prism",
        "tipo": "ROM Hack",
        "base": "Pokémon Crystal",
        "plataforma": "Game Boy / GBC",
        "geracao": "Geração 2",
        "regiao": "Naljo",
        "dificuldade": "Média",
        "status": "Projeto da comunidade",
        "emoji": "💎",
        "descricao": (
            "Modificação de Pokémon Crystal com a região de Naljo, "
            "novas mecânicas e grande quantidade de conteúdo autoral."
        ),
        "recursos": [
            "Região Naljo",
            "Customização",
            "Novas mecânicas",
            "Até 20 insígnias",
            "Qualidade de vida",
        ],
        "fonte": "RainbowDevs — Pokémon Prism",
        "url": "https://rainbowdevs.com/title/prism/",
    },
    {
        "nome": "Pokémon Glazed",
        "tipo": "ROM Hack",
        "base": "Pokémon Emerald",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Regiões próprias",
        "dificuldade": "Média",
        "status": "Clássico da comunidade",
        "emoji": "✨",
        "descricao": (
            "ROM Hack clássico construído sobre Emerald e conhecido "
            "por campanha própria e exploração de regiões adicionais."
        ),
        "recursos": [
            "História própria",
            "Regiões adicionais",
            "Pokémon de várias gerações",
            "Eventos próprios",
        ],
        "fonte": "PokéCommunity — tópico do projeto",
        "url": (
            "https://www.pokecommunity.com/threads/"
            "pokemon-glazed.408226/"
        ),
    },
    {
        "nome": "Pokémon Insurgence",
        "tipo": "Fan Game",
        "base": "Jogo independente",
        "plataforma": "PC",
        "geracao": "Múltiplas gerações",
        "regiao": "Torren",
        "dificuldade": "Difícil",
        "status": "Lançado",
        "emoji": "🧪",
        "descricao": (
            "Fan Game independente com região própria, sistemas "
            "próprios e campanha independente."
        ),
        "recursos": [
            "Região Torren",
            "Delta Pokémon",
            "Mega Evolução",
            "História própria",
            "Sistemas próprios",
        ],
        "fonte": "Site do projeto",
        "url": "https://p-insurgence.com/",
    },
    {
        "nome": "Pokémon Uranium",
        "tipo": "Fan Game",
        "base": "RPG Maker XP",
        "plataforma": "PC",
        "geracao": "Múltiplas gerações",
        "regiao": "Tandor",
        "dificuldade": "Média",
        "status": "Comunidade ativa",
        "emoji": "☢️",
        "descricao": (
            "Fan Game criado em RPG Maker XP com a região de Tandor, "
            "Pokémon originais e o tipo Nuclear."
        ),
        "recursos": [
            "Região Tandor",
            "Pokémon originais",
            "Tipo Nuclear",
            "História própria",
            "Comunidade",
        ],
        "fonte": "Site/comunidade do projeto",
        "url": "https://pokemonuranium.co/",
    },
    {
        "nome": "Pokémon Xenoverse",
        "tipo": "Fan Game",
        "base": "Jogo independente",
        "plataforma": "PC",
        "geracao": "Múltiplas gerações",
        "regiao": "Eldiw",
        "dificuldade": "Média",
        "status": "Lançado",
        "emoji": "🌌",
        "descricao": (
            "Fan Game com a região de Eldiw, a dimensão Xenoverse "
            "e sistemas próprios."
        ),
        "recursos": [
            "Região Eldiw",
            "Xenoverse",
            "X Species",
            "PokéWES",
            "História própria",
        ],
        "fonte": "Site do projeto",
        "url": "https://pokemonxenoverse.com/",
    },
    {
        "nome": "Pokémon Infinite Fusion",
        "tipo": "Fan Game",
        "base": "Jogo independente",
        "plataforma": "PC",
        "geracao": "Múltiplas gerações",
        "regiao": "Kanto / Johto",
        "dificuldade": "Média",
        "status": "Lançado / atualizado",
        "emoji": "🧬",
        "descricao": (
            "Fan Game centrado na fusão de Pokémon, com grande "
            "quantidade de combinações e sprites personalizados."
        ),
        "recursos": [
            "Fusão de Pokémon",
            "Milhares de combinações",
            "Kanto",
            "Johto / pós-jogo",
            "Sidequests",
            "Randomizer",
        ],
        "fonte": "PokéCommunity — tópico do projeto",
        "url": (
            "https://www.pokecommunity.com/threads/"
            "v6-7-pok%C3%A9mon-infinite-fusion-new-pok%C3%A9mon-"
            "character-customization-and-more.347883/"
        ),
    },
    {
        "nome": "Pokémon Stone Dragon 1",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Nova aventura",
        "dificuldade": "Média",
        "status": "Clássico da série",
        "emoji": "🐉",
        "descricao": (
            "Primeiro capítulo da série Stone Dragon. Para esta entrada, "
            "o KAYZAC aponta para o catálogo do PokeBat enquanto a página "
            "específica do primeiro capítulo não está bem indexada."
        ),
        "recursos": [
            "Série Stone Dragon",
            "ROM Hack GBA",
            "Projeto da comunidade",
        ],
        "fonte": "PokeBat — catálogo de ROM Hacks",
        "url": "https://pokebat.net/2017/04/roms-de-pokemon-gba-download.html",
    },
    {
        "nome": "Pokémon Stone Dragon 2",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Kayrus",
        "dificuldade": "Hardcore",
        "status": "Completo",
        "emoji": "🐉",
        "descricao": (
            "Segundo capítulo da série Stone Dragon, ambientado na região "
            "de Kayrus, com nova história, foco em desafio e Mega Evolução."
        ),
        "recursos": [
            "Nova região Kayrus",
            "História própria",
            "Pokémon das gerações 1–7",
            "Mega Evolução",
            "Divisão físico/especial",
        ],
        "fonte": "PokeBat — Stone Dragon 2",
        "url": "https://pokebat.net/2019/03/pokemon-stone-dragon-2-portugues-pt-br-mega-em-batalha.html",
    },
    {
        "nome": "Pokémon Stone Dragon 3",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Unova",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "🐉",
        "descricao": (
            "Terceiro capítulo da série Stone Dragon, com uma nova jornada "
            "baseada em Unova e presença de Ash e da Equipe Plasma."
        ),
        "recursos": [
            "Região inspirada em Unova",
            "Nova história",
            "Pokémon das gerações 1–6",
            "Novos gráficos",
            "EXP All",
        ],
        "fonte": "PokeBat — Stone Dragon 3",
        "url": "https://pokebat.net/2023/08/stone-dragon-3.html",
    },
    {
        "nome": "Pokémon Blue Stars",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Kanto / conteúdo próprio",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "⭐",
        "descricao": (
            "Primeiro Blue Stars, com a história de FireRed atualizada "
            "por mecânicas mais modernas, mapas e conteúdo adicional."
        ),
        "recursos": [
            "Base FireRed",
            "Mecânicas atualizadas",
            "Novos mapas",
            "Pós-jogo",
            "Novos Pokémon",
        ],
        "fonte": "PokeBat — Blue Stars",
        "url": "https://pokebat.net/2018/04/pokemon-blue-stars-pt-br.html",
    },
    {
        "nome": "Pokémon Blue Stars 2",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Conteúdo próprio",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "⭐",
        "descricao": (
            "Sequência de Blue Stars ambientada 35 anos depois do primeiro "
            "jogo, com nova geração de personagens e sistemas modernos."
        ),
        "recursos": [
            "História própria",
            "Pokémon das gerações 1–7",
            "Mega Evolução",
            "Tipo Fada",
            "Pokémon visíveis",
            "Pós-jogo",
        ],
        "fonte": "PokeBat — Blue Stars 2",
        "url": "https://pokebat.net/2019/06/https-pokebat-net-2019-01-pokemon-blues-stars-2-pt-br-html.html",
    },
    {
        "nome": "Pokémon Blue Stars 2 Ultimate",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Conteúdo próprio",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "⭐",
        "descricao": (
            "Edição Ultimate de Blue Stars 2, com eventos adicionais, "
            "revisões e conteúdo pós-jogo."
        ),
        "recursos": [
            "Conteúdo adicional",
            "Pós-jogo",
            "Mega Evolução",
            "Novos eventos",
            "Wonder Trade",
        ],
        "fonte": "PokeBat — Blue Stars 2 Ultimate",
        "url": "https://pokebat.net/2021/06/pokemonbluestars-2.html",
    },
    {
        "nome": "Pokémon Blue Stars 3 FORCES",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Statior",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "⭐",
        "descricao": (
            "Terceiro Blue Stars, com a região de Statior e uma nova trama "
            "envolvendo Cosmog, a Team rival e um eclipse."
        ),
        "recursos": [
            "Região Statior",
            "Pokémon até a 7ª geração",
            "Missões",
            "Mega Evolução",
            "Z-Moves",
            "Pós-jogo",
        ],
        "fonte": "PokeBat — Blue Stars 3 FORCES",
        "url": "https://pokebat.net/2022/10/pokemon-blue-stars-3.html",
    },
    {
        "nome": "Pokémon Blue Stars 4",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Geração 3",
        "regiao": "Shinstar",
        "dificuldade": "Média",
        "status": "Completo",
        "emoji": "⭐",
        "descricao": (
            "Quarto capítulo de Blue Stars, ambientado em Shinstar, com "
            "nova história, missões secundárias e vários sistemas modernos."
        ),
        "recursos": [
            "Região Shinstar",
            "Dynamax e Gigantamax",
            "Mega Evolução",
            "Z-Moves",
            "Level Cap",
            "Eventos secundários",
        ],
        "fonte": "PokeBat — Blue Stars 4",
        "url": "https://pokebat.net/2024/03/pokemon-blue-stars-4-pt-br.html",
    },
    {
        "nome": "Pokémon Quetzal",
        "tipo": "ROM Hack",
        "base": "Emerald",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Hoenn",
        "dificuldade": "Personalizável",
        "status": "Atualizado",
        "emoji": "🐉",
        "descricao": (
            "ROM Hack de Emerald de Tenma com multiplayer cooperativo, "
            "Pokémon de várias gerações e diversos sistemas modernos."
        ),
        "recursos": [
            "Multiplayer cooperativo",
            "Pokémon até a 9ª geração",
            "Mega Evolução",
            "Z-Moves",
            "Dynamax/Gigantamax",
            "Terastalização",
            "Pokémon como personagens jogáveis",
        ],
        "fonte": "Pokémon Quetzal — site do projeto",
        "url": "https://pokemonquetzal.app/",
    },
    {
        "nome": "Pokémon Super Dark Workship",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Seafood",
        "dificuldade": "Personalizável",
        "status": "Versão 2.0.3 catalogada",
        "emoji": "🌑",
        "descricao": (
            "Hack brasileira com história própria, sistemas modernos e "
            "forte identidade visual, catalogada atualmente pelo HEY!PIKACHU."
        ),
        "recursos": [
            "História própria",
            "Mega Evolução",
            "Z-Moves",
            "Dynamax",
            "Sidequests",
            "Diferentes dificuldades",
        ],
        "fonte": "HEY!PIKACHU",
        "url": "https://midias.heypikachu.com/2024/05/pokemon-super-dark-workship.html",
    },
    {
        "nome": "Pokémon Duality",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Lumina",
        "dificuldade": "Personalizável",
        "status": "Em desenvolvimento",
        "emoji": "⚖️",
        "descricao": (
            "Hack de Jean Stars ambientada em Lumina, com a proposta de "
            "duas campanhas distintas: uma trajetória de herói e outra ligada "
            "à equipe vilã."
        ),
        "recursos": [
            "Região Lumina",
            "Duas campanhas",
            "História própria",
            "Mega Evolução",
            "Z-Moves",
            "Dynamax",
        ],
        "fonte": "TioFail — Pokémon Duality",
        "url": "https://tiofail.com/2025/12/pokemon-duality/",
    },
    {
        "nome": "Pokémon Dark Worship 2",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Sinnoh",
        "dificuldade": "Difícil",
        "status": "Beta / em desenvolvimento",
        "emoji": "🕯️",
        "descricao": (
            "Continuação de Dark Worship, com nova história em Sinnoh, "
            "27 opções de iniciais, modos de dificuldade e sistemas modernos."
        ),
        "recursos": [
            "História em Sinnoh",
            "27 iniciais",
            "Following Pokémon",
            "Modos de dificuldade",
            "Z-Moves",
            "QoL",
        ],
        "fonte": "TioFail — Pokémon Dark Worship 2",
        "url": "https://tiofail.com/2025/12/pokemon-dark-worship-2-2/",
    },
    {
        "nome": "Pokémon Elite Redux",
        "tipo": "ROM Hack",
        "base": "Emerald",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Hoenn",
        "dificuldade": "Muito difícil",
        "status": "Ativo",
        "emoji": "⚔️",
        "descricao": (
            "Hack de Emerald focado em batalhas estratégicas, com múltiplas "
            "habilidades simultâneas e forte rebalanço competitivo."
        ),
        "recursos": [
            "Até 4 habilidades simultâneas",
            "IA aprimorada",
            "Múltiplos modos de dificuldade",
            "Sem grind tradicional",
            "Moves e habilidades reequilibrados",
        ],
        "fonte": "Pokémon Elite Redux — GitHub / site do projeto",
        "url": "https://elite-redux.com/",
    },
    {
        "nome": "Pokémon R.O.W.E",
        "tipo": "ROM Hack",
        "base": "Emerald",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Hoenn",
        "dificuldade": "Média",
        "status": "Ativo",
        "emoji": "🗺️",
        "descricao": (
            "Hack de Emerald com foco em exploração aberta e estrutura de "
            "aventura mais flexível, com código-fonte e atualizações comunitárias."
        ),
        "recursos": [
            "Exploração aberta",
            "Estrutura não linear",
            "Projeto open source",
            "Patcher próprio",
        ],
        "fonte": "GitHub — projeto Pokémon R.O.W.E",
        "url": "https://github.com/Iamdivinefox/Rowe",
    },
    {
        "nome": "Pokémon Emerald Imperium",
        "tipo": "ROM Hack",
        "base": "Emerald",
        "plataforma": "GBA",
        "geracao": "Gerações 1–9",
        "regiao": "Hoenn",
        "dificuldade": "Difícil",
        "status": "Ativo",
        "emoji": "👑",
        "descricao": (
            "Hack de Emerald com foco em batalhas estratégicas, escalada de "
            "dificuldade, Nuzlocke e reequilíbrio geral da aventura."
        ),
        "recursos": [
            "Pokémon das gerações 1–9",
            "27 iniciais",
            "Mega Evolução",
            "DexNav",
            "Randomizer",
            "Cheats internos",
        ],
        "fonte": "GitHub — Pokémon Emerald Imperium",
        "url": "https://github.com/pokemonemeraldimperium",
    },
    {
        "nome": "Pokémon MegaRed Version",
        "tipo": "ROM Hack",
        "base": "FireRed",
        "plataforma": "GBA",
        "geracao": "Gerações 1–9",
        "regiao": "Kanto",
        "dificuldade": "Difícil",
        "status": "Completo",
        "emoji": "💥",
        "descricao": (
            "Hack de FireRed com foco em Mega Evoluções, formas de comunidade, "
            "conteúdo até a 9ª geração e desafios mais fortes."
        ),
        "recursos": [
            "Mega Evoluções inéditas",
            "Z-Moves",
            "Dynamax",
            "Pokémon das gerações 1–9",
            "Chefes opcionais",
            "Pós-jogo expandido",
        ],
        "fonte": "HEY!PIKACHU — MegaRed Version",
        "url": "https://midias.heypikachu.com/2026/06/pokemon-megared-version.html",
    },
    {
        "nome": "Pokémon Emerald Rogue",
        "tipo": "ROM Hack",
        "base": "Emerald",
        "plataforma": "GBA",
        "geracao": "Múltiplas gerações",
        "regiao": "Hoenn / estrutura roguelike",
        "dificuldade": "Difícil",
        "status": "Atualizado",
        "emoji": "🎲",
        "descricao": (
            "Projeto que transforma Emerald em uma experiência de progressão "
            "roguelike, com partidas e rotas altamente rejogáveis."
        ),
        "recursos": [
            "Estrutura roguelike",
            "Runs rejogáveis",
            "Randomização",
            "Desafios",
            "Progressão própria",
        ],
        "fonte": "HEY!PIKACHU — biblioteca de ROM Hacks",
        "url": "https://midias.heypikachu.com/",
    },
    {
        "nome": "Pokémon Light Platinum DS",
        "tipo": "ROM Hack",
        "base": "Pokémon Platinum",
        "plataforma": "Nintendo DS",
        "geracao": "Geração 4",
        "regiao": "Região própria",
        "dificuldade": "Média",
        "status": "Em desenvolvimento",
        "emoji": "💡",
        "descricao": (
            "Projeto NDS baseado no clássico Light Platinum, atualmente "
            "catalogado pelo HEY!PIKACHU como hack em desenvolvimento."
        ),
        "recursos": [
            "Nintendo DS",
            "Projeto baseado em Light Platinum",
            "História própria",
            "Novos conteúdos",
        ],
        "fonte": "HEY!PIKACHU — Light Platinum DS",
        "url": "https://midias.heypikachu.com/2026/06/pokemon-light-platinum-ds.html",
    },
    {
        "nome": "Pokémon Crystal Advance Redux",
        "tipo": "ROM Hack",
        "base": "Crystal",
        "plataforma": "GBC",
        "geracao": "Geração 2",
        "regiao": "Johto",
        "dificuldade": "Média",
        "status": "Atualizado",
        "emoji": "💎",
        "descricao": (
            "Projeto de Crystal atualizado e catalogado pelo HEY!PIKACHU, "
            "levando mecânicas modernas para a base de Geração 2."
        ),
        "recursos": [
            "Base Crystal",
            "Mecânicas modernas",
            "Johto",
            "Projeto da comunidade",
        ],
        "fonte": "HEY!PIKACHU — biblioteca de ROM Hacks",
        "url": "https://midias.heypikachu.com/",
    },

]


# ============================================================
# FAVORITOS
# ============================================================

def carregar_favoritos() -> list[str]:
    if not ARQUIVO_FAVORITOS.exists():
        return []

    try:
        with ARQUIVO_FAVORITOS.open(
            "r",
            encoding="utf-8",
        ) as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return [
                str(item)
                for item in dados
                if str(item).strip()
            ]

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return []


def salvar_favoritos(
    favoritos: list[str],
) -> None:
    try:
        ARQUIVO_FAVORITOS.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with ARQUIVO_FAVORITOS.open(
            "w",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                sorted(set(favoritos)),
                arquivo,
                ensure_ascii=False,
                indent=4,
            )

    except OSError:
        st.error(
            "❌ Não foi possível salvar os favoritos."
        )


def inicializar_estado() -> None:
    if "rom_favoritos" not in st.session_state:
        st.session_state.rom_favoritos = (
            carregar_favoritos()
        )


def alternar_favorito(
    nome: str,
) -> None:
    favoritos = list(
        st.session_state.rom_favoritos
    )

    if nome in favoritos:
        favoritos.remove(nome)
    else:
        favoritos.append(nome)

    st.session_state.rom_favoritos = favoritos
    salvar_favoritos(favoritos)


def buscar_projeto(
    nome: str,
) -> dict | None:
    for projeto in PROJETOS:
        if projeto["nome"] == nome:
            return projeto

    return None


# ============================================================
# HELPERS VISUAIS
# ============================================================

def texto_status(
    status: str,
) -> str:
    texto = status.lower()

    if "concluído" in texto:
        return "✅ " + status

    if "lançado" in texto:
        return "✅ " + status

    if "desenvolvimento" in texto:
        return "🛠️ " + status

    if "atualização" in texto:
        return "🔄 " + status

    return "📌 " + status


# ============================================================
# INICIALIZAÇÃO
# ============================================================

inicializar_estado()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div style="
        padding: 1.7rem;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                #101b38,
                #080d1d
            );
        border: 1px solid
            rgba(90,170,255,.30);
        margin-bottom: 1rem;
    ">
        <h1>🎮 KAYZAC — ROM HACKS & FAN GAMES</h1>
        <p>
            Explore ROM Hacks, Fan Games e comunidades
            da cena Pokémon.
        </p>
        <b>
            ⚡ Descubra • Conheça • Favorite • Explore
        </b>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "ℹ️ O KAYZAC funciona como catálogo e portal de descoberta. "
    "Para cada projeto, use a página da equipe/comunidade "
    "correspondente para obter as versões disponíveis."
)


# ============================================================
# RESUMO
# ============================================================

total_rom_hacks = sum(
    projeto["tipo"] == "ROM Hack"
    for projeto in PROJETOS
)

total_fan_games = sum(
    projeto["tipo"] == "Fan Game"
    for projeto in PROJETOS
)

total_favoritos = len(
    st.session_state.rom_favoritos
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🧩 ROM Hacks",
        total_rom_hacks,
    )

with col2:
    st.metric(
        "🎮 Fan Games",
        total_fan_games,
    )

with col3:
    st.metric(
        "⭐ Favoritos",
        total_favoritos,
    )


# ============================================================
# PORTAIS DA COMUNIDADE
# ============================================================

st.divider()
st.subheader(
    "🌐 Portais e comunidades"
)

st.caption(
    "Aqui ficam atalhos para sites que catalogam, "
    "divulgam ou desenvolvem projetos Pokémon."
)

colunas_portais = st.columns(3)

for indice, portal in enumerate(PORTAIS):

    with colunas_portais[indice % 3]:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {portal['emoji']} "
                f"{portal['nome']}"
            )

            st.caption(
                portal["categoria"]
            )

            st.write(
                portal["descricao"]
            )

            st.link_button(
                "🌐 Abrir portal",
                portal["url"],
                use_container_width=True,
            )


# ============================================================
# FILTROS
# ============================================================

st.divider()
st.subheader(
    "🔎 Explorar projetos"
)

pesquisa = st.text_input(
    "🔍 Pesquisar",
    placeholder=(
        "Ex.: Unbound, GBA, difícil, Kanto..."
    ),
    key="rom_pesquisa",
)

coluna_a, coluna_b, coluna_c = st.columns(3)

tipos_disponiveis = sorted(
    {
        projeto["tipo"]
        for projeto in PROJETOS
    }
)

bases_disponiveis = sorted(
    {
        projeto["base"]
        for projeto in PROJETOS
    }
)

dificuldades_disponiveis = sorted(
    {
        projeto["dificuldade"]
        for projeto in PROJETOS
    }
)

with coluna_a:

    filtro_tipo = st.selectbox(
        "🎮 Tipo",
        ["Todos"] + tipos_disponiveis,
        key="rom_filtro_tipo_v2",
    )

with coluna_b:

    filtro_base = st.selectbox(
        "💾 Base / Engine",
        ["Todas"] + bases_disponiveis,
        key="rom_filtro_base_v2",
    )

with coluna_c:

    filtro_dificuldade = st.selectbox(
        "⚔️ Dificuldade",
        ["Todas"] + dificuldades_disponiveis,
        key="rom_filtro_dificuldade_v2",
    )


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

projetos_filtrados = []

pesquisa_normalizada = (
    pesquisa.strip().lower()
)

for projeto in PROJETOS:

    if (
        filtro_tipo != "Todos"
        and projeto["tipo"] != filtro_tipo
    ):
        continue

    if (
        filtro_base != "Todas"
        and projeto["base"] != filtro_base
    ):
        continue

    if (
        filtro_dificuldade != "Todas"
        and projeto["dificuldade"]
        != filtro_dificuldade
    ):
        continue

    if pesquisa_normalizada:

        campos = " ".join(
            [
                projeto["nome"],
                projeto["tipo"],
                projeto["base"],
                projeto["plataforma"],
                projeto["geracao"],
                projeto["regiao"],
                projeto["dificuldade"],
                projeto["status"],
                projeto["descricao"],
                " ".join(
                    projeto["recursos"]
                ),
            ]
        ).lower()

        if (
            pesquisa_normalizada
            not in campos
        ):
            continue

    projetos_filtrados.append(
        projeto
    )


st.caption(
    f"📚 {len(projetos_filtrados)} "
    "projeto(s) encontrado(s)."
)


# ============================================================
# PROJETOS + FICHA
# ============================================================

if not projetos_filtrados:

    st.warning(
        "🔍 Nenhum projeto corresponde "
        "aos filtros atuais."
    )

else:

    colunas = st.columns(2)

    for indice, projeto in enumerate(
        projetos_filtrados
    ):

        with colunas[
            indice % 2
        ]:

            favorito = (
                projeto["nome"]
                in st.session_state.rom_favoritos
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"## {projeto['emoji']} "
                    f"{projeto['nome']}"
                )

                st.caption(
                    f"**{projeto['tipo']}** • "
                    f"{projeto['base']} • "
                    f"{projeto['plataforma']}"
                )

                st.write(
                    projeto["descricao"]
                )

                st.write(
                    f"🌍 **Região:** "
                    f"{projeto['regiao']}"
                )

                st.write(
                    f"⚔️ **Dificuldade:** "
                    f"{projeto['dificuldade']}"
                )

                st.write(
                    f"📌 **Status:** "
                    f"{texto_status(
                        projeto['status']
                    )}"
                )

                col_fav, col_link = (
                    st.columns(2)
                )

                with col_fav:

                    if st.button(
                        (
                            "💛 Favoritado"
                            if favorito
                            else "⭐ Favoritar"
                        ),
                        key=(
                            "favorito_v2_"
                            + projeto["nome"]
                        ),
                        use_container_width=True,
                    ):

                        alternar_favorito(
                            projeto["nome"]
                        )

                        st.rerun()

                with col_link:

                    st.link_button(
                        "🌐 Projeto",
                        projeto["url"],
                        use_container_width=True,
                    )

                # ------------------------------------------------
                # FICHA — AGORA SEM DEPENDER DE SESSION STATE
                # ------------------------------------------------

                with st.expander(
                    "📖 Abrir ficha completa",
                    expanded=False,
                ):

                    st.markdown(
                        f"### {projeto['emoji']} "
                        f"{projeto['nome']}"
                    )

                    info_a, info_b = (
                        st.columns(2)
                    )

                    with info_a:

                        st.write(
                            f"**Tipo:** "
                            f"{projeto['tipo']}"
                        )

                        st.write(
                            f"**Base / Engine:** "
                            f"{projeto['base']}"
                        )

                        st.write(
                            f"**Plataforma:** "
                            f"{projeto['plataforma']}"
                        )

                        st.write(
                            f"**Geração:** "
                            f"{projeto['geracao']}"
                        )

                    with info_b:

                        st.write(
                            f"**Região:** "
                            f"{projeto['regiao']}"
                        )

                        st.write(
                            f"**Dificuldade:** "
                            f"{projeto['dificuldade']}"
                        )

                        st.write(
                            f"**Status:** "
                            f"{projeto['status']}"
                        )

                        st.write(
                            f"**Fonte:** "
                            f"{projeto['fonte']}"
                        )

                    st.markdown(
                        "### ✨ Recursos"
                    )

                    for recurso in (
                        projeto["recursos"]
                    ):
                        st.write(
                            f"🔹 {recurso}"
                        )

                    st.markdown(
                        "### 📖 Descrição"
                    )

                    st.write(
                        projeto["descricao"]
                    )

                    st.link_button(
                        "🌐 Abrir página do projeto",
                        projeto["url"],
                        use_container_width=True,
                    )


# ============================================================
# FAVORITOS
# ============================================================

st.divider()

st.subheader(
    "⭐ Meus ROM Hacks & Fan Games favoritos"
)

projetos_favoritos = [
    buscar_projeto(nome)
    for nome in (
        st.session_state.rom_favoritos
    )
]

projetos_favoritos = [
    projeto
    for projeto in projetos_favoritos
    if projeto is not None
]

if not projetos_favoritos:

    st.info(
        "⭐ Você ainda não favoritou nenhum projeto."
    )

else:

    colunas_fav = st.columns(2)

    for indice, projeto in enumerate(
        projetos_favoritos
    ):

        with colunas_fav[
            indice % 2
        ]:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {projeto['emoji']} "
                    f"{projeto['nome']}"
                )

                st.caption(
                    f"{projeto['tipo']} • "
                    f"{projeto['plataforma']} • "
                    f"{projeto['dificuldade']}"
                )

                st.write(
                    projeto["descricao"]
                )

                col_link, col_remove = (
                    st.columns(2)
                )

                with col_link:

                    st.link_button(
                        "🌐 Abrir projeto",
                        projeto["url"],
                        use_container_width=True,
                    )

                with col_remove:

                    if st.button(
                        "🗑️ Remover",
                        key=(
                            "remover_v2_"
                            + projeto["nome"]
                        ),
                        use_container_width=True,
                    ):

                        alternar_favorito(
                            projeto["nome"]
                        )

                        st.rerun()


# ============================================================
# GUIA
# ============================================================

st.divider()

st.subheader(
    "🧭 Como usar"
)

colunas_guia = st.columns(3)

with colunas_guia[0]:

    st.markdown(
        "### 🔎 1. Pesquise"
    )

    st.write(
        "Use nome, plataforma, região, "
        "dificuldade ou tipo."
    )

with colunas_guia[1]:

    st.markdown(
        "### 📖 2. Abra a ficha"
    )

    st.write(
        "Abra **📖 Ficha completa** diretamente "
        "no card do projeto."
    )

with colunas_guia[2]:

    st.markdown(
        "### ⭐ 3. Favorite"
    )

    st.write(
        "Se encontrar um projeto interessante, "
        "favorite para guardar no KAYZAC."
    )


# ============================================================
# NOTA
# ============================================================

st.divider()

st.caption(
    "⚠️ KAYZAC — catálogo informativo de projetos "
    "de fãs. Pokémon e suas marcas pertencem "
    "aos respectivos proprietários."
)

st.caption(
    "Para ROM Hacks, prefira sempre a página do "
    "projeto/equipe ou uma comunidade reconhecida "
    "para verificar a forma de distribuição da versão."
)

st.caption(
    "⚡ KAYZAC - MASTER POKEMON • "
    "16 — ROM Hacks & Fan Games"
)
