# PFE 2027 Tracker — Agroalimentaire

Plateforme HTML locale gratuite : ouvrir `index.html`. Saisie d'offres, recherche, statuts, top 5, import/export JSON et anti-doublons. Les statuts et notes restent dans le **navigateur utilisé**, pas dans GitHub.

## Hébergement gratuit et veille planifiée

1. Créer un dépôt **public** GitHub et y déposer tout le contenu de ce dossier (y compris `.github/workflows/veille.yml`).
2. Dans `Settings > Pages`, choisir `Deploy from a branch` puis `main` et `/ (root)`.
3. Ouvrir `https://VOTRE-COMPTE.github.io/NOM-DU-DEPOT/`.
4. Demander un accès à l'API Offres d'emploi de France Travail sur https://francetravail.io/produits-partages/catalogue/offres-emploi (l'accès peut nécessiter inscription/habilitation). Dans `Settings > Secrets and variables > Actions`, créer `FRANCE_TRAVAIL_CLIENT_ID`, `FRANCE_TRAVAIL_CLIENT_SECRET`, et éventuellement `FRANCE_TRAVAIL_SCOPE` selon la documentation officielle de l'application.
5. Autoriser les GitHub Actions et la permission `Read and write permissions` si nécessaire dans `Settings > Actions > General`. Le workflow `Veille PFE 2027` est programmé quotidiennement ; le lancer manuellement une première fois dans l'onglet Actions.

**Limitations importantes :**
- Sans clés API, aucune nouvelle offre n'est extraite automatiquement : le site conserve le suivi manuel.
- L'API France Travail ne couvre pas exhaustivement LinkedIn, Welcome to the Jungle, Apec, stage.fr ni tous les sites carrières.
- Une annonce extraite n'est pas nécessairement un PFE à partir de février 2027 ; début, durée et éligibilité des étudiants étrangers sont signalés « à confirmer » lorsqu'ils ne sont pas explicitement établis.
- La détection des doublons s'appuie sur le lien ou le couple entreprise + titre + localisation. Les statuts locaux sont conservés lors des synchronisations.
- La page peut être publiée publiquement, mais **ne publiez jamais vos notes privées ou vos candidatures** dans `data/opportunities.json`, qui est un fichier public. Pour migrer vos statuts sur un autre ordinateur, utilisez Exporter / Importer.
- GitHub Pages et Actions pour les dépôts publics sont généralement gratuits, sous réserve des conditions de GitHub. L'accès à l'API France Travail doit être accordé.
- Github scheduled Actions peut être retardé ou désactivé après une longue période d'inactivité. Le workflow peut être relancé manuellement.

## Données du flux
`data/opportunities.json` reste volontairement vide initialement pour éviter d'inventer ou de recopier des liens non vérifiés. L'utilisateur peut ajouter de vraies annonces via l'interface, ou alimenter le JSON à partir de ses propres recherches.

