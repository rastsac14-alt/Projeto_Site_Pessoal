from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import requests
import streamlit as st

# ============================================================
# 📚 KAYZAC - MASTER POKEMON
# Biblioteca Pokémon — versão COMPLETA
# Fonte de dados principal: PokéAPI
# ============================================================

st.set_page_config(
    page_title="KAYZAC - Biblioteca Pokémon",
    page_icon="📚",
    layout="wide",
)

BASE_URL = "https://pokeapi.co/api/v2"
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache_kayzac_biblioteca"
CACHE_DIR.mkdir(exist_ok=True)

LANGS = ("pt-br", "pt", "en")


# ============================================================
# 🧪 TIPOS EXCLUSIVOS / CLASSIFICAÇÕES ESPECIAIS KAYZAC
# ============================================================
# Importante: somente ??? e Stellar possuem histórico de tipo
# reconhecido oficialmente na série principal. Shadow é uma
# classificação/mecânica dos jogos de Orre, enquanto Som, Arma,
# Vento e Anime são subtipos experimentais do projeto KAYZAC.

TIPOS_ESPECIAIS_KAYZAC = {
    "???": {
        "emoji": "❓",
        "status": "Histórico oficial — aposentado",
        "origem": "Geração II (1999/2000), criada pela Game Freak para representar o misterioso movimento Curse e, em Geração III, a tipagem visual de Eggs.",
        "quando": "Geração II → Geração IV; removido da série principal a partir da Geração V.",
        "quem": "Game Freak / série principal",
        "natureza": "Tipo oficial legado",
        "vantagens": ["Nenhuma — era neutro contra todos os tipos"],
        "desvantagens": ["Nenhuma — todos os tipos também eram neutros contra ???"],
        "pokemon": [
            "Pokémon Eggs (exibição em certos jogos)",
            "Unown (associação temática ao desconhecido)",
            "Arceus (associação temática ao tipo ???)",
            "Porygon (associação temática à identidade/tipagem digital)",
            "Porygon2 (associação temática à identidade/tipagem digital)",
            "Porygon-Z (associação temática à identidade/tipagem digital)",
        ],
        "movimentos": ["Curse (era originalmente ???)", "Conversion não podia se transformar em ???"],
        "habilidades": ["Não houve habilidade própria do tipo ???"],
        "semelhantes": ["Normal", "Ghost", "Typeless"],
        "compatibilidade": "Funciona melhor como classificação de desconhecido/placeholder do que como elemento ofensivo.",
        "nota": "O ??? era neutro contra todos os tipos. Curse mudou para Ghost na Geração V.",
    },
    "Estelar": {
        "emoji": "⭐",
        "status": "Oficial — tipo especial da Geração IX",
        "origem": "Introduzido em Pokémon Scarlet e Violet através da mecânica de Terastalização, ligado à influência de Terapagos em Area Zero.",
        "quando": "Geração IX — The Indigo Disk (2023).",
        "quem": "Game Freak / Pokémon Scarlet e Violet",
        "natureza": "Tipo especial de Terastalização",
        "vantagens": ["Contra Pokémon já Terastalizados — Stellar Tera Blast é super efetivo"],
        "desvantagens": ["Não possui a tabela defensiva tradicional de um tipo permanente"],
        "pokemon": [
            "Terapagos — Stellar Form",
            "Arceus",
            "Silvally",
            "Mew",
            "Necrozma",
            "Jirachi",
        ],
        "movimentos": ["Tera Blast", "Tera Starstorm"],
        "habilidades": ["Tera Shift", "Teraform Zero", "Tera Shell"],
        "semelhantes": ["???", "Shadow", "Normal"],
        "compatibilidade": "Excelente com Pokémon ofensivos que querem cobertura ampla, especialmente usuários de Tera Blast e equipes que valorizam pressão após a Terastalização.",
        "nota": "Stellar continua sendo uma exceção oficial: é um tipo especial ligado à Terastalização. Os demais Pokémon da lista são representantes temáticos do KAYZAC, não portadores naturais da tipagem Stellar.",
    },
    "Shadow": {
        "emoji": "🌑",
        "status": "Oficial em spin-offs — classificação/mecânica especial",
        "origem": "Shadow Lugia vem de Pokémon XD: Gale of Darkness (2005); Shadow Mewtwo vem de Pokkén Tournament (2015).",
        "quando": "O conceito Shadow foi introduzido em Pokémon Colosseum/XD e reutilizado em outras mídias; não é um tipo permanente da série principal.",
        "quem": "Nintendo / Genius Sonority / projetos Pokémon de Orre e outras mídias Pokémon",
        "natureza": "Classificação/mecânica especial de Pokémon e movimentos Shadow",
        "vantagens": ["Em XD, movimentos Shadow são super efetivos contra Pokémon não-Shadow", "Em Colosseum, Shadow Rush era neutro contra todos"],
        "desvantagens": ["Em XD, movimentos Shadow são pouco efetivos contra Pokémon Shadow"],
        "pokemon": ["Shadow Lugia", "Shadow Mewtwo"],
        "movimentos": ["Shadow Rush", "Shadow Blitz", "Shadow Wave", "Shadow Rave", "Shadow Half", "e outros Shadow moves de XD"],
        "habilidades": ["Não há uma habilidade universal 'Shadow' equivalente a um tipo principal"],
        "semelhantes": ["Sombrio", "Fantasma", "???", "Estelar"],
        "compatibilidade": "Combina melhor com Pokémon sombrios, corrompidos ou com mecânicas de purificação, além de movimentos que representam energia obscura.",
        "nota": "Shadow não era uma tipagem normal do Pokémon: em Colosseum/XD, os movimentos Shadow tinham regras próprias e os Pokémon mantinham suas tipagens normais.",
    },
    "Som": {
        "emoji": "🎵",
        "status": "Fanon / subtipo experimental KAYZAC",
        "origem": "Não existe uma adoção oficial única. 'Sound' é um conceito recorrente em projetos e universos fan-made, inspirado na grande quantidade de movimentos sonoros, Pokémon musicais e criaturas associadas a voz, vibração e ressonância.",
        "quando": "Conceito fan-made recorrente; no KAYZAC, a classificação é organizada por afinidade sonora.",
        "quem": "Comunidade fan-made / KAYZAC",
        "natureza": "Subtipo temático",
        "vantagens": [
            "Vantagem teórica contra Psíquico",
            "Vantagem teórica contra Voador",
            "Vantagem teórica contra Gelo",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Aço",
            "Desvantagem teórica contra Água",
            "Desvantagem teórica contra Fada",
        ],
        "pokemon": [
            # Base original do KAYZAC + expansão do subtipo Som
            "Igglybuff", "Jigglypuff", "Wigglytuff",
            "Popplio", "Brionne", "Primarina",
            "Whismur", "Loudred", "Exploud",
            "Chatot", "Kricketot", "Kricketune",
            "Chingling", "Chimecho",
            "Bronzor", "Bronzong",
            "Zubat", "Golbat", "Crobat",
            "Woobat", "Swoobat",
            "Noibat", "Noivern",
            "Vibrava", "Flygon",
            "Seismitoad",
            "Toxtricity",
            "Meloetta", "Oricorio", "Rillaboom",
            "Jangmo-o", "Hakamo-o", "Kommo-o",
            "Skeledirge", "Lapras",
        ],
        "categorias_pokemon": {
            "🎤 Vocal / Canto": [
                "Igglybuff", "Jigglypuff", "Wigglytuff",
                "Popplio", "Brionne", "Primarina",
                "Whismur", "Loudred", "Exploud",
                "Chatot", "Meloetta", "Skeledirge", "Lapras",
            ],
            "🎸 Música / Performance": [
                "Chatot", "Kricketot", "Kricketune",
                "Toxtricity", "Popplio", "Primarina",
                "Meloetta", "Oricorio", "Rillaboom",
            ],
            "🔔 Ressonância / Sinos / Metal": [
                "Chingling", "Chimecho", "Bronzor", "Bronzong",
            ],
            "📡 Som / Vibração / Ultrassom": [
                "Zubat", "Golbat", "Crobat",
                "Woobat", "Swoobat",
                "Noibat", "Noivern",
                "Vibrava", "Flygon", "Seismitoad",
                "Whismur", "Loudred", "Exploud",
                "Jangmo-o", "Hakamo-o", "Kommo-o",
                "Toxtricity",
            ],
            "🥁 Ritmo / Instrumentos / Impacto sonoro": [
                "Kricketot", "Kricketune", "Rillaboom",
                "Toxtricity", "Kommo-o", "Chatot",
            ],
        },
        "movimentos": [
            "Hyper Voice", "Boomburst", "Echoed Voice", "Uproar",
            "Perish Song", "Sing", "Round", "Snore", "Chatter",
            "Bug Buzz", "Clanging Scales", "Clangorous Soul",
            "Clangorous Soulblaze", "Relic Song", "Sparkling Aria",
            "Torch Song", "Overdrive", "Alluring Voice", "Disarming Voice",
            "Growl", "Howl", "Noble Roar", "Roar", "Screech",
            "Supersonic", "Metal Sound", "Snarl",
        ],
        "habilidades": [
            "Punk Rock",
            "Soundproof",
            "Liquid Voice",
        ],
        "semelhantes": ["Normal", "Voador", "Elétrico", "Psíquico"],
        "compatibilidade": "Muito alta com Pokémon focados em canto, música, gritos, instrumentos, vibrações, ressonância, ultrassom ou ataques classificados como sound-based.",
        "nota": "As categorias e vantagens/desvantagens são uma classificação teórica do KAYZAC, não uma tipagem oficial da franquia.",
    },
    "Arma": {
        "emoji": "⚔️",
        "status": "Fanon / subtipo experimental KAYZAC",
        "origem": (
            "Não existe um 'Tipo Arma' oficial nos jogos principais. No KAYZAC, "
            "a classificação representa Pokémon cujo design, anatomia, movimentos, "
            "equipamentos ou temática remetem claramente a armas e sistemas de combate."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral",
        "natureza": "Subtipo temático de armamento",
        "vantagens": [
            "Vantagem teórica contra Gelo",
            "Vantagem teórica contra Pedra",
            "Vantagem teórica contra Planta",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Água",
            "Desvantagem teórica contra Aço",
            "Desvantagem teórica contra Lutador",
        ],
        "pokemon": [
            "Honedge", "Doublade", "Aegislash", "Scyther", "Scizor",
            "Gallade", "Ceruledge", "Bisharp", "Kingambit", "Kartana",
            "Samurott", "Zacian", "Iron Valiant", "Sirfetch’d",
            "Kleavor", "Kabutops", "Haxorus", "Golisopod",
            "Decidueye", "Inteleon", "Tinkaton", "Zamazenta", "Chesnaught",
            "Remoraid", "Octillery", "Blastoise", "Clawitzer", "Genesect", "Dragapult",
            "Voltorb", "Electrode", "Pineco", "Forretress", "Blacephalon",
            "Dhelmise", "Excadrill", "Drilbur", "Timburr", "Gurdurr", "Conkeldurr",
            "Golurk", "Falinks", "Varoom", "Revavroom", "Iron Treads", "Iron Hands",
        ],
        "categorias_pokemon": {
            "⚔️ Espadas & Lâminas": [
                "Honedge", "Doublade", "Aegislash", "Scyther", "Scizor",
                "Gallade", "Sirfetch’d", "Ceruledge", "Bisharp", "Kingambit", "Kartana",
                "Samurott", "Zacian", "Iron Valiant",
            ],
            "🪓 Machados & Foices": [
                "Kleavor", "Kabutops", "Haxorus", "Golisopod",
            ],
            "⛏️ Ferramentas & Mineração": [
                "Drilbur", "Excadrill", "Timburr", "Gurdurr", "Conkeldurr",
            ],
            "🏹 Arcos & Projéteis": [
                "Decidueye", "Gallade",
            ],
            "🔫 Pistolas & Precisão": [
                "Remoraid", "Octillery", "Inteleon",
            ],
            "💥 Canhões / Bazucas / Artilharia": [
                "Blastoise", "Clawitzer", "Genesect", "Dragapult",
            ],
            "💣 Explosivos": [
                "Voltorb", "Electrode", "Pineco", "Forretress", "Blacephalon",
            ],
            "🔨 Martelos & Impacto": [
                "Tinkaton", "Gurdurr", "Conkeldurr",
            ],
            "🛡️ Escudos & Armamento defensivo": [
                "Aegislash", "Zamazenta", "Chesnaught",
            ],
            "⚓ Armas / Ferramentas improvisadas": [
                "Dhelmise", "Golisopod", "Golurk",
            ],
            "🤖 Armamento tecnológico": [
                "Genesect", "Golurk", "Iron Treads", "Iron Hands", "Varoom", "Revavroom",
            ],
            "🪖 Militar / Guerra": [
                "Falinks", "Blastoise", "Genesect", "Golurk",
            ],
        },
        "movimentos": [
            "Sacred Sword", "Night Slash", "Iron Head", "Psycho Cut",
            "Ceaseless Edge", "Bitter Blade", "King's Shield", "Smart Strike",
            "Stone Axe", "Mighty Cleave", "Gigaton Hammer", "Bullet Punch",
            "Bullet Seed", "Rock Blast", "Flash Cannon", "Beak Blast",
            "Fell Stinger", "X-Scissor", "Metal Burst", "Shell Smash",
        ],
        "habilidades": [
            "Sharpness", "Tough Claws", "Sword of Ruin", "Defiant",
            "Stance Change", "Mega Launcher", "Iron Fist", "Steelworker",
            "Bulletproof", "Battle Armor",
        ],
        "semelhantes": ["Aço", "Lutador", "Sombrio", "Pedra"],
        "compatibilidade": (
            "Classificação temática para Pokémon que funcionam como espadachins, "
            "machados, foices, ferramentas de combate, arqueiros, armas de fogo, "
            "canhões, explosivos, escudos ou plataformas de armamento tecnológico."
        ),
        "nota": (
            "As categorias, representantes e interações ofensivas/defensivas são "
            "uma proposta teórica do KAYZAC e não constituem uma tipagem oficial."
        ),
    },
    "Vento": {
        "emoji": "🌪️",
        "status": "Fanon / subtipo experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Vento oficial. No KAYZAC, o subtipo representa "
            "rajadas, correntes de ar, brisas, tornados, furacões, tempestades, "
            "pressão atmosférica, voo sustentado e outras manifestações de vento."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral",
        "natureza": "Subtipo elemental/atmosférico",
        "vantagens": [
            "Vantagem teórica contra Grama",
            "Vantagem teórica contra Inseto",
            "Vantagem teórica contra Lutador",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Elétrico",
            "Desvantagem teórica contra Pedra",
            "Desvantagem teórica contra Aço",
        ],
        "pokemon": [
            "Pidgeot", "Fearow", "Noctowl",
            "Crobat", "Togekiss",
            "Pelipper", "Swellow", "Altaria", "Salamence",
            "Staraptor", "Honchkrow", "Gliscor",
            "Tornadus", "Thundurus", "Landorus",
            "Sigilyph", "Swoobat", "Archeops",
            "Braviary", "Mandibuzz", "Hawlucha",
            "Talonflame", "Noivern", "Oricorio",
            "Corviknight", "Cramorant",
            "Wyrdeer", "Kilowattrel", "Bombirdier", "Flamigo",
            "Whimsicott", "Jumpluff", "Tropius", "Eldegoss",
            "Emolga", "Dragonite", "Rayquaza",
        ],
        "categorias_pokemon": {
            "🌬️ Brisa & Correntes de Ar": [
                "Pidgeot", "Fearow", "Noctowl", "Swellow",
                "Staraptor", "Togekiss", "Talonflame",
                "Corviknight", "Kilowattrel", "Flamigo",
            ],
            "💨 Rajadas & Vento Cortante": [
                "Crobat", "Gliscor", "Hawlucha", "Noivern",
                "Staraptor", "Braviary", "Scyther",
            ],
            "🌪️ Tornados & Ciclones": [
                "Tornadus", "Noivern", "Flygon", "Altaria",
                "Gliscor", "Salamence",
            ],
            "🌀 Furacões & Grandes Tempestades": [
                "Tornadus", "Thundurus", "Rayquaza",
                "Pelipper", "Noivern", "Dragonite",
            ],
            "⛈️ Tempestade & Pressão Atmosférica": [
                "Thundurus", "Zapdos", "Kilowattrel",
                "Pelipper", "Cramorant", "Rayquaza",
            ],
            "☁️ Nuvens & Atmosfera": [
                "Altaria", "Swablu", "Tornadus",
                "Castform", "Jumpluff", "Drifblim",
            ],
            "🍃 Folhas, Pétalas & Vento Natural": [
                "Whimsicott", "Jumpluff", "Tropius", "Eldegoss",
            ],
            "🪽 Voo & Correntes Ascendentes": [
                "Braviary", "Mandibuzz", "Hawlucha",
                "Corviknight", "Talonflame", "Pelipper",
                "Dragonite", "Salamence", "Togekiss",
            ],
            "🔊 Vento, Som & Ultrassom": [
                "Noivern", "Crobat", "Swoobat", "Sigilyph",
            ],
            "🌩️ Vento + Eletricidade": [
                "Thundurus", "Zapdos", "Emolga",
                "Kilowattrel", "Rayquaza",
            ],
            "🐉 Dragões & Poder Atmosférico": [
                "Dragonite", "Salamence", "Altaria",
                "Noivern", "Rayquaza",
            ],
            "🌠 Fenômenos Aéreos Especiais": [
                "Tornadus", "Thundurus", "Landorus",
                "Rayquaza", "Wyrdeer",
            ],
        },
        "movimentos": [
            "Gust", "Twister", "Whirlwind", "Razor Wind",
            "Air Cutter", "Air Slash", "Hurricane",
            "Tailwind", "Icy Wind", "Bleakwind Storm",
            "Springtide Storm", "Sandsear Storm", "Heat Wave",
            "Defog", "Roost", "Aerial Ace", "Acrobatics",
            "Floaty Fall", "Petal Blizzard",
        ],
        "habilidades": [
            "Wind Rider",
            "Wind Power",
            "Gale Wings",
            "Aerilate",
            "Air Lock",
            "Cloud Nine",
        ],
        "semelhantes": ["Voador", "Elétrico", "Gelo", "Água", "Grama"],
        "compatibilidade": (
            "Excelente para Pokémon ligados a correntes de ar, rajadas, voo, "
            "ciclones, furacões, tempestades, pressão atmosférica e movimentos "
            "que manipulam o campo por meio do vento ou da velocidade aérea."
        ),
        "nota": (
            "As categorias, representantes e vantagens/desvantagens são uma "
            "classificação teórica do KAYZAC, não uma tipagem oficial. Um Pokémon "
            "pode pertencer ao subtipo Vento mesmo mantendo uma tipagem oficial diferente."
        ),
    },
    "Cyber": {
        "emoji": "💻",
        "status": "Fanon / subtipo tecnológico experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Cyber oficial. No KAYZAC, Cyber representa Pokémon ligados a "
            "tecnologia, programação, sistemas digitais, inteligência artificial, robótica, "
            "maquinário e formas artificiais de vida."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em tecnologia, ficção científica e cultura digital",
        "natureza": "Subtipo tecnológico / digital / artificial",
        "vantagens": [
            "Vantagem teórica contra Água, porque tecnologia pode explorar redes, sistemas e recursos eletrônicos.",
            "Vantagem teórica contra tipos associados a organismos exclusivamente naturais.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Elétrico quando a energia é instável ou sofre sobrecarga.",
            "Desvantagem teórica contra Terra quando circuitos e máquinas ficam vulneráveis a interferências físicas.",
        ],
        "pokemon": [
            "Porygon", "Porygon2", "Porygon-Z", "Magnemite", "Magneton", "Magnezone",
            "Rotom", "Metagross", "Klinklang", "Genesect", "Golurk", "Varoom", "Revavroom",
            "Iron Treads", "Iron Hands", "Iron Thorns", "Iron Bundle", "Miraidon", "Type: Null",
            "Silvally", "Toxtricity",
        ],
        "categorias_pokemon": {
            "🖥️ Sistemas Digitais & Programação": [
                "Porygon", "Porygon2", "Porygon-Z", "Rotom", "Type: Null", "Silvally",
            ],
            "🤖 Robôs & Máquinas": [
                "Magnemite", "Magneton", "Magnezone", "Metagross", "Klinklang", "Golurk",
            ],
            "⚙️ Motores & Engenharia": [
                "Varoom", "Revavroom", "Iron Treads", "Iron Hands", "Iron Thorns",
            ],
            "🧬 Organismos Artificiais": [
                "Porygon-Z", "Genesect", "Type: Null", "Silvally", "Miraidon",
            ],
            "🔋 Energia & Circuitos": [
                "Rotom", "Toxtricity", "Magnezone", "Iron Hands", "Iron Bundle",
            ],
            "🚀 Tecnologia Futurista": [
                "Iron Treads", "Iron Bundle", "Iron Thorns", "Miraidon", "Metagross",
            ],
            "🛡️ Armas Tecnológicas & Sistemas de Combate": [
                "Genesect", "Golurk", "Metagross", "Iron Hands", "Iron Treads",
            ],
        },
        "movimentos": [
            "Tri Attack", "Conversion", "Conversion 2", "Signal Beam", "Flash Cannon",
            "Thunderbolt", "Electro Drift", "Techno Blast", "Gear Grind", "Shift Gear",
            "Magnet Rise", "Mirror Shot", "Lock-On", "Zap Cannon", "Charge Beam",
            "Hyper Beam", "Flash", "Steel Beam",
        ],
        "habilidades": [
            "Download", "Analytic", "Adaptability", "Levitate", "Motor Drive",
            "Quark Drive", "Clear Body", "Light Metal", "Heavy Metal", "Technician",
        ],
        "semelhantes": ["Elétrico", "Aço", "???", "Arma", "Plástico"],
        "compatibilidade": (
            "Classificação para Pokémon que remetem a computadores, inteligência artificial, robôs, "
            "veículos, máquinas, redes digitais, experimentos tecnológicos ou cenários futuristas."
        ),
        "nota": (
            "Cyber é uma classificação temática do KAYZAC. As associações destacam elementos de "
            "tecnologia e ficção científica, não uma tipagem oficial dos Pokémon."
        ),
    },
    "Cósmico": {
        "emoji": "🌌",
        "status": "Fanon / subtipo espacial e celestial experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Cósmico oficial. No KAYZAC, ele reúne Pokémon associados a estrelas, "
            "planetas, luas, espaço sideral, meteoros, gravidade, dimensões e fenômenos celestes."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em astronomia, espaço e mitologia celeste",
        "natureza": "Subtipo espacial / astronômico / dimensional",
        "vantagens": [
            "Vantagem teórica contra Água, pela associação com marés e influência lunar.",
            "Vantagem teórica contra tipos terrestres, pela escala e manipulação de fenômenos cósmicos.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Sombrio, representando o vazio e a ausência de luz.",
            "Desvantagem teórica contra Aço, associado à resistência de corpos e estruturas tecnológicas espaciais.",
        ],
        "pokemon": [
            "Clefairy", "Clefable", "Starmie", "Lunatone", "Solrock", "Minior",
            "Elgyem", "Beheeyem", "Deoxys", "Jirachi", "Rayquaza", "Cosmog", "Cosmoem",
            "Solgaleo", "Lunala", "Necrozma", "Terapagos", "Dialga", "Palkia", "Giratina", "Eternatus",
        ],
        "categorias_pokemon": {
            "⭐ Estrelas & Constelações": [
                "Clefairy", "Clefable", "Jirachi", "Minior", "Starmie",
            ],
            "🌙 Lua & Noite": [
                "Clefairy", "Clefable", "Lunatone", "Lunala", "Cresselia",
            ],
            "☀️ Sol & Corpos Celestes": [
                "Solrock", "Solgaleo", "Rayquaza", "Terapagos",
            ],
            "☄️ Meteoros & Queda Cósmica": [
                "Minior", "Deoxys", "Rayquaza", "Tyranitar",
            ],
            "🪐 Espaço & Exploração": [
                "Elgyem", "Beheeyem", "Deoxys", "Lunala", "Solgaleo",
            ],
            "🌀 Gravidade & Dimensões": [
                "Palkia", "Dialga", "Giratina", "Necrozma", "Terapagos",
            ],
            "🌠 Energia Cósmica": [
                "Necrozma", "Jirachi", "Rayquaza", "Eternatus", "Terapagos",
            ],
        },
        "movimentos": [
            "Cosmic Power", "Meteor Mash", "Meteor Beam", "Draco Meteor", "Gravity",
            "Psyshock", "Psychic", "Photon Geyser", "Core Enforcer", "Spacial Rend",
            "Roar of Time", "Shadow Force", "Moonblast", "Moonlight", "Solar Beam",
            "Expanding Force", "Psychic Terrain", "Gravity",
        ],
        "habilidades": [
            "Pressure", "Levitate", "Prism Armor", "Neuroforce", "Full Metal Body",
            "Shadow Shield", "Teraform Zero", "Telepathy", "Synchronize",
        ],
        "semelhantes": ["Estelar", "Psíquico", "Luz", "Vento", "???"],
        "compatibilidade": (
            "Representa Pokémon cuja identidade visual, lore, poderes ou habitats remetem diretamente "
            "ao espaço, estrelas, luas, planetas, meteoros, gravidade ou dimensões cósmicas."
        ),
        "nota": (
            "Cósmico é uma classificação fanon do KAYZAC. Ela amplia a leitura espacial de certos Pokémon "
            "sem transformá-la em uma tipagem oficial."
        ),
    },
    "Luz": {
        "emoji": "☀️",
        "status": "Fanon / subtipo de luminosidade experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Luz oficial. No KAYZAC, Luz representa brilho, radiação, auroras, "
            "claridade, purificação, calor luminoso, feixes e Pokémon que simbolizam esperança ou iluminação."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em luminosidade, energia e simbolismo heroico",
        "natureza": "Subtipo luminoso / energético / simbólico",
        "vantagens": [
            "Vantagem teórica contra Sombrio e entidades associadas a escuridão ou medo.",
            "Vantagem teórica contra ambientes subterrâneos ou dependentes de ocultação.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra tipos que absorvem ou bloqueiam luz, como Sombrio e Pedra em contextos específicos.",
            "A classificação continua temática, portanto as interações variam conforme a proposta do KAYZAC.",
        ],
        "pokemon": [
            "Ampharos", "Volcarona", "Togekiss", "Espeon", "Sylveon", "Florges", "Bellossom",
            "Lanturn", "Litwick", "Lampent", "Chandelure", "Shiinotic", "Gardevoir", "Cresselia",
            "Solgaleo", "Ho-Oh", "Xurkitree", "Dedenne", "Ribombee", "Lurantis",
        ],
        "categorias_pokemon": {
            "✨ Brilho & Radiância": [
                "Ampharos", "Togekiss", "Espeon", "Sylveon", "Florges",
            ],
            "🔥 Luz & Calor": [
                "Volcarona", "Chandelure", "Litwick", "Lampent", "Solgaleo",
            ],
            "🌙 Luz Lunar & Aurora": [
                "Cresselia", "Lunala", "Ribombee", "Shiinotic", "Espeon",
            ],
            "🌞 Luz Solar": [
                "Volcarona", "Solgaleo", "Bellossom", "Lurantis", "Ho-Oh",
            ],
            "💡 Lâmpadas & Fontes Artificiais": [
                "Ampharos", "Lanturn", "Litwick", "Lampent", "Chandelure",
            ],
            "🌈 Beleza & Cores Luminosas": [
                "Florges", "Sylveon", "Ribombee", "Gardevoir", "Bellossom",
            ],
            "⚡ Luz Elétrica": [
                "Ampharos", "Lanturn", "Xurkitree", "Dedenne",
            ],
        },
        "movimentos": [
            "Dazzling Gleam", "Moonblast", "Aurora Beam", "Flash", "Light Screen",
            "Morning Sun", "Sunny Day", "Solar Beam", "Prismatic Laser", "Photon Geyser",
            "Signal Beam",
        ],
        "habilidades": [
            "Illuminate", "Dazzling", "Flash Fire", "Flame Body", "Solar Power",
            "Serene Grace", "Pixilate", "Prism Armor",
        ],
        "semelhantes": ["Fada", "Psíquico", "Fogo", "Estelar", "Cósmico"],
        "compatibilidade": (
            "É voltado para Pokémon que literalmente produzem luz ou que, por design e lore, "
            "representam brilho, esperança, purificação, aurora, sol ou energia luminosa."
        ),
        "nota": (
            "Luz é uma classificação temática KAYZAC. Ela não substitui o Tipo Fada, Elétrico, Fogo, "
            "Psíquico ou qualquer outro tipo oficial."
        ),
    },
    "Areia": {
        "emoji": "🏜️",
        "status": "Fanon / subtipo desértico e granular experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Areia oficial. No KAYZAC, Areia reúne Pokémon associados a desertos, "
            "dunas, tempestades de areia, erosão, soterramento, emboscadas subterrâneas e paisagens áridas."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em desertos, geologia e sobrevivência",
        "natureza": "Subtipo geográfico / granular / desértico",
        "vantagens": [
            "Vantagem teórica contra Elétrico, representando isolamento do solo e abrasão em equipamentos.",
            "Vantagem teórica contra Fogo em contextos de soterramento e contenção do terreno.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Água, que dispersa e arrasta areia.",
            "Desvantagem teórica contra Gelo, que pode compactar ou alterar o terreno arenoso.",
        ],
        "pokemon": [
            "Sandshrew", "Sandslash", "Trapinch", "Vibrava", "Flygon", "Hippopotas", "Hippowdon",
            "Sandile", "Krokorok", "Krookodile", "Cacnea", "Cacturne", "Sandygast", "Palossand",
            "Sandaconda", "Stonjourner", "Garchomp", "Excadrill", "Gligar", "Gliscor", "Tyranitar",
        ],
        "categorias_pokemon": {
            "🏜️ Deserto & Dunas": [
                "Sandshrew", "Sandslash", "Hippopotas", "Hippowdon", "Cacnea", "Cacturne",
            ],
            "🌪️ Tempestades de Areia": [
                "Tyranitar", "Hippowdon", "Excadrill", "Krookodile", "Sandaconda",
            ],
            "🕳️ Soterramento & Emboscada": [
                "Trapinch", "Sandile", "Krokorok", "Sandshrew", "Palossand",
            ],
            "🐍 Areia Viva & Serpentes": [
                "Sandaconda", "Krookodile", "Flygon", "Vibrava",
            ],
            "🏺 Ruínas & Areia Antiga": [
                "Sigilyph", "Runerigus", "Palossand", "Stonjourner",
            ],
            "⛏️ Escavação & Subsolo": [
                "Excadrill", "Sandslash", "Garchomp", "Gligar", "Gliscor",
            ],
            "🪨 Areia & Rocha": [
                "Stonjourner", "Garchomp", "Tyranitar", "Hippowdon",
            ],
        },
        "movimentos": [
            "Sand Attack", "Sand Tomb", "Sandstorm", "Scorching Sands", "Dig", "Earthquake",
            "Bulldoze", "Drill Run", "Mud-Slap", "Mud Shot", "Shore Up", "Spikes",
            "Rock Tomb", "Rock Slide", "Stone Edge", "Headlong Rush",
        ],
        "habilidades": [
            "Sand Stream", "Sand Veil", "Sand Rush", "Sand Force", "Sand Spit", "Shed Skin",
            "Arena Trap", "Rough Skin",
        ],
        "semelhantes": ["Terra", "Pedra", "Vento", "Madeira", "Plástico"],
        "compatibilidade": (
            "Classificação para Pokémon que vivem em ambientes áridos ou manipulam areia, poeira, "
            "tempestades de areia, escavação e terreno desértico."
        ),
        "nota": (
            "Areia é um subtipo fanon KAYZAC. Ele é propositalmente mais específico que Terra e Pedra, "
            "focando o fenômeno e o ambiente arenoso."
        ),
    },
    "Madeira": {
        "emoji": "🪵",
        "status": "Fanon / subtipo arbóreo e lenhoso experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Madeira oficial. No KAYZAC, Madeira representa árvores, troncos, cascas, "
            "florestas antigas, espíritos arbóreos, madeira viva e criaturas cuja identidade visual nasce de elementos lenhosos."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em florestas, árvores e natureza ancestral",
        "natureza": "Subtipo natural / arbóreo / lenhoso",
        "vantagens": [
            "Vantagem teórica contra Água por absorção e controle de vegetação em ambientes naturais.",
            "Vantagem teórica contra Terra em cenários de raízes e florestas dominando o terreno.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Fogo, pela vulnerabilidade da madeira à combustão.",
            "Desvantagem teórica contra Inseto, que pode explorar madeira e cascas como alimento ou abrigo.",
        ],
        "pokemon": [
            "Bonsly", "Sudowoodo", "Phantump", "Trevenant", "Exeggcute", "Exeggutor",
            "Exeggutor de Alola", "Torterra", "Shiftry", "Rillaboom", "Arboliva", "Bramblin",
            "Venusaur",
            "Brambleghast", "Ogerpon", "Chesnaught", "Decidueye", "Dhelmise", "Leafeon",
            "Lurantis", "Tsareena", "Simisage",
        ],
        "categorias_pokemon": {
            "🌳 Árvores & Troncos": [
                "Bonsly", "Sudowoodo", "Torterra", "Exeggutor", "Exeggutor de Alola",
            ],
            "👻 Espíritos da Floresta": [
                "Phantump", "Trevenant", "Dhelmise",
            ],
            "🥁 Madeira & Ritmo": [
                "Rillaboom", "Simisage",
            ],
            "🌿 Floresta Ancestral": [
                "Shiftry", "Trevenant", "Torterra", "Ogerpon", "Decidueye",
            ],
            "🌱 Madeira Viva & Crescimento": [
                "Arboliva", "Bramblin", "Brambleghast", "Leafeon", "Lurantis",
            ],
            "🛡️ Armadura Vegetal": [
                "Chesnaught", "Torterra", "Decidueye", "Ogerpon",
            ],
            "🍃 Galhos, Folhas & Cipós": [
                "Venusaur", "Tsareena", "Leafeon", "Lurantis", "Arboliva",
            ],
        },
        "movimentos": [
            "Wood Hammer", "Horn Leech", "Branch Poke", "Trailblaze", "Leaf Blade",
            "Leaf Storm", "Razor Leaf", "Energy Ball", "Seed Bomb", "Grassy Terrain",
            "Leech Seed", "Synthesis", "Drum Beating", "Growth",
        ],
        "habilidades": [
            "Grassy Surge", "Overgrow", "Sap Sipper", "Harvest", "Natural Cure",
            "Leaf Guard", "Regenerator", "Effect Spore", "Prankster",
        ],
        "semelhantes": ["Grama", "Terra", "Areia", "Inseto", "Som"],
        "compatibilidade": (
            "É reservado para Pokémon cuja identidade visual ou mecânica remete diretamente a árvores, "
            "madeira, troncos, cascas, cipós, florestas antigas ou espíritos da natureza."
        ),
        "nota": (
            "Madeira é um subtipo temático KAYZAC, deliberadamente mais específico que o Tipo Grama. "
            "A associação depende do aspecto lenhoso e arbóreo do Pokémon."
        ),
    },
    "Plástico": {
        "emoji": "🧴",
        "status": "Fanon / subtipo sintético e industrial experimental KAYZAC",
        "origem": (
            "Não existe um Tipo Plástico oficial. No KAYZAC, Plástico representa materiais sintéticos, "
            "polímeros, embalagens, borracha, resíduos, objetos manufaturados e criaturas associadas à poluição urbana."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral inspirada em materiais sintéticos, reciclagem e cultura industrial",
        "natureza": "Subtipo material / sintético / industrial",
        "vantagens": [
            "Vantagem teórica contra Água em contextos de impermeabilidade e resíduos flutuantes.",
            "Vantagem teórica contra ambientes naturais quando a poluição e o lixo se tornam dominantes.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra Fogo, devido à combustão de materiais sintéticos.",
            "Desvantagem teórica contra Veneno e Terra em cenários de degradação e contaminação do material.",
        ],
        "pokemon": [
            "Trubbish", "Garbodor", "Grimer", "Muk", "Grimer de Alola", "Muk de Alola",
            "Gulpin", "Swalot", "Porygon", "Porygon2", "Porygon-Z", "Voltorb", "Electrode",
            "Voltorb de Hisui", "Electrode de Hisui", "Ditto", "Drifloon", "Drifblim", "Varoom", "Revavroom",
        ],
        "categorias_pokemon": {
            "♻️ Resíduos & Lixo": [
                "Trubbish", "Garbodor", "Grimer", "Muk", "Gulpin", "Swalot",
            ],
            "🧪 Materiais Sintéticos & Polímeros": [
                "Trubbish", "Garbodor", "Ditto", "Drifloon", "Drifblim",
            ],
            "🖥️ Plástico & Tecnologia": [
                "Porygon", "Porygon2", "Porygon-Z", "Voltorb", "Electrode",
            ],
            "🎈 Borracha, Balões & Revestimentos": [
                "Drifloon", "Drifblim", "Voltorb", "Electrode",
            ],
            "🏭 Indústria & Poluição": [
                "Garbodor", "Muk", "Revavroom", "Varoom",
            ],
            "🧸 Formas Artificiais & Manufaturadas": [
                "Porygon", "Porygon2", "Porygon-Z", "Ditto", "Voltorb",
            ],
            "🛞 Borracha & Maquinário": [
                "Varoom", "Revavroom",
            ],
        },
        "movimentos": [
            "Sludge", "Sludge Bomb", "Gunk Shot", "Recycle", "Take Down", "Tackle",
            "Tri Attack", "Conversion", "Conversion 2", "Explosion", "Self-Destruct",
            "Rollout", "Gyro Ball", "Acid Spray", "Corrosive Gas", "Belch", "Smog",
        ],
        "habilidades": [
            "Stench", "Sticky Hold", "Gluttony", "Aftermath", "Download", "Analytic",
            "Adaptability", "Levitate", "Neutralizing Gas",
        ],
        "semelhantes": ["Cyber", "Veneno", "???", "Arma", "Aço"],
        "compatibilidade": (
            "Classificação voltada para Pokémon que lembram lixo plástico, resíduos industriais, materiais "
            "sintéticos, objetos manufaturados, borracha, polímeros ou tecnologia artificial."
        ),
        "nota": (
            "Plástico é um subtipo fanon KAYZAC e funciona como classificação material. Ele não afirma "
            "que os corpos dos Pokémon sejam literalmente feitos de plástico; a curadoria é baseada em design, lore e conceito."
        ),
    },
    "Sangue": {
        "emoji": "🩸",
        "status": "Fanon / subtipo conceitual KAYZAC",
        "origem": (
            "Não existe um Tipo Sangue oficial. No KAYZAC, a classificação representa sangue, vampirismo, "
            "hematofagia, ferocidade, drenagem de vitalidade e estética carmesim — sempre como conceito temático."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática",
        "natureza": "Subtipo biológico / vitalidade / drenagem",
        "vantagens": ["Vantagem teórica contra classificações frágeis a desgaste e drenagem de vitalidade."],
        "desvantagens": ["Desvantagem teórica contra conceitos de cura, luz e purificação."],
        "pokemon": [
            "Crobat", "Gliscor", "Scolipede", "Seviper", "Zangoose", "Glimmora",
            "Malamar", "Skorupi", "Drapion", "Golbat", "Sneasler", "Absol", "Ursaluna (Bloodmoon)",
        ],
        "categorias_pokemon": {
            "🦇 Vampirismo / Hematofagia": ["Crobat", "Golbat", "Gliscor", "Sneasler"],
            "🌕 Sangue Lunar / Bloodmoon": ["Ursaluna (Bloodmoon)"],
            "🩸 Veneno / Toxinas / Ferocidade": ["Scolipede", "Skorupi", "Drapion", "Seviper"],
            "🗡️ Predadores / Instinto": ["Zangoose", "Absol", "Malamar", "Gliscor"],
            "💠 Cristais / Fluidos / Aspecto carmesim": ["Glimmora", "Scolipede", "Skorupi"],
        },
        "movimentos": ["Leech Life", "Bite", "Crunch", "Night Slash", "Cross Poison", "Poison Fang", "Blood Moon", "Drain Punch", "Giga Drain"],
        "habilidades": ["Vampire-like theme / Poison Heal / Poison Point / Merciless / Strong Jaw"],
        "semelhantes": ["Veneno", "Sombrio", "Luz", "Espírito"],
        "compatibilidade": "Classificação temática ligada à vitalidade, sangue, ferocidade e drenagem de energia — não implica que um Pokémon possua sangue com propriedades especiais.",
        "nota": "Sangue é um subtipo fanon e conceitual do KAYZAC; associações podem ser literais, visuais ou baseadas em movimentos e comportamento.",
    },
    "Cristal": {
        "emoji": "💎",
        "status": "Fanon / subtipo material e energético KAYZAC",
        "origem": "Representa Pokémon associados a cristais, gemas, prismas, cristalização e energia refratada.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo mineral / energético",
        "vantagens": ["Vantagem teórica contra materiais frágeis e energia mal estabilizada."],
        "desvantagens": ["Desvantagem teórica contra impacto bruto, pressão e calor extremo."],
        "pokemon": ["Diancie", "Carbink", "Glimmora", "Sableye", "Starmie", "Minior", "Cryogonal", "Regice", "Terapagos"],
        "categorias_pokemon": {
            "💎 Gemas / Diamantes": ["Diancie", "Carbink", "Sableye"],
            "🔮 Prismas / Refração / Cristalização": ["Starmie", "Glimmora", "Terapagos"],
            "☄️ Cristais vindos do espaço": ["Minior", "Terapagos"],
            "❄️ Cristais de gelo": ["Cryogonal", "Regice"],
        },
        "movimentos": ["Power Gem", "Diamond Storm", "Meteor Beam", "Tera Starstorm", "Mirror Shot", "Ice Beam"],
        "habilidades": ["Prism Armor", "Clear Body", "Light Metal", "Solid Rock"],
        "semelhantes": ["Mineral", "Estelar", "Luz", "Pedra"],
        "compatibilidade": "Classifica Pokémon cuja identidade visual ou mecânica gira em torno de cristais, gemas, superfícies prismáticas ou energia cristalina.",
        "nota": "Cristal é fanon KAYZAC e não substitui o tipo oficial de nenhum Pokémon.",
    },
    "Lua": {
        "emoji": "🌙",
        "status": "Fanon / subtipo astral KAYZAC",
        "origem": "Representa a Lua, luar, marés, ciclos noturnos, sonhos e criaturas associadas à noite lunar.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo astral / noturno",
        "vantagens": ["Vantagem teórica contra conceitos solares ou dependentes de exposição intensa à luz."],
        "desvantagens": ["Desvantagem teórica contra conceitos solares e luminosos."],
        "pokemon": ["Clefairy", "Clefable", "Lunatone", "Lunala", "Umbreon", "Cresselia", "Darkrai", "Espeon", "Noctowl"],
        "categorias_pokemon": {
            "🌕 Lua / Luar": ["Clefairy", "Clefable", "Lunatone", "Lunala"],
            "🌙 Noite / Eclipse / Sombra": ["Umbreon", "Darkrai", "Noctowl"],
            "💭 Sonhos sob o luar": ["Cresselia", "Clefairy", "Clefable"],
            "🌗 Dualidade Lunar / Solar": ["Espeon", "Umbreon"],
        },
        "movimentos": ["Moonblast", "Moonlight", "Lunar Dance", "Moongeist Beam", "Dream Eater", "Psychic", "Night Daze"],
        "habilidades": ["Lunar theme / Synchronize / Insomnia / Bad Dreams / Inner Focus"],
        "semelhantes": ["Cósmico", "Sol", "Sonhos", "Trevas", "Estelar"],
        "compatibilidade": "Une astronomia, noite, ciclos lunares e simbolismos de sonho, eclipse e luar.",
        "nota": "Lua é uma classificação temática KAYZAC; não é uma tipagem oficial.",
    },
    "Sol": {
        "emoji": "☀️",
        "status": "Fanon / subtipo solar KAYZAC",
        "origem": "Representa luz solar, calor, fotossíntese, dias ensolarados e energia proveniente do Sol.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo astral / térmico / luminoso",
        "vantagens": ["Vantagem teórica contra gelo, trevas e ambientes de baixa luminosidade."],
        "desvantagens": ["Desvantagem teórica contra conceitos lunares, aquáticos e de absorção de luz."],
        "pokemon": ["Solgaleo", "Sunkern", "Sunflora", "Cherrim", "Heliolisk", "Volcarona", "Espeon", "Bellossom", "Lilligant"],
        "categorias_pokemon": {
            "☀️ Energia Solar": ["Solgaleo", "Sunkern", "Sunflora", "Heliolisk"],
            "🌻 Fotossíntese / Plantas solares": ["Sunkern", "Sunflora", "Cherrim", "Bellossom", "Lilligant"],
            "🔥 Calor / Sol ardente": ["Volcarona", "Heliolisk", "Solgaleo"],
            "🌞 Brilho / Dia ensolarado": ["Espeon", "Cherrim", "Sunflora"],
        },
        "movimentos": ["Solar Beam", "Solar Blade", "Morning Sun", "Sunsteel Strike", "Flame Charge", "Sunny Day", "Weather Ball"],
        "habilidades": ["Drought", "Chlorophyll", "Solar Power", "Flower Gift", "Protosynthesis"],
        "semelhantes": ["Luz", "Lua", "Fogo", "Natureza", "Cósmico"],
        "compatibilidade": "Classificação para Pokémon ligados ao Sol por energia, estética, fotossíntese, calor ou mecânicas de clima.",
        "nota": "Sol é fanon KAYZAC; algumas habilidades e movimentos citados possuem relação oficial com Sunny Day e luz solar.",
    },
    "Tempo": {
        "emoji": "⏳",
        "status": "Fanon / subtipo temporal KAYZAC",
        "origem": "Representa tempo, relógios, passado, futuro, ciclos e manipulação temporal.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo temporal",
        "vantagens": ["Vantagem teórica contra conceitos dependentes de ciclos e previsibilidade."],
        "desvantagens": ["Desvantagem teórica contra espaço, caos e efeitos fora de causalidade comum."],
        "pokemon": ["Dialga", "Celebi", "Bronzong", "Slowking", "Slowbro", "Claydol", "Jirachi", "Porygon-Z"],
        "categorias_pokemon": {
            "⏰ Manipulação do tempo": ["Dialga", "Celebi"],
            "🕰️ Relógios / Ciclos / Engrenagens": ["Bronzong", "Porygon-Z"],
            "🐢 Percepção lenta / velocidade temporal": ["Slowbro", "Slowking"],
            "🌟 Tempo mítico / desejos / eras": ["Celebi", "Jirachi"],
        },
        "movimentos": ["Roar of Time", "Future Sight", "Time Warp", "Trick Room", "Protect", "Wish"],
        "habilidades": ["Regenerator", "Own Tempo", "Temporal theme"],
        "semelhantes": ["Espaço", "Cósmico", "Sonhos", "DNA"],
        "compatibilidade": "Classificação centrada em entidades, designs ou mecânicas associadas a passado, futuro, ciclos e distorções temporais.",
        "nota": "Nem todo Pokémon listado manipula tempo literalmente; a curadoria separa representação direta de afinidade temática.",
    },
    "DNA": {
        "emoji": "🧬",
        "status": "Fanon / subtipo genético KAYZAC",
        "origem": "Representa genética, mutação, clonagem, engenharia biológica, evolução artificial e alteração de organismo.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática baseada em ciência Pokémon",
        "natureza": "Subtipo biológico / genético",
        "vantagens": ["Vantagem teórica contra formas biológicas instáveis ou geneticamente manipuladas."],
        "desvantagens": ["Desvantagem teórica contra conceitos puramente artificiais ou energéticos."],
        "pokemon": ["Mew", "Mewtwo", "Deoxys", "Genesect", "Ditto", "Porygon", "Porygon2", "Porygon-Z", "Silvally", "Type: Null", "Zygarde"],
        "categorias_pokemon": {
            "🧬 Clonagem / Genes": ["Mew", "Mewtwo", "Ditto"],
            "☄️ Mutação / Origem extraterrestre": ["Deoxys", "Zygarde"],
            "🤖 Biotecnologia / Engenharia": ["Genesect", "Porygon", "Porygon2", "Porygon-Z"],
            "🔄 Alteração / Adaptação genética": ["Silvally", "Type: Null", "Zygarde"],
        },
        "movimentos": ["Transform", "Imposter", "Conversion", "Conversion 2", "Recover", "Multi-Attack"],
        "habilidades": ["Imposter", "Download", "Adaptability", "RKS System", "Power Construct"],
        "semelhantes": ["Cyber", "Plástico", "Espaço", "Tempo", "Cósmico"],
        "compatibilidade": "Classificação para Pokémon relacionados diretamente a genética, clonagem, mutação, adaptação ou engenharia biológica/artificial.",
        "nota": "DNA é fanon KAYZAC; a presença de um Pokémon nessa lista é uma classificação temática, não uma afirmação científica sobre sua biologia real.",
    },
    "Espaço": {
        "emoji": "🌀",
        "status": "Fanon / subtipo espacial KAYZAC",
        "origem": "Representa espaço, dimensões, portais, distorções espaciais, gravidade e seres do além do mundo conhecido.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo dimensional / espacial",
        "vantagens": ["Vantagem teórica contra efeitos puramente locais ou presos a uma única dimensão."],
        "desvantagens": ["Desvantagem teórica contra tempo e energia cósmica concentrada."],
        "pokemon": ["Palkia", "Giratina", "Deoxys", "Hoopa", "Elgyem", "Beheeyem", "Lunatone", "Solrock", "Cleffa", "Minior"],
        "categorias_pokemon": {
            "🌌 Dimensões / Distorsões": ["Palkia", "Giratina", "Hoopa"],
            "☄️ Visitantes do espaço": ["Deoxys", "Elgyem", "Beheeyem", "Minior"],
            "🪐 Corpos celestes": ["Lunatone", "Solrock", "Cleffa"],
            "🌀 Portais / Passagens": ["Hoopa", "Giratina"],
        },
        "movimentos": ["Spacial Rend", "Hyperspace Hole", "Hyperspace Fury", "Psycho Boost", "Teleport", "Gravity"],
        "habilidades": ["Prism Armor", "Levitate", "Pressure", "Telepathy", "Magician"],
        "semelhantes": ["Cósmico", "Tempo", "DNA", "Estelar", "Lua"],
        "compatibilidade": "Subtipo dedicado a dimensões, espaço sideral, portais, distorções e conceitos que transcendem um único lugar.",
        "nota": "Espaço é fanon KAYZAC, separado de Cósmico: aqui o foco é dimensão, distância, portais e estrutura espacial.",
    },
    "Radiação": {
        "emoji": "☢️",
        "status": "Fanon / subtipo energético-industrial KAYZAC",
        "origem": "Representa radiação, energia ionizante, contaminação, mutação e ambientes de alta energia.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo energético / científico",
        "vantagens": ["Vantagem teórica contra formas biológicas sensíveis a contaminação energética."],
        "desvantagens": ["Desvantagem teórica contra absorção, dissipação e contenção de energia."],
        "pokemon": ["Eternatus", "Electrode", "Voltorb", "Muk", "Grimer", "Weezing", "Koffing", "Garbodor", "Glimmora", "Magnezone", "Deoxys"],
        "categorias_pokemon": {
            "☢️ Energia extrema / radiação": ["Eternatus", "Deoxys", "Magnezone"],
            "💥 Instabilidade / explosão": ["Voltorb", "Electrode"],
            "☣️ Contaminação / resíduos": ["Grimer", "Muk", "Koffing", "Weezing", "Garbodor"],
            "💎 Cristais / energia concentrada": ["Glimmora", "Eternatus"],
        },
        "movimentos": ["Explosion", "Self-Destruct", "Sludge Bomb", "Gunk Shot", "Electro Ball", "Thunderbolt", "Eternabeam", "Psycho Boost"],
        "habilidades": ["Aftermath", "Levitate", "Neutralizing Gas", "Stench", "Pressure"],
        "semelhantes": ["Cyber", "Plástico", "DNA", "Cósmico", "Veneno"],
        "compatibilidade": "Classificação conceitual para radiação, energia intensa, resíduos contaminantes e mutações associadas à alta energia.",
        "nota": "Radiação é fanon KAYZAC; a classificação não afirma que qualquer Pokémon listado seja radioativo no sentido científico.",
    },
    "Realeza": {
        "emoji": "👑",
        "status": "Fanon / subtipo hierárquico KAYZAC",
        "origem": "Representa reis, rainhas, príncipes, nobres, monarcas, guardiões da coroa e símbolos de autoridade.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática",
        "natureza": "Subtipo social / simbólico",
        "vantagens": ["Vantagem teórica contra arquétipos de submissão ou desorganização."],
        "desvantagens": ["Desvantagem teórica contra rebelião, imprevisibilidade e força popular."],
        "pokemon": ["Nidoking", "Nidoqueen", "Slowking", "Kingambit", "Empoleon", "Pyroar", "Vespiquen", "Tsareena", "Corviknight", "Zacian", "Zamazenta"],
        "categorias_pokemon": {
            "👑 Reis / Rainhas": ["Nidoking", "Nidoqueen", "Slowking", "Kingambit", "Tsareena"],
            "🏰 Monarcas / Impérios": ["Empoleon", "Pyroar", "Vespiquen"],
            "⚔️ Cavaleiros / Guardiões": ["Corviknight", "Zacian", "Zamazenta"],
            "🦁 Símbolos de poder / majestade": ["Pyroar", "Nidoking", "Empoleon"],
        },
        "movimentos": ["King's Shield", "Iron Head", "Swords Dance", "Noble Roar", "Royal-themed moves"],
        "habilidades": ["Supreme Overlord", "Queenly Majesty", "Intimidate", "Competitive", "Pressure", "Defiant"],
        "semelhantes": ["Arma", "Samurai", "Aura", "Anime", "Luz"],
        "compatibilidade": "Classificação baseada em títulos, postura, design, estruturas sociais retratadas na Pokédex e simbolismos de autoridade.",
        "nota": "Realeza é fanon KAYZAC e não depende de o Pokémon literalmente governar uma região ou espécie.",
    },
    "Aura": {
        "emoji": "🌀",
        "status": "Fanon / subtipo energético KAYZAC",
        "origem": "Representa aura, energia vital, força interior, presença espiritual, vontade e poder de combate.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo energético / espiritual / marcial",
        "vantagens": ["Vantagem teórica contra medo, intimidação e ilusões quando a força de vontade prevalece."],
        "desvantagens": ["Desvantagem teórica contra drenagem, silêncio energético e efeitos de neutralização."],
        "pokemon": ["Lucario", "Riolu", "Mewtwo", "Medicham", "Gallade", "Gardevoir", "Espeon", "Alakazam", "Greninja", "Blaziken"],
        "categorias_pokemon": {
            "💙 Aura / Energia Vital": ["Lucario", "Riolu", "Mewtwo"],
            "🥋 Disciplina / Artes Marciais": ["Medicham", "Blaziken", "Lucario"],
            "🧠 Energia Mental / Psíquica": ["Gardevoir", "Alakazam", "Espeon"],
            "⚡ Presença / Poder Interior": ["Gallade", "Greninja", "Lucario"],
        },
        "movimentos": ["Aura Sphere", "Vacuum Wave", "Force Palm", "Close Combat", "Detect", "Calm Mind", "Psychic", "Psycho Cut"],
        "habilidades": ["Inner Focus", "Justified", "Steadfast", "Telepathy", "Synchronize", "Battle Bond"],
        "semelhantes": ["Anime", "Psíquico", "Lutador", "Espírito", "Luz"],
        "compatibilidade": "É o subtipo da energia interior no KAYZAC: vontade, disciplina, espírito de luta e presença. Lucario ocupa o papel de símbolo central da classificação.",
        "nota": "Aura é fanon como classificação, embora Aura exista oficialmente como conceito de lore e movimentos no universo Pokémon.",
    },
    "Ninjas": {
        "emoji": "🥷",
        "status": "Fanon / subtipo marcial KAYZAC",
        "origem": "Representa ninjas, furtividade, espionagem, mobilidade, técnicas secretas, shuriken e combate rápido.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo marcial / furtivo",
        "vantagens": ["Vantagem teórica contra alvos lentos ou despreparados."],
        "desvantagens": ["Desvantagem teórica contra rastreamento, controle de área e ataques que revelam a posição."],
        "pokemon": ["Greninja", "Ninjask", "Shedinja", "Accelgor", "Kecleon", "Scizor", "Zoroark", "Weavile", "Decidueye", "Sneasler"],
        "categorias_pokemon": {
            "🥷 Ninjas clássicos": ["Greninja", "Ninjask", "Accelgor"],
            "🗡️ Lâminas / Shuriken / Assalto": ["Scizor", "Weavile", "Decidueye"],
            "👤 Furtividade / Camuflagem": ["Kecleon", "Zoroark", "Shedinja"],
            "💨 Velocidade / Mobilidade": ["Ninjask", "Sneasler", "Greninja"],
        },
        "movimentos": ["Water Shuriken", "Shuriken", "Double Team", "Smokescreen", "U-turn", "Substitute", "Night Slash", "Aerial Ace"],
        "habilidades": ["Protean", "Battle Bond", "Speed Boost", "Technician", "Illusion", "Unburden"],
        "semelhantes": ["Samurais", "Anime", "Arma", "Vento", "Aura"],
        "compatibilidade": "Especialização em furtividade, velocidade, lâminas, camuflagem e técnicas rápidas de combate.",
        "nota": "Ninjas é um subtipo autoral distinto do Anime: aqui o foco é o arquétipo marcial ninja, não a nostalgia de mídia.",
    },
    "Samurais": {
        "emoji": "🗡️",
        "status": "Fanon / subtipo guerreiro KAYZAC",
        "origem": "Representa samurais, bushidō, katana, armaduras, duelistas e guerreiros de disciplina tradicional.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo marcial / guerreiro",
        "vantagens": ["Vantagem teórica em duelos e confrontos diretos."],
        "desvantagens": ["Desvantagem teórica contra mobilidade extrema, ataques furtivos e combate à distância."],
        "pokemon": ["Samurott", "Samurott de Hisui", "Aegislash", "Gallade", "Bisharp", "Kingambit", "Scizor", "Sirfetch’d", "Kartana", "Kleavor"],
        "categorias_pokemon": {
            "🗡️ Katana / Espadachins": ["Samurott", "Samurott de Hisui", "Gallade", "Sirfetch’d"],
            "⚔️ Armadura / Clãs / Guerra": ["Aegislash", "Bisharp", "Kingambit", "Kleavor"],
            "🎯 Precisão / Corte": ["Kartana", "Scizor", "Gallade"],
            "👑 Daimyō / Senhor da guerra": ["Kingambit", "Bisharp", "Samurott de Hisui"],
        },
        "movimentos": ["Sacred Sword", "Night Slash", "Swords Dance", "Psycho Cut", "Leaf Blade", "Ceaseless Edge", "Kowtow Cleave", "Fury Cutter"],
        "habilidades": ["Sharpness", "Defiant", "Supreme Overlord", "Technician", "Stance Change"],
        "semelhantes": ["Ninjas", "Arma", "Anime", "Realeza", "Aura"],
        "compatibilidade": "Subtipo para guerreiros de lâmina, armadura, disciplina, duelo e estética de samurai.",
        "nota": "Samurais é fanon KAYZAC; o critério é arquétipo visual, cultural e de combate.",
    },
    "Sonhos": {
        "emoji": "💭",
        "status": "Fanon / subtipo onírico KAYZAC",
        "origem": "Representa sonhos, pesadelos, sono, imaginação, subconsciente e mundos mentais.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo mental / onírico",
        "vantagens": ["Vantagem teórica contra consciência vulnerável e efeitos baseados em vigília."],
        "desvantagens": ["Desvantagem teórica contra disciplina mental, despertares e energia luminosa."],
        "pokemon": ["Darkrai", "Cresselia", "Musharna", "Munna", "Hypno", "Jigglypuff", "Komala", "Drowzee", "Lunala", "Clefairy"],
        "categorias_pokemon": {
            "🌙 Sonhos positivos / proteção": ["Cresselia", "Munna", "Musharna", "Clefairy"],
            "🌑 Pesadelos": ["Darkrai", "Hypno", "Drowzee"],
            "😴 Sono / Sonolência": ["Komala", "Jigglypuff", "Hypno"],
            "🌌 Sonhos cósmicos": ["Lunala", "Cresselia", "Darkrai"],
        },
        "movimentos": ["Dream Eater", "Hypnosis", "Sing", "Sleep Powder", "Rest", "Yawn", "Lunar Dance", "Psychic"],
        "habilidades": ["Bad Dreams", "Forewarn", "Insomnia", "Comatose", "Synchronize"],
        "semelhantes": ["Lua", "Psíquico", "Anime", "Aura", "Espírito"],
        "compatibilidade": "Classificação centrada no mundo dos sonhos, sono, pesadelos e efeitos psicológicos associados ao subconsciente.",
        "nota": "Sonhos é fanon KAYZAC, embora sonhos e sono sejam elementos oficiais recorrentes na franquia.",
    },
    "Sorte": {
        "emoji": "🍀",
        "status": "Fanon / subtipo de fortuna KAYZAC",
        "origem": "Representa sorte, azar, coincidência favorável, fortuna, probabilidades e acontecimentos improváveis.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática",
        "natureza": "Subtipo abstrato / probabilidade",
        "vantagens": ["Vantagem teórica em situações de alta variância e golpes de chance."],
        "desvantagens": ["Desvantagem teórica contra planejamento, consistência e controle absoluto."],
        "pokemon": ["Chansey", "Blissey", "Jirachi", "Togepi", "Togetic", "Togekiss", "Meowth", "Persian", "Delibird", "Absol", "Sableye"],
        "categorias_pokemon": {
            "🍀 Sorte / Fortuna": ["Chansey", "Blissey", "Togepi", "Togekiss"],
            "🌟 Desejos / Estrelas": ["Jirachi", "Togepi", "Togetic"],
            "💰 Sorte / Riqueza": ["Meowth", "Persian", "Sableye"],
            "🎲 Azar / Destino imprevisível": ["Delibird", "Absol", "Sableye"],
        },
        "movimentos": ["Lucky Chant", "Metronome", "Serene Grace theme", "Present", "Bestow", "Wish"],
        "habilidades": ["Serene Grace", "Super Luck", "Lucky Egg theme", "Friend Guard", "Natural Cure"],
        "semelhantes": ["Estelar", "Sonhos", "Aura", "Realeza"],
        "compatibilidade": "Subtipo abstrato para Pokémon associados a sorte, desejos, fortuna, coincidência, prosperidade ou imprevisibilidade.",
        "nota": "Sorte é uma classificação conceitual do KAYZAC, não uma força elemental oficial.",
    },
    "Comida": {
        "emoji": "🍔",
        "status": "Fanon / subtipo gastronômico KAYZAC",
        "origem": "Representa alimentos, frutas, ingredientes, confeitaria, guloseimas, cozinha e Pokémon associados à alimentação.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta temática",
        "natureza": "Subtipo gastronômico / cotidiano",
        "vantagens": ["Vantagem teórica contra conceitos de consumo, fome e desgaste prolongado."],
        "desvantagens": ["Desvantagem teórica contra fogo, veneno e contaminação de alimentos."],
        "pokemon": ["Vanilluxe", "Alcremie", "Slurpuff", "Appletun", "Applin", "Tropius", "Cherubi", "Cherrim", "Ogerpon", "Polteageist", "Sinistea", "Miltank", "Skwovet", "Greedent", "Appletun"],
        "categorias_pokemon": {
            "🍰 Doces / Confeitaria": ["Alcremie", "Slurpuff", "Vanilluxe"],
            "🍎 Frutas / Plantações": ["Applin", "Appletun", "Cherubi", "Cherrim", "Tropius"],
            "🥛 Leite / Ingredientes": ["Miltank", "Tropius"],
            "☕ Bebidas / Preparações": ["Polteageist", "Sinistea"],
            "🥜 Fome / Armazenamento de comida": ["Skwovet", "Greedent"],
            "🍃 Alimento / Natureza regional": ["Ogerpon", "Appletun", "Tropius"],
        },
        "movimentos": ["Stuff Cheeks", "Swallow", "Stockpile", "Recycle", "Belch", "Teatime", "Sweet Kiss", "Apple Acid"],
        "habilidades": ["Gluttony", "Cheek Pouch", "Harvest", "Sweet Veil", "Thick Fat"],
        "semelhantes": ["Madeira", "Natureza", "Plástico", "Sorte"],
        "compatibilidade": "Classificação divertida e cotidiana para Pokémon ligados a alimentos, frutas, doces, bebidas ou comportamentos alimentares.",
        "nota": "Comida é fanon KAYZAC e privilegia design, lore e mecânicas sobre uma definição literal de dieta.",
    },
    "Garras e Dentes": {
        "emoji": "🦷",
        "status": "Fanon / subtipo predatório KAYZAC",
        "origem": "Representa feras, presas, garras, mordidas, caça, instinto e combate corpo a corpo baseado em anatomia natural.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática",
        "natureza": "Subtipo bestial / predatório",
        "vantagens": ["Vantagem teórica contra alvos expostos ao combate próximo e à pressão física."],
        "desvantagens": ["Desvantagem teórica contra armaduras, escudos e combate de longo alcance."],
        "pokemon": ["Luxray", "Zangoose", "Seviper", "Weavile", "Sneasler", "Krookodile", "Lycanroc", "Persian", "Arcanine", "Haxorus", "Druddigon", "Tyranitar", "Garchomp", "Granbull"],
        "categorias_pokemon": {
            "🦷 Presas / Mordidas": ["Krookodile", "Tyranitar", "Garchomp", "Persian", "Granbull"],
            "🐾 Garras / Predadores": ["Luxray", "Weavile", "Sneasler", "Zangoose"],
            "🐍 Presas / Répteis": ["Seviper", "Krookodile", "Haxorus", "Druddigon"],
            "🐺 Lobos / Feras": ["Lycanroc", "Arcanine", "Luxray"],
            "🦖 Monstros / Predadores pesados": ["Tyranitar", "Garchomp", "Haxorus", "Druddigon"],
        },
        "movimentos": ["Bite", "Crunch", "Jaw Lock", "Hyper Fang", "Fire Fang", "Ice Fang", "Thunder Fang", "Slash", "Night Slash", "Fury Swipes", "Metal Claw"],
        "habilidades": ["Strong Jaw", "Tough Claws", "Sharpness", "Intimidate", "Guts", "Rivalry"],
        "semelhantes": ["Arma", "Sangue", "Ninjas", "Samurais", "Anime"],
        "compatibilidade": "Uma classificação bestial focada na anatomia de predadores: garras, presas, mordidas, caça e força corporal.",
        "nota": "Garras e Dentes é fanon KAYZAC. A classificação valoriza a anatomia e os movimentos associados a mordidas e cortes.",
    },
    "Animal": {
        "emoji": "🐾",
        "status": "Fanon / subtipo zoológico KAYZAC",
        "origem": (
            "Representa Pokémon baseados em animais reais ou arquétipos zoológicos — mamíferos, aves, répteis, "
            "anfíbios, peixes, insetos, aracnídeos e outras formas de vida animal."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática",
        "natureza": "Subtipo zoológico / fauna",
        "vantagens": [
            "Vantagem teórica contra conceitos artificiais quando a naturalidade e os instintos são centrais.",
            "Pode representar caça, sobrevivência, sentidos aguçados, mobilidade e adaptação física.",
        ],
        "desvantagens": [
            "Desvantagem teórica contra máquinas, armaduras e mecanismos artificiais especializados.",
        ],
        "pokemon": [
            "Pikachu", "Eevee", "Arcanine", "Luxray", "Lycanroc", "Lopunny", "Ursaring",
            "Pyroar", "Serperior", "Talonflame", "Corviknight", "Gyarados", "Milotic",
            "Meowth", "Persian", "Persian de Alola", "Skitty", "Delcatty", "Purrloin", "Liepard",
            "Glameow", "Purugly", "Espurr", "Meowstic", "Litten", "Torracat", "Incineroar",
            "Sprigatito", "Floragato", "Meowscarada", "Zeraora",
            "Frogadier", "Greninja", "Butterfree", "Beedrill", "Scolipede", "Tyrantrum",
            "Aurorus", "Great Tusk", "Sneasler", "Ursaluna", "Cyclizar", "Koraidon",
        ],
        "categorias_pokemon": {
            "🐺 Mamíferos / Feras": ["Eevee", "Arcanine", "Luxray", "Lycanroc", "Lopunny", "Ursaring", "Pyroar"],
            "🐈 Gatos / Felinos": ["Meowth", "Persian", "Persian de Alola", "Skitty", "Delcatty", "Purrloin", "Liepard", "Glameow", "Purugly", "Espurr", "Meowstic", "Litten", "Torracat", "Incineroar", "Sprigatito", "Floragato", "Meowscarada", "Zeraora"],
            "🦅 Aves / Predadores aéreos": ["Talonflame", "Corviknight", "Pidgeot", "Staraptor", "Braviary"],
            "🐍 Répteis / Serpentes / Lagartos": ["Serperior", "Arbok", "Sandaconda", "Koraidon", "Cyclizar"],
            "🐟 Aquáticos / Peixes": ["Gyarados", "Milotic", "Sharpedo", "Whiscash", "Barraskewda"],
            "🐸 Anfíbios": ["Froakie", "Frogadier", "Greninja", "Politoed", "Seismitoad"],
            "🪲 Insetos / Aracnídeos": ["Butterfree", "Beedrill", "Scolipede", "Ariados", "Galvantula"],
            "🦖 Pré-históricos": ["Tyrantrum", "Aurorus", "Rampardos", "Bastiodon", "Great Tusk"],
        },
        "movimentos": ["Bite", "Crunch", "Scratch", "Slash", "Horn Attack", "Peck", "Wing Attack", "Fury Swipes", "Take Down"],
        "habilidades": ["Keen Eye", "Strong Jaw", "Intimidate", "Adaptability", "Natural Cure", "Predator theme"],
        "semelhantes": ["Garras e Dentes", "Vento", "Sangue", "Natureza", "Humanoide"],
        "compatibilidade": "Classificação ampla para Pokémon cuja inspiração zoológica é um componente marcante do design ou da biologia retratada.",
        "nota": "Animal é fanon KAYZAC. A classificação é temática e não tenta reproduzir integralmente a árvore zoológica da vida real.",
    },
    "Humanoide": {
        "emoji": "🧍",
        "status": "Fanon / subtipo antropomórfico KAYZAC",
        "origem": "Representa Pokémon com anatomia bípede, proporções humanoides, gestos humanos, profissões, vestimentas ou arquétipos sociais reconhecíveis.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação antropomórfica",
        "natureza": "Subtipo antropomórfico / social",
        "vantagens": ["Vantagem teórica em interações baseadas em técnica, ferramenta, linguagem corporal ou cultura."],
        "desvantagens": ["Desvantagem teórica contra formas totalmente bestiais, gigantescas ou essencialmente não antropomórficas."],
        "pokemon": [
            "Machamp", "Machoke", "Hitmonlee", "Hitmonchan", "Hitmontop", "Lucario", "Gardevoir", "Gallade",
            "Mr. Mime", "Mr. Rime", "Jynx", "Medicham", "Alakazam", "Grimmsnarl", "Incineroar", "Cinderace",
            "Meowscarada", "Delphox", "Sneasler", "Iron Valiant", "Conkeldurr", "Annihilape", "Toxtricity",
        ],
        "categorias_pokemon": {
            "🥋 Lutadores / Artistas marciais": ["Machamp", "Machoke", "Hitmonlee", "Hitmonchan", "Hitmontop", "Medicham", "Lucario"],
            "🧙 Psíquicos / Magos / Feiticeiros": ["Alakazam", "Gardevoir", "Gallade", "Delphox", "Jynx"],
            "🎭 Performers / Expressão humana": ["Mr. Mime", "Mr. Rime", "Jynx", "Cinderace", "Meowscarada"],
            "⚔️ Guerreiros / Combatentes": ["Lucario", "Gallade", "Sneasler", "Iron Valiant", "Incineroar"],
            "👹 Criaturas humanoides monstruosas": ["Grimmsnarl", "Annihilape", "Conkeldurr", "Toxtricity"],
        },
        "movimentos": ["Close Combat", "Aura Sphere", "Psychic", "Calm Mind", "Swords Dance", "Mach Punch", "Bulk Up"],
        "habilidades": ["Inner Focus", "Justified", "Steadfast", "Sharpness", "Iron Fist", "Limber"],
        "semelhantes": ["Anime", "Aura", "Samurais", "Ninjas", "Garras e Dentes"],
        "compatibilidade": "Foca no quanto o Pokémon se aproxima de uma silhueta, comportamento ou arquétipo humanoide, incluindo lutadores, artistas, magos e personagens sociais.",
        "nota": "Humanoide é fanon KAYZAC e não afirma que esses Pokémon sejam humanos ou tenham origem humana.",
    },
    "+18": {
        "emoji": "🔞",
        "status": "Fanon / classificação temática madura KAYZAC",
        "origem": (
            "Representa temas adultos e vícios humanos vistos de forma simbólica: sexualidade adulta e sedução, "
            "álcool e intoxicação, drogas e toxinas, violência, morte, obsessão, crime, vício e outros tabus."
        ),
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / leitura simbólica de temas maduros",
        "natureza": "Subtipo adulto / vícios / tabus",
        "vantagens": [
            "Classificação temática para Pokémon associados a excessos, perigos, compulsões, transgressões ou temas sombrios da vida adulta.",
        ],
        "desvantagens": [
            "Não possui relações oficiais de tipo; seu objetivo é apenas curatorial e narrativo.",
        ],
        "pokemon": [
            "Salazzle", "Jynx", "Lopunny", "Tsareena", "Meowscarada", "Milotic", "Delcatty", "Liepard",
            "Gothitelle", "Gardevoir", "Oricorio", "Primarina", "Roserade", "Meowstic", "Obstagoon", "Koffing", "Weezing",
            "Muk", "Garbodor", "Toxtricity", "Swalot", "Malamar", "Houndoom", "Absol", "Sneasler",
            "Scizor", "Banette", "Chandelure", "Houndstone", "Spiritomb", "Drifblim",
            "Gorebyss", "Cursola", "Cofagrigus", "Runerigus", "Yamask", "Basculegion",
            "Froslass", "Shedinja", "Dhelmise", "Gholdengo", "Meowth",
        ],
        "categorias_pokemon": {
            "💋 Sedução / Charme / Sexualidade adulta": ["Jynx", "Salazzle", "Lopunny", "Tsareena", "Meowscarada", "Milotic", "Delcatty", "Liepard", "Gothitelle", "Gardevoir", "Oricorio", "Primarina", "Roserade", "Meowstic"],
            "🍷 Álcool / Intoxicação / Excesso": ["Polteageist", "Sinistea", "Drampa", "Swalot", "Toxtricity"],
            "💊 Drogas / Toxinas / Dependência": ["Koffing", "Weezing", "Muk", "Garbodor", "Toxapex", "Salazzle"],
            "🔪 Violência / Agressão / Caça": ["Houndoom", "Sneasler", "Scizor", "Obstagoon", "Absol"],
            "💀 Morte / Luto / Mortalidade": [
                "Banette", "Chandelure", "Houndstone", "Spiritomb", "Drifblim",
                "Gorebyss", "Cursola", "Cofagrigus", "Runerigus", "Yamask",
                "Basculegion", "Froslass", "Shedinja", "Dhelmise", "Gengar",
            ],
            "🎭 Obsessão / Crime / Vícios": ["Malamar", "Gholdengo", "Meowth", "Obstagoon", "Toxtricity"],
        },
        "movimentos": ["Toxic", "Sludge Wave", "Gunk Shot", "Night Slash", "Knock Off", "Thief", "Payback", "Hex", "Destiny Bond"],
        "habilidades": ["Poison Touch", "Toxic Debris", "Corrosion", "Merciless", "Intimidate", "Stench", "Strong Jaw"],
        "semelhantes": ["Sangue", "Radiação", "Plástico", "Trevas", "Espírito", "Garras e Dentes"],
        "compatibilidade": "Subtipo de leitura simbólica e madura: os Pokémon não são definidos moralmente por isso; representam apenas temas adultos, vícios, perigos ou tabus presentes na ficção. A parte de sexualidade adulta é tratada em termos de charme, sedução, romance e arquétipos de atração, sem conteúdo sexual explícito.",
        "nota": "+18 é uma classificação fanon KAYZAC. A Biblioteca evita conteúdo sexual explícito; o foco é simbolismo, narrativa, vícios, violência e temas adultos.",
    },
    "Brinquedos": {
        "emoji": "🧸",
        "status": "Fanon / subtipo infantil e lúdico KAYZAC",
        "origem": "Representa brinquedos, bonecos, marionetes, objetos de infância, miniaturas, jogos e Pokémon cujo design evoca diversão ou colecionismo.",
        "quando": "Subtipo autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / classificação temática infantil",
        "natureza": "Subtipo lúdico / infantil / objetos",
        "vantagens": ["Vantagem teórica contra conceitos ligados a medo infantil, rigidez ou ambientes excessivamente austeros."],
        "desvantagens": ["Desvantagem teórica contra conceitos de destruição industrial, desgaste ou corrosão."],
        "pokemon": [
            "Mime Jr.", "Mr. Mime", "Mr. Rime", "Banette", "Mimikyu", "Baltoy", "Claydol", "Falinks",
            "Tinkaton", "Tinkatuff", "Tinkatink", "Stufful", "Bewear", "Chingling", "Klefki", "Togepi",
            "Cleffa", "Igglybuff", "Pawmi", "Pawmo",
        ],
        "categorias_pokemon": {
            "🪆 Bonecos / Marionetes / Máscaras": ["Banette", "Mimikyu", "Mr. Mime", "Mr. Rime", "Mime Jr."],
            "🧸 Pelúcias / Brinquedos fofos": ["Stufful", "Bewear", "Togepi", "Cleffa", "Igglybuff"],
            "🤖 Brinquedos mecânicos / Miniaturas": ["Baltoy", "Claydol", "Falinks", "Tinkatink", "Tinkatuff", "Tinkaton"],
            "🔔 Objetos lúdicos / Colecionáveis": ["Klefki", "Chingling", "Pawmi", "Pawmo"],
        },
        "movimentos": ["Play Rough", "Toys / Playful theme", "Encore", "Copycat", "Metronome", "Trick", "Mimic"],
        "habilidades": ["Prankster", "Cursed Body", "Mimicry theme", "Pickup", "Klutz"],
        "semelhantes": ["Anime", "Humanoide", "Plástico", "Cyber", "Sonhos", "Comida"],
        "compatibilidade": "Classificação nostálgica para Pokémon que parecem brinquedos, bonecos, objetos de infância ou companheiros de brincadeira.",
        "nota": "Brinquedos é fanon KAYZAC; a classificação valoriza silhueta, função lúdica, nostalgia e associação cultural.",
    },
    "Anime": {
        "emoji": "🎬",
        "status": "Fanon / classificação especial KAYZAC",
        "origem": (
            "Não existe um Tipo Anime oficial. No KAYZAC, Anime representa Pokémon que "
            "evocam a estética, os arquétipos, a linguagem visual e a energia emocional dos "
            "animes que marcaram gerações — com foco especial no espírito shōnen de treino, "
            "amizade, rivalidade, superação, transformações e batalhas decisivas."
        ),
        "quando": "Classificação autoral KAYZAC — sem data oficial externa.",
        "quem": "KAYZAC / proposta autoral baseada na nostalgia dos animes e no arquétipo shōnen",
        "natureza": "Classificação de mídia / nostalgia / arquétipo shōnen",
        "vantagens": [
            "Vantagem teórica contra estilos passivos: representa pressão, iniciativa, treino e evolução em batalha.",
            "Vantagem teórica contra arquétipos que dependem de intimidação ou previsibilidade.",
        ],
        "desvantagens": [
            "Sem tabela oficial; as interações são definidas pelo sistema KAYZAC.",
            "A classificação é temática: uma associação não significa que o Pokémon seja uma referência oficial a determinado anime.",
        ],
        "pokemon": [
            "Pikachu", "Lucario", "Infernape", "Greninja", "Charizard", "Sceptile",
            "Blaziken", "Garchomp", "Gengar", "Zoroark", "Gallade", "Samurott",
            "Ceruledge", "Scizor", "Tyranitar", "Dragonite", "Metagross", "Haxorus",
            "Lycanroc (Dusk Form)", "Cinderace", "Decidueye", "Mewtwo", "Gardevoir", "Weavile",
            "Krookodile", "Absol", "Kommo-o", "Hydreigon", "Toxtricity",
        ],
        "categorias_pokemon": {
            "🥊 Protagonistas Shōnen / Heróis de Batalha": [
                "Pikachu", "Lucario", "Infernape", "Greninja", "Charizard",
                "Sceptile", "Blaziken", "Garchomp", "Cinderace", "Samurott",
            ],
            "🔥 Treino / Superação / Espírito de Luta": [
                "Riolu", "Lucario", "Chimchar", "Infernape", "Treecko", "Sceptile",
                "Torchic", "Blaziken", "Froakie", "Greninja", "Rockruff", "Lycanroc (Dusk Form)",
            ],
            "🥷 Ninjas / Agilidade / Técnicas Secretas": [
                "Greninja", "Ninjask", "Shedinja", "Kecleon", "Accelgor",
                "Scizor", "Zoroark", "Decidueye", "Weavile",
            ],
            "⚔️ Espadachins / Duelistas / Rivais": [
                "Gallade", "Aegislash", "Samurott", "Samurott de Hisui", "Ceruledge",
                "Scizor", "Bisharp", "Kingambit", "Sirfetch’d", "Kartana",
            ],
            "🌀 Aura / Energia / Poder Interior": [
                "Lucario", "Riolu", "Mewtwo", "Gardevoir", "Gallade", "Espeon",
                "Alakazam", "Medicham", "Greninja", "Necrozma",
            ],
            "👑 Dragões / Reis / Monstros de Poder": [
                "Charizard", "Dragonite", "Salamence", "Garchomp", "Metagross",
                "Tyranitar", "Haxorus", "Hydreigon", "Kommo-o", "Goodra",
            ],
            "👺 Rivais / Anti-heróis / Presenças sombrias": [
                "Gengar", "Zoroark", "Weavile", "Absol", "Houndoom", "Krookodile",
                "Drapion", "Scrafty", "Bisharp", "Hydreigon",
            ],
            "⚡ Transformações / Power-ups / Formas icônicas": [
                "Pikachu", "Charizard", "Lucario", "Greninja", "Gardevoir",
                "Gengar", "Mewtwo", "Toxtricity", "Lycanroc (Dusk Form)", "Cinderace",
            ],
            "🌟 Nostalgia Pokémon / Aventuras que atravessaram gerações": [
                "Pikachu", "Charizard", "Blastoise", "Venusaur", "Eevee", "Gengar",
                "Dragonite", "Lucario", "Greninja", "Sceptile", "Infernape", "Garchomp",
            ],
        },
        "referencias_nostalgia": {
            "🐉 Dragon Ball / Torneios / Evolução de Poder": [
                "Lucario", "Infernape", "Blaziken", "Machamp", "Garchomp", "Mewtwo",
            ],
            "🍥 Naruto / Ninjas / Clãs / Técnicas": [
                "Greninja", "Accelgor", "Ninjask", "Scizor", "Zoroark", "Decidueye",
            ],
            "⚔️ Bleach / Espadachins / Transformações": [
                "Aegislash", "Gallade", "Ceruledge", "Samurott", "Bisharp", "Scizor",
            ],
            "☠️ One Piece / Aventura / Tripulação / Rivalidade": [
                "Pikachu", "Lucario", "Infernape", "Gengar", "Garchomp", "Krookodile",
            ],
            "👹 Yu Yu Hakusho / Energia Espiritual / Demônios": [
                "Lucario", "Mewtwo", "Gengar", "Zoroark", "Absol", "Gallade",
            ],
            "🥋 Clássicos de luta / Torneios / Artes marciais": [
                "Hitmonlee", "Hitmonchan", "Hitmontop", "Lucario", "Blaziken", "Medicham",
            ],
            "🤖 Digimon / Criaturas parceiras / Evolução": [
                "Pikachu", "Charizard", "Lucario", "Garchomp", "Metagross", "Tyranitar",
            ],
            "🎡 Yu-Gi-Oh! / Rivalidade / Monstros emblemáticos": [
                "Mewtwo", "Gengar", "Garchomp", "Charizard", "Tyranitar", "Hydreigon",
            ],
            "⚙️ Beyblade / Medabots / Batalhas de arena": [
                "Metagross", "Scizor", "Klinklang", "Aggron", "Tinkaton", "Lucario",
            ],
        },
        "movimentos": [
            "Aura Sphere", "Close Combat", "Bullet Punch", "Mach Punch", "Vacuum Wave",
            "Thunderbolt", "Thunder Punch", "Flamethrower", "Flare Blitz", "Blast Burn",
            "Water Shuriken", "Leaf Blade", "Dragon Claw", "Dragon Rush", "Psychic",
            "Psycho Cut", "Sacred Sword", "Night Slash", "Dark Pulse", "Shadow Ball",
            "Extreme Speed", "Quick Attack", "Double Team", "Substitute", "Protect",
            "Detect", "Focus Blast", "Meteor Mash", "Overheat", "Behemoth Blade",
        ],
        "habilidades": [
            "Battle Bond", "Inner Focus", "Steadfast", "Blaze", "Torrent", "Overgrow",
            "Static", "Intimidate", "Justified", "Sharpness", "Unburden", "Libero",
            "Protean", "Iron Fist", "Technician", "Pressure",
        ],
        "semelhantes": ["Lutador", "Psíquico", "Fogo", "Dragão", "Sombrio", "Estelar"],
        "compatibilidade": (
            "Serve como uma cápsula de nostalgia dentro do KAYZAC: o Pokémon é associado a "
            "arquétipos de anime — protagonista, rival, mestre, anti-herói, espadachim, ninja, "
            "monstro de poder ou parceiro de aventura — sem afirmar que o design tenha sido "
            "oficialmente inspirado por uma obra específica. No caso de Lycanroc, o representante escolhido é o Dusk Form associado ao Ash; a forma é usada como referência temática de protagonista, rivalidade e superação. O coração da classificação é o espírito shōnen: "
            "treinar, cair, levantar, superar limites e proteger quem importa."
        ),
        "nota": (
            "Anime é uma classificação especial do KAYZAC, não uma tipagem oficial. As referências a "
            "Dragon Ball, Naruto, Bleach, One Piece, Yu Yu Hakusho, Digimon, Yu-Gi-Oh!, Beyblade, "
            "Medabots e outros clássicos são associações de nostalgia e arquétipo feitas pelo projeto; "
            "não representam confirmação oficial de inspiração dos designs dos Pokémon."
        ),
    },
}

# ============================================================
# 🎨 ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .library-hero {
        padding: 28px;
        border: 1px solid rgba(128,128,128,.35);
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(35,45,65,.72), rgba(18,20,28,.52));
        margin-bottom: 22px;
    }

    .library-card {
        border: 1px solid rgba(128,128,128,.30);
        border-radius: 16px;
        padding: 18px;
        background: rgba(20,22,30,.48);
        margin-bottom: 14px;
    }

    .library-title {
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .library-subtitle {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .tag {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 999px;
        border: 1px solid rgba(128,128,128,.28);
        font-size: 13px;
    }

    .stat-box {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 14px;
        padding: 14px;
        min-height: 94px;
        background: rgba(20,22,30,.40);
    }

    .small-muted {
        color: #9ca3af;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 🛠️ UTILITÁRIOS
# ============================================================


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def bonito_nome(nome: str) -> str:
    texto = str(nome or "").replace("-", " ")
    texto = re.sub(r"\bmc\b", "MC", texto, flags=re.I)
    return " ".join(parte.capitalize() for parte in texto.split())


def escolher_idioma(entradas: list[dict[str, Any]] | None, campo: str = "name") -> str | None:
    entradas = entradas or []
    for idioma in LANGS:
        for entrada in entradas:
            lang = entrada.get("language", {}).get("name")
            if lang == idioma and entrada.get(campo):
                return str(entrada[campo])
    return None


def limpar_texto(texto: str | None) -> str:
    if not texto:
        return ""
    return re.sub(r"\s+", " ", str(texto).replace("\n", " ").replace("\\n", " ")).strip()


def nome_tipo(nome: str) -> str:
    mapa = {
        "normal": "Normal",
        "fire": "Fogo",
        "water": "Água",
        "electric": "Elétrico",
        "grass": "Grama",
        "ice": "Gelo",
        "fighting": "Lutador",
        "poison": "Veneno",
        "ground": "Terrestre",
        "flying": "Voador",
        "psychic": "Psíquico",
        "bug": "Inseto",
        "rock": "Pedra",
        "ghost": "Fantasma",
        "dragon": "Dragão",
        "dark": "Sombrio",
        "steel": "Aço",
        "fairy": "Fada",
        "stellar": "Estelar",
        "unknown": "???",
        "shadow": "Shadow",
    }
    return mapa.get(str(nome).lower(), bonito_nome(nome))


def classe_movimento(nome: str) -> str:
    mapa = {"physical": "Físico", "special": "Especial", "status": "Status"}
    return mapa.get(str(nome).lower(), bonito_nome(nome))


def geracao_nome(nome: str) -> str:
    mapa = {
        "generation-i": "Geração I",
        "generation-ii": "Geração II",
        "generation-iii": "Geração III",
        "generation-iv": "Geração IV",
        "generation-v": "Geração V",
        "generation-vi": "Geração VI",
        "generation-vii": "Geração VII",
        "generation-viii": "Geração VIII",
        "generation-ix": "Geração IX",
    }
    return mapa.get(str(nome), bonito_nome(nome))


def categoria_item_nome(nome: str) -> str:
    mapa = {
        "standard-balls": "Poké Balls",
        "special-balls": "Poké Balls especiais",
        "medicine": "Medicinas",
        "status-cures": "Curas de status",
        "vitamins": "Vitaminas",
        "stat-boosts": "Boosts de atributos",
        "healing": "Recuperação",
        "pp-recovery": "Recuperação de PP",
        "revival": "Reviver",
        "held-items": "Itens seguráveis",
        "choice": "Choice Items",
        "bad-held-items": "Itens especiais seguráveis",
        "evolution": "Evolução",
        "spelunking": "Exploração",
        "collectibles": "Colecionáveis",
        "plot-advancement": "História",
        "event-items": "Eventos",
        "gameplay": "Gameplay",
        "loot": "Recompensas",
        "all-mail": "Mail",
        "flutes": "Flautas",
        "miracle-shooter": "Miracle Shooter",
        "type-enhancement": "Potencializadores de tipo",
        "mega-stones": "Mega Stones",
        "memories": "Memories",
        "z-crystals": "Z-Crystals",
        "dynamax-crystals": "Dynamax Crystals",
        "species-specific": "Específicos de espécie",
        "tera-shards": "Tera Shards",
        "tm-materials": "Materiais de TM",
    }
    return mapa.get(str(nome).lower(), bonito_nome(nome))


@st.cache_data(ttl=86400, show_spinner=False)
def api_get(url_or_endpoint: str) -> dict[str, Any] | None:
    url = url_or_endpoint
    if not url.startswith("http"):
        url = f"{BASE_URL}/{url.lstrip('/')}"
    try:
        resposta = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "KAYZAC-Master-Pokemon/2.0"},
        )
        resposta.raise_for_status()
        return resposta.json()
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def listar_recursos(endpoint: str, limite: int = 1000) -> list[dict[str, str]]:
    dados = api_get(f"{endpoint}?limit={limite}&offset=0")
    if not dados:
        return []
    return dados.get("results", []) or []


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_recurso(endpoint: str, nome_ou_id: str) -> dict[str, Any] | None:
    return api_get(f"{endpoint}/{nome_ou_id}")


def extrair_id_pokemon(url: str) -> int | None:
    """Extrai o ID numérico de uma URL de recurso Pokémon da PokéAPI."""
    numeros = re.findall(r"/([0-9]+)/?$", str(url or ""))
    if not numeros:
        return None
    try:
        return int(numeros[-1])
    except ValueError:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def dados_mini_dex_pokemon(nome: str, url: str = "") -> dict[str, Any]:
    """Monta os dados do card sem usar Bulbasaur como fallback indevido."""
    slug = slugify(nome)
    dados = None

    # Quando a URL do catálogo está disponível, usamos o recurso correto.
    if url:
        dados = api_get(url)

    # Se algum chamador não fornecer a URL, buscamos pelo nome real.
    if not dados and slug:
        dados = api_get(f"pokemon/{slug}")

    pokemon_id = (dados or {}).get("id") or extrair_id_pokemon(url)
    sprites = (dados or {}).get("sprites", {}) or {}
    outros = sprites.get("other", {}) or {}
    artwork = (outros.get("official-artwork", {}) or {}).get("front_default")
    home = (outros.get("home", {}) or {}).get("front_default")
    front = sprites.get("front_default")
    sprite = artwork or home or front

    # Último recurso: URL oficial construída pelo ID correto.
    # Nunca usamos ID 1 / Bulbasaur como fallback genérico.
    if not sprite and pokemon_id:
        sprite = (
            f"https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/other/official-artwork/{pokemon_id}.png"
        )

    return {
        "nome": bonito_nome((dados or {}).get("name") or slug or nome),
        "slug": slug,
        "id": pokemon_id,
        "sprite": sprite,
    }


def encontrar_pagina_pokedex() -> str | None:
    """Localiza a página física da Pokédex dentro da pasta pages."""
    base_dir = Path(__file__).resolve().parent.parent
    pasta_pages = base_dir / "pages"

    candidatos = [
        "pokedex.py",
        "1_Pokedex.py",
        "1_Pokedex_COMPLETA.py",
        "1_Pokedex_COMPLETA_CORRIGIDA_evolucoes_formas.py",
    ]

    for nome_arquivo in candidatos:
        caminho = pasta_pages / nome_arquivo
        if caminho.exists():
            return str(caminho.relative_to(base_dir)).replace("\\", "/")

    encontrados = sorted(pasta_pages.glob("*pokedex*.py")) + sorted(pasta_pages.glob("*Pokedex*.py"))
    if encontrados:
        return str(encontrados[0].relative_to(base_dir)).replace("\\", "/")
    return None


def abrir_pokemon_na_pokedex(nome: str) -> None:
    """Envia o usuário para a Pokédex com o Pokémon já focado."""
    slug = str(nome or "").strip().lower().replace(" ", "-")
    st.session_state["pokemon_focado"] = slug
    pagina = encontrar_pagina_pokedex()
    if pagina:
        st.switch_page(pagina)
    else:
        st.error("Não foi possível localizar a página da Pokédex na pasta pages/.")


# ============================================================
# 📚 CATÁLOGOS LEVES
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def catalogo_movimentos() -> list[dict[str, str]]:
    return listar_recursos("move", 2000)


@st.cache_data(ttl=86400, show_spinner=False)
def catalogo_itens() -> list[dict[str, str]]:
    return listar_recursos("item", 3000)


@st.cache_data(ttl=86400, show_spinner=False)
def catalogo_habilidades() -> list[dict[str, str]]:
    return listar_recursos("ability", 1000)


@st.cache_data(ttl=86400, show_spinner=False)
def catalogo_tipos_oficiais() -> list[dict[str, str]]:
    recursos = listar_recursos("type", 100)
    ids_oficiais = {
        "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
        "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy",
    }
    return [r for r in recursos if r.get("name") in ids_oficiais]


@st.cache_data(ttl=86400, show_spinner=False)
def pokemon_por_tipo_oficial(tipo_slug: str) -> list[dict[str, str]]:
    """Retorna todos os Pokémon/variantes cadastrados com a tipagem oficial.

    O recurso Type da PokéAPI mantém a lista de Pokémon que possuem aquela
    tipagem. Como variantes também podem ser recursos Pokémon próprios, formas
    como Mega Charizard X entram no tipo Dragão quando a própria variante possui
    Dragão — independentemente de a espécie-base ser Fogo/Voador.
    """
    dados = buscar_recurso("type", tipo_slug)
    if not dados:
        return []

    retorno: list[dict[str, str]] = []
    vistos: set[str] = set()

    for entrada in dados.get("pokemon", []) or []:
        recurso = entrada.get("pokemon", {}) or {}
        nome = str(recurso.get("name", "")).strip()
        url = str(recurso.get("url", "")).strip()
        if not nome or nome in vistos:
            continue
        vistos.add(nome)
        retorno.append({"name": nome, "url": url})

    return retorno


def eh_variante_pokemon(nome: str) -> bool:
    """Detecta variantes/formas pelo identificador do recurso Pokémon."""
    slug = str(nome or "").strip().lower()
    return "-" in slug


def nome_variante_legivel(nome: str) -> str:
    """Converte alguns sufixos comuns de formas em rótulos amigáveis."""
    slug = str(nome or "").strip().lower()
    mapa = {
        "-mega-x": " Mega X",
        "-mega-y": " Mega Y",
        "-mega": " Mega",
        "-gmax": " Gigantamax",
        "-alola": " de Alola",
        "-galar": " de Galar",
        "-hisui": " de Hisui",
        "-paldea": " de Paldea",
        "-origin": " Forma Origem",
        "-therian": " Forma Therian",
        "-incarnate": " Forma Incarnate",
        "-sky": " Forma Céu",
        "-dawn": " Forma Dawn",
        "-dusk": " Forma Dusk",
        "-midnight": " Forma Midnight",
        "-sunny": " Forma Sunny",
        "-rainy": " Forma Rainy",
        "-snowy": " Forma Snowy",
        "-wash": " Wash",
        "-heat": " Heat",
        "-mow": " Mow",
        "-frost": " Frost",
        "-fan": " Fan",
        "-blade": " Blade",
        "-shield": " Shield",
        "-dusk-form": " Forma Dusk",
        "-bloodmoon": " Bloodmoon",
        "-stellar": " Stellar Form",
        "-sky-shaymin": " Sky Forme",
    }

    for sufixo in sorted(mapa, key=len, reverse=True):
        if slug.endswith(sufixo):
            base = slug[: -len(sufixo)]
            return f"{bonito_nome(base)}{mapa[sufixo]}"

    return bonito_nome(slug)


@st.cache_data(ttl=86400, show_spinner=False)
def dados_mini_dex_tipo_oficial(tipo_slug: str) -> list[dict[str, Any]]:
    """Monta o Mini-Dex completo de um tipo oficial, incluindo variantes."""
    retorno: list[dict[str, Any]] = []

    for recurso in pokemon_por_tipo_oficial(tipo_slug):
        nome = recurso.get("name", "")
        url = recurso.get("url", "")
        mini = dados_mini_dex_pokemon(nome, url)
        mini["nome_exibicao"] = nome_variante_legivel(nome)
        mini["eh_variante"] = eh_variante_pokemon(nome)
        retorno.append(mini)

    def chave_ordenacao(item: dict[str, Any]) -> tuple[int, int, str]:
        pokemon_id = item.get("id")
        if isinstance(pokemon_id, int):
            return (1 if item.get("eh_variante") else 0, pokemon_id, str(item.get("slug", "")))
        return (1 if item.get("eh_variante") else 0, 999999, str(item.get("slug", "")))

    retorno.sort(key=chave_ordenacao)
    return retorno


@st.cache_data(ttl=86400, show_spinner=False)
def catalogo_classes_dano() -> dict[str, set[str]]:
    retorno: dict[str, set[str]] = {"physical": set(), "special": set(), "status": set()}
    for classe in retorno:
        dados = listar_recursos(f"move-damage-class/{classe}", 2000)
        # A chamada acima, para endpoint com nome, retorna um objeto e não lista.
        if dados and isinstance(dados, list):
            retorno[classe] = {item.get("name", "") for item in dados}
        else:
            detalhe = buscar_recurso("move-damage-class", classe)
            if detalhe:
                retorno[classe] = {item.get("name", "") for item in detalhe.get("moves", [])}
    return retorno


@st.cache_data(ttl=86400, show_spinner=False)
def geracoes_com_habilidades() -> dict[str, set[str]]:
    retorno: dict[str, set[str]] = {}
    for i in range(1, 10):
        dados = buscar_recurso("generation", str(i))
        if dados:
            retorno[dados.get("name", f"generation-{i}")] = {
                item.get("name", "") for item in dados.get("abilities", [])
            }
    return retorno


@st.cache_data(ttl=86400, show_spinner=False)
def categorias_itens() -> dict[str, set[str]]:
    retorno: dict[str, set[str]] = {}
    categorias = listar_recursos("item-category", 200)
    for categoria in categorias:
        dados = buscar_recurso("item-category", categoria.get("name", ""))
        if dados:
            retorno[dados.get("name", "")] = {
                item.get("name", "") for item in dados.get("items", [])
            }
    return retorno


# ============================================================
# ⭐ MOVIMENTOS DE ASSINATURA — HEURÍSTICA
# ============================================================

ASSINATURAS_CONHECIDAS = {
    # Kanto / Johto / Hoenn / Sinnoh / Unova / Kalos / Alola / Galar / Paldea
    "pika-sparkling-starstorm", "volt-tackle", "bolt-strike", "blue-flare",
    "spacial-rend", "roar-of-time", "shadow-force", "signature-move",
    "sacred-fire", "aeroblast", "diamond-storm", "origin-pulse", "precipice-blades",
    "psystrike", "v-create", "oblivion-wing", "gearing-up", "core-enforcer",
    "sunsteel-strike", "moongeist-beam", "spectral-thief", "mind-blown",
    "snipe-shot", "behemoth-blade", "behemoth-bash", "astral-barrage",
    "glacial-lance", "bleakwind-storm", "wildbolt-storm", "sandsear-storm",
    "ceaseless-edge", "stone-axe", "dire-claw", "mountain-gale", "torch-song",
    "aqua-step", "flower-trick", "make-it-rain", "kowtow-cleave", "gigaton-hammer",
    "population-bomb", "collision-course", "electro-drift", "mortal-spin",
    "psyblade", "lumina-crash", "hydro-steam", "dragon-cheer",
}

# ============================================================
# 🌑 FORMAS SHADOW — IMAGENS LOCAIS
# ============================================================

FORMAS_SHADOW_LOCAIS = {
    "Shadow Lugia": {
        "slug": "lugia",
        "arquivo": "shadow_lugia.png",
        "caminho": "imagens/formas/shadow_lugia.png",
        "id": 249,
        "descricao": "Lugia na forma Shadow (XD001), apresentado em Pokémon XD: Gale of Darkness.",
    },
    "Shadow Mewtwo": {
        "slug": "mewtwo",
        "arquivo": "shadow_mewtwo.png",
        "caminho": "imagens/formas/shadow_mewtwo.png",
        "id": 150,
        "descricao": "Manifestação especial conhecida como Shadow Mewtwo no universo de Pokkén Tournament.",
    },
}


def localizar_imagem_shadow(nome_forma: str) -> Path | None:
    """Localiza a arte customizada da forma Shadow no projeto."""
    dados = FORMAS_SHADOW_LOCAIS.get(nome_forma)
    if not dados:
        return None

    candidatos = [
        Path(__file__).resolve().parent.parent / dados["caminho"],
        Path(__file__).resolve().parent.parent / "imagens" / "formas" / dados["arquivo"],
        Path.cwd() / dados["caminho"],
    ]

    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None


def abrir_forma_shadow_na_pokedex(nome_forma: str) -> None:
    """Abre a espécie-base na Pokédex para consultar a forma cadastrada."""
    dados = FORMAS_SHADOW_LOCAIS.get(nome_forma)
    if not dados:
        return
    abrir_pokemon_na_pokedex(dados["slug"])


def mostrar_card_shadow(nome_forma: str, indice: int) -> None:
    """Mostra um card dedicado para Shadow Lugia e Shadow Mewtwo."""
    dados = FORMAS_SHADOW_LOCAIS[nome_forma]
    imagem = localizar_imagem_shadow(nome_forma)

    with st.container(border=True):
        if imagem:
            st.image(str(imagem), width=150)
        else:
            # Fallback visual: arte oficial da espécie-base.
            st.image(
                f"https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                f"sprites/pokemon/other/official-artwork/{dados['id']}.png",
                width=150,
            )
            st.caption(
                f"⚠️ Arte Shadow local não encontrada em `{dados['caminho']}`"
            )

        st.markdown(f"### 🌑 {nome_forma}")
        st.caption(dados["descricao"])
        st.markdown(
            f"**Pokémon-base:** {bonito_nome(dados['slug'])}"
        )

        if st.button(
            "📖 Abrir na Pokédex",
            key=f"shadow_pokedex_{indice}_{slugify(nome_forma)}",
            use_container_width=True,
        ):
            abrir_forma_shadow_na_pokedex(nome_forma)


def mostrar_lista_shadow() -> None:
    """Exibe somente os dois representantes Shadow definidos pelo KAYZAC."""
    st.markdown("### 🌑 Representantes cadastrados")
    st.caption(
        "No KAYZAC, esta seção usa as artes locais das duas formas especiais "
        "cadastradas: Shadow Lugia e Shadow Mewtwo."
    )

    nomes_shadow = ["Shadow Lugia", "Shadow Mewtwo"]
    colunas = st.columns(2)
    for indice, nome_forma in enumerate(nomes_shadow):
        with colunas[indice]:
            mostrar_card_shadow(nome_forma, indice)


# ============================================================
# 🏠 CABEÇALHO
# ============================================================

st.title("📚 Biblioteca Pokémon")
st.caption("Movimentos, itens, habilidades e tipos — agora usando dados reais da PokéAPI.")

st.markdown(
    """
    <div class="library-hero">
        <div class="library-title">⚡ KAYZAC - MASTER POKEMON! ⚡</div>
        <div class="library-subtitle">
            A biblioteca central das batalhas Pokémon. Pesquise recursos, abra fichas detalhadas
            e explore a tabela oficial de tipos.
        </div>
        <span class="tag">🥊 Movimentos</span>
        <span class="tag">🎒 Itens</span>
        <span class="tag">🧬 Habilidades</span>
        <span class="tag">🌈 Tipos</span>
        <span class="tag">⭐ Assinaturas</span>
        <span class="tag">💠 Z-Moves</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 📊 CONTADORES
# ============================================================

with st.spinner("Carregando o catálogo da Biblioteca..."):
    movimentos_catalogo = catalogo_movimentos()
    itens_catalogo = catalogo_itens()
    habilidades_catalogo = catalogo_habilidades()
    tipos_catalogo = catalogo_tipos_oficiais()

# Catálogo leve de espécies/forms reconhecidos pela PokéAPI.
# Ele é usado apenas para validar os cards temáticos da Biblioteca.
pokemon_catalogo = listar_recursos("pokemon", 2000)
pokemon_catalogo_nomes = {
    x.get("name", "")
    for x in pokemon_catalogo
}
pokemon_catalogo_urls = {
    str(x.get("name", "")): str(x.get("url", ""))
    for x in pokemon_catalogo
    if x.get("name") and x.get("url")
}

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><b>🥊 Movimentos</b><br><b style="font-size:25px">{len(movimentos_catalogo):,}</b></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><b>🎒 Itens</b><br><b style="font-size:25px">{len(itens_catalogo):,}</b></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><b>🧬 Habilidades</b><br><b style="font-size:25px">{len(habilidades_catalogo):,}</b></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-box"><b>🌈 Tipos oficiais</b><br><b style="font-size:25px">{len(tipos_catalogo):,}</b></div>', unsafe_allow_html=True)

st.write("")

# ============================================================
# 🧭 ABAS
# ============================================================

aba_mov, aba_itens, aba_hab, aba_tipos = st.tabs(
    ["🥊 Movimentos", "🎒 Itens", "🧬 Habilidades", "🌈 Tipos"]
)

# ============================================================
# 🥊 MOVIMENTOS
# ============================================================

with aba_mov:
    st.subheader("🥊 Todos os Movimentos")
    st.caption("O catálogo usa a lista completa da PokéAPI e carrega os detalhes somente quando necessário.")

    nomes_mov = [item.get("name", "") for item in movimentos_catalogo]
    nomes_mov.sort()

    f1, f2, f3 = st.columns([2.2, 1, 1])
    with f1:
        busca_mov = st.text_input(
            "🔎 Pesquisar movimento",
            placeholder="Ex.: Aura Sphere, Thunderbolt, Close Combat...",
            key="biblioteca_busca_mov",
        )
    with f2:
        filtro_classe = st.selectbox(
            "🎯 Categoria",
            ["Todas", "Físico", "Especial", "Status"],
            key="biblioteca_filtro_classe",
        )
    with f3:
        filtro_assinatura = st.selectbox(
            "⭐ Assinatura",
            ["Todos", "Assinaturas conhecidas", "Exclusivos/raríssimos"],
            key="biblioteca_filtro_assinatura",
        )

    candidatos = nomes_mov
    if busca_mov:
        termo = slugify(busca_mov).replace("-", " ")
        candidatos = [
            nome for nome in candidatos
            if termo in nome.replace("-", " ") or busca_mov.lower() in bonito_nome(nome).lower()
        ]

    if filtro_classe != "Todas":
        classe_slug = {"Físico": "physical", "Especial": "special", "Status": "status"}[filtro_classe]
        classes = catalogo_classes_dano()
        candidatos = [nome for nome in candidatos if nome in classes.get(classe_slug, set())]

    if filtro_assinatura == "Assinaturas conhecidas":
        candidatos = [nome for nome in candidatos if nome in ASSINATURAS_CONHECIDAS]
    elif filtro_assinatura == "Exclusivos/raríssimos":
        limite = st.slider("Máximo de Pokémon que aprendem", 1, 10, 2, key="limite_assinatura")
        # Esta opção é calculada apenas para os candidatos exibidos.
        candidatos = candidatos[:80]
        filtrados = []
        with st.spinner("Verificando exclusividade dos movimentos..."):
            for nome in candidatos:
                detalhe = buscar_recurso("move", nome)
                if detalhe and len(detalhe.get("learned_by_pokemon", [])) <= limite:
                    filtrados.append(nome)
        candidatos = filtrados

    if not candidatos:
        st.warning("Nenhum movimento encontrado com esses filtros.")
    else:
        opcoes = ["— selecione um movimento —"] + candidatos[:500]
        mov_escolhido = st.selectbox(
            f"📖 Resultado da pesquisa ({len(candidatos):,})",
            opcoes,
            format_func=lambda x: "— selecione um movimento —" if x.startswith("—") else bonito_nome(x),
            key="biblioteca_movimento_escolhido",
        )

        if mov_escolhido != opcoes[0]:
            with st.spinner(f"Carregando {bonito_nome(mov_escolhido)}..."):
                dados = buscar_recurso("move", mov_escolhido)

            if dados:
                nome = escolher_idioma(dados.get("names"), "name") or bonito_nome(dados.get("name", ""))
                tipo = nome_tipo(dados.get("type", {}).get("name", ""))
                classe = classe_movimento(dados.get("damage_class", {}).get("name", ""))
                geracao = geracao_nome(dados.get("generation", {}).get("name", ""))
                efeito = escolher_idioma(dados.get("effect_entries"), "short_effect")
                descricao = escolher_idioma(dados.get("flavor_text_entries"), "flavor_text")
                alvo = bonito_nome(dados.get("target", {}).get("name", ""))
                ailment = bonito_nome(dados.get("meta", {}).get("ailment", {}).get("name", "")) if dados.get("meta") else "Nenhum"
                assinatura = mov_escolhido in ASSINATURAS_CONHECIDAS
                learned_by = dados.get("learned_by_pokemon", [])
                z_move = bool(dados.get("z_move"))
                max_move = bool(dados.get("max_move"))

                st.markdown(
                    f'<div class="library-card"><div class="library-title">🥊 {nome} {"⭐" if assinatura else ""}</div>'
                    f'<div class="library-subtitle">{tipo} • {classe} • {geracao}</div>'
                    f'<span class="tag">⚡ Poder: {dados.get("power") or "—"}</span>'
                    f'<span class="tag">🎯 Precisão: {dados.get("accuracy") or "—"}</span>'
                    f'<span class="tag">🔄 PP: {dados.get("pp") or "—"}</span>'
                    f'<span class="tag">↕️ Prioridade: {dados.get("priority", 0)}</span>'
                    f'<span class="tag">🎯 Alvo: {alvo}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                d1, d2, d3 = st.columns(3)
                with d1:
                    st.markdown("### 📜 Efeito")
                    st.write(efeito or descricao or "Sem descrição disponível.")
                with d2:
                    st.markdown("### ✨ Efeitos adicionais")
                    st.write(f"Chance do efeito: {dados.get('effect_chance') or '—'}%")
                    st.write(f"Status/ailment: {ailment or 'Nenhum'}")
                    st.write(f"Contato: {'Sim' if dados.get('meta', {}).get('flinch_chance') is not None and dados.get('meta') else 'Não informado'}")
                with d3:
                    st.markdown("### 💠 Mecânicas")
                    st.write(f"Movimento Z associado: {'Sim' if z_move else 'Não'}")
                    st.write(f"Movimento Dynamax: {'Sim' if max_move else 'Não'}")
                    st.write(f"Aprendido por: {len(learned_by):,} Pokémon")

                with st.expander("📚 Pokémon que aprendem este movimento", expanded=True):
                    if learned_by:
                        st.caption(
                            "Mini-Dex: clique na imagem ou no botão de um Pokémon para abrir sua ficha na Pokédex."
                        )

                        # Mini-Dex visual semelhante às galerias usadas em Regiões e Personagens.
                        colunas = 6
                        for inicio in range(0, len(learned_by), colunas):
                            grupo = learned_by[inicio:inicio + colunas]
                            cols = st.columns(colunas)
                            for idx, pokemon_ref in enumerate(grupo):
                                with cols[idx]:
                                    nome_pokemon = pokemon_ref.get("name", "")
                                    dados_mini = dados_mini_dex_pokemon(
                                        nome_pokemon, pokemon_ref.get("url", "")
                                    )
                                    st.image(
                                        dados_mini["sprite"],
                                        width=105,
                                        caption=(
                                            f"#{dados_mini['id']} • {dados_mini['nome']}"
                                            if dados_mini["id"]
                                            else dados_mini["nome"]
                                        ),
                                    )
                                    if st.button(
                                        "📖 Abrir na Pokédex",
                                        key=f"mini_dex_move_{mov_escolhido}_{inicio}_{idx}",
                                        use_container_width=True,
                                    ):
                                        abrir_pokemon_na_pokedex(nome_pokemon)
                    else:
                        st.info("Nenhum Pokémon listado pela PokéAPI para este movimento.")

                with st.expander("⚙️ Dados técnicos completos"):
                    st.json(dados)
        else:
            st.info("Selecione um movimento acima para abrir a ficha completa.")

    with st.expander("⭐ Como a Biblioteca identifica movimentos de assinatura"):
        st.write(
            "A lista 'Assinaturas conhecidas' é uma curadoria inicial do projeto. "
            "A categoria não é um campo universal da PokéAPI: exclusividade de movimento "
            "também depende de geração, formas e métodos de aprendizado. Já a opção "
            "'Exclusivos/raríssimos' usa a quantidade de Pokémon listados pela API como heurística."
        )

# ============================================================
# 🎒 ITENS
# ============================================================

with aba_itens:
    st.subheader("🎒 Todos os Itens")
    st.caption("Poké Balls, itens de batalha, evolução, berries, Mega Stones, Z-Crystals e muito mais.")

    f1, f2, f3 = st.columns([2.4, 1, 1])
    with f1:
        busca_item = st.text_input(
            "🔎 Pesquisar item",
            placeholder="Ex.: Focus Sash, Light Clay, Lucarionite...",
            key="biblioteca_busca_item",
        )
    with f2:
        filtro_item = st.selectbox(
            "📂 Categoria",
            ["Todas", "Poké Balls", "Medicinas", "Seguráveis", "Evolução", "Mega Stones", "Z-Crystals", "Específicos de espécie"],
            key="biblioteca_filtro_item",
        )
    with f3:
        filtro_held = st.selectbox(
            "⚔️ Batalha",
            ["Todos", "Interessantes no competitivo"],
            key="biblioteca_filtro_held",
        )

    candidatos_item = [x.get("name", "") for x in itens_catalogo]
    candidatos_item.sort()

    if busca_item:
        candidatos_item = [
            nome for nome in candidatos_item
            if busca_item.lower() in nome.lower() or busca_item.lower() in bonito_nome(nome).lower()
        ]

    if filtro_item != "Todas":
        mapa_categoria = {
            "Poké Balls": "standard-balls",
            "Medicinas": "medicine",
            "Seguráveis": "held-items",
            "Evolução": "evolution",
            "Mega Stones": "mega-stones",
            "Z-Crystals": "z-crystals",
            "Específicos de espécie": "species-specific",
        }
        cat_slug = mapa_categoria[filtro_item]
        categorias = categorias_itens()
        candidatos_item = [nome for nome in candidatos_item if nome in categorias.get(cat_slug, set())]

    if filtro_held == "Interessantes no competitivo":
        palavras = ("choice", "sash", "orb", "leftovers", "boots", "helmet", "vest", "clay", "scarf", "band", "specs", "eviolite", "air-balloon", "sitrus")
        candidatos_item = [nome for nome in candidatos_item if any(p in nome for p in palavras)]

    if not candidatos_item:
        st.warning("Nenhum item encontrado com esses filtros.")
    else:
        opcoes = ["— selecione um item —"] + candidatos_item[:700]
        item_escolhido = st.selectbox(
            f"📖 Resultado da pesquisa ({len(candidatos_item):,})",
            opcoes,
            format_func=lambda x: "— selecione um item —" if x.startswith("—") else bonito_nome(x),
            key="biblioteca_item_escolhido",
        )

        if item_escolhido != opcoes[0]:
            with st.spinner(f"Carregando {bonito_nome(item_escolhido)}..."):
                dados = buscar_recurso("item", item_escolhido)

            if dados:
                nome = escolher_idioma(dados.get("names"), "name") or bonito_nome(dados.get("name", ""))
                categoria = categoria_item_nome(dados.get("category", {}).get("name", ""))
                efeito = escolher_idioma(dados.get("effect_entries"), "short_effect")
                descricao = escolher_idioma(dados.get("flavor_text_entries"), "text")
                sprite = dados.get("sprites", {}).get("default")
                held_by = dados.get("held_by_pokemon", [])

                if sprite:
                    cimg, cinfo = st.columns([1, 3])
                    with cimg:
                        st.image(sprite, width=120)
                    with cinfo:
                        st.markdown(f'<div class="library-title">🎒 {nome}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="library-subtitle">{categoria}</div>', unsafe_allow_html=True)
                        st.write(efeito or descricao or "Sem descrição disponível.")
                else:
                    st.markdown(f"## 🎒 {nome}")
                    st.write(efeito or descricao or "Sem descrição disponível.")

                a, b, c = st.columns(3)
                with a:
                    st.metric("💰 Preço", dados.get("cost") if dados.get("cost") is not None else "—")
                with b:
                    st.metric("🪨 Fling Power", dados.get("fling_power") if dados.get("fling_power") is not None else "—")
                with c:
                    st.metric("🐾 Pokémon que seguram", len(held_by))

                if held_by:
                    with st.expander("🐾 Pokémon que podem carregar este item"):
                        st.write(" • ".join(sorted(bonito_nome(p.get("pokemon", {}).get("name", "")) for p in held_by)))

                with st.expander("⚙️ Dados técnicos completos"):
                    st.json(dados)
        else:
            st.info("Selecione um item acima para abrir a ficha completa.")

# ============================================================
# 🧬 HABILIDADES
# ============================================================

with aba_hab:
    st.subheader("🧬 Todas as Habilidades")
    st.caption("Habilidades normais, ocultas e especiais, com descrição e geração de origem.")

    f1, f2, f3 = st.columns([2.4, 1, 1])
    with f1:
        busca_hab = st.text_input(
            "🔎 Pesquisar habilidade",
            placeholder="Ex.: Intimidate, Adaptability, Protean...",
            key="biblioteca_busca_hab",
        )
    with f2:
        filtro_geracao = st.selectbox(
            "📅 Geração",
            ["Todas"] + [f"Geração {i}" for i in range(1, 10)],
            key="biblioteca_filtro_geracao_hab",
        )
    with f3:
        limite_hab = st.slider(
            "📚 Mostrar até",
            20,
            500,
            120,
            step=20,
            key="biblioteca_limite_hab",
        )

    candidatos_hab = [x.get("name", "") for x in habilidades_catalogo]
    candidatos_hab.sort()

    if busca_hab:
        candidatos_hab = [
            nome for nome in candidatos_hab
            if busca_hab.lower() in nome.lower() or busca_hab.lower() in bonito_nome(nome).lower()
        ]

    if filtro_geracao != "Todas":
        numero = int(filtro_geracao.split()[-1])
        mapa = geracoes_com_habilidades()
        chave = f"generation-{['i','ii','iii','iv','v','vi','vii','viii','ix'][numero-1]}"
        candidatos_hab = [nome for nome in candidatos_hab if nome in mapa.get(chave, set())]

    if not candidatos_hab:
        st.warning("Nenhuma habilidade encontrada.")
    else:
        opcoes = ["— selecione uma habilidade —"] + candidatos_hab[:limite_hab]
        hab_escolhida = st.selectbox(
            f"📖 Resultado da pesquisa ({len(candidatos_hab):,})",
            opcoes,
            format_func=lambda x: "— selecione uma habilidade —" if x.startswith("—") else bonito_nome(x),
            key="biblioteca_hab_escolhida",
        )

        if hab_escolhida != opcoes[0]:
            with st.spinner(f"Carregando {bonito_nome(hab_escolhida)}..."):
                dados = buscar_recurso("ability", hab_escolhida)

            if dados:
                nome = escolher_idioma(dados.get("names"), "name") or bonito_nome(dados.get("name", ""))
                efeito = escolher_idioma(dados.get("effect_entries"), "short_effect")
                descricao = escolher_idioma(dados.get("flavor_text_entries"), "flavor_text")
                geracao = geracao_nome(dados.get("generation", {}).get("name", ""))
                pokemon = dados.get("pokemon", [])

                st.markdown(
                    f'<div class="library-card"><div class="library-title">🧬 {nome}</div>'
                    f'<div class="library-subtitle">Introduzida em {geracao}</div>'
                    f'<div>{efeito or descricao or "Sem descrição disponível."}</div></div>',
                    unsafe_allow_html=True,
                )

                st.metric("🐾 Pokémon associados", len(pokemon))
                with st.expander("🐾 Pokémon com esta habilidade", expanded=True):
                    if pokemon:
                        st.caption(
                            "Mini-Dex: cada card usa a URL do Pokémon retornada pela PokéAPI, "
                            "evitando imagens trocadas ou o fallback do Bulbasaur."
                        )

                        colunas = 6
                        for inicio in range(0, len(pokemon), colunas):
                            grupo = pokemon[inicio:inicio + colunas]
                            cols = st.columns(colunas)

                            for idx, pokemon_ref in enumerate(grupo):
                                with cols[idx]:
                                    pokemon_data = pokemon_ref.get("pokemon", {}) or {}
                                    nome_pokemon = pokemon_data.get("name", "")
                                    url_pokemon = pokemon_data.get("url", "")

                                    if not nome_pokemon:
                                        st.caption("Pokémon sem nome disponível")
                                        continue

                                    dados_mini = dados_mini_dex_pokemon(
                                        nome_pokemon,
                                        url_pokemon,
                                    )

                                    with st.container(border=True):
                                        if dados_mini.get("sprite"):
                                            st.image(
                                                dados_mini["sprite"],
                                                width=105,
                                                caption=(
                                                    f"#{dados_mini['id']} • {dados_mini['nome']}"
                                                    if dados_mini.get("id")
                                                    else dados_mini["nome"]
                                                ),
                                            )
                                        else:
                                            st.markdown(f"**{dados_mini['nome']}**")

                                        if pokemon_ref.get("is_hidden"):
                                            st.caption("🌟 Habilidade oculta")
                                        else:
                                            st.caption("🧬 Habilidade disponível")

                                        if st.button(
                                            "📖 Abrir na Pokédex",
                                            key=(
                                                f"mini_dex_hab_{hab_escolhida}_"
                                                f"{inicio}_{idx}_{nome_pokemon}"
                                            ),
                                            use_container_width=True,
                                        ):
                                            abrir_pokemon_na_pokedex(nome_pokemon)
                    else:
                        st.info("Nenhum Pokémon listado pela PokéAPI para esta habilidade.")

                with st.expander("⚙️ Dados técnicos completos"):
                    st.json(dados)
        else:
            st.info("Selecione uma habilidade acima para abrir a ficha completa.")

# ============================================================
# 🖼️ RENDERIZAÇÃO ROBUSTA DOS POKÉMON DA CURADORIA
# ============================================================

# Alguns nomes da curadoria representam formas específicas, observações
# entre parênteses ou Pokémon que não são recursos próprios da PokéAPI.
# Os aliases abaixo fazem a ponte entre o nome exibido e o slug pesquisável.
ALIASES_CURADORIA_POKEMON = {
    "aegislash": "aegislash-shield",
    "toxtricity": "toxtricity-amped",
    "meloetta": "meloetta-aria",
    "tornadus": "tornadus-incarnate",
    "thundurus": "thundurus-incarnate",
    "landorus": "landorus-incarnate",
    "thundurus-therian": "thundurus-therian",
    "landorus-therian": "landorus-therian",
    "tornadus-therian": "tornadus-therian",
    # Lycanroc no subtipo Anime representa especificamente o Dusk Form de Ash.
    "lycanroc": "lycanroc-dusk",
    "lycanroc-dusk-form": "lycanroc-dusk",
    "lycanroc-dusk": "lycanroc-dusk",
    "terapagos": "terapagos",
    "terapagos-stellar-form": "terapagos-stellar",
    # 🌌 Espécies cósmicas com resolução direta pela espécie-base.
    "minior": "minior",
    "giratina": "giratina",
    "deoxys": "deoxys",
    "venusaur": "venusaur",
    "mimikyu": "mimikyu",
    "meowstic": "meowstic-male",
    "meowstic-male": "meowstic-male",
    "meowstic-female": "meowstic-female",
    "basculegion": "basculegion",
    "basculegion-male": "basculegion-male",
    "basculegion-female": "basculegion-female",
    "persian-de-alola": "persian-alola",
    "ursaluna-bloodmoon": "ursaluna-bloodmoon",
    "ursaluna-blood-moon": "ursaluna-bloodmoon",
    "unown": "unown",
    "sirfetchd": "sirfetchd",
    "sirfetch-d": "sirfetchd",
    "porygon-z": "porygon-z",
    # Formas regionais usadas nas classificações KAYZAC.
    "decidueye-de-hisui": "decidueye-hisui",
    "samurott-de-hisui": "samurott-hisui",
    "voltorb-de-hisui": "voltorb-hisui",
    "electrode-de-hisui": "electrode-hisui",
    "samurott-de-hisui": "samurott-hisui",
    "type-null": "type-null",
    "grimer-de-alola": "grimer-alola",
    "muk-de-alola": "muk-alola",
    "exeggutor-de-alola": "exeggutor-alola",
}

# IDs oficiais das espécies que servem como último fallback visual.
# Assim, uma falha pontual da API nunca faz o card desaparecer.
IDS_FALLBACK_CURADORIA = {
    "unown": 201,
    "arceus": 493,
    "porygon": 137,
    "porygon2": 233,
    "porygon-z": 474,
    "sirfetchd": 865,
    "aegislash": 681,
    "aegislash-shield": 681,
    "aegislash-blade": 681,
    "toxtricity": 849,
    "toxtricity-amped": 849,
    "toxtricity-low-key": 849,
    "meloetta": 648,
    "meloetta-aria": 648,
    "meloetta-pirouette": 648,
    "tornadus": 641,
    "tornadus-incarnate": 641,
    "tornadus-therian": 641,
    "thundurus": 642,
    "thundurus-incarnate": 642,
    "thundurus-therian": 642,
    "landorus": 645,
    "landorus-incarnate": 645,
    "landorus-therian": 645,
    "lycanroc": 745,
    "lycanroc-dusk": 745,
    "terapagos": 1024,
    "terapagos-stellar": 1024,
    # 🌌 Cósmico — fallbacks de espécies que podem falhar no catálogo local.
    "minior": 774,
    "giratina": 487,
    "deoxys": 386,
    "pyroar": 668,
    "zygarde": 718,
    "venusaur": 3,
    "mimikyu": 778,
    "meowstic": 678,
    "meowstic-male": 678,
    "meowstic-female": 678,
    "basculegion": 902,
    "basculegion-male": 902,
    "basculegion-female": 902,
    "persian-alola": 53,
    "ursaluna-bloodmoon": 10272,
    "exploud": 295,
    "noivern": 715,
    "chatot": 441,
    "kricketune": 402,
    "primarina": 730,
    "ceruledge": 937,
    "bisharp": 625,
    "kingambit": 983,
    "gallade": 475,
    "kartana": 798,
    "samurott": 503,
    "whimsicott": 547,
    "talonflame": 663,
    "kilowattrel": 941,
    "altaria": 334,
    "igglybuff": 174,
    "jigglypuff": 39,
    "wigglytuff": 40,
    "whismur": 293,
    "loudred": 294,
    "kricketot": 401,
    "chingling": 433,
    "chimecho": 358,
    "bronzor": 436,
    "bronzong": 437,
    "vibrava": 329,
    "flygon": 330,
    "brionne": 729,
    "oricorio": 741,
    "rillaboom": 812,
    "kommo-o": 784,
    "skeledirge": 911,
    "lapras": 131,
    "popplio": 728,
    "zubat": 41,
    "golbat": 42,
    "crobat": 169,
    "woobat": 527,
    "swoobat": 528,
    "noibat": 714,
    "seismitoad": 537,
    "jangmo-o": 782,
    "hakamo-o": 783,
    # ⚔️ Arma — representantes adicionais.
    "honedge": 679,
    "doublade": 680,
    "scyther": 123,
    "scizor": 212,
    "aegislash-shield": 681,
    "gallade": 475,
    "ceruledge": 937,
    "bisharp": 625,
    "kingambit": 983,
    "kartana": 798,
    "samurott": 503,
    "samurott-hisui": 503,
    "zacian": 888,
    "iron-valiant": 1006,
    "kleavor": 900,
    "kabutops": 141,
    "haxorus": 612,
    "golisopod": 768,
    "decidueye": 724,
    "decidueye-hisui": 724,
    "inteleon": 818,
    "tinkaton": 959,
    "zamazenta": 889,
    "chesnaught": 652,
    "remoraid": 223,
    "octillery": 224,
    "blastoise": 9,
    "clawitzer": 693,
    "genesect": 649,
    "dragapult": 887,
    "voltorb": 100,
    "electrode": 101,
    "voltorb-hisui": 100,
    "electrode-hisui": 101,
    "pineco": 204,
    "forretress": 205,
    "blacephalon": 806,
    "dhelmise": 781,
    "drilbur": 529,
    "excadrill": 530,
    "timburr": 532,
    "gurdurr": 533,
    "conkeldurr": 534,
    "golurk": 623,
    "falinks": 870,
    "varoom": 965,
    "revavroom": 966,
    "iron-treads": 990,
    "iron-hands": 992,
}


def limpar_nome_curadoria(nome: str) -> str:
    """Remove observações e normaliza apóstrofos antes de criar o slug."""
    texto = str(nome or "").strip()
    texto = re.sub(r"\s*\([^)]*\)", "", texto)
    if "—" in texto:
        texto = texto.split("—", 1)[0].strip()

    # A PokéAPI usa "sirfetchd", enquanto o nome exibido pode ser
    # escrito como "Sirfetch’d". Removemos os apóstrofos para que
    # ambos resultem no mesmo identificador.
    texto = (
        texto
        .replace("’", "")
        .replace("‘", "")
        .replace("'", "")
        .replace("ʼ", "")
    )

    return slugify(texto)


def resolver_curadoria_pokemon(nome_exibicao: str) -> tuple[str, str, int | None]:
    # Basculegion (base e variantes de gênero) possui fallback nacional #902.
    """Resolve (slug, url, id) sem depender apenas do catálogo em memória."""
    slug_original = limpar_nome_curadoria(nome_exibicao)
    candidatos = [slug_original]

    alias = ALIASES_CURADORIA_POKEMON.get(slug_original)
    if alias and alias not in candidatos:
        candidatos.append(alias)

    # Formas sem entrada direta no catálogo: tenta a espécie-base.
    base = slug_original.split("-")[0]
    if base and base not in candidatos:
        candidatos.append(base)

    for candidato in candidatos:
        url = pokemon_catalogo_urls.get(candidato, "")
        if url:
            pokemon_id = extrair_id_pokemon(url)
            return candidato, url, pokemon_id

    # Sem URL no catálogo: mantém o slug pesquisável para a própria função
    # consultar a PokéAPI diretamente.
    for candidato in candidatos:
        if candidato:
            if candidato in IDS_FALLBACK_CURADORIA:
                return candidato, "", IDS_FALLBACK_CURADORIA[candidato]

    return slug_original, "", None


def dados_mini_dex_curadoria(nome_exibicao: str) -> dict[str, Any]:
    """Mini-Dex de curadoria com API + aliases + fallback de ID."""
    slug, url, id_fallback = resolver_curadoria_pokemon(nome_exibicao)
    dados = dados_mini_dex_pokemon(slug, url)

    if dados.get("sprite"):
        return dados

    if id_fallback:
        dados["id"] = id_fallback
        dados["nome"] = nome_exibicao.split("(", 1)[0].strip()

        # Ursaluna Bloodmoon possui recurso próprio na PokéAPI (#10272).
        if slug == "ursaluna-bloodmoon":
            dados["sprite"] = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                "sprites/pokemon/other/official-artwork/10272.png"
            )

        # Lycanroc tem três formas no mesmo número nacional.
        # Para o subtipo Anime, usamos a forma Crepuscular (Dusk).
        if slug == "lycanroc-dusk":
            dados["sprite"] = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                "sprites/pokemon/other/official-artwork/745-dusk.png"
            )
        else:
            dados["sprite"] = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                f"sprites/pokemon/other/official-artwork/{id_fallback}.png"
            )

    return dados


# ============================================================
# 🌈 TIPOS
# ============================================================

with aba_tipos:
    st.subheader("🌈 Tabela de Tipos")
    st.caption("Matriz oficial baseada nas relações de dano da PokéAPI.")

    tipos_oficiais = sorted(
        [x.get("name", "") for x in tipos_catalogo],
        key=lambda x: ["normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison", "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"].index(x),
    )

    tipo_escolhido = st.selectbox(
        "🌈 Escolha um tipo para análise",
        tipos_oficiais,
        format_func=nome_tipo,
        key="biblioteca_tipo_escolhido",
    )

    if tipo_escolhido:
        with st.spinner(f"Carregando relações do tipo {nome_tipo(tipo_escolhido)}..."):
            dados_tipo = buscar_recurso("type", tipo_escolhido)

        if dados_tipo:
            rel = dados_tipo.get("damage_relations", {})
            forte = [nome_tipo(x.get("name", "")) for x in rel.get("double_damage_to", [])]
            fraco = [nome_tipo(x.get("name", "")) for x in rel.get("half_damage_to", [])]
            imune = [nome_tipo(x.get("name", "")) for x in rel.get("no_damage_to", [])]
            defensivo_forte = [nome_tipo(x.get("name", "")) for x in rel.get("double_damage_from", [])]
            defensivo_fraco = [nome_tipo(x.get("name", "")) for x in rel.get("half_damage_from", [])]
            defensivo_imune = [nome_tipo(x.get("name", "")) for x in rel.get("no_damage_from", [])]

            st.markdown(f"## 🌈 {nome_tipo(tipo_escolhido)}")

            o1, o2, o3 = st.columns(3)
            with o1:
                st.markdown("### ⚔️ Ofensivo — 2×")
                st.write(" • ".join(forte) if forte else "Nenhum")
            with o2:
                st.markdown("### 🛡️ Ofensivo — ½×")
                st.write(" • ".join(fraco) if fraco else "Nenhum")
            with o3:
                st.markdown("### 🚫 Ofensivo — 0×")
                st.write(" • ".join(imune) if imune else "Nenhum")

            st.divider()

            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("### 💥 Defensivo — sofre 2×")
                st.write(" • ".join(defensivo_forte) if defensivo_forte else "Nenhum")
            with d2:
                st.markdown("### 🧱 Defensivo — sofre ½×")
                st.write(" • ".join(defensivo_fraco) if defensivo_fraco else "Nenhum")
            with d3:
                st.markdown("### 🛡️ Defensivo — sofre 0×")
                st.write(" • ".join(defensivo_imune) if defensivo_imune else "Nenhum")

    # ========================================================
    # 🐾 POKÉMON DA TIPAGEM — MINI-DEX SOB DEMANDA
    # ========================================================
    st.divider()
    st.markdown(f"### 🐾 Pokémon do tipo {nome_tipo(tipo_escolhido)}")
    st.caption(
        "O catálogo completo de Pokémon, formas e transformações é pesado para carregar. "
        "Por isso, o Mini-Dex só é consultado quando você clicar no botão abaixo. "
        "Assim, trocar de tipo continua rápido."
    )

    # Esta consulta é leve e aproveita o cache do recurso Type.
    # O Mini-Dex completo, que busca imagens/dados individuais, fica sob demanda.
    membros_tipo = pokemon_por_tipo_oficial(tipo_escolhido)
    qtd_variantes = sum(
        1 for item in membros_tipo if eh_variante_pokemon(item.get("name", ""))
    )
    qtd_base = max(0, len(membros_tipo) - qtd_variantes)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Pokémon / variantes", f"{len(membros_tipo):,}")
    with m2:
        st.metric("Entradas base", f"{qtd_base:,}")
    with m3:
        st.metric("Formas / transformações", f"{qtd_variantes:,}")

    chave_mini_dex = f"mini_dex_tipo_aberto_{tipo_escolhido}"
    if st.button(
        f"📖 Mini-Dex ({nome_tipo(tipo_escolhido)})",
        key=f"abrir_mini_dex_tipo_{tipo_escolhido}",
        use_container_width=True,
        type="primary",
    ):
        st.session_state[chave_mini_dex] = True

    if st.session_state.get(chave_mini_dex, False):
        with st.spinner(f"Montando o Mini-Dex de {nome_tipo(tipo_escolhido)}..."):
            minis_tipo = dados_mini_dex_tipo_oficial(tipo_escolhido)

        if minis_tipo:
            st.markdown("#### 📖 Mini-Dex completo")
            st.caption(
                "Cada forma é considerada pela sua própria tipagem. Exemplo: "
                "Mega Charizard X entra em Dragão porque a forma Mega X é "
                "Fogo/Dragão, enquanto Mega Charizard Y continua em Fogo/Voador."
            )

            colunas_tipo = 6
            for inicio in range(0, len(minis_tipo), colunas_tipo):
                grupo = minis_tipo[inicio:inicio + colunas_tipo]
                cols_tipo = st.columns(colunas_tipo)
                for idx_tipo, mini in enumerate(grupo):
                    with cols_tipo[idx_tipo]:
                        slug = mini.get("slug") or ""
                        with st.container(border=True):
                            if mini.get("sprite"):
                                st.image(mini["sprite"], width=95)

                            titulo = mini.get("nome_exibicao") or mini.get("nome") or slug
                            st.markdown(f"**{titulo}**")

                            if mini.get("eh_variante"):
                                st.caption("🔄 Forma / transformação")
                            else:
                                st.caption(f"# {mini.get('id') or '—'}")

                            if st.button(
                                "📖 Pokédex",
                                key=(
                                    f"tipo_oficial_pokemon_{tipo_escolhido}_"
                                    f"{inicio}_{idx_tipo}_{slug}"
                                ),
                                use_container_width=True,
                            ):
                                abrir_pokemon_na_pokedex(slug)
        else:
            st.warning("A PokéAPI não retornou Pokémon para esta tipagem no momento.")

    st.divider()
    st.markdown("### 📊 Os 18 tipos oficiais")
    colunas = st.columns(6)
    for idx, tipo in enumerate(tipos_oficiais):
        with colunas[idx % 6]:
            st.button(
                nome_tipo(tipo),
                key=f"tipo_oficial_{tipo}",
                use_container_width=True,
                disabled=True,
            )

    with st.expander("📋 Matriz completa 18 × 18"):
        # Monta a matriz usando os dados oficiais e os valores de dano.
        multiplicadores: dict[str, dict[str, str]] = {}
        mapa_ordem = tipos_oficiais
        with st.spinner("Montando a matriz oficial de tipos..."):
            for atacante in mapa_ordem:
                dados = buscar_recurso("type", atacante)
                rel = (dados or {}).get("damage_relations", {})
                por_nome: dict[str, str] = {alvo: "1×" for alvo in mapa_ordem}
                for alvo in rel.get("double_damage_to", []):
                    por_nome[alvo.get("name", "")] = "2×"
                for alvo in rel.get("half_damage_to", []):
                    por_nome[alvo.get("name", "")] = "½×"
                for alvo in rel.get("no_damage_to", []):
                    por_nome[alvo.get("name", "")] = "0×"
                multiplicadores[atacante] = por_nome

        cabecalho = [nome_tipo(x) for x in mapa_ordem]
        linhas = []
        for atacante in mapa_ordem:
            linhas.append([nome_tipo(atacante)] + [multiplicadores.get(atacante, {}).get(defensor, "1×") for defensor in mapa_ordem])

        st.dataframe(
            linhas,
            column_config={
                str(i): st.column_config.TextColumn(cabecalho[i - 1] if i > 0 else "Ataque ↓")
                for i in range(len(cabecalho) + 1)
            },
            hide_index=True,
            use_container_width=True,
        )

    with st.expander("🧪 Tipos exclusivos / classificações especiais KAYZAC", expanded=False):
        st.info(
            "Aqui ficam classificações que não devem ser misturadas à tabela oficial. "
            "??? e Stellar possuem histórico na série principal; Shadow pertence às mecânicas "
            "de Colosseum/XD; Som, Arma, Vento, Anime, Cyber, Cósmico, Luz, Areia, Madeira e Plástico "
            "são subtipos experimentais do KAYZAC."
        )

        especial_escolhido = st.selectbox(
            "🔬 Escolha uma classificação especial",
            list(TIPOS_ESPECIAIS_KAYZAC.keys()),
            format_func=lambda x: f"{TIPOS_ESPECIAIS_KAYZAC[x]['emoji']} {x}",
            key="biblioteca_especial_kayzac",
        )

        especial = TIPOS_ESPECIAIS_KAYZAC[especial_escolhido]

        st.markdown(
            f'<div class="library-card"><div class="library-title">'
            f'{especial["emoji"]} {especial_escolhido}</div>'
            f'<div class="library-subtitle">{especial["status"]}</div>'
            f'<b>Natureza:</b> {especial["natureza"]}<br>'
            f'<b>Origem:</b> {especial["origem"]}</div>',
            unsafe_allow_html=True,
        )

        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown("### 🕰️ Quando surgiu / começou a ser usado")
            st.write(especial["quando"])
        with h2:
            st.markdown("### 👤 Quem introduziu / popularizou")
            st.write(especial["quem"])
        with h3:
            st.markdown("### 🧠 Como o KAYZAC interpreta")
            st.write(especial["compatibilidade"])

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ⚔️ Vantagens teóricas")
            for item in especial["vantagens"]:
                st.write(f"✅ {item}")
        with c2:
            st.markdown("### 🛡️ Desvantagens / limitações")
            for item in especial["desvantagens"]:
                st.write(f"❌ {item}")

        st.divider()

        st.markdown("### 🐾 Pokémon mais compatíveis")
        st.caption(
            "Curadoria temática: são Pokémon cuja estética, lore, movimentos ou mecânicas "
            "mais combinam com a classificação. Não significa que tenham essa tipagem oficial."
        )
        if especial_escolhido == "Shadow":
            # Shadow Lugia e Shadow Mewtwo não são espécies/formas padrão da PokéAPI.
            # Por isso, a Biblioteca os renderiza diretamente pelas imagens locais
            # cadastradas no projeto, sem depender da API.
            mostrar_lista_shadow()
        elif especial_escolhido in {"Som", "Arma", "Vento", "Anime", "Cyber", "Cósmico", "Luz", "Areia", "Madeira", "Plástico", "Sangue", "Cristal", "Lua", "Sol", "Tempo", "DNA", "Espaço", "Radiação", "Realeza", "Aura", "Ninjas", "Samurais", "Sonhos", "Sorte", "Comida", "Garras e Dentes", "Animal", "Humanoide", "+18", "Brinquedos"} and especial.get("categorias_pokemon"):
            # Os subtipos temáticos com categorias possuem várias afinidades temáticas.
            # Cada categoria mantém o mesmo Mini-Dex robusto das demais entradas.
            emoji_categoria = {
                "Som": "🎵", "Arma": "⚔️", "Vento": "🌪️", "Anime": "🎬",
                "Cyber": "💻", "Cósmico": "🌌", "Luz": "☀️", "Areia": "🏜️",
                "Madeira": "🪵", "Plástico": "🧴", "Sangue": "🩸", "Cristal": "💎",
                "Lua": "🌙", "Sol": "☀️", "Tempo": "⏳", "DNA": "🧬",
                "Espaço": "🌀", "Radiação": "☢️", "Realeza": "👑", "Aura": "🌀",
                "Ninjas": "🥷", "Samurais": "🗡️", "Sonhos": "💭", "Sorte": "🍀",
                "Comida": "🍔", "Garras e Dentes": "🦷", "Animal": "🐾", "Humanoide": "🧍", "+18": "🔞", "Brinquedos": "🧸",
            }.get(especial_escolhido, "⭐")
            for categoria_nome, pokemon_lista in especial["categorias_pokemon"].items():
                st.markdown(f"### {categoria_nome}")
                cols = st.columns(6)
                for idx, pokemon_nome in enumerate(pokemon_lista):
                    with cols[idx % 6]:
                        with st.container(border=True):
                            slug_limpo = limpar_nome_curadoria(pokemon_nome)
                            e_pokemon_real = (
                                slug_limpo in pokemon_catalogo_nomes
                                or slug_limpo in IDS_FALLBACK_CURADORIA
                                or slug_limpo in ALIASES_CURADORIA_POKEMON
                            )

                            if e_pokemon_real:
                                mini = dados_mini_dex_curadoria(pokemon_nome)
                                if mini.get("sprite"):
                                    st.image(mini["sprite"], width=95)
                                titulo = pokemon_nome.split("(", 1)[0].strip()
                                st.markdown(f"**{titulo}**")
                                st.caption(
                                    f"{emoji_categoria} "
                                    f"{categoria_nome.split('/', 1)[-1].strip()}"
                                )
                                if st.button(
                                    "📖 Pokédex",
                                    key=f"especial_pokemon_{especial_escolhido}_{categoria_nome}_{idx}",
                                    use_container_width=True,
                                ):
                                    abrir_pokemon_na_pokedex(
                                        mini.get("slug") or slug_limpo
                                    )
                            else:
                                st.markdown(f"**{pokemon_nome}**")
                                st.caption("Associação temática")

            if especial_escolhido == "Anime" and especial.get("referencias_nostalgia"):
                st.divider()
                st.markdown("### 📺 Referências de nostalgia / arquétipos de anime")
                st.caption(
                    "Estas associações representam a leitura temática do KAYZAC — nostalgia, arquétipos "
                    "e energia shōnen — e não uma confirmação oficial de que um Pokémon foi inspirado por uma obra específica."
                )
                for referencia_nome, pokemon_ref in especial["referencias_nostalgia"].items():
                    st.markdown(f"#### {referencia_nome}")
                    cols_ref = st.columns(6)
                    for idx_ref, pokemon_nome_ref in enumerate(pokemon_ref):
                        with cols_ref[idx_ref % 6]:
                            with st.container(border=True):
                                slug_ref = limpar_nome_curadoria(pokemon_nome_ref)
                                real_ref = (
                                    slug_ref in pokemon_catalogo_nomes
                                    or slug_ref in IDS_FALLBACK_CURADORIA
                                    or slug_ref in ALIASES_CURADORIA_POKEMON
                                )
                                if real_ref:
                                    mini_ref = dados_mini_dex_curadoria(pokemon_nome_ref)
                                    if mini_ref.get("sprite"):
                                        st.image(mini_ref["sprite"], width=90)
                                    st.markdown(f"**{pokemon_nome_ref}**")
                                    if st.button(
                                        "📖 Pokédex",
                                        key=f"anime_ref_{referencia_nome}_{idx_ref}",
                                        use_container_width=True,
                                    ):
                                        abrir_pokemon_na_pokedex(
                                            mini_ref.get("slug") or slug_ref
                                        )
                                else:
                                    st.markdown(f"**{pokemon_nome_ref}**")
                                    st.caption("Associação temática")
        else:
            pokemon_lista = especial["pokemon"]
            cols = st.columns(6)
            for idx, pokemon_nome in enumerate(pokemon_lista):
                with cols[idx % 6]:
                    with st.container(border=True):
                        slug_limpo = limpar_nome_curadoria(pokemon_nome)
                        e_pokemon_real = slug_limpo in pokemon_catalogo_nomes or slug_limpo in IDS_FALLBACK_CURADORIA or slug_limpo in ALIASES_CURADORIA_POKEMON

                        if e_pokemon_real:
                            mini = dados_mini_dex_curadoria(pokemon_nome)

                            if mini.get("sprite"):
                                st.image(mini["sprite"], width=95)
                                titulo = pokemon_nome.split("(", 1)[0].strip()
                                st.markdown(f"**{titulo}**")
                                if st.button(
                                    "📖 Pokédex",
                                    key=f"especial_pokemon_{especial_escolhido}_{idx}",
                                    use_container_width=True,
                                ):
                                    abrir_pokemon_na_pokedex(
                                        mini.get("slug") or slug_limpo
                                    )
                            else:
                                st.markdown(f"**{pokemon_nome}**")
                                st.caption("Associação temática — arte não disponível")
                        else:
                            # Conceitos como Pokémon Eggs continuam textuais:
                            # não são espécies jogáveis com recurso Pokémon próprio.
                            st.markdown(f"**{pokemon_nome}**")
                            st.caption("Associação temática")

        st.markdown("### 🥊 Movimentos mais compatíveis")
        movimentos = especial["movimentos"]
        mov_cols = st.columns(4)
        for idx, movimento in enumerate(movimentos):
            with mov_cols[idx % 4]:
                st.markdown(f"🎯 **{movimento}**")

        st.markdown("### 🧬 Habilidades mais compatíveis")
        hab_cols = st.columns(4)
        for idx, habilidade in enumerate(especial["habilidades"]):
            with hab_cols[idx % 4]:
                st.markdown(f"✨ **{habilidade}**")

        st.markdown("### 🔗 Tipos / conceitos mais semelhantes")
        st.write(" • ".join(especial["semelhantes"]))

        st.warning(f"💡 {especial['nota']}")


# ============================================================
# 📝 NOTAS FINAIS
# ============================================================

st.divider()
st.caption(
    "Dados dinâmicos: PokéAPI. Os detalhes são carregados sob demanda e ficam em cache para reduzir requisições."
)
st.caption(
    "Conteúdo especial KAYZAC (como subtipos e a curadoria inicial de assinaturas) é separado dos dados oficiais."
)
