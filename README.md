# Clair — résumés locaux de documents

Clair est un site en français qui extrait les PDF textuels, Word `.docx`, `.txt` et Markdown `.md`, puis rédige le résumé avec Qwen 2.5 0.5B exécuté sur cet ordinateur. Aucune clé ni API distante n'est utilisée. Le résumé apparaît dans la page et peut être copié, téléchargé en TXT ou Word, ou imprimé en PDF depuis le navigateur.

## Installation Windows PowerShell

Python 3.10+ est requis. Crée et active l'environnement du projet :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Installe PyTorch en version CPU depuis le sélecteur officiel Windows/Pip/CPU : [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/), puis installe les paquets du projet :

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ouvre http://127.0.0.1:8000. Si `.venv` existe déjà, active-le sans le recréer.

## Premier résumé

Au premier clic sur « Générer », Transformers télécharge les poids Qwen dans `.model-cache` (environ 1 Go pour les poids non quantifiés) puis les conserve sur cet ordinateur. PyTorch et Transformers prennent aussi de l'espace disque. Le modèle fonctionne en CPU et peut être lent, surtout sur un PC modeste. L'interface du site s'ouvre sans charger le modèle; celui-ci n'est initialisé qu'au premier résumé.

Qwen 2.5 0.5B a une fenêtre documentée de 32 768 tokens, mais cela ne signifie pas qu'il peut résumer un livre entier d'un seul coup. Clair découpe le document, résume chaque partie l'une après l'autre pour limiter l'usage mémoire, condense les résumés intermédiaires, puis rédige la synthèse globale. Un ouvrage de centaines de pages peut prendre longtemps. Un petit modèle peut aussi manquer des nuances; il faut relire le résultat.

Le mode Synthétique est sélectionné par défaut (130–180 mots), Équilibré vise 300–450 mots et Approfondi 700–900 mots. Le résumé est rédigé en prose avec le sujet, le fil directeur, les idées ou événements principaux et la conclusion.

Les PDF scannés qui ne contiennent que des images nécessitent une étape OCR, non incluse. Les formats acceptés sont PDF, DOCX, TXT et MD. La taille des fichiers et des sections se règle dans `.env` (copié depuis `.env.example`). Les anciens fichiers sous `resultats/` viennent de l'ancien résumé extractif et ne sont pas les résultats de Qwen.
