import time
import os
import sys
from zapv2 import ZAPv2

print("="*60)
print("OWASP ZAP SCAN - PyGoat")
print("="*60)

api_key = os.environ.get('ZAP_API_KEY', '')
target = 'http://localhost:8000'

print(f"[1] Target: {target}")
print(f"[2] API Key: {'✅ OK' if api_key else '❌ NO'}")

# Conectar a ZAP
print(f"[3] Conectando a ZAP en http://localhost:8080...")
zap = ZAPv2(apikey=api_key, proxies={'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})

# Intentar conectar con reintentos
conectado = False
for i in range(20):
    try:
        version = zap.core.version
        print(f"    ✅ ZAP conectado. Versión: {version}")
        conectado = True
        break
    except Exception as e:
        print(f"    ⏳ Intento {i+1}/20: ZAP no responde, esperando 3s...")
        time.sleep(3)

if not conectado:
    print("    ❌ No se pudo conectar a ZAP")
    sys.exit(1)

# Nueva sesión
print("[4] Creando nueva sesión...")
zap.core.new_session(name='pygoat-scan', overwrite=True)

# Spider
print("[5] Iniciando spider...")
zap.spider.scan(target)
time.sleep(5)
for i in range(12):
    status = zap.spider.status()
    print(f"    Spider: {status}%")
    if status == '100':
        break
    time.sleep(5)

# Escaneo activo
print("[6] Iniciando escaneo activo...")
zap.ascan.scan(target)
time.sleep(5)
for i in range(15):
    status = zap.ascan.status()
    print(f"    Escaneo: {status}%")
    if status == '100':
        break
    time.sleep(5)

# Obtener alertas
print("[7] Obteniendo alertas...")
alerts = zap.core.alerts()
high_alerts = [a for a in alerts if a.get('risk') == 'High']
medium_alerts = [a for a in alerts if a.get('risk') == 'Medium']
low_alerts = [a for a in alerts if a.get('risk') == 'Low']

print(f"\n📊 RESULTADOS:")
print(f"  🔴 HIGH: {len(high_alerts)}")
print(f"  🟡 MEDIUM: {len(medium_alerts)}")
print(f"  🟢 LOW: {len(low_alerts)}")
print(f"  📋 TOTAL: {len(alerts)}")

# ============================================
# GENERAR REPORTE HTML COMPLETO - MISMA INFO, MEJOR UI
# ============================================
print("[8] Generando reporte HTML detallado...")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OWASP ZAP DAST Report - PyGoat</title>
  <style>
    :root {{
      --bg: #0b1220;
      --panel: rgba(255,255,255,0.06);
      --panel-2: rgba(255,255,255,0.10);
      --text: rgba(255,255,255,0.92);
      --muted: rgba(255,255,255,0.65);
      --border: rgba(255,255,255,0.12);

      --high: #ff4d4f;
      --medium: #faad14;
      --low: #52c41a;
      --info: #40a9ff;

      --shadow: 0 14px 40px rgba(0,0,0,0.35);
      --radius: 18px;
      --radius-sm: 12px;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      color: var(--text);
      background:
        radial-gradient(1200px 600px at 10% 0%, rgba(64,169,255,0.18), transparent 55%),
        radial-gradient(900px 500px at 90% 10%, rgba(255,77,79,0.12), transparent 55%),
        radial-gradient(900px 500px at 70% 90%, rgba(82,196,26,0.10), transparent 55%),
        var(--bg);
    }}

    a {{ color: var(--info); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    .topbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(10px);
      background: rgba(11,18,32,0.55);
      border-bottom: 1px solid var(--border);
    }}

    .topbar-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 14px 18px;
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }}

    .brand {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 260px;
    }}

    .brand h1 {{
      font-size: 16px;
      margin: 0;
      font-weight: 800;
      letter-spacing: 0.2px;
    }}
    .brand .meta {{
      font-size: 12px;
      color: var(--muted);
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .controls {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}

    .search {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      background: var(--panel);
      border: 1px solid var(--border);
      min-width: 260px;
    }}
    .search input {{
      width: 100%;
      background: transparent;
      border: 0;
      outline: 0;
      color: var(--text);
      font-size: 13px;
    }}
    .search input::placeholder {{ color: rgba(255,255,255,0.45); }}

    .chip {{
      user-select: none;
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--panel);
      padding: 8px 10px;
      border-radius: 999px;
      font-size: 12px;
      color: var(--text);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: transform .08s ease, background .2s ease;
    }}
    .chip:active {{ transform: scale(0.98); }}
    .chip[data-active="true"] {{
      background: var(--panel-2);
      border-color: rgba(255,255,255,0.22);
    }}
    .dot {{
      width: 8px; height: 8px; border-radius: 999px;
      display: inline-block;
    }}
    .dot.high {{ background: var(--high); }}
    .dot.medium {{ background: var(--medium); }}
    .dot.low {{ background: var(--low); }}

    .container {{
      max-width: 1200px;
      margin: 18px auto 60px auto;
      padding: 0 18px;
    }}

    .hero {{
      margin-top: 18px;
      padding: 20px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.04));
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .hero-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .hero-title h2 {{
      margin: 0;
      font-size: 22px;
      letter-spacing: 0.2px;
    }}
    .sub {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }}

    .stats {{
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    @media (max-width: 980px) {{
      .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .brand {{ min-width: 0; }}
    }}
    @media (max-width: 520px) {{
      .stats {{ grid-template-columns: 1fr; }}
      .search {{ min-width: 200px; flex: 1; }}
    }}

    .stat {{
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: var(--radius);
      padding: 14px 14px;
    }}
    .stat .label {{
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .stat .value {{
      font-size: 34px;
      font-weight: 900;
      line-height: 1;
      letter-spacing: -0.6px;
    }}
    .stat.high .value {{ color: var(--high); }}
    .stat.medium .value {{ color: var(--medium); }}
    .stat.low .value {{ color: var(--low); }}

    .section {{
      margin-top: 18px;
      padding: 18px;
      border-radius: var(--radius);
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.04);
    }}
    .section h3 {{
      margin: 0 0 12px 0;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .badge {{
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--panel);
      color: var(--text);
    }}

    .alert {{
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: var(--radius);
      overflow: hidden;
      margin: 12px 0;
    }}
    .alert-header {{
      padding: 14px 14px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: center;
      cursor: pointer;
    }}
    .alert-title {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }}
    .sev {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 800;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.05);
      white-space: nowrap;
    }}
    .sev.high {{ color: var(--high); border-color: rgba(255,77,79,0.35); }}
    .sev.medium {{ color: var(--medium); border-color: rgba(250,173,20,0.35); }}
    .sev.low {{ color: var(--low); border-color: rgba(82,196,26,0.35); }}

    .alert-title h4 {{
      margin: 0;
      font-size: 13.5px;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .url {{
      margin: 4px 0 0 0;
      font-size: 12px;
      color: var(--muted);
      word-break: break-all;
    }}

    .actions {{
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .btn {{
      cursor: pointer;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.06);
      color: var(--text);
      padding: 8px 10px;
      border-radius: 10px;
      font-size: 12px;
      user-select: none;
    }}
    .btn:hover {{ background: rgba(255,255,255,0.10); }}

    .alert-body {{
      display: none;
      padding: 0 14px 14px 14px;
      border-top: 1px solid var(--border);
    }}
    .alert[data-open="true"] .alert-body {{ display: block; }}

    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 12px;
    }}
    @media (max-width: 820px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}

    .kv {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.04);
      border-radius: var(--radius-sm);
      padding: 12px;
    }}
    .kv .k {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .kv .v {{
      font-size: 13px;
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    .footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }}

    .hidden {{ display: none !important; }}
  </style>
</head>
<body>

  <div class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <h1>🔍 OWASP ZAP DAST Report</h1>
        <p class="meta">
          Target: <strong>{target}</strong> · Fecha: <strong>{time.strftime('%Y-%m-%d %H:%M:%S')}</strong> · ZAP: <strong>{zap.core.version}</strong>
        </p>
      </div>

      <div class="controls">
        <div class="search" title="Busca por nombre, URL, descripción, solución...">
          🔎
          <input id="q" type="text" placeholder="Buscar alertas..." />
        </div>

        <div class="chip" id="fHigh" data-active="true" title="Mostrar/Ocultar HIGH">
          <span class="dot high"></span> HIGH
        </div>
        <div class="chip" id="fMed" data-active="true" title="Mostrar/Ocultar MEDIUM">
          <span class="dot medium"></span> MEDIUM
        </div>
        <div class="chip" id="fLow" data-active="true" title="Mostrar/Ocultar LOW">
          <span class="dot low"></span> LOW
        </div>

        <div class="chip" id="expandAll" data-active="false" title="Expandir/Colapsar todo">
          ⤢ Expandir
        </div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="hero">
      <div class="hero-title">
        <h2>Resumen del escaneo</h2>
        <span class="badge">Pipeline: <strong>{"FALLIDO" if len(high_alerts) > 0 else "EXITOSO"}</strong></span>
      </div>
      <div class="sub">
        Este reporte contiene todas las alertas devueltas por ZAP (sin límite), agrupadas por severidad.
        Usa el buscador y los filtros para revisar más rápido.
      </div>

      <div class="stats">
        <div class="stat high">
          <div class="label"><span class="dot high"></span> Alertas HIGH</div>
          <div class="value">{len(high_alerts)}</div>
        </div>
        <div class="stat medium">
          <div class="label"><span class="dot medium"></span> Alertas MEDIUM</div>
          <div class="value">{len(medium_alerts)}</div>
        </div>
        <div class="stat low">
          <div class="label"><span class="dot low"></span> Alertas LOW</div>
          <div class="value">{len(low_alerts)}</div>
        </div>
        <div class="stat">
          <div class="label"><span class="dot" style="background: var(--info)"></span> Total</div>
          <div class="value">{len(alerts)}</div>
        </div>
      </div>
    </div>

    <div class="section" id="sec-high">
      <h3>
        🔴 Alertas HIGH
        <span class="badge">{len(high_alerts)} encontradas</span>
      </h3>
"""

# ============================================
# ALERTAS HIGH - TODAS, SIN LÍMITE (MISMA DATA)
# ============================================
if high_alerts:
    for alert in high_alerts:
        html_content += f"""
      <div class="alert" data-sev="High" data-open="false">
        <div class="alert-header" onclick="toggleAlert(this)">
          <div class="alert-title">
            <span class="sev high">🔴 HIGH</span>
            <div style="min-width:0;">
              <h4 title="{alert.get('alert', 'N/A')}">{alert.get('alert', 'N/A')}</h4>
              <p class="url"><strong>URL:</strong> <a href="{alert.get('url', 'N/A')}" target="_blank" rel="noopener noreferrer">{alert.get('url', 'N/A')}</a></p>
            </div>
          </div>
          <div class="actions" onclick="event.stopPropagation()">
            <button class="btn" onclick="copyText('{str(alert.get('url', 'N/A')).replace("'", "\\'")}')">Copiar URL</button>
            <button class="btn" onclick="copyText('{str(alert.get('alert', 'N/A')).replace("'", "\\'")}')">Copiar título</button>
            <button class="btn" onclick="openAllForSev('High')">Ver HIGH</button>
          </div>
        </div>
        <div class="alert-body">
          <div class="grid">
            <div class="kv">
              <div class="k">Confianza</div>
              <div class="v">{alert.get('confidence', 'N/A')}</div>
            </div>
            <div class="kv">
              <div class="k">Riesgo</div>
              <div class="v"><span style="color: var(--high); font-weight:800;">{alert.get('risk', 'N/A')}</span></div>
            </div>
            <div class="kv">
              <div class="k">Descripción</div>
              <div class="v">{alert.get('description', 'N/A')}</div>
            </div>
            <div class="kv">
              <div class="k">Solución</div>
              <div class="v">{alert.get('solution', 'No disponible')}</div>
            </div>
            <div class="kv" style="grid-column: 1 / -1;">
              <div class="k">Referencia</div>
              <div class="v">{alert.get('reference', 'N/A')}</div>
            </div>
          </div>
        </div>
      </div>
"""
else:
    html_content += "<p>No se encontraron vulnerabilidades de alto riesgo.</p>"

html_content += f"""
    </div>

    <div class="section" id="sec-medium">
      <h3>
        🟡 Alertas MEDIUM
        <span class="badge">{len(medium_alerts)} encontradas</span>
      </h3>
"""

# ============================================
# ALERTAS MEDIUM - TODAS, SIN LÍMITE
# ============================================
if medium_alerts:
    for alert in medium_alerts:
        html_content += f"""
      <div class="alert" data-sev="Medium" data-open="false">
        <div class="alert-header" onclick="toggleAlert(this)">
          <div class="alert-title">
            <span class="sev medium">🟡 MEDIUM</span>
            <div style="min-width:0;">
              <h4 title="{alert.get('alert', 'N/A')}">{alert.get('alert', 'N/A')}</h4>
              <p class="url"><strong>URL:</strong> <a href="{alert.get('url', 'N/A')}" target="_blank" rel="noopener noreferrer">{alert.get('url', 'N/A')}</a></p>
            </div>
          </div>
          <div class="actions" onclick="event.stopPropagation()">
            <button class="btn" onclick="copyText('{str(alert.get('url', 'N/A')).replace("'", "\\'")}')">Copiar URL</button>
            <button class="btn" onclick="copyText('{str(alert.get('alert', 'N/A')).replace("'", "\\'")}')">Copiar título</button>
            <button class="btn" onclick="openAllForSev('Medium')">Ver MEDIUM</button>
          </div>
        </div>
        <div class="alert-body">
          <div class="grid">
            <div class="kv">
              <div class="k">Confianza</div>
              <div class="v">{alert.get('confidence', 'N/A')}</div>
            </div>
            <div class="kv">
              <div class="k">Riesgo</div>
              <div class="v"><span style="color: var(--medium); font-weight:800;">{alert.get('risk', 'N/A')}</span></div>
            </div>
            <div class="kv">
              <div class="k">Descripción</div>
              <div class="v">{alert.get('description', 'N/A')}</div>
            </div>
            <div class="kv">
              <div class="k">Solución</div>
              <div class="v">{alert.get('solution', 'No disponible')}</div>
            </div>
          </div>
        </div>
      </div>
"""
else:
    html_content += "<p>No se encontraron vulnerabilidades de riesgo medio.</p>"

html_content += f"""
    </div>

    <div class="section" id="sec-low">
      <h3>
        🟢 Alertas LOW
        <span class="badge">{len(low_alerts)} encontradas</span>
      </h3>
"""

# ============================================
# ALERTAS LOW - TODAS, SIN LÍMITE
# ============================================
if low_alerts:
    for alert in low_alerts:
        html_content += f"""
      <div class="alert" data-sev="Low" data-open="false">
        <div class="alert-header" onclick="toggleAlert(this)">
          <div class="alert-title">
            <span class="sev low">🟢 LOW</span>
            <div style="min-width:0;">
              <h4 title="{alert.get('alert', 'N/A')}">{alert.get('alert', 'N/A')}</h4>
              <p class="url"><strong>URL:</strong> <a href="{alert.get('url', 'N/A')}" target="_blank" rel="noopener noreferrer">{alert.get('url', 'N/A')}</a></p>
            </div>
          </div>
          <div class="actions" onclick="event.stopPropagation()">
            <button class="btn" onclick="copyText('{str(alert.get('url', 'N/A')).replace("'", "\\'")}')">Copiar URL</button>
            <button class="btn" onclick="copyText('{str(alert.get('alert', 'N/A')).replace("'", "\\'")}')">Copiar título</button>
            <button class="btn" onclick="openAllForSev('Low')">Ver LOW</button>
          </div>
        </div>
        <div class="alert-body">
          <div class="grid">
            <div class="kv">
              <div class="k">Confianza</div>
              <div class="v">{alert.get('confidence', 'N/A')}</div>
            </div>
            <div class="kv">
              <div class="k">Riesgo</div>
              <div class="v"><span style="color: var(--low); font-weight:800;">{alert.get('risk', 'N/A')}</span></div>
            </div>
            <div class="kv">
              <div class="k">Descripción</div>
              <div class="v">{alert.get('description', 'N/A')}</div>
            </div>
          </div>
        </div>
      </div>
"""
else:
    html_content += "<p>No se encontraron vulnerabilidades de riesgo bajo.</p>"

html_content += f"""
    </div>

    <div class="section" id="sec-summary">
      <h3>📊 Resumen General <span class="badge">Total {len(alerts)}</span></h3>
      <div class="grid">
        <div class="kv">
          <div class="k">Estado</div>
          <div class="v">Spider: Completado · Escaneo activo: Completado</div>
        </div>
        <div class="kv">
          <div class="k">Distribución</div>
          <div class="v">🔴 HIGH: {len(high_alerts)} · 🟡 MEDIUM: {len(medium_alerts)} · 🟢 LOW: {len(low_alerts)}</div>
        </div>
        <div class="kv" style="grid-column: 1 / -1;">
          <div class="k">ZAP</div>
          <div class="v">Versión: {zap.core.version}</div>
        </div>
      </div>

      <div class="footer">
        Reporte generado automáticamente por GitHub Actions<br>
        Commit: {os.popen('git rev-parse --short HEAD').read().strip() if os.path.exists('.git') else 'N/A'}
      </div>
    </div>
  </div>

  <script>
    const q = document.getElementById('q');
    const fHigh = document.getElementById('fHigh');
    const fMed = document.getElementById('fMed');
    const fLow = document.getElementById('fLow');
    const expandAll = document.getElementById('expandAll');

    function normalize(s) {{
      return (s || '').toString().toLowerCase();
    }}

    function toggleChip(el) {{
      const active = el.getAttribute('data-active') === 'true';
      el.setAttribute('data-active', active ? 'false' : 'true');
      applyFilters();
    }}

    function applyFilters() {{
      const query = normalize(q.value).trim();
      const showHigh = fHigh.getAttribute('data-active') === 'true';
      const showMed = fMed.getAttribute('data-active') === 'true';
      const showLow = fLow.getAttribute('data-active') === 'true';

      const alerts = document.querySelectorAll('.alert');
      alerts.forEach(card => {{
        const sev = card.getAttribute('data-sev');
        const text = normalize(card.innerText);

        let sevOk = true;
        if (sev === 'High') sevOk = showHigh;
        if (sev === 'Medium') sevOk = showMed;
        if (sev === 'Low') sevOk = showLow;

        const qOk = query === '' || text.includes(query);

        card.classList.toggle('hidden', !(sevOk && qOk));
      }});

      // Ocultar secciones si no queda nada visible
      ['sec-high','sec-medium','sec-low'].forEach(id => {{
        const sec = document.getElementById(id);
        const visible = sec.querySelectorAll('.alert:not(.hidden)').length > 0;
        sec.style.display = visible ? 'block' : 'none';
      }});
    }}

    function toggleAlert(headerEl) {{
      const card = headerEl.closest('.alert');
      const open = card.getAttribute('data-open') === 'true';
      card.setAttribute('data-open', open ? 'false' : 'true');
    }}

    function setAll(open) {{
      document.querySelectorAll('.alert:not(.hidden)').forEach(card => {{
        card.setAttribute('data-open', open ? 'true' : 'false');
      }});
    }}

    function openAllForSev(sev) {{
      document.querySelectorAll('.alert[data-sev="' + sev + '"]:not(.hidden)').forEach(card => {{
        card.setAttribute('data-open', 'true');
      }});
    }}

    function copyText(text) {{
      try {{
        navigator.clipboard.writeText(text);
      }} catch (e) {{
        // fallback silencioso
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }}
    }}

    q.addEventListener('input', applyFilters);
    fHigh.addEventListener('click', () => toggleChip(fHigh));
    fMed.addEventListener('click', () => toggleChip(fMed));
    fLow.addEventListener('click', () => toggleChip(fLow));

    expandAll.addEventListener('click', () => {{
      const active = expandAll.getAttribute('data-active') === 'true';
      expandAll.setAttribute('data-active', active ? 'false' : 'true');
      expandAll.innerText = active ? '⤢ Expandir' : '⤡ Colapsar';
      setAll(!active);
    }});

    // Inicial
    applyFilters();
  </script>
</body>
</html>
"""

# Guardar reporte
with open('zap-report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Verificar
if os.path.exists('zap-report.html'):
    size = os.path.getsize('zap-report.html')
    print(f"    ✅ Reporte HTML generado: {size} bytes")
else:
    print("    ❌ No se pudo generar el reporte")
    sys.exit(1)

# Resultado final
print("\n" + "="*60)
if len(high_alerts) > 0:
    print(f"❌ PIPELINE FALLIDO: {len(high_alerts)} vulnerabilidades HIGH encontradas")
    print(f"    Revisa el reporte HTML para más detalles")
    sys.exit(1)
else:
    print("✅ PIPELINE EXITOSO: No hay vulnerabilidades HIGH")
    sys.exit(0)
