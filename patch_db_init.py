from pathlib import Path

p = Path(__file__).parent / 'app.py'
text = p.read_text()
old = "if __name__ == '__main__':\n    app.run(debug=True)\n"
new = "if __name__ == '__main__':\n    with app.app_context():\n        db.create_all()\n    app.run(debug=True)\n"
if old not in text:
    raise RuntimeError('old block not found')

p.write_text(text.replace(old, new))
print('patched')
