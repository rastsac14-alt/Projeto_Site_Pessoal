from pathlib import Path
import io

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
    {"nome": "Geeta", "regiao": "Paldea", "categoria": "Campeão", "jogo": "Scarlet / Violet", "papel": "Campeã da Liga de Paldea e presidente da Pokémon League.", "ace": "glimmora"},
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
]


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
def buscar_arte_personagem(nome: str):
    """Busca e baixa a arte oficial do personagem no Bulbagarden Archives.

    O retorno são bytes da imagem, e não somente uma URL. Isso evita que o
    navegador precise acessar diretamente o arquivo remoto e corrige vários
    casos em que a imagem aparecia quebrada no Streamlit.
    """
    nome = str(nome or "").strip()
    if not nome:
        return None

    endpoint = "https://archives.bulbagarden.net/w/api.php"
    consultas = [
        f'"{nome}" artwork',
        f'"{nome}" character',
        f'"{nome}" official',
        nome,
    ]

    headers = {
        "User-Agent": "KAYZAC-Master-Pokemon/1.0 (Streamlit; character gallery)",
        "Accept": "application/json,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    for consulta in consultas:
        try:
            resposta = requests.get(
                endpoint,
                params={
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": consulta,
                    "gsrnamespace": 6,
                    "gsrlimit": 20,
                    "prop": "imageinfo",
                    "iiprop": "url|mime|size",
                    "format": "json",
                    "formatversion": 2,
                },
                timeout=15,
                headers=headers,
            )
            resposta.raise_for_status()
            dados = resposta.json()
        except Exception:
            continue

        paginas = dados.get("query", {}).get("pages", [])
        if not isinstance(paginas, list):
            continue

        nome_lower = nome.lower()
        candidatos = []

        for pagina in paginas:
            titulo = str(pagina.get("title", ""))
            titulo_lower = titulo.lower()
            info = pagina.get("imageinfo", [])
            if not info:
                continue

            metadados = info[0] if isinstance(info[0], dict) else {}
            url = metadados.get("url")
            mime = str(metadados.get("mime", "")).lower()
            if not url:
                continue

            # Aumenta a chance de pegar arte oficial e reduz sprites/ícones.
            pontuacao = 0
            if nome_lower in titulo_lower:
                pontuacao += 20
            if "official" in titulo_lower:
                pontuacao += 8
            if "artwork" in titulo_lower:
                pontuacao += 8
            if "character" in titulo_lower:
                pontuacao += 5
            if "sugimori" in titulo_lower:
                pontuacao += 4
            if "concept" in titulo_lower:
                pontuacao += 2
            if "sprite" in titulo_lower:
                pontuacao -= 12
            if "icon" in titulo_lower:
                pontuacao -= 12
            if "badge" in titulo_lower:
                pontuacao -= 10
            if "anime" in titulo_lower:
                pontuacao -= 6
            if "tcg" in titulo_lower:
                pontuacao -= 6
            if mime == "image/svg+xml":
                pontuacao -= 2

            candidatos.append((pontuacao, titulo, url, mime))

        candidatos.sort(key=lambda item: item[0], reverse=True)

        # Tenta os melhores candidatos e valida o arquivo de verdade.
        for _, _, url, mime in candidatos[:12]:
            try:
                imagem = requests.get(
                    url,
                    timeout=20,
                    headers={
                        "User-Agent": headers["User-Agent"],
                        "Referer": "https://archives.bulbagarden.net/",
                    },
                )
                imagem.raise_for_status()
                dados_imagem = imagem.content
                if not dados_imagem or len(dados_imagem) < 1000:
                    continue

                # Normaliza formatos que o navegador/Streamlit pode tratar mal.
                try:
                    with Image.open(io.BytesIO(dados_imagem)) as img:
                        img.load()
                        if img.mode not in ("RGB", "RGBA"):
                            img = img.convert("RGBA")
                        saida = io.BytesIO()
                        img.save(saida, format="PNG")
                        return saida.getvalue()
                except Exception:
                    # Caso seja um formato não suportado pelo Pillow, mantém os bytes originais.
                    if mime.startswith("image/"):
                        return dados_imagem
            except Exception:
                continue

    return None


def imagem_personagem(personagem: dict):
    """Retorna os bytes da arte do treinador/personagem."""
    return buscar_arte_personagem(personagem.get("nome", ""))


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


def card_personagem(personagem: dict, indice: int):
    with st.container(border=True):
        col_img, col_info = st.columns([1, 2])

        with col_img:
            imagem = imagem_personagem(personagem)
            if imagem:
                st.image(imagem, use_container_width=True)
            else:
                st.markdown("## 👤")
                st.caption("Perfil de personagem")

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


# ============================================================
# CABEÇALHO
# ============================================================

st.title("👥 KAYZAC - PERSONAGENS POKÉMON")
st.write(
    "Conheça protagonistas, rivais, professores, Líderes de Ginásio, Elite Four, Campeões,"
    " aliados e os principais antagonistas de cada região."
)
st.caption(
    "A página foi pensada como um banco de personagens do universo dos jogos principais,"
    " com espaço para crescer junto com o projeto."
)
st.divider()


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    regiao = st.selectbox("🌎 Região", REGIOES, key="personagens_regiao")

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


m1, m2, m3 = st.columns(3)
m1.metric("👥 Personagens encontrados", len(resultados))
m2.metric("🌎 Regiões no banco", len(REGIOES) - 1)
m3.metric("🏷️ Categorias", len(CATEGORIAS) - 1)

st.divider()

if not resultados:
    st.warning("🔎 Nenhum personagem encontrado com esses filtros.")
else:
    st.subheader("📚 Banco de Personagens")
    st.caption("Use os filtros acima para navegar pela coleção.")

    colunas = st.columns(2)
    for indice, personagem in enumerate(resultados):
        with colunas[indice % 2]:
            card_personagem(personagem, indice)


# ============================================================
# DESTAQUES
# ============================================================

st.divider()
st.subheader("⭐ Personagens em destaque")

buscas_destaque = ["Cynthia", "Giovanni", "N", "Lillie", "Leon", "Nemona"]
destaques = [p for p in PERSONAGENS if p["nome"] in buscas_destaque]

dest_cols = st.columns(3)
for indice, personagem in enumerate(destaques):
    with dest_cols[indice % 3]:
        imagem = imagem_personagem(personagem)
        if imagem:
            st.image(imagem, width=130)
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
