# SPEC 01 — Comandos consultar para los modelos sin comando

> **Estado:** Aprobado
> **Depende de:** —
> **Fecha:** 2026-10-21
> **Objetivo:** Crear el subcomando `consultar` de las tablas que ya tienen modelo pero no comando, con filtros revisados tabla por tabla.

---

## Por qué existe este spec

Los modelos ya están en `models/`, encontrarás que varias tablas ya tienen comando.
Cada comando nuevo se genera con el skill `nuevo-comando`, que decide columnas y filtros caso por caso.
Este spec fija de antemano los parámetros de cada comando para revisarlos, quitar los poco útiles y agregar los que falten antes de implementar.

---

## Alcance

**Dentro:**

- Cuatro funciones nuevas en `core/validations.py`: `safe_opcion`, `safe_opcion_int`, `safe_id` y `safe_uuid`.
- Archivos nuevos `commands/<modelo>.py`, cada uno con el subcomando `consultar`.
- Registro de los 29 comandos en `main.py`, en orden alfabético.
- Mostrar la columna "ID" en las tablas padre que no tienen columna única (`arc-documentos`, `arc-remesas`, `exh-exhortos`), para poder filtrar a sus hijos.

**Fuera de alcance (para specs futuros):**

- Subcomando `exportar` (SPEC 02). Ya decidido: CSV con el módulo `csv` de la biblioteca estándar, archivo en `exports/`, mismos filtros que `consultar` y sin `offset`/`limit`.
- Subcomandos de detalle, alta, edición o borrado.
- Cambios a los comandos existentes (salvo `main.py`).
- Cambios a los modelos o al esquema de la base de datos.
- Los stubs vacíos ya registrados.

---

## Modelo de datos

Este spec no introduce estructuras de datos nuevas; lee las tablas existentes.
Agrega cuatro validaciones a `core/validations.py`:

```python
def safe_opcion(valor: str, opciones: Container) -> str:
    """Validar que el valor sea una de las opciones del catálogo del modelo"""
    # Si no está en opciones lanza MyNotValidParamError

def safe_opcion_int(valor: int, opciones: Container) -> int:
    """Validar que el valor sea una de las opciones del catálogo del modelo"""
    # Para catálogos con claves enteras (TIPOS_DOCUMENTOS, TIPOS_PARTES); si no está en opciones lanza MyNotValidParamError

def safe_id(id_: int) -> int:
    """Validar que el id sea un entero positivo"""
    # Lanza MyNotValidParamError si id_ <= 0

def safe_uuid(texto: str) -> uuid.UUID:
    """Validar y convertir un UUID"""
    # Lanza MyNotValidParamError si no es un UUID válido
```

### Convenciones comunes a todos los comandos

- Parámetros: `offset: int = 0` y `limit: int = 25` primero; luego los filtros, todos con valor por defecto `None`.
- Validación con el patrón `if valor and (valor := safe_*(valor)):` del skill `nuevo-comando`.
- Excepciones al patrón `:=`: los filtros enteros (`anio`, `*_id`, catálogos con claves enteras) usan `if valor is not None:` porque `0` debe rechazarse, no ignorarse.
- Filtro por padre: por su columna única (`clave`, `nombre`, `email`, `edificio`) con `==`.
- Si el padre no tiene columna única, se filtra por su id con `safe_id` (entero) o `safe_uuid` (UUID).
- Columnas de catálogo (`Enum`): `safe_opcion(valor, Modelo.CATALOGO)` y `==`; si las claves del catálogo son enteras, `safe_opcion_int`.
- Fechas (`date`): `<campo>_desde` / `<campo>_hasta` con `safe_fecha`, comparación `>=` / `<=`.
- Fechas y horas (`datetime`): `<campo>_desde` con `>=`; `<campo>_hasta` con `< hasta + timedelta(days=1)` para incluir el día completo.
- Salida: `date` como `%Y-%m-%d`, `datetime` como `%Y-%m-%d %H:%M`, booleanos como `"Sí"`/`"No"`, `None` como `""`.
- Cada tabla padre unida agrega su cláusula `Padre.estatus == "A"`.
- Nombre del comando en `main.py`: nombre del archivo del modelo con guiones (`arc_documentos` → `arc-documentos`).

### Parámetros por comando

En las tablas siguientes, "Validación" indica la función de `core/validations.py`.
Tacha o agrega filas para ajustar los filtros antes de aprobar el spec.

#### Módulo Archivo

**`arc-documentos-tipos`** — orden `nombre`. Salida: Nombre.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--nombre` | `ArcDocumentoTipo.nombre` | `safe_string` | `like` |

**`arc-juzgados-extintos`** — join `Distrito`; orden `clave`. Salida: Clave, Descripción corta, Distrito.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--distrito-clave` | `Distrito.clave` | `safe_clave` | `==` |
| `--clave` | `ArcJuzgadoExtinto.clave` | `safe_clave` | `==` |
| `--descripcion-corta` | `ArcJuzgadoExtinto.descripcion_corta` | `safe_string` | `like` |

**`arc-documentos`** — joins `Autoridad`, `ArcJuzgadoExtinto`, `ArcDocumentoTipo`; orden `expediente`. Salida: ID, Autoridad, Expediente, Año, Actor, Demandado, Tipo, Juzgado origen, Tipo juzgado, Ubicación, Fojas.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--arc-juzgado-origen-clave` | `ArcJuzgadoExtinto.clave` | `safe_clave` | `==` |
| `--arc-documento-tipo-nombre` | `ArcDocumentoTipo.nombre` | `safe_string` | `==` |
| `--expediente` | `ArcDocumento.expediente` | `safe_expediente` | `==` |
| `--expediente-numero` | `ArcDocumento.expediente_numero` | `is not None` | `==` |
| `--anio` | `ArcDocumento.anio` | `is not None` | `==` |
| `--actor` | `ArcDocumento.actor` | `safe_string` | `like` |
| `--demandado` | `ArcDocumento.demandado` | `safe_string` | `like` |
| `--tipo-juzgado` | `ArcDocumento.tipo_juzgado` | `safe_opcion(TIPO_JUZGADOS)` | `==` |
| `--ubicacion` | `ArcDocumento.ubicacion` | `safe_opcion(UBICACIONES)` | `==` |

**`arc-remesas`** — joins `Autoridad`, `Usuario` (asignado), `ArcDocumentoTipo`; orden `tiempo_enviado.desc()`. Salida: ID, Autoridad, Oficio, Año, Tipo, Asignado, Enviado, Documentos, Anomalías, Estado.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--usuario-asignado-email` | `Usuario.email` | `safe_email` | `==` |
| `--arc-documento-tipo-nombre` | `ArcDocumentoTipo.nombre` | `safe_string` | `==` |
| `--num-oficio` | `ArcRemesa.num_oficio` | `safe_string` | `like` |
| `--anio` | `ArcRemesa.anio` | `safe_string` | `==` |
| `--estado` | `ArcRemesa.estado` | `safe_opcion(ESTADOS)` | `==` |
| `--tiempo-enviado-desde` / `--tiempo-enviado-hasta` | `ArcRemesa.tiempo_enviado` | `safe_fecha` | `>=` / `< +1 día` |

**`arc-remesas-documentos`** — joins `ArcRemesa`, `ArcDocumento`; orden `ArcDocumento.expediente`. Salida: Remesa ID, Documento ID, Expediente, Tipo juzgado, Fojas, Anomalía.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--arc-remesa-id` | `ArcRemesaDocumento.arc_remesa_id` | `safe_id` | `==` |
| `--arc-documento-id` | `ArcRemesaDocumento.arc_documento_id` | `safe_id` | `==` |
| `--tipo-juzgado` | `ArcRemesaDocumento.tipo_juzgado` | `safe_opcion(TIPOS)` | `==` |
| `--anomalia` | `ArcRemesaDocumento.anomalia` | `safe_opcion(ANOMALIAS)` | `==` |

#### Catálogos geográficos y oficinas

**`estados`** — orden `clave`. Salida: Clave, Nombre.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `Estado.clave` | `safe_clave` | `==` |
| `--nombre` | `Estado.nombre` | `safe_string` | `like` |

**`municipios`** — join `Estado`; orden `Estado.clave`, `Municipio.clave`. Salida: Estado, Clave, Nombre.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--estado-clave` | `Estado.clave` | `safe_clave` | `==` |
| `--clave` | `Municipio.clave` | `safe_clave` | `==` |
| `--nombre` | `Municipio.nombre` | `safe_string` | `like` |

**`domicilios`** — join `Distrito`; orden `edificio`. Salida: Edificio, Distrito, Municipio, Calle, Colonia, C.P.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--distrito-clave` | `Distrito.clave` | `safe_clave` | `==` |
| `--edificio` | `Domicilio.edificio` | `safe_string` | `like` |
| `--municipio` | `Domicilio.municipio` | `safe_string` | `like` |

**`oficinas`** — joins `Distrito`, `Domicilio`; orden `clave`. Salida: Clave, Descripción corta, Distrito, Edificio, Jurisdiccional.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--distrito-clave` | `Distrito.clave` | `safe_clave` | `==` |
| `--domicilio-edificio` | `Domicilio.edificio` | `safe_string` | `==` |
| `--clave` | `Oficina.clave` | `safe_clave(max_len=32)` | `==` |
| `--descripcion` | `Oficina.descripcion` | `safe_string` | `like` |
| `--descripcion-corta` | `Oficina.descripcion_corta` | `safe_string` | `like` |
| `--es-jurisdiccional / --no-es-jurisdiccional` | `Oficina.es_jurisdiccional` | `is not None` | `==` |

#### Funcionarios y soportes

**`funcionarios`** — orden `apellido_paterno`, `apellido_materno`, `nombres`. Salida: Nombres, Apellido paterno, Apellido materno, CURP, Email, Puesto, En funciones, En soportes.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--nombres` | `Funcionario.nombres` | `safe_string` | `like` |
| `--apellido-paterno` | `Funcionario.apellido_paterno` | `safe_string` | `like` |
| `--apellido-materno` | `Funcionario.apellido_materno` | `safe_string` | `like` |
| `--curp` | `Funcionario.curp` | `safe_curp` | `==` |
| `--email` | `Funcionario.email` | `safe_email` | `==` |
| `--puesto` | `Funcionario.puesto` | `safe_string` | `like` |
| `--en-funciones / --no-en-funciones` | `Funcionario.en_funciones` | `is not None` | `==` |
| `--en-soportes / --no-en-soportes` | `Funcionario.en_soportes` | `is not None` | `==` |

**`funcionarios-oficinas`** — joins `Funcionario`, `Oficina`; orden `Funcionario.email`, `Oficina.clave`. Salida: Funcionario email, Oficina, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--funcionario-curp` | `Funcionario.curp` | `safe_curp` | `==` |
| `--funcionario-email` | `Funcionario.email` | `safe_email` | `==` |
| `--oficina-clave` | `Oficina.clave` | `safe_clave(max_len=32)` | `==` |

**`soportes-categorias`** — orden `nombre`. Salida: Nombre, Departamento.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--nombre` | `SoporteCategoria.nombre` | `safe_string` | `like` |
| `--departamento` | `SoporteCategoria.departamento` | `safe_opcion(DEPARTAMENTOS)` | `==` |

**`soportes-tickets`** — joins `Funcionario`, `SoporteCategoria`, `Usuario`; orden `SoporteTicket.id.desc()`. Salida: ID, Creado, Usuario, Categoría, Funcionario, Departamento, Estado, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--usuario-email` | `Usuario.email` | `safe_email` | `==` |
| `--funcionario-curp` | `Funcionario.curp` | `safe_curp` | `==` |
| `--funcionario-email` | `Funcionario.email` | `safe_email` | `==` |
| `--soporte-categoria-nombre` | `SoporteCategoria.nombre` | `safe_string` | `==` |
| `--departamento` | `SoporteTicket.departamento` | `safe_opcion(DEPARTAMENTOS)` | `==` |
| `--estado` | `SoporteTicket.estado` | `safe_opcion(ESTADOS)` | `==` |
| `--descripcion` | `SoporteTicket.descripcion` | `safe_string` | `like` |
| `--creado-desde` / `--creado-hasta` | `SoporteTicket.creado` | `safe_fecha` | `>=` / `< +1 día` |

#### Módulo Digitalización

**`dgt-depositos`** — orden `clave`. Salida: Clave, Descripción, Propósito.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `DgtDepositos.clave` | `safe_clave(max_len=64)` | `==` |
| `--descripcion` | `DgtDepositos.descripcion` | `safe_string` | `like` |
| `--proposito` | `DgtDepositos.proposito` | `safe_opcion(PROPOSITOS)` | `==` |

**`dgt-tipos`** — orden `clave`. Salida: Clave, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `DgtTipo.clave` | `safe_clave(max_len=64)` | `==` |
| `--descripcion` | `DgtTipo.descripcion` | `safe_string` | `like` |

**`dgt-rutas`** — joins `DgtDepositos`, `DgtTipo`; orden `clave`. Salida: Clave, Depósito, Tipo, Autoridad clave, Directorio.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--dgt-deposito-clave` | `DgtDepositos.clave` | `safe_clave(max_len=64)` | `==` |
| `--dgt-tipo-clave` | `DgtTipo.clave` | `safe_clave(max_len=64)` | `==` |
| `--clave` | `DgtRuta.clave` | `safe_clave(max_len=64)` | `==` |
| `--autoridad-clave` | `DgtRuta.autoridad_clave` | `safe_clave` | `==` |

**`dgt-plataformas`** — orden `clave`. Salida: Clave, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `DgtPlataforma.clave` | `safe_clave(max_len=64)` | `==` |
| `--descripcion` | `DgtPlataforma.descripcion` | `safe_string` | `like` |

**`dgt-plataformas-autoridades`** — joins `Autoridad`, `DgtPlataforma`; orden `Autoridad.clave`. Salida: Autoridad, Plataforma.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--dgt-plataforma-clave` | `DgtPlataforma.clave` | `safe_clave(max_len=64)` | `==` |

**`dgt-plataformas-endpoints`** — join `DgtPlataforma`; orden `DgtPlataforma.clave`, `ruta`. Salida: Plataforma, Propósito, Método, Ruta, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--dgt-plataforma-clave` | `DgtPlataforma.clave` | `safe_clave(max_len=64)` | `==` |
| `--proposito` | `DgtPlataformaEndpoint.proposito` | `safe_opcion(PROPOSITOS)` | `==` |
| `--metodo` | `DgtPlataformaEndpoint.metodo` | `safe_opcion(METODOS)` | `==` |

**`dgt-digitalizaciones`** — joins `Autoridad`, `DgtRuta`; orden `ultimo_evento_creado.desc()`. Salida: Autoridad, Ruta, Expediente, Archivo, Último evento, Fecha evento, Anómalo, Entregado.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--dgt-ruta-clave` | `DgtRuta.clave` | `safe_clave(max_len=64)` | `==` |
| `--expediente` | `DgtDigitalizacion.expediente` | `safe_expediente` | `==` |
| `--archivo-nombre` | `DgtDigitalizacion.archivo_nombre` | `safe_string` | `like` |
| `--ultimo-evento` | `DgtDigitalizacion.ultimo_evento` | `safe_string` | `==` |
| `--es-anomalo / --no-es-anomalo` | `DgtDigitalizacion.es_anomalo` | `is not None` | `==` |
| `--ultimo-evento-creado-desde` / `--ultimo-evento-creado-hasta` | `DgtDigitalizacion.ultimo_evento_creado` | `safe_fecha` | `>=` / `< +1 día` |

**`dgt-entregas`** — joins `Autoridad`, `DgtRuta`; orden `ultimo_evento_creado.desc()`. Salida: Autoridad, Ruta, Expediente, Archivo, Último evento, Fecha evento, Anómalo.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--dgt-ruta-clave` | `DgtRuta.clave` | `safe_clave(max_len=64)` | `==` |
| `--expediente` | `DgtEntrega.expediente` | `safe_expediente` | `==` |
| `--archivo-nombre` | `DgtEntrega.archivo_nombre` | `safe_string` | `like` |
| `--ultimo-evento` | `DgtEntrega.ultimo_evento` | `safe_string` | `==` |
| `--es-anomalo / --no-es-anomalo` | `DgtEntrega.es_anomalo` | `is not None` | `==` |
| `--ultimo-evento-creado-desde` / `--ultimo-evento-creado-hasta` | `DgtEntrega.ultimo_evento_creado` | `safe_fecha` | `>=` / `< +1 día` |

#### Módulo Exhortos

**`exh-areas`** — orden `clave`. Salida: Clave, Nombre.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `ExhArea.clave` | `safe_clave` | `==` |
| `--nombre` | `ExhArea.nombre` | `safe_string` | `like` |

**`exh-tipos-diligencias`** — orden `clave`. Salida: Clave, Descripción.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--clave` | `ExhTipoDiligencia.clave` | `safe_clave` | `==` |
| `--descripcion` | `ExhTipoDiligencia.descripcion` | `safe_string` | `like` |

**`exh-exhortos`** — joins `Autoridad`, `ExhArea`, `ExhTipoDiligencia`; orden `ExhExhorto.id.desc()`. Salida: ID, Autoridad, Área, Tipo diligencia, Exhorto origen ID, Expediente origen, Juzgado origen, Materia, Remitente, Estado.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--exh-area-clave` | `ExhArea.clave` | `safe_clave` | `==` |
| `--exh-tipo-diligencia-clave` | `ExhTipoDiligencia.clave` | `safe_clave` | `==` |
| `--exhorto-origen-id` | `func.upper(ExhExhorto.exhorto_origen_id)` | `safe_string(max_len=64)` | `==` |
| `--numero-expediente-origen` | `ExhExhorto.numero_expediente_origen` | `safe_string` | `like` |
| `--juzgado-origen-nombre` | `ExhExhorto.juzgado_origen_nombre` | `safe_string` | `like` |
| `--materia-clave` | `ExhExhorto.materia_clave` | `safe_clave(max_len=32)` | `==` |
| `--remitente` | `ExhExhorto.remitente` | `safe_opcion(REMITENTES)` | `==` |
| `--estado` | `ExhExhorto.estado` | `safe_opcion(ESTADOS)` | `==` |

**`exh-exhortos-archivos`** — join `ExhExhorto`; orden `fecha_hora_recepcion.desc()`. Salida: Exhorto ID, Nombre archivo, Tipo documento, Tamaño, Recepción, Estado.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--exh-exhorto-id` | `ExhExhortoArchivo.exh_exhorto_id` | `safe_id` | `==` |
| `--nombre-archivo` | `ExhExhortoArchivo.nombre_archivo` | `safe_string` | `like` |
| `--tipo-documento` | `ExhExhortoArchivo.tipo_documento` | `safe_opcion_int(TIPOS_DOCUMENTOS)` | `==` |
| `--estado` | `ExhExhortoArchivo.estado` | `safe_opcion(ESTADOS)` | `==` |

**`exh-exhortos-partes`** — join `ExhExhorto`; orden `ExhExhortoParte.exh_exhorto_id`, `nombre`. Salida: Exhorto ID, Nombre, Apellido paterno, Apellido materno, Género, Persona moral, Tipo parte.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--exh-exhorto-id` | `ExhExhortoParte.exh_exhorto_id` | `safe_id` | `==` |
| `--nombre` | `ExhExhortoParte.nombre` | `safe_string` | `like` |
| `--apellido-paterno` | `ExhExhortoParte.apellido_paterno` | `safe_string` | `like` |
| `--apellido-materno` | `ExhExhortoParte.apellido_materno` | `safe_string` | `like` |
| `--tipo-parte` | `ExhExhortoParte.tipo_parte` | `safe_opcion_int(TIPOS_PARTES)` | `==` |

#### Módulo Oficios

**`ofi-documentos-adjuntos`** — join `OfiDocumento`; orden `descripcion`. Salida: Oficio ID, Descripción, Archivo.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--ofi-documento-id` | `OfiDocumentoAdjunto.ofi_documento_id` | `safe_uuid` | `==` |
| `--descripcion` | `OfiDocumentoAdjunto.descripcion` | `safe_string` | `like` |

#### Otros

**`redams`** — join `Autoridad`; orden `fecha.desc()`. Salida: Fecha, Autoridad, Expediente, Nombre.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--autoridad-clave` | `Autoridad.clave` | `safe_clave` | `==` |
| `--nombre` | `Redam.nombre` | `safe_string` | `like` |
| `--expediente` | `Redam.expediente` | `safe_string` | `like` |
| `--fecha-desde` / `--fecha-hasta` | `Redam.fecha` | `safe_fecha` | `>=` / `<=` |

**`repsvm-agresores`** — join `Distrito`; orden `Distrito.clave`, `consecutivo`. Salida: Distrito, Consecutivo, Nombre, Número causa, Delito genérico, Tipo juzgado, Tipo sentencia, Público.

| Opción CLI | Columna | Validación | Comparación |
| ---------- | ------- | ---------- | ----------- |
| `--distrito-clave` | `Distrito.clave` | `safe_clave` | `==` |
| `--nombre` | `RepsvmAgresor.nombre` | `safe_string` | `like` |
| `--numero-causa` | `RepsvmAgresor.numero_causa` | `safe_string` | `like` |
| `--delito-generico` | `RepsvmAgresor.delito_generico` | `safe_string` | `like` |
| `--tipo-juzgado` | `RepsvmAgresor.tipo_juzgado` | `safe_opcion(TIPOS_JUZGADOS)` | `==` |
| `--tipo-sentencia` | `RepsvmAgresor.tipo_sentencia` | `safe_opcion(TIPOS_SENTENCIAS)` | `==` |
| `--es-publico / --no-es-publico` | `RepsvmAgresor.es_publico` | `is not None` | `==` |

---

## Plan de implementación

Cada comando se crea con el skill `nuevo-comando`, usando la tabla de parámetros de este spec como diseño ya confirmado (se omite su Fase 3).
Cada paso termina registrando sus comandos en `main.py` y ejecutando `--help` de cada uno.

1. Agregar `safe_opcion`, `safe_id` y `safe_uuid` a `core/validations.py`. Prueba manual: importarlas con `uv run python -c` y validar un valor bueno y uno malo de cada una.
2. Módulo Archivo: `arc-documentos-tipos`, `arc-juzgados-extintos`, `arc-documentos`, `arc-remesas`, `arc-remesas-documentos`.
3. Catálogos geográficos y oficinas: `estados`, `municipios`, `domicilios`, `oficinas`.
4. Funcionarios y soportes: `funcionarios`, `funcionarios-oficinas`, `soportes-categorias`, `soportes-tickets`.
5. Digitalización (catálogos): `dgt-depositos`, `dgt-tipos`, `dgt-rutas`, `dgt-plataformas`.
6. Digitalización (registros): `dgt-plataformas-autoridades`, `dgt-plataformas-endpoints`, `dgt-digitalizaciones`, `dgt-entregas`.
7. Módulo Exhortos: `exh-areas`, `exh-tipos-diligencias`, `exh-exhortos`, `exh-exhortos-archivos`, `exh-exhortos-partes`.
8. Módulo Oficios: `ofi-documentos-adjuntos`.
9. Otros: `redams`, `repsvm-agresores`.

---

## Criterios de aceptación

- [ ] `core/validations.py` define `safe_opcion`, `safe_opcion_int`, `safe_id` y `safe_uuid`, y cada una lanza `MyNotValidParamError` con un valor inválido.
- [ ] Existen los 29 archivos `commands/<modelo>.py` listados en el plan.
- [ ] `main.py` registra los 29 comandos con su nombre con guiones, en orden alfabético.
- [ ] `uv run src/pjecz_hercules_cli_typer/main.py <comando> consultar --help` muestra `--offset`, `--limit` y exactamente los filtros de su tabla en este spec, para los 29 comandos.
- [ ] Con conexión a la base de datos, `<comando> consultar --limit 5` termina sin error y muestra una tabla `rich` en los 29 comandos.
- [ ] `arc-documentos consultar`, `arc-remesas consultar` y `exh-exhortos consultar` muestran la columna "ID".
- [ ] `exh-exhortos-partes consultar --exh-exhorto-id 0` termina con código 1 y un mensaje en rojo, sin traceback.
- [ ] `ofi-documentos-adjuntos consultar --ofi-documento-id abc` termina con código 1 y un mensaje en rojo, sin traceback.
- [ ] `exh-exhortos consultar --estado INEXISTENTE` termina con código 1 y un mensaje en rojo, sin traceback.
- [ ] `soportes-tickets consultar --creado-hasta <hoy>` incluye los tickets creados hoy.
- [ ] Ningún subcomando nuevo modifica la base de datos (sólo usa `select`).
- [ ] `ruff check` y `black --check` pasan sin errores en los archivos nuevos.

---

## Decisiones

- **Sí:** un spec sólo para `consultar` de las 29 tablas. Es el mismo patrón repetido; aquí se revisan los parámetros.
- **No:** incluir `exportar` aquí. Va en SPEC 02 cuando los filtros estén fijos, para no duplicar cambios.
- **No:** un spec por módulo. El patrón es uniforme; los módulos quedan como pasos del plan.
- **Sí (para SPEC 02):** exportar a CSV con el módulo `csv`, en `exports/`, con los mismos filtros y sin `offset`/`limit`.
- **No (para SPEC 02):** Excel con `openpyxl`. Agrega una dependencia sin necesidad.
- **Sí:** filtrar a los hijos por la columna única del padre (`clave`, `nombre`, `email`, `edificio`). Es lo que el usuario conoce y escribe.
- **Sí:** filtrar por id sólo cuando el padre no tiene columna única (`exh_exhortos`, `arc_documentos`, `arc_remesas`, `ofi_documentos`).
- **Sí:** mostrar la columna "ID" en esos padres. Sin ella no hay forma de conocer el valor para filtrar a los hijos.
- **No:** filtrar hijos por un campo no único del padre (`num_oficio`, `exhorto_origen_id`). Puede devolver registros de varios padres.
- **Sí:** `safe_opcion` genérica para columnas de catálogo, contra el diccionario del modelo y con `==`. Rechaza errores de dedo en lugar de devolver cero resultados.
- **No:** `safe_string` con `like` para catálogos. No avisa cuando la opción no existe.
- **Sí:** `safe_id` y `safe_uuid` en `core/validations.py`. El error se muestra igual que el resto vía `main()`.
- **No:** tipos nativos `uuid.UUID` de Typer. Su mensaje de error difiere del resto del CLI.
- **Sí:** en columnas `datetime`, `*_hasta` incluye el día completo (`< hasta + 1 día`).
- **No:** comparar `datetime <= date`. Excluiría los registros del mismo día después de las 00:00.
- **Sí:** `--exhorto-origen-id` compara contra `func.upper(...)`. Lo envía otro Poder Judicial y puede traer minúsculas; `safe_string` siempre convierte a mayúsculas.
- **Sí:** el nombre del archivo del comando es el del modelo (`redams.py`, aunque la tabla se llama `redam`).

---

## Riesgos

| Riesgo | Mitigación |
| ------ | ---------- |
| Una relación con `back_populates` mal escrita rompe los mappers al ejecutar cualquier comando | `models/__init__.py` ya importa todos los modelos; ejecutar `--limit 5` en cada paso del plan detecta el error en ese paso. |
| `arc_remesas` une `Usuario` por `usuario_asignado_id`; un remesa sin asignar desaparece con `join` interno | Usar `outerjoin` para `Usuario` en `arc-remesas`, y no agregar `Usuario.estatus == "A"` a menos que se filtre por él. |
| `safe_opcion` con `safe_string` quita acentos; claves como `"SIN ORDEN CRONOLÓGICO"` no coincidirían | Ninguna columna filtrada en este spec usa claves con acentos; documentarlo en el docstring de `safe_opcion`. |
| Tablas grandes (`dgt_digitalizaciones`, `exh_exhortos`) con `like` sin índice son lentas | `limit` por defecto de 25 y orden por columna indexada o clave primaria. |

---

## Lo que **no** está en este spec

- Subcomando `exportar` (SPEC 02).
- Subcomandos de detalle, alta, edición o borrado.
- Cambios a modelos, esquema o comandos existentes.
- Pruebas automatizadas.

Cada uno, si llega, va en su propio spec.
