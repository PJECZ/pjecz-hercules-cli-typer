---
name: nuevo-comando
description: Elabora un nuevo comando Typer con el subcomando `consultar` a partir de un modelo SQLAlchemy existente en models/, siguiendo el patrón de los comandos ya listos (roles, usuarios, autoridades, usuarios-roles). Úsalo cuando se pida crear el comando de una tabla que ya tiene modelo.
argument-hint: <nombre_del_modelo_o_tabla>
allowed-tools: Read, Glob, Grep, Edit, Write, AskUserQuestion, Bash(ls:*), Bash(cat:*), Bash(uv run:*)
---

# /nuevo-comando — Comando `consultar` a partir de un modelo

## Contexto de la sesión

Modelos disponibles:
!`ls src/pjecz_hercules_cli_typer/models/`

Comandos existentes (tamaño en bytes; los de pocos bytes son stubs vacíos):
!`ls -l src/pjecz_hercules_cli_typer/commands/ | awk '{print $5, $9}'`

Registro actual en main.py:
!`grep -n "add_typer" src/pjecz_hercules_cli_typer/main.py`

---

Tu trabajo es crear `commands/<tabla>.py` con un subcomando `consultar` a partir del modelo `models/<tabla>.py`, y registrarlo en `main.py`. El código, los docstrings, los comentarios y los nombres de opciones van **en español**. Responde en el idioma del usuario.

El argumento recibido es: `$ARGUMENTS`

## Reglas obligatorias del subcomando `consultar`

1. **Parámetros**: siempre `offset: int = 0` y `limit: int = 25` primero; después los filtros opcionales, todos con valor por defecto `None` (`str | None = None`, `int | None = None`, ...).
2. **Validación**: todo filtro de texto proporcionado se sanea con una función de `core/safe_string.py` **antes** de usarse, y sólo se agrega a `where_clauses` si el resultado no es vacío (`if valor:`; nunca `if valor is not None:` porque las funciones devuelven `""`).
3. **Salida**: siempre una `rich.table.Table` mostrada con `Console().print(tabla)`. Nunca `print()` ni `typer.echo()` para los resultados.
4. **Sólo lectura**: el subcomando no modifica la base de datos.

## Fase 1 — Identificar el modelo

- Si `$ARGUMENTS` está vacío, muestra los modelos disponibles (arriba) y pregunta cuál usar. Detente.
- Acepta el nombre del archivo (`edictos`), de la tabla o de la clase (`Edicto`). Ojo: el nombre del archivo del modelo puede diferir del comando (p. ej. `models/materias_tipos_juicios.py` vs `commands/materias_tipos_de_juicios.py`).
- Si `commands/<tabla>.py` ya existe y **no** es un stub (sólo tiene el docstring), avisa y pregunta si se reemplaza. Si es un stub, se sobreescribe.

## Fase 2 — Analizar el modelo y los comandos de referencia

1. Lee el modelo completo. Anota: nombre de la clase, columnas con su tipo y longitud, claves foráneas y relaciones (`# Claves foráneas`, `# Hijos`).
2. Lee los comandos de referencia para copiar el estilo exacto:
   - `commands/roles.py` — tabla simple sin joins.
   - `commands/usuarios.py` y `commands/autoridades.py` — joins con condición explícita y filtros por clave de la tabla padre.
   - `commands/usuarios_roles.py` y `commands/permisos.py` — tablas de unión; `permisos.py` también muestra un filtro entero validado.
3. Lee `templates/consultar.py.tmpl` (en el directorio de este skill): es el esqueleto a completar.

## Fase 3 — Proponer el diseño (y esperar confirmación)

Presenta al usuario, en una lista breve:

- **Columnas de la tabla de salida**: las columnas útiles del modelo (omite `id`, las columnas de auditoría `creado`/`modificado`/`estatus`, y columnas largas como `url`, `archivo` o directorios salvo que tengan sentido), más la clave o nombre de cada padre (p. ej. `Autoridad.clave` como "Autoridad").
- **Filtros opcionales** y la función de saneamiento de cada uno, según esta tabla:

| Tipo de columna                                   | Función                                        | Comparación                  |
| ------------------------------------------------- | ---------------------------------------------- | ---------------------------- |
| Clave (`clave`, `<padre>_clave`)                  | `safe_clave(valor)`                            | `==`                         |
| Email                                             | `safe_email(valor, search_fragment=True)`      | `.like("%" + valor + "%")`   |
| Texto con nombres propios/descripciones (con ñ)   | `safe_string(valor, save_enie=True)`           | `.like("%" + valor + "%")`   |
| Texto en mayúsculas sin ñ (CURP, RFC, expediente) | `safe_string(valor)`                           | `.like("%" + valor + "%")`   |
| Entero con dominio acotado                        | función `safe_<campo>` local (ver permisos) | `==`                         |
| Fecha (`date`)                                    | parámetros `<campo>_desde` / `<campo>_hasta` de tipo `str \| None`, convertidos con `date.fromisoformat` dentro de `try/except ValueError` que hace `raise Exit(1)` | `>=` / `<=` |

  Las columnas con `unique=True` (como `clave`) se filtran con `==`. Recuerda que `safe_string` convierte a mayúsculas por defecto; si la columna guarda minúsculas, pasa `to_uppercase=False`.

- **Joins** necesarios para los filtros/columnas de tablas padre, con condición explícita (`.join(Padre, Modelo.padre_id == Padre.id)`), y su cláusula `Padre.estatus == "A"`.
- **Orden** (`order_by`): la columna natural de búsqueda (clave, nombre, email; en tablas con fecha, `Modelo.fecha.desc()`).
- **Nombre del sub-comando en main.py**: el nombre de la tabla con guiones (`listas_de_acuerdos` → `listas-de-acuerdos`).

Si hay alguna decisión dudosa (qué columnas mostrar, qué filtros incluir), pregunta con `AskUserQuestion`. No escribas código hasta que el usuario confirme el diseño.

## Fase 4 — Implementar

1. Escribe `commands/<tabla>.py` a partir de `templates/consultar.py.tmpl`, respetando:
   - Docstring del módulo con el nombre legible de la tabla; `app = Typer(help="<Nombre>")`.
   - Imports ordenados al estilo isort (perfil black): stdlib, terceros (`rich`, `sqlalchemy`, `typer`), luego `pjecz_hercules_cli_typer.*` en orden alfabético; importa sólo las funciones de `safe_string` que uses.
   - Comentarios de sección exactos: `# Preparar tabla`, `# Cláusulas where`, `# Sentencia`, `# Consultar, agregar a la tabla y mostrar`.
   - Columnas con `header_style="green"`; `no_wrap=True` en claves y emails.
   - `select(...)` de columnas específicas (nunca la entidad completa), con `.label("<padre>_<columna>")` para las de tablas padre.
   - `tabla.add_row(...)` recibe sólo cadenas: convierte enteros con `str(...)`, fechas con `.strftime("%Y-%m-%d")`, booleanos como `"Sí"`/`"No"`, y `None` como `""`.
   - Líneas de máximo 128 caracteres.
2. **Relaciones del modelo**: SQLAlchemy necesita que todas las clases mencionadas en `relationship(...)` estén importadas antes de configurar los mappers. Para eso `models/__init__.py` importa todos los modelos; verifica que el modelo de la tabla (y cualquier modelo que éste referencie) esté ahí, y si falta agrégalo en orden alfabético, tanto en los imports como en `__all__`.
3. Registra el comando en `main.py`: agrega `from pjecz_hercules_cli_typer.commands.<tabla> import app as <tabla>_app` y `app.add_typer(<tabla>_app, name="<tabla-con-guiones>")`, ambos en orden alfabético con los existentes.

## Fase 5 — Verificar

1. Ejecuta `uv run src/pjecz_hercules_cli_typer/main.py <tabla-con-guiones> consultar --help` y confirma que aparecen `--offset`, `--limit` y todos los filtros.
2. Si hay conexión a la base de datos (`.env` presente), ejecuta `uv run src/pjecz_hercules_cli_typer/main.py <tabla-con-guiones> consultar --limit 5` y un ejemplo con al menos un filtro. Si falla por conexión, repórtalo tal cual; si falla por mappers (`InvalidRequestError ... failed to locate a name`), corrige `models/__init__.py` según el paso 4.2.
3. Resume al usuario: archivo creado, filtros con su función de saneamiento, y un ejemplo de uso. No hagas commit salvo que el usuario lo pida.
