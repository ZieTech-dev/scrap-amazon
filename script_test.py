import re

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

def convertir_urls_multiples(urls):
    """
    Convertit plusieurs URLs en une seule fois
    
    Args:
        urls (list): Liste des URLs à convertir
        
    Returns:
        list: Liste des URLs converties
    """
    return [convertir_url_amazon(url) for url in urls]

# Exemples d'utilisation
if __name__ == "__main__":
    # Test avec les exemples fournis
    urls_test = [
        'https://m.media-amazon.com/images/I/81PoGjMMHWL._AC._SR360,460.jpg',
        'https://m.media-amazon.com/images/I/716fxNpDtNL._AC._SR360,460.jpg'
    ]
    
    print("URLs d'origine:")
    for i, url in enumerate(urls_test, 1):
        print(f"{i}. {url}")
    
    print("\nURLs converties:")
    urls_converties = convertir_urls_multiples(urls_test)
    for i, url in enumerate(urls_converties, 1):
        print(f"{i}. {url}")
    
    print("\n" + "="*50)
    print("Test individuel:")
    
    # Test avec une seule URL
    url_exemple = 'https://m.media-amazon.com/images/I/81PoGjMMHWL._AC._SR360,460.jpg'
    url_convertie = convertir_url_amazon(url_exemple)
    
    print(f"Avant: {url_exemple}")
    print(f"Après: {url_convertie}")