# SumUp to Shopify Converter usando IA para generar contenido faltante

Este proyecto permite convertir un archivo de exportación de productos de **SumUp** en un archivo de importación compatible con **Shopify POS**. Además, utiliza inteligencia artificial para generar automáticamente descripciones y etiquetas de productos, enriqueciendo la información antes de importarla a Shopify.

## Características principales

- **Conversión automática**: Toma un CSV exportado desde SumUp y lo transforma al formato requerido por Shopify, utilizando una plantilla de ejemplo.
- **Generación de descripciones con IA**: Si faltan descripciones o etiquetas, el sistema utiliza un modelo de lenguaje grande (LLM) local, accedido mediante la API de LMStudio, para generar textos persuasivos y compatibles con Google Shopping.
- **Personalización avanzada**: El prompt enviado a la IA está cuidadosamente diseñado para obtener títulos, descripciones en HTML y tags relevantes para Shopify.
- **Salida estructurada**: El resultado devuelto por el modelo (por ejemplo, `gpt-oss 20b`) es un JSON listo para ser utilizado en el flujo de importación.

## Archivo de configuración

El comportamiento del conversor puede personalizarse mediante el archivo de configuración `shopify_config.json`, ubicado en la carpeta `src/config/`.  
En este archivo puedes definir:

- **vendor**: El nombre del proveedor que se usará por defecto en todos los productos importados.
- **published**: Determina si los productos importados quedarán publicados (`"TRUE"`) o como borrador (`"FALSE"`) en Shopify.

### Ejemplo de archivo `shopify_config.json`

```json
{
  "vendor": "Bimajo.cl Mangas / Comics / Regalos",
  "published": "FALSE"
}
```

> Si deseas que los productos se publiquen automáticamente en Shopify, cambia `"published"` a `"TRUE"`.

## Ejemplo de JSON generado por la IA

```json
{
  "titulo": "Llavero Acrílico 3‑en‑uno – Ropa y Accesorios",
  "descripcion": "<p>Haz que cada llave brille con estilo gracias a nuestro set de llaveros acrílicos 3‑en‑uno. Cada llavero está diseñado para destacar en cualquier bolso, mochila o llavero principal, aportando un toque moderno y resistente al día a día. Ideal para coleccionar, regalar o simplemente añadir un detalle divertido a tu rutina.</p>\n<ul>\n  <li>Material: Acrílico transparente;</li>\n  <li>Tamaño disponible: 7 cm × 2 cm (punto final);</li>\n</ul>",
  "tags": "llavero, acrílico, accesorios, set de llaveros, 3‑en‑uno, regalo"
}
```

## ¿Dónde se encuentra el prompt y cómo personalizarlo?

El prompt que se utiliza para la generación de contenido con IA se encuentra en el archivo [`src/libs/lmstudio_api.py`](src/libs/lmstudio_api.py), dentro de la función `get_lmstudio_description`.  
Puedes modificar este prompt para ajustar el tono, formato o tipo de información que deseas que la IA genere para tus productos.

### Ejemplo de prompt utilizado

```python
SYSTEM_PROMPT = (
    "Genera descripciones de productos para Shopify siguiendo estas reglas:\n\n"
    "- El título debe tener el formato: Tipo de producto y nombre del personaje y serie o película al que pertenece. Ejemplo: Anya de Spy x Family.\n"
    "- No incluyas en el título características como que es hipoalergénico.\n"
    "- Si el producto no tiene personaje o serie de televisión, infiere el título solo con la información entregada, sin inventar series o películas.\n"
    "- Si el producto dice \"3 x\" es porque son 3 productos y debes agregar esa información en el título y la descripción.\n"
    "- Si no tienes información de color, no la agregues.\n"
    "- Usa las unidades de medida que se usan en Chile, evita usar pulgadas y utiliza centímetros en esos casos.\n"
    "- La descripción debe tener un tono lúdico y persuasivo para la compra, en un solo párrafo y sin emojis.\n"
    "- Las características del producto como el material y color deben ir en una lista tipo bullet list en HTML, cada elemento debe terminar en punto.\n"
    "- La descripción debe ser compatible con Google Shopping.\n"
    "- Incluye etiquetas (\"tags\") de productos para Shopify.\n"
    "- La respuesta debe ser un JSON con las claves \"titulo\", \"descripcion\" y \"tags\".\n"
    "- La descripción debe estar en HTML para Shopify.\n"
    "- Puedes inventar información de caracteristicas del producto basandote en lo que sabes del producto, por ejemplo, si es un llavero acrilico, tu puedes inferir cuanto mide un llavero, que es de acrilico, y que tiene un diseño de un personaje popular."
)
```

### Ejemplos de prompts cortos para otros productos

- `"Dame la descripción de un producto para Shopify: Polera Pikachu, categoría Poleras."`
- `"Dame la descripción de un producto para Shopify: Taza Sailor Moon, categoría Tazas."`
- `"Dame la descripción de un producto para Shopify: Mochila Totoro, categoría Mochilas."`

El sistema enviará estos prompts junto con las reglas del prompt principal para obtener un JSON estructurado con título, descripción y tags.


## Estructura del proyecto

- `src/converter.py`: Script principal para ejecutar la conversión.
- `src/libs/sumup_to_shopify.py`: Lógica de transformación de datos SumUp a Shopify.
- `src/libs/lmstudio_api.py`: Comunicación con la API local de LMStudio para generación de descripciones.
- `src/libs/shopify_writer.py`: Utilidades para manejo de plantillas CSV de Shopify.
- `src/libs/utils.py`: Funciones auxiliares (slugify, spinner, etc).
- `src/config/shopify_config.json`: Configuración de vendor y estado de publicación.
- `docs/`: Ejemplos de archivos CSV de entrada y salida.

## Lenguaje de programación

- **Python 3** (recomendado 3.8+)
- Dependencias: `pandas`, `requests`

## Ejemplo de uso

Supón que tienes un archivo de productos exportado de SumUp llamado `sumup_base.csv` y quieres generar un archivo de importación para Shopify llamado `shopify1.csv`:

```sh
python src/converter.py sumup_base.csv shopify1.csv
```

Opcionalmente, puedes especificar una plantilla diferente, limitar el número de registros o indicar desde qué línea comenzar:

```sh
python src/converter.py sumup_base.csv shopify1.csv --template product_template.csv --num 10 --start 5
```

## ¿Cómo funciona la generación con IA?

- Por cada producto, si falta información relevante, se envía un prompt a un modelo LLM local (por ejemplo, `gpt-oss 20b` corriendo en LMStudio).
- El prompt está diseñado para obtener un JSON con las claves `titulo`, `descripcion` (en HTML) y `tags`.
- El resultado se integra automáticamente en el CSV de salida para Shopify.

## Requisitos para la IA

- Tener corriendo **LMStudio** en tu máquina local, escuchando en `http://localhost:1234/v1/chat/completions`.
- El modelo recomendado es `gpt-oss 20b` (puedes cambiarlo en [`get_lmstudio_description`](src/libs/lmstudio_api.py)).

---

**Autor: Cristián Riveros**  
Este proyecto fue desarrollado para facilitar la migración y enriquecimiento de catálogos de productos entre SumUp y Shopify, aprovechando el poder de la IA generativa