# ARQ-Metabólica MX 🏛️📱
### App Móvil con Flet (Python + Flutter)
**Índice Arquitectónico de Riesgo de Resistencia a la Insulina (IARRI-MX)**

---

## ▶️ Correr en tu PC (preview móvil)

```bash
pip install flet numpy scipy
python main.py
```

---

## 📱 Compilar APK para Android

### Requisitos
- Python 3.9+
- Flutter SDK instalado → https://flutter.dev/docs/get-started/install
- Android Studio + Android SDK

### Pasos

```bash
# 1. Instalar flet con soporte build
pip install flet numpy scipy

# 2. Entrar a la carpeta del proyecto
cd arq_metabolica_flet

# 3. Compilar APK
flet build apk

# El APK quedará en:
#   build/apk/arq-metabolica-mx.apk
```

### Instalar en el celular
```bash
# Con el celular conectado por USB (modo desarrollador activado)
adb install build/apk/arq-metabolica-mx.apk
```

---

## 🍎 Compilar para iOS (solo macOS)

```bash
flet build ipa
```

---

## 📱 Publicar en Google Play / App Store

```bash
# Android (AAB para Play Store)
flet build aab

# iOS (archivo .ipa para App Store)
flet build ipa --team-id TU_TEAM_ID
```

---

## 📁 Estructura

```
arq_metabolica_flet/
├── main.py           ← App completa (única fuente)
├── pyproject.toml    ← Configuración del proyecto
└── README.md
```

---

## 📱 Pantallas de la App

| Pantalla | Descripción |
|----------|-------------|
| 🏠 **Inicio** | Selector de municipio, IARRI en grande, semáforo, 5 tarjetas de variables, análisis de sensibilidad, fórmula |
| 🗺️ **Mapa** | Mapa SVG con heatmaps, comparativa municipal con barras, tabla epidemiológica Prob(RI) |
| 🧮 **Calcular** | 5 sliders interactivos, cálculo en tiempo real, desglose por variable, Monte Carlo 1000 iter. con histograma |
| 🛡️ **Intervención** | KPIs, recomendaciones expandibles, simulación Cuautlancingo 0.78→0.64, insignias gamificadas |

---

## 🧮 Fórmula IARRI

```
IARRI = 0.20(1−AV) + 0.25(1−IC) + 0.15(1−ED) + 0.25(EAR) + 0.15(IM)
```

| Var | Descripción | Peso |
|-----|-------------|------|
| AV  | Áreas Verdes (OMS 9 m²/hab) | 0.20 |
| IC  | Índice de Caminabilidad | 0.25 |
| ED  | Equipamiento Deportivo | 0.15 |
| EAR | Entorno Alimentario Riesgoso | 0.25 |
| IM  | Índice de Marginación (CONAPO) | 0.15 |

---

## 📊 Resultados — 3 Municipios de Puebla

| Municipio | IARRI | Riesgo |
|-----------|-------|--------|
| San Andrés Cholula | 0.3575 | Medio |
| San Pablo Xochimehuacan | 0.6150 | Medio-Alto |
| Cuautlancingo | 0.7800 | Alto |

---

## 🎯 ODS 3 — Salud  ·  ODS 11 — Ciudades Sostenibles
