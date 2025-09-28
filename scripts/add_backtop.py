import os
import re

def add_backtop_to_files(root_dir):
    # Modèle pour trouver la div de classe "texte"
    texte_div_pattern = re.compile(r'<div class="texte">.*?</div>', re.DOTALL)
    
    # Modèle pour vérifier si le lien "Revenir en haut" existe déjà
    backtop_pattern = re.compile(r'<a class="backtop" href="#top">Revenir en haut</a>')
    
    # Texte à ajouter
    backtop_html = '\n        \n    </div>'
    
    # Parcourir tous les fichiers HTML
    for root, dirs, files in os.walk(root_dir):
        if 'index.html' in files:
            file_path = os.path.join(root, 'index.html')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifier si le fichier contient déjà le lien
                if backtop_pattern.search(content):
                    print(f'OK: {file_path}')
                    continue
                
                # Trouver la div de classe "texte"
                match = texte_div_pattern.search(content)
                if match:
                    # Remplacer la balise de fermeture par notre nouveau contenu
                    new_content = content.replace('</div>', backtop_html, 1)
                    
                    # Écrire les modifications
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'AJOUTÉ: {file_path}')
                else:
                    print(f'PAS DE DIV TEXTE: {file_path}')
                    
            except Exception as e:
                print(f'ERREUR: {file_path} - {str(e)}')

if __name__ == '__main__':
    # Remplacer par le chemin de votre répertoire
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    add_backtop_to_files(base_dir)
    print("Traitement terminé.")
