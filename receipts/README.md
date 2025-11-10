# Recibos Digitales

Esta carpeta almacena los recibos digitales generados por el Notario Digital.

## Formato

Los recibos se guardan en formato JSON:

```json
{
  "timestamp": "2025-11-10T14:30:00.123456Z",
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "firma": "MEUCIQDxKvqL5h3w...",
  "archivo_original": "documento.pdf"
}
```

## Nomenclatura

Los archivos se nombran automáticamente como:

```
recibo_[nombre_archivo]_[timestamp].json
```

Ejemplo: `recibo_contrato.pdf_2025-11-10T14-30-00-123456Z.json`

## Uso

- **Guardar**: Los recibos se guardan automáticamente al notarizar
- **Verificar**: Carga un recibo en la pestaña "Verificar Recibo" de la aplicación

## Seguridad

✓ Los recibos son seguros para compartir
✓ No contienen información sensible del archivo
✓ Solo contienen el hash, timestamp y firma

⚠️ Guarda copias de seguridad de tus recibos importantes
