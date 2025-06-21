import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import unicodedata
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from controller.extract_amazon_produit import extract_amazon_octopus

def click_button_with_selenium(driver, xpath, timeout=10):
    try:
        wait = WebDriverWait(driver, timeout)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        try:
            button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Erreur lors du clic sur le bouton : {e}")
        return False

def remove_accents(input_str):
    return ''.join(
        c for c in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(c) != 'Mn'
    )

def extract_category_by_name(driver, category_name):
    """
    Recherche la section de catégorie par son nom (sans accent) dans tous les menus visibles.
    Si non trouvée, tente de cliquer sur la catégorie parente puis réessaye.
    """
    try:
        cat_name_norm = remove_accents(category_name.lower())
        # Chercher toutes les sections de catégorie visibles dans tous les menus
        sections = driver.find_elements(By.XPATH, "//section[contains(@class, 'category-section')]")
        for section in sections:
            try:
                titre = section.find_element(By.CLASS_NAME, "hmenu-title").text.strip()
                titre_norm = remove_accents(titre.lower())
                if titre_norm == cat_name_norm:
                    sous_categories = []
                    for a in section.find_elements(By.CSS_SELECTOR, "ul li a.hmenu-item"):
                        nom = a.text.strip()
                        lien = a.get_attribute("href")
                        sous_categories.append((nom, lien))
                    return titre, sous_categories
            except Exception:
                continue
        # Si non trouvée, tenter de cliquer sur la catégorie parente (dans le menu principal)
        parent_xpath = f"//a[contains(@class, 'hmenu-item') and div[text()='{category_name}']]"
        try:
            if click_button_with_selenium(driver, parent_xpath, timeout=3):
                time.sleep(2)
                # Après le clic, de nouveaux menus apparaissent, on relance la recherche
                sections = driver.find_elements(By.XPATH, "//section[contains(@class, 'category-section')]")
                for section in sections:
                    try:
                        titre = section.find_element(By.CLASS_NAME, "hmenu-title").text.strip()
                        titre_norm = remove_accents(titre.lower())
                        if titre_norm == cat_name_norm:
                            sous_categories = []
                            for a in section.find_elements(By.CSS_SELECTOR, "ul li a.hmenu-item"):
                                nom = a.text.strip()
                                lien = a.get_attribute("href")
                                sous_categories.append((nom, lien))
                            return titre, sous_categories
                    except Exception:
                        continue
        except Exception:
            pass
        print(f"Catégorie '{category_name}' non trouvée.")
        return None, []
    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return None, []
    
# fonction pour sauvegarder les données de la catégorie dans un fichier JSON
def save_category_to_json(category_name, subcategories):
    """
    Sauvegarde les données de la catégorie dans un fichier JSON.
    Le nom du fichier est basé sur le nom de la catégorie (sans accents).
    """
    dossier = os.path.join(os.path.dirname(__file__), "..", r"resource\json")
    os.makedirs(dossier, exist_ok=True)
    filename = os.path.join(dossier, f"{remove_accents(category_name.lower()).replace(' ', '_')}.json")
    # filename = f"{remove_accents(category_name)}.json"
    data = {
        "category": category_name,
        "subcategories": [{"name": name, "link": link} for name, link in subcategories]
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {filename}")
    # return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_amazon_category.py 'Nom de la catégorie'")
        sys.exit(1)
    category_name = sys.argv[1]
    url = "https://www.amazon.fr/ref=nav_bb_logo"
    xpath_cookies = "//*[@id=\"a-autoid-0\"]"
    xpath_menu = "//*[@id=\"nav-hamburger-menu\"]"
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(2)
        click_button_with_selenium(driver, xpath_cookies)
        click_button_with_selenium(driver, xpath_menu)
        time.sleep(2)
        # Essayer de cliquer sur 'Tout afficher' si présent
        xpath_tout_afficher = "//a[contains(@aria-label, 'Afficher toutes les catégories')]"
        click_button_with_selenium(driver, xpath_tout_afficher, timeout=3)
        time.sleep(2)
        titre, sous_categories = extract_category_by_name(driver, category_name)
        if titre:
            print(f"Catégorie : {titre}")
            for nom, lien in sous_categories:
                print(f"- {nom} : {lien}")
            # Sauvegarde JSON via fonction dédiée
            save_category_to_json(titre, sous_categories)
        else:
            print("Aucune donnée extraite.")

        # Lancer l'extraction des produits de la catégorie
        for nom, lien in sous_categories:
            extract_amazon_octopus(titre, nom, lien)
        

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
