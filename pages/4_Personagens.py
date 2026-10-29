from pathlib import Path
import shutil
import sys

# Instalador aditivo para a página pages/4_Personagens.py do KAYZAC.
# Coloque este arquivo na raiz do repositório e execute:
#   python adicionar_personagens_anime.py

ROOT = Path(__file__).resolve().parent
ALVO = ROOT / "pages" / "4_Personagens.py"
MARCADOR = "# PERSONAGENS_ANIME_KAYZAC_V1"

if not ALVO.is_file():
    print("ERRO: não encontrei pages/4_Personagens.py.")
    print("Coloque este instalador na raiz do projeto KAYZAC, ao lado de app.py.")
    sys.exit(1)

codigo = ALVO.read_text(encoding="utf-8")
if MARCADOR in codigo:
    print("A atualização do banco de personagens do anime já foi aplicada. Nada foi alterado.")
    sys.exit(0)

# 1) Acrescenta Anime à lista de regiões/áreas de filtro.
substituicoes = [
    (
        '    "Paldea",\n]\n\nCATEGORIAS = [',
        '    "Paldea",\n    "Anime",\n]\n\nCATEGORIAS = [',
        "lista de regiões",
    ),
    (
        '# Dados estruturados para a página. A ideia é ampliar esta base ao longo do projeto.\nPERSONAGENS = [',
        'ORIGENS_PERSONAGENS = ["Todas", "Jogos", "Anime"]\n\n# Dados estruturados para a página. A ideia é ampliar esta base ao longo do projeto.\nPERSONAGENS = [',
        "filtro por origem",
    ),
    (
        'col1, col2, col3 = st.columns([1, 1, 2])',
        'col1, col2, col3, col4 = st.columns([1, 1, 1, 2])',
        "layout dos filtros",
    ),
    (
        'with col3:\n    busca = st.text_input(',
        'with col3:\n    origem_personagem = st.selectbox(\n        "🎬 Origem", ORIGENS_PERSONAGENS, key="personagens_origem"\n    )\n\nwith col4:\n    busca = st.text_input(',
        "seletor de origem",
    ),
    (
        'm2.metric("🌎 Regiões no banco", len(REGIOES) - 1)',
        'm2.metric("🌎 Regiões e origens", len(REGIOES) - 1)',
        "rótulo da métrica",
    ),
]

# O bloco de personagens é inserido antes da seção FUNÇÕES, logo depois da lista existente.
marcador_fim_lista = '\n\n\n# ============================================================\n# FUNÇÕES\n# ============================================================\n'
bloco_personagens = r'''
# PERSONAGENS_ANIME_KAYZAC_V1
# Personagens centrais do anime que não estavam no banco dos jogos.
PERSONAGENS.extend([
    {"nome": "Ash Ketchum", "regiao": "Kanto", "categoria": "Protagonista", "jogo": "Anime Pokémon — série clássica e Jornadas", "papel": "Protagonista histórico do anime; viaja com Pikachu e busca se tornar um Mestre Pokémon.", "ace": "pikachu", "origem": "Anime"},
    {"nome": "Goh", "regiao": "Kanto", "categoria": "Protagonista", "jogo": "Pokémon Jornadas", "papel": "Coprotagonista de Jornadas; sonha em capturar todos os Pokémon e pesquisa Mew.", "ace": "cinderace", "origem": "Anime"},
    {"nome": "Chloe Cerise", "regiao": "Kanto", "categoria": "Aliado", "jogo": "Pokémon Jornadas", "papel": "Amiga de infância de Goh e filha do Professor Cerise; sua jornada ganha destaque ao lado de Eevee.", "ace": "eevee", "origem": "Anime"},
    {"nome": "Liko", "regiao": "Paldea", "categoria": "Protagonista", "jogo": "Pokémon Horizontes", "papel": "Uma das protagonistas de Horizontes; sua aventura começa com um pingente misterioso.", "ace": "meowscarada", "origem": "Anime"},
    {"nome": "Roy", "regiao": "Kanto", "categoria": "Protagonista", "jogo": "Pokémon Horizontes", "papel": "Protagonista de Horizontes que viaja com Fuecoco e uma Poké Bola antiga e misteriosa.", "ace": "skeledirge", "origem": "Anime"},
    {"nome": "Dot", "regiao": "Paldea", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Integrante dos Trovonautas, especialista em pesquisa e vídeos como Nidothing.", "ace": "quaquaval", "origem": "Anime"},
    {"nome": "Friede", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Treinador e líder dos Trovonautas, conhecido por viajar com o Capitão Pikachu.", "ace": "charizard", "origem": "Anime"},
    {"nome": "Capitão Pikachu", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Parceiro de Friede e capitão do dirigível dos Trovonautas.", "ace": "pikachu", "origem": "Anime"},
    {"nome": "Ann", "regiao": "Paldea", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Amiga de Liko da Academia Índigo e treinadora que também segue sua própria jornada.", "ace": "piplup", "origem": "Anime"},
    {"nome": "Gary Oak", "regiao": "Kanto", "categoria": "Rival", "jogo": "Anime Pokémon — série clássica e Jornadas", "papel": "Rival inicial de Ash; mais tarde atua como pesquisador Pokémon.", "ace": "blastoise", "origem": "Anime"},
    {"nome": "Paul", "regiao": "Sinnoh", "categoria": "Rival", "jogo": "Anime Pokémon — Diamante e Pérola", "papel": "Rival exigente de Ash, conhecido por sua abordagem rigorosa ao treinamento.", "ace": "electivire", "origem": "Anime"},
    {"nome": "Alain", "regiao": "Kalos", "categoria": "Rival", "jogo": "Pokémon XY / Mega Evolution", "papel": "Treinador focado em Mega Evolução e um dos rivais mais fortes enfrentados por Ash.", "ace": "charizard", "origem": "Anime"},
    {"nome": "Tracey Sketchit", "regiao": "Kanto", "categoria": "Aliado", "jogo": "Anime Pokémon — Ilhas Laranja", "papel": "Observador Pokémon que acompanha Ash e Misty durante a jornada pelas Ilhas Laranja.", "ace": "scyther", "origem": "Anime"},
    {"nome": "Max", "regiao": "Hoenn", "categoria": "Aliado", "jogo": "Anime Pokémon — Hoenn e Fronteira de Batalha", "papel": "Irmão mais novo de May; viaja com o grupo mesmo ainda sem ter idade para receber seu próprio Pokémon.", "ace": "ralts", "origem": "Anime"},
    {"nome": "Bonnie", "regiao": "Kalos", "categoria": "Aliado", "jogo": "Anime Pokémon XY", "papel": "Irmã mais nova de Clemont; viaja com Ash e cuida de Dedenne durante a aventura.", "ace": "dedenne", "origem": "Anime"},
    {"nome": "Amethio", "regiao": "Paldea", "categoria": "Antagonista", "jogo": "Pokémon Horizontes", "papel": "Treinador ligado aos Exploradores, inicialmente em busca do pingente de Liko.", "ace": "ceruledge", "origem": "Anime"},
    {"nome": "Ult", "regiao": "Paldea", "categoria": "Rival", "jogo": "Pokémon Horizontes", "papel": "Treinador competitivo que cruza o caminho de Liko e Roy e participa das aventuras de Horizontes.", "ace": "dragonite", "origem": "Anime"},
    {"nome": "Murdock", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Cozinheiro dos Trovonautas e tio de Dot.", "ace": "rockruff", "origem": "Anime"},
    {"nome": "Orla", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Mecânica dos Trovonautas, responsável pela manutenção do dirigível.", "ace": "metagross", "origem": "Anime"},
    {"nome": "Mollie", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Profissional de saúde dos Trovonautas, responsável por cuidar de pessoas e Pokémon.", "ace": "chansey", "origem": "Anime"},
    {"nome": "Ludlow", "regiao": "Anime", "categoria": "Aliado", "jogo": "Pokémon Horizontes", "papel": "Membro experiente dos Trovonautas, que também participa das expedições do grupo.", "ace": "quagsire", "origem": "Anime"},
    {"nome": "Zirc", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizontes", "papel": "Integrante dos Exploradores que participa das missões contra os Trovonautas.", "ace": "houndoom", "origem": "Anime"},
    {"nome": "Onia", "regiao": "Paldea", "categoria": "Organização / Vilão", "jogo": "Pokémon Horizontes", "papel": "Integrante dos Exploradores que atua ao lado de Zirc.", "ace": "skarmory", "origem": "Anime"},
])

# Personagens já cadastrados por causa dos jogos que também têm papéis importantes no anime.
PERSONAGENS_JOGOS_TAMBEM_NO_ANIME = {
    "Brock", "Misty", "Professor Oak", "May", "Dawn", "Iris", "Cilan",
    "Serena", "Clemont", "Lillie", "Gladion", "Kiawe", "Lana", "Mallow",
    "Sophocles", "Leon", "Hop", "Sonia", "Nemona", "Korrina", "Cynthia",
    "Lance", "Giovanni", "Lysandre", "N", "Ghetsis", "Hau", "Professor Kukui",
}
'''

# Aplica tudo em memória e só grava se todos os trechos esperados forem encontrados.
novo = codigo
for antigo, novo_trecho, nome in substituicoes:
    qtd = novo.count(antigo)
    if qtd != 1:
        print(f"ERRO: não consegui localizar com segurança o trecho de {nome} (ocorrências: {qtd}).")
        print("Nenhuma alteração foi gravada. Seu arquivo original continua intacto.")
        sys.exit(2)
    novo = novo.replace(antigo, novo_trecho, 1)

# Adiciona dados de anime depois da lista PERSONAGENS existente.
if novo.count(marcador_fim_lista) != 1:
    print("ERRO: não consegui localizar o final da lista PERSONAGENS com segurança.")
    print("Nenhuma alteração foi gravada. Seu arquivo original continua intacto.")
    sys.exit(2)
novo = novo.replace(marcador_fim_lista, bloco_personagens + marcador_fim_lista, 1)

# Torna o filtro de origem funcional antes de aplicar a categoria.
antigo_filtro = '''if categoria != "Todos":
    resultados = [p for p in resultados if p["categoria"] == categoria]

if busca:'''
novo_filtro = '''if origem_personagem == "Jogos":
    resultados = [p for p in resultados if p.get("origem", "Jogos") != "Anime"]
elif origem_personagem == "Anime":
    resultados = [
        p for p in resultados
        if p.get("origem") == "Anime" or p["nome"] in PERSONAGENS_JOGOS_TAMBEM_NO_ANIME
    ]

if categoria != "Todos":
    resultados = [p for p in resultados if p["categoria"] == categoria]

if busca:'''
if novo.count(antigo_filtro) != 1:
    print("ERRO: não consegui localizar o bloco de filtros dos resultados com segurança.")
    print("Nenhuma alteração foi gravada. Seu arquivo original continua intacto.")
    sys.exit(2)
novo = novo.replace(antigo_filtro, novo_filtro, 1)

# Acrescenta a etiqueta de origem à descrição geral sem mexer nas fichas existentes.
novo = novo.replace(
    '"Conheça protagonistas, rivais, professores, Líderes de Ginásio, Elite Four, Campeões,"\n    " aliados e os principais antagonistas de cada região."',
    '"Conheça protagonistas, rivais, professores, Líderes de Ginásio, Elite Four, Campeões,"\n    " aliados e antagonistas dos jogos e do anime Pokémon."',
    1,
)

# Verificação sintática antes de gravar o arquivo de destino.
try:
    compile(novo, str(ALVO), "exec")
except SyntaxError as erro:
    print(f"ERRO de sintaxe durante a montagem: {erro}")
    print("Nenhuma alteração foi gravada. Seu arquivo original continua intacto.")
    sys.exit(3)

backup = ALVO.with_suffix(ALVO.suffix + ".bak")
if not backup.exists():
    shutil.copy2(ALVO, backup)
ALVO.write_text(novo, encoding="utf-8")
print("Atualização concluída!")
print(f"Arquivo alterado: {ALVO}")
print(f"Backup salvo em: {backup}")
print("Foram acrescentados personagens do anime e o filtro 🎬 Origem (Todas/Jogos/Anime).")
print("Agora teste localmente e revise os dados antes de fazer commit no GitHub.")
