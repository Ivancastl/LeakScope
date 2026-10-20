# LeakScope

Buscador de filtraciones publicadas en foros tipo *breach* y *dark*, para uso OSINT.
Muestra únicamente los metadatos de cada registro (títulos, autores, fechas, vistas…),
**sin los datos filtrados ni los enlaces**: sirve para saber qué se ha expuesto, no para
acceder a ello. Es una app web ligera hecha con Flask.

## Clonar

```powershell
git clone https://github.com/Ivancastl/LeakScope.git
cd LeakScope
```

## Requisitos

- Python 3.10 o superior
- Flask (se instala con `requirements.txt`)

## Ejecutar (Windows / PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre **http://127.0.0.1:5000** en el navegador. Para detener el servidor: **Ctrl+C**.

## Notas

- Los CSV que lee la app están en la carpeta `data/`.
- Antes de mostrar o exportar, se eliminan las columnas de URL y cualquier enlace.
- El servidor escucha solo en tu equipo (`127.0.0.1`).
