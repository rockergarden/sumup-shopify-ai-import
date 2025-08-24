import requests
import json

def get_lmstudio_description(nombre, categoria):
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
    user_prompt = f'Dame la descripción de un producto para Shopify: {nombre}, categoría {categoria}.'
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 780,
        "top_p": 0.92,
        "presence_penalty": 0.3,
        "frequency_penalty": 0.1,
        "stream": False
    }
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        data = json.loads(content)
    except Exception:
        data = json.loads(content)
    return data