import os
import re

def replace_in_files(root_dir):
    # Parcourir tous les fichiers et dossiers
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Lire le contenu du fichier
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remplacer le texte
                    new_content = content.replace('>Voyages<', '>La carte<')
                    
                    # Si le contenu a changé, écrire les modifications
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f'Mis à jour: {file_path}')
                        
                except Exception as e:
                    print(f'Erreur lors du traitement de {file_path}: {str(e)}')

if __name__ == '__main__':
    # Remplacer par le chemin de votre répertoire
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    replace_in_files(base_dir)
    print("Remplacement terminé.")
