import os
import re

def remove_dashes_from_files(root_dir):
    # Parcourir tous les fichiers et dossiers
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Lire le contenu du fichier
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Supprimer les lignes contenant uniquement "---"
                    new_lines = [line for line in lines if line.strip() != '---']
                    
                    # Si le contenu a changé, écrire les modifications
                    if len(new_lines) != len(lines):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        print(f'Mis à jour: {file_path}')
                        
                except Exception as e:
                    print(f'Erreur lors du traitement de {file_path}: {str(e)}')

if __name__ == '__main__':
    # Remplacer par le chemin de votre répertoire
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    remove_dashes_from_files(base_dir)
    print("Nettoyage terminé.")
