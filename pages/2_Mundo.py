import json
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="KAYZAC WORLD • Atlas Pokémon",
    page_icon="🌎",
    layout="wide"
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_MAPAS = BASE_DIR / "mapas"


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🌎 KAYZAC WORLD 🌎"
)

st.write(
    "Um atlas interativo do universo Pokémon: escolha uma região, "
    "explore cidades, rotas, ginásios, personagens, Pokémon, história "
    "e use o sistema de viagem para navegar pelo mundo."
)

st.divider()


# ============================================================
# ESTADO
# ============================================================

if "regiao_atual" not in st.session_state:
    st.session_state.regiao_atual = "Kanto"

if "secao_regiao" not in st.session_state:
    st.session_state.secao_regiao = "🌎 Visão Geral"


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def nome_bonito(nome):

    if not nome:
        return ""

    return (
        str(nome)
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def traduzir_tipo(tipo):
    traducoes = {
        "normal": "Normal",
        "fire": "Fogo",
        "water": "Água",
        "electric": "Elétrico",
        "grass": "Grama",
        "ice": "Gelo",
        "fighting": "Lutador",
        "poison": "Veneno",
        "ground": "Terra",
        "flying": "Voador",
        "psychic": "Psíquico",
        "bug": "Inseto",
        "rock": "Pedra",
        "ghost": "Fantasma",
        "dragon": "Dragão",
        "dark": "Sombrio",
        "steel": "Aço",
        "fairy": "Fada",
    }
    return traducoes.get(normalizar_nome(tipo), str(tipo).title())


def normalizar_nome(nome):

    if not nome:
        return ""

    return (
        str(nome)
        .strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def requisicao_api(url):

    try:

        resposta = requests.get(
            url,
            timeout=10
        )

        resposta.raise_for_status()

        return resposta.json()

    except requests.exceptions.RequestException:

        return None


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_regiao(nome):

    nome_api = normalizar_nome(nome)

    return requisicao_api(
        "https://pokeapi.co/api/v2/"
        f"region/{nome_api}"
    )


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_pokedex(url):

    if not url:
        return None

    return requisicao_api(
        url
    )


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_local(url):

    if not url:
        return None

    return requisicao_api(
        url
    )


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_pokemon(nome):

    return requisicao_api(
        "https://pokeapi.co/api/v2/"
        f"pokemon/{normalizar_nome(nome)}"
    )


# ============================================================
# DADOS DAS REGIÕES
# ============================================================

REGIOES = {

    "Kanto": {

        "api": "kanto",

        "geracao": "Geração I",

        "jogos": [
            "Pokémon Red",
            "Pokémon Blue",
            "Pokémon Yellow",
            "Pokémon FireRed",
            "Pokémon LeafGreen",
            "Pokémon Let's Go, Pikachu!",
            "Pokémon Let's Go, Eevee!"
        ],

        "descricao": (
            "Kanto é a primeira grande região apresentada "
            "na franquia Pokémon e é o ponto de partida "
            "para a aventura original."
        ),

        "professor": "Professor Carvalho",

        "campeao": "Blue",

        "equipe_vila": "Equipe Rocket",

        "mapa": "kanto.png",

        "caracteristicos": [
            "Bulbasaur",
            "Charmander",
            "Squirtle",
            "Pikachu",
            "Eevee",
            "Mewtwo",
            "Mew",
            "Snorlax"
        ],

        "personagens": [
            "Professor Carvalho",
            "Red",
            "Blue",
            "Brock",
            "Misty",
            "Lt. Surge",
            "Erika",
            "Koga",
            "Sabrina",
            "Blaine",
            "Giovanni"
        ],

        "vilao_descricao": (
            "A Equipe Rocket é uma organização criminosa "
            "liderada por Giovanni."
        ),

        "ginasios": [

            {
                "lider": "Brock",
                "cidade": "Pewter City",
                "tipo": "Pedra",
                "insignia": "Boulder"
            },

            {
                "lider": "Misty",
                "cidade": "Cerulean City",
                "tipo": "Água",
                "insignia": "Cascade"
            },

            {
                "lider": "Lt. Surge",
                "cidade": "Vermilion City",
                "tipo": "Elétrico",
                "insignia": "Thunder"
            },

            {
                "lider": "Erika",
                "cidade": "Celadon City",
                "tipo": "Grama",
                "insignia": "Rainbow"
            },

            {
                "lider": "Koga",
                "cidade": "Fuchsia City",
                "tipo": "Veneno",
                "insignia": "Soul"
            },

            {
                "lider": "Sabrina",
                "cidade": "Saffron City",
                "tipo": "Psíquico",
                "insignia": "Marsh"
            },

            {
                "lider": "Blaine",
                "cidade": "Cinnabar Island",
                "tipo": "Fogo",
                "insignia": "Volcano"
            },

            {
                "lider": "Giovanni",
                "cidade": "Viridian City",
                "tipo": "Terrestre",
                "insignia": "Earth"
            }
        ],

        "elite": [

            "Lorelei",
            "Bruno",
            "Agatha",
            "Lance"
        ],

        "historia": [
            "A aventura original da série principal começa em Kanto.",
            "O jogador recebe seu primeiro Pokémon do Professor Carvalho.",
            "O objetivo principal é conquistar as oito insígnias.",
            "A Equipe Rocket interfere em diversos acontecimentos da região.",
            "Após os oito ginásios, o treinador desafia a Liga Pokémon."
        ],

        "curiosidades": [
            "Kanto foi a primeira região criada para a série principal.",
            "É inspirada principalmente na região de Kantō, no Japão.",
            "Pallet Town é o ponto inicial da aventura original.",
            "Mewtwo pode ser encontrado no pós-jogo em Cerulean Cave."
        ]
    },


    "Johto": {

        "api": "johto",

        "geracao": "Geração II",

        "jogos": [
            "Pokémon Gold",
            "Pokémon Silver",
            "Pokémon Crystal",
            "Pokémon HeartGold",
            "Pokémon SoulSilver"
        ],

        "descricao": (
            "Johto é uma região conhecida por sua forte "
            "ligação com tradições, torres, lendas e história."
        ),

        "professor": "Professor Elm",

        "campeao": "Lance",

        "equipe_vila": "Equipe Rocket",

        "mapa": "johto.png",

        "caracteristicos": [
            "Chikorita",
            "Cyndaquil",
            "Totodile",
            "Pichu",
            "Togepi",
            "Lugia",
            "Ho-Oh",
            "Celebi"
        ],

        "personagens": [
            "Professor Elm",
            "Ethan",
            "Lyra",
            "Silver",
            "Falkner",
            "Whitney",
            "Morty",
            "Jasmine",
            "Pryce",
            "Clair"
        ],

        "vilao_descricao": (
            "A Equipe Rocket tenta reconstruir sua organização "
            "e encontrar Giovanni novamente."
        ),

        "ginasios": [

            {
                "lider": "Falkner",
                "cidade": "Violet City",
                "tipo": "Voador",
                "insignia": "Zephyr"
            },

            {
                "lider": "Bugsy",
                "cidade": "Azalea Town",
                "tipo": "Inseto",
                "insignia": "Hive"
            },

            {
                "lider": "Whitney",
                "cidade": "Goldenrod City",
                "tipo": "Normal",
                "insignia": "Plain"
            },

            {
                "lider": "Morty",
                "cidade": "Ecruteak City",
                "tipo": "Fantasma",
                "insignia": "Fog"
            },

            {
                "lider": "Chuck",
                "cidade": "Cianwood City",
                "tipo": "Lutador",
                "insignia": "Storm"
            },

            {
                "lider": "Jasmine",
                "cidade": "Olivine City",
                "tipo": "Aço",
                "insignia": "Mineral"
            },

            {
                "lider": "Pryce",
                "cidade": "Mahogany Town",
                "tipo": "Gelo",
                "insignia": "Glacier"
            },

            {
                "lider": "Clair",
                "cidade": "Blackthorn City",
                "tipo": "Dragão",
                "insignia": "Rising"
            }
        ],

        "elite": [
            "Will",
            "Koga",
            "Bruno",
            "Karen"
        ],

        "historia": [
            "Johto introduziu novas espécies além das originais de Kanto.",
            "As lendas de Lugia e Ho-Oh são centrais na identidade da região.",
            "A região apresenta uma forte relação com Pokémon ancestrais e tradições.",
            "O jogador pode posteriormente retornar a Kanto."
        ],

        "curiosidades": [
            "Johto e Kanto podem ser exploradas na mesma aventura em Gold, Silver e Crystal.",
            "Ecruteak City possui a Burned Tower e a Bell Tower.",
            "Johto introduziu o sistema de criação de Pokémon.",
            "Togepi teve grande destaque durante a Geração II."
        ]
    },


    "Hoenn": {

        "api": "hoenn",

        "geracao": "Geração III",

        "jogos": [
            "Pokémon Ruby",
            "Pokémon Sapphire",
            "Pokémon Emerald",
            "Pokémon Omega Ruby",
            "Pokémon Alpha Sapphire"
        ],

        "descricao": (
            "Hoenn é uma região marcada por grandes áreas marítimas, "
            "vulcões, ilhas e pelo conflito entre terra e oceano."
        ),

        "professor": "Professor Birch",

        "campeao": "Steven Stone",

        "equipe_vila": "Equipe Magma / Equipe Aqua",

        "mapa": "hoenn.png",

        "caracteristicos": [
            "Treecko",
            "Torchic",
            "Mudkip",
            "Gardevoir",
            "Absol",
            "Rayquaza",
            "Groudon",
            "Kyogre"
        ],

        "personagens": [
            "Professor Birch",
            "Brendan",
            "May",
            "Wally",
            "Steven Stone",
            "Wallace",
            "Maxie",
            "Archie"
        ],

        "vilao_descricao": (
            "Equipe Magma e Equipe Aqua representam ideais opostos: "
            "expansão da terra e expansão dos oceanos."
        ),

        "ginasios": [

            {
                "lider": "Roxanne",
                "cidade": "Rustboro City",
                "tipo": "Pedra",
                "insignia": "Stone"
            },

            {
                "lider": "Brawly",
                "cidade": "Dewford Town",
                "tipo": "Lutador",
                "insignia": "Knuckle"
            },

            {
                "lider": "Wattson",
                "cidade": "Mauville City",
                "tipo": "Elétrico",
                "insignia": "Dynamo"
            },

            {
                "lider": "Flannery",
                "cidade": "Lavaridge Town",
                "tipo": "Fogo",
                "insignia": "Heat"
            },

            {
                "lider": "Norman",
                "cidade": "Petalburg City",
                "tipo": "Normal",
                "insignia": "Balance"
            },

            {
                "lider": "Winona",
                "cidade": "Fortree City",
                "tipo": "Voador",
                "insignia": "Feather"
            },

            {
                "lider": "Tate & Liza",
                "cidade": "Mossdeep City",
                "tipo": "Psíquico",
                "insignia": "Mind"
            },

            {
                "lider": "Wallace",
                "cidade": "Sootopolis City",
                "tipo": "Água",
                "insignia": "Rain"
            }
        ],

        "elite": [
            "Sidney",
            "Phoebe",
            "Glacia",
            "Drake"
        ],

        "historia": [
            "Hoenn apresenta um conflito entre forças naturais ligadas à terra e ao mar.",
            "Groudon e Kyogre são figuras centrais das lendas regionais.",
            "Rayquaza atua como uma força capaz de equilibrar o conflito.",
            "A região possui um forte foco em ambientes naturais."
        ],

        "curiosidades": [
            "Pokémon Ruby e Sapphire introduziram 135 novas espécies.",
            "Hoenn é fortemente baseada na ilha japonesa de Kyushu.",
            "Fortree City foi construída entre árvores.",
            "Pokémon Emerald colocou Rayquaza no centro da história."
        ]
    },


    "Sinnoh": {

        "api": "sinnoh",

        "geracao": "Geração IV",

        "jogos": [
            "Pokémon Diamond",
            "Pokémon Pearl",
            "Pokémon Platinum",
            "Pokémon Brilliant Diamond",
            "Pokémon Shining Pearl",
            "Pokémon Legends: Arceus"
        ],

        "descricao": (
            "Sinnoh é uma região montanhosa, conhecida por suas "
            "lendas sobre a criação do mundo Pokémon."
        ),

        "professor": "Professor Rowan",

        "campeao": "Cynthia",

        "equipe_vila": "Equipe Galáctica",

        "mapa": "sinnoh.png",

        "caracteristicos": [
            "Turtwig",
            "Chimchar",
            "Piplup",
            "Lucario",
            "Garchomp",
            "Dialga",
            "Palkia",
            "Giratina"
        ],

        "personagens": [
            "Professor Rowan",
            "Lucas",
            "Dawn",
            "Barry",
            "Cynthia",
            "Cyrus"
        ],

        "vilao_descricao": (
            "A Equipe Galáctica busca remodelar o universo "
            "sob a visão de seu líder Cyrus."
        ),

        "ginasios": [

            {
                "lider": "Roark",
                "cidade": "Oreburgh City",
                "tipo": "Pedra",
                "insignia": "Coal"
            },

            {
                "lider": "Gardenia",
                "cidade": "Eterna City",
                "tipo": "Grama",
                "insignia": "Forest"
            },

            {
                "lider": "Maylene",
                "cidade": "Veilstone City",
                "tipo": "Lutador",
                "insignia": "Cobble"
            },

            {
                "lider": "Crasher Wake",
                "cidade": "Pastoria City",
                "tipo": "Água",
                "insignia": "Fen"
            },

            {
                "lider": "Fantina",
                "cidade": "Hearthome City",
                "tipo": "Fantasma",
                "insignia": "Relic"
            },

            {
                "lider": "Byron",
                "cidade": "Canalave City",
                "tipo": "Aço",
                "insignia": "Mine"
            },

            {
                "lider": "Candice",
                "cidade": "Snowpoint City",
                "tipo": "Gelo",
                "insignia": "Icicle"
            },

            {
                "lider": "Volkner",
                "cidade": "Sunyshore City",
                "tipo": "Elétrico",
                "insignia": "Beacon"
            }
        ],

        "elite": [
            "Aaron",
            "Bertha",
            "Flint",
            "Lucian"
        ],

        "historia": [
            "Sinnoh possui algumas das maiores lendas cosmológicas da franquia.",
            "Dialga, Palkia e Giratina estão diretamente ligados ao espaço, tempo e mundo distorcido.",
            "Arceus é associado à origem do universo Pokémon.",
            "A região também é fortemente marcada pelo Monte Coronet."
        ],

        "curiosidades": [
            "Sinnoh é inspirada principalmente em Hokkaido e partes próximas do Japão.",
            "Cynthia é uma das campeãs mais famosas da série.",
            "O Underground possui destaque em Diamond, Pearl e Platinum.",
            "Pokémon Legends: Arceus explora a antiga Hisui."
        ]
    },


    "Unova": {

        "api": "unova",

        "geracao": "Geração V",

        "jogos": [
            "Pokémon Black",
            "Pokémon White",
            "Pokémon Black 2",
            "Pokémon White 2"
        ],

        "descricao": (
            "Unova apresenta uma identidade urbana e moderna, "
            "com forte inspiração norte-americana."
        ),

        "professor": "Professor Juniper",

        "campeao": "Iris",

        "equipe_vila": "Equipe Plasma",

        "mapa": "unova.png",

        "caracteristicos": [
            "Snivy",
            "Tepig",
            "Oshawott",
            "Zoroark",
            "Volcarona",
            "Reshiram",
            "Zekrom",
            "Kyurem"
        ],

        "personagens": [
            "Professor Juniper",
            "Hilbert",
            "Hilda",
            "Nate",
            "Rosa",
            "N",
            "Ghetsis",
            "Alder"
        ],

        "vilao_descricao": (
            "A Equipe Plasma questiona a relação entre humanos "
            "e Pokémon, enquanto seus líderes possuem objetivos próprios."
        ),

        "ginasios": [

            {
                "lider": "Cilan / Chili / Cress",
                "cidade": "Striaton City",
                "tipo": "Grama / Fogo / Água",
                "insignia": "Trio"
            },

            {
                "lider": "Lenora",
                "cidade": "Nacrene City",
                "tipo": "Normal",
                "insignia": "Basic"
            },

            {
                "lider": "Burgh",
                "cidade": "Castelia City",
                "tipo": "Inseto",
                "insignia": "Insect"
            },

            {
                "lider": "Elesa",
                "cidade": "Nimbasa City",
                "tipo": "Elétrico",
                "insignia": "Bolt"
            },

            {
                "lider": "Clay",
                "cidade": "Driftveil City",
                "tipo": "Terrestre",
                "insignia": "Quake"
            },

            {
                "lider": "Skyla",
                "cidade": "Mistralton City",
                "tipo": "Voador",
                "insignia": "Jet"
            },

            {
                "lider": "Brycen",
                "cidade": "Icirrus City",
                "tipo": "Gelo",
                "insignia": "Freeze"
            },

            {
                "lider": "Drayden / Iris",
                "cidade": "Opelucid City",
                "tipo": "Dragão",
                "insignia": "Legend"
            }
        ],

        "elite": [
            "Shauntal",
            "Marshal",
            "Grimsley",
            "Caitlin"
        ],

        "historia": [
            "Black e White apresentam inicialmente apenas espécies de Unova.",
            "A história trabalha fortemente a relação entre humanos e Pokémon.",
            "N é uma das figuras centrais da narrativa.",
            "Black 2 e White 2 acontecem posteriormente aos eventos dos jogos originais."
        ],

        "curiosidades": [
            "Unova foi a primeira região principal inspirada fortemente em uma área fora do Japão.",
            "Castelia City é uma das maiores cidades da franquia.",
            "A região possui o conhecido lema 'Truth vs. Ideals' associado à narrativa de Black e White.",
            "Black 2 e White 2 apresentam uma Unova modificada."
        ]
    },


    "Kalos": {

        "api": "kalos",

        "geracao": "Geração VI",

        "jogos": [
            "Pokémon X",
            "Pokémon Y"
        ],

        "descricao": (
            "Kalos é uma região marcada por elegância, tecnologia, "
            "belezas naturais e pela introdução da Mega Evolução."
        ),

        "professor": "Professor Sycamore",

        "campeao": "Diantha",

        "equipe_vila": "Equipe Flare",

        "mapa": "kalos.png",

        "caracteristicos": [
            "Chespin",
            "Fennekin",
            "Froakie",
            "Greninja",
            "Talonflame",
            "Sylveon",
            "Xerneas",
            "Yveltal",
            "Zygarde"
        ],

        "personagens": [
            "Professor Sycamore",
            "Calem",
            "Serena",
            "Shauna",
            "Tierno",
            "Trevor",
            "Diantha",
            "Lysandre"
        ],

        "vilao_descricao": (
            "A Equipe Flare é liderada por Lysandre, "
            "que busca criar um mundo que considera ideal."
        ),

        "ginasios": [

            {
                "lider": "Viola",
                "cidade": "Santalune City",
                "tipo": "Inseto",
                "insignia": "Bug"
            },

            {
                "lider": "Grant",
                "cidade": "Cyllage City",
                "tipo": "Pedra",
                "insignia": "Cliff"
            },

            {
                "lider": "Korrina",
                "cidade": "Shalour City",
                "tipo": "Lutador",
                "insignia": "Rumble"
            },

            {
                "lider": "Ramos",
                "cidade": "Coumarine City",
                "tipo": "Grama",
                "insignia": "Plant"
            },

            {
                "lider": "Clemont",
                "cidade": "Lumiose City",
                "tipo": "Elétrico",
                "insignia": "Voltage"
            },

            {
                "lider": "Valerie",
                "cidade": "Laverre City",
                "tipo": "Fada",
                "insignia": "Fairy"
            },

            {
                "lider": "Olympia",
                "cidade": "Anistar City",
                "tipo": "Psíquico",
                "insignia": "Psychic"
            },

            {
                "lider": "Wulfric",
                "cidade": "Snowbelle City",
                "tipo": "Gelo",
                "insignia": "Iceberg"
            }
        ],

        "elite": [
            "Malva",
            "Siebold",
            "Wikstrom",
            "Drasna"
        ],

        "historia": [
            "Kalos introduziu a Mega Evolução.",
            "A narrativa envolve a antiga guerra associada à arma suprema.",
            "AZ é uma figura histórica importante para a região.",
            "Xerneas e Yveltal representam forças lendárias centrais."
        ],

        "curiosidades": [
            "Kalos é fortemente inspirada na França.",
            "Lumiose City é uma das maiores cidades do mundo Pokémon.",
            "A região introduziu o tipo Fada.",
            "Greninja ganhou uma forma especial muito conhecida: Ash-Greninja."
        ]
    },


    "Alola": {

        "api": "alola",

        "geracao": "Geração VII",

        "jogos": [
            "Pokémon Sun",
            "Pokémon Moon",
            "Pokémon Ultra Sun",
            "Pokémon Ultra Moon"
        ],

        "descricao": (
            "Alola é formada por quatro ilhas principais e uma ilha artificial, "
            "com cultura inspirada no Havaí e um forte foco em tradições."
        ),

        "professor": "Professor Kukui",

        "campeao": "Treinador do jogador",

        "equipe_vila": "Equipe Skull / Fundação Aether / Necrozma",

        "mapa": "alola.png",

        "caracteristicos": [
            "Rowlet",
            "Litten",
            "Popplio",
            "Rockruff",
            "Mimikyu",
            "Solgaleo",
            "Lunala",
            "Necrozma"
        ],

        "personagens": [
            "Professor Kukui",
            "Hau",
            "Lillie",
            "Gladion",
            "Guzma",
            "Lusamine",
            "Nanu"
        ],

        "vilao_descricao": (
            "A Equipe Skull atua como uma organização problemática, "
            "enquanto a Fundação Aether esconde objetivos próprios "
            "durante a história."
        ),

        "ginasios": [],

        "elite": [
            "Hala",
            "Olivia",
            "Acerola",
            "Kahili"
        ],

        "historia": [
            "Alola substitui a estrutura tradicional de oito ginásios pelos desafios das ilhas.",
            "O jogador participa de Island Trials.",
            "Lillie e os Ultra Beasts são elementos centrais da narrativa.",
            "Necrozma assume papel de destaque em Ultra Sun e Ultra Moon."
        ],

        "curiosidades": [
            "Alola introduziu as formas regionais.",
            "O arquipélago é formado por ilhas com ambientes bastante diferentes.",
            "A região utiliza Z-Moves como uma das principais mecânicas.",
            "Pikachu possui diferentes chapéus durante aventuras e eventos relacionados a Alola."
        ]
    },


    "Galar": {

        "api": "galar",

        "geracao": "Geração VIII",

        "jogos": [
            "Pokémon Sword",
            "Pokémon Shield"
        ],

        "descricao": (
            "Galar possui grandes cidades, áreas rurais e o fenômeno "
            "Dynamax, que influencia fortemente as batalhas."
        ),

        "professor": "Professor Magnolia",

        "campeao": "Leon",

        "equipe_vila": "Team Yell / macro cosmos",

        "mapa": "galar.png",

        "caracteristicos": [
            "Grookey",
            "Scorbunny",
            "Sobble",
            "Corviknight",
            "Wooloo",
            "Zacian",
            "Zamazenta",
            "Eternatus"
        ],

        "personagens": [
            "Professor Magnolia",
            "Sonia",
            "Leon",
            "Hop",
            "Marnie",
            "Bede",
            "Rose",
            "Oleana"
        ],

        "vilao_descricao": (
            "O Team Yell interfere com os desafios da Liga, "
            "enquanto Rose e a Macro Cosmos estão ligados ao conflito central."
        ),

        "ginasios": [

            {
                "lider": "Milo",
                "cidade": "Turffield",
                "tipo": "Grama",
                "insignia": "Grass"
            },

            {
                "lider": "Nessa",
                "cidade": "Hulbury",
                "tipo": "Água",
                "insignia": "Water"
            },

            {
                "lider": "Kabu",
                "cidade": "Motostoke",
                "tipo": "Fogo",
                "insignia": "Fire"
            },

            {
                "lider": "Bea / Allister",
                "cidade": "Stow-on-Side",
                "tipo": "Lutador / Fantasma",
                "insignia": "Fighting / Ghost"
            },

            {
                "lider": "Opal",
                "cidade": "Ballonlea",
                "tipo": "Fada",
                "insignia": "Fairy"
            },

            {
                "lider": "Gordie / Melony",
                "cidade": "Circhester",
                "tipo": "Pedra / Gelo",
                "insignia": "Rock / Ice"
            },

            {
                "lider": "Piers",
                "cidade": "Spikemuth",
                "tipo": "Sombrio",
                "insignia": "Dark"
            },

            {
                "lider": "Raihan",
                "cidade": "Hammerlocke",
                "tipo": "Dragão",
                "insignia": "Dragon"
            }
        ],

        "elite": [],

        "historia": [
            "Galar introduz o fenômeno Dynamax e Gigantamax.",
            "A Liga Pokémon funciona como um grande espetáculo esportivo.",
            "Leon é conhecido como o campeão invicto da região.",
            "A história envolve a energia Dynamax e a ameaça de Eternatus."
        ],

        "curiosidades": [
            "Galar é fortemente inspirada no Reino Unido.",
            "A região possui o sistema de Wild Area.",
            "Gigantamax cria formas especiais para determinados Pokémon.",
            "Sword e Shield introduzem os Pokémon iniciais Grookey, Scorbunny e Sobble."
        ]
    },


    "Paldea": {

        "api": "paldea",

        "geracao": "Geração IX",

        "jogos": [
            "Pokémon Scarlet",
            "Pokémon Violet"
        ],

        "descricao": (
            "Paldea é uma região de mundo aberto, "
            "com escolas, cidades e uma grande variedade de ambientes."
        ),

        "professor": "Professor Sada / Professor Turo",

        "campeao": "Geeta",

        "equipe_vila": "Team Star",

        "mapa": "paldea.png",

        "caracteristicos": [
            "Sprigatito",
            "Fuecoco",
            "Quaxly",
            "Pawmi",
            "Lechonk",
            "Koraidon",
            "Miraidon",
            "Tinkaton"
        ],

        "personagens": [
            "Professor Sada",
            "Professor Turo",
            "Nemona",
            "Arven",
            "Penny",
            "Geeta",
            "Clavell"
        ],

        "vilao_descricao": (
            "A Team Star está ligada a um grupo de estudantes "
            "envolvidos em conflitos dentro da Academia."
        ),

        "ginasios": [

            {
                "lider": "Katy",
                "cidade": "Cortondo",
                "tipo": "Inseto",
                "insignia": "Inseto"
            },

            {
                "lider": "Brassius",
                "cidade": "Artazon",
                "tipo": "Grama",
                "insignia": "Grama"
            },

            {
                "lider": "Iono",
                "cidade": "Levincia",
                "tipo": "Elétrico",
                "insignia": "Elétrico"
            },

            {
                "lider": "Kofu",
                "cidade": "Cascarrafa",
                "tipo": "Água",
                "insignia": "Água"
            },

            {
                "lider": "Larry",
                "cidade": "Medali",
                "tipo": "Normal",
                "insignia": "Normal"
            },

            {
                "lider": "Ryme",
                "cidade": "Montenevera",
                "tipo": "Fantasma",
                "insignia": "Fantasma"
            },

            {
                "lider": "Tulip",
                "cidade": "Alfornada",
                "tipo": "Psíquico",
                "insignia": "Psíquico"
            },

            {
                "lider": "Grusha",
                "cidade": "Glaseado",
                "tipo": "Gelo",
                "insignia": "Gelo"
            }
        ],

        "elite": [
            "Rika",
            "Poppy",
            "Larry",
            "Hassel"
        ],

        "historia": [
            "Paldea apresenta três caminhos principais de aventura.",
            "O jogador participa da Victory Road, Path of Legends e Starfall Street.",
            "A região introduz a Terastalização.",
            "A Área Zero possui papel central nos acontecimentos finais."
        ],

        "curiosidades": [
            "Paldea é inspirada principalmente na Península Ibérica.",
            "O jogador pode explorar a região em uma estrutura de mundo aberto.",
            "Koraidon e Miraidon funcionam como parceiros de exploração.",
            "A Terastalização pode alterar o tipo de um Pokémon durante a batalha."
        ]
    }
}


# ============================================================
# RECURSOS EXTRAS DA ENCICLOPÉDIA
# ============================================================

REGIAO_ORDEM = [
    "Kanto", "Johto", "Hoenn", "Sinnoh", "Unova",
    "Kalos", "Alola", "Galar", "Paldea"
]

TIPOS_ICONE = {
    "Normal": "⚪", "Fogo": "🔥", "Água": "💧", "Elétrico": "⚡",
    "Grama": "🌿", "Gelo": "❄️", "Lutador": "🥊", "Veneno": "☠️",
    "Terra": "🌎", "Voador": "🪽", "Psíquico": "🔮", "Inseto": "🐛",
    "Pedra": "🪨", "Fantasma": "👻", "Dragão": "🐉", "Sombrio": "🌑",
    "Aço": "⚙️", "Fada": "✨"
}

ELITE_TIPOS = {
    "Kanto": {"Lorelei": "Gelo", "Bruno": "Lutador", "Agatha": "Fantasma", "Lance": "Dragão"},
    "Johto": {"Will": "Psíquico", "Koga": "Veneno", "Bruno": "Lutador", "Karen": "Sombrio"},
    "Hoenn": {"Sidney": "Sombrio", "Phoebe": "Fantasma", "Glacia": "Gelo", "Drake": "Dragão"},
    "Sinnoh": {"Aaron": "Inseto", "Bertha": "Terra", "Flint": "Fogo", "Lucian": "Psíquico"},
    "Unova": {"Shauntal": "Fantasma", "Marshal": "Lutador", "Grimsley": "Sombrio", "Caitlin": "Psíquico"},
    "Kalos": {"Malva": "Fogo", "Siebold": "Água", "Wikstrom": "Aço", "Drasna": "Dragão"},
    "Galar": {"Bea": "Lutador", "Gordie": "Pedra", "Melony": "Gelo", "Piers": "Sombrio"},
    "Paldea": {"Rika": "Terra", "Poppy": "Aço", "Larry": "Voador", "Hassel": "Dragão"},
}

CAMPEAO_DETALHES = {
    "Kanto": "O desafio final da Liga culmina no confronto contra o Campeão, consolidando a jornada iniciada em Pallet Town.",
    "Johto": "A Liga de Johto encerra a aventura principal e abre caminho para a conexão histórica com Kanto.",
    "Hoenn": "A Liga encerra a jornada regional após a exploração de cidades, rotas, Contest Halls e eventos lendários.",
    "Sinnoh": "A vitória na Liga coroa uma aventura ligada aos mitos da criação e aos lendários de Sinnoh.",
    "Unova": "A Liga está profundamente ligada ao conflito ideológico envolvendo Pokémon, treinadores e a Equipe Plasma.",
    "Kalos": "O título de Campeão fecha a jornada de Kalos, marcada pelo Professor Sycamore, Mega Evolução e a crise da Equipe Flare.",
    "Alola": "A primeira Liga de Alola representa a consolidação da tradição competitiva criada pelas Island Trials.",
    "Galar": "A Liga em Galar é apresentada como um grande espetáculo esportivo, culminando no Champion Cup.",
    "Paldea": "A avaliação final ocorre no contexto da Champion Assessment, após os caminhos Victory Road, Path of Legends e Starfall Street."
}

HISTORIA_DETALHADA = {
    "Kanto": [
        "🌱 A jornada começa em Pallet Town, com a entrega do primeiro Pokémon e a missão da Pokédex.",
        "🛤️ O protagonista atravessa cidades, rotas, cavernas e mares enquanto enfrenta oito ginásios.",
        "😈 A Equipe Rocket atua em vários pontos da região e busca explorar Pokémon e tecnologias raras.",
        "🔥 O evento de Cinnabar Island e a Mansão Pokémon conectam a história humana aos experimentos com Mewtwo.",
        "🏆 A Liga Pokémon encerra a campanha principal e estabelece Kanto como a base histórica da franquia."
    ],
    "Johto": [
        "🌸 Johto apresenta uma tradição antiga, santuários e cidades profundamente ligadas à cultura regional.",
        "🥚 O protagonista recebe seu Pokémon inicial e começa a investigar os acontecimentos envolvendo a Equipe Rocket.",
        "🗼 A Torre de Rádio e a Torre Queimada revelam partes importantes da história local.",
        "🕯️ Lugia, Ho-Oh e as feras lendárias ocupam papel central na identidade mitológica da região.",
        "🏆 A Liga de Johto leva o treinador à Victory Road e conecta diretamente a aventura com Kanto."
    ],
    "Hoenn": [
        "🌊 Hoenn é construída ao redor de mares, ilhas e uma forte relação entre terra e água.",
        "🔴 A Equipe Magma e a Equipe Aqua perseguem objetivos opostos ligados à expansão de terra e mar.",
        "🌋 Groudon, Kyogre e Rayquaza formam o núcleo lendário da crise climática da região.",
        "🧭 A exploração marítima amplia a sensação de aventura e cria múltiplas rotas de acesso.",
        "🏆 A Liga coroa a jornada após a resolução da crise ambiental."
    ],
    "Sinnoh": [
        "🏔️ Sinnoh possui uma geografia montanhosa e uma tradição antiga ligada à criação do mundo.",
        "🌌 A Equipe Galáctica busca controlar o espaço, o tempo e o mundo de acordo com sua visão.",
        "🐉 Dialga, Palkia e Giratina estão ligados aos mitos fundamentais da região.",
        "⛩️ Locais como Spear Pillar, Mt. Coronet e os lagos guardam peças importantes da mitologia.",
        "🏆 A Liga representa o fechamento da aventura contemporânea, com a elite especializada em diferentes áreas."
    ],
    "Unova": [
        "🏙️ Unova apresenta uma região mais urbana e cosmopolita, com forte destaque para Castelia City.",
        "🐲 A Equipe Plasma questiona a relação entre humanos e Pokémon e ganha força política sob Ghetsis.",
        "⚖️ N e o lendário ligado à versão do jogo tornam o conflito ideológico o centro da narrativa.",
        "🌀 Após a aventura original, Unova recebe consequências e mudanças exploradas em Black 2 e White 2.",
        "🏆 A Liga fecha a campanha mantendo a temática de identidade, amizade e ideologia."
    ],
    "Kalos": [
        "🌼 Kalos é conhecida por cidades elegantes, arte, tradição e a inspiração francesa de sua paisagem.",
        "💠 O Professor Sycamore apresenta ao protagonista a jornada e a pesquisa sobre Mega Evolução.",
        "😈 A Equipe Flare procura utilizar a arma final e impor uma visão extrema de beleza e sobrevivência.",
        "⚡ O evento de Geosenge Town e a arma antiga conectam o presente com a história de AZ.",
        "🏆 A Liga fecha a jornada enquanto Mega Evolução permanece como uma das marcas da região."
    ],
    "Alola": [
        "🏝️ Alola é formada por quatro ilhas principais e uma tradição baseada em Island Trials.",
        "🌺 Kahunas e capitães conduzem os desafios, substituindo a estrutura tradicional de oito ginásios.",
        "🌌 Ultra Beasts e Ultra Wormholes expandem a narrativa para dimensões além de Alola.",
        "😈 A Equipe Skull aparece como ameaça local, enquanto a Fundação Aether ocupa posição ambígua na história.",
        "🏆 A criação da Liga de Alola estabelece uma nova tradição competitiva para a região."
    ],
    "Galar": [
        "🏟️ Galar transforma a Liga Pokémon em um enorme evento esportivo acompanhado pelo público.",
        "⚔️ O fenômeno Dynamax e as formas Gigantamax estão integrados à cultura competitiva regional.",
        "😈 A história envolve Team Yell, Macro Cosmos e os acontecimentos ligados a Chairman Rose.",
        "🐺 Zacian e Zamazenta são fundamentais para a lenda regional e para a crise envolvendo o Darkest Day.",
        "🏆 O Champion Cup coloca o treinador no centro do espetáculo da Liga de Galar."
    ],
    "Paldea": [
        "🎓 A aventura começa na Academia Naranja ou Uva e se divide em três caminhos independentes.",
        "🛣️ Victory Road acompanha a jornada de Ginásios e da Liga; Path of Legends gira em torno dos Herba Mystica; Starfall Street envolve a Team Star.",
        "🧪 O Area Zero e o fenômeno Terastal estão no centro dos mistérios científicos da região.",
        "🤖 Koraidon ou Miraidon acompanham a exploração do mundo aberto e conectam a história às pesquisas do Professor Sada ou Turo.",
        "🌌 Os eventos de The Teal Mask e The Indigo Disk expandem a história de Paldea e conectam a região a Kitakami e Blueberry Academy."
    ]
}

EQUIPES_CRONOLOGIA = {
    "Kanto": [
        ("🟥 Equipe Rocket", "Atuação criminosa centrada em roubo, experimentos e exploração de Pokémon."),
        ("🏢 Silph Co.", "A crise na Silph Company mostra o alcance da Equipe Rocket sobre empresas estratégicas."),
        ("🧬 Mewtwo", "Os acontecimentos da Mansão Pokémon e de Cerulean Cave conectam a Rocket à criação de uma arma biológica."),
    ],
    "Johto": [
        ("📻 Retorno da Equipe Rocket", "A organização tenta recuperar o antigo poder após a ausência de Giovanni."),
        ("📡 Torre de Rádio", "A tomada da Radio Tower serve como tentativa pública de chamar Giovanni de volta."),
        ("❌ Dissolução", "Após a derrota, a organização abandona a região e se dispersa.")
    ],
    "Hoenn": [
        ("🌋 Equipe Magma", "Busca ampliar as terras e promove uma visão favorável à expansão continental."),
        ("🌊 Equipe Aqua", "Busca ampliar os mares e entra em conflito direto com a Magma."),
        ("🌎 Crise climática", "As metas de ambas as equipes colocam Groudon e Kyogre em rota de colisão.")
    ],
    "Sinnoh": [
        ("🌌 Equipe Galáctica", "Busca criar um novo mundo sob a liderança de Cyrus."),
        ("🔴 Comandantes", "Mars, Jupiter e Saturn trabalham para reunir recursos e capturar os lendários dos lagos."),
        ("⛰️ Spear Pillar", "O plano chega ao ápice no topo do Mt. Coronet, provocando uma crise de proporções regionais.")
    ],
    "Unova": [
        ("🟣 Equipe Plasma", "Questiona a captura e o treinamento de Pokémon, usando o discurso de libertação como instrumento político."),
        ("👑 N", "A figura de N encarna o conflito filosófico entre humanos e Pokémon."),
        ("🧠 Ghetsis", "O verdadeiro objetivo de poder de Ghetsis é revelado e torna a Plasma uma ameaça direta à região."),
        ("❄️ Neo Plasma", "Em Black 2 e White 2, a organização ressurge com objetivos ainda mais agressivos.")
    ],
    "Kalos": [
        ("🔥 Equipe Flare", "Procura construir um mundo considerado perfeito sob uma visão extrema de beleza."),
        ("👑 Lysandre", "Lysandre utiliza a riqueza e a tecnologia do grupo para ativar a arma ancestral."),
        ("💠 Arma definitiva", "O plano conecta a história antiga de AZ ao conflito do presente."),
    ],
    "Alola": [
        ("💀 Equipe Skull", "Uma equipe local de arruaceiros formada por jovens que não se encaixaram nos Trials tradicionais."),
        ("🏢 Fundação Aether", "Organização criada para proteger Pokémon, mas que ganha papel central nos conflitos com Ultra Beasts."),
        ("🌌 Ultra Wormholes", "A abertura de Ultra Wormholes transforma a ameaça em um fenômeno interdimensional."),
    ],
    "Galar": [
        ("🦎 Team Yell", "Grupo de fãs ligado a Marnie que interfere na jornada e nos desafios do protagonista."),
        ("🏢 Macro Cosmos", "Grande conglomerado empresarial associado ao projeto de energia de Galar."),
        ("☄️ Darkest Day", "Chairman Rose desencadeia uma crise ao tentar garantir energia para o futuro da região."),
    ],
    "Paldea": [
        ("⭐ Team Star", "Grupo estudantil formado em resposta a problemas de bullying e conflitos escolares."),
        ("🎓 Starfall Street", "O protagonista enfrenta as bases da Team Star e conhece as histórias dos líderes do grupo."),
        ("🧑‍🏫 Cassiopeia", "A identidade por trás do chamado inicial conduz o arco de Team Star."),
        ("🚗 Clavell e Penny", "A resolução do arco combina disciplina escolar, identidade pessoal e reconstrução do grupo."),
    ]
}

TIPOS_TIPOLOGIA = {
    "city": "🏙️ Cidade",
    "town": "🏘️ Vila",
    "island": "🏝️ Ilha",
    "route": "🛣️ Rota",
    "road": "🛣️ Estrada",
    "cave": "🕳️ Caverna",
    "mount": "⛰️ Montanha",
    "forest": "🌲 Floresta",
    "tower": "🗼 Torre",
    "sea": "🌊 Mar",
    "desert": "🏜️ Deserto",
    "lake": "🏞️ Lago",
}


def classificar_local(nome):
    texto = normalizar_nome(nome)
    for palavra, rotulo in TIPOS_TIPOLOGIA.items():
        if palavra in texto:
            return rotulo
    return "📍 Local"


def extrair_id_url(url):
    if not url:
        return None
    try:
        return int(str(url).rstrip('/').split('/')[-1])
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_area_local(url):
    return requisicao_api(url) if url else None


def imagem_pokemon(nome, dados=None):
    """Usa a imagem oficial da própria resposta da API, com fallback pelo nome."""
    if dados:
        sprite = (
            dados.get('sprites', {})
            .get('other', {})
            .get('official-artwork', {})
            .get('front_default')
        )
        if sprite:
            return sprite
    ids_fixos = {
        'oinkologne': 916, 'oinklonke': 916,
        'lycanroc': 745, 'oricorio': 741, 'maushold': 925
    }
    pid = ids_fixos.get(normalizar_nome(nome))
    if pid:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"
    return None


def detalhe_jogo(jogo, regiao):
    texto = jogo.lower()
    if 'remake' in texto or jogo in {'Pokémon FireRed', 'Pokémon LeafGreen', 'Pokémon HeartGold', 'Pokémon SoulSilver', 'Pokémon Omega Ruby', 'Pokémon Alpha Sapphire', 'Pokémon Brilliant Diamond', 'Pokémon Shining Pearl'}:
        categoria = '🔁 Remake'
    elif any(x in texto for x in ['yellow', 'crystal', 'emerald', 'platinum', 'ultra sun', 'ultra moon']) or 'Let\'s Go' in jogo:
        categoria = '✨ Versão especial / aprimorada'
    elif any(x in texto for x in ['sword', 'shield', 'scarlet', 'violet', 'red', 'blue', 'gold', 'silver', 'ruby', 'sapphire', 'diamond', 'pearl', 'black', 'white', 'x', 'y']):
        categoria = '🎮 Jogo principal'
    else:
        categoria = '🎮 Título relacionado'
    return categoria, f"{jogo} é uma das experiências ligadas a {regiao}, apresentando sua exploração, personagens, Pokémon e sistemas próprios da geração."


def navegar_regiao(delta):
    atual_nome = st.session_state.get(
        "select_regiao",
        st.session_state.get("regiao_atual", REGIAO_ORDEM[0])
    )
    atual = REGIAO_ORDEM.index(atual_nome)
    novo = REGIAO_ORDEM[(atual + delta) % len(REGIAO_ORDEM)]

    # IMPORTANTE: não alteramos o estado do selectbox aqui.
    # Guardamos a mudança para ser aplicada ANTES de o widget
    # ser criado no próximo rerun.
    st.session_state["regiao_pendente"] = novo


def abrir_secao(nome):
    # A seção também é aplicada no próximo rerun, antes do
    # selectbox ser instanciado. Isso evita o StreamlitAPIException.
    st.session_state["secao_pendente"] = nome


def ir_para_regiao_secao(regiao, nome):
    st.session_state["regiao_pendente"] = regiao
    st.session_state["secao_pendente"] = nome


# ============================================================
# SEÇÕES
# ============================================================

SECOES = [
    "🌎 Visão Geral",
    "🗺️ Mapa Interativo",
    "🏙️ Cidades e Vilas",
    "🛣️ Rotas & Encontros",
    "🏆 Ginásios",
    "👑 Elite Four & Campeão",
    "👥 Personagens",
    "😈 Equipes Vilãs",
    "📖 Pokédex da Região",
    "🐾 Pokémon Característicos",
    "📚 História & Cronologia",
    "🎮 Linha do Tempo dos Jogos",
    "⭐ Curiosidades"
]


# ============================================================
# SELEÇÃO DA REGIÃO
# ============================================================

# Aplica navegações pendentes ANTES de criar qualquer widget
# com essas chaves.
if "regiao_pendente" in st.session_state:
    novo_registro = st.session_state.pop("regiao_pendente")
    st.session_state["regiao_atual"] = novo_registro
    st.session_state["select_regiao"] = novo_registro

if "secao_pendente" in st.session_state:
    nova_secao = st.session_state.pop("secao_pendente")
    st.session_state["secao_regiao"] = nova_secao
    st.session_state["secao_seletor"] = nova_secao

if "select_regiao" not in st.session_state:
    st.session_state.select_regiao = st.session_state.get(
        "regiao_atual", REGIAO_ORDEM[0]
    )

if "secao_seletor" not in st.session_state:
    st.session_state.secao_seletor = st.session_state.get(
        "secao_regiao", SECOES[0]
    )

regiao_escolhida = st.selectbox(
    "🌎 Escolha uma região:",
    REGIAO_ORDEM,
    key="select_regiao"
)

st.session_state.regiao_atual = regiao_escolhida
dados_regiao = REGIOES[regiao_escolhida]

# Navegação entre regiões
col_ant, col_meio, col_prox = st.columns([1, 3, 1])
with col_ant:
    st.button(
        "⬅️ Região anterior",
        use_container_width=True,
        on_click=navegar_regiao,
        args=(-1,),
        key="btn_regiao_anterior"
    )
with col_meio:
    indice_regiao = REGIAO_ORDEM.index(regiao_escolhida) + 1
    st.markdown(
        f"<div style='text-align:center;font-weight:700'>🌎 {indice_regiao}/9 • {regiao_escolhida}</div>",
        unsafe_allow_html=True
    )
with col_prox:
    st.button(
        "Próxima região ➡️",
        use_container_width=True,
        on_click=navegar_regiao,
        args=(1,),
        key="btn_regiao_proxima"
    )


# ============================================================
# NAVEGAÇÃO INTERNA
# ============================================================

st.markdown("## 🧭 Navegação rápida pelo KAYZAC WORLD")

atalhos = [
    ("📖", "Pokédex da Região", "Catálogo regional"),
    ("🗺️", "Mapa Interativo", "Explore localidades"),
    ("🏙️", "Cidades e Vilas", "Conheça os centros"),
    ("🛣️", "Rotas & Encontros", "Veja Pokémon encontrados"),
    ("🏆", "Ginásios", "Líderes e insígnias"),
    ("👑", "Elite Four & Campeão", "A Liga regional"),
    ("😈", "Equipes Vilãs", "Cronologia das ameaças"),
    ("📚", "História & Cronologia", "Linha histórica"),
    ("🎮", "Linha do Tempo dos Jogos", "Jogos e detalhes"),
]
cols = st.columns(3)
for i, (icone, titulo, subtitulo) in enumerate(atalhos):
    with cols[i % 3]:
        if st.button(f"{icone} {titulo}\n{subtitulo}", key=f"atalho_{normalizar_nome(regiao_escolhida)}_{i}", use_container_width=True):
            abrir_secao(f"{icone} {titulo}")

secao = st.selectbox(
    "Escolha o que deseja explorar:",
    SECOES,
    key="secao_seletor"
)
st.session_state.secao_regiao = secao
st.divider()


# ============================================================
# BUSCAR DADOS DA API
# ============================================================

with st.spinner(
    f"🌎 Carregando dados de {regiao_escolhida}..."
):

    dados_api = buscar_regiao(
        dados_regiao["api"]
    )


# ============================================================
# IDENTIDADE
# ============================================================

if secao == "🌎 Visão Geral":

    st.header("🌎 KAYZAC WORLD")
    st.write(
        "Bem-vindo ao atlas interativo do KAYZAC. Aqui a antiga aba de Regiões "
        "vira o centro geográfico do projeto: cada região funciona como uma "
        "porta de entrada para cidades, rotas, Pokémon, ginásios, personagens, "
        "história e jogos."
    )

    st.divider()

    # --------------------------------------------------------
    # PAINEL DA REGIÃO ATUAL
    # --------------------------------------------------------
    st.subheader(f"📍 Você está em {regiao_escolhida}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Geração", dados_regiao.get("geracao", "—"))
    with col2:
        st.metric("👨‍🔬 Professor", dados_regiao.get("professor", "—"))
    with col3:
        st.metric("🏆 Campeão", dados_regiao.get("campeao", "—"))
    with col4:
        st.metric("😈 Ameaça", dados_regiao.get("equipe_vila", "—"))

    st.info(dados_regiao.get("descricao", "Explore esta região pelo atlas KAYZAC."))

    # --------------------------------------------------------
    # VIAJAR
    # --------------------------------------------------------
    st.markdown("## ✈️ Viajar pelo Mundo")
    st.caption("Escolha um destino e o KAYZAC leva você diretamente para a região escolhida.")

    cols_viagem = st.columns(3)
    for i, destino in enumerate(REGIAO_ORDEM):
        with cols_viagem[i % 3]:
            dados_destino = REGIOES[destino]
            with st.container(border=True):
                st.markdown(f"### 🌎 {destino}")
                st.caption(dados_destino.get("geracao", ""))
                st.write(dados_destino.get("descricao", ""))
                if destino == regiao_escolhida:
                    st.success("📍 Localização atual")
                else:
                    if st.button(
                        f"✈️ Viajar para {destino}",
                        key=f"viajar_{normalizar_nome(destino)}",
                        use_container_width=True,
                        on_click=ir_para_regiao_secao,
                        args=(destino, "🌎 Visão Geral"),
                    ):
                        pass

    st.divider()

    # --------------------------------------------------------
    # MAPA + ATALHOS
    # --------------------------------------------------------
    col_mapa, col_atalhos = st.columns([1.15, 1])

    with col_mapa:
        st.markdown(f"## 🗺️ Mapa de {regiao_escolhida}")
        caminho_mapa = PASTA_MAPAS / dados_regiao.get("mapa", "")
        if caminho_mapa.exists():
            st.image(str(caminho_mapa), use_container_width=True)
            st.caption("Mapa regional do KAYZAC WORLD.")
        else:
            st.warning("Mapa local ainda não encontrado na pasta `mapas/`.")

    with col_atalhos:
        st.markdown("## 🧭 Explorar região")
        atalhos_world = [
            ("🗺️", "Mapa Interativo", "Explore localidades"),
            ("🏙️", "Cidades e Vilas", "Centros e localidades"),
            ("🛣️", "Rotas & Encontros", "Áreas e Pokémon"),
            ("🏆", "Ginásios", "Líderes e insígnias"),
            ("👑", "Elite Four & Campeão", "A Liga regional"),
            ("👥", "Personagens", "Figuras importantes"),
            ("😈", "Equipes Vilãs", "Ameaças e organizações"),
            ("📖", "Pokédex da Região", "Espécies registradas"),
            ("🐾", "Pokémon Característicos", "Catálogo visual"),
            ("📚", "História & Cronologia", "Grandes acontecimentos"),
            ("🎮", "Linha do Tempo dos Jogos", "Jogos ligados à região"),
            ("⭐", "Curiosidades", "Detalhes especiais"),
        ]

        for i, (icone, titulo, subtitulo) in enumerate(atalhos_world):
            if st.button(
                f"{icone} {titulo}\n{subtitulo}",
                key=f"world_atalho_{normalizar_nome(regiao_escolhida)}_{i}",
                use_container_width=True,
                on_click=abrir_secao,
                args=(f"{icone} {titulo}",),
            ):
                pass

    st.divider()

    # --------------------------------------------------------
    # IDENTIDADE REGIONAL
    # --------------------------------------------------------
    st.markdown(f"## 🪪 Identidade de {regiao_escolhida}")

    col_id1, col_id2 = st.columns(2)
    with col_id1:
        st.markdown("### 🎮 Jogos")
        for jogo in dados_regiao.get("jogos", []):
            st.write(f"🎮 {jogo}")
    with col_id2:
        st.markdown("### 🐾 Pokémon característicos")
        for pokemon in dados_regiao.get("caracteristicos", []):
            st.write(f"🐾 {nome_bonito(pokemon)}")

    if dados_api:
        st.divider()
        st.markdown("### 📊 Dados geográficos carregados")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🗺️ Localidades", len(dados_api.get("locations", [])))
        with c2:
            st.metric("📖 Pokédexes", len(dados_api.get("pokedexes", [])))
        with c3:
            st.metric("🧭 Geração registrada", len(dados_api.get("version_groups", [])))


# ============================================================
# MAPA INTERATIVO
# ============================================================

elif secao == "🗺️ Mapa Interativo":

    st.header(f"🗺️ Mapa Interativo de {regiao_escolhida}")
    st.write("Selecione uma localidade para transformar o mapa em um atlas navegável.")

    locais = dados_api.get("locations", []) if dados_api else []
    nomes_locais = [nome_bonito(x.get("name", "")) for x in locais]
    nomes_locais = sorted([x for x in nomes_locais if x])

    filtro_mapa = st.text_input(
        "🔎 Filtrar localidades no mapa:",
        key=f"filtro_mapa_{normalizar_nome(regiao_escolhida)}"
    ).strip().lower()

    filtrados = [x for x in nomes_locais if not filtro_mapa or filtro_mapa in x.lower()]
    escolha_mapa = st.selectbox(
        "📍 Localidade selecionada:",
        ["— Escolha uma localidade —"] + filtrados[:200],
        key=f"mapa_local_{normalizar_nome(regiao_escolhida)}"
    )

    caminho_mapa = PASTA_MAPAS / dados_regiao["mapa"]
    col_mapa, col_info = st.columns([2, 1])

    with col_mapa:
        if caminho_mapa.exists():
            st.image(caminho_mapa, caption=f"Mapa de {regiao_escolhida}", use_container_width=True)
        else:
            st.warning("🗺️ O mapa local ainda não está na pasta `mapas/`.")
            st.code(f"mapas/{dados_regiao['mapa']}")

    with col_info:
        st.subheader("📍 Atlas")
        st.metric("Localidades", len(locais))
        st.metric("Pokédexes", len(dados_api.get("pokedexes", [])) if dados_api else 0)
        if escolha_mapa != "— Escolha uma localidade —":
            nome_api = normalizar_nome(escolha_mapa)
            encontrada = next((x for x in locais if normalizar_nome(x.get("name", "")) == nome_api), None)
            if encontrada:
                detalhes = buscar_local(encontrada.get("url"))
                st.markdown(f"### {classificar_local(escolha_mapa)}")
                st.write(f"**{escolha_mapa}**")
                if detalhes:
                    st.write(f"🧩 **Áreas:** {len(detalhes.get('areas', []))}")
                    st.write(f"🎮 **Registros de geração:** {len(detalhes.get('game_indices', []))}")
                    if st.button("🏙️ Abrir detalhes", key=f"mapa_detalhe_{normalizar_nome(escolha_mapa)}", use_container_width=True):
                        st.session_state[f"cidade_foco_{normalizar_nome(regiao_escolhida)}"] = escolha_mapa
                        abrir_secao("🏙️ Cidades e Vilas")

# ============================================================
# CIDADES E VILAS
# ============================================================

elif secao == "🏙️ Cidades e Vilas":

    st.header(f"🏙️ Cidades e Vilas de {regiao_escolhida}")
    st.write("Cada localidade combina dados da PokéAPI com informações de exploração para funcionar como uma ficha de atlas.")

    locais = dados_api.get("locations", []) if dados_api else []
    cidades = [x for x in locais if any(chave in x.get("name", "").lower() for chave in ["city", "town", "island", "village"])]
    cidades = sorted(cidades, key=lambda x: nome_bonito(x.get("name", "")))

    filtro = st.text_input("🔎 Procurar cidade, vila ou ilha:", key=f"filtro_cidades_{normalizar_nome(regiao_escolhida)}").strip().lower()
    cidades = [x for x in cidades if not filtro or filtro in nome_bonito(x.get("name", "")).lower()]

    foco = st.session_state.get(f"cidade_foco_{normalizar_nome(regiao_escolhida)}")
    if foco:
        st.info(f"📌 Local selecionado pelo mapa: **{foco}**")
        if st.button("✖️ Limpar local selecionado", key=f"limpar_foco_{normalizar_nome(regiao_escolhida)}"):
            del st.session_state[f"cidade_foco_{normalizar_nome(regiao_escolhida)}"]
            st.rerun()

    for local in cidades:
        nome = nome_bonito(local.get("name", ""))
        with st.expander(f"{classificar_local(nome)} {nome}", expanded=(foco == nome)):
            detalhes = buscar_local(local.get("url"))
            st.write(f"**🌎 Região:** {regiao_escolhida}")
            if detalhes:
                st.metric("🧩 Áreas internas", len(detalhes.get("areas", [])))
                jogos = [x.get("generation", {}).get("name", "") for x in detalhes.get("game_indices", [])]
                if jogos:
                    st.write("🎮 **Gerações com registro:** " + ", ".join(nome_bonito(x) for x in jogos))
                if detalhes.get("areas"):
                    st.markdown("**📍 Áreas e pontos de interesse:**")
                    for area in detalhes["areas"]:
                        st.write(f"• {nome_bonito(area.get('name', 'Área'))}")
            st.caption("💡 Use a seção Rotas & Encontros para consultar Pokémon ligados às áreas exploráveis.")

    if not cidades:
        st.info("Nenhuma cidade ou vila encontrada com esse filtro.")

# ============================================================
# ROTAS & ENCONTROS
# ============================================================

elif secao == "🛣️ Rotas & Encontros":

    st.header(f"🛣️ Rotas de {regiao_escolhida}")
    st.write("Escolha uma rota para consultar áreas e Pokémon encontrados. Os encontros são carregados sob demanda e ficam em cache.")

    locais = dados_api.get("locations", []) if dados_api else []
    rotas = [x for x in locais if any(p in x.get("name", "").lower() for p in ["route", "road"])]
    rotas = sorted(rotas, key=lambda x: nome_bonito(x.get("name", "")))

    if rotas:
        nomes_rotas = [nome_bonito(x.get("name", "")) for x in rotas]
        escolha = st.selectbox("🛣️ Escolha uma rota:", nomes_rotas, key=f"rota_escolhida_{normalizar_nome(regiao_escolhida)}")
        local = rotas[nomes_rotas.index(escolha)]
        detalhes = buscar_local(local.get("url"))

        st.subheader(f"{classificar_local(escolha)} {escolha}")
        if detalhes and detalhes.get("areas"):
            encontros = {}
            for area in detalhes.get("areas", []):
                area_dados = buscar_area_local(area.get("url"))
                if not area_dados:
                    continue
                for encontro in area_dados.get("pokemon_encounters", []):
                    p = encontro.get("pokemon", {})
                    nome = p.get("name")
                    if nome:
                        encontros[nome] = area_dados.get("names", [{}])[0].get("name", "") if area_dados.get("names") else area_dados.get("name", "")

            st.metric("🐾 Pokémon registrados", len(encontros))
            if encontros:
                filtro = st.text_input("🔎 Filtrar Pokémon encontrados:", key=f"filtro_encontros_{normalizar_nome(escolha)}").strip().lower()
                nomes = sorted([x for x in encontros if not filtro or filtro in x.lower()])
                cols = st.columns(4)
                for i, nome in enumerate(nomes):
                    with cols[i % 4]:
                        dados_poke = buscar_pokemon(nome)
                        sprite = imagem_pokemon(nome, dados_poke)
                        with st.container(border=True):
                            if sprite:
                                st.image(sprite, use_container_width=True)
                            st.markdown(f"**{nome_bonito(nome)}**")
                            if dados_poke:
                                tipos = [traduzir_tipo(t.get("type", {}).get("name")) for t in dados_poke.get("types", [])]
                                st.caption(" / ".join(tipos))
                            st.caption(f"📍 {nome_bonito(encontros[nome])}")
                            if st.button("📖 Pokédex", key=f"rota_poke_{normalizar_nome(escolha)}_{normalizar_nome(nome)}", use_container_width=True):
                                st.session_state["pokemon_focado"] = normalizar_nome(nome)
                                st.switch_page("pages/1_Pokedex.py")
            else:
                st.info("Nenhum encontro foi retornado pela API para as áreas desta rota.")
        else:
            st.info("Esta localidade não possui áreas de encontro registradas na API.")
    else:
        st.info("Nenhuma rota foi identificada automaticamente para esta região.")

# ============================================================
# GINÁSIOS
# ============================================================

elif secao == "🏆 Ginásios":

    st.header(f"🏆 Ginásios de {regiao_escolhida}")
    ginasios = dados_regiao.get("ginasios", [])

    if ginasios:
        filtro_tipo = st.selectbox("🔹 Filtrar por tipo:", ["Todos"] + sorted({ginasio.get("tipo", "") for ginasio in ginasios}), key=f"filtro_ginasio_{normalizar_nome(regiao_escolhida)}")
        for indice, ginasio in enumerate(ginasios, 1):
            if filtro_tipo != "Todos" and ginasio.get("tipo") != filtro_tipo:
                continue
            tipo = ginasio.get("tipo", "")
            with st.container(border=True):
                st.markdown(f"### 🏆 Ginásio {indice} • {ginasio.get('cidade', 'Cidade')}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**👤 Líder:** {ginasio.get('lider', '—')}")
                    st.write(f"**🏙️ Cidade:** {ginasio.get('cidade', '—')}")
                with c2:
                    st.write(f"**{TIPOS_ICONE.get(tipo, '🔹')} Tipo:** {tipo}")
                    st.write(f"**🎖️ Insígnia:** {ginasio.get('insignia', '—')}")
                with c3:
                    st.write("**🎯 Estilo de batalha**")
                    st.write(f"A estratégia gira em torno de golpes e resistências associados ao tipo **{tipo}**.")
                st.caption("ℹ️ As equipes dos líderes podem variar entre versões e remakes; esta ficha mantém a identidade regional do ginásio.")
    else:
        st.info("🌺 Esta região não utiliza a estrutura tradicional de oito ginásios.")
        if regiao_escolhida == "Alola":
            st.write("Alola utiliza Island Trials, Totem Pokémon e Kahunas.")
        elif regiao_escolhida == "Galar":
            st.write("Galar mistura ginásios, estádios e o grande espetáculo da Champion Cup.")

# ============================================================
# ELITE FOUR E CAMPEÃO
# ============================================================

elif secao == "👑 Elite Four & Campeão":

    st.header(f"👑 Liga Pokémon de {regiao_escolhida}")
    st.subheader("🏆 Campeão")
    st.success(dados_regiao.get("campeao", "—"))
    st.write(CAMPEAO_DETALHES.get(regiao_escolhida, "A conquista do título representa o ápice da jornada regional."))

    st.divider()
    elite = dados_regiao.get("elite", [])
    if elite:
        st.subheader("👑 Elite Four")
        cols = st.columns(4)
        for i, membro in enumerate(elite):
            tipo = ELITE_TIPOS.get(regiao_escolhida, {}).get(membro, "Especialista")
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"### 👑 {membro}")
                    st.write(f"{TIPOS_ICONE.get(tipo, '🔹')} **Especialidade:** {tipo}")
                    st.caption("Membro da Elite Four responsável por uma das especialidades que definem a Liga regional.")
    else:
        st.info("Esta região não possui uma Elite Four tradicional nesse formato.")

# ============================================================
# PERSONAGENS
# ============================================================

elif secao == "👥 Personagens":

    st.header(
        f"👥 Personagens de {regiao_escolhida}"
    )

    personagens = dados_regiao.get(
        "personagens",
        []
    )

    for personagem in personagens:

        st.write(
            f"👤 {personagem}"
        )


# ============================================================
# EQUIPES VILÃS
# ============================================================

elif secao == "😈 Equipes Vilãs":

    st.header(f"😈 Equipes e ameaças de {regiao_escolhida}")
    st.warning(dados_regiao.get("equipe_vila", "Nenhuma organização registrada."))
    st.write(dados_regiao.get("vilao_descricao", "A região possui diferentes conflitos e organizações ao longo de seus jogos."))

    st.divider()
    st.subheader("🕰️ Cronologia das equipes e ameaças")
    eventos = EQUIPES_CRONOLOGIA.get(regiao_escolhida, [])
    for numero, (titulo, descricao) in enumerate(eventos, 1):
        with st.container(border=True):
            st.markdown(f"### {numero}. {titulo}")
            st.write(descricao)

    st.divider()
    st.markdown("### 📖 Como esse arco se encaixa na história?")
    historia = HISTORIA_DETALHADA.get(regiao_escolhida, dados_regiao.get("historia", []))
    st.write(historia[2] if len(historia) > 2 else "O conflito das equipes faz parte da história regional.")

# ============================================================
# POKÉDEX DA REGIÃO
# ============================================================

elif secao == "📖 Pokédex da Região":

    st.header(
        f"📖 Pokédex de {regiao_escolhida}"
    )

    if not dados_api:

        st.error(
            "❌ Não foi possível carregar a Pokédex da região."
        )

    else:

        pokedexes = dados_api.get(
            "pokedexes",
            []
        )

        if not pokedexes:

            st.info(
                "Nenhuma Pokédex foi registrada."
            )

        else:

            nomes_pokedex = [

                nome_bonito(
                    p.get("name")
                )

                for p in pokedexes
            ]

            if len(nomes_pokedex) == 1:

                indice_pokedex = 0

            else:

                nome_escolhido = st.selectbox(
                    "📚 Escolha a Pokédex:",
                    nomes_pokedex
                )

                indice_pokedex = nomes_pokedex.index(
                    nome_escolhido
                )

            url_pokedex = pokedexes[
                indice_pokedex
            ].get(
                "url"
            )

            with st.spinner(
                "📖 Carregando Pokémon da Pokédex..."
            ):

                dados_pokedex = buscar_pokedex(
                    url_pokedex
                )

            if dados_pokedex:

                entradas = dados_pokedex.get(
                    "pokemon_entries",
                    []
                )

                st.write(
                    f"📚 Total de Pokémon: "
                    f"**{len(entradas)}**"
                )

                filtro_pokemon = st.text_input(
                    "🔎 Procurar Pokémon:",
                    key=f"filtro_pokedex_{normalizar_nome(regiao_escolhida)}"
                ).lower().strip()

                encontrados = []

                for entrada in entradas:

                    especie = entrada.get(
                        "pokemon_species",
                        {}
                    )

                    nome_pokemon = especie.get(
                        "name",
                        ""
                    )

                    if (
                        filtro_pokemon
                        and filtro_pokemon
                        not in nome_pokemon.lower()
                    ):

                        continue

                    encontrados.append(
                        (
                            entrada.get(
                                "entry_number"
                            ),
                            nome_pokemon
                        )
                    )

                encontrados = encontrados[
                    :150
                ]

                for numero_dex, nome in encontrados:

                    col1, col2 = st.columns(
                        [1, 4]
                    )

                    with col1:

                        st.write(
                            f"#{numero_dex}"
                        )

                    with col2:

                        st.write(
                            f"🐾 {nome_bonito(nome)}"
                        )

                if len(encontrados) >= 150:

                    st.caption(
                        "Mostrando até 150 resultados. "
                        "Use o filtro para localizar um Pokémon."
                    )


# ============================================================
# POKÉMON CARACTERÍSTICOS
# ============================================================

elif secao == "🐾 Pokémon Característicos":

    st.header(f"🐾 Pokémon de {regiao_escolhida}")
    st.write("Explore o catálogo regional com busca, número, tipo e paginação para evitar carregamentos desnecessários.")

    if not dados_api:
        st.error("❌ Não foi possível carregar os dados da região.")
    else:
        pokedexes = dados_api.get("pokedexes", [])
        pokedex_regional = next((p for p in pokedexes if normalizar_nome(regiao_escolhida) in p.get("name", "").lower()), None)
        if not pokedex_regional and pokedexes:
            pokedex_regional = pokedexes[0]

        if pokedex_regional:
            dados_pokedex = buscar_pokedex(pokedex_regional.get("url"))
            entradas = dados_pokedex.get("pokemon_entries", []) if dados_pokedex else []
            st.metric("📚 Registros regionais", len(entradas))

            filtro_nome = st.text_input("🔎 Nome:", key=f"filtro_caracteristicos_{normalizar_nome(regiao_escolhida)}").strip().lower()
            filtro_tipo = st.selectbox("🔹 Tipo:", ["Todos"] + sorted(TIPOS_ICONE.keys()), key=f"tipo_caracteristico_{normalizar_nome(regiao_escolhida)}")
            pagina = st.number_input("📄 Página:", min_value=1, value=1, step=1, key=f"pag_char_{normalizar_nome(regiao_escolhida)}")
            por_pagina = st.selectbox("📦 Pokémon por página:", [12, 24, 48], index=1, key=f"qtd_char_{normalizar_nome(regiao_escolhida)}")

            candidatos = []
            for entrada in entradas:
                especie = entrada.get("pokemon_species", {})
                nome = especie.get("name", "")
                if filtro_nome and filtro_nome not in nome.lower():
                    continue
                candidatos.append((entrada.get("entry_number", 0), nome))

            # Para o filtro de tipo, consulta somente os candidatos atuais.
            if filtro_tipo != "Todos":
                filtrados_tipo = []
                for numero, nome in candidatos:
                    dados = buscar_pokemon(nome)
                    tipos = {traduzir_tipo(t.get("type", {}).get("name")) for t in (dados or {}).get("types", [])}
                    if filtro_tipo in tipos:
                        filtrados_tipo.append((numero, nome))
                candidatos = filtrados_tipo

            candidatos = sorted(candidatos, key=lambda x: x[0])
            inicio = (pagina - 1) * por_pagina
            fim = inicio + por_pagina
            pagina_itens = candidatos[inicio:fim]
            total_paginas = max(1, (len(candidatos) + por_pagina - 1) // por_pagina)
            st.caption(f"Página {min(pagina, total_paginas)} de {total_paginas} • {len(candidatos)} resultados")

            if pagina > total_paginas:
                st.warning("A página selecionada está além do último resultado.")
            elif pagina_itens:
                cols = st.columns(4)
                for i, (numero_dex, nome) in enumerate(pagina_itens):
                    with cols[i % 4]:
                        dados = buscar_pokemon(nome)
                        sprite = imagem_pokemon(nome, dados)
                        with st.container(border=True):
                            if sprite:
                                st.image(sprite, use_container_width=True)
                            else:
                                st.write("🖼️ Sem imagem")
                            st.markdown(f"### #{numero_dex:03d}")
                            st.markdown(f"**{nome_bonito(nome)}**")
                            if dados:
                                tipos = [traduzir_tipo(t.get("type", {}).get("name")) for t in dados.get("types", [])]
                                if tipos:
                                    st.caption(" / ".join(tipos))
                            if st.button("📖 Abrir Pokédex", key=f"abrir_char_{normalizar_nome(regiao_escolhida)}_{numero_dex}_{normalizar_nome(nome)}", use_container_width=True):
                                st.session_state["pokemon_focado"] = normalizar_nome(nome)
                                st.switch_page("pages/1_Pokedex.py")
            else:
                st.info("Nenhum Pokémon encontrado com esses filtros.")
        else:
            st.warning("⚠️ Nenhuma Pokédex regional encontrada.")

# ============================================================
# HISTÓRIA & CRONOLOGIA
# ============================================================

elif secao == "📚 História & Cronologia":

    st.header(f"📚 História de {regiao_escolhida}")
    st.write("Uma linha do tempo narrativa para entender a identidade e os grandes acontecimentos da região.")

    historia = HISTORIA_DETALHADA.get(regiao_escolhida, dados_regiao.get("historia", []))
    for indice, acontecimento in enumerate(historia, 1):
        with st.container(border=True):
            st.markdown(f"### {indice:02d} • Capítulo da região")
            st.write(acontecimento)

    st.divider()
    st.subheader("🧭 Resumo histórico")
    st.info(dados_regiao.get("descricao", "A região possui sua própria tradição, personagens, Pokémon e conflitos."))

# ============================================================
# LINHA DO TEMPO DOS JOGOS
# ============================================================

elif secao == "🎮 Linha do Tempo dos Jogos":

    st.header(f"🎮 Linha do Tempo de {regiao_escolhida}")
    st.write("Aqui os jogos são apresentados como uma pequena cronologia, com categoria e contexto regional.")

    jogos = dados_regiao.get("jogos", [])
    for indice, jogo in enumerate(jogos, 1):
        categoria, descricao = detalhe_jogo(jogo, regiao_escolhida)
        with st.container(border=True):
            c1, c2 = st.columns([1, 5])
            with c1:
                st.markdown(f"## {indice}")
            with c2:
                st.markdown(f"### 🎮 {jogo}")
                st.write(f"**Categoria:** {categoria}")
                st.write(descricao)

    st.divider()
    st.markdown("### 📚 Jogos como parte da evolução da região")
    st.write("Remakes, versões especiais e continuações ajudam a revisitar a mesma região com novos sistemas, formas de exploração e conteúdo narrativo.")

# ============================================================
# CURIOSIDADES
# ============================================================

elif secao == "⭐ Curiosidades":

    st.header(
        f"⭐ Curiosidades sobre {regiao_escolhida}"
    )

    curiosidades = dados_regiao.get(
        "curiosidades",
        []
    )

    for curiosidade in curiosidades:

        st.write(
            f"⭐ {curiosidade}"
        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "🌎 KAYZAC WORLD • Atlas Interativo Pokémon"
)

st.caption(
    "Geografia, localidades e referências estruturadas "
    "com apoio da PokéAPI e do universo KAYZAC."
)
