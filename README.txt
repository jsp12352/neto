NETO — SITE ADMIN + 2 BOTS DISCORD

CONTENU
- Site vitrine NETO et panneau admin Flask.
- Bot Discord Python : /onoff, /infobot, /say, /reglement, /bienvenueconfig.
- Bot Discord JavaScript : commandes de gestion et tickets.
- Un fichier .env unique pour les tokens et les identifiants autorisés.

INSTALLATION DANS TERMUX
1. Installe les outils :
   pkg update && pkg install python nodejs unzip -y
2. Décompresse le ZIP dans un dossier propre :
   mkdir -p ~/neto-complet
   unzip -o ~/storage/downloads/NETO_site_admin_et_2_bots.zip -d ~/neto-complet
   cd ~/neto-complet
3. Installe les dépendances Python :
   python -m pip install -r requirements.txt
4. Installe les dépendances du bot JavaScript :
   cd bots && npm install && cd ..
5. Crée le fichier .env depuis le modèle :
   cp .env.example .env
   nano .env
6. Remplace les valeurs d'exemple par tes vraies informations, puis enregistre dans nano avec CTRL+O, Entrée, CTRL+X.
7. Lance les trois services :
   python start_neto.py
8. Sur le téléphone, ouvre http://127.0.0.1:5000
   Admin : http://127.0.0.1:5000/admin/login
   Mot de passe local par défaut : 9999

CONFIGURATION DISCORD
- OWNER_IDS doit contenir les IDs utilisateur Discord de toi, ton ami et ton bras droit, séparés par des virgules, sans @.
- GESTION_CLIENT_ID est l'ID de l'application du deuxième bot.
- Colle les tokens seulement dans .env, jamais dans un message ou une capture d'écran.
- Dans le portail développeur Discord, configure les intents nécessaires et invite les deux bots avec bot + applications.commands et les permissions nécessaires.
- Les bots doivent rester en cours d'exécution pour répondre. Si tu fermes Termux, ils s'arrêtent.

SÉCURITÉ
- Le mot de passe 9999 est facile à deviner : acceptable pour un test local, à remplacer avant toute mise en ligne.
- Avant publication publique, définis une longue NETO_SECRET et un mot de passe admin robuste. Ne déploie pas les bots dans un service web qui arrête les processus enfants.
- Vérifie les permissions Discord et teste d'abord sur un serveur privé.
