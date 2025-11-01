# 📚 Guía Completa de Alembic - Migraciones de Base de Datos

## 🤔 ¿Qué es Alembic?

**Alembic es un sistema de migraciones de base de datos para SQLAlchemy.** Piensa en él como **Git pero para tu base de datos**.

### ¿Por qué lo necesitamos?

Sin Alembic:

- ❌ Cambios manuales en SQL: `ALTER TABLE users ADD COLUMN phone VARCHAR(20);`
- ❌ Difícil rastrear qué cambios se hicieron y cuándo
- ❌ Cada desarrollador tiene una estructura de DB diferente
- ❌ En producción, ¿cómo sabes qué cambios aplicar?

Con Alembic:

- ✅ Cada cambio queda registrado en archivos Python versionados
- ✅ Puedes aplicar y revertir cambios de forma controlada
- ✅ Todo el equipo tiene la misma estructura de DB
- ✅ Despliegues a producción seguros y predecibles

---

## 📁 Estructura de Archivos

```text
proyecto/
├── alembic/
│   ├── versions/                    # 📂 Aquí van las migraciones
│   │   ├── 001_create_users.py
│   │   ├── 002_add_phone_to_users.py
│   │   └── 003_create_products.py
│   ├── env.py                       # ⚙️ Configuración de Alembic
│   └── script.py.mako               # 📝 Plantilla para nuevas migraciones
├── alembic.ini                      # ⚙️ Configuración general
└── app/
    └── models/                      # 🗂️ Tus modelos SQLAlchemy
```

---

## 🚀 Comandos Básicos (Los que usarás diario)

### 1. Ver el estado actual

```bash
# ¿Qué migración está aplicada actualmente?
alembic current

# Respuesta ejemplo:
# abc123def456 (head)
```

### 2. Ver historial de migraciones

```bash
# Ver todas las migraciones disponibles
alembic history

# Ver con más detalle
alembic history --verbose
```

Ejemplo de salida:

```text
abc123 -> def456 (head), add phone to users
       -> abc123, create users table
<base> -> 
```

### 3. Crear una nueva migración (AUTOGENERADA)

```bash
# Alembic compara tus modelos con la DB y genera el código automáticamente
alembic revision --autogenerate -m "descripción del cambio"
```

**Ejemplo:**

```bash
alembic revision --autogenerate -m "add phone to users"
```

Esto:

1. Lee tus modelos SQLAlchemy (`app/models/user.py`)
2. Se conecta a PostgreSQL y lee la estructura actual
3. Compara ambos
4. Genera un archivo Python con los cambios

### 4. Aplicar migraciones

```bash
# Aplicar TODAS las migraciones pendientes
alembic upgrade head

# Aplicar solo la siguiente migración
alembic upgrade +1

# Aplicar hasta una migración específica
alembic upgrade abc123
```

### 5. Revertir migraciones

```bash
# Revertir la última migración
alembic downgrade -1

# Revertir 2 migraciones
alembic downgrade -2

# Volver a una migración específica
alembic downgrade abc123

# Volver al inicio (CUIDADO: elimina todo)
alembic downgrade base
```

---

## 🔄 Flujo de Trabajo Completo (Paso a Paso)

### Escenario 1: Agregar una nueva tabla

**Paso 1:** Crea el modelo en SQLAlchemy

```python
# app/models/product.py
from sqlalchemy import Column, String, Float
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, nullable=False)
```

**Paso 2:** Importa el modelo en `app/models/__init__.py`

```python
from app.models.user import User
from app.models.product import Product  # ← NUEVO
```

**Paso 3:** Importa el modelo en `alembic/env.py`

```python
# alembic/env.py
from app.models import User, Product  # ← Agrega Product
```

**Paso 4:** Genera la migración

```bash
alembic revision --autogenerate -m "create products table"
```

Verás:

```bash
INFO  [alembic.autogenerate.compare] Detected added table 'products'
Generating /alembic/versions/def456_create_products_table.py ...  done
```

**Paso 5:** Revisa el archivo generado

Abre `alembic/versions/def456_create_products_table.py`:

```python
def upgrade() -> None:
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        # ... timestamps, etc
        sa.PrimaryKeyConstraint('id')
    )
```

**Paso 6:** Aplica la migración

```bash
alembic upgrade head
```

✅ ¡Tabla creada en PostgreSQL!

---

### Escenario 2: Agregar una columna a una tabla existente

**Paso 1:** Modifica el modelo

```python
# app/models/user.py
class User(BaseModel):
    # ... campos existentes ...
    phone = Column(String, nullable=True)  # ← NUEVA COLUMNA
```

**Paso 2:** Genera migración

```bash
alembic revision --autogenerate -m "add phone to users"
```

**Paso 3:** Revisa y aplica

```bash
# Revisar el archivo generado si quieres
# alembic/versions/xxx_add_phone_to_users.py

# Aplicar
alembic upgrade head
```

---

### Escenario 3: Modificar una columna existente

**⚠️ IMPORTANTE:** Alembic **NO siempre detecta** cambios en columnas (ej: cambiar tipo de dato). A veces debes hacerlo manual.

**Paso 1:** Modifica el modelo

```python
# Cambiar phone de String a String(20)
phone = Column(String(20), nullable=False)  # Antes era nullable=True
```

**Paso 2:** Genera migración

```bash
alembic revision --autogenerate -m "modify phone column"
```

**Paso 3:** ⚠️ REVISA EL ARCHIVO

A veces Alembic no detecta el cambio. Si el archivo está vacío:

```python
def upgrade() -> None:
    pass  # ← Vacío, Alembic no detectó nada
```

**Edita manualmente:**

```python
def upgrade() -> None:
    op.alter_column('users', 'phone',
                    existing_type=sa.String(),
                    type_=sa.String(length=20),
                    nullable=False)

def downgrade() -> None:
    op.alter_column('users', 'phone',
                    existing_type=sa.String(length=20),
                    type_=sa.String(),
                    nullable=True)
```

**Paso 4:** Aplica la migración

```bash
alembic upgrade head
```

---

### Escenario 4: Eliminar una columna

**Paso 1:** Elimina del modelo

```python
# app/models/user.py
class User(BaseModel):
    # ... campos existentes ...
    # phone = Column(String)  ← COMENTADO O ELIMINADO
```

**Paso 2:** Genera y aplica

```bash
alembic revision --autogenerate -m "remove phone from users"
alembic upgrade head
```

---

## 🛠️ Comandos Avanzados

### Ver SQL sin ejecutar (dry-run)

```bash
# Ver qué SQL se ejecutaría sin aplicar cambios
alembic upgrade head --sql
```

### Crear migración vacía (para editar manualmente)

```bash
alembic revision -m "custom migration"
```

Útil cuando necesitas:

- Insertar datos iniciales (seed data)
- Hacer cambios complejos que Alembic no detecta
- Ejecutar SQL personalizado

### Marcar una migración como aplicada (sin ejecutarla)

```bash
# Útil si aplicaste cambios manualmente en la DB
alembic stamp head
```

---

## 📊 La Tabla `alembic_version`

Alembic crea esta tabla automáticamente en tu DB:

```sql
SELECT * FROM alembic_version;
```

```text
 version_num 
-------------
 def456abc789
```

**¿Qué significa?**

- `def456abc789` es el ID de la última migración aplicada
- Alembic usa esto para saber desde dónde continuar
- **NO modifiques esta tabla manualmente** (salvo que sepas lo que haces)

---

## 🔥 Casos Comunes y Soluciones

### ❌ Error: "Can't locate revision identified by 'xxxx'"

**Causa:** Alguien borró un archivo de migración o la DB tiene una migración que no existe.

**Solución:**

```bash
# Ver qué migración está en la DB
alembic current

# Ver migraciones disponibles
alembic history

# Si falta un archivo, puedes "stampar" a una migración válida
alembic stamp abc123
```

---

### ❌ Error: "Target database is not up to date"

**Causa:** Hay migraciones pendientes.

**Solución:**

```bash
alembic upgrade head
```

---

### ❌ Alembic no detecta mis cambios

**Causas comunes:**

1. No importaste el modelo en `alembic/env.py`
2. No importaste el modelo en `app/models/__init__.py`
3. El cambio es muy sutil (tipo de columna, longitud, etc.)

**Solución:**

```python
# Verifica que esté en alembic/env.py:
from app.models import User, Product, Sale  # ← Todos tus modelos

# Si sigue sin detectar, crea migración vacía y edítala manualmente:
alembic revision -m "manual changes"
```

---

### ❌ Conflicto: Dos desarrolladores crearon migraciones al mismo tiempo

**Escenario:**

- Developer A crea: `abc123_add_phone.py` (down_revision = `xyz789`)
- Developer B crea: `def456_add_address.py` (down_revision = `xyz789`)
- Ambos apuntan a la misma migración padre → conflicto

**Solución:**

```bash
# Developer B debe "rebasar" su migración
alembic merge abc123 def456 -m "merge migrations"
```

Esto crea una migración que une ambas ramas.

---

## 📝 Buenas Prácticas

### ✅ SIEMPRE revisa las migraciones autogeneradas

```bash
alembic revision --autogenerate -m "add something"

# NO hagas upgrade inmediatamente
# PRIMERO abre el archivo generado y revisa que esté correcto
# LUEGO aplica:
alembic upgrade head
```

### ✅ Nombres descriptivos

```bash
# ❌ Malo
alembic revision --autogenerate -m "changes"

# ✅ Bueno
alembic revision --autogenerate -m "add phone and address to users table"
```

### ✅ Una migración = Un cambio lógico

```bash
# ❌ Malo: Mezclar cambios no relacionados
alembic revision --autogenerate -m "add users and products and sales"

# ✅ Bueno: Separar en múltiples migraciones
alembic revision --autogenerate -m "create users table"
alembic revision --autogenerate -m "create products table"
alembic revision --autogenerate -m "create sales table"
```

### ✅ Nunca modifiques migraciones ya aplicadas

Si una migración ya está en producción, **NO la edites**. Crea una nueva migración con el cambio.

```bash
# ❌ Malo: Editar 001_create_users.py después de aplicarla

# ✅ Bueno: Crear nueva migración
alembic revision --autogenerate -m "fix users table"
```

### ✅ Haz backup antes de cambios grandes

```bash
# Backup de PostgreSQL antes de migraciones importantes
pg_dump -U usuario optikt_db > backup_$(date +%Y%m%d).sql

# Luego aplica migración
alembic upgrade head
```

---

## 🚨 Emergencias

### Revertir TODO (destruir y recrear DB)

```bash
# ⚠️ ESTO BORRA TODA LA DATA

# 1. Revertir todas las migraciones
alembic downgrade base

# 2. O drop/create la DB manualmente
psql -U usuario
DROP DATABASE optikt_db;
CREATE DATABASE optikt_db;
\q

# 3. Aplicar migraciones desde cero
alembic upgrade head
```

### Resetear Alembic (mantener data)

Si Alembic está roto pero tu DB está bien:

```bash
# 1. Eliminar tabla de versiones
psql -U usuario -d optikt_db
DROP TABLE alembic_version;
\q

# 2. Re-stampar a la migración actual
alembic stamp head
```

---

## 📚 Resumen de Comandos

| Comando | Descripción |
|---------|-------------|
| `alembic current` | Ver migración actual |
| `alembic history` | Ver historial de migraciones |
| `alembic revision --autogenerate -m "msg"` | Crear nueva migración (auto) |
| `alembic revision -m "msg"` | Crear migración vacía (manual) |
| `alembic upgrade head` | Aplicar todas las migraciones |
| `alembic upgrade +1` | Aplicar siguiente migración |
| `alembic downgrade -1` | Revertir última migración |
| `alembic downgrade base` | Revertir todo (⚠️ peligroso) |
| `alembic stamp head` | Marcar como aplicada sin ejecutar |
| `alembic upgrade head --sql` | Ver SQL sin ejecutar |

---

## 🎓 Workflow Diario

```bash
# 1. Modificas un modelo en app/models/
# 2. Importas el modelo en app/models/__init__.py y alembic/env.py
# 3. Generas migración
alembic revision --autogenerate -m "descripción clara"

# 4. REVISAS el archivo generado en alembic/versions/
# 5. Si está bien, aplicas
alembic upgrade head

# 6. Commit en Git (incluye el archivo de migración)
git add alembic/versions/xxx_descripcion.py
git commit -m "migration: descripción clara"
```

---

## 🤝 Para el Equipo

Cuando hagas `git pull` y haya nuevas migraciones:

```bash
# 1. Pull del repo
git pull origin main

# 2. Ver si hay migraciones nuevas
alembic history

# 3. Aplicar migraciones pendientes
alembic upgrade head

# 4. Listo para desarrollar
```

---

## 📞 ¿Dudas?

- Documentación oficial: <https://alembic.sqlalchemy.org/>
- Si Alembic no detecta cambios, revisa `alembic/env.py`
- Si hay errores, lee el mensaje completo (suele ser claro)
- En caso de duda, pregunta antes de hacer `downgrade base` 😅

---

## **¡Happy Migrating! 🚀**
