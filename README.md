# Scrap Amazon (Catégories & Produits)

Ce projet permet d'extraire automatiquement les sous-catégories et les produits (avec images, prix, etc.) depuis Amazon.fr, en organisant les résultats dans des fichiers CSV, Excel et en téléchargeant les images dans des dossiers structurés.

## Prérequis
- Python 3.8+
- Google Chrome (ou Firefox, à adapter dans le code)
- [ChromeDriver](https://chromedriver.chromium.org/downloads) compatible avec votre version de Chrome (doit être dans le PATH ou dans le dossier du projet)

## Installation
1. Clonez ce dépôt ou téléchargez les fichiers.
2. Installez les dépendances Python :

```bash
pip install -r requirements.txt
```

## Utilisation

### Extraction d'une catégorie Amazon

Pour extraire toutes les sous-catégories et les produits d'une catégorie Amazon :

```bash
cd controller
python extract_amazon_category.py "Nom de la catégorie"
```

Exemple :
```bash
python extract_amazon_category.py "Livres"
```

- Les sous-catégories et leurs liens sont extraits et sauvegardés en JSON dans `resource/json/`.
- Pour chaque sous-catégorie, les produits "meilleures ventes" sont extraits, et les résultats sont enregistrés dans :
  - `resource/csv/<categorie>/<souscategorie>.csv`
  - `resource/xlsx/<categorie>/<souscategorie>.xlsx`
  - Les images dans `media/<categorie>/<souscategorie>/`

### Utilisation en tant que module

Vous pouvez importer la fonction d'extraction produit dans vos propres scripts :

```python
from controller.extract_amazon_produit import extract_amazon_octopus
extract_amazon_octopus("Informatique et bureau", "Réseaux", "https://www.amazon.fr/gp/browse.html?node=427941031&ref_=nav_em__compo_0_2_14_7")
```

## Personnalisation
- Modifiez les variables `categorie`, `sousCategorie` et `url` pour cibler la catégorie/sous-catégorie de votre choix.
- Le code gère automatiquement l'organisation des fichiers et dossiers.

## Limitations
- Le scraping Amazon peut être bloqué par des captchas ou des changements de structure du site.
- Utilisation à des fins personnelles ou éducatives uniquement.

## Dépendances principales
- selenium
- openpyxl
- requests

## Auteurs
- PaulEm
---

N'hésitez pas à ouvrir une issue pour toute question ou amélioration !
