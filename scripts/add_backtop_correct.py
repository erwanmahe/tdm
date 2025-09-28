import os
import re

def add_backtop_to_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si le lien "Revenir en haut" existe déjà
    if 'Revenir en haut' in content:
        print(f"Le lien 'Revenir en haut' existe déjà dans {file_path}")
        return False
    
    # Vérifier si le fichier contient la balise </main>
    if '</main>' not in content:
        print(f"La balise </main> est manquante dans {file_path}")
        return False
    
    # Ajouter le lien avant la fermeture de la balise main
    new_content = content.replace('</main>', '        <p class="backtop"><a href="#top">Revenir en haut</a></p>\n      </main>')
    
    # Écrire le contenu modifié
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Lien 'Revenir en haut' ajouté à {file_path}")
    return True

def process_directory(directory):
    for root, _, files in os.walk(directory):
        if 'index.html' in files:
            file_path = os.path.join(root, 'index.html')
            try:
                add_backtop_to_file(file_path)
            except Exception as e:
                print(f"Erreur lors du traitement de {file_path}: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process_directory(base_dir)
    print("Traitement terminé.")
