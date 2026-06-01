# OcularGuard — Plataforma de Diagnóstico Ocular IA

App web para pre-diagnóstico de patologías oculares usando imágenes de fondo de ojo analizadas con IA (Claude Vision).

---

## Inicio rápido

### Opción A — Un solo click (recomendado)

Doble click en **`start.bat`** en la raíz del proyecto.

Abre automáticamente el backend, el frontend y el browser.

---

### Opción B — Manual (dos terminales)

#### Terminal 1 — Backend

```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Espera hasta ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2 — Frontend

```powershell
cd frontend
python -m http.server 5500
```

Luego abre el browser en:
```
http://localhost:5500/pages/login.html
```

---

## Primera vez (instalación)

Solo necesitas hacer esto una vez:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y completa tu API key de Anthropic si tienes una (sin ella funciona con datos de prueba).

---

## Credenciales demo

| Campo    | Valor                          |
|----------|-------------------------------|
| Email    | `dr.garcia@ocularguard.com`   |
| Password | `demo1234`                    |

---

## URLs

| Servicio     | URL                                      |
|--------------|------------------------------------------|
| App (login)  | http://localhost:5500/pages/login.html   |
| Backend API  | http://localhost:8000                    |
| Docs API     | http://localhost:8000/docs               |

---

## Pantallas

| Pantalla       | Archivo                        | Descripción                        |
|----------------|--------------------------------|------------------------------------|
| Login          | `frontend/pages/login.html`    | Acceso con credenciales clínicas   |
| Estudio        | `frontend/pages/study.html`    | Carga de imagen + ID de paciente   |
| Pre-diagnóstico| `frontend/pages/results.html`  | Resultados del análisis IA         |

---

## Estructura del proyecto

```
EYEAPP/
├── start.bat                  ← Arranque rápido (doble click)
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI entry point
│   │   ├── config.py          ← Variables de entorno
│   │   ├── dependencies.py    ← Autenticación JWT
│   │   ├── core/security.py   ← Hash + JWT
│   │   ├── models/            ← Esquemas Pydantic
│   │   ├── routes/            ← Endpoints API
│   │   └── services/          ← Lógica + Claude API
│   ├── .env                   ← Variables locales (no subir a git)
│   ├── .env.example           ← Plantilla de variables
│   └── requirements.txt
└── frontend/
    ├── pages/
    │   ├── login.html
    │   ├── study.html
    │   └── results.html
    └── assets/
        ├── js/api.js           ← Cliente HTTP centralizado
        └── css/custom.css
```

---

## Stack tecnológico

| Capa      | Tecnología                        |
|-----------|-----------------------------------|
| Backend   | Python 3.13 + FastAPI + Uvicorn   |
| IA        | Claude Vision (Anthropic API)     |
| Auth      | JWT (python-jose + passlib)       |
| Frontend  | HTML + Tailwind CSS + Alpine.js   |

---

## Notas importantes

- El análisis IA funciona **sin API key** usando datos de prueba (mock).
- **No abrir** `login.html` directamente desde el explorador de archivos — usar siempre `http://localhost:5500`.
- Los servidores se detienen al cerrar las terminales.
