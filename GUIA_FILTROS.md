# Guía de Filtros para Testing/Debugging del RPA

El RPA ahora soporta diferentes modos para procesar clientes específicos. Esto es útil para:
- 🐛 **Debugging**: Probar con un cliente problemático específico
- 🧪 **Testing**: Validar cambios sin procesar todo el Excel
- ⚡ **Desarrollo rápido**: Iterar rápidamente con casos específicos

## Cómo usar los filtros

Edita el archivo `main.py`, función `main()` y descomenta/modifica la línea que necesites:

---

## MODO 1: Procesar TODOS los clientes (Por defecto)

```python
rpa = RPA_AUTECO(RUTA_EXCEL)
```

✅ Procesa todos los clientes del Excel de principio a fin

---

## MODO 2: Procesar solo FILAS específicas

```python
rpa = RPA_AUTECO(RUTA_EXCEL, solo_filas=[0, 2, 4])
```

📌 **Parámetro**: `solo_filas` - Lista de índices (empiezan en 0)

**Ejemplos:**
- `solo_filas=[0]` → Solo la primera fila del Excel (fila 1)
- `solo_filas=[2]` → Solo la tercera fila del Excel (fila 3)
- `solo_filas=[0, 4, 9]` → Filas 1, 5 y 10 del Excel
- `solo_filas=[5, 6, 7]` → Filas 6, 7 y 8 consecutivas

💡 **Uso típico**: 
- Tienes un error en la fila 15 del Excel
- Cambias a: `solo_filas=[14]` (recuerda: índice 0)
- Ejecutas solo ese cliente para ver el error específico

---

## MODO 3: Procesar solo CÉDULAS específicas

```python
rpa = RPA_AUTECO(RUTA_EXCEL, solo_cedulas=['1234567890', '9876543210'])
```

📌 **Parámetro**: `solo_cedulas` - Lista de cédulas (como strings)

**Ejemplos:**
- `solo_cedulas=['1234567890']` → Solo el cliente con esa cédula
- `solo_cedulas=['111', '222', '333']` → Tres clientes específicos

💡 **Uso típico**: 
- Sabes que el cliente cédula "1234567890" tiene un problema
- No sabes en qué fila está
- Usas `solo_cedulas=['1234567890']` para procesarlo directamente

---

## MODO 4: Limitar CANTIDAD de clientes

```python
rpa = RPA_AUTECO(RUTA_EXCEL, limite=3)
```

📌 **Parámetro**: `limite` - Número entero

**Ejemplos:**
- `limite=1` → Solo el primer cliente
- `limite=5` → Los primeros 5 clientes
- `limite=10` → Los primeros 10 clientes

💡 **Uso típico**: 
- Quieres probar cambios sin esperar horas
- Procesas solo los primeros 3 clientes como prueba
- Si funciona bien, quitas el límite y ejecutas todos

---

## Actualización del Excel con Estados

✨ **Importante**: El Excel siempre se actualiza en la fila correcta, incluso con filtros.

Cuando usas filtros:
- Las columnas "Estado" y "Detalle Error" se actualizan en las filas correctas
- Las filas no procesadas mantienen su estado anterior
- Puedes ejecutar múltiples veces con diferentes filtros

**Ejemplo de flujo:**
1. Ejecutas con `limite=5` → Primeros 5 marcados como procesados
2. Hay error en el 3ro → Cambias a `solo_filas=[2]`
3. Corriges el error, ejecutas de nuevo
4. El Excel solo actualiza la fila 3

---

## Combinando con el Excel de Estados

El Excel tendrá estas columnas automáticamente:

| Estado | Detalle Error |
|--------|---------------|
| Pedido creado | Proceso completado exitosamente |
| Omitido - Material bloqueado | Todos los materiales están bloqueados |
| Error al crear pedido | [descripción del error] |
| Omitido | Referencia inválida |
| Pendiente | (no procesado aún) |

---

## Consejos

1. **Para debugging específico**: Usa `solo_filas` con el índice exacto
2. **Para pruebas rápidas**: Usa `limite=3` o `limite=5`
3. **Para clientes conocidos**: Usa `solo_cedulas`
4. **Para producción**: Quita todos los filtros (modo 1)

---

## Ejemplo completo de debugging

Tienes un error en el cliente "Juan Pérez" que está en la fila 25:

```python
# Paso 1: Ejecuta solo esa fila
rpa = RPA_AUTECO(RUTA_EXCEL, solo_filas=[24])  # Fila 25 = índice 24
rpa.ejecutar()

# Paso 2: Ves el error en consola, lo corriges en el código

# Paso 3: Vuelves a ejecutar para validar
rpa = RPA_AUTECO(RUTA_EXCEL, solo_filas=[24])
rpa.ejecutar()

# Paso 4: Funciona! Ahora pruebas con unos pocos más
rpa = RPA_AUTECO(RUTA_EXCEL, limite=10)
rpa.ejecutar()

# Paso 5: Todo OK! Ejecutas producción completa
rpa = RPA_AUTECO(RUTA_EXCEL)
rpa.ejecutar()
```

---

📝 **Nota**: Recuerda que los índices en Python empiezan en 0:
- Fila 1 del Excel = índice 0
- Fila 2 del Excel = índice 1
- Fila 10 del Excel = índice 9
- etc.
