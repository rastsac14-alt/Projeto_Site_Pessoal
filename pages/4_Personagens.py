from pathlib import Path
import io
import re

import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="KAYZAC - Personagens Pokémon",
    page_icon="👥",
    layout="wide",
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

REGIOES = [
    "Todas",
    "Kanto",
    "Johto",
    "Hoenn",
    "Sinnoh",
    "Hisui",
    "Unova",
    "Kalos",
    "Alola",
    "Galar",
    "Paldea",
    "Anime",
]

CATEGORIAS = [
    "Todos",
    "Protagonista",
    "Rival",
    "Professor(a)",
    "Líder de Ginásio",
    "Elite Four",
    "Campeão",
    "Aliado",
    "Antagonista",
    "Organização / Vilão",
    "Personagem de Z-A",
]

# Dados estruturados para a página. A ideia é ampliar esta base ao longo do projeto.
PERSONAGENS = [
    # ========================================================
    # KANTO
    # ========================================================
    {"nome": "Red", "regiao": "Kanto", "categoria": "Protagonista", "jogo": "Red / Blue / Yellow / FireRed / LeafGreen", "papel": "Protagonista clássico de Kanto.", "ace": "pikachu"},
    {"nome": "Leaf", "regiao": "Kanto", "categoria": "Protagonista", "jogo": "FireRed / LeafGreen", "papel": "Protagonista jogável apresentada nos remakes.", "ace": "venusaur"},
    {"nome": "Blue", "regiao": "Kanto", "categoria": "Rival", "jogo": "Red / Blue / Yellow / FireRed / LeafGreen", "papel": "Rival de Red e Campeão da Liga em Kanto.", "ace": "pidgeot"},
    {"nome": "Professor Oak", "regiao": "Kanto", "categoria": "Professor(a)", "jogo": "Red / Blue / Yellow / FireRed / LeafGreen", "papel": "Professor responsável pelo estudo dos Pokémon e por iniciar a jornada de Kanto.", "ace": ""},
    {"nome": "Brock", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Pewter, especialista em Pokémon do tipo Pedra.", "ace": "onix"},
    {"nome": "Misty", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Cerulean, especialista em Água.", "ace": "starmie"},
    {"nome": "Lt. Surge", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Vermilion, especialista em Elétrico.", "ace": "raichu"},
    {"nome": "Erika", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Celadon, especialista em Grama.", "ace": "vileplume"},
    {"nome": "Koga", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder especialista em Veneno; em Johto também integra a Elite Four.", "ace": "weezing"},
    {"nome": "Sabrina", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Saffron, especialista em Psíquico.", "ace": "alakazam"},
    {"nome": "Blaine", "regiao": "Kanto", "categoria": "Líder de Ginásio", "jogo": "Kanto", "papel": "Líder do Ginásio de Cinnabar, especialista em Fogo.", "ace": "arcanine"},
    {"nome": "Giovanni", "regiao": "Kanto", "categoria": "Organização / Vilão", "jogo": "Kanto", "papel": "Chefe da Equipe Rocket e antigo líder do Ginásio de Viridian.", "ace": "rhyhorn"},
    {"nome": "Lorelei", "regiao": "Kanto", "categoria": "Elite Four", "jogo": "Liga Pokémon", "papel": "Membro da Elite Four especialista em Gelo.", "ace": "lapras"},
    {"nome": "Bruno", "regiao": "Kanto", "categoria": "Elite Four", "jogo": "Liga Pokémon", "papel": "Membro da Elite Four especialista em Lutador.", "ace": "machamp"},
    {"nome": "Agatha", "regiao": "Kanto", "categoria": "Elite Four", "jogo": "Liga Pokémon", "papel": "Membro da Elite Four especialista em Pokémon Fantasma.", "ace": "gengar"},
    {"nome": "Lance", "regiao": "Kanto", "categoria": "Campeão", "jogo": "Red / Blue / Yellow / FireRed / LeafGreen", "papel": "Mestre dos tipos Dragão e Campeão da Liga em Kanto na geração I/III.", "ace": "dragonite"},

    # ========================================================
    # JOHTO
    # ========================================================
    {"nome": "Ethan", "regiao": "Johto", "categoria": "Protagonista", "jogo": "Gold / Silver / Crystal / HeartGold / SoulSilver", "papel": "Protagonista jogável de Johto.", "ace": "typhlosion"},
    {"nome": "Lyra", "regiao": "Johto", "categoria": "Protagonista", "jogo": "HeartGold / SoulSilver", "papel": "Protagonista alternativa dos remakes de Johto.", "ace": "meganium"},
    {"nome": "Silver", "regiao": "Johto", "categoria": "Rival", "jogo": "Gold / Silver / Crystal / HeartGold / SoulSilver", "papel": "Rival de Johto e filho de Giovanni.", "ace": "weavile"},
    {"nome": "Professor Elm", "regiao": "Johto", "categoria": "Professor(a)", "jogo": "Gold / Silver / Crystal / HeartGold / SoulSilver", "papel": "Professor de Johto especializado em pesquisa de reprodução Pokémon.", "ace": ""},
    {"nome": "Falkner", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Violet City, especialista em Voador.", "ace": "pidgeotto"},
    {"nome": "Bugsy", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Azalea Town, especialista em Inseto.", "ace": "scyther"},
    {"nome": "Whitney", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Goldenrod City, especialista em Normal.", "ace": "miltank"},
    {"nome": "Morty", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Ecruteak City, especialista em Fantasma.", "ace": "gengar"},
    {"nome": "Jasmine", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Olivine City, especialista em Aço.", "ace": "steelix"},
    {"nome": "Pryce", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Mahogany Town, especialista em Gelo.", "ace": "piloswine"},
    {"nome": "Clair", "regiao": "Johto", "categoria": "Líder de Ginásio", "jogo": "Johto", "papel": "Líder de Blackthorn City, especialista em Dragão.", "ace": "kingdra"},
    {"nome": "Karen", "regiao": "Johto", "categoria": "Elite Four", "jogo": "Johto", "papel": "Membro da Elite Four especialista em Noturno.", "ace": "houndoom"},
    {"nome": "Lance", "regiao": "Johto", "categoria": "Campeão", "jogo": "Gold / Silver / Crystal / HeartGold / SoulSilver", "papel": "Campeão da Liga de Johto.", "ace": "dragonite"},
    {"nome": "Archer", "regiao": "Johto", "categoria": "Organização / Vilão", "jogo": "HeartGold / SoulSilver", "papel": "Líder da Equipe Rocket durante o retorno da organização em Johto.", "ace": "houndoom"},

    # ========================================================
    # HOENN
    # ========================================================
    {"nome": "Brendan", "regiao": "Hoenn", "categoria": "Protagonista", "jogo": "Ruby / Sapphire / Emerald / Omega Ruby / Alpha Sapphire", "papel": "Protagonista jogável de Hoenn.", "ace": "swampert"},
    {"nome": "May", "regiao": "Hoenn", "categoria": "Protagonista", "jogo": "Ruby / Sapphire / Emerald / Omega Ruby / Alpha Sapphire", "papel": "Protagonista alternativa e personagem importante da jornada de Hoenn.", "ace": "blaziken"},
    {"nome": "Wally", "regiao": "Hoenn", "categoria": "Rival", "jogo": "Ruby / Sapphire / Emerald / Omega Ruby / Alpha Sapphire", "papel": "Treinador que evolui ao longo da história e se torna um grande rival.", "ace": "gallade"},
    {"nome": "Professor Birch", "regiao": "Hoenn", "categoria": "Professor(a)", "jogo": "Hoenn", "papel": "Professor Pokémon de Hoenn especializado em comportamento Pokémon no campo.", "ace": ""},
    {"nome": "Roxanne", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Rustboro City, especialista em Pedra.", "ace": "nosepass"},
    {"nome": "Brawly", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Dewford Town, especialista em Lutador.", "ace": "hariyama"},
    {"nome": "Wattson", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Mauville City, especialista em Elétrico.", "ace": "manectric"},
    {"nome": "Flannery", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Lavaridge Town, especialista em Fogo.", "ace": "torkoal"},
    {"nome": "Norman", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Petalburg City, especialista em Normal.", "ace": "slaking"},
    {"nome": "Winona", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Líder de Fortree City, especialista em Voador.", "ace": "altaria"},
    {"nome": "Tate & Liza", "regiao": "Hoenn", "categoria": "Líder de Ginásio", "jogo": "Hoenn", "papel": "Dupla líder de Mossdeep City, especialistas em Psíquico.", "ace": "solrock"},
    {"nome": "Wallace", "regiao": "Hoenn", "categoria": "Campeão", "jogo": "Emerald / Omega Ruby / Alpha Sapphire", "papel": "Campeão de Hoenn em Emerald e figura central dos remakes.", "ace": "milotic"},
    {"nome": "Steven Stone", "regiao": "Hoenn", "categoria": "Campeão", "jogo": "Ruby / Sapphire / Emerald / Omega Ruby / Alpha Sapphire", "papel": "Campeão de Hoenn em Ruby/Sapphire e Emerald; especialista em Aço.", "ace": "metagross"},
    {"nome": "Maxie", "regiao": "Hoenn", "categoria": "Organização / Vilão", "jogo": "Ruby / Emerald / Omega Ruby", "papel": "Líder da Equipe Magma.", "ace": "camerupt"},
    {"nome": "Archie", "regiao": "Hoenn", "categoria": "Organização / Vilão", "jogo": "Sapphire / Emerald / Alpha Sapphire", "papel": "Líder da Equipe Aqua.", "ace": "sharpedo"},

    # ========================================================
    # SINNOH
    # ========================================================
    {"nome": "Lucas", "regiao": "Sinnoh", "categoria": "Protagonista", "jogo": "Diamond / Pearl / Platinum / Brilliant Diamond / Shining Pearl", "papel": "Protagonista jogável de Sinnoh.", "ace": "infernape"},
    {"nome": "Dawn", "regiao": "Sinnoh", "categoria": "Protagonista", "jogo": "Diamond / Pearl / Platinum / Brilliant Diamond / Shining Pearl", "papel": "Protagonista alternativa e parceira de pesquisa de Rowan.", "ace": "empoleon"},
    {"nome": "Barry", "regiao": "Sinnoh", "categoria": "Rival", "jogo": "Sinnoh", "papel": "Rival extremamente energético e filho de Palmer.", "ace": "empoleon"},
    {"nome": "Professor Rowan", "regiao": "Sinnoh", "categoria": "Professor(a)", "jogo": "Sinnoh", "papel": "Professor responsável pelo estudo da evolução Pokémon.", "ace": ""},
    {"nome": "Cynthia", "regiao": "Sinnoh", "categoria": "Campeão", "jogo": "Diamond / Pearl / Platinum / BDSP", "papel": "Campeã de Sinnoh, pesquisadora da mitologia e uma das treinadoras mais marcantes da série.", "ace": "garchomp"},
    {"nome": "Roark", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Oreburgh City, especialista em Pedra.", "ace": "cranidos"},
    {"nome": "Gardenia", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Eterna City, especialista em Grama.", "ace": "roserade"},
    {"nome": "Maylene", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Veilstone City, especialista em Lutador.", "ace": "lucario"},
    {"nome": "Crasher Wake", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Pastoria City, especialista em Água.", "ace": "floatzel"},
    {"nome": "Fantina", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Hearthome City, especialista em Fantasma.", "ace": "mismagius"},
    {"nome": "Byron", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Canalave City, especialista em Aço.", "ace": "bastiodon"},
    {"nome": "Candice", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Snowpoint City, especialista em Gelo.", "ace": "abomasnow"},
    {"nome": "Volkner", "regiao": "Sinnoh", "categoria": "Líder de Ginásio", "jogo": "Sinnoh", "papel": "Líder de Sunyshore City, especialista em Elétrico.", "ace": "luxray"},
    {"nome": "Cyrus", "regiao": "Sinnoh", "categoria": "Antagonista", "jogo": "Diamond / Pearl / Platinum", "papel": "Líder da Team Galactic e principal antagonista de Sinnoh.", "ace": "weavile"},
    {"nome": "Mars", "regiao": "Sinnoh", "categoria": "Organização / Vilão", "jogo": "Sinnoh", "papel": "Comandante da Team Galactic.", "ace": "purugly"},
    {"nome": "Jupiter", "regiao": "Sinnoh", "categoria": "Organização / Vilão", "jogo": "Sinnoh", "papel": "Comandante da Team Galactic.", "ace": "skuntank"},
    {"nome": "Saturn", "regiao": "Sinnoh", "categoria": "Organização / Vilão", "jogo": "Sinnoh", "papel": "Comandante da Team Galactic.", "ace": "toxicroak"},

    # ========================================================
    # HISUI
    # ========================================================
    {"nome": "Rei", "regiao": "Hisui", "categoria": "Protagonista", "jogo": "Legends: Arceus", "papel": "Uma das identidades possíveis do protagonista de Hisui.", "ace": "samurott-hisui"},
    {"nome": "Akari", "regiao": "Hisui", "categoria": "Protagonista", "jogo": "Legends: Arceus", "papel": "Uma das identidades possíveis do protagonista de Hisui.", "ace": "decidueye-hisui"},
    {"nome": "Professor Laventon", "regiao": "Hisui", "categoria": "Professor(a)", "jogo": "Legends: Arceus", "papel": "Pesquisador da Expedição Galaxy e responsável pelo estudo da Pokédex de Hisui.", "ace": ""},
    {"nome": "Adaman", "regiao": "Hisui", "categoria": "Aliado", "jogo": "Legends: Arceus", "papel": "Líder do Diamond Clan.", "ace": "leafeon"},
    {"nome": "Irida", "regiao": "Hisui", "categoria": "Aliado", "jogo": "Legends: Arceus", "papel": "Líder do Pearl Clan.", "ace": "glaceon"},
    {"nome": "Commander Kamado", "regiao": "Hisui", "categoria": "Aliado", "jogo": "Legends: Arceus", "papel": "Comandante da Galaxy Expedition Team.", "ace": ""},
    {"nome": "Volo", "regiao": "Hisui", "categoria": "Antagonista", "jogo": "Legends: Arceus", "papel": "Mercador e personagem central da trama envolvendo a mitologia de Sinnoh.", "ace": "togekiss"},
    {"nome": "Cogita", "regiao": "Hisui", "categoria": "Aliado", "jogo": "Legends: Arceus", "papel": "Pesquisadora que guarda conhecimentos sobre a história antiga de Hisui.", "ace": ""},

    # ========================================================
    # UNOVA
    # ========================================================
    {"nome": "Hilbert", "regiao": "Unova", "categoria": "Protagonista", "jogo": "Black / White", "papel": "Protagonista jogável de Unova.", "ace": "samurott"},
    {"nome": "Hilda", "regiao": "Unova", "categoria": "Protagonista", "jogo": "Black / White", "papel": "Protagonista alternativa de Unova.", "ace": "serperior"},
    {"nome": "Nate", "regiao": "Unova", "categoria": "Protagonista", "jogo": "Black 2 / White 2", "papel": "Protagonista jogável das sequências.", "ace": "samurott"},
    {"nome": "Rosa", "regiao": "Unova", "categoria": "Protagonista", "jogo": "Black 2 / White 2", "papel": "Protagonista alternativa das sequências.", "ace": "emboar"},
    {"nome": "Bianca", "regiao": "Unova", "categoria": "Aliado", "jogo": "Black / White / Black 2 / White 2", "papel": "Amiga do protagonista e pesquisadora ligada à Professora Juniper.", "ace": "musharna"},
    {"nome": "Cheren", "regiao": "Unova", "categoria": "Rival", "jogo": "Black / White / Black 2 / White 2", "papel": "Rival e, mais tarde, Líder de Ginásio em Black 2/White 2.", "ace": "stoutland"},
    {"nome": "Hugh", "regiao": "Unova", "categoria": "Rival", "jogo": "Black 2 / White 2", "papel": "Rival de Black 2/White 2 movido por uma busca pessoal.", "ace": "samurott"},
    {"nome": "Professor Juniper", "regiao": "Unova", "categoria": "Professor(a)", "jogo": "Black / White", "papel": "Professora de Unova que pesquisa Pokémon e envia o protagonista em sua jornada.", "ace": ""},
    {"nome": "N", "regiao": "Unova", "categoria": "Antagonista", "jogo": "Black / White / Black 2 / White 2", "papel": "Treinador central da narrativa de Team Plasma e um dos personagens mais importantes de Unova.", "ace": "zoroark"},
    {"nome": "Ghetsis", "regiao": "Unova", "categoria": "Antagonista", "jogo": "Black / White / Black 2 / White 2", "papel": "Um dos líderes da Team Plasma e principal antagonista.", "ace": "hydreigon"},
    {"nome": "Alder", "regiao": "Unova", "categoria": "Campeão", "jogo": "Black / White", "papel": "Campeão da Liga de Unova em Black/White.", "ace": "volcarona"},
    {"nome": "Iris", "regiao": "Unova", "categoria": "Campeão", "jogo": "Black 2 / White 2", "papel": "Campeã da Liga de Unova em Black 2/White 2.", "ace": "haxorus"},
    {"nome": "Cilan", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Black / White", "papel": "Um dos líderes de Striaton City e especialista em Grama.", "ace": "pansage"},
    {"nome": "Lenora", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Black / White", "papel": "Líder de Nacrene City, especialista em Normal.", "ace": "watchog"},
    {"nome": "Elesa", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Unova", "papel": "Líder de Nimbasa City, especialista em Elétrico.", "ace": "zebstrika"},
    {"nome": "Clay", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Unova", "papel": "Líder de Driftveil City, especialista em Terra.", "ace": "excadrill"},
    {"nome": "Skyla", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Unova", "papel": "Líder de Mistralton City, especialista em Voador.", "ace": "swanna"},
    {"nome": "Drayden", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Black / White", "papel": "Líder de Opelucid City, especialista em Dragão em Black.", "ace": "haxorus"},
    {"nome": "Roxie", "regiao": "Unova", "categoria": "Líder de Ginásio", "jogo": "Black 2 / White 2", "papel": "Líder de Virbank City, especialista em Veneno.", "ace": "scolipede"},

    # ========================================================
    # KALOS
    # ========================================================
    {"nome": "Calem", "regiao": "Kalos", "categoria": "Protagonista", "jogo": "X / Y", "papel": "Protagonista jogável de Kalos.", "ace": "chesnaught"},
    {"nome": "Serena", "regiao": "Kalos", "categoria": "Protagonista", "jogo": "X / Y", "papel": "Protagonista alternativa de Kalos.", "ace": "delphox"},
    {"nome": "Shauna", "regiao": "Kalos", "categoria": "Rival", "jogo": "X / Y", "papel": "Amiga e companheira do protagonista em Kalos.", "ace": "goodra"},
    {"nome": "Tierno", "regiao": "Kalos", "categoria": "Rival", "jogo": "X / Y", "papel": "Treinador apaixonado por dança.", "ace": "crawdaunt"},
    {"nome": "Trevor", "regiao": "Kalos", "categoria": "Rival", "jogo": "X / Y", "papel": "Colecionador e pesquisador que busca completar a Pokédex.", "ace": "florges"},
    {"nome": "Professor Sycamore", "regiao": "Kalos", "categoria": "Professor(a)", "jogo": "X / Y", "papel": "Professor de Kalos que pesquisa a evolução Pokémon.", "ace": ""},
    {"nome": "Diantha", "regiao": "Kalos", "categoria": "Campeão", "jogo": "X / Y", "papel": "Campeã de Kalos e estrela de cinema.", "ace": "gardevoir"},
    {"nome": "Viola", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Santalune City, especialista em Inseto.", "ace": "vivillon"},
    {"nome": "Grant", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Cyllage City, especialista em Pedra.", "ace": "tyrunt"},
    {"nome": "Korrina", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Shalour City, especialista em Lutador e figura central da Mega Evolução.", "ace": "lucario"},
    {"nome": "Ramos", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Coumarine City, especialista em Grama.", "ace": "gogoat"},
    {"nome": "Clemont", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Lumiose City, inventor e especialista em Elétrico.", "ace": "heliolisk"},
    {"nome": "Wulfric", "regiao": "Kalos", "categoria": "Líder de Ginásio", "jogo": "Kalos", "papel": "Líder de Snowbelle City, especialista em Gelo.", "ace": "avalugg"},
    {"nome": "AZ", "regiao": "Kalos", "categoria": "Aliado", "jogo": "X / Y / Legends: Z-A", "papel": "Figura lendária da história de Kalos, ligada à antiga guerra e à Floette eterna.", "ace": "floette"},
    {"nome": "Lysandre", "regiao": "Kalos", "categoria": "Antagonista", "jogo": "X / Y", "papel": "Líder da Team Flare e principal antagonista de Kalos.", "ace": "pyroar"},
    {"nome": "Mable", "regiao": "Kalos", "categoria": "Personagem de Z-A", "jogo": "Legends: Z-A", "papel": "Diretora em exercício do Laboratório de Pesquisa Pokémon em Lumiose City.", "ace": ""},
    {"nome": "Urbain / Taunie", "regiao": "Kalos", "categoria": "Personagem de Z-A", "jogo": "Legends: Z-A", "papel": "Companheiro encontrado no Hotel Z; o personagem depende da aparência escolhida pelo jogador.", "ace": ""},
    {"nome": "Lida", "regiao": "Kalos", "categoria": "Personagem de Z-A", "jogo": "Legends: Z-A", "papel": "Membro da Team MZ e estudante de dança que busca se tornar dançarina profissional.", "ace": ""},
    {"nome": "Naveen", "regiao": "Kalos", "categoria": "Personagem de Z-A", "jogo": "Legends: Z-A", "papel": "Membro da Team MZ que pretende se tornar designer de moda.", "ace": ""},

    # ========================================================
    # ALOLA
    # ========================================================
    {"nome": "Elio", "regiao": "Alola", "categoria": "Protagonista", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Protagonista masculino de Alola.", "ace": "incineroar"},
    {"nome": "Selene", "regiao": "Alola", "categoria": "Protagonista", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Protagonista feminina de Alola.", "ace": "primarina"},
    {"nome": "Hau", "regiao": "Alola", "categoria": "Rival", "jogo": "Alola", "papel": "Rival e grande amigo do protagonista.", "ace": "raichu-alola"},
    {"nome": "Gladion", "regiao": "Alola", "categoria": "Rival", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Rival e membro ligado à Aether Foundation e aos Ultra Recon Squad em versões específicas.", "ace": "silvally"},
    {"nome": "Lillie", "regiao": "Alola", "categoria": "Aliado", "jogo": "Alola", "papel": "Uma das personagens centrais da história de Alola e próxima de Nebby.", "ace": "clefairy"},
    {"nome": "Professor Kukui", "regiao": "Alola", "categoria": "Professor(a)", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Professor de Alola e fundador da Liga Pokémon da região.", "ace": "incineroar"},
    {"nome": "Professor Burnet", "regiao": "Alola", "categoria": "Professor(a)", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Pesquisadora ligada à Fundação Aether, especializada em Ultra Wormholes e esposa do Professor Kukui.", "ace": ""},
    {"nome": "Samson Oak", "regiao": "Alola", "categoria": "Professor(a)", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Diretor da Escola Pokémon de Alola e primo do Professor Samuel Oak.", "ace": ""},
    {"nome": "Ilima", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Capitão de prova de Melemele e especialista em Pokémon do tipo Normal.", "ace": "gumshoos"},
    {"nome": "Kiawe", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Capitão de prova de Akala, especialista em Fogo e dançarino tradicional de Alola.", "ace": "marowak-alola"},
    {"nome": "Mallow", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Capitã de prova de Akala, apaixonada por culinária e especialista em Grama.", "ace": "tsareena"},
    {"nome": "Lana", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Capitã de prova de Akala, especialista em Água e conhecida por suas histórias de pescaria.", "ace": "araquanid"},
    {"nome": "Sophocles", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Capitão de prova de Ula'ula, inventor e especialista em Elétrico.", "ace": "togedemaru"},
    {"nome": "Hala", "regiao": "Alola", "categoria": "Aliado", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Kahuna da Ilha Melemele e especialista em Lutador.", "ace": "crabominable"},
    {"nome": "Olivia", "regiao": "Alola", "categoria": "Aliado", "jogo": "Alola", "papel": "Kahuna da Ilha Akala e especialista em Pedra.", "ace": "lycanroc"},
    {"nome": "Nanu", "regiao": "Alola", "categoria": "Aliado", "jogo": "Alola", "papel": "Kahuna de Ula'ula e especialista em Noturno.", "ace": "krookodile"},
    {"nome": "Hapu", "regiao": "Alola", "categoria": "Aliado", "jogo": "Alola", "papel": "Kahuna de Poni e especialista em Terra.", "ace": "mudsdale"},
    {"nome": "Acerola", "regiao": "Alola", "categoria": "Elite Four", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Especialista em Fantasma e membro da Elite Four de Alola.", "ace": "palossand"},
    {"nome": "Guzma", "regiao": "Alola", "categoria": "Antagonista", "jogo": "Alola", "papel": "Chefe da Team Skull.", "ace": "golisopod"},
    {"nome": "Lusamine", "regiao": "Alola", "categoria": "Antagonista", "jogo": "Sun / Moon / Ultra Sun / Ultra Moon", "papel": "Presidente da Aether Foundation e figura central dos conflitos de Alola.", "ace": "milotic"},
    {"nome": "Plumeria", "regiao": "Alola", "categoria": "Organização / Vilão", "jogo": "Alola", "papel": "Administradora da Team Skull e irmã mais velha de outros membros.", "ace": "salazzle"},
    
    # ========================================================
    # GALAR
    # ========================================================
    {"nome": "Victor", "regiao": "Galar", "categoria": "Protagonista", "jogo": "Sword / Shield", "papel": "Protagonista masculino de Galar.", "ace": "cinderace"},
    {"nome": "Gloria", "regiao": "Galar", "categoria": "Protagonista", "jogo": "Sword / Shield", "papel": "Protagonista feminina de Galar.", "ace": "rillaboom"},
    {"nome": "Hop", "regiao": "Galar", "categoria": "Rival", "jogo": "Sword / Shield", "papel": "Rival, irmão mais novo de Leon e companheiro de jornada.", "ace": "dubwool"},
    {"nome": "Bede", "regiao": "Galar", "categoria": "Rival", "jogo": "Sword / Shield", "papel": "Rival de personalidade forte que passa por mudanças ao longo da história.", "ace": "hatterene"},
    {"nome": "Marnie", "regiao": "Galar", "categoria": "Rival", "jogo": "Sword / Shield", "papel": "Rival e treinadora de Spikemuth apoiada pelos Team Yell.", "ace": "morpeko"},
    {"nome": "Professor Magnolia", "regiao": "Galar", "categoria": "Professor(a)", "jogo": "Sword / Shield", "papel": "Professora ligada ao estudo do fenômeno Dynamax.", "ace": ""},
    {"nome": "Sonia", "regiao": "Galar", "categoria": "Aliado", "jogo": "Sword / Shield", "papel": "Pesquisadora da história de Galar e neta de Magnolia.", "ace": "yamper"},
    {"nome": "Leon", "regiao": "Galar", "categoria": "Campeão", "jogo": "Sword / Shield", "papel": "Campeão invicto de Galar e irmão mais velho de Hop.", "ace": "charizard"},
    {"nome": "Milo", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword / Shield", "papel": "Líder de Turffield, especialista em Grama.", "ace": "eldegoss"},
    {"nome": "Nessa", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword / Shield", "papel": "Líder de Hulbury, especialista em Água.", "ace": "drednaw"},
    {"nome": "Kabu", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword / Shield", "papel": "Líder de Motostoke, especialista em Fogo.", "ace": "centiskorch"},
    {"nome": "Bea", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword", "papel": "Líder de Stow-on-Side, especialista em Lutador.", "ace": "machamp"},
    {"nome": "Allister", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Shield", "papel": "Líder de Stow-on-Side, especialista em Fantasma.", "ace": "gengar"},
    {"nome": "Piers", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword / Shield", "papel": "Líder de Spikemuth e especialista em Noturno.", "ace": "obstagoon"},
    {"nome": "Raihan", "regiao": "Galar", "categoria": "Líder de Ginásio", "jogo": "Sword / Shield", "papel": "Líder de Hammerlocke, especialista em Dragão e estratégias de clima.", "ace": "duraludon"},
    {"nome": "Rose", "regiao": "Galar", "categoria": "Antagonista", "jogo": "Sword / Shield", "papel": "Presidente da Macro Cosmos e peça central do conflito envolvendo energia de Galar.", "ace": "copperajah"},
    {"nome": "Oleana", "regiao": "Galar", "categoria": "Organização / Vilão", "jogo": "Sword / Shield", "papel": "Diretora da Macro Cosmos e braço direito de Rose.", "ace": "garbodor"},
    
    # ========================================================
    # PALDEA
    # ========================================================
    {"nome": "Florian", "regiao": "Paldea", "categoria": "Protagonista", "jogo": "Scarlet / Violet", "papel": "Protagonista masculino de Paldea.", "ace": "quaquaval"},
    {"nome": "Juliana", "regiao": "Paldea", "categoria": "Protagonista", "jogo": "Scarlet / Violet", "papel": "Protagonista feminina de Paldea.", "ace": "meowscarada"},
    {"nome": "Nemona", "regiao": "Paldea", "categoria": "Rival", "jogo": "Scarlet / Violet", "papel": "Rival e Treinadora de alto nível apaixonada por batalhas.", "ace": "lycanroc"},
    {"nome": "Arven", "regiao": "Paldea", "categoria": "Rival", "jogo": "Scarlet / Violet", "papel": "Companheiro ligado à Path of Legends e à história de seus pais.", "ace": "mabosstiff"},
    {"nome": "Penny", "regiao": "Paldea", "categoria": "Rival", "jogo": "Scarlet / Violet", "papel": "Companheira central de Starfall Street e responsável pelo plano Cassiopeia.", "ace": "eevee"},
    {"nome": "Clavell", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Diretor da Naranja/Uva Academy e figura importante na investigação da Team Star.", "ace": "quaquaval"},
    {"nome": "Jacq", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professor responsável por tecnologia ligada à Pokédex.", "ace": ""},
    {"nome": "Professor Sada", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Pokémon Scarlet", "papel": "Professora responsável pelo Laboratório da Área Zero em Scarlet e por pesquisas sobre o passado de Paldea.", "ace": ""},
    {"nome": "Professor Turo", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Pokémon Violet", "papel": "Professor responsável pelo Laboratório da Área Zero em Violet e por pesquisas sobre o futuro de Paldea.", "ace": ""},
    {"nome": "Geeta", "regiao": "Paldea", "categoria": "Campeão", "jogo": "Scarlet / Violet", "papel": "Campeã da Liga de Paldea e presidente da Pokémon League.", "ace": "glimmora"},
    {"nome": "Katy", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder do Ginásio de Cortondo e especialista em Pokémon do tipo Inseto.", "ace": "teddiursa"},
    {"nome": "Ryme", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder do Ginásio de Montenevera, rapper e especialista em Pokémon do tipo Fantasma.", "ace": ""},
    {"nome": "Tulip", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder do Ginásio de Alfornada e especialista em Pokémon do tipo Psíquico.", "ace": "espathra"},
    {"nome": "Rika", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "Scarlet / Violet", "papel": "Membro da Elite Four e braço direito de Geeta.", "ace": "clodsire"},
    {"nome": "Poppy", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "Scarlet / Violet", "papel": "Membro da Elite Four especialista em Aço.", "ace": "tinkaton"},
    {"nome": "Larry", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "Scarlet / Violet", "papel": "Membro da Elite Four e também Líder do Ginásio de Medali.", "ace": "flamigo"},
    {"nome": "Hassel", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "Scarlet / Violet", "papel": "Membro da Elite Four especialista em Dragão.", "ace": "baxcalibur"},
    {"nome": "Brassius", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder de Artazon, especialista em Grama.", "ace": "sudowoodo"},
    {"nome": "Iono", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder de Levincia, especialista em Elétrico e streamer.", "ace": "bellibolt"},
    {"nome": "Kofu", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder de Cascarrafa, especialista em Água.", "ace": "veluza"},
    {"nome": "Grusha", "regiao": "Paldea", "categoria": "Líder de Ginásio", "jogo": "Scarlet / Violet", "papel": "Líder de Glaseado, especialista em Gelo.", "ace": "cetitan"},
    {"nome": "Giacomo", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Scarlet / Violet", "papel": "Chefe da Team Star associado ao grupo Dark Crew.", "ace": "mabosstiff"},
    {"nome": "Mela", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Scarlet / Violet", "papel": "Chefe da Team Star associado ao grupo Fire Crew.", "ace": "torkoal"},
    {"nome": "Atticus", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Scarlet / Violet", "papel": "Chefe da Team Star associado ao grupo Poison Crew.", "ace": "revavroom"},
    {"nome": "Ortega", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Scarlet / Violet", "papel": "Chefe da Team Star associado ao grupo Fairy Crew.", "ace": "wugtrio"},
    {"nome": "Eri", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Scarlet / Violet", "papel": "Chefe da Team Star associado ao grupo Fighting Crew.", "ace": "annihilape"},
    # DLC The Teal Mask / Kitakami
    {"nome": "Carmine", "regiao": "Paldea", "categoria": "Rival", "jogo": "The Teal Mask", "papel": "Treinadora de Kitakami e irmã mais velha de Kieran, que acompanha o protagonista durante a visita à região.", "ace": "sinistcha"},
    {"nome": "Kieran", "regiao": "Paldea", "categoria": "Rival", "jogo": "The Teal Mask / The Indigo Disk", "papel": "Treinador de Kitakami e irmão mais novo de Carmine, cuja relação com o protagonista muda ao longo das expansões.", "ace": "hydrapple"},
    {"nome": "Perrin", "regiao": "Paldea", "categoria": "Aliado", "jogo": "The Teal Mask", "papel": "Fotógrafa Pokémon de Kitakami que ajuda o protagonista em uma investigação sobre Pokémon raros.", "ace": ""},
    # DLC The Indigo Disk / Blueberry Academy
    {"nome": "Briar", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "The Indigo Disk", "papel": "Professora da Blueberry Academy que pesquisa a Área Zero, Terapagos e os mistérios do mundo Pokémon.", "ace": ""},
    {"nome": "Cyrano", "regiao": "Paldea", "categoria": "Aliado", "jogo": "The Indigo Disk", "papel": "Diretor da Blueberry Academy e responsável pelo convite ao intercâmbio escolar.", "ace": ""},
    {"nome": "Lacey", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "The Indigo Disk", "papel": "Integrante da Elite Quatro da Blueberry Academy e especialista em Pokémon do tipo Fada.", "ace": "excadrill"},
    {"nome": "Crispin", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "The Indigo Disk", "papel": "Integrante da Elite Quatro da Blueberry Academy e especialista em Pokémon do tipo Fogo.", "ace": ""},
    {"nome": "Amarys", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "The Indigo Disk", "papel": "Integrante da Elite Quatro da Blueberry Academy e especialista em Pokémon do tipo Aço.", "ace": "skarmory"},
    {"nome": "Drayton", "regiao": "Paldea", "categoria": "Elite Four", "jogo": "The Indigo Disk", "papel": "Integrante da Elite Quatro da Blueberry Academy, especialista em Dragão e neto de Drayden.", "ace": "archaludon"},
    # Professores da Naranja / Uva Academy
    {"nome": "Dendra", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professora de Educação Física da academia, apaixonada por batalhas e treinamento Pokémon.", "ace": ""},
    {"nome": "Miriam", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Enfermeira da academia e professora de Biologia substituta.", "ace": ""},
    {"nome": "Raifort", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professora de História que pesquisa os tesouros e os mistérios antigos de Paldea.", "ace": ""},
    {"nome": "Salvatore", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professor de Línguas da academia, conhecido por seu carinho pelos Pokémon.", "ace": ""},
    {"nome": "Tyme", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professora de Matemática e antiga Líder de Ginásio de Montenevera.", "ace": ""},
    {"nome": "Saguaro", "regiao": "Paldea", "categoria": "Professor(a)", "jogo": "Scarlet / Violet", "papel": "Professor de Economia Doméstica da academia.", "ace": ""},
]


# ============================================================
# PERSONAGENS EXCLUSIVOS DO ANIME
# ============================================================
# Origem "Anime" separa esta coleção dos personagens cadastrados pelos jogos.
# arte_url só é preenchida quando há uma imagem individual identificada em
# fonte que identifica a imagem como arte oficial do jogo ou da animação; nunca usamos busca genérica.
PERSONAGENS_ANIME = [
    {"nome": "Ash Ketchum", "regiao": "Anime", "categoria": "Protagonista", "jogo": "Pokémon the Series / Jornadas", "papel": "Protagonista da série animada por mais de duas décadas; viaja com Pikachu em busca do sonho de se tornar Mestre Pokémon.", "ace": "pikachu", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/c/cd/Ash_JN.png"},
    {"nome": "Goh", "regiao": "Anime", "categoria": "Protagonista", "jogo": "Pokémon Jornadas", "papel": "Companheiro de Ash em Jornadas; sonha em capturar todos os Pokémon e pesquisar Mew.", "ace": "cinderace", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/2/25/Goh_JN.png"},
    {"nome": "Chloe Cerise", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Jornadas", "papel": "Amiga de infância de Goh e filha do Professor Cerise; sua jornada acompanha Eevee e suas possibilidades de evolução.", "ace": "eevee", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/b/b7/Chloe_JN.png"},
    {"nome": "Professor Cerise", "regiao": "Anime", "categoria": "Professor(a)", "jogo": "Pokémon Jornadas", "papel": "Pesquisador que dirige o Laboratório Cerise e convida Ash e Goh para atuar como pesquisadores oficiais.", "ace": "", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/d/d8/Professor_Cerise_JN.png"},
    {"nome": "Jessie", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon the Series", "papel": "Integrante da Equipe Rocket que persegue Pikachu ao lado de James e Meowth.", "ace": "wobbuffet", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/0/0d/Jessie_JN.png"},
    {"nome": "James", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon the Series", "papel": "Integrante da Equipe Rocket e parceiro de Jessie nas tentativas de capturar Pikachu.", "ace": "inkay", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/1/19/James_JN.png"},
    {"nome": "Meowth (Equipe Rocket)", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon the Series", "papel": "Meowth falante da Equipe Rocket, capaz de conversar com humanos e integrante da equipe de Jessie e James.", "ace": "meowth", "origem": "Anime", "arte_url": "https://archives.bulbagarden.net/media/upload/a/aa/052Meowth_JN_anime.png"},
    {"nome": "Tracey Sketchit", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon the Series: The Johto Journeys", "papel": "Observador Pokémon que viaja com Ash e Misty nas Ilhas Laranja e depois trabalha com Professor Oak.", "ace": "scyther", "origem": "Anime"},
    {"nome": "Max", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon the Series: Advanced", "papel": "Irmão mais novo de May; acompanha Ash e seus amigos durante a jornada por Hoenn e Kanto.", "ace": "", "origem": "Anime"},
    {"nome": "Ritchie", "regiao": "Anime", "categoria": "Rival", "jogo": "Pokémon the Series", "papel": "Treinador que conhece Ash na Liga Índigo e se torna um de seus rivais mais lembrados.", "ace": "pikachu", "origem": "Anime"},
    {"nome": "Paul", "regiao": "Anime", "categoria": "Rival", "jogo": "Pokémon the Series: Diamond and Pearl", "papel": "Rival de Ash em Sinnoh, conhecido por seu estilo rigoroso de treinamento e por seu Electivire.", "ace": "electivire", "origem": "Anime"},
    {"nome": "Alain", "regiao": "Anime", "categoria": "Rival", "jogo": "Pokémon the Series: XY", "papel": "Treinador focado em Mega Evolução que se torna um dos grandes adversários de Ash em Kalos.", "ace": "charizard", "origem": "Anime"},
    {"nome": "Mairin", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Mega Evolution Specials / XY", "papel": "Companheira de Alain nos especiais de Mega Evolução e treinadora de Chespin.", "ace": "chespin", "origem": "Anime"},
    {"nome": "Koko", "regiao": "Anime", "categoria": "Protagonista", "jogo": "Pokémon the Movie: Secrets of the Jungle", "papel": "Garoto criado por Dada Zarude na Floresta de Okoya, cuja amizade com Ash transforma sua visão sobre si mesmo.", "ace": "zarude", "origem": "Anime", "arte_url": "https://zarude.pokemon.com/assets/images/characters/koko.png"},
    {"nome": "Liko", "regiao": "Anime", "categoria": "Protagonista", "jogo": "Pokémon Horizons", "papel": "Protagonista de Pokémon Horizons, estudante de Paldea que parte em uma aventura com Sprigatito e seu misterioso pingente.", "ace": "sprigatito", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/liko-sprigatito.png"},
    {"nome": "Roy", "regiao": "Anime", "categoria": "Protagonista", "jogo": "Pokémon Horizons", "papel": "Protagonista de Pokémon Horizons, garoto de uma ilha de Kanto que viaja com Fuecoco e uma Poké Bola Ancestral.", "ace": "fuecoco", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/roy-fuecoco.png"},
    {"nome": "Friede", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Líder dos Tackleadores Aéreos; aventureiro e habilidoso em batalhas, acompanhado por Charizard e Capitão Pikachu.", "ace": "charizard", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/friede-captain-pikachu.png"},
    {"nome": "Dot", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Gênio da computação dos Tackleadores Aéreos e sobrinha de Murdock; viaja com Quaxly.", "ace": "quaxly", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/dot-quaxly.png"},
    {"nome": "Murdock", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Cozinheiro dos Tackleadores Aéreos, conhecido por cuidar do grupo e por sua parceria com Rockruff.", "ace": "rockruff", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/murdock-rockruff.png"},
    {"nome": "Orla", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Mecânica e engenheira responsável pela manutenção do dirigível Brave Olivine; sua parceira é Metagross.", "ace": "metagross", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/orla-metagross.png"},
    {"nome": "Mollie", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Responsável pelos cuidados médicos dos Pokémon a bordo do Brave Olivine, com Chansey como parceira.", "ace": "chansey", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/mollie-chansey.png"},
    {"nome": "Ludlow", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Pescador experiente e integrante dos Tackleadores Aéreos; viaja com Quagsire.", "ace": "quagsire", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/ludlow-quagsuire.png"},
    {"nome": "Amethio", "regiao": "Anime", "categoria": "Antagonista", "jogo": "Pokémon Horizons", "papel": "Integrante dos Exploradores interessado no pingente de Liko; seu parceiro Pokémon é Ceruledge.", "ace": "ceruledge", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/amethio-ceruledge.png"},
    {"nome": "Zirc", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "Membro dos Exploradores que responde a Amethio e costuma demonstrar a força de Rhydon.", "ace": "rhydon", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/zirc-rhydon.png"},
    {"nome": "Onia", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "Integrante dos Exploradores que trabalha com Amethio e tem Golduck como parceiro.", "ace": "golduck", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/onia-golduck.png"},
    {"nome": "Hamber", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "Membro veterano dos Exploradores que supervisiona operações ao lado de Dusknoir.", "ace": "dusknoir", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/hamber.png"},
    {"nome": "Spinel", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "General dos Exploradores que manipula comunicações e tenta roubar o pingente de Liko.", "ace": "umbreon", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/spinell.png"},
    {"nome": "Sidian", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "General dos Exploradores, conhecido por sua postura séria e por lutar ao lado de Garganacl.", "ace": "garganacl", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/sidan.png"},
    {"nome": "Coral", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "General dos Exploradores de personalidade impulsiva e brincalhona, parceira de Glalie.", "ace": "glalie", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/coral.png"},
    {"nome": "Chalce", "regiao": "Anime", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizons", "papel": "General dos Exploradores de postura calma e crítica, que batalha ao lado de Medicham.", "ace": "medicham", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/chalce.png"},
    {"nome": "Nidothing", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizons", "papel": "Streamer popular que usa uma fantasia para esconder sua identidade e é admirada por Liko.", "ace": "", "origem": "Anime", "arte_url": "https://horizons.pokemon.com/_images/home/character-assets/nidothing.png"},
]

PERSONAGENS.extend(PERSONAGENS_ANIME)


# ============================================================
# FUNÇÕES
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_pokemon(nome: str):
    if not nome:
        return None
    try:
        import requests

        resposta = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{nome}",
            timeout=8,
        )
        resposta.raise_for_status()
        return resposta.json()
    except Exception:
        return None


def nome_bonito(nome: str) -> str:
    if not nome:
        return ""
    return (
        nome.replace("-", " ")
        .replace("_", " ")
        .title()
        .replace("Hisui", "de Hisui")
        .replace("Alola", "de Alola")
    )


@st.cache_data(ttl=86400, show_spinner=False)
def obter_catalogo_ken_sugimori():
    """Carrega somente arquivos da categoria oficial Ken Sugimori character artwork."""
    endpoint = "https://archives.bulbagarden.net/w/api.php"
    headers = {
        "User-Agent": "KAYZAC-Master-Pokemon/3.0 (character artwork catalog)",
        "Accept": "application/json",
    }
    parametros = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": "Category:Ken_Sugimori_character_artwork",
        "gcmtype": "file",
        "gcmlimit": 500,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "format": "json",
        "formatversion": 2,
    }
    arquivos = []

    # A categoria contém algumas centenas de arquivos. O continue evita que
    # futuras expansões do catálogo deixem personagens sem imagem.
    for _ in range(4):
        try:
            resposta = requests.get(endpoint, params=parametros, timeout=(4, 12), headers=headers)
            resposta.raise_for_status()
            dados = resposta.json()
        except Exception:
            break

        paginas = dados.get("query", {}).get("pages", [])
        if isinstance(paginas, dict):
            paginas = list(paginas.values())
        if not isinstance(paginas, list):
            break

        for pagina in paginas:
            infos = pagina.get("imageinfo", [])
            if not infos or not isinstance(infos[0], dict):
                continue
            info = infos[0]
            url = info.get("url")
            mime = str(info.get("mime", "")).lower()
            titulo = str(pagina.get("title", ""))
            if url and mime.startswith("image/") and titulo:
                arquivos.append({"titulo": titulo, "url": url, "mime": mime})

        continuacao = dados.get("continue", {})
        if not continuacao:
            break
        parametros.update(continuacao)

    return arquivos


def normalizar_titulo_arquivo(valor: str) -> str:
    import unicodedata

    valor = unicodedata.normalize("NFKD", str(valor or ""))
    valor = "".join(caractere for caractere in valor if not unicodedata.combining(caractere))
    return re.sub(r"[^a-z0-9]+", " ", valor.lower()).strip()


ALIASES_ARTES_SUGIMORI = {
    "Lt. Surge": ("Lt Surge",),
    "Professor Oak": ("Professor Oak",),
    "Professor Elm": ("Professor Elm",),
    "Professor Birch": ("Professor Birch",),
    "Professor Rowan": ("Professor Rowan", "Rowan"),
    "Professor Juniper": ("Professor Juniper", "Juniper"),
    "Professor Sycamore": ("Professor Sycamore", "Sycamore"),
    "Professor Kukui": ("Professor Kukui", "Kukui"),
    "Professor Magnolia": ("Professor Magnolia", "Magnolia"),
    "Professor Laventon": ("Professor Laventon", "Laventon"),
    # Os arquivos oficiais usam apenas Sada/Turo no final do nome.
    "Professor Sada": ("Professor Sada", "Sada"),
    "Professor Turo": ("Professor Turo", "Turo"),
    "Steven Stone": ("Steven Stone", "Steven"),
    "Tate & Liza": ("Tate & Liza", "Tate and Liza"),
    "Urbain / Taunie": ("Urbain", "Taunie"),
}

PREFERENCIA_EDICAO_SUGIMORI = {
    "Kanto": ("firered leafgreen", "red green", "red blue"),
    "Johto": ("heartgold soulsilver", "crystal", "gold silver"),
    "Hoenn": ("emerald", "omega ruby alpha sapphire", "ruby sapphire"),
    "Sinnoh": ("platinum", "diamond pearl"),
    "Hisui": ("legends arceus",),
    "Unova": ("black 2 white 2", "black white"),
    "Kalos": ("x y",),
    "Alola": ("ultra sun ultra moon", "sun moon"),
    "Galar": ("sword shield",),
    "Paldea": ("scarlet violet",),
}


def escolher_arquivo_sugimori(nome: str, regiao: str, catalogo: list):
    """Retorna uma correspondência por sufixo exato, nunca por busca aproximada."""
    aliases = ALIASES_ARTES_SUGIMORI.get(nome, (nome,))
    aliases_norm = tuple(normalizar_titulo_arquivo(alias) for alias in aliases)
    preferencias = PREFERENCIA_EDICAO_SUGIMORI.get(regiao, ())
    candidatos = []

    for arquivo in catalogo:
        titulo = str(arquivo.get("titulo", ""))
        nome_arquivo = titulo.split(":", 1)[-1].rsplit(".", 1)[0]
        base = normalizar_titulo_arquivo(nome_arquivo)
        for alias in aliases_norm:
            if not alias or not (base == alias or base.endswith(" " + alias)):
                continue
            prefixo = base[:-len(alias)].strip()
            prioridade = 0
            for indice, edicao in enumerate(preferencias):
                if edicao in prefixo:
                    prioridade = 1000 - (indice * 100)
                    break
            # Em empate, nomes de arquivo mais específicos têm precedência.
            candidatos.append((prioridade, len(prefixo), arquivo))

    if not candidatos:
        return None
    candidatos.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidatos[0][2]


def baixar_arte_oficial(url: str, origem: str = ""):
    if not url:
        return None
    headers = {"User-Agent": "KAYZAC-Master-Pokemon/3.0"}
    if "bulbagarden.net" in url:
        headers["Referer"] = "https://archives.bulbagarden.net/"
    try:
        resposta = requests.get(url, timeout=(4, 10), headers=headers)
        resposta.raise_for_status()
        if not resposta.content or len(resposta.content) < 300:
            return None
        with Image.open(io.BytesIO(resposta.content)) as img:
            img.load()
            modo = "RGBA" if "A" in img.getbands() else "RGB"
            convertido = img.convert(modo)
            saida = io.BytesIO()
            convertido.save(saida, format="PNG")
            return saida.getvalue()
    except Exception:
        return None


# Algumas artes oficiais não estão dentro da categoria Ken Sugimori.
# O Archives mantém categorias individuais (ex.: Lyra, Hilda, Adaman, Mela).
# Estes aliases cobrem diferenças entre o nome exibido e o nome da categoria.
ALIASES_CATEGORIA_PERSONAGEM = {
    "Commander Kamado": ("Kamado",),
    "Urbain / Taunie": ("Urbain", "Taunie"),
    # Categorias do Archives que não seguem exatamente o nome exibido no site.
    "Professor Sada": ("Professor Sada", "Sada"),
    "Professor Turo": ("Professor Turo", "Turo"),
    "Elio": ("Elio (game)", "Elio"),
    "Selene": ("Selene (game)", "Selene"),
    "Victor": ("Victor (game)", "Victor"),
    # Estes cinco professores não têm artwork individual de Ken Sugimori catalogado.
    # Usamos os retratos VS oficiais extraídos do próprio Scarlet/Violet.
    "Dendra": ("Dendra", "VSDendra"),
    "Miriam": ("Miriam", "VSMiriam"),
    "Raifort": ("Raifort", "VSRaifort"),
    "Saguaro": ("Saguaro", "VSSaguaro"),
    "Tyme": ("Tyme", "VSTyme"),
    "Professor Oak": ("Professor Oak", "Oak"),
    "Professor Elm": ("Professor Elm", "Elm"),
    "Professor Birch": ("Professor Birch", "Birch"),
    "Professor Rowan": ("Professor Rowan", "Rowan"),
    "Professor Juniper": ("Professor Juniper", "Juniper"),
    "Professor Sycamore": ("Professor Sycamore", "Sycamore"),
    "Professor Kukui": ("Professor Kukui", "Kukui"),
    "Professor Magnolia": ("Professor Magnolia", "Magnolia"),
    "Professor Laventon": ("Professor Laventon", "Laventon"),
    "Professor Burnet": ("Professor Burnet", "Burnet"),
    # Salvatore possui um retrato oficial de perfil do League Club Room em Scarlet/Violet.
    "Salvatore": ("Salvatore",),
    # Este arquivo é artwork oficial da animação Sun & Moon (não sprite de jogo).
    "Samson Oak": ("Samson Oak SM", "Samson Oak"),
    "Tracey Sketchit": ("Tracey Sketchit", "Tracey"),
    "Koko": ("Koko", "Koko (M23)"),
}

PREFERENCIA_ARTES_PERSONAGEM = {
    "Kanto": ("firered leafgreen", "red blue", "red green"),
    "Johto": ("heartgold soulsilver", "crystal", "gold silver"),
    "Hoenn": ("omega ruby alpha sapphire", "emerald", "ruby sapphire"),
    "Sinnoh": ("platinum", "diamond pearl"),
    "Hisui": ("legends arceus",),
    "Unova": ("black 2 white 2", "black white"),
    "Kalos": ("legends z a", "pokemon legends z a", "x y"),
    "Alola": ("ultra sun ultra moon", "sun moon"),
    "Galar": ("sword shield",),
    "Paldea": ("scarlet violet", "the teal mask", "the indigo disk", "indigo disk"),
}

# Nomes de arquivo conhecidos como arte de personagem do anime (não screenshots).
ALIASES_ARTES_ANIME = {
    "Tracey Sketchit": ("TraceyEP", "Tracey"),
    "Max": ("Max AG 2", "MaxAG", "Max AG", "Max character sheet"),
    "Alain": ("Alain JN", "Alain XY"),
    "Ritchie": ("Ritchie Artwork",),
    "Paul": ("Paul DP",),
    "Mairin": ("Mairin",),
    "Koko": ("Koko",),
    "Spinel": ("Spinel anime 2", "Spinel anime"),
}

TERMOS_ARTES_NAO_PRINCIPAIS = (
    "sprite", "emote", "masters", "tcg", "card", "plush", "playmat",
    "sleeves", "banner", "screenshot", "episode", "opening", "ending",
    "adventures", "merch", "icon", "key frame", "eyecatch", "wallpaper",
)

# Nomes exatos dos retratos oficiais que devem vencer outras imagens da mesma categoria.
# Os arquivos VSDendra/VSMiriam/etc. são renders 3D de batalha, não desenhos Sugimori.
ARQUIVOS_ARTES_PRIORITARIOS = {
    # Retrato oficial de perfil do League Club Room (não é artwork Sugimori).
    "Salvatore": ("LCR Salvatore icon large",),
    "Samson Oak": ("Samson Oak SM",),
    "Dendra": ("VSDendra",),
    "Miriam": ("VSMiriam",),
    "Raifort": ("VSRaifort",),
    "Saguaro": ("VSSaguaro",),
    "Tyme": ("VSTyme",),
}

ROTULOS_ARTES_ESPECIAIS = {
    "Salvatore": "Retrato oficial de perfil • League Club Room (Scarlet/Violet)",
    "Samson Oak": "Artwork oficial do anime • Sun & Moon",
    "Dendra": "Retrato VS oficial do jogo • modelo 3D de Scarlet/Violet",
    "Miriam": "Retrato VS oficial do jogo • modelo 3D de Scarlet/Violet",
    "Raifort": "Retrato VS oficial do jogo • modelo 3D de Scarlet/Violet",
    "Saguaro": "Retrato VS oficial do jogo • modelo 3D de Scarlet/Violet",
    "Tyme": "Retrato VS oficial do jogo • modelo 3D de Scarlet/Violet",
}

VERSAO_CACHE_ARTES = "2026-11-03-personagens-artes-v3-salvatore"


@st.cache_data(ttl=86400, show_spinner=False)
def obter_arquivos_categoria_personagem(categorias: tuple):
    """Consulta categorias individuais no Archives e devolve apenas arquivos de imagem."""
    endpoint = "https://archives.bulbagarden.net/w/api.php"
    headers = {
        "User-Agent": "KAYZAC-Master-Pokemon/3.1 (official character artwork)",
        "Accept": "application/json",
    }
    arquivos = []

    for categoria in categorias:
        parametros = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": f"Category:{categoria}",
            "gcmtype": "file",
            "gcmlimit": 100,
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "format": "json",
            "formatversion": 2,
        }

        # Paginações adicionais protegem categorias maiores (ex.: Max ou Alain).
        for _ in range(4):
            try:
                resposta = requests.get(
                    endpoint,
                    params=parametros,
                    timeout=(4, 12),
                    headers=headers,
                )
                resposta.raise_for_status()
                dados = resposta.json()
            except Exception:
                break

            paginas = dados.get("query", {}).get("pages", [])
            if isinstance(paginas, dict):
                paginas = list(paginas.values())
            if not isinstance(paginas, list):
                break

            for pagina in paginas:
                infos = pagina.get("imageinfo", [])
                if not infos or not isinstance(infos[0], dict):
                    continue
                info = infos[0]
                url = info.get("url")
                mime = str(info.get("mime", "")).lower()
                if url and mime.startswith("image/"):
                    arquivos.append({
                        "titulo": str(pagina.get("title", "")),
                        "url": url,
                        "mime": mime,
                        "largura": int(info.get("width", 0) or 0),
                        "altura": int(info.get("height", 0) or 0),
                    })

            continuacao = dados.get("continue", {})
            if not continuacao:
                break
            parametros.update(continuacao)

    return arquivos


def escolher_arquivo_categoria_personagem(
    nome: str,
    regiao: str,
    origem: str,
    catalogo: list,
):
    """Escolhe a arte principal por nome de arquivo, jogo e proporção; evita imagens aleatórias."""
    if origem == "Anime":
        aliases = ALIASES_ARTES_ANIME.get(nome, (nome,))
        preferencias = ()
    else:
        aliases = ALIASES_CATEGORIA_PERSONAGEM.get(nome, (nome,))
        preferencias = PREFERENCIA_ARTES_PERSONAGEM.get(regiao, ())

    # Prioridade absoluta para arquivos cujo título foi conferido individualmente.
    # Isso impede, por exemplo, que o modelo 3D de Miriam seja confundido com artwork.
    preferidos = tuple(
        normalizar_titulo_arquivo(item)
        for item in ARQUIVOS_ARTES_PRIORITARIOS.get(nome, ())
    )
    for preferido in preferidos:
        for arquivo in catalogo:
            titulo = str(arquivo.get("titulo", ""))
            nome_arquivo = titulo.split(":", 1)[-1].rsplit(".", 1)[0]
            if normalizar_titulo_arquivo(nome_arquivo) == preferido:
                return arquivo

    aliases_norm = tuple(normalizar_titulo_arquivo(alias) for alias in aliases)
    candidatos = []

    for arquivo in catalogo:
        titulo = str(arquivo.get("titulo", ""))
        nome_arquivo = titulo.split(":", 1)[-1].rsplit(".", 1)[0]
        base = normalizar_titulo_arquivo(nome_arquivo)
        alias_usado = None
        tipo_match = 0

        for alias in aliases_norm:
            if not alias:
                continue
            if base == alias:
                alias_usado, tipo_match = alias, 120
                break
            if base.endswith(" " + alias):
                alias_usado, tipo_match = alias, 110
                break
            # No anime, alguns arquivos oficiais usam o nome seguido da série.
            alias_compacto = alias.replace(" ", "")
            if origem == "Anime" and (base.startswith(alias + " ") or base.startswith(alias_compacto)):
                alias_usado, tipo_match = alias, 100
                break

        if not alias_usado:
            continue

        prioridade_edicao = 0
        for indice, edicao in enumerate(preferencias):
            if edicao in base:
                prioridade_edicao = 1000 - (indice * 100)
                break

        # Mantém artes oficiais como Masters/concept art apenas como opção inferior.
        penalidade = sum(1 for termo in TERMOS_ARTES_NAO_PRINCIPAIS if termo in base)
        largura = int(arquivo.get("largura", 0) or 0)
        altura = int(arquivo.get("altura", 0) or 0)
        proporcao_vertical = 1 if altura >= 700 and (not largura or largura / max(altura, 1) <= 0.9) else 0

        if origem == "Anime":
            # Os aliases de anime são específicos para as artes de personagem já identificadas.
            score = tipo_match * 10 + proporcao_vertical * 30 - penalidade * 120
        else:
            score = prioridade_edicao + tipo_match + proporcao_vertical * 30 - penalidade * 120

        candidatos.append((score, prioridade_edicao, proporcao_vertical, arquivo))

    if not candidatos:
        return None

    candidatos.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return candidatos[0][3]


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_arte_personagem(
    nome: str,
    regiao: str = "",
    origem: str = "Jogos",
    arte_url: str = "",
    versao_cache: str = VERSAO_CACHE_ARTES,
):
    """Busca artwork oficial e usa retratos VS somente nos cinco professores indicados."""
    # O parâmetro altera a chave do cache quando corrigimos aliases e fontes.
    _ = versao_cache
    # Para o anime, respeita a fonte explícita cadastrada. Se o link estiver antigo ou
    # quebrado, tenta a categoria individual do personagem como alternativa.
    if origem == "Anime" and arte_url:
        imagem = baixar_arte_oficial(arte_url, origem)
        if imagem:
            return imagem

    if origem != "Anime":
        catalogo = obter_catalogo_ken_sugimori()
        arquivo = escolher_arquivo_sugimori(nome, regiao, catalogo)
        if arquivo:
            imagem = baixar_arte_oficial(arquivo.get("url", ""), "Ken Sugimori")
            if imagem:
                return imagem

    aliases_categoria = ALIASES_CATEGORIA_PERSONAGEM.get(nome, (nome,))
    categorias = tuple(dict.fromkeys(str(alias).strip() for alias in aliases_categoria if str(alias).strip()))
    catalogo_personagem = obter_arquivos_categoria_personagem(categorias)
    arquivo_personagem = escolher_arquivo_categoria_personagem(
        nome,
        regiao,
        origem,
        catalogo_personagem,
    )
    if not arquivo_personagem:
        return None
    return baixar_arte_oficial(arquivo_personagem.get("url", ""), "Bulbagarden Archives")


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_artes_em_lote(
    personagens_info: tuple,
    versao_cache: str = VERSAO_CACHE_ARTES,
):
    """Busca artes oficiais apenas para os cards visíveis, em paralelo e sob demanda."""
    _ = versao_cache
    from concurrent.futures import ThreadPoolExecutor, as_completed

    itens = tuple(dict.fromkeys(personagens_info))
    if not itens:
        return {}

    resultados = {}
    with ThreadPoolExecutor(max_workers=min(8, len(itens))) as executor:
        tarefas = {}
        for item in itens:
            nome, regiao, origem, arte_url = item
            tarefa = executor.submit(
                buscar_arte_personagem,
                nome,
                regiao,
                origem,
                arte_url,
                versao_cache,
            )
            tarefas[tarefa] = nome
        for tarefa in as_completed(tarefas):
            nome = tarefas[tarefa]
            try:
                resultados[nome] = tarefa.result()
            except Exception:
                resultados[nome] = None
    return resultados


def info_arte_personagem(personagem: dict) -> tuple:
    return (
        personagem.get("nome", ""),
        personagem.get("regiao", ""),
        personagem.get("origem", "Jogos"),
        personagem.get("arte_url", ""),
    )


def imagem_personagem(personagem: dict):
    """Compatibilidade: cards não fazem consultas de imagem automaticamente."""
    return None


def encontrar_pagina_pokedex():
    """Localiza o arquivo da Pokédex dentro de pages/ sem depender de um nome específico."""
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
            return f"pages/{nome_arquivo}"

    # Último recurso: procura qualquer arquivo Python cujo nome contenha "pokedex".
    if pasta_pages.exists():
        encontrados = sorted(
            caminho for caminho in pasta_pages.glob("*.py")
            if "pokedex" in caminho.stem.lower()
        )
        if encontrados:
            return f"pages/{encontrados[0].name}"

    return None


def abrir_pokedex(nome: str):
    st.session_state["pokemon_focado"] = nome.lower().replace(" ", "-")
    pagina = encontrar_pagina_pokedex()

    if pagina:
        st.switch_page(pagina)
    else:
        st.error(
            "❌ Não encontrei o arquivo da Pokédex na pasta pages/. "
            "Verifique se a sua página da Pokédex está dentro da pasta pages."
        )


def card_personagem(
    personagem: dict,
    indice: int,
    artes=None,
    carregar_arte: bool = False,
):
    """Desenha o card sem executar consultas de rede durante a renderização."""
    with st.container(border=True):
        col_img, col_info = st.columns([1, 2])

        with col_img:
            imagem = (artes or {}).get(personagem.get("nome")) if carregar_arte else None
            if imagem:
                st.image(imagem, use_container_width=True)
            else:
                st.markdown("## 👤")
                if not carregar_arte:
                    st.caption("Arte oficial sob demanda")
                elif personagem.get("origem") == "Anime":
                    st.caption("Arte oficial do anime não localizada na categoria do personagem.")
                else:
                    st.caption("Arte oficial não localizada nos catálogos consultados.")
            if imagem:
                legenda_arte = ROTULOS_ARTES_ESPECIAIS.get(personagem.get("nome"))
                if legenda_arte:
                    st.caption(legenda_arte)
                else:
                    st.caption(
                        "Arte oficial do anime" if personagem.get("origem") == "Anime"
                        else "Artwork oficial do personagem"
                    )

        with col_info:
            st.markdown(f"### 👤 {personagem['nome']}")
            origem_legenda = "Anime" if personagem.get("origem") == "Anime" else personagem['regiao']
            st.caption(f"{origem_legenda} • {personagem['categoria']}")
            st.write(personagem["papel"])
            rotulo_midia = "📺 Série" if personagem.get("origem") == "Anime" else "🎮 Jogos"
            st.markdown(f"**{rotulo_midia}:** {personagem['jogo']}")

            if personagem.get("ace"):
                st.markdown(f"**⭐ Pokémon de destaque:** {nome_bonito(personagem['ace'])}")
                if st.button(
                    "📖 Abrir Pokémon na Pokédex",
                    key=f"personagem_pokedex_{indice}_{personagem['nome']}",
                    use_container_width=True,
                ):
                    abrir_pokedex(personagem["ace"])


# ============================================================
# CABEÇALHO
# ============================================================

st.title("👥 KAYZAC - PERSONAGENS POKÉMON")
st.write(
    "Conheça protagonistas, rivais, professores, Líderes de Ginásio, Elite Four, Campeões,"
    " aliados, antagonistas e personagens exclusivos da animação Pokémon."
)
st.caption(
    "As artes dos jogos são procuradas no catálogo Ken Sugimori e nas categorias individuais de cada personagem. "
    "Para Dendra, Miriam, Raifort, Saguaro e Tyme, a página usa retratos VS 3D oficiais de Scarlet/Violet, "
    "pois não foi localizado artwork individual de Ken Sugimori para eles. Personagens do anime usam artes oficiais da animação."
)
st.divider()


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    regiao = st.selectbox("🌎 Região / mídia", REGIOES, key="personagens_regiao")

with col2:
    categoria = st.selectbox("🏷️ Categoria", CATEGORIAS, key="personagens_categoria")

with col3:
    busca = st.text_input(
        "🔎 Buscar personagem",
        placeholder="Ex.: Cynthia, Giovanni, Lillie...",
        key="personagens_busca",
    ).strip().lower()


# ============================================================
# RESULTADOS
# ============================================================

resultados = PERSONAGENS

if regiao != "Todas":
    resultados = [p for p in resultados if p["regiao"] == regiao]

if categoria != "Todos":
    resultados = [p for p in resultados if p["categoria"] == categoria]

if busca:
    resultados = [
        p for p in resultados
        if busca in p["nome"].lower()
        or busca in p["papel"].lower()
        or busca in p["jogo"].lower()
    ]

# KAYZAC_PERSONAGENS_PERFORMANCE_V3
# Renderização inicial leve: só 12 cards e nenhuma busca remota automática.
CARDS_POR_PAGINA = 12
_assinatura_filtros = (regiao, categoria, busca)
if st.session_state.get("_personagens_filtros_rapidos") != _assinatura_filtros:
    st.session_state["_personagens_filtros_rapidos"] = _assinatura_filtros
    st.session_state["personagens_pagina_rapida"] = 1

total_paginas = max(1, (len(resultados) + CARDS_POR_PAGINA - 1) // CARDS_POR_PAGINA)
st.session_state["personagens_pagina_rapida"] = min(
    max(1, int(st.session_state.get("personagens_pagina_rapida", 1))),
    total_paginas,
)
carregar_artes_resultados = st.toggle(
    "🖼️ Carregar artes oficiais dos personagens desta página",
    value=False,
    key="personagens_carregar_artes_resultados_rapido",
    help="Desativado por padrão para a página abrir imediatamente. Ao ativar, procura artwork Sugimori, retratos VS oficiais dos cinco professores de Paldea e artes oficiais do anime para os até 12 personagens visíveis.",
)

m1, m2, m3 = st.columns(3)
m1.metric("👥 Personagens encontrados", len(resultados))
m2.metric("🌎 Regiões / mídias", len(REGIOES) - 1)
m3.metric("🏷️ Categorias", len(CATEGORIAS) - 1)

st.divider()

if resultados and total_paginas > 1:
    pag_esq, pag_meio, pag_dir = st.columns([1, 2, 1])
    with pag_esq:
        if st.button(
            "⬅️ Anterior",
            disabled=st.session_state["personagens_pagina_rapida"] <= 1,
            use_container_width=True,
            key="personagens_pagina_anterior_rapida",
        ):
            st.session_state["personagens_pagina_rapida"] -= 1
            st.rerun()
    with pag_meio:
        st.markdown(
            f"<div style='text-align:center;padding:.45rem 0'>Página "
            f"<b>{st.session_state['personagens_pagina_rapida']}</b> de "
            f"<b>{total_paginas}</b> · {len(resultados)} personagens</div>",
            unsafe_allow_html=True,
        )
    with pag_dir:
        if st.button(
            "Próxima ➡️",
            disabled=st.session_state["personagens_pagina_rapida"] >= total_paginas,
            use_container_width=True,
            key="personagens_proxima_pagina_rapida",
        ):
            st.session_state["personagens_pagina_rapida"] += 1
            st.rerun()

_indice_inicio = (st.session_state["personagens_pagina_rapida"] - 1) * CARDS_POR_PAGINA
resultados_pagina = resultados[_indice_inicio:_indice_inicio + CARDS_POR_PAGINA]

if not resultados:
    st.warning("🔎 Nenhum personagem encontrado com esses filtros.")
else:
    st.subheader("📚 Banco de Personagens")
    st.caption("Use os filtros acima para navegar pela coleção.")

    artes_resultados = {}
    if carregar_artes_resultados and resultados_pagina:
        with st.spinner("🖼️ Carregando artes dos personagens desta página..."):
            artes_resultados = buscar_artes_em_lote(
                tuple(info_arte_personagem(personagem) for personagem in resultados_pagina),
                VERSAO_CACHE_ARTES,
            )

    colunas = st.columns(2)
    for indice, personagem in enumerate(resultados_pagina):
        with colunas[indice % 2]:
            card_personagem(
                personagem,
                _indice_inicio + indice,
                artes=artes_resultados,
                carregar_arte=carregar_artes_resultados,
            )


# ============================================================
# DESTAQUES
# ============================================================

st.divider()
st.subheader("⭐ Personagens em destaque")

buscas_destaque = ["Cynthia", "Giovanni", "N", "Lillie", "Leon", "Nemona"]
destaques = [p for p in PERSONAGENS if p["nome"] in buscas_destaque]
carregar_artes_destaques = st.toggle(
    "🖼️ Carregar artes oficiais dos personagens em destaque",
    value=False,
    key="personagens_carregar_artes_destaques_rapido",
    help="Busca separadamente as artes dos seis destaques, somente quando solicitada.",
)
artes_destaques = {}
if carregar_artes_destaques and destaques:
    with st.spinner("🖼️ Carregando artes dos destaques..."):
        artes_destaques = buscar_artes_em_lote(
            tuple(info_arte_personagem(personagem) for personagem in destaques),
            VERSAO_CACHE_ARTES,
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
        st.write(personagem["papel"])


# ============================================================
# KALOS / LEGENDS Z-A
# ============================================================

st.divider()
st.subheader("🟦 Kalos • Pokémon Legends: Z-A")
st.info(
    "O módulo também reserva uma categoria própria para personagens de Pokémon Legends: Z-A, "
    "permitindo separar os novos personagens de Lumiose dos personagens clássicos de Kalos."
)

with st.expander("📖 Personagens de Z-A cadastrados"):
    for personagem in [p for p in PERSONAGENS if p["categoria"] == "Personagem de Z-A"]:
        st.write(f"**{personagem['nome']}** — {personagem['papel']}")


# ============================================================
# IDEIAS PARA EXPANSÃO
# ============================================================

with st.expander("🧩 Próximas expansões do banco"):
    st.write(
        "Podemos acrescentar equipes completas dos personagens, Pokémon assinatura por jogo, "
        "história individual, relações, aparições, sprites/arte oficial, personagens de spin-offs "
        "e uma ficha detalhada para cada personagem."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption("👥 KAYZAC - MASTER POKEMON! • Banco de Personagens")
st.caption("Personagens organizados por região, papel e jogo.")
