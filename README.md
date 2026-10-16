<div align="center">
  <img src="frontend/public/puntuador-mascots-v3.png" alt="Logo de Puntuador-inador" width="260" />

# Puntuador-inador

### Cada capítulo merece su estrella.

Tu espacio para organizar series y anime, guardar tus impresiones y descubrir qué ver después.

**Vue 3 · TypeScript · FastAPI · SQLite**

[Primeros pasos](#-primeros-pasos) · [Funciones](#-qué-puedes-hacer) · [Estructura](#-estructura-del-proyecto) · [Solución de problemas](#-solución-de-problemas)

</div>

---

## ✨ ¿Qué es Puntuador-inador?

Una aplicación local para llevar tu colección de series y anime **capítulo a capítulo**. Cada perfil tiene su propia biblioteca, favoritas, comentarios y puntuaciones, con una interfaz ilustrada y modos claro y oscuro.

Las valoraciones van de **0.5 a 5 estrellas**, en incrementos de media estrella. El progreso representa **capítulos puntuados**: la aplicación no reproduce videos ni registra minutos de reproducción.

> **Sin Docker ni servidor de base de datos aparte.** Los datos se guardan en un archivo SQLite en tu equipo. Necesitas Node.js y Python para ejecutar la aplicación.

## 🎬 Qué puedes hacer

| Módulo | Funciones |
| --- | --- |
| **Inicio** | Saludo del perfil, continuar puntuando, próximos capítulos importados, actividad reciente y estadísticas. |
| **Mi colección** | Todas tus series, búsqueda por título, filtros de estado y género, solo favoritas, orden por nombre o puntuación y vista de tarjetas o lista. |
| **Ficha de serie** | Temporadas y tabla de capítulos; editor de estrellas y comentarios; importación, actualización y agregado manual de episodios. |
| **Ranking** | Consulta tus valoraciones y los capítulos mejor puntuados. |
| **Configuración** | Apariencia, color de acento, colección compacta, exportación de datos y gestión de perfiles. |
| **Recomendaciones** | Sugerencias del catálogo guardado, motivos de afinidad y opción de agregarlas a pendientes. |

### Perfiles independientes

- Crea y edita perfiles con nombre, descripción, avatar y color.
- Sube una imagen JPG, PNG o WebP de hasta 2 MB; se optimiza y guarda en SQLite.
- Cambia de perfil sin mezclar colecciones ni puntuaciones.
- El navegador recuerda el perfil seleccionado al volver a abrir la página.
- Puedes eliminar perfiles con confirmación; siempre debe quedar al menos uno.

Los perfiles son locales y **no tienen contraseña**. La apariencia general es compartida; el color y avatar de cada perfil son independientes.

### Una colección a tu medida

La sidebar tiene cuatro accesos: **Inicio, Mi colección, Ranking y Configuración**. Siguiendo, Pendientes, Terminadas y Favoritas se consultan mediante filtros de la colección.

Los filtros se reflejan en la URL, por ejemplo:

```text
#/coleccion?estado=siguiendo
#/coleccion?estado=pendiente&favoritas=true
#/coleccion?genero=Drama
```

En Configuración puedes probar un color de acento con **vista previa inmediata**. Pulsa **Guardar configuración** para conservarlo: se aplica a botones, enlaces, bordes, selección y progreso. El fondo, el logo y los colores de estado conservan su identidad.

## 🚀 Primeros pasos

### Requisitos

- **Node.js:** `^22.18.0` o `>=24.12.0`, con npm.
- **Python 3.13:** versión utilizada para el entorno del proyecto.
- Internet para instalar dependencias, consultar catálogos y cargar portadas externas.

Ejecuta los comandos desde la raíz del proyecto.

### Preparación en Windows · PowerShell

```powershell
py -3.13 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend install
```

### Preparación en macOS / Linux

```bash
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend install
```

### Iniciar la aplicación

```powershell
npm --prefix frontend run dev
```

Abre la dirección **Local** que indique Vite en la terminal. El puerto habitual es `5173`, pero puede cambiar si está ocupado.

Este comando inicia el frontend y, si hace falta, la API Python en `127.0.0.1:8000`. Espera a que la API esté lista y muestra su salida en la misma terminal. Si ya existe una API compatible, la reutiliza.

**Mantén la terminal abierta.** Para detener la aplicación, pulsa `Ctrl+C`. No hace falta iniciarla como servicio ni dejar un proceso separado en segundo plano.

### Tu primera serie

1. Crea o selecciona un perfil.
2. Pulsa **Explorar series y anime** en Inicio o **Agregar serie** en Colección.
3. Elige el catálogo, busca un título y selecciona su estado inicial.
4. Abre la serie desde su portada para consultar los capítulos.
5. Pulsa **Puntuar**, elige las estrellas y guarda tu comentario.

Después de guardar, puedes usar **Volver a puntuar** para editar la valoración.

## 🔎 Catálogos y recomendaciones

### Series y anime

| Proveedor | Uso |
| --- | --- |
| **TVmaze** | Búsqueda de series, portadas, metadatos y capítulos. |
| **Jikan / MyAnimeList** | Búsqueda de anime e importación de episodios, sin configurar una clave de API. |

Las búsquedas se almacenan en SQLite durante una hora, con un máximo de 200 consultas guardadas. Ante un fallo del proveedor se pueden reutilizar resultados anteriores. Jikan cuenta con reintentos limitados para errores temporales.

Algunos títulos requieren su nombre original. En MyAnimeList, distintas temporadas, especiales o películas pueden aparecer como fichas separadas. Si faltan episodios, puedes agregarlos manualmente. Actualizar los capítulos conserva sus puntuaciones.

### Cómo se eligen las recomendaciones

Las sugerencias se calculan **localmente a partir de las búsquedas guardadas**, sin consultar Jikan cada vez que abres Inicio:

1. Se reúnen los títulos disponibles en la caché del catálogo.
2. Se excluyen los que ya están en la colección del perfil activo.
3. Se priorizan los géneros de tus series: las favoritas tienen más peso, seguidas por las que estás viendo.
4. Inicio muestra hasta cuatro sugerencias; **Ver más** abre `#/recomendaciones`, con hasta 60 resultados en tandas de 12.

No es un sistema de IA ni utiliza todavía tus puntuaciones para calcular afinidad. Si la instalación es nueva y no hay búsquedas guardadas, explora primero algunos títulos para alimentar las sugerencias. Las portadas siguen dependiendo de su proveedor externo.

## 🧩 Estructura del proyecto

```text
Reviews/
├── frontend/
│   ├── public/                # Logo, fondos y recursos estáticos
│   ├── src/
│   │   ├── assets/styles/     # Estilos organizados por módulo y tema
│   │   ├── components/        # Navegación, formularios, tarjetas y diálogos
│   │   ├── composables/       # Estado, navegación, perfiles y puntuaciones
│   │   ├── services/          # Cliente HTTP y acceso al catálogo
│   │   ├── types/             # Tipos compartidos de TypeScript
│   │   └── views/             # Inicio, colección, ranking y demás páginas
│   └── tooling/               # Integración de Vite con la API Python
├── backend/
│   ├── app/                   # API, validaciones y acceso a SQLite
│   │   ├── catalog.py         # Catálogos y caché
│   │   ├── anime_catalog.py   # Integración con Jikan
│   │   ├── recommendations.py # Afinidad por géneros
│   │   ├── episodes.py        # Capítulos y valoraciones
│   │   ├── repository.py      # Colecciones, perfiles y preferencias
│   │   └── routes.py          # Rutas HTTP
│   ├── tests/                 # Pruebas del backend
│   ├── requirements.txt
│   └── run.py
└── README.md
```

El frontend usa navegación por **hash**, implementada en `useNavigation.ts`. No requiere configurar reescrituras del servidor ni incorpora Vue Router.

| Ruta | Destino |
| --- | --- |
| `#/inicio` | Dashboard |
| `#/coleccion` | Biblioteca con filtros en la URL |
| `#/ranking` | Ranking |
| `#/configuracion` | Apariencia y perfiles |
| `#/series/{id}` | Capítulos de una serie |
| `#/recomendaciones` | Sugerencias ampliadas |

Los enlaces anteriores a estados de seguimiento redirigen a Colección con el filtro equivalente. `#/perfiles` lleva a Configuración, `#/calendario` a Inicio y `#/explorar` a Colección.

## 💾 Datos y respaldos

La aplicación usa el siguiente archivo SQLite:

- **Instalación existente:** `frontend/data/club.sqlite`, si ya existe.
- **Instalación nueva:** `backend/data/club.sqlite`.
- **Ruta personalizada:** variable de entorno `CLUB_DB`.

Para hacer una copia de seguridad completa, **detén la aplicación y copia el archivo SQLite activo**. Incluye colecciones, perfiles, avatares, puntuaciones y caché del catálogo.

Configuración también permite exportar los datos disponibles del club en JSON. Esa exportación no sustituye una copia completa de SQLite.

La biblioteca y las puntuaciones se almacenan localmente. La aplicación está pensada para uso local; no incluye autenticación de usuarios ni una configuración de despliegue público.

## 🛠️ Desarrollo y comprobaciones

Desde la raíz:

```powershell
# Pruebas del backend con el entorno virtual del proyecto
npm --prefix backend test

# Comprobación TypeScript y compilación del frontend
npm --prefix frontend run build

# Solo comprobación de tipos
npm --prefix frontend run type-check
```

La compilación genera `frontend/dist`; no inicia el servidor.

Con la API en ejecución:

- Estado: `http://127.0.0.1:8000/api/health`
- Documentación interactiva: `http://127.0.0.1:8000/docs`

## 🧯 Solución de problemas

| Problema | Qué revisar |
| --- | --- |
| **Falta `backend/.venv`** | Ejecuta los pasos de preparación de Python y la instalación de dependencias. |
| **Puerto 8000 ocupado / API antigua** | Detén la instancia anterior desde su terminal y vuelve a ejecutar `npm --prefix frontend run dev`. |
| **La API no está disponible** | Revisa el error de Python en la terminal y comprueba que instalaste `backend/requirements.txt`. |
| **Error 502 o 503 al buscar anime** | Puede ser un timeout, indisponibilidad o límite del proveedor. Espera y reintenta; también puedes agregar una serie manualmente. |
| **Recomendaciones vacías** | Realiza búsquedas en el catálogo. Las sugerencias necesitan títulos guardados que aún no estén en tu colección. |
| **Faltan portadas o próximos capítulos** | Las portadas requieren conexión y las próximas fechas dependen de los capítulos importados y los datos del proveedor. |
| **No se conserva el color elegido** | Pulsa Guardar configuración; la vista previa por sí sola no guarda el cambio. |

---

<div align="center">

**Puntuador-inador** · Tu siguiente capítulo empieza aquí.

</div>
