# Site Tour du Monde

## Commande de generation

```bash
python3 tools/build_static.py
```

## Appliquer le thème (optionnel)

Pour améliorer le rendu (police Roboto, style Material, lightbox pour les images, et petits raffinements UI), exécutez l'outil de thématisation après la génération du site statique.

```bash
python3 tools/apply_theme.py
```

Cela post-traite les fichiers `static_site/*.html` pour injecter les feuilles de style et scripts depuis `static_site/assets/` sans modifier `tools/build_static.py`.
