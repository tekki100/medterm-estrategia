import json, re

with open('/home/antigravity/medterm-estrategia/src/data/termsCatalog.js', 'r', encoding='utf-8') as f:
    terms_js = f.read()

with open('/home/antigravity/medterm-estrategia/src/data/questionsBank.js', 'r', encoding='utf-8') as f:
    questions_js = f.read()

with open('/home/antigravity/medterm-estrategia/src/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

with open('/home/antigravity/medterm-estrategia/src/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Remover imports ES Modules do app.js para torná-lo inline no HTML
app_js_clean = re.sub(r'import\s+.*?;', '', app_js)

html = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MedTerm Estratégia — 500 Questões de Terminologia Médica</title>
  <style>
{css}
  </style>
</head>
<body>
  <div id="app"></div>
  <script>
{terms_js.replace('export const TERMS_CATALOG =', 'window.TERMS_CATALOG = const_terms =')}
const TERMS_CATALOG = window.TERMS_CATALOG;

{questions_js.replace('export const QUESTIONS_BANK =', 'window.QUESTIONS_BANK = const_questions =')}
const QUESTIONS_BANK = window.QUESTIONS_BANK;

{app_js_clean}
  </script>
</body>
</html>
"""

artifact_path = '/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/ede86493-80cd-459f-b62f-074d0d6f84ec/medterm_estrategia_500.html'
with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Artefato standalone gerado com sucesso em {artifact_path} ({len(html)} bytes)!")
