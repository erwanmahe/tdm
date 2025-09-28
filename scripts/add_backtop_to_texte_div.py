import os
import re

def needs_backtop(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si le fichier contient le lien "Revenir en haut"
    if 'Revenir en haut' in content:
        return False
    
    # Vérifier si le fichier contient une div de classe "texte"
    if 'class="texte"' not in content:
        return False
        
    return True

def add_backtop_to_texte_div(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Trouver la position de la fin de la div de classe "texte"
    texte_div_pattern = re.compile(r'(<div\s+class=["\']texte["\']>.*?)(</div>)', re.DOTALL)
    
    def add_backtop(match):
        # Si le contenu de la div se termine déjà par un paragraphe, on ajoute avant
        content = match.group(1).rstrip()
        if content.endswith('</p>'):
            return f"{content}\n          <p><a class=\"backtop\" href=\"#top\">Revenir en haut</a></p>\n        {match.group(2)}"
        # Sinon, on ajoute le paragraphe directement avant la fermeture de la div
        else:
            return f"{content}\n          <p><a class=\"backtop\" href=\"#top\">Revenir en haut</a></p>\n        {match.group(2)}"
    
    # Remplacer la div de classe "texte" en ajoutant le lien
    new_content, count = texte_div_pattern.subn(add_backtop, content)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Lien 'Revenir en haut' ajouté à {file_path}")
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
                if needs_backtop(file_path):
                    if add_backtop_to_texte_div(file_path):
                        modified_count += 1
            except Exception as e:
                print(f"Erreur lors du traitement de {file_path}: {e}")
    
    print(f"\nTraitement terminé. {modified_count} fichiers ont été modifiés.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process_directory(base_dir)
