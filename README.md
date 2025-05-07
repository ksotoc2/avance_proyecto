# 📚 Proyecto Django - Sistema de Préstamos de Libros

Este proyecto es una plataforma web para la gestión de préstamos de libros en una institución educativa. Incluye roles de usuario (docente, bibliotecario, director), panel de administración, reportes en PDF y sistema de generación de datos semilla.

---

## ✅ Requisitos

- Python 3.11 o superior
- pip
- Entorno virtual (recomendado)

---

## 🚀 Pasos para la instalación

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd biblioteca_docentes
```

### 2. Crear y activar el entorno virtual

```bash
# En Windows
python -m venv env
env\Scripts\activate

# En Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configurar la base de datos

### 4. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌱 Generar datos de prueba (seeders)

Puedes poblar la base de datos con usuarios, libros, préstamos y devoluciones usando estos comandos:

```bash
# Crear usuarios (docentes, bibliotecarios y directores)
python manage.py seed_usuarios --docentes 10 --bibliotecarios 2 --directores 1

# Crear categorías y libros
python manage.py seed_libros --categorias 8 --libros 50

# Crear préstamos y devoluciones
python manage.py seed_prestamos --prestamos 30 --porcentaje_devueltos 60 --porcentaje_retrasados 20
```

> 🔐 **Notas importantes:**
> - Todos los usuarios creados tendrán la contraseña por defecto: `password123`
> - El usuario admin creado tendrá como contraseña: `admin123`

---

## 🖥️ Ejecutar el servidor

```bash
python manage.py runserver
```

Visita: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔐 Acceso al panel de administración

Puedes acceder al panel de Django en:

[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 🧪 Extras

- Reportes PDF disponibles desde las vistas con filtros.
- Control de acceso según rol de usuario.

---

## 📁 Estructura base

```
biblioteca_docentes/
│
├── biblioteca_docentes/       # Proyecto Django
├── app1/, app2/, etc.         # Aplicaciones separadas por módulos
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## 🧑‍💻 Autor

Proyecto desarrollado para fines educativos.
