# Publicar Puntuador-inador

El proyecto está preparado para **un servicio Python en Render**, con Vue compilado servido por FastAPI y SQLite en un disco persistente. No necesitas instalar Docker. El repositorio incluye `render.yaml`; todavía debes conectar tu cuenta y desplegarlo.

## 1. Antes de subirlo

- Crea un repositorio **privado** y sube el código, `frontend/package-lock.json`, `backend/requirements.txt` y `render.yaml`.
- El `.gitignore` excluye bases de datos, contraseñas, dependencias y copias de seguridad. No publiques tu SQLite ni un archivo `.env` con claves reales.
- Guarda una copia de los datos actuales. Desde la raíz, con el entorno Python instalado:

```powershell
.\backend\.venv\Scripts\python.exe backend/scripts/storage.py backup backups/club-export.sqlite
```

Este comando usa el mecanismo de respaldo de SQLite y no sobrescribe archivos existentes. La copia incluye todos los perfiles, avatares, puntuaciones y, si ya habilitaste cuentas, credenciales cifradas mediante hash y sesiones. Trátala como un archivo privado.

## 2. Crear el servicio

1. En Render conecta el repositorio y crea un **Blueprint** desde `render.yaml`.
2. Revisa el costo antes de confirmar: la configuración propone un servicio **Starter** y un disco persistente de **1 GB**. No uses un servicio gratuito sin disco para guardar SQLite.
3. Configura los secretos solicitados:
   - `ADMIN_USERNAME`: de 3 a 60 letras, números, punto, guion o guion bajo.
   - `ADMIN_PASSWORD`: contraseña única de 12 a 128 caracteres.
4. Ejecuta el despliegue. Render instalará Python y npm, compilará Vue e iniciará FastAPI.
5. Abre la URL HTTPS que entregue Render e inicia sesión con la cuenta administradora.

La primera inicialización crea el administrador y le asigna todos los perfiles preexistentes. Los secretos de bootstrap **no restablecen la contraseña en los siguientes arranques**. Puedes retirar `ADMIN_PASSWORD` del panel después de comprobar el acceso; tendrás que volver a configurarla si comienzas con una base vacía.

La API no arranca con autenticación habilitada si la base está vacía y faltan las credenciales iniciales. Una base que ya contiene cuentas sigue exigiendo acceso aunque se retire `AUTH_ENABLED`.

### Valores incluidos

| Variable | Valor / función |
| --- | --- |
| `APP_ENV` | `production`; activa acceso protegido, cookies Secure y frontend compilado. |
| `CLUB_DB` | `/var/data/club.sqlite`; siempre dentro del disco persistente. |
| `PORT` | Lo proporciona Render. |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | Solo bootstrap de la primera cuenta. |
| `PUBLIC_ORIGIN` | Opcional; URL HTTPS pública sin barra final para otro proxy o dominio personalizado. En Render se utiliza también `RENDER_EXTERNAL_URL`. |
| `FRONTEND_DIST` | Opcional; la ruta predeterminada es `frontend/dist`. |

El servicio usa **un worker y una instancia**. No aumentes réplicas con archivos SQLite independientes. Las rutas de la interfaz usan `#/`, por lo que no requieren reglas especiales para recargar páginas.

## 3. Trasladar tus datos actuales

Hazlo **antes de invitar amigos o empezar a guardar datos en la web**: restaurar reemplaza el estado del servidor, no fusiona bases.

1. Genera el respaldo local con el comando anterior.
2. Transfiérelo de forma privada al disco del servicio, por ejemplo a `/var/data/club-import.sqlite`, mediante el acceso SSH/SCP indicado en el panel de Render. Usa la dirección exacta que te proporcione el servicio; no subas la base a GitHub ni a `frontend/public`.
3. Prepara un reinicio controlado. Para que la restauración ocurra antes de levantar la API, puedes usar temporalmente este **Start Command**:

```bash
cd backend && if [ ! -f /var/data/import-complete ]; then python scripts/storage.py restore /var/data/club-import.sqlite --confirm-offline && touch /var/data/import-complete || exit 1; fi; python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 1 --proxy-headers
```

4. Reinicia/despliega el servicio. Con disco persistente, Render detiene la instancia anterior antes de iniciar la nueva. **No ejecutes la restauración desde una shell mientras la API esté atendiendo solicitudes.**
5. Verifica perfiles y puntuaciones. Si la base importada era local y no tenía cuentas, se asociará al administrador creado con los secretos del paso 2.
6. Restablece el Start Command original de `render.yaml`. Conserva una copia privada del respaldo fuera del servidor; elimina el archivo de importación cuando ya no lo necesites.

El script comprueba integridad y tablas, guarda una copia de la base anterior y reemplaza el archivo mediante una copia temporal. El marcador evita repetir la importación en cada reinicio. No borres ese marcador para repetirla sin revisar antes los datos que vas a reemplazar.

## 4. Invitar a tus amigos

En **Configuración → Tu cuenta → Invitar a un amigo**, crea un enlace y compártelo tú con el destinatario.

- La invitación sirve una sola vez y vence en siete días.
- El amigo elige usuario y contraseña; se crea un perfil vacío propio.
- Cada cuenta solo puede consultar, editar o borrar sus propios perfiles y colecciones.
- Las preferencias se guardan por cuenta. El catálogo y sus metadatos se comparten internamente.
- Los perfiles históricos importados permanecen en tu cuenta administradora; no se transfieren automáticamente a los invitados.
- No hay registro público ni envío de correos.

Las sesiones usan cookies HttpOnly, Secure en producción y SameSite=Lax. Las contraseñas se almacenan con scrypt y sal aleatoria. Las invitaciones y los tokens de sesión se almacenan como hashes. Las acciones requieren una cabecera de la aplicación y se valida el origen. Hay límites de intentos de acceso.

## 5. Respaldos y recuperación

En una terminal del servidor, desde `backend`:

```bash
python scripts/storage.py backup /var/data/backup-fecha.sqlite
```

Descarga copias fuera del servicio periódicamente. El proyecto incluye el comando; **no crea todavía respaldos programados**. No guardes una única copia en el mismo disco que quieres proteger.

Para recuperar una cuenta si olvidaste la contraseña:

```bash
python scripts/reset_password.py
```

Introduce el usuario y la contraseña nueva cuando se soliciten. La contraseña no aparece en pantalla ni se pasa como argumento del comando; se invalidan las sesiones de esa cuenta. No hay recuperación automática por correo.

Los usuarios pueden cambiar su propia contraseña desde Configuración; ese cambio cierra sus otras sesiones.

## 6. Comprobar antes de compartir

- Entrar y cerrar sesión; comprobar que no aparece la colección antes de entrar.
- Crear una invitación, registrarse desde una ventana privada y comprobar que empieza con una colección vacía.
- Agregar una serie, puntuar un capítulo y volver a entrar para verificar persistencia.
- Confirmar que cambiar de cuenta no permite ver perfiles de otra persona.
- Reiniciar el servicio y comprobar que los datos siguen presentes.
- Revisar `/api/health`. La documentación interactiva `/docs` está deshabilitada en producción.

Las pruebas locales de API usan bases temporales y `TestClient`, sin iniciar un servidor en segundo plano. La disponibilidad real de TVmaze/Jikan y el resultado del despliegue en Render deben comprobarse una vez publicado.

## Desarrollo local

Sin cuentas en la base y sin `AUTH_ENABLED=1`, `npm --prefix frontend run dev` conserva el flujo local de perfiles. Para probar cuentas localmente, establece `AUTH_ENABLED=1`, `ADMIN_USERNAME` y `ADMIN_PASSWORD` en tu terminal y usa preferiblemente `CLUB_DB` apuntando a una base de pruebas. `APP_ENV=production` necesita HTTPS para que funcionen las cookies Secure; no lo uses para probar login por HTTP local.

Los archivos `.env` no se cargan automáticamente. Usa variables del sistema/terminal o el panel del proveedor.

## Referencias del proveedor

- [Render Blueprints](https://render.com/docs/blueprint-spec)
- [Discos persistentes y transferencias](https://render.com/docs/disks)
- [Variables de entorno](https://render.com/docs/configure-environment-variables)
- [Runtimes nativos](https://render.com/docs/native-runtimes)

Este documento describe la preparación del proyecto. No se han creado servicios, contratado planes ni publicado datos.
