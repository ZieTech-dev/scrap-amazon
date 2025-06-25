import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import webbrowser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
from openpyxl import Workbook
import requests
import unicodedata
import re

import html

# définir une fonction qui va cliquer sur un bouton avec selenium à partir de son xpath
def click_button_with_selenium(driver, xpath, timeout=10):
    """
    Tente de cliquer sur un bouton. Retourne True si succès, False sinon.
    Attend que le bouton soit cliquable. Essaie aussi un clic JavaScript si le clic normal échoue.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        try:
            button.click()
        except Exception as e:
            print(f"Clic classique échoué, tentative via JavaScript : {e}")
            driver.execute_script("arguments[0].click();", button)
        print(f"Bouton cliqué avec succès : {xpath}")
        time.sleep(2)  # Attendre un peu pour voir le résultat du clic
        return True
    except Exception as e:
        print(f"Erreur lors du clic sur le bouton : {e}")
        return False

def extract_octopus_best_seller_products(driver):
    """
    Extrait les produits de la section 'octopus-pc-card' (meilleures ventes) sur Amazon.
    Retourne une liste de dictionnaires avec les infos principales.
    """

    def convertir_url_amazon(url):
        """
        Convertit une URL d'image Amazon du format _SR360,460 vers _SX679_
        
        Args:
            url (str): URL d'origine au format _SR360,460
            
        Returns:
            str: URL convertie au format _SX679_
        """
        # Pattern pour matcher _AC._SR360,460 et le remplacer par _AC_SX679_
        pattern = r'_AC\._SR\d+,\d+'
        replacement = '_AC_SX679_'
        
        # Effectuer la substitution
        nouvelle_url = re.sub(pattern, replacement, url)
        
        return nouvelle_url

    produits = []
    try:
        # Attendre que la section soit présente
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.octopus-pc-card.octopus-best-seller-card'))
        )
        time.sleep(2)  # Attendre un peu pour que la section se charge complètement
        items = section.find_elements(By.CSS_SELECTOR, 'li.octopus-pc-item')
        for item in items:
            time.sleep(0.5)  # Pour éviter de surcharger le serveur avec trop de requêtes
            try:
                # Lien et titre
                a_tag = item.find_element(By.CSS_SELECTOR, 'a.octopus-pc-item-link')
                nom = a_tag.get_attribute('title') or a_tag.text
                lien = a_tag.get_attribute('href')
                # Image
                try:
                    img = item.find_element(By.CSS_SELECTOR, 'img.octopus-pc-item-image')
                    image = img.get_attribute('src')
                    image = convertir_url_amazon(image)
                except:
                    image = ''
                # Prix
                try:
                    prix = item.find_element(By.CSS_SELECTOR, 'span.a-price > span.a-offscreen').text
                except:
                    prix = ''
                # Prix barré
                try:
                    prix_barre = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-strike-price span.a-text-strike').text
                except:
                    prix_barre = ''
                # Nombre d'avis
                try:
                    nb_avis = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-review-star span.a-size-mini').text
                except:
                    nb_avis = ''
                # Note
                try:
                    note = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-review-star span.a-icon-alt').text
                except:
                    note = ''
                produits.append({
                    'nom': nom.strip(),
                    'lien': lien,
                    'image': image,
                    'prix': prix,
                    'prix_barre': prix_barre,
                    'nb_avis': nb_avis,
                    'note': note
                })
            except Exception as e:
                print(f"Erreur extraction produit octopus: {e}")
    except Exception as e:
        print(f"Section octopus non trouvée: {e}")
    return produits

def extract_all_octopus_sections(driver):
    """
    Extrait toutes les sections octopus (meilleures ventes, etc.) avec leur titre et leurs produits.
    Retourne une liste de dicts : { 'titre': str, 'produits': [dict, ...] }
    """

    def convertir_url_amazon(url):
        """
        Convertit une URL d'image Amazon du format _SR360,460 vers _SX679_
        
        Args:
            url (str): URL d'origine au format _SR360,460
            
        Returns:
            str: URL convertie au format _SX679_
        """
        # Pattern pour matcher _AC._SR360,460 et le remplacer par _AC_SX679_
        pattern = r'_AC\._SR\d+,\d+'
        replacement = '_AC_SX679_'
        
        # Effectuer la substitution
        nouvelle_url = re.sub(pattern, replacement, url)
        
        return nouvelle_url


    def nettoyer_titre(titre):
        """
        Nettoie un titre en décodant les entités HTML et en corrigeant les caractères mal encodés
        
        Args:
            titre (str): Titre à nettoyer
            
        Returns:
            str: Titre nettoyé
        """
        # Étape 1: Décoder les entités HTML standard
        titre_nettoye = html.unescape(titre)
        
        # Étape 2: Corriger les entités HTML mal encodées courantes
        corrections = {
            '&amp;#39;': "'",           # Apostrophe mal encodée
            '&#39;': "'",              # Apostrophe HTML
            '&amp;quot;': '"',         # Guillemets mal encodés
            '&#34;': '"',              # Guillemets HTML
            '&amp;amp;': '&',          # Esperluette mal encodée
            '&amp;lt;': '<',           # Inférieur mal encodé
            '&amp;gt;': '>',           # Supérieur mal encodé
            '&amp;#034;': '"',         # Autre forme de guillemets
            '&amp;#8217;': "'",        # Apostrophe typographique
            '&amp;#8220;': '"',        # Guillemet ouvrant
            '&amp;#8221;': '"',        # Guillemet fermant
            '&amp;#8211;': '–',        # Tiret en
            '&amp;#8212;': '—',        # Tiret em
            '&amp;nbsp;': ' ',         # Espace insécable
        }
        
        # Appliquer les corrections
        for mauvais, bon in corrections.items():
            titre_nettoye = titre_nettoye.replace(mauvais, bon)
        
        # Étape 3: Nettoyer les doubles apostrophes consécutives
        titre_nettoye = re.sub(r"'{2,}", "'", titre_nettoye)
        
        # Étape 4: Nettoyer les espaces multiples
        titre_nettoye = re.sub(r'\s+', ' ', titre_nettoye)
        
        # Étape 5: Supprimer les espaces en début et fin
        titre_nettoye = titre_nettoye.strip()
        
        return titre_nettoye


    sections = []
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.octopus-pc-card.octopus-best-seller-card')
        for card in cards:
            try:
                # Titre de la section
                titre = card.find_element(By.CSS_SELECTOR, 'div.octopus-pc-card-title span.a-size-extra-large').text.strip()
            except:
                titre = ''
            produits = []
            items = card.find_elements(By.CSS_SELECTOR, 'li.octopus-pc-item')
            for item in items:
                try:
                    a_tag = item.find_element(By.CSS_SELECTOR, 'a.octopus-pc-item-link')
                    nom = a_tag.get_attribute('title') or a_tag.text
                    nom = nettoyer_titre(nom)  # Nettoyer le titre
                    lien = a_tag.get_attribute('href')
                    try:
                        img = item.find_element(By.CSS_SELECTOR, 'img.octopus-pc-item-image')
                        image = img.get_attribute('src')
                        image = convertir_url_amazon(image)
                    except:
                        image = ''
                    try:
                        prix = item.find_element(By.CSS_SELECTOR, 'span.a-price > span.a-offscreen').text
                    except:
                        prix = ''
                    try:
                        prix_barre = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-strike-price span.a-text-strike').text
                    except:
                        prix_barre = ''
                    try:
                        nb_avis = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-review-star span.a-size-mini').text
                    except:
                        nb_avis = ''
                    try:
                        note = item.find_element(By.CSS_SELECTOR, 'div.octopus-pc-asin-review-star span.a-icon-alt').text
                    except:
                        note = ''
                    produits.append({
                        'nom': nom.strip(),
                        'lien': lien,
                        'image': image,
                        'prix': prix,
                        'prix_barre': prix_barre,
                        'nb_avis': nb_avis,
                        'note': note
                    })
                except Exception as e:
                    print(f"Erreur extraction produit octopus: {e}")
            sections.append({'titre': titre, 'produits': produits})
    except Exception as e:
        print(f"Erreur lors de l'extraction des sections octopus: {e}")
    return sections

def save_octopus_sections_to_csv(sections, filepath):
    """
    Sauvegarde toutes les sections octopus et leurs produits dans un fichier CSV.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['section', 'nom', 'lien', 'image', 'prix', 'prix_barre', 'nb_avis', 'note']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for section in sections:
            titre = section['titre']
            for prod in section['produits']:
                row = {'section': titre}
                row.update(prod)
                writer.writerow(row)

def save_octopus_sections_to_xlsx(sections, filepath):
    """
    Sauvegarde toutes les sections octopus et leurs produits dans un fichier Excel (.xlsx).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.append(['section', 'nom', 'lien', 'image', 'prix', 'prix_barre', 'nb_avis', 'note'])
    for section in sections:
        titre = section['titre']
        for prod in section['produits']:
            ws.append([
                titre,
                prod.get('nom', ''),
                prod.get('lien', ''),
                prod.get('image', ''),
                prod.get('prix', ''),
                prod.get('prix_barre', ''),
                prod.get('nb_avis', ''),
                prod.get('note', '')
            ])
    wb.save(filepath)

def download_images_from_csv(csv_path, media_dir):
    """
    Lit le fichier CSV, télécharge les images (colonne 'image') dans le dossier media.
    """
    os.makedirs(media_dir, exist_ok=True)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('image', '').strip()
            if url:
                # Nom de fichier basé sur le nom du produit ou l'URL
                nom = row.get('nom', '').strip().replace(' ', '_').replace('/', '_')
                ext = os.path.splitext(url)[1].split('?')[0]
                if not ext or len(ext) > 5:
                    ext = '.jpg'
                filename = f"{nom[:50]}{ext}"
                filepath = os.path.join(media_dir, filename)
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(r.content)
                        print(f"Image téléchargée : {filepath}")
                    else:
                        print(f"Erreur téléchargement image : {url}")
                except Exception as e:
                    print(f"Erreur téléchargement image {url} : {e}")

def clean_name(name):
    """Nettoie un nom pour l'utiliser dans un chemin de fichier/dossier : minuscules, sans accents, sans espaces ni caractères spéciaux."""
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
    name = name.lower().replace(' ', '_')
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    return name

def extract_amazon_octopus(categorie, sousCategorie, url):
    """
    Extrait les sections octopus d'une page Amazon et sauvegarde CSV/XLSX/images selon la logique demandée.
    """
    cat_clean = clean_name(categorie)
    souscat_clean = clean_name(sousCategorie)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'resource', 'csv', cat_clean, f'{souscat_clean}.csv')
    xlsx_path = os.path.join(base_dir, 'resource', 'xlsx', cat_clean, f'{souscat_clean}.xlsx')
    media_dir = os.path.join(base_dir, 'media', cat_clean, souscat_clean)
    xpath = "//*[@id=\"sp-cc-accept\"]"
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(5)
        if click_button_with_selenium(driver, xpath):
            print("Bouton 'accepter les cookies' cliqué avec succès.")
        else:
            print("Échec du clic sur le bouton 'accepter les cookies'.")
        sections = extract_all_octopus_sections(driver)
        print("\nSections octopus extraites :")
        for section in sections:
            print(f"Section : {section['titre']}")
            for prod in section['produits']:
                print(prod)
        save_octopus_sections_to_csv(sections, csv_path)
        print(f"\nDonnées enregistrées dans {csv_path}")
        save_octopus_sections_to_xlsx(sections, xlsx_path)
        print(f"Données enregistrées dans {xlsx_path}")
        download_images_from_csv(csv_path, media_dir)
    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
    finally:
        print("Fermeture du navigateur.")
        driver.quit()

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation importable
    categorie = "Informatique et bureau"
    sousCategorie = "Réseaux"
    url = "https://www.amazon.fr/gp/browse.html?node=427941031&ref_=nav_em__compo_0_2_14_7"
    extract_amazon_octopus(categorie, sousCategorie, url)
