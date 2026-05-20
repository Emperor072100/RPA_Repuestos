# Guía de Uso — RPA Auteco Repuestos

---

## ¿Qué hace el RPA?

El RPA (Robot de Automatización) lee un archivo Excel con solicitudes de repuestos, consulta los precios en el Portal de Socios Auteco y crea automáticamente los pedidos en SAP. Al terminar, actualiza el mismo Excel con el número de pedido generado y el estado de cada solicitud.

---

## ¿Qué necesita el archivo Excel?

El archivo debe tener las siguientes columnas (los nombres pueden tener mayúsculas/minúsculas):

| Columna | Descripción | Ejemplo |
|---|---|---|
| **ID** | Identificador único de la solicitud | 1045 |
| **Nombre completo** | Nombre del cliente | Juan Pérez |
| **Cédula** | Número de cédula del cliente | 1012345678 |
| **Teléfono** / **Celular** | Número de contacto | 3001234567 |
| **Ciudad** | Ciudad de entrega | Bogotá |
| **Marca** | Marca de la moto | TVS / Honda / Yamaha |
| **Repuestos** / **Referencia** | Código(s) del repuesto | Ver formatos abajo |
| **Estado** | El RPA lo llena automáticamente | — |
| **Numero Pedido** | El RPA lo llena automáticamente | — |
| **Detalle Error** | El RPA lo llena automáticamente | — |

> **Nota:** Las columnas **Estado**, **Numero Pedido** y **Detalle Error** no necesitan existir en el Excel. Si no están, el RPA las crea solo.

---

## Formatos válidos en la columna de Repuestos

| Lo que escribes | Qué significa |
|---|---|
| `12345` | Un repuesto, cantidad 1 |
| `12345 X2` | Un repuesto, cantidad 2 |
| `12345 (3)` | Un repuesto, cantidad 3 |
| `12345, 67890` | Dos repuestos distintos, cantidad 1 cada uno |
| `12345 X2, 67890` | Dos repuestos: el primero cantidad 2, el segundo cantidad 1 |

### Casos que el RPA descarta automáticamente
- Valores con guion: `12345-A` → se omite
- Valores que empiezan con letra: `ABC123` → se omite
- Celdas vacías → se omite

---

## Cómo ejecutar el RPA

### Paso 1 — Abrir el programa
Haga doble clic en el archivo **`main.exe`**.

Se abrirá una ventana negra (consola) que muestra el progreso del robot.

### Paso 2 — Seleccionar el Excel
Aparecerá una ventana para seleccionar el archivo. Busque su Excel y haga clic en **Abrir**.

### Paso 3 — Login en SAP (primera vez del día)
El RPA abre Chrome automáticamente. Si SAP pide verificación de cookies o captcha:

1. Ingrese manualmente su usuario y contraseña en la página de SAP que aparece en Chrome.
2. Una vez dentro de SAP, el robot continúa solo.

> **Importante:** Esto solo ocurre la primera vez que ejecuta el RPA en el día, o si Chrome fue cerrado. Las siguientes ejecuciones del mismo día no pedirán login.

### Paso 4 — Esperar que termine
El robot procesa cada fila del Excel de forma automática. En la consola verá el progreso en tiempo real. Al finalizar muestra un resumen:

```
Total de clientes: 20
Exitosos: 17
Fallidos: 3
```

### Paso 5 — Revisar el Excel
Al terminar, abra su Excel. Encontrará las columnas **Estado** y **Numero Pedido** actualizadas en cada fila.

---

## Estados que verá en el Excel

| Estado | Significado |
|---|---|
| **Pedido creado** | El pedido fue creado exitosamente en SAP. La columna *Numero Pedido* tendrá el número asignado. |
| **Disponibilidad dealer** | El repuesto está disponible en el dealer (página 1 del portal). No se crea pedido SAP. |
| **Omitido** | La referencia del repuesto no tiene un formato válido o está vacía. |
| **Omitido - Material bloqueado** | El repuesto está bloqueado en SAP y no puede ser pedido. |
| **Bloqueado** | El cliente o la combinación cliente/producto está bloqueada en SAP. |
| **Pedido ya existe** | Ya existe un pedido SAP para ese cliente y repuesto (evita duplicados). |
| **Error al crear pedido** | Ocurrió un error inesperado. Revisar la columna *Detalle Error* para más información. |
| **Error - Precio en 0** | El portal no tiene precio registrado para ese repuesto. |
| **Error - Portal sin precio** | No se pudo consultar el precio en el portal de socios. |

---

## Reglas importantes

- **El RPA omite automáticamente** las filas que ya tienen un número de pedido en la columna *Numero Pedido*, para evitar crear duplicados.
- **El RPA omite automáticamente** las filas con estado *Error al crear pedido* o *Bloqueado* en ejecuciones posteriores.
- Si necesita reprocesar una fila con error, borre el contenido de las columnas *Estado* y *Detalle Error* de esa fila y vuelva a ejecutar el RPA.
- **No cierre Chrome** mientras el RPA está corriendo.
- **No modifique el Excel** mientras el RPA está en ejecución.

---

## Preguntas frecuentes

**¿Puedo agregar más filas al Excel y volver a ejecutar?**
Sí. El RPA solo procesa las filas que no tienen número de pedido asignado.

**¿Qué pasa si el RPA se cierra a la mitad?**
Los pedidos ya creados quedan guardados en el Excel. Al volver a ejecutar, el robot retoma desde donde quedó (omite los que ya tienen número de pedido).

**¿Por qué algunas filas quedan en "Disponibilidad dealer"?**
Significa que el repuesto tiene stock disponible en el concesionario (página 1 del portal de socios), por lo que no se genera un pedido a SAP.

**El robot no encuentra el botón / se traba en pantalla**
Cierre Chrome manualmente, espere 10 segundos y vuelva a ejecutar `main.exe`. Si el problema persiste, contacte al área de soporte.

---

*Documento preparado para usuarios del RPA Auteco — Repuestos*
