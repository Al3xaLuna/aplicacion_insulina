"""
ARQ-Metabólica MX — App Móvil Flet
IARRI = 0.20(1-AV) + 0.25(1-IC) + 0.15(1-ED) + 0.25(EAR) + 0.15(IM)

pip install flet numpy
python main.py
flet build apk
"""

import flet as ft
import numpy as np
import threading

BG      = "#0a0e1a"
SURFACE = "#111827"
CARD    = "#161f35"
BORDER  = "#1e2d4a"
ACCENT  = "#00e5c8"
ACCENT2 = "#ff6b35"
ACCENT3 = "#7c3aed"
LOW     = "#10b981"
MID     = "#f59e0b"
HIGH    = "#ef4444"
TEXT    = "#e8edf5"
MUTED   = "#6b7fa3"

W = {"AV": 0.20, "IC": 0.25, "ED": 0.15, "EAR": 0.25, "IM": 0.15}

MUNICIPIOS = [
    {"nombre": "San Andres Cholula",      "AV": 0.80, "IC": 0.60, "ED": 0.40, "EAR": 0.45, "IM": 0.10},
    {"nombre": "San Pablo Xochimehuacan", "AV": 0.50, "IC": 0.35, "ED": 0.20, "EAR": 0.60, "IM": 0.55},
    {"nombre": "Cuautlancingo",           "AV": 0.30, "IC": 0.20, "ED": 0.10, "EAR": 0.80, "IM": 0.70},
]

def calc(AV, IC, ED, EAR, IM):
    return W["AV"]*(1-AV) + W["IC"]*(1-IC) + W["ED"]*(1-ED) + W["EAR"]*EAR + W["IM"]*IM

def nivel(v):
    if v <= 0.33: return "Bajo",  LOW
    if v <= 0.66: return "Medio", MID
    return               "Alto",  HIGH

def prob_ri(v):
    return min(1.0, 0.10 + 0.50 * v)

def monte_carlo(base, n=1000, sigma=0.12):
    res = np.array([
        calc(**{k: max(0.0, min(1.0, base[k] + np.random.uniform(-sigma, sigma)))
                for k in ["AV","IC","ED","EAR","IM"]})
        for _ in range(n)
    ])
    return res, res.mean(), res.std(), np.percentile(res, 2.5), np.percentile(res, 97.5)

def card(content, padding=14):
    return ft.Container(content=content, bgcolor=CARD, border_radius=14,
                        padding=padding, border=ft.border.all(1, BORDER))

def sec(texto):
    return ft.Text(texto.upper(), size=10, color=MUTED, weight=ft.FontWeight.BOLD)

def barra(valor, color, alto=6):
    ancho = max(2, int(min(1.0, valor) * 260))
    return ft.Stack([
        ft.Container(height=alto, border_radius=3, bgcolor=BORDER, width=260),
        ft.Container(height=alto, border_radius=3, bgcolor=color, width=ancho),
    ])

def bdg(niv_txt, color):
    return ft.Container(
        content=ft.Row([
            ft.Container(width=7, height=7, border_radius=4, bgcolor=color),
            ft.Text(f"Riesgo {niv_txt}", size=12, weight=ft.FontWeight.BOLD, color=color),
        ], spacing=6, tight=True),
        bgcolor=color+"22", border=ft.border.all(1, color+"55"),
        border_radius=20, padding=ft.padding.symmetric(horizontal=12, vertical=5),
    )

# ── TAB 1: CALCULADORA ──────────────────────────────────────
def tab_calc(page):
    vals = {"AV": 0.50, "IC": 0.50, "ED": 0.50, "EAR": 0.50, "IM": 0.50}
    VARS = [
        ("AV",  "Áreas Verdes",                "🌳", LOW,    True),
        ("IC",  "Índice Caminabilidad",          "🚶", ACCENT, True),
        ("ED",  "Equipamiento Deportivo",        "⚽", ACCENT3,True),
        ("EAR", "Entorno Alimentario Riesgoso", "🍟", ACCENT2,False),
        ("IM",  "Índice de Marginación",         "📉", MID,    False),
    ]

    lbl_iarri = ft.Text("0.5000", size=52, weight=ft.FontWeight.W_900, color=ACCENT)
    lbl_nivel = ft.Text("Riesgo Medio", size=14, weight=ft.FontWeight.BOLD, color=MID)
    lbl_prob  = ft.Text("Prob. RI: 35.0%", size=12, color=MUTED)
    sem_low   = ft.Container(width=16, height=16, border_radius=8, bgcolor=LOW,  opacity=0.2)
    sem_mid   = ft.Container(width=16, height=16, border_radius=8, bgcolor=MID,  opacity=1.0)
    sem_high  = ft.Container(width=16, height=16, border_radius=8, bgcolor=HIGH, opacity=0.2)

    slbl = {}
    cbars = {}
    clbls = {}
    sliders = {}

    def actualizar():
        iarri = calc(**vals)
        niv, col = nivel(iarri)
        lbl_iarri.value = f"{iarri:.4f}"
        lbl_iarri.color = col
        lbl_nivel.value = f"● Riesgo {niv}"
        lbl_nivel.color = col
        lbl_prob.value  = f"Prob. RI: {prob_ri(iarri)*100:.1f}%"
        sem_low.opacity  = 1.0 if iarri <= 0.33 else 0.15
        sem_mid.opacity  = 1.0 if 0.33 < iarri <= 0.66 else 0.15
        sem_high.opacity = 1.0 if iarri > 0.66 else 0.15
        cs = {"AV": W["AV"]*(1-vals["AV"]), "IC": W["IC"]*(1-vals["IC"]),
              "ED": W["ED"]*(1-vals["ED"]), "EAR": W["EAR"]*vals["EAR"],
              "IM": W["IM"]*vals["IM"]}
        for k in cs:
            cbars[k].width = max(2, int(cs[k] * 1040))
            clbls[k].value = f"{cs[k]:.3f}"
        page.update()

    def on_slide(key):
        def h(e):
            vals[key] = round(e.control.value, 2)
            slbl[key].value = f"{vals[key]:.2f}"
            actualizar()
        return h

    def set_muni(idx):
        m = MUNICIPIOS[idx]
        for k in ["AV","IC","ED","EAR","IM"]:
            vals[k] = m[k]
            slbl[k].value = f"{m[k]:.2f}"
            sliders[k].value = m[k]
        actualizar()

    scards = []
    for key, label, icon, color, inv in VARS:
        lv = ft.Text(f"{vals[key]:.2f}", size=15, weight=ft.FontWeight.W_900,
                     color=color, width=44)
        slbl[key] = lv
        s = ft.Slider(min=0, max=1, value=vals[key], divisions=100,
                      active_color=color, inactive_color=BORDER,
                      thumb_color=color, on_change=on_slide(key), expand=True)
        sliders[key] = s
        bi = ft.Container(height=6, border_radius=3, bgcolor=color, width=130)
        bl = ft.Text("0.100", size=10, color=color, width=36,
                     text_align=ft.TextAlign.RIGHT, font_family="monospace")
        cbars[key] = bi
        clbls[key] = bl
        scards.append(card(ft.Column([
            ft.Row([
                ft.Text(f"{icon} {label}", size=12, weight=ft.FontWeight.W_600,
                        color=TEXT, expand=True),
                lv,
            ]),
            s,
            ft.Row([ft.Text("0.0",size=9,color=MUTED), ft.Container(expand=True),
                    ft.Text("0.5",size=9,color=MUTED), ft.Container(expand=True),
                    ft.Text("1.0",size=9,color=MUTED)]),
            ft.Text("protector ↓" if inv else "riesgo ↑", size=9, color=color, italic=True),
        ], spacing=2)))

    presets = ft.Row([
        ft.ElevatedButton(
            m["nombre"].split()[0],
            bgcolor=CARD, color=TEXT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=lambda e, i=i: set_muni(i),
        ) for i, m in enumerate(MUNICIPIOS)
    ], spacing=6)

    resultado = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([ft.Text("IARRI", size=11, color=MUTED), lbl_iarri]),
                ft.Column([lbl_nivel, lbl_prob],
                          horizontal_alignment=ft.CrossAxisAlignment.END),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(color=BORDER),
            ft.Text("Desglose contribuciones", size=11, color=MUTED),
            *[ft.Row([
                ft.Text(k, size=11, color=MUTED, width=36, font_family="monospace"),
                ft.Stack([
                    ft.Container(height=6, border_radius=3, bgcolor=BORDER, width=260),
                    cbars[k],
                ]),
                clbls[k],
            ], spacing=8) for k, *_ in VARS],
            ft.Divider(color=BORDER),
            ft.Row([sem_low, sem_mid, sem_high,
                    ft.Text("Semáforo", size=12, color=MUTED)], spacing=10),
        ], spacing=10),
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1,-1), end=ft.alignment.Alignment(1,1),
            colors=["#0f2441","#1a0a2e"],
        ),
        border=ft.border.all(1, BORDER), border_radius=16, padding=16,
    )

    actualizar()
    return ft.Column([
        sec("Preset municipio"), ft.Container(height=6), presets,
        ft.Container(height=8),
        card(ft.Text("IARRI = 0.20(1−AV) + 0.25(1−IC) + 0.15(1−ED) + 0.25(EAR) + 0.15(IM)",
                     size=10, color=ACCENT, font_family="monospace")),
        ft.Container(height=8),
        sec("Variables"), ft.Container(height=6),
        *scards,
        ft.Container(height=8), resultado, ft.Container(height=20),
    ], spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)


# ── TAB 2: MUNICIPIOS ───────────────────────────────────────
def tab_municipios(page):
    rows = []
    for m in MUNICIPIOS:
        iarri = calc(m["AV"],m["IC"],m["ED"],m["EAR"],m["IM"])
        niv, col = nivel(iarri)
        rows.append(card(ft.Column([
            ft.Row([
                ft.Text(m["nombre"], size=13, weight=ft.FontWeight.BOLD,
                        color=TEXT, expand=True),
                bdg(niv, col),
            ]),
            ft.Row([
                ft.Text("IARRI:", size=11, color=MUTED),
                ft.Text(f"{iarri:.4f}", size=20, weight=ft.FontWeight.W_900, color=col),
                ft.Container(expand=True),
                ft.Text("Prob.RI:", size=11, color=MUTED),
                ft.Text(f"{prob_ri(iarri)*100:.1f}%", size=15,
                        weight=ft.FontWeight.BOLD, color=col),
            ]),
            barra(iarri, col, 8),
            ft.Row([
                ft.Column([ft.Text("AV",  size=9, color=MUTED),
                           ft.Text(f"{m['AV']:.2f}",  size=12, color=LOW,    weight=ft.FontWeight.BOLD),
                           barra(m["AV"],  LOW,    4)], spacing=2),
                ft.Column([ft.Text("IC",  size=9, color=MUTED),
                           ft.Text(f"{m['IC']:.2f}",  size=12, color=ACCENT, weight=ft.FontWeight.BOLD),
                           barra(m["IC"],  ACCENT, 4)], spacing=2),
                ft.Column([ft.Text("ED",  size=9, color=MUTED),
                           ft.Text(f"{m['ED']:.2f}",  size=12, color=ACCENT3,weight=ft.FontWeight.BOLD),
                           barra(m["ED"],  ACCENT3,4)], spacing=2),
                ft.Column([ft.Text("EAR", size=9, color=MUTED),
                           ft.Text(f"{m['EAR']:.2f}", size=12, color=ACCENT2,weight=ft.FontWeight.BOLD),
                           barra(m["EAR"], ACCENT2,4)], spacing=2),
                ft.Column([ft.Text("IM",  size=9, color=MUTED),
                           ft.Text(f"{m['IM']:.2f}",  size=12, color=MID,    weight=ft.FontWeight.BOLD),
                           barra(m["IM"],  MID,    4)], spacing=2),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=8)))

    hdr = ft.Container(
        content=ft.Row([
            ft.Text("Municipio", size=10, color=MUTED, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("IARRI",     size=10, color=MUTED, weight=ft.FontWeight.BOLD, width=56),
            ft.Text("Prob.RI",   size=10, color=MUTED, weight=ft.FontWeight.BOLD, width=54),
            ft.Text("Nivel",     size=10, color=MUTED, weight=ft.FontWeight.BOLD, width=50),
        ]),
        bgcolor=SURFACE, padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=ft.border_radius.only(top_left=10, top_right=10),
    )
    trows = []
    for i, m in enumerate(MUNICIPIOS):
        iarri = calc(m["AV"],m["IC"],m["ED"],m["EAR"],m["IM"])
        niv, col = nivel(iarri)
        trows.append(ft.Container(
            content=ft.Row([
                ft.Text(m["nombre"].split()[0]+" "+m["nombre"].split()[1],
                        size=11, color=TEXT, expand=2),
                ft.Text(f"{iarri:.4f}", size=12, color=col,
                        weight=ft.FontWeight.BOLD, width=56, font_family="monospace"),
                ft.Text(f"{prob_ri(iarri)*100:.1f}%", size=12, color=TEXT, width=54),
                ft.Container(
                    content=ft.Text(niv, size=10, color=col, weight=ft.FontWeight.BOLD),
                    bgcolor=col+"22", border=ft.border.all(1, col+"55"),
                    border_radius=8, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    width=50,
                ),
            ]),
            bgcolor=CARD if i%2==0 else SURFACE,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
        ))

    return ft.Column([
        sec("Comparación municipal"), ft.Container(height=8),
        *rows,
        ft.Container(height=12),
        sec("Tabla epidemiológica"), ft.Container(height=8),
        ft.Container(
            content=ft.Column([hdr, *trows], spacing=1),
            border=ft.border.all(1, BORDER), border_radius=10,
        ),
        ft.Container(height=6),
        ft.Text("Prob(RI) = 0.10 + 0.50 × IARRI  —  Modelo conceptual ENSANUT",
                size=9, color=MUTED, italic=True),
        ft.Container(height=20),
    ], spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)


# ── TAB 3: MONTE CARLO ──────────────────────────────────────
def tab_mc(page):
    mc_base = {"AV": 0.30, "IC": 0.20, "ED": 0.10, "EAR": 0.80, "IM": 0.70}
    lbl_mean  = ft.Text("IRMA promedio: —", size=11, color=ACCENT, font_family="monospace")
    lbl_std   = ft.Text("Desviación estándar IRMA: —", size=11, color=ACCENT3, font_family="monospace")
    lbl_ci    = ft.Text("IC 95%: —", size=11, color=MID, font_family="monospace")
    hist_row  = ft.Row([], spacing=2, height=90,
                        vertical_alignment=ft.CrossAxisAlignment.END)
    btn_lbl   = ft.Text("▶  Ejecutar 1000 simulaciones",
                         size=13, weight=ft.FontWeight.BOLD, color="#000000")
    sigma_lbl = ft.Text("σ = 0.12", size=11, color=ACCENT3, width=60)
    sigma_s   = ft.Slider(min=0.05, max=0.25, value=0.12, divisions=40,
                           active_color=ACCENT3, inactive_color=BORDER, thumb_color=ACCENT3,
                           expand=True,
                           on_change=lambda e: (
                               sigma_lbl.__setattr__("value", f"σ = {e.control.value:.2f}"),
                               page.update()
                           ))
    muni_dd   = ft.Dropdown(
        value="Cuautlancingo",
        options=[ft.dropdown.Option(m["nombre"]) for m in MUNICIPIOS],
        bgcolor=CARD, color=TEXT, border_color=BORDER,
        focused_border_color=ACCENT, width=280,
        on_change=lambda e: mc_base.update(
            next(m for m in MUNICIPIOS if m["nombre"] == e.control.value)
        ),
    )

    def run(e):
        btn_lbl.value = "⏳  Calculando..."
        page.update()
        def _t():
            res, media, desv, ci_lo, ci_hi = monte_carlo(mc_base, 1000, sigma_s.value)
            counts, edges = np.histogram(res, bins=24, range=(0,1))
            mx = counts.max()
            hist_row.controls = [
                ft.Container(
                    bgcolor=ACCENT if abs(edges[i]-media) < 1/24 else
                            (LOW if edges[i] < 0.33 else (MID if edges[i] < 0.66 else HIGH)),
                    border_radius=ft.border_radius.only(top_left=2, top_right=2),
                    height=max(3, int(c/mx*86)), expand=True, opacity=0.9,
                )
                for i, c in enumerate(counts)
            ]
            lbl_mean.value = f"IRMA promedio: {media:.16f}"
            lbl_std.value  = f"Desviación estándar IRMA: {desv:.16f}"
            lbl_ci.value   = f"IC 95%: [{ci_lo:.4f},  {ci_hi:.4f}]"
            btn_lbl.value  = "▶  Ejecutar 1000 simulaciones"
            page.update()
        threading.Thread(target=_t, daemon=True).start()

    sens = [
        ("IC",  0.25, ACCENT,  "∂IARRI/∂IC  = −0.25"),
        ("EAR", 0.25, ACCENT2, "∂IARRI/∂EAR = +0.25"),
        ("AV",  0.20, LOW,     "∂IARRI/∂AV  = −0.20"),
        ("ED",  0.15, ACCENT3, "∂IARRI/∂ED  = −0.15"),
        ("IM",  0.15, MID,     "∂IARRI/∂IM  = +0.15"),
    ]

    return ft.Column([
        sec("Configuración"),ft.Container(height=8),
        card(ft.Column([
            ft.Text("Municipio base:", size=11, color=MUTED),
            muni_dd,
            ft.Row([ft.Text("Perturbación:",size=11,color=MUTED),
                    sigma_s, sigma_lbl], spacing=8),
        ], spacing=10)),
        ft.Container(height=8),
        ft.ElevatedButton(content=btn_lbl, bgcolor=ACCENT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            height=48, expand=True, on_click=run),
        ft.Container(height=12),
        sec("Distribución IARRI"), ft.Container(height=8),
        card(ft.Column([
            hist_row,
            ft.Row([ft.Text("0.0",size=9,color=MUTED), ft.Container(expand=True),
                    ft.Text("0.33",size=9,color=LOW),   ft.Container(expand=True),
                    ft.Text("0.66",size=9,color=MID),   ft.Container(expand=True),
                    ft.Text("1.0",size=9,color=HIGH)]),
            ft.Divider(color=BORDER),
            lbl_mean, lbl_std, lbl_ci,
        ], spacing=8)),
        ft.Container(height=12),
        sec("Análisis de sensibilidad ∂IARRI"), ft.Container(height=8),
        card(ft.Column([
            ft.Text("Derivadas parciales — impacto marginal",size=11,color=MUTED),
            *[ft.Row([
                ft.Text(k, size=11, color=MUTED, width=36, font_family="monospace"),
                ft.Stack([
                    ft.Container(height=8, border_radius=4, bgcolor=BORDER, width=200),
                    ft.Container(height=8, border_radius=4, bgcolor=c, width=int(v*800)),
                ]),
                ft.Text(f, size=10, color=c, font_family="monospace"),
            ], spacing=8) for k,v,c,f in sens],
            ft.Text("Mayor impacto: IC y EAR",size=10,color=MUTED,italic=True),
        ], spacing=8)),
        ft.Container(height=20),
    ], spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)


# ── TAB 4: INTERVENCIÓN ─────────────────────────────────────
def tab_interv(page):
    antes   = {"AV":0.30,"IC":0.20,"ED":0.10,"EAR":0.80,"IM":0.70}
    despues = {"AV":0.55,"IC":0.45,"ED":0.30,"EAR":0.80,"IM":0.70}
    ia  = calc(**antes)
    id_ = calc(**despues)
    red = (ia-id_)/ia*100

    RECS = [
        ("🌳",LOW,    "Incrementar Áreas Verdes",  "Corredores verdes. AV: 0.30→0.55",    "↓ IARRI −0.05 (−6.4%)"),
        ("🚶",ACCENT, "Ruta Diaria de 15 min",     "Banquetas e iluminación. IC: 0.20→0.45","↓ IARRI −0.0625 (−8%)"),
        ("⚽",ACCENT3,"Espacios Deportivos",        "2 unidades barriales. ED: 0.10→0.30", "↓ IARRI −0.03 (−3.8%)"),
        ("🏗️",ACCENT2,"Regulación Alimentaria",   "Reducir EAR: 0.80→0.60",              "↓ IARRI −0.05 (−6.4%)"),
        ("🪟",MID,    "Diseño Arquitectónico",     "Ventilación cruzada",                  "Compensación: +18%"),
    ]
    BADGES = [
        ("🏛️","Arquitecto Preventivo",True),
        ("🌱","Diseñador Bioactivo",  True),
        ("⚡","Agente Metabólico",    False),
        ("📊","Analista Territorial", False),
        ("🗺️","Mapeador Urbano",      True),
        ("🔬","Investigador IARRI",   False),
    ]

    badge_items = [
        ft.Container(
            content=ft.Column([
                ft.Text(em, size=26, opacity=1.0 if e else 0.3),
                ft.Text(nm, size=9, text_align=ft.TextAlign.CENTER,
                        color=TEXT if e else MUTED,
                        weight=ft.FontWeight.W_600 if e else ft.FontWeight.NORMAL),
                ft.Text("✓" if e else "🔒", size=9, color=ACCENT3 if e else MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
            bgcolor=ACCENT3+"11" if e else CARD,
            border=ft.border.all(1, ACCENT3 if e else BORDER),
            border_radius=12, padding=10, expand=True,
        )
        for em, nm, e in BADGES
    ]

    return ft.Column([
        sec("Simulación — Cuautlancingo"), ft.Container(height=8),
        ft.Row([
            ft.Container(content=ft.Column([
                ft.Text(f"{ia:.4f}",size=20,weight=ft.FontWeight.W_900,color=HIGH),
                ft.Text("Antes",size=10,color=MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2),
            bgcolor=CARD,border=ft.border.all(1,BORDER),border_radius=12,padding=12,expand=True),
            ft.Container(content=ft.Text("→",size=22,color=ACCENT),padding=8),
            ft.Container(content=ft.Column([
                ft.Text(f"{id_:.4f}",size=20,weight=ft.FontWeight.W_900,color=MID),
                ft.Text("Después",size=10,color=MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2),
            bgcolor=CARD,border=ft.border.all(1,BORDER),border_radius=12,padding=12,expand=True),
            ft.Container(content=ft.Column([
                ft.Text(f"−{red:.1f}%",size=20,weight=ft.FontWeight.W_900,color=ACCENT),
                ft.Text("Reducción",size=10,color=MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2),
            bgcolor=CARD,border=ft.border.all(1,BORDER),border_radius=12,padding=12,expand=True),
        ], spacing=6),
        ft.Container(height=8),
        card(ft.Column([
            *[ft.Column([
                ft.Row([
                    ft.Text(k,size=12,color=col,weight=ft.FontWeight.BOLD,
                            width=32,font_family="monospace"),
                    ft.Text(d,size=11,color=TEXT,expand=True),
                    ft.Text(f"{va:.2f}→{vd:.2f}",size=11,color=col,font_family="monospace"),
                ]),
                ft.Row([ft.Text("Antes:",size=9,color=MUTED,width=44),barra(va,MUTED,5)],spacing=6),
                ft.Row([ft.Text("Después:",size=9,color=col,width=44),barra(vd,col,5)],spacing=6),
            ], spacing=3)
            for k,va,vd,col,d in [("AV",0.30,0.55,LOW,"Áreas verdes"),
                                    ("IC",0.20,0.45,ACCENT,"Caminabilidad"),
                                    ("ED",0.10,0.30,ACCENT3,"Equipamiento dep.")]],
            ft.Container(
                content=ft.Text(f"↓ Reducción: {red:.1f}%  —  Potencial preventivo del diseño urbano",
                                 size=11,color=ACCENT,text_align=ft.TextAlign.CENTER),
                bgcolor=ACCENT+"11",border=ft.border.all(1,ACCENT+"33"),
                border_radius=10,padding=10,
            ),
        ], spacing=8)),
        ft.Container(height=12),
        sec("Recomendaciones arquitectónicas"), ft.Container(height=6),
        *[card(ft.Row([
            ft.Container(content=ft.Text(ic,size=22), bgcolor=col+"22",border_radius=10,
                         width=44,height=44,alignment=ft.alignment.Alignment(0,0)),
            ft.Column([
                ft.Text(ti,size=13,weight=ft.FontWeight.W_600,color=TEXT),
                ft.Text(de,size=11,color=MUTED),
                ft.Text(im,size=11,color=col,weight=ft.FontWeight.BOLD),
            ], spacing=2,expand=True),
        ], spacing=12)) for ic,col,ti,de,im in RECS],
        ft.Container(height=12),
        sec("Insignias"), ft.Container(height=8),
        ft.Row(badge_items[:3],spacing=6),
        ft.Container(height=6),
        ft.Row(badge_items[3:],spacing=6),
        ft.Container(height=20),
    ], spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)


# ── APP PRINCIPAL ────────────────────────────────────────────
def main(page: ft.Page):
    page.title      = "ARQ-Metabolica MX"
    page.bgcolor    = BG
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width  = 400
    page.window_height = 800

    header = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("ARQ-Metabólica MX", size=17,
                        weight=ft.FontWeight.W_900, color=ACCENT),
                ft.Text("IARRI-MX  ·  Puebla, México", size=10, color=MUTED),
            ], spacing=0),
            ft.Container(
                content=ft.Text("v1.0", size=10, color=ACCENT, weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT+"22", border=ft.border.all(1, ACCENT+"44"),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        expand=True,
        tab_alignment=ft.TabAlignment.FILL,
        label_color=ACCENT,
        unselected_label_color=MUTED,
        indicator_color=ACCENT,
        divider_color=BORDER,
        tabs=[
            ft.Tab(text="Calcular",    icon=ft.icons.CALCULATE_OUTLINED,
                   content=ft.Container(content=tab_calc(page),
                       padding=ft.padding.symmetric(horizontal=16,vertical=8),expand=True)),
            ft.Tab(text="Municipios",  icon=ft.icons.LOCATION_CITY_OUTLINED,
                   content=ft.Container(content=tab_municipios(page),
                       padding=ft.padding.symmetric(horizontal=16,vertical=8),expand=True)),
            ft.Tab(text="Monte Carlo", icon=ft.icons.BAR_CHART_OUTLINED,
                   content=ft.Container(content=tab_mc(page),
                       padding=ft.padding.symmetric(horizontal=16,vertical=8),expand=True)),
            ft.Tab(text="Intervención",icon=ft.icons.SHIELD_OUTLINED,
                   content=ft.Container(content=tab_interv(page),
                       padding=ft.padding.symmetric(horizontal=16,vertical=8),expand=True)),
        ],
    )

    page.add(ft.Column([header, tabs], spacing=0, expand=True))

if __name__ == "__main__":
    ft.app(target=main)
