import pandas as pd
import sys
import threading
import os
import time
import json
from libs.utils import slugify, spinner
from libs.lmstudio_api import get_lmstudio_description
from libs.shopify_writer import load_template_headers

# Ruta absoluta al archivo de configuración
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'shopify_config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    SHOPIFY_CONFIG = json.load(f)

def sumup_to_shopify(input_csv, output_csv, template_csv, num_records=None, start_line=None):
    import csv
    start_time = time.time()
    df = pd.read_csv(input_csv)
    template_headers = load_template_headers(template_csv)
    
    # FILTRO: excluir Manga y Comics (insensible a mayúsculas/minúsculas)
    df = df[~df['Category'].astype(str).str.lower().isin(['manga', 'mangas', 'comic', 'comics'])]
    df = df.reset_index(drop=True)

    if num_records is not None:
        df = df.head(num_records)
    
    productos_procesados = 0
    errores = []
    sumup_fallidos = []

    idx = start_line if start_line is not None else 0
    print(f"Iniciando procesamiento desde la línea {idx + 1}")

    write_header = not os.path.exists(output_csv) or os.stat(output_csv).st_size == 0
    output_file = open(output_csv, 'a', newline='', encoding='utf-8')
    writer = csv.DictWriter(output_file, fieldnames=template_headers)
    if write_header:
        writer.writeheader()
    
    while idx < len(df):
        row = df.iloc[idx]
        nombre = row['Item name']
        
        if pd.isna(nombre) or nombre.strip() == "":
            idx += 1
            continue
        
        handle = slugify(nombre)
        categoria = row['Category']
        
        stop_event = threading.Event()
        spin_thread = threading.Thread(target=spinner, args=(f"[Línea {idx + 1}] Procesando {nombre}", stop_event))
        spin_thread.start()
        
        try:
            t0 = time.time()
            desc_data = get_lmstudio_description(nombre, categoria)
            t1 = time.time()
            
            stop_event.set()
            spin_thread.join()
            
            tags = desc_data.get('tags', '')
            if isinstance(tags, list):
                tags = ", ".join(tags)
            else:
                tags = str(tags)
            
            variantes = []
            j = idx + 1
            while j < len(df) and (pd.isna(df.iloc[j]['Item name']) or df.iloc[j]['Item name'].strip() == ""):
                if not pd.isna(df.iloc[j]['Variations']) and df.iloc[j]['Variations'].strip():
                    variantes.append(df.iloc[j])
                j += 1
            
            if variantes:
                for i, variante in enumerate(variantes):
                    shopify_row = {col: "" for col in template_headers}
                    shopify_row['Handle'] = handle
                    if i == 0:
                        shopify_row['Title'] = nombre
                        shopify_row['Body (HTML)'] = desc_data.get('descripcion', '')
                        shopify_row['Vendor'] = SHOPIFY_CONFIG['vendor']
                        shopify_row['Type'] = categoria
                        shopify_row['Tags'] = f"from_sumup, {tags}"
                        shopify_row['Published'] = SHOPIFY_CONFIG['published']
                        shopify_row['Image Src'] = row.get('Image 1', '')
                    variacion = variante['Variations'].strip()
                    if variacion.startswith('Talla '):
                        shopify_row['Option1 Name'] = 'Talla'
                        shopify_row['Option1 Value'] = variacion.replace('Talla ', '')
                    else:
                        shopify_row['Option1 Name'] = 'Tipo'
                        shopify_row['Option1 Value'] = variacion
                    shopify_row['Variant Price'] = variante.get('Price', '')
                    shopify_row['Variant Inventory Qty'] = variante.get('Quantity', 0)
                    shopify_row['Variant Inventory Policy'] = 'deny'
                    shopify_row['Variant Fulfillment Service'] = 'manual'
                    shopify_row['Variant Requires Shipping'] = 'TRUE'
                    shopify_row['Variant Taxable'] = 'TRUE'
                    shopify_row['Variant Weight Unit'] = 'g'
                    shopify_row['Status'] = 'draft'
                    writer.writerow(shopify_row)
            else:
                shopify_row = {col: "" for col in template_headers}
                shopify_row['Handle'] = handle
                shopify_row['Title'] = nombre
                shopify_row['Body (HTML)'] = desc_data.get('descripcion', '')
                shopify_row['Vendor'] = SHOPIFY_CONFIG['vendor']
                shopify_row['Type'] = categoria
                shopify_row['Tags'] = f"imported, {tags}"
                shopify_row['Published'] = SHOPIFY_CONFIG['published']
                shopify_row['Image Src'] = row.get('Image 1', '')
                shopify_row['Option1 Name'] = 'Title'
                shopify_row['Option1 Value'] = 'Default Title'
                shopify_row['Variant Price'] = row.get('Price', '')
                shopify_row['Variant Inventory Qty'] = row.get('Quantity', 0)
                shopify_row['Variant Inventory Policy'] = 'deny'
                shopify_row['Variant Fulfillment Service'] = 'manual'
                shopify_row['Variant Requires Shipping'] = 'TRUE'
                shopify_row['Variant Taxable'] = 'TRUE'
                shopify_row['Variant Weight Unit'] = 'g'
                shopify_row['Status'] = 'draft'
                writer.writerow(shopify_row)
            
            productos_procesados += 1

            # Estimación de tiempo restante y barra de progreso fija y verde
            elapsed = time.time() - start_time
            total = len(df)
            restantes = total - productos_procesados
            if productos_procesados > 0:
                avg_time = elapsed / productos_procesados
                tiempo_restante = avg_time * restantes
                h, rem = divmod(tiempo_restante, 3600)
                m, s = divmod(rem, 60)
                bar_len = 100
                filled_len = int(bar_len * productos_procesados // total)
                bar = '\033[42m' + ' ' * filled_len + '\033[0m' + '-' * (bar_len - filled_len)
                sys.stdout.write('\033[F\033[K\033[F\033[K')
                print(f"Procesado: [Línea {idx + 1}] {nombre} ({t1-t0:.2f}s) {productos_procesados}/{total}")
                print(f"Tiempo estimado restante: {int(h):02d}:{int(m):02d}:{int(s):02d} | [{bar}]")
            idx = j
            
        except Exception as e:
            stop_event.set()
            spin_thread.join()
            print(f"❌ [Línea {idx + 1}] Error procesando {nombre}: {e}")
            print(f"💡 Para continuar desde este punto, usa: --start {idx}")
            errores.append(f"Línea {idx + 1}: {nombre} - {e}")
            sumup_fallidos.append(row)
            idx += 1

    output_file.close()
    
    if errores:
        with open('errores.log', 'w', encoding='utf-8') as f:
            for linea in errores:
                f.write(linea + '\n')
        print(f"Se guardaron {len(errores)} errores en errores.log")
    
    if sumup_fallidos:
        base, ext = os.path.splitext(input_csv)
        fallidos_csv = f"{base}.fallidos{ext}"
        sumup_fallidos_df = pd.DataFrame(sumup_fallidos)
        sumup_fallidos_df.to_csv(fallidos_csv, index=False, encoding='utf-8')
        print(f"Se guardaron {len(sumup_fallidos)} registros fallidos en {fallidos_csv}")
    
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Exportados {productos_procesados} productos principales a {output_csv}")
    print(f"Tiempo de procesamiento: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d} (hh:mm:ss)")
