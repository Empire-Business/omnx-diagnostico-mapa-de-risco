#!/usr/bin/env python3
"""Valida o diagnóstico (dados.json) e gera mapa-de-risco.md e mapa-de-risco.html. Só biblioteca padrão.

Uso: gerar_mapa.py <dados.json> --insumos <pasta> --saida <pasta>
Imprime JSON. Sai com 0 quando gera, 1 quando recusa os dados e 2 quando não consegue ler ou gravar.
Rodar duas vezes com os mesmos dados dá os mesmos arquivos.
"""
import argparse
import html
import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PILARES = [
    ("posicionamento", "Posicionamento"),
    ("autoridade", "Autoridade percebida"),
    ("encaixe", "Encaixe entre público e oferta"),
    ("maturidade", "Maturidade comercial"),
    ("reposicionamento", "Risco de reposicionamento"),
]
AVISO = ("As notas são um julgamento da IA a partir dos arquivos lidos. Não medem resultado futuro e podem errar. "
         "Nota alta exige prova: toda nota de 4 para cima tem ao menos duas evidências comprovadas nos arquivos.")
INVERSA = "Neste pilar, nota alta significa risco baixo."


def status(n):
    if n is None:
        return "SEM DADOS"
    if n >= 4:
        return "APTO"
    if n >= 2.5:
        return "ATENÇÃO"
    return "CRÍTICO"


def fmt(n):
    return "sem nota" if n is None else f"{n:.1f}"


def validar(d, insumos):
    erros = []
    for campo in ("cliente", "data", "resumo", "veredito"):
        if not isinstance(d.get(campo), str) or not d[campo].strip():
            erros.append(f"falta o campo '{campo}'")
    prior = d.get("prioridades")
    if not isinstance(prior, list) or not (1 <= len(prior) <= 5) or not all(isinstance(p, str) and p.strip() for p in prior):
        erros.append("'prioridades' precisa ter de 1 a 5 itens de texto")
    if "nao_lidos" in d and not (isinstance(d["nao_lidos"], list) and all(isinstance(x, str) for x in d["nao_lidos"])):
        erros.append("'nao_lidos' precisa ser uma lista de textos")
    pil = d.get("pilares")
    if not isinstance(pil, dict):
        return erros + ["falta o bloco 'pilares'"]
    extras = sorted(set(pil) - {p for p, _ in PILARES})
    if extras:
        erros.append("pilar desconhecido: " + ", ".join(extras))
    avaliados = 0
    for pid, nome in PILARES:
        p = pil.get(pid)
        if not isinstance(p, dict):
            erros.append(f"falta o pilar '{pid}'")
            continue
        nota = p.get("nota", "ausente")
        if nota == "ausente":
            erros.append(f"{nome}: falta 'nota' (use null se não houver dados)")
            continue
        if not isinstance(p.get("recomendacao"), str) or not p["recomendacao"].strip():
            erros.append(f"{nome}: falta a recomendação")
        if nota is None:
            if not isinstance(p.get("falta"), str) or not p["falta"].strip():
                erros.append(f"{nome}: sem nota, diga em 'falta' o que não veio nos arquivos")
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            erros.append(f"{nome}: a nota precisa ser um número ou null")
            continue
        if not 1 <= nota <= 5 or (nota * 2) != int(nota * 2):
            erros.append(f"{nome}: nota {nota} inválida (de 1.0 a 5.0, de meia em meia)")
            continue
        avaliados += 1
        if not isinstance(p.get("justificativa"), str) or not p["justificativa"].strip():
            erros.append(f"{nome}: falta a justificativa")
        evid = p.get("evidencias")
        if not isinstance(evid, list) or not evid:
            erros.append(f"{nome}: toda nota precisa de ao menos uma evidência")
            continue
        provas = 0
        for i, e in enumerate(evid, 1):
            if not isinstance(e, dict) or e.get("tipo") not in ("prova", "indicio"):
                erros.append(f"{nome}, evidência {i}: 'tipo' precisa ser prova ou indicio")
                continue
            if not isinstance(e.get("texto"), str) or not e["texto"].strip():
                erros.append(f"{nome}, evidência {i}: falta o texto")
            fonte = e.get("fonte")
            if not isinstance(fonte, str) or not fonte.strip():
                erros.append(f"{nome}, evidência {i}: falta a fonte")
                continue
            alvo = (insumos / fonte).resolve()
            if insumos != alvo and insumos not in alvo.parents:
                erros.append(f"{nome}, evidência {i}: a fonte está fora da pasta de insumos: {fonte}")
            elif not alvo.is_file():
                erros.append(f"{nome}, evidência {i}: arquivo não encontrado nos insumos: {fonte}")
            elif e["tipo"] == "prova":
                provas += 1
        if nota >= 4 and provas < 2:
            erros.append(f"{nome}: nota {nota} exige ao menos 2 provas com arquivo existente; achei {provas}. "
                         "Baixe a nota ou traga prova verdadeira.")
    if avaliados == 0:
        erros.append("nenhum pilar tem nota: não há como fazer o diagnóstico")
    return erros


def calcular(d):
    notas = [d["pilares"][p]["nota"] for p, _ in PILARES if d["pilares"][p].get("nota") is not None]
    media = Decimal(str(sum(notas))) / Decimal(len(notas))
    geral = float(media.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    return geral, status(geral), len(notas)


# ---------- Markdown ----------

def gerar_md(d, geral, st, avaliados):
    linhas = [f"# Mapa de risco: {d['cliente']}", "", f"Data: {d['data']}", "", f"> {AVISO}", "",
              "## Resumo", "", d["resumo"], "",
              f"## Nota geral: {geral:.1f} de 5 ({st})"]
    if avaliados < 5:
        linhas += ["", f"Nota parcial: só {avaliados} de 5 pilares têm dados suficientes."]
    linhas += ["", "## Pilares", ""]
    for i, (pid, nome) in enumerate(PILARES, 1):
        p = d["pilares"][pid]
        linhas.append(f"### {i}. {nome}: {fmt(p.get('nota'))} ({status(p.get('nota'))})")
        linhas.append("")
        if pid == "reposicionamento":
            linhas += [f"*{INVERSA}*", ""]
        if p.get("nota") is None:
            linhas += [f"**O que faltou nos arquivos:** {p['falta']}", ""]
        else:
            linhas += ["**Justificativa:**", "", p["justificativa"], "", "**Evidências:**", ""]
            for e in p["evidencias"]:
                rotulo = "Prova" if e["tipo"] == "prova" else "Indício"
                onde = f", {e['onde']}" if e.get("onde") else ""
                linhas.append(f"- {rotulo}: {e['texto']} (`{e['fonte']}`{onde})")
            linhas.append("")
        linhas += ["**O que fazer agora:**", "", p["recomendacao"], "", "---", ""]
    linhas += ["## Veredito", "", d["veredito"], "", "### Prioridades", ""]
    linhas += [f"{i}. {x}" for i, x in enumerate(d["prioridades"], 1)]
    if d.get("nao_lidos"):
        linhas += ["", "## Arquivos que não foram lidos", ""] + [f"- {x}" for x in d["nao_lidos"]]
    return "\n".join(linhas) + "\n"


# ---------- HTML ----------

CSS = """
:root{--bg:#F4F5F7;--surface:#FFF;--ink:#16202E;--muted:#576272;--line:#D8DDE5;--accent:#475569;--ok:#15703B;--warn:#8A6410;--crit:#A32222;--none:#6B7280;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141A;--surface:#181E27;--ink:#E7ECF2;--muted:#9AA6B6;--line:#2A3340;--accent:#A8B4C6;--ok:#4FD08A;--warn:#E5BB5C;--crit:#F08A8A;--none:#9CA3AF;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#10141A;--surface:#181E27;--ink:#E7ECF2;--muted:#9AA6B6;--line:#2A3340;--accent:#A8B4C6;--ok:#4FD08A;--warn:#E5BB5C;--crit:#F08A8A;--none:#9CA3AF;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 "Segoe UI",system-ui,-apple-system,sans-serif;padding:0 16px}
.wrap{max-width:900px;margin:0 auto;padding:36px 0 48px;display:grid;gap:24px}
h1,h2,h3{line-height:1.2;margin:0}
h1{font-size:clamp(1.9rem,5vw,2.8rem);letter-spacing:-.01em}
h2{font-size:1.35rem}
p{margin:0}
.top{display:flex;justify-content:space-between;gap:16px;align-items:start}
.kicker{font-size:.85rem;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}
.date{color:var(--muted);font-size:.95rem;margin-top:6px}
button.tema{border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:8px;padding:8px 12px;font:inherit;font-size:.85rem;cursor:pointer;white-space:nowrap}
.aviso{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:0 10px 10px 0;padding:14px 18px;font-size:.95rem}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:22px}
.geral{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:center}
.nota{font-size:4rem;font-weight:800;line-height:1}
.nota small{font-size:1.1rem;color:var(--muted);font-weight:400}
.tag{display:inline-block;font-size:.76rem;font-weight:700;letter-spacing:.06em;padding:3px 10px;border-radius:999px;border:1px solid currentColor}
.ok{color:var(--ok)}.warn{color:var(--warn)}.crit{color:var(--crit)}.none{color:var(--none)}
.bars{display:grid;gap:8px;margin-top:14px}
.bar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;font-size:.88rem;align-items:center}
.bar div.track{grid-column:1/-1;height:6px;border-radius:3px;background:var(--line)}
.bar div.fill{height:6px;border-radius:3px;background:currentColor}
.bar b{text-align:right}
svg{display:block;width:100%;max-width:420px;margin:0 auto}
svg .grid{fill:none;stroke:var(--line);stroke-width:1}
svg .axis{stroke:var(--line);stroke-width:1}
svg .area{fill:var(--accent);fill-opacity:.18;stroke:var(--accent);stroke-width:2}
svg .pt{fill:var(--accent)}
svg text{fill:var(--muted);font-size:13px;font-family:inherit}
details{background:var(--surface);border:1px solid var(--line);border-radius:12px}
summary{padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;font-weight:700}
summary span.num{white-space:nowrap;font-size:1rem}
.corpo{padding:0 20px 20px;display:grid;gap:12px}
.corpo h3{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
ul,ol{margin:0;padding-left:1.2em;display:grid;gap:6px}
.fonte{color:var(--muted);font-size:.84rem;overflow-wrap:anywhere}
.tipo{font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-right:6px}
footer{color:var(--muted);font-size:.86rem;border-top:1px solid var(--line);padding-top:14px}
@media (max-width:640px){.geral{grid-template-columns:1fr}.nota{font-size:3.2rem}}
@media print{button.tema{display:none}details{break-inside:avoid}}
"""

JS = """
var b=document.querySelector('.tema');if(b){b.addEventListener('click',function(){var r=document.documentElement;
var escuro=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
r.dataset.theme=escuro?'light':'dark';});}
"""


def classe(st):
    return {"APTO": "ok", "ATENÇÃO": "warn", "CRÍTICO": "crit", "SEM DADOS": "none"}[st]


def radar(d):
    cx, cy, raio, n = 170, 170, 108, len(PILARES)
    def ponto(i, r):
        a = 2 * math.pi * i / n - math.pi / 2
        return cx + r * math.cos(a), cy + r * math.sin(a)
    partes = []
    for nivel in range(1, 6):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (ponto(i, raio * nivel / 5) for i in range(n)))
        partes.append(f'<polygon class="grid" points="{pts}"/>')
    rotulos = ["Posicionamento", "Autoridade", "Encaixe", "Maturidade", "Reposicionamento"]
    area = []
    for i, (pid, _) in enumerate(PILARES):
        x, y = ponto(i, raio)
        partes.append(f'<line class="axis" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')
        nota = d["pilares"][pid].get("nota")
        area.append(ponto(i, raio * (nota or 0) / 5))
        lx, ly = ponto(i, raio + 20)
        anc = "middle" if abs(lx - cx) < 8 else ("start" if lx > cx else "end")
        extra = "" if nota is not None else " (sem nota)"
        partes.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" dominant-baseline="middle">{rotulos[i]}{extra}</text>')
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in area)
    partes.append(f'<polygon class="area" points="{pts}"/>')
    for x, y in area:
        partes.append(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="3.5"/>')
    legenda = "; ".join(f"{nome}: {fmt(d['pilares'][pid].get('nota'))}" for pid, nome in PILARES)
    return f'<svg viewBox="-90 20 520 300" role="img" aria-label="Radar das notas. {html.escape(legenda)}">{"".join(partes)}</svg>'


def gerar_html(d, geral, st, avaliados):
    e = html.escape
    barras, cartoes = [], []
    for i, (pid, nome) in enumerate(PILARES, 1):
        p = d["pilares"][pid]
        n = p.get("nota")
        s = status(n)
        largura = 0 if n is None else n * 20
        barras.append(f'<div class="bar {classe(s)}"><span style="color:var(--ink)">{e(nome)}</span><b>{fmt(n)}</b>'
                      f'<div class="track"><div class="fill" style="width:{largura:.0f}%"></div></div></div>')
        corpo = []
        if pid == "reposicionamento":
            corpo.append(f"<p><em>{INVERSA}</em></p>")
        if n is None:
            corpo.append(f"<h3>O que faltou nos arquivos</h3><p>{e(p['falta'])}</p>")
        else:
            itens = "".join(
                f'<li><span class="tipo">{"Prova" if x["tipo"] == "prova" else "Indício"}</span>{e(x["texto"])} '
                f'<span class="fonte">({e(x["fonte"])}{", " + e(x["onde"]) if x.get("onde") else ""})</span></li>'
                for x in p["evidencias"])
            corpo.append(f"<h3>Justificativa</h3><p>{e(p['justificativa'])}</p><h3>Evidências</h3><ul>{itens}</ul>")
        corpo.append(f"<h3>O que fazer agora</h3><p>{e(p['recomendacao'])}</p>")
        cartoes.append(f'<details open><summary><span>{i}. {e(nome)}</span>'
                       f'<span class="num {classe(s)}">{fmt(n)} <span class="tag">{s}</span></span></summary>'
                       f'<div class="corpo">{"".join(corpo)}</div></details>')
    parcial = f'<p class="date">Nota parcial: só {avaliados} de 5 pilares têm dados suficientes.</p>' if avaliados < 5 else ""
    prior = "".join(f"<li>{e(x)}</li>" for x in d["prioridades"])
    nao = ""
    if d.get("nao_lidos"):
        nao = '<section class="card"><h2>Arquivos que não foram lidos</h2><ul style="margin-top:10px">' + "".join(f"<li>{e(x)}</li>" for x in d["nao_lidos"]) + "</ul></section>"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa de risco · {e(d['cliente'])}</title>
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <header class="top">
    <div><div class="kicker">Mapa de risco</div><h1>{e(d['cliente'])}</h1><div class="date">{e(d['data'])}</div></div>
    <button class="tema" type="button">Tema claro ou escuro</button>
  </header>
  <p class="aviso">{AVISO}</p>
  <section class="card geral">
    <div>
      <div class="kicker">Nota geral</div>
      <div class="nota {classe(st)}">{geral:.1f} <small>de 5</small></div>
      <p style="margin-top:8px"><span class="tag {classe(st)}">{st}</span></p>
      {parcial}
      <p style="margin-top:12px">{e(d['resumo'])}</p>
      <div class="bars">{''.join(barras)}</div>
    </div>
    <div>{radar(d)}</div>
  </section>
  {''.join(cartoes)}
  <section class="card">
    <h2>Veredito</h2>
    <p style="margin:10px 0 14px">{e(d['veredito'])}</p>
    <h2 style="font-size:1.05rem;margin-bottom:8px">Prioridades</h2>
    <ol>{prior}</ol>
  </section>
  {nao}
  <footer>{AVISO}</footer>
</main>
<script>{JS}</script>
</body>
</html>
"""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("dados")
    a.add_argument("--insumos", required=True)
    a.add_argument("--saida", required=True)
    args = a.parse_args()

    def falha(codigo, *msgs):
        print(json.dumps({"ok": False, "erros": list(msgs)}, ensure_ascii=False, indent=2))
        return codigo

    insumos = Path(args.insumos).expanduser().resolve()
    saida = Path(args.saida).expanduser().resolve()
    skill = Path(__file__).resolve().parent.parent
    if not insumos.is_dir():
        return falha(2, f"a pasta de insumos não existe: {insumos}")
    if not any(p.is_file() and p.name != ".DS_Store" for p in insumos.rglob("*")):
        return falha(2, "a pasta de insumos está vazia")
    for proibida, nome in ((insumos, "de insumos"), (skill, "da skill")):
        if saida == proibida or proibida in saida.parents:
            return falha(2, f"a pasta de saída não pode ficar dentro da pasta {nome}")
    try:
        d = json.loads(Path(args.dados).expanduser().read_text(encoding="utf-8-sig"))
    except OSError:
        return falha(2, f"não encontrei o arquivo de dados: {args.dados}")
    except json.JSONDecodeError as e:
        return falha(2, f"o JSON de dados está com erro na linha {e.lineno}")
    if not isinstance(d, dict):
        return falha(1, "o JSON de dados precisa ser um objeto")
    erros = validar(d, insumos)
    if erros:
        return falha(1, *erros)
    geral, st, avaliados = calcular(d)
    try:
        saida.mkdir(parents=True, exist_ok=True)
        md = saida / "mapa-de-risco.md"
        ht = saida / "mapa-de-risco.html"
        md.write_text(gerar_md(d, geral, st, avaliados), encoding="utf-8")
        ht.write_text(gerar_html(d, geral, st, avaliados), encoding="utf-8")
    except OSError as e:
        return falha(2, f"não consegui gravar em {saida}: {e.strerror}")
    print(json.dumps({"ok": True, "nota_geral": geral, "status": st, "pilares_avaliados": avaliados,
                      "arquivos": [str(md), str(ht)]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
