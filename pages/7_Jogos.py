from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import platform
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# ⚡ KAYZAC - MASTER POKEMON
# 🎮 PÁGINA 7 — KAYZAC GAME CENTER
#
# Versão expandida:
# • Emulação retro diretamente no navegador com EmulatorJS
# • Game Boy / GBC / GBA / NDS / NES / SNES / N64 / SEGA
# • 3DS experimental usando o core Azahar do EmulatorJS 4.3.0-pre
# • Launcher local para emuladores externos (3DS / Switch)
# • Modo streaming/Web client para máquinas fracas/celulares
# • Perfis de desempenho e experiência mobile
#
# O projeto não distribui ROMs, firmware, chaves ou BIOS.
# ============================================================


st.set_page_config(
    page_title="KAYZAC - Game Center",
    page_icon="🎮",
    layout="wide",
)


# ============================================================
# 📁 CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_JOGOS = BASE_DIR / "jogos"
PASTA_JOGOS_AVANCADOS = BASE_DIR / ".kayzac_game_cache"
PASTA_JOGOS_AVANCADOS.mkdir(exist_ok=True)


# ============================================================
# ⚙️ CONFIGURAÇÕES
# ============================================================

EMULATORJS_STABLE_CDN = "https://cdn.emulatorjs.org/stable/data/"
EMULATORJS_3DS_PRE_CDN = "https://cdn.emulatorjs.org/4.3.0-pre/data/"

# Retro direto no navegador.
MAX_BROWSER_ROM_MB = 128

# 3DS / Switch preparados para launcher local.
MAX_ADVANCED_FILE_MB = 1024

AZAHAR_URL = "https://github.com/azahar-emu/azahar"
RYUBING_URL = "https://github.com/Ryubing"
EMULATORJS_DOCS_URL = "https://emulatorjs.org/docs/"


# ============================================================
# 🗂️ SISTEMAS RETRO
# ============================================================

SISTEMAS_RETRO: dict[str, dict[str, Any]] = {
    "🎮 Game Boy": {
        "core": "gb",
        "scheme": "gb",
        "ext": [".gb"],
        "descricao": "Game Boy clássico.",
        "cdn": "stable",
    },
    "🎨 Game Boy Color": {
        "core": "gb",
        "scheme": "gb",
        "ext": [".gbc", ".gb"],
        "descricao": "Game Boy Color.",
        "cdn": "stable",
    },
    "🔥 Game Boy Advance": {
        "core": "gba",
        "scheme": "gba",
        "ext": [".gba"],
        "descricao": "Game Boy Advance — FireRed, LeafGreen, Ruby, Sapphire e Emerald.",
        "cdn": "stable",
    },
    "🟦 Nintendo DS": {
        "core": "desmume",
        "scheme": "nds",
        "ext": [".nds"],
        "descricao": "Nintendo DS — Diamond, Pearl, Platinum, HGSS, Black/White e B2W2.",
        "cdn": "stable",
    },
    "👾 NES / Famicom": {
        "core": "nes",
        "scheme": "nes",
        "ext": [".nes"],
        "descricao": "Nintendo Entertainment System.",
        "cdn": "stable",
    },
    "⭐ SNES / Super Famicom": {
        "core": "snes",
        "scheme": "snes",
        "ext": [".sfc", ".smc"],
        "descricao": "Super Nintendo.",
        "cdn": "stable",
    },
    "🕹️ Nintendo 64": {
        "core": "n64",
        "scheme": "n64",
        "ext": [".z64", ".n64", ".v64"],
        "descricao": "Nintendo 64.",
        "cdn": "stable",
    },
    "🔵 Sega Mega Drive": {
        "core": "segaMD",
        "scheme": "segaMD",
        "ext": [".md", ".gen"],
        "descricao": "Sega Mega Drive / Genesis.",
        "cdn": "stable",
    },
    "📺 Sega Master System": {
        "core": "segaMS",
        "scheme": "segaMS",
        "ext": [".sms"],
        "descricao": "Sega Master System.",
        "cdn": "stable",
    },
    "💨 Sega Game Gear": {
        "core": "segaGG",
        "scheme": "segaGG",
        "ext": [".gg"],
        "descricao": "Sega Game Gear.",
        "cdn": "stable",
    },
}


# ============================================================
# 🟣 3DS EXPERIMENTAL
# ============================================================

SISTEMA_3DS = "🟣 Nintendo 3DS — experimental"
DADOS_3DS = {
    "core": "azahar",
    "scheme": "",
    "ext": [".3ds", ".cci", ".3dz", ".3dsx"],
    "descricao": (
        "Experimental no navegador usando o core Azahar do EmulatorJS 4.3.0-pre. "
        "Como é uma pré-release, compatibilidade e estabilidade podem variar."
    ),
    "cdn": "3ds",
}


# ============================================================
# 🔴 SWITCH / EMULADORES EXTERNOS
# ============================================================

SISTEMAS_AVANCADOS: dict[str, dict[str, Any]] = {
    SISTEMA_3DS: DADOS_3DS,
    "🔴 Nintendo Switch — launcher local": {
        "core": None,
        "scheme": None,
        "ext": [".nsp", ".xci", ".nca"],
        "descricao": (
            "Nintendo Switch via emulador externo. O Game Center pode preparar "
            "o arquivo e iniciar um emulador instalado na máquina que executa o Streamlit."
        ),
        "cdn": None,
    },
}


EXTENSOES_BROWSER = {
    ext: nome
    for nome, dados in SISTEMAS_RETRO.items()
    for ext in dados["ext"]
}
EXTENSOES_BROWSER.update({ext: SISTEMA_3DS for ext in DADOS_3DS["ext"]})

EXTENSOES_AVANCADAS = {
    ext: nome
    for nome, dados in SISTEMAS_AVANCADOS.items()
    for ext in dados["ext"]
}


# ============================================================
# 🧠 PERFIS DE DESEMPENHO
# ============================================================

PERFIS = {
    "🪶 Ultra Leve": {
        "descricao": "Prioriza consumo baixo e telas pequenas. Ideal para celulares e PCs modestos.",
        "threads": False,
        "legacy": True,
        "hide_shader": True,
        "browser_mode": "mobile",
    },
    "⚖️ Equilibrado": {
        "descricao": "Equilíbrio entre desempenho, compatibilidade e qualidade visual.",
        "threads": True,
        "legacy": False,
        "hide_shader": False,
        "browser_mode": "desktop",
    },
    "🔥 Qualidade": {
        "descricao": "Deixa mais recursos disponíveis para qualidade visual em máquinas mais fortes.",
        "threads": True,
        "legacy": False,
        "hide_shader": False,
        "browser_mode": "desktop",
    },
}


# ============================================================
# 🐾 IDENTIDADE / RECONHECIMENTO DE JOGOS POKÉMON
# ============================================================

FAMILIAS_POKEMON = [
    ("fire red", "🔥 Kanto · FireRed"),
    ("leaf green", "🍃 Kanto · LeafGreen"),
    ("red", "🔴 Kanto · Red"),
    ("blue", "🔵 Kanto · Blue"),
    ("yellow", "⚡ Kanto · Yellow"),
    ("gold", "✨ Johto · Gold"),
    ("silver", "🌙 Johto · Silver"),
    ("crystal", "💎 Johto · Crystal"),
    ("ruby", "❤️‍🔥 Hoenn · Ruby"),
    ("sapphire", "💙 Hoenn · Sapphire"),
    ("emerald", "💚 Hoenn · Emerald"),
    ("diamond", "💎 Sinnoh · Diamond"),
    ("pearl", "🌸 Sinnoh · Pearl"),
    ("platinum", "⚙️ Sinnoh · Platinum"),
    ("heartgold", "✨ Johto · HeartGold"),
    ("soul silver", "🌙 Johto · SoulSilver"),
    ("soulsilver", "🌙 Johto · SoulSilver"),
    ("black 2", "⚫ Unova · Black 2"),
    ("white 2", "⚪ Unova · White 2"),
    ("black", "⚫ Unova · Black"),
    ("white", "⚪ Unova · White"),
    ("x", "🔷 Kalos · X"),
    ("y", "🔶 Kalos · Y"),
    ("omega ruby", "🔥 Hoenn · Omega Ruby"),
    ("alpha sapphire", "💙 Hoenn · Alpha Sapphire"),
    ("sun", "☀️ Alola · Sun"),
    ("moon", "🌙 Alola · Moon"),
    ("ultra sun", "☀️ Alola · Ultra Sun"),
    ("ultra moon", "🌙 Alola · Ultra Moon"),
    ("sword", "⚔️ Galar · Sword"),
    ("shield", "🛡️ Galar · Shield"),
    ("brilliant diamond", "💎 Sinnoh · Brilliant Diamond"),
    ("shining pearl", "🌸 Sinnoh · Shining Pearl"),
    ("legends arceus", "⚪ Hisui · Legends: Arceus"),
    ("scarlet", "🔴 Paldea · Scarlet"),
    ("violet", "🟣 Paldea · Violet"),
    ("let's go pikachu", "⚡ Kanto · Let's Go, Pikachu!"),
    ("lets go pikachu", "⚡ Kanto · Let's Go, Pikachu!"),
    ("let's go eevee", "🟤 Kanto · Let's Go, Eevee!"),
    ("lets go eevee", "🟤 Kanto · Let's Go, Eevee!"),
]


# ============================================================
# 🧰 FUNÇÕES GERAIS
# ============================================================


def detectar_sistema(nome_arquivo: str) -> str | None:
    extensao = Path(nome_arquivo).suffix.lower()
    return EXTENSOES_BROWSER.get(extensao) or EXTENSOES_AVANCADAS.get(extensao)


def nome_seguro(nome: str) -> str:
    stem = Path(nome).stem.strip()
    return stem[:90] or "Jogo"


def classificar_jogo_pokemon(nome: str) -> str | None:
    texto = str(nome).lower().replace("_", " ").replace("-", " ")
    for termo, rotulo in FAMILIAS_POKEMON:
        if termo in texto:
            return rotulo
    return None


def id_jogo(dados_rom: bytes, nome: str) -> int:
    assinatura = hashlib.sha256(
        dados_rom + nome.encode("utf-8", errors="ignore")
    ).hexdigest()
    return max(1, int(assinatura[:12], 16) % 2_000_000_000)


def salvar_upload_temporario(nome: str, dados: bytes) -> Path:
    assinatura = hashlib.sha256(dados).hexdigest()[:16]
    extensao = Path(nome).suffix.lower() or ".bin"
    destino = PASTA_JOGOS_AVANCADOS / f"{assinatura}{extensao}"
    destino.write_bytes(dados)
    return destino


def listar_jogos_locais(extensoes: set[str]) -> list[Path]:
    if not PASTA_JOGOS.exists():
        return []
    return [
        caminho
        for caminho in sorted(PASTA_JOGOS.iterdir())
        if caminho.is_file() and caminho.suffix.lower() in extensoes
    ]


def launcher_nome_sugerido(sistema: str) -> str:
    if "3DS" in sistema:
        return "Azahar"
    if "Switch" in sistema:
        return "Ryubing"
    return "Emulador"


def comandos_seguranca(caminho: str) -> list[str]:
    """Divide um campo de argumentos sem shell=True."""
    texto = str(caminho or "").strip()
    if not texto:
        return []
    if os.name == "nt":
        try:
            return shlex.split(texto, posix=False)
        except ValueError:
            return [texto]
    try:
        return shlex.split(texto)
    except ValueError:
        return [texto]


def iniciar_emulador_local(
    executavel: str,
    arquivo_jogo: str,
    argumentos: str = "",
) -> tuple[bool, str]:
    exe = Path(executavel.strip().strip('"'))
    jogo = Path(arquivo_jogo.strip().strip('"'))

    if not exe.exists():
        return False, f"Executável não encontrado: {exe}"

    if not jogo.exists():
        return False, f"Jogo não encontrado: {jogo}"

    comando = [str(exe)]
    comando.extend(comandos_seguranca(argumentos))
    comando.append(str(jogo))

    try:
        kwargs: dict[str, Any] = {
            "cwd": str(exe.parent),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }

        if os.name == "nt":
            kwargs["creationflags"] = getattr(
                subprocess,
                "CREATE_NEW_PROCESS_GROUP",
                0,
            )

        subprocess.Popen(comando, **kwargs)
        return True, "Processo iniciado."

    except OSError as erro:
        return False, f"Não foi possível iniciar o emulador: {erro}"


# ============================================================
# 🎮 PAYLOAD DO EMULATORJS
# ============================================================


def montar_payload_rom(
    dados_rom: bytes,
    nome_arquivo: str,
    sistema_nome: str,
    perfil_nome: str,
) -> dict[str, Any]:
    sistema = SISTEMAS_RETRO[sistema_nome] if sistema_nome in SISTEMAS_RETRO else DADOS_3DS

    return {
        "nome": Path(nome_arquivo).name,
        "nome_jogo": nome_seguro(nome_arquivo),
        "core": sistema["core"],
        "scheme": sistema["scheme"],
        "sistema": sistema_nome,
        "game_id": id_jogo(dados_rom, Path(nome_arquivo).name),
        "rom_base64": base64.b64encode(dados_rom).decode("ascii"),
        "tamanho": len(dados_rom),
        "perfil": perfil_nome,
        "pokemon": classificar_jogo_pokemon(nome_arquivo),
        "cdn": sistema["cdn"],
    }


def renderizar_emulador(payload: dict[str, Any]) -> None:
    perfil = PERFIS.get(payload.get("perfil", "⚖️ Equilibrado"), PERFIS["⚖️ Equilibrado"])
    eh_3ds = payload.get("core") == "azahar"
    cdn = EMULATORJS_3DS_PRE_CDN if eh_3ds else EMULATORJS_STABLE_CDN

    dados_json = json.dumps(
        {
            "nome": payload["nome"],
            "nome_jogo": payload["nome_jogo"],
            "core": payload["core"],
            "scheme": payload["scheme"],
            "sistema": payload["sistema"],
            "game_id": payload["game_id"],
            "rom_base64": payload["rom_base64"],
        },
        ensure_ascii=False,
    )

    controles = {
        0: {
            0: {"value": "x", "value2": "BUTTON_2"},
            1: {"value": "s", "value2": "BUTTON_4"},
            2: {"value": "v", "value2": "SELECT"},
            3: {"value": "enter", "value2": "START"},
            4: {"value": "up arrow", "value2": "DPAD_UP"},
            5: {"value": "down arrow", "value2": "DPAD_DOWN"},
            6: {"value": "left arrow", "value2": "DPAD_LEFT"},
            7: {"value": "right arrow", "value2": "DPAD_RIGHT"},
            8: {"value": "z", "value2": "BUTTON_1"},
            9: {"value": "a", "value2": "BUTTON_3"},
            10: {"value": "q", "value2": "LEFT_TOP_SHOULDER"},
            11: {"value": "e", "value2": "RIGHT_TOP_SHOULDER"},
            12: {"value": "tab", "value2": "LEFT_BOTTOM_SHOULDER"},
            13: {"value": "r", "value2": "RIGHT_BOTTOM_SHOULDER"},
            14: {"value": "", "value2": "LEFT_STICK"},
            15: {"value": "", "value2": "RIGHT_STICK"},
            16: {"value": "h", "value2": "LEFT_STICK_X:+1"},
            17: {"value": "f", "value2": "LEFT_STICK_X:-1"},
            18: {"value": "g", "value2": "LEFT_STICK_Y:+1"},
            19: {"value": "t", "value2": "LEFT_STICK_Y:-1"},
            20: {"value": "l", "value2": "RIGHT_STICK_X:+1"},
            21: {"value": "j", "value2": "RIGHT_STICK_X:-1"},
            22: {"value": "k", "value2": "RIGHT_STICK_Y:+1"},
            23: {"value": "i", "value2": "RIGHT_STICK_Y:-1"},
            24: {"value": "F2"},
            25: {"value": "F4"},
            26: {"value": "F6"},
            27: {"value": "F7"},
            28: {"value": "F8"},
            29: {"value": "F9"},
        },
        1: {},
        2: {},
        3: {},
    }

    botao_extra = """
        customKAYZAC: {
            visible: true,
            displayName: "⚡ KAYZAC",
            icon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>',
            callback: () => {
                try {
                    window.EJS_emulator.displayMessage("⚡ KAYZAC GAME CENTER", 1800);
                } catch (e) {
                    console.log("KAYZAC:", e);
                }
            }
        }
    """

    codigo_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
    :root {{
        --azul: #118cff;
        --azul-claro: #53b7ff;
        --texto: #f4f8ff;
        --texto-fraco: #aab9c8;
    }}
    html, body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: Arial, Helvetica, sans-serif;
        color: var(--texto);
    }}
    * {{ box-sizing: border-box; }}
    .game-center {{
        width: 100%;
        background:
            radial-gradient(circle at 10% 10%, rgba(17,140,255,.16), transparent 28%),
            radial-gradient(circle at 88% 10%, rgba(83,183,255,.10), transparent 25%),
            linear-gradient(180deg, #060a0f 0%, #05070a 100%);
        border: 1px solid rgba(83,183,255,.34);
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 18px 55px rgba(0,0,0,.32);
    }}
    .game-top {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }}
    .game-title {{ font-size: 1.25rem; font-weight: 800; }}
    .game-system {{ color: var(--texto-fraco); font-size: .9rem; margin-top: 4px; }}
    .toolbar {{
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 8px;
        margin-bottom: 12px;
    }}
    .toolbar button {{
        appearance: none;
        border: 1px solid rgba(83,183,255,.35);
        background: linear-gradient(180deg, #101b28, #0b121a);
        color: #edf7ff;
        border-radius: 11px;
        padding: 10px 8px;
        font-weight: 700;
        cursor: pointer;
        transition: transform .08s ease, border-color .12s ease, background .12s ease;
        min-height: 44px;
    }}
    .toolbar button:hover {{
        border-color: rgba(83,183,255,.78);
        background: linear-gradient(180deg, #132538, #0d1722);
    }}
    .toolbar button:active,
    .toolbar button.pressed {{
        transform: translateY(1px) scale(.985);
        border-color: var(--azul-claro);
        background: #10304c;
    }}
    .toolbar .danger {{ border-color: rgba(255,88,88,.35); }}
    .screen {{
        width: 100%;
        min-height: 650px;
        border-radius: 16px;
        overflow: hidden;
        background: #000;
        border: 1px solid rgba(255,255,255,.08);
    }}
    #game {{ width: 100%; height: 650px; }}
    .under-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 12px;
        color: var(--texto-fraco);
        font-size: .82rem;
    }}
    .hint {{
        margin-top: 12px;
        padding: 10px 12px;
        border-radius: 10px;
        background: rgba(17,140,255,.07);
        border: 1px solid rgba(17,140,255,.18);
        color: #cbd9e7;
        line-height: 1.45;
    }}
    .status {{ font-weight: 700; color: #8fd1ff; }}
    @media (max-width: 900px) {{
        .toolbar {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        #game, .screen {{ min-height: 520px; height: 520px; }}
    }}
    @media (max-width: 560px) {{
        .game-center {{ border-radius: 14px; padding: 10px; }}
        .toolbar {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        #game, .screen {{ min-height: 430px; height: 430px; }}
    }}
</style>
</head>
<body>
<div class="game-center" id="game-shell">
    <div class="game-top">
        <div>
            <div class="game-title">🎮 {html.escape(payload['nome_jogo'])}</div>
            <div class="game-system">{html.escape(payload['sistema'])} · Perfil: {html.escape(payload['perfil'])}</div>
        </div>
        <div class="status" id="status">⏳ Preparando emulador...</div>
    </div>

    <div class="toolbar" aria-label="Controles rápidos KAYZAC">
        <button id="save" type="button">💾 Quick Save</button>
        <button id="load" type="button">📂 Quick Load</button>
        <button id="slot" type="button">🔢 Trocar Slot</button>
        <button id="ff" type="button">⚡ Fast Forward</button>
        <button id="rewind" type="button">⏪ Rewind</button>
        <button id="slow" type="button">🐢 Slow Motion</button>
        <button id="fullscreen" type="button">⛶ Tela Cheia</button>
        <button id="restart" type="button" class="danger">🔄 Reiniciar</button>
        <button id="menu" type="button">⚙️ Menu</button>
        <button id="help" type="button">❓ Atalhos</button>
        <button id="focus" type="button">🎯 Focar Jogo</button>
        <button id="release" type="button">🖱️ Liberar Foco</button>
    </div>

    <div class="screen" id="screen"><div id="game"></div></div>

    <div class="under-bar">
        <span>🎮 Setas = D-pad · Z = A · X = B · A = X · S = Y · Q/E = L/R · Enter = Start</span>
        <span id="slot-label">Slot: 0</span>
    </div>

    <div class="hint" id="hint">
        💡 Save states, Quick Save/Load, Rewind, Fast Forward, Slow Motion,
        Gamepad, Screenshot e outras funções ficam disponíveis no EmulatorJS.
    </div>
</div>

<script>
(() => {{
    const PAYLOAD = {dados_json};
    const CONTROLS = {json.dumps(controles)};

    const statusEl = document.getElementById("status");
    const slotLabel = document.getElementById("slot-label");
    const hintEl = document.getElementById("hint");
    const screen = document.getElementById("screen");
    let slotAtual = 0;
    let emulatorCarregado = false;

    function base64ToBlobUrl(base64) {{
        const binario = atob(base64);
        const partes = [];
        const CHUNK = 1024 * 1024;
        for (let inicio = 0; inicio < binario.length; inicio += CHUNK) {{
            const fim = Math.min(inicio + CHUNK, binario.length);
            const tamanho = fim - inicio;
            const bytes = new Uint8Array(tamanho);
            for (let i = 0; i < tamanho; i++) bytes[i] = binario.charCodeAt(inicio + i);
            partes.push(bytes);
        }}
        return URL.createObjectURL(new Blob(partes, {{ type: "application/octet-stream" }}));
    }}

    const ROM_URL = base64ToBlobUrl(PAYLOAD.rom_base64);

    window.EJS_player = "#game";
    window.EJS_core = PAYLOAD.core;
    window.EJS_gameUrl = ROM_URL;
    window.EJS_gameName = PAYLOAD.nome_jogo;
    window.EJS_gameID = PAYLOAD.game_id;
    window.EJS_pathtodata = "{cdn}";
    window.EJS_language = "pt-BR";
    window.EJS_disableAutoLang = true;
    window.EJS_startOnLoaded = true;
    window.EJS_volume = 0.75;
    window.EJS_color = "#118cff";
    window.EJS_backgroundColor = "#05070a";
    window.EJS_askBeforeExit = true;
    window.EJS_disableLocalStorage = false;
    window.EJS_threads = {str(bool(perfil['threads'])).lower()};
    window.EJS_forceLegacyCores = {str(bool(perfil['legacy'])).lower()};
    window.EJS_browserMode = {json.dumps(perfil['browser_mode'])};
    window.EJS_defaultControls = CONTROLS;
    window.EJS_hideSettings = {json.dumps(['shader'] if perfil['hide_shader'] else [])};

    window.EJS_defaultOptions = {{
        "save-state-slot": 0,
        "save-state-location": "browser"
    }};

    window.EJS_Buttons = {{
        playPause: true,
        restart: true,
        mute: true,
        settings: true,
        fullscreen: true,
        saveState: true,
        loadState: true,
        screenRecord: true,
        gamepad: true,
        cheat: true,
        volume: true,
        saveSavFiles: true,
        loadSavFiles: true,
        quickSave: true,
        quickLoad: true,
        screenshot: true,
        cacheManager: true,
        exitEmulation: true,
        {botao_extra}
    }};

    window.EJS_ready = function() {{
        emulatorCarregado = true;
        statusEl.textContent = "🟢 Emulador pronto";
        statusEl.style.color = "#79e6a9";
        hintEl.innerHTML =
            "🔥 Jogo carregado. Use o menu do EmulatorJS ou os atalhos rápidos do KAYZAC. " +
            (PAYLOAD.core === "azahar" ? "🟣 3DS experimental: esta integração usa uma pré-release do EmulatorJS." : "");
    }};

    window.EJS_onGameStart = function() {{
        statusEl.textContent = "🟢 Jogando";
        statusEl.style.color = "#79e6a9";
    }};

    window.EJS_onExit = function() {{
        emulatorCarregado = false;
        statusEl.textContent = "⚪ Emulador encerrado";
        statusEl.style.color = "#aab9c8";
    }};

    function enviarTecla(key, down = true) {{
        const init = {{ key, code: key, bubbles: true, cancelable: true }};
        const evento = new KeyboardEvent(down ? "keydown" : "keyup", init);
        window.dispatchEvent(evento);
        document.dispatchEvent(evento);
    }}

    function cliqueTecla(buttonId, key, mensagem) {{
        document.getElementById(buttonId).addEventListener("click", () => {{
            enviarTecla(key, true);
            setTimeout(() => enviarTecla(key, false), 70);
            statusEl.textContent = mensagem;
        }});
    }}

    function segurarTecla(buttonId, key, mensagem) {{
        const button = document.getElementById(buttonId);
        let pressionado = false;
        const iniciar = (event) => {{
            event.preventDefault();
            if (pressionado) return;
            pressionado = true;
            button.classList.add("pressed");
            enviarTecla(key, true);
            statusEl.textContent = mensagem;
        }};
        const parar = (event) => {{
            if (event) event.preventDefault();
            if (!pressionado) return;
            pressionado = false;
            button.classList.remove("pressed");
            enviarTecla(key, false);
            if (emulatorCarregado) statusEl.textContent = "🟢 Jogando";
        }};
        button.addEventListener("pointerdown", iniciar);
        button.addEventListener("pointerup", parar);
        button.addEventListener("pointercancel", parar);
        button.addEventListener("pointerleave", parar);
    }}

    cliqueTecla("save", "F2", "💾 Quick Save");
    cliqueTecla("load", "F4", "📂 Quick Load");
    cliqueTecla("slot", "F6", "🔢 Slot alterado");
    segurarTecla("ff", "F7", "⚡ Fast Forward ativo");
    segurarTecla("rewind", "F8", "⏪ Rewind ativo");
    segurarTecla("slow", "F9", "🐢 Slow Motion ativo");

    document.getElementById("slot").addEventListener("click", () => {{
        slotAtual = (slotAtual + 1) % 10;
        slotLabel.textContent = "Slot: " + slotAtual;
    }});

    document.getElementById("fullscreen").addEventListener("click", async () => {{
        try {{
            if (screen.requestFullscreen) await screen.requestFullscreen();
        }} catch (erro) {{
            statusEl.textContent = "⚠️ O navegador bloqueou a tela cheia";
        }}
    }});

    document.getElementById("restart").addEventListener("click", () => {{
        if (window.EJS_emulator && typeof window.EJS_emulator.restart === "function") {{
            try {{ window.EJS_emulator.restart(); return; }} catch (erro) {{}}
        }}
        statusEl.textContent = "⚠️ Use Restart no menu EmulatorJS";
    }});

    document.getElementById("menu").addEventListener("click", () => {{
        hintEl.innerHTML =
            "⚙️ Use o menu do próprio EmulatorJS para configurações, Save State, Load State, " +
            "Gamepad, Cheats, Screenshot, volume, cache e outras funções.";
        statusEl.textContent = "⚙️ Menu EmulatorJS";
    }});

    document.getElementById("focus").addEventListener("click", () => {{
        const game = document.getElementById("game");
        game.setAttribute("tabindex", "0");
        game.focus();
        statusEl.textContent = "🎯 Foco no jogo";
    }});

    document.getElementById("release").addEventListener("click", () => {{
        document.body.focus();
        statusEl.textContent = "🖱️ Foco liberado";
    }});

    document.getElementById("help").addEventListener("click", () => {{
        hintEl.innerHTML =
            "<strong>🎮 Controles</strong><br>" +
            "Setas = direcional · Z = A · X = B · A = X · S = Y · " +
            "Enter = Start · V = Select · Q/E = L/R.<br><br>" +
            "<strong>⚡ Extras</strong><br>" +
            "F2 = Quick Save · F4 = Quick Load · F6 = Slot · " +
            "F7 = Fast Forward · F8 = Rewind · F9 = Slow Motion.";
        statusEl.textContent = "❓ Atalhos exibidos";
    }});

    window.addEventListener("beforeunload", () => {{
        try {{ URL.revokeObjectURL(ROM_URL); }} catch (erro) {{}}
    }});

    // Ajuda para ambientes com SharedArrayBuffer.
    const threadsInfo = {str(bool(perfil['threads'])).lower()};
    if (threadsInfo && !window.crossOriginIsolated) {{
        const aviso = " ⚠️ Threads avançadas não estão isoladas neste iframe; o navegador pode mantê-las desativadas.";
        hintEl.textContent += aviso;
    }}

    const loader = document.createElement("script");
    loader.src = "{cdn}loader.js";
    loader.async = false;
    loader.onload = () => {{
        statusEl.textContent = "⏳ Carregando core e jogo...";
    }};
    loader.onerror = () => {{
        statusEl.textContent = "❌ Não foi possível carregar o EmulatorJS";
        statusEl.style.color = "#ff7474";
        hintEl.innerHTML =
            "⚠️ Falha ao baixar o loader/core. Verifique sua conexão. " +
            (PAYLOAD.core === "azahar" ?
                " A versão 3DS usa uma pré-release do EmulatorJS; uma falha de compatibilidade é possível." : "");
    }};
    document.body.appendChild(loader);
}})();
</script>
</body>
</html>
"""

    components.html(codigo_html, height=850, scrolling=False)


# ============================================================
# 🏠 CABEÇALHO
# ============================================================

st.markdown(
    """
    <div style="
        background:
            radial-gradient(circle at 8% 10%, rgba(17,140,255,.18), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(83,183,255,.10), transparent 26%),
            linear-gradient(180deg, #070b10 0%, #05070a 100%);
        border: 1px solid rgba(83,183,255,.32);
        border-radius: 22px;
        padding: 26px;
        margin-bottom: 18px;
    ">
        <div style="font-size: 2.1rem; font-weight: 900;">
            🎮 KAYZAC GAME CENTER
        </div>
        <div style="margin-top: 7px; color: #aab9c8; font-size: 1.02rem;">
            O cantinho do treinador para jogar, salvar, acelerar e continuar sua aventura.
        </div>
        <div style="margin-top: 12px; color: #d8e8f6;">
            ⚡ Retro · 🟣 3DS experimental · 🔴 Switch avançado · 📱 Mobile · 💾 Saves
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.info(
    "🎮 O KAYZAC fornece a interface e a integração com os emuladores. "
    "Você deve usar apenas jogos, saves, BIOS/firmware e demais arquivos que tenha direito de usar. "
    "O site não inclui nem distribui ROMs, chaves ou firmware."
)


# ============================================================
# 🎛️ PAINEL GLOBAL
# ============================================================

painel1, painel2, painel3 = st.columns([1.2, 1.2, 1])

with painel1:
    perfil_escolhido = st.selectbox(
        "⚡ Perfil de desempenho",
        list(PERFIS),
        index=0,
        key="kayzac_perfil",
    )
    st.caption(PERFIS[perfil_escolhido]["descricao"])

with painel2:
    interface_escolhida = st.selectbox(
        "📱 Interface alvo",
        ["🤖 Automático", "📱 Celular", "🖥️ Computador"],
        key="kayzac_interface",
    )

with painel3:
    if st.button("🧹 Limpar jogo ativo", use_container_width=True, key="limpar_jogo_ativo"):
        st.session_state.pop("game_center_payload", None)
        st.rerun()


# ============================================================
# 🧭 GUIA RÁPIDO
# ============================================================

st.markdown("### 🧭 Escolha como você quer jogar")

modo = st.radio(
    "",
    [
        "🎮 Retro no navegador",
        "🟣 Nintendo 3DS experimental",
        "🔴 Nintendo Switch / emulador externo",
        "☁️ Streaming / Web Client",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="kayzac_modo_jogo",
)


# ============================================================
# 🎮 RETRO NO NAVEGADOR
# ============================================================

if modo == "🎮 Retro no navegador":
    st.markdown("## 🎮 Retro no navegador")
    st.caption(
        "Use esta área para os sistemas que o EmulatorJS suporta diretamente. "
        "Para Pokémon, GBA e NDS são os caminhos principais."
    )

    aba_upload, aba_pasta = st.tabs(["📁 Upload", "🗂️ Pasta jogos/"])

    with aba_upload:
        arquivo_upload = st.file_uploader(
            "Escolha uma ROM",
            type=[
                ext.lstrip(".")
                for dados in SISTEMAS_RETRO.values()
                for ext in dados["ext"]
            ],
            key="game_center_retro_upload",
        )

        if arquivo_upload:
            dados = arquivo_upload.getvalue()
            tamanho_mb = len(dados) / (1024 * 1024)
            deteccao = detectar_sistema(arquivo_upload.name)
            sistemas_validos = list(SISTEMAS_RETRO)
            sistema_padrao = deteccao if deteccao in sistemas_validos else sistemas_validos[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("📦 Arquivo", arquivo_upload.name)
            c2.metric("💾 Tamanho", f"{tamanho_mb:.2f} MB")
            c3.metric("🔎 Sistema", sistema_padrao.split(" ", 1)[1])

            sistema = st.selectbox(
                "🕹️ Sistema / core",
                sistemas_validos,
                index=sistemas_validos.index(sistema_padrao),
                key="retro_upload_sistema",
            )

            pokemon_rotulo = classificar_jogo_pokemon(arquivo_upload.name)
            if pokemon_rotulo:
                st.success(f"⚡ Pokémon detectado: **{pokemon_rotulo}**")

            if tamanho_mb > MAX_BROWSER_ROM_MB:
                st.error(
                    f"❌ O arquivo ultrapassa o limite do navegador de {MAX_BROWSER_ROM_MB} MB. "
                    "Para arquivos maiores, use um emulador externo/local."
                )
            elif st.button(
                "🎮 INICIAR AVENTURA",
                type="primary",
                use_container_width=True,
                key="retro_iniciar_upload",
            ):
                st.session_state["game_center_payload"] = montar_payload_rom(
                    dados,
                    arquivo_upload.name,
                    sistema,
                    perfil_escolhido,
                )
                st.rerun()

    with aba_pasta:
        jogos = listar_jogos_locais(set(EXTENSOES_BROWSER) & set(EXTENSOES_AVANCADAS) | set(EXTENSOES_BROWSER))

        if not PASTA_JOGOS.exists():
            st.warning(
                "📂 A pasta `jogos/` ainda não existe. Crie-a na raiz do projeto."
            )
        elif not jogos:
            st.info("📭 Não encontrei ROMs retro suportadas na pasta `jogos/`.")
        else:
            nomes = [p.name for p in jogos]
            nome_escolhido = st.selectbox(
                "🎮 Escolha um jogo",
                nomes,
                key="retro_pasta_nome",
            )
            caminho = PASTA_JOGOS / nome_escolhido
            deteccao = detectar_sistema(nome_escolhido)

            if deteccao not in SISTEMAS_RETRO:
                st.warning("⚠️ Este arquivo é suportado pelo Game Center, mas não pertence ao modo retro nesta seleção.")
            else:
                st.caption(
                    f"📦 {nome_escolhido} · {caminho.stat().st_size / (1024 * 1024):.2f} MB · "
                    f"{SISTEMAS_RETRO[deteccao]['descricao']}"
                )

                if st.button(
                    "🎮 JOGAR DA PASTA",
                    type="primary",
                    use_container_width=True,
                    key="retro_iniciar_pasta",
                ):
                    dados_local = caminho.read_bytes()
                    tamanho_mb = len(dados_local) / (1024 * 1024)
                    if tamanho_mb > MAX_BROWSER_ROM_MB:
                        st.error(
                            f"❌ Arquivo acima de {MAX_BROWSER_ROM_MB} MB. "
                            "Use o launcher externo."
                        )
                    else:
                        st.session_state["game_center_payload"] = montar_payload_rom(
                            dados_local,
                            caminho.name,
                            deteccao,
                            perfil_escolhido,
                        )
                        st.rerun()


# ============================================================
# 🟣 3DS EXPERIMENTAL
# ============================================================

elif modo == "🟣 Nintendo 3DS experimental":
    st.markdown("## 🟣 Nintendo 3DS — modo experimental")
    st.warning(
        "🧪 Esta opção usa o EmulatorJS 4.3.0-pre, que adiciona o core Azahar. "
        "É uma pré-release: pode haver jogos que não iniciem, travem ou apresentem problemas."
    )

    st.link_button("🌐 Projeto Azahar", AZAHAR_URL, use_container_width=False)

    st.markdown("### 📁 Carregar jogo 3DS")
    arquivo_3ds = st.file_uploader(
        "Extensões aceitas nesta integração",
        type=[ext.lstrip(".") for ext in DADOS_3DS["ext"]],
        key="game_center_3ds_upload",
    )

    if arquivo_3ds:
        dados_3ds = arquivo_3ds.getvalue()
        tamanho_mb = len(dados_3ds) / (1024 * 1024)
        st.metric("💾 Tamanho do arquivo", f"{tamanho_mb:.2f} MB")

        if st.button(
            "🟣 TENTAR RODAR 3DS NO NAVEGADOR",
            type="primary",
            use_container_width=True,
            key="iniciar_3ds_experimental",
        ):
            if tamanho_mb > MAX_BROWSER_ROM_MB:
                st.error(
                    f"❌ O arquivo ultrapassa {MAX_BROWSER_ROM_MB} MB nesta integração de navegador."
                )
            else:
                st.session_state["game_center_payload"] = montar_payload_rom(
                    dados_3ds,
                    arquivo_3ds.name,
                    SISTEMA_3DS,
                    perfil_escolhido,
                )
                st.rerun()

    st.divider()
    st.markdown("### 🖥️ Alternativa local: Azahar")
    st.write(
        "No seu próprio computador, também é possível usar o launcher local abaixo para abrir o jogo "
        "com uma instalação do Azahar."
    )
    st.caption(
        "Essa função executa o emulador na máquina que está executando o Streamlit. "
        "Em um site hospedado remotamente, isso não inicia programas no celular/PC do visitante."
    )

    exe_3ds = st.text_input(
        "📍 Caminho do executável do Azahar",
        placeholder=r"C:\Program Files\Azahar\azahar.exe",
        key="azahar_exe",
    )

    arquivo_3ds_local = st.text_input(
        "📍 Caminho do jogo 3DS",
        placeholder=r"C:\Jogos\Pokemon_X.3ds",
        key="azahar_jogo",
    )

    if st.button(
        "🚀 ABRIR NO AZAHAR",
        use_container_width=True,
        key="abrir_azahar_local",
    ):
        ok, mensagem = iniciar_emulador_local(exe_3ds, arquivo_3ds_local)
        (st.success if ok else st.error)("✅ " + mensagem if ok else "❌ " + mensagem)


# ============================================================
# 🔴 SWITCH / EMULADOR EXTERNO
# ============================================================

elif modo == "🔴 Nintendo Switch / emulador externo":
    st.markdown("## 🔴 Nintendo Switch — modo avançado")
    st.warning(
        "🧩 O Game Center não tenta fingir que Switch roda nativamente dentro de um iframe leve. "
        "Aqui usamos um launcher local para um emulador instalado na máquina ou um cliente de streaming."
    )

    st.link_button("🌐 Projeto Ryubing", RYUBING_URL, use_container_width=False)

    st.markdown("### 📁 Preparar jogo para o launcher")
    arquivo_switch = st.file_uploader(
        "Arquivo do jogo",
        type=[ext.lstrip(".") for ext in [".nsp", ".xci", ".nca"]],
        key="game_center_switch_upload",
    )

    caminho_preparado = ""

    if arquivo_switch:
        dados_switch = arquivo_switch.getvalue()
        tamanho_mb = len(dados_switch) / (1024 * 1024)
        st.metric("💾 Tamanho", f"{tamanho_mb:.2f} MB")

        if tamanho_mb > MAX_ADVANCED_FILE_MB:
            st.error(f"❌ O arquivo ultrapassa o limite de {MAX_ADVANCED_FILE_MB} MB desta página.")
        elif st.button(
            "📦 PREPARAR ARQUIVO LOCAL",
            use_container_width=True,
            key="preparar_switch",
        ):
            destino = salvar_upload_temporario(arquivo_switch.name, dados_switch)
            st.session_state["switch_prepared_path"] = str(destino)

    caminho_preparado = st.session_state.get("switch_prepared_path", "")
    if caminho_preparado:
        st.success(f"📦 Arquivo preparado: `{caminho_preparado}`")

    st.markdown("### 🚀 Launcher local")
    exe_switch = st.text_input(
        "📍 Caminho do executável do emulador",
        placeholder=r"C:\Emuladores\Ryubing\Ryujinx.exe",
        key="switch_exe",
    )

    jogo_switch = st.text_input(
        "📍 Caminho do jogo",
        value=caminho_preparado,
        placeholder=r"C:\Jogos\Pokemon_Scarlet.nsp",
        key="switch_jogo",
    )

    args_switch = st.text_input(
        "⚙️ Argumentos adicionais (opcional)",
        placeholder="",
        key="switch_args",
    )

    if st.button(
        "🚀 ABRIR EMULADOR DE SWITCH",
        type="primary",
        use_container_width=True,
        key="abrir_switch_local",
    ):
        ok, mensagem = iniciar_emulador_local(
            exe_switch,
            jogo_switch,
            args_switch,
        )
        (st.success if ok else st.error)("✅ " + mensagem if ok else "❌ " + mensagem)

    st.caption(
        "⚠️ A documentação do ecossistema Ryubing informa requisitos de hardware elevados para o emulador. "
        "Em celulares fracos, streaming tende a ser o caminho mais realista para sistemas pesados."
    )


# ============================================================
# ☁️ STREAMING / WEB CLIENT
# ============================================================

elif modo == "☁️ Streaming / Web Client":
    st.markdown("## ☁️ Jogar por streaming / Web Client")
    st.write(
        "Este modo é pensado para quando a emulação fica pesada demais para o aparelho do visitante. "
        "Você pode apontar o KAYZAC para um cliente web de streaming que já esteja rodando."
    )

    streaming_url = st.text_input(
        "🌐 URL do cliente web",
        placeholder="https://seu-servidor-ou-cliente.local/",
        key="kayzac_streaming_url",
    ).strip()

    if streaming_url:
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("🌐 Abrir streaming", streaming_url, use_container_width=True)
        with c2:
            st.link_button("↗️ Abrir em nova guia", streaming_url, use_container_width=True)

        if st.checkbox(
            "🖼️ Tentar incorporar dentro do KAYZAC",
            key="kayzac_streaming_embed",
        ):
            st.warning(
                "Alguns servidores bloqueiam incorporação por iframe (CSP/X-Frame-Options). "
                "Nesse caso, use o botão de abrir em nova guia."
            )
            try:
                components.iframe(streaming_url, height=720, scrolling=True)
            except Exception as erro:
                st.error(f"Não foi possível incorporar o cliente: {erro}")


# ============================================================
# 🎮 JOGO ATIVO
# ============================================================

payload_atual = st.session_state.get("game_center_payload")

if payload_atual:
    st.divider()
    st.markdown("## 🎮 AVENTURA EM ANDAMENTO")

    info1, info2, info3 = st.columns([2, 2, 1])
    with info1:
        st.success(f"🟢 **{payload_atual['nome']}**")
    with info2:
        st.caption(f"{payload_atual['sistema']} · {payload_atual['perfil']}")
        if payload_atual.get("pokemon"):
            st.caption(f"⚡ {payload_atual['pokemon']}")
    with info3:
        if st.button("⏹️ Parar", use_container_width=True, key="parar_emulador"):
            st.session_state.pop("game_center_payload", None)
            st.rerun()

    renderizar_emulador(payload_atual)


# ============================================================
# 💾 SAVE STATES & DADOS
# ============================================================

st.divider()
st.markdown("## 💾 Continuidade da aventura")

save_col1, save_col2 = st.columns(2)

with save_col1:
    st.markdown("### ⚡ Quick Save / Quick Load")
    st.write(
        "Os atalhos rápidos e os Save States são gerenciados pelo EmulatorJS e podem ficar "
        "associados ao navegador e ao gameID do jogo."
    )
    st.caption(
        "Para partidas importantes, use também a exportação de save/state disponível no menu do emulador."
    )

with save_col2:
    st.markdown("### 🛟 Regra de ouro do treinador")
    st.write(
        "Antes de fechar uma aventura longa, faça um save normal dentro do jogo e, quando necessário, "
        "um Save State externo. Assim você tem duas camadas de segurança."
    )


# ============================================================
# 📱 OTIMIZAÇÃO
# ============================================================

with st.expander("📱 Otimização para celulares fracos"):
    st.markdown(
        """
        **🪶 Ultra Leve**

        Reduz a quantidade de efeitos visuais e força a interface móvel do EmulatorJS. É o primeiro perfil a testar em aparelhos modestos.

        **⚖️ Equilibrado**

        Libera recursos de desempenho quando o navegador oferece infraestrutura adequada.

        **🔥 Qualidade**

        Pensado para computadores mais fortes, priorizando qualidade visual.

        **🧠 Dica importante:** a emulação pesada não pode ser tornada leve apenas pelo HTML do site. Quando CPU/GPU do aparelho não dão conta, o Game Center precisa migrar a execução para um PC/servidor e transmitir a imagem.
        """
    )

    if interface_escolhida == "📱 Celular":
        st.info(
            "📱 Interface móvel selecionada. Para sistemas retro, comece por Ultra Leve. "
            "Para 3DS/Switch, considere o modo de streaming."
        )
    elif interface_escolhida == "🖥️ Computador":
        st.info(
            "🖥️ Interface desktop selecionada. Em máquinas fortes, o perfil Equilibrado costuma ser um bom ponto de partida."
        )


# ============================================================
# 🧪 INFORMAÇÕES TÉCNICAS
# ============================================================

with st.expander("⚙️ Informações técnicas"):
    st.write(
        "O Game Center usa um componente HTML/JavaScript para o frontend de emulação retro, "
        "com armazenamento local do EmulatorJS e gameID por título. O 3DS usa separadamente "
        "a pré-release 4.3.0 do EmulatorJS, que inclui o core Azahar."
    )

    st.code(
        f"Python: {platform.python_version()}\n"
        f"Sistema do processo: {platform.system()}\n"
        f"Pasta de jogos: {PASTA_JOGOS}\n"
        f"Cache local de jogos avançados: {PASTA_JOGOS_AVANCADOS}\n"
        f"Retro CDN: {EMULATORJS_STABLE_CDN}\n"
        f"3DS experimental CDN: {EMULATORJS_3DS_PRE_CDN}\n"
        f"Limite navegador: {MAX_BROWSER_ROM_MB} MB\n"
        f"Limite avançado: {MAX_ADVANCED_FILE_MB} MB",
        language="text",
    )

    st.link_button("📚 Documentação do EmulatorJS", EMULATORJS_DOCS_URL, use_container_width=True)


# ============================================================
# 🏁 RODAPÉ
# ============================================================

st.divider()
st.caption(
    "⚡ KAYZAC - MASTER POKEMON · 🎮 GAME CENTER · "
    "Integrações de emulação são componentes separados do projeto KAYZAC. "
    "Pokémon e marcas relacionadas pertencem aos respectivos detentores."
)
