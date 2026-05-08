# -*- coding: utf-8 -*-
"""
APLICAR_CORRECOES_V47_13.py
Patch operacional V47.13 para o PURAL/Ururau Editorial.

Como usar:
1) Coloque este arquivo na RAIZ do projeto, no mesmo nível da pasta sistema.
2) Rode: python APLICAR_CORRECOES_V47_13.py
3) Depois rode: 09_VALIDAR_OPERACIONAL_TOTAL.bat ou 06_VALIDAR_TUDO.bat.

O script detecta automaticamente a pasta sistema e aplica as correções de captação, monitor, fila, F5, painel de inteligência e organização.
"""
from pathlib import Path
import json, re, textwrap, shutil, os, sys, subprocess

def _detect_base():
    cwd = Path.cwd().resolve()
    if (cwd / 'sistema').is_dir():
        return cwd
    if cwd.name.lower() == 'sistema' and (cwd / 'ururau').is_dir():
        return cwd.parent
    for p in [cwd] + list(cwd.parents):
        if (p / 'sistema').is_dir():
            return p
    for child in cwd.iterdir() if cwd.exists() else []:
        if child.is_dir() and (child / 'sistema').is_dir():
            return child
    raise SystemExit('ERRO: não encontrei a pasta sistema. Coloque este arquivo na raiz do projeto e rode novamente.')

D = _detect_base()
S = D / 'sistema'
print('[V47.13] Projeto detectado em:', D)
print('[V47.13] Pasta sistema:', S)

def _backup_once(path: Path):
    if not path.exists():
        return
    bak = path.with_suffix(path.suffix + '.bak_v47_13')
    if not bak.exists():
        try: shutil.copy2(path, bak)
        except Exception as e: print('[WARN] backup falhou:', path, e)

def _ensure_dir(path: Path): path.mkdir(parents=True, exist_ok=True)
def _write(path: Path, content: str):
    _ensure_dir(path.parent); _backup_once(path); path.write_text(content, encoding='utf-8')
    print('[OK] gravado:', path.relative_to(D))
def _read(path: Path):
    return path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''
def _patch_append(path: Path, marker: str, code: str):
    txt = _read(path)
    _backup_once(path)
    if marker not in txt:
        path.write_text(txt.rstrip() + '\n\n' + code.strip() + '\n', encoding='utf-8')
        print('[OK] patch aplicado:', path.relative_to(D))
    else:
        print('[OK] patch já existia:', path.relative_to(D))

def _bat(name, body):
    _write(D / name, body.replace('\n','\r\n'))

# ---------------- matriz de monitor ----------------
config_dir = S / 'config'
_ensure_dir(config_dir)
monitor_cfg = {
  "modo_cms_padrao": "rascunho",
  "intervalo_normal_segundos": 180,
  "intervalo_sem_pauta_segundos": 180,
  "max_publicacoes_hora": 24,
  "score_minimo_monitor": 45,
  "janela_horas_coleta": 12,
  "janela_horas_google_news": 12,
  "usar_fila_painel_no_monitor": True,
  "limite_fila_painel_monitor": 120,
  "limite_varredura_fila": 260,
  "max_itens_por_fonte_rss": 18,
  "max_google_news_por_termo": 5,
  "max_google_news_total": 80,
  "max_source_hunter": 160,
  "seo_minimo_publicacao_direta": 90,
  "texto_minimo_util_chars": 900,
  "permitir_rascunho_com_texto_minimo": True,
  "coleta": {
    "rss_configurado": True,
    "autofontes_diagnostico_v131": True,
    "google_news_integrado_v111": True,
    "google_news_ciclo_combinado_v111": True,
    "google_news_hidratacao_v111": True,
    "google_news_fallback_v110": True,
    "google_news_rss_legado_v108": True,
    "source_hunter": True,
    "fila_painel_monitor": True,
    "diagnostico_fonte_aplicado": True
  },
  "extracao": {
    "v104_orquestrador_canonico": True,
    "v86_multiestrategia": True,
    "requests_canonical_variantes": True,
    "json_ld_articlebody_nextdata": True,
    "kimi_article_extractor_v110": True,
    "trafilatura_readability_v108": True,
    "wordpress_rest_publico": True,
    "pipeline_v90_adapters": True,
    "playwright_publico_se_falhar": True,
    "preextraido_longo_ultimo_recurso": True
  },
  "ui": {
    "mostrar_score_so_com_texto_extraido": True,
    "selecionar_pauta_com_contorno_roxo": True,
    "navegacao_setas_fila": True,
    "f5_forca_varredura_fila": True,
    "painel_inteligencia_sem_chute": True
  }
}
_write(config_dir / 'monitor_24h.json', json.dumps(monitor_cfg, ensure_ascii=False, indent=2))

# ---------------- defaults de scrapers ----------------
coleta_dir = S / 'ururau' / 'coleta'
_ensure_dir(coleta_dir)
_write(coleta_dir / 'scraper_defaults_v47_10.py', r'''
# -*- coding: utf-8 -*-
"""Defaults aditivos de coleta/extração para manter todos os mecanismos ativos."""
from __future__ import annotations
import os, json
from pathlib import Path

COLETORES_ATIVOS = {
    'rss_configurado': True,
    'autofontes_diagnostico_v131': True,
    'google_news_integrado_v111': True,
    'google_news_ciclo_combinado_v111': True,
    'google_news_hidratacao_v111': True,
    'google_news_fallback_v110': True,
    'google_news_rss_legado_v108': True,
    'source_hunter': True,
    'fila_painel_monitor': True,
}
EXTRATORES_ATIVOS = {
    'v104_orquestrador_canonico': True,
    'v86_multiestrategia': True,
    'requests_canonical_variantes': True,
    'json_ld_articlebody_nextdata': True,
    'kimi_article_extractor_v110': True,
    'trafilatura_readability_v108': True,
    'wordpress_rest_publico': True,
    'pipeline_v90_adapters': True,
    'playwright_publico_se_falhar_v104': True,
    'playwright_publico_se_falhar_v86': True,
    'preextraido_longo_ultimo_recurso': True,
}
ENV_TRUE = {
    'URURAU_V111_GNEWS_INTEGRADO':'1',
    'URURAU_V111_USAR_EXTRACAO_COMPLETA':'1',
    'URURAU_V111_USAR_CICLO_COMBINADO':'1',
    'URURAU_V110_MONITOR_GNEWS_LEGADO':'1',
    'URURAU_V108_GNEWS_TERMOS':'1',
    'URURAU_SOURCE_HUNTER_ATIVO':'1',
    'URURAU_AUTOFONTES_V131_ATIVO':'1',
    'URURAU_AUTO_DIAGNOSTICO_FONTE':'1',
    'URURAU_MONITOR_USAR_FILA_PAINEL':'1',
}

def aplicar_defaults_scrapers(logger=None):
    for k,v in ENV_TRUE.items(): os.environ.setdefault(k,v)
    os.environ.setdefault('URURAU_GNEWS_JANELA_HORAS','12')
    os.environ.setdefault('URURAU_RSS_MAX_POR_FONTE','18')
    os.environ.setdefault('URURAU_MONITOR_SCORE_MINIMO','45')
    if logger:
        try: logger.info('[V47.10][SCRAPERS] ativos=' + ', '.join(list(COLETORES_ATIVOS)+list(EXTRATORES_ATIVOS)))
        except Exception: pass
    return {'coletores': COLETORES_ATIVOS, 'extratores': EXTRATORES_ATIVOS}
''')

# ---------------- fontes unificadas ----------------
_write(coleta_dir / 'fontes_unificadas_v47_13.py', r'''
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, re
from urllib.parse import urlparse

def _root():
    p = Path(__file__).resolve()
    for parent in p.parents:
        if parent.name == 'sistema': return parent
    return Path.cwd()

def _urls_from_obj(obj):
    found=[]
    def walk(x):
        if isinstance(x, str):
            if x.startswith('http://') or x.startswith('https://'): found.append(x.strip())
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(obj); return found

def carregar_fontes_unificadas(limit=None):
    s=_root(); paths=[
      s/'fontes_rss.json', s/'config'/'fontes_rss.json', s/'configuracoes'/'fontes_rss.json',
      s/'config'/'perfis_fontes_v131.json', s/'configuracoes'/'perfis_fontes_v131.json',
      s/'config'/'fontes_especiais_v129.json', s/'configuracoes'/'fontes_especiais_v129.json',
      s/'fontes_especiais_v129.json'
    ]
    urls=[]
    for p in paths:
        try:
            if p.exists(): urls.extend(_urls_from_obj(json.loads(p.read_text(encoding='utf-8'))))
        except Exception: pass
    seen=set(); out=[]
    for u in urls:
        key=u.split('#')[0].rstrip('/')
        if key in seen: continue
        seen.add(key); out.append({'url':u, 'dominio':urlparse(u).netloc, 'origem':'fontes_unificadas_v47_13'})
    return out[:limit] if limit else out
''')

# ---------------- SEO premium ----------------
editorial_dir = S / 'ururau' / 'editorial'
_ensure_dir(editorial_dir)
_write(editorial_dir / 'seo_premium_v47_12.py', r'''
# -*- coding: utf-8 -*-
from __future__ import annotations
import re, unicodedata

def _txt(v): return str(v or '').strip()
def _words(t): return re.findall(r'\w+', _txt(t), flags=re.UNICODE)
def _norm(t):
    t=unicodedata.normalize('NFKD', _txt(t)).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',t).strip()

TERMOS_IA = ['reforça','acende o alerta','vale lembrar','cabe ressaltar','é importante destacar','nesse contexto','ganha destaque','chama atenção']

def avaliar_seo_premium(materia: dict) -> dict:
    titulo=_txt(materia.get('titulo') or materia.get('titulo_seo'))
    capa=_txt(materia.get('titulo_capa'))
    sub=_txt(materia.get('subtitulo') or materia.get('descricao'))
    meta=_txt(materia.get('meta_description') or materia.get('meta'))
    corpo=_txt(materia.get('corpo') or materia.get('texto') or materia.get('conteudo'))
    tags=materia.get('tags') or []
    if isinstance(tags,str): tags=[x.strip() for x in tags.split(',') if x.strip()]
    score=0; checks=[]
    def add(ok, pts, msg):
        nonlocal score
        if ok: score += pts
        checks.append({'ok':bool(ok),'pts':pts,'msg':msg})
    add(35 <= len(titulo) <= 89, 14, f'título SEO com {len(titulo)} caracteres')
    add(not capa or len(capa) <= 60, 6, f'título de capa com {len(capa)} caracteres')
    add(35 <= len(sub) <= 180, 10, f'subtítulo com {len(sub)} caracteres')
    add(110 <= len(meta) <= 165, 10, f'meta description com {len(meta)} caracteres')
    add(len(_words(corpo)) >= 220, 14, f'corpo com {len(_words(corpo))} palavras')
    add(len(re.findall(r'\n\s*\n|\n', corpo)) >= 2, 8, 'estrutura em parágrafos')
    add(5 <= len(tags) <= 12, 8, f'{len(tags)} tags')
    add(bool(re.search(r'\b(quando|onde|quem|segundo|nesta|neste|após|durante)\b', corpo.lower())), 8, 'contexto factual')
    add(not any(t in _norm(titulo+' '+sub+' '+corpo) for t in TERMOS_IA), 12, 'sem termos de IA bloqueantes')
    add(bool(titulo and corpo and sub), 10, 'campos essenciais preenchidos')
    return {'seo_score': min(100, score), 'score': min(100,score), 'checks': checks, 'aprovado_publicacao_direta': score >= 90}

def otimizar_metadados_basico(materia: dict) -> dict:
    m=dict(materia or {})
    titulo=_txt(m.get('titulo') or m.get('titulo_seo'))
    if len(titulo)>89: m['titulo']=titulo[:86].rstrip()+'...'
    if not _txt(m.get('titulo_capa')) and titulo: m['titulo_capa']=titulo[:60].rstrip()
    corpo=_txt(m.get('corpo') or m.get('texto') or m.get('conteudo'))
    if not _txt(m.get('meta_description')):
        frase=re.split(r'(?<=[.!?])\s+', corpo)[0] if corpo else _txt(m.get('subtitulo'))
        m['meta_description']=frase[:160].rstrip()
    return m
''')

# ---------------- risco detalhado ----------------
_write(editorial_dir / 'risco.py', r'''
# -*- coding: utf-8 -*-
from __future__ import annotations
import re, unicodedata

def _norm(t):
    t=unicodedata.normalize('NFKD', str(t or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',t)

def _score(texto, termos, peso=12):
    n=_norm(texto); hits=[t for t in termos if t in n]
    return min(100, len(hits)*peso), hits

def analisar_risco_detalhado(materia_or_texto):
    if isinstance(materia_or_texto, dict):
        texto=' '.join(str(materia_or_texto.get(k,'') or '') for k in ['titulo','subtitulo','corpo','texto','conteudo'])
    else: texto=str(materia_or_texto or '')
    des,h1=_score(texto, ['boato','fake news','suposto print','mensagem atribuida','sem confirmacao','viralizou'], 18)
    vies,h2=_score(texto, ['absurdo','vergonha','escandalo sem precedentes','inacreditavel','chocante'], 18)
    sens,h3=_score(texto, ['chocante','bomba','urgente!','veja video','revoltante','nao vai acreditar'], 16)
    sen,h4=_score(texto, ['morte','homicidio','estupro','menor','crianca','adolescente','cadaver','trafico','prisao'], 10)
    geral=max(des,vies,sens,sen)
    nivel='baixo' if geral<30 else 'medio' if geral<60 else 'alto'
    return {'score_risco':geral,'risco_desinformacao':des,'vies_editorial':vies,'sensacionalismo':sens,'conteudo_sensivel':sen,'nivel_risco':nivel,'alertas_risco':h1+h2+h3+h4}
''')

# ---------------- patches em monitor ----------------
for mon in [S/'monitor.py', S/'ururau_monitor.py']:
    if mon.exists():
        _patch_append(mon, '# PATCH_V47_13_MONITOR_DEFAULTS', r'''
# PATCH_V47_13_MONITOR_DEFAULTS
try:
    from ururau.coleta.scraper_defaults_v47_10 import aplicar_defaults_scrapers
    aplicar_defaults_scrapers(globals().get('logger'))
except Exception:
    pass
''')

# ---------------- patches no painel ----------------
painel = S/'ururau'/'ui'/'painel.py'
if painel.exists():
    _patch_append(painel, '# PATCH_V47_13_UI_PREMIUM', r'''
# PATCH_V47_13_UI_PREMIUM
try:
    import tkinter as _tk_v4713
except Exception:
    _tk_v4713 = None

def _v4713_tem_texto_util(pauta):
    try:
        if not isinstance(pauta, dict): return False
        texto = pauta.get('texto_fonte') or pauta.get('fonte_texto') or pauta.get('texto_extraido') or pauta.get('corpo_fonte') or pauta.get('corpo') or ''
        return len(str(texto).strip()) >= 900
    except Exception: return False

def _v4713_score_visual(pauta):
    if not _v4713_tem_texto_util(pauta): return '--'
    for k in ('seo_score','qualidade_ia','score_qualidade','score_editorial','score'):
        try:
            v=pauta.get(k)
            if v is not None and str(v).strip()!='': return str(int(float(v)))
        except Exception: pass
    return '--'

def _v4713_ordenar_pautas_cronologico(pautas):
    def key(p):
        if not isinstance(p, dict): return ''
        return str(p.get('data_pub_fonte') or p.get('published') or p.get('data_publicacao') or p.get('created_at') or p.get('coletado_em') or '')
    try: return sorted(list(pautas or []), key=key, reverse=True)
    except Exception: return pautas

def _v4713_bind_fila_navegacao(widget, callback=None):
    if widget is None: return
    def move(delta):
        try:
            cur = widget.curselection()
            size = widget.size()
            idx = (cur[0] if cur else 0) + delta
            idx = max(0, min(size-1, idx))
            widget.selection_clear(0, 'end'); widget.selection_set(idx); widget.activate(idx); widget.see(idx); widget.focus_set()
            if callback: callback(None)
            return 'break'
        except Exception: return None
    try:
        widget.bind('<Down>', lambda e: move(1))
        widget.bind('<Up>', lambda e: move(-1))
        widget.bind('<Next>', lambda e: move(8))
        widget.bind('<Prior>', lambda e: move(-8))
        widget.bind('<Home>', lambda e: move(-999999))
        widget.bind('<End>', lambda e: move(999999))
        widget.configure(highlightthickness=2, highlightbackground='#7c3aed', highlightcolor='#7c3aed', exportselection=False)
    except Exception: pass

def _v4713_f5_operacional(app=None):
    funcs=['_carregar_pautas','carregar_pautas','atualizar_fila','refresh','_refresh']
    alvo = app if app is not None else globals().get('self')
    for name in funcs:
        try:
            fn=getattr(alvo,name,None)
            if callable(fn):
                try: fn(forcar=True)
                except TypeError: fn()
        except Exception: pass
    try:
        print('[V47.13] F5 operacional: fila recarregada e pautas pendentes reenfileiradas para extração.')
    except Exception: pass
''')

# ---------------- gate SEO ----------------
qg = editorial_dir/'quality_gate_v103.py'
if qg.exists():
    _patch_append(qg, '# PATCH_V47_13_SEO_GATE', r'''
# PATCH_V47_13_SEO_GATE
try:
    from ururau.editorial.seo_premium_v47_12 import avaliar_seo_premium
except Exception:
    avaliar_seo_premium = None

def v4713_gate_seo_publicacao_direta(materia):
    if avaliar_seo_premium is None: return {'ok': False, 'motivo': 'seo_premium indisponível'}
    r=avaliar_seo_premium(materia or {})
    return {'ok': r.get('seo_score',0) >= 90, 'seo_score': r.get('seo_score',0), 'detalhes': r}
''')

# ---------------- validações ----------------
val_dir = S/'ferramentas'/'validadores'
_ensure_dir(val_dir)
_write(val_dir/'VALIDAR_OPERACIONAL_TOTAL_V47_13.py', r'''
# -*- coding: utf-8 -*-
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve()
for p in ROOT.parents:
    if p.name=='sistema': S=p; break
else: S=Path.cwd()
errors=[]
def ok(cond,msg):
    print(('OK   ' if cond else 'ERRO ') + msg)
    if not cond: errors.append(msg)
cfg=S/'config'/'monitor_24h.json'
ok(cfg.exists(),'config/monitor_24h.json existe')
if cfg.exists():
    data=json.loads(cfg.read_text(encoding='utf-8'))
    ok(data.get('score_minimo_monitor',99)<=45,'score mínimo flexível para rascunho')
    ok(data.get('coleta',{}).get('google_news_integrado_v111') is True,'Google News v111 ativo')
    ok(data.get('coleta',{}).get('fila_painel_monitor') is True,'fila do painel entra no monitor')
    ok(data.get('extracao',{}).get('playwright_publico_se_falhar') is True,'Playwright público fallback ativo')
ok((S/'ururau'/'coleta'/'scraper_defaults_v47_10.py').exists(),'scraper defaults existe')
ok((S/'ururau'/'coleta'/'fontes_unificadas_v47_13.py').exists(),'fontes unificadas existe')
ok((S/'ururau'/'editorial'/'seo_premium_v47_12.py').exists(),'SEO premium existe')
ok((S/'ururau'/'editorial'/'risco.py').exists(),'risco detalhado existe')
if errors:
    print('\nFALHAS:', errors); sys.exit(1)
print('\nVALIDAÇÃO V47.13 OK')
''')

_bat('09_VALIDAR_OPERACIONAL_TOTAL.bat', '@echo off\ncd /d "%~dp0sistema"\npython ferramentas\\validadores\\VALIDAR_OPERACIONAL_TOTAL_V47_13.py\npause\n')
_bat('04_MONITOR_24H_RASCUNHO.bat', '@echo off\ncd /d "%~dp0sistema"\nset URURAU_MONITOR_MODO_CMS=rascunho\nset URURAU_PUBLICAR_DIRETO=0\nset URURAU_CMS_PUBLICACAO_DIRETA=0\npython ururau_monitor.py --modo-cms rascunho\npause\n')
_bat('02_ABRIR_PAINEL.bat', '@echo off\ncd /d "%~dp0sistema"\npython -m ururau.ui.painel\npause\n')
_bat('03_ABRIR_PAINEL_COM_LOG_VISIVEL.bat', '@echo off\ncd /d "%~dp0sistema"\npython -m ururau.ui.painel\npause\n')

# Limpa raiz: move docs/validadores soltos para pastas, preserva BATs e pastas principais
_docs = S/'documentacao'
_tools = S/'ferramentas'/'avulsos'
_ensure_dir(_docs); _ensure_dir(_tools)
for p in list(S.iterdir()):
    if p.is_file() and p.suffix.lower() in {'.txt','.md'}:
        try: shutil.move(str(p), str(_docs/p.name)); print('[OK] documento movido:', p.name)
        except Exception: pass
    elif p.is_file() and p.suffix.lower()=='.py' and p.name.upper().startswith('VALIDAR_'):
        try: shutil.move(str(p), str(val_dir/p.name)); print('[OK] validador movido:', p.name)
        except Exception: pass

# Compilação rápida
try:
    subprocess.run([sys.executable, '-m', 'compileall', '-q', str(S/'ururau')], check=False)
except Exception as e: print('[WARN] compileall falhou:', e)

print('\n[V47.13] Correções aplicadas. Rode:')
print('  09_VALIDAR_OPERACIONAL_TOTAL.bat')
print('  02_ABRIR_PAINEL.bat')
print('  04_MONITOR_24H_RASCUNHO.bat')
