from pathlib import Path
import csv
import io
import re
import math
from datetime import datetime
from flask import Flask, render_template, request, Response

app = Flask(__name__)

LABELS = {
    'fuente': 'Fuente', 'tid': 'ID', 'prefijo': 'Prefijo', 'titulo': 'Título', 'autor': 'Autor',
    'fecha_publicacion': 'Publicación', 'respuestas': 'Respuestas', 'vistas': 'Vistas',
    'paginas': 'Páginas', 'adjuntos': 'Adjuntos', 'ultimo_post_fecha': 'Fecha últ. modificación',
    'ultimo_post_usuario': 'Última modificación', 'estado': 'Estado', 'pagina_listado': 'Pág. listado',
    'capturado': 'Capturado',
}
NUMERIC = {'tid', 'respuestas', 'vistas', 'paginas', 'adjuntos', 'pagina_listado'}
DATES = {'fecha_publicacion', 'ultimo_post_fecha', 'capturado'}

@app.template_filter('fecha')
def fecha(value):
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%d-%m-%y, %I:%M %p', '%Y-%m-%d %H:%M:%S', '%d-%m-%y'):
        try:
            d = datetime.strptime(value.strip(), fmt)
            return d.strftime('%Y-%m-%d' if fmt == '%d-%m-%y' else '%Y-%m-%d %H:%M')
        except (ValueError, AttributeError):
            pass
    return value
DATA_DIR = Path(__file__).resolve().parent / 'data'
SOURCES = {
    'breach': DATA_DIR / 'db_leaks_progreso.csv',
    'darkforum': DATA_DIR / 'databases_progreso.csv',
}
DEFAULT = ['titulo', 'ultimo_post_usuario', 'respuestas', 'vistas', 'adjuntos']

def load_data():
    rows, fields, errors = [], [], []
    for source, path in SOURCES.items():
        try:
            with path.open(encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                allowed = [k for k in (reader.fieldnames or []) if 'url' not in k.lower()]
                fields.extend(k for k in allowed if k not in fields)
                for raw in reader:
                    row = {k: re.sub(r'https?://\S+', '[enlace omitido]', raw.get(k) or '') for k in allowed}
                    row['fuente'] = source
                    rows.append(row)
        except (OSError, UnicodeError, csv.Error) as e:
            errors.append(f'{source}: {e}')
    return rows, ['fuente'] + fields, errors

def selection():
    rows, fields, errors = load_data()
    q = request.args.get('q', '').strip().casefold()
    source = request.args.get('fuente', '')
    rows = [r for r in rows if (not source or r['fuente'] == source) and (not q or q in ' '.join(r.values()).casefold())]
    sort = request.args.get('orden', 'vistas')
    if sort not in fields:
        sort = 'vistas'
    numeric = sort in NUMERIC
    def key(row):
        value = row.get(sort, '')
        if numeric:
            try:
                return int(value.replace(',', '').replace('.', ''))
            except ValueError:
                return -1
        return value.casefold()
    rows.sort(key=key, reverse=request.args.get('direccion', 'desc') == 'desc')
    return rows, fields, errors

@app.get('/')
def index():
    rows, fields, errors = selection()
    counts = {s: sum(1 for r in rows if r['fuente'] == s) for s in SOURCES}
    try:
        page = max(1, int(request.args.get('pagina', 1)))
    except ValueError:
        page = 1
    pages = max(1, math.ceil(len(rows) / 50))
    page = min(page, pages)
    columns = fields if request.args.get('detalle') == '1' else ['fuente'] + [k for k in DEFAULT if k in fields]
    def page_url(n):
        args = request.args.to_dict()
        args['pagina'] = n
        from flask import url_for
        return url_for('index', **args)
    return render_template('index.html', rows=rows[(page-1)*50:page*50], fields=fields, columns=columns, errors=errors, total=len(rows), page=page, pages=pages, page_url=page_url, counts=counts, labels=LABELS, numeric=NUMERIC, dates=DATES)

@app.get('/exportar')
def export():
    rows, fields, _ = selection()
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        # Avoid spreadsheet formulas when opening the export in Excel.
        writer.writerow({k: "'" + v if v.lstrip().startswith(('=', '+', '-', '@')) else v for k, v in row.items()})
    return Response('\ufeff' + buffer.getvalue(), mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=registros_sin_urls.csv'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

