import os
import argparse
from libs.sumup_to_shopify import sumup_to_shopify

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convierte CSV de SumUp a formato Shopify POS.")
    parser.add_argument("input_csv", help="Archivo de entrada (SumUp CSV)")
    parser.add_argument("output_csv", help="Archivo de salida (Shopify CSV)")
    parser.add_argument("--template", default="product_template.csv", help="Archivo CSV de plantilla de Shopify")
    parser.add_argument("--num", type=int, help="Cantidad de registros a exportar")
    parser.add_argument("--start", type=int, help="Línea de inicio para procesar (0-indexada)")
    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_csv = os.path.join(BASE_DIR, 'docs', args.input_csv)
    output_csv = os.path.join(BASE_DIR, 'docs', args.output_csv)
    template_csv = os.path.join(BASE_DIR, 'docs', args.template)

    sumup_to_shopify(input_csv, output_csv, template_csv, args.num, args.start)