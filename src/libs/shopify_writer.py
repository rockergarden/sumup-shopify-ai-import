def load_template_headers(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
    return header.split(',')