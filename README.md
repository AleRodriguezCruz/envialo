# Envialo 📦

Clon de WeTransfer construido con FastAPI, PostgreSQL y Supabase. Permite subir archivos, compartirlos mediante un link seguro y enviar notificaciones por correo al destinatario.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Supabase](https://img.shields.io/badge/Supabase-Storage-black)

---

## Stack tecnológico

- **Backend:** Python 3.11 + FastAPI
- **Base de datos principal:** PostgreSQL (Docker)
- **Almacenamiento de archivos:** Supabase Storage
- **Logs de auditoría:** Supabase (tabla `audit_logs`)
- **Correos:** Resend
- **Frontend:** HTML + CSS + JS vanilla
- **Contenedores:** Docker + Docker Compose
- **Migraciones:** Alembic
- **Worker de limpieza:** APScheduler

---

## Arquitectura

Frontend (HTML/JS)
↓
API Routes (FastAPI)
↓
Servicios (lógica de negocio)
↓
Repositorios (acceso a DB)
↓
PostgreSQL (metadata) + Supabase (archivos binarios)

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/upload` | Sube un archivo y retorna el token |
| GET | `/api/v1/download/{token}` | Retorna URLs firmadas de descarga |
| GET | `/api/v1/file/{token}` | Obtiene información del transfer |
| DELETE | `/api/v1/file/{token}` | Elimina un transfer y sus archivos |
| GET | `/health` | Verifica que la app está corriendo |

---

## Seguridad implementada

- Validación de MIME real con **magic bytes** (no por extensión)
- Protección contra **path traversal**
- Bloqueo de **scripts ejecutables** (.exe, .bat, .sh, etc.)
- Tokens seguros con **UUID + secrets**
- Límite de tamaño configurable (default 100 MB)
- Manejo de errores: 413, 415, 404, 410
- Archivos servidos mediante **URLs firmadas** de Supabase (nunca exposición directa)

---

## Instalación y configuración

### Requisitos previos

- Python 3.11+
- Docker Desktop
- Git
- Cuenta en [Supabase](https://supabase.com)
- Cuenta en [Resend](https://resend.com)

### 1. Clonar el repositorio

```bash
git clone https://github.com/AleRodriguezCruz/envialo.git
cd envialo
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# POSTGRESQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=wetransfer_user
POSTGRES_PASSWORD=wetransfer_secret
POSTGRES_DB=wetransfer_db

# SUPABASE
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_KEY=tu-service-key
SUPABASE_BUCKET=transfers

# RESEND
RESEND_API_KEY=re_tu-api-key
RESEND_FROM_EMAIL=onboarding@resend.dev

# SEGURIDAD
SECRET_KEY=genera-uno-con-secrets.token_hex(32)
```

### 3. Configurar Supabase

1. Crea un proyecto en [supabase.com](https://supabase.com)
2. Ve a **SQL Editor** y ejecuta el script `scripts/setup_supabase.sql`
3. Esto crea el bucket `transfers` y la tabla `audit_logs`

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Levantar PostgreSQL con Docker

```bash
docker compose up postgres -d
```

### 6. Correr migraciones

```bash
python -m alembic upgrade head
```

### 7. Iniciar la aplicación

```bash
python -m uvicorn app.main:app --reload --port 8000
```

La app estará disponible en:
- **Frontend:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `APP_ENV` | Entorno (development/production) | `development` |
| `APP_PORT` | Puerto del servidor | `8000` |
| `MAX_FILE_SIZE` | Tamaño máximo en bytes | `104857600` (100MB) |
| `TRANSFER_EXPIRY_HOURS` | Horas antes de expirar | `72` |
| `CLEANUP_INTERVAL_HOURS` | Intervalo del worker de limpieza | `6` |
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` |
| `SUPABASE_URL` | URL del proyecto Supabase | — |
| `RESEND_API_KEY` | API key de Resend | — |

---

## Worker de limpieza

El worker se ejecuta automáticamente cada `CLEANUP_INTERVAL_HOURS` horas y elimina transfers expirados de Supabase Storage y los marca en PostgreSQL.

Para ejecutarlo manualmente:

```bash
python scripts/run_worker.py
```

---

## Estructura del proyecto

envialo/
├── app/
│   ├── api/          # Controladores y rutas de la API
│   ├── core/         # Configuración, seguridad y excepciones
│   ├── db/           # Modelos de SQLAlchemy y conexión a DB
│   ├── repositories/ # Patrón Repository (Acceso a datos)
│   ├── services/     # Lógica de negocio (Servicios orquestadores)
│   └── workers/      # Tareas de limpieza en segundo plano
├── frontend/         # Interfaz de usuario (HTML/JS)
├── migrations/       # Scripts de migración de Alembic
└── scripts/          # Utilidades de automatización

---

👥 Créditos e Integrantes

Este proyecto fue desarrollado con un enfoque profesional y educativo por:

    Alejandra Rodríguez de la Cruz - GitHub

    Flor Jazmín Mayon Cisneros

## Screenshots

### Interfaz de subida
![Interfaz de subida](screenshots/upload.png)

### Correo recibido
![Correo recibido](screenshots/email.png)