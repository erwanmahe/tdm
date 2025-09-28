import os
import re

def add_backtop_to_texte_div(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si le lien "Revenir en haut" existe déjà
    if 'Revenir en haut' in content:
        print(f"Le lien 'Revenir en haut' existe déjà dans {file_path}")
        return False
    
    # Vérifier si le fichier contient une div de classe "texte"
    if 'class="texte"' not in content:
        print(f"Aucune div de classe 'texte' trouvée dans {file_path}")
        return False
    
    # Trouver la position de la fin de la div de classe "texte"
    texte_div_pattern = re.compile(r'(<div\s+class=["\']texte["\']>.*?)(</div>)', re.DOTALL)
    
    def add_backtop(match):
        # Récupérer le contenu actuel de la div
        div_content = match.group(1).rstrip()
        # Ajouter le lien avant la fermeture de la div
        return f"{div_content}\n          <p><a class=\"backtop\" href=\"#top\">Revenir en haut</a></p>\n        {match.group(2)}"
    
    # Remplacer la div de classe "texte" en ajoutant le lien
    new_content, count = texte_div_pattern.subn(add_backtop, content)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Lien 'Revenir en haut' ajouté dans la div 'texte' de {file_path}")
        return True
    else:
        print(f"Impossible d'ajouter le lien dans {file_path}")
        return False

def process_directory(directory):
    modified_count = 0
    for root, _, files in os.walk(directory):
        if 'index.html' in files:
            file_path = os.path.join(root, 'index.html')
            try:
                if add_backtop_to_texte_div(file_path):
                    modified_count += 1
            except Exception as e:
                print(f"Erreur lors du traitement de {file_path}: {e}")
    
    print(f"\nTraitement terminé. {modified_count} fichiers ont été modifiés.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process_directory(base_dir)
