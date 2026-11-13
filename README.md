# Clair — résumés locaux de documents

Clair est un site en français qui extrait les PDF textuels, Word `.docx`, `.txt` et Markdown `.md`, puis sélectionne les phrases importantes avec Sumy LSA, exécuté sur cet ordinateur. Aucun gros modèle ni API distante n'est utilisé. Le résumé apparaît dans la page et peut être copié, téléchargé en TXT ou Word, ou imprimé en PDF depuis le navigateur.

## Installation Windows PowerShell

Python 3.10+ est requis. Sumy LSA fonctionne sur CPU sans gros modèle à télécharger. Cette méthode extrait des phrases importantes sans les réécrire : elle est rapide et évite les faits inventés, mais peut manquer de transitions et de contexte, surtout dans les romans. Crée et active l'environnement du projet :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Installe les dépendances légères du projet :

```powershell
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ouvre http://127.0.0.1:8000. Si `.venv` existe déjà, active-le sans le recréer.

## Premier résumé

Sumy LSA classe les phrases par importance statistique et les extrait du texte. Il ne comprend pas réellement l'intrigue : ses résumés peuvent manquer de transitions ou de contexte. Cette méthode évite de reformuler ou d'inventer des phrases, mais ne garantit pas que chaque sélection soit complète ou parfaitement fidèle.

Clair traite le document par sections pour limiter la mémoire. Les textes longs sont résumés bloc par bloc, puis les phrases retenues sont réduites à la longueur demandée. La qualité dépend de la ponctuation et de l'extraction du texte; les en-têtes et numéros de page répétés peuvent gêner la sélection.

Le mode Synthétique est sélectionné par défaut (130–180 mots), Équilibré vise 300–450 mots et Approfondi 700–900 mots. Le résumé est rédigé en prose avec le sujet, le fil directeur, les idées ou événements principaux et la conclusion.

Les PDF scannés qui ne contiennent que des images nécessitent une étape OCR, non incluse. Les formats acceptés sont PDF, DOCX, TXT et MD. La taille maximale des fichiers se règle dans `.env` (copié depuis `.env.example`). Sumy fonctionne en CPU et ne télécharge aucun modèle.
