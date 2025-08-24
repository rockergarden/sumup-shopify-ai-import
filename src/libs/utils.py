import unicodedata
import re
import itertools
import sys
import time

def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

def spinner(msg, stop_event):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        sys.stdout.write(f'\r{msg} {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')