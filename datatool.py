# -*- coding: utf-8 -*-
"""Point d'entree de l'utilitaire datatool."""

import sys
import json
import csv

import traitement


def LireFichier(chemin):
    """
    Lit un fichier CSV de mesures environnementales de manière sécurisée.
    
    Gestion des ressources (BCC3.1) : Utilise un gestionnaire de contexte 
    'with open' pour éviter toute fuite de descripteur.
    Validation de structure (Programmation défensive) : Ignore les lignes vides, 
    les en-têtes et les lignes ayant des champs critiques vides (site ou capteur),
    en écrivant des avertissements sur sys.stderr.
    
    :param chemin: Chemin vers le fichier CSV.
    :return: Liste de dictionnaires de la forme {"site": str, "capteur": str, "valeur": float}.
    """
    enregs = [] # Initialisation de la liste qui contiendra les enregistrements parsés
    
    # Ouverture sécurisée du fichier en lecture avec encodage UTF-8
    with open(chemin, "r", encoding="utf-8") as f:
        # splitlines() sépare le contenu par ligne et retire automatiquement les sauts de ligne (\n, \r)
        lignes = f.read().splitlines()
        
    nb = 0 # Compteur de lignes lues
    for idx, l in enumerate(lignes):
        if nb == 0:
            nb += 1
            continue  # Sauter la ligne d'en-tête (ex: site;capteur;valeur)
        if l.strip() == "":
            continue  # Sauter les lignes vides pour éviter les plantages
            
        # Découpage de la ligne par le séparateur point-virgule (;)
        champs = l.split(";")
        
        # Vérification du nombre minimal de colonnes attendu (3)
        if len(champs) < 3:
            sys.stderr.write(f"Avertissement ligne {idx + 1} : ligne incomplete {champs}\n")
            continue # Ligne malformée, passage à la ligne suivante
            
        # Nettoyage des espaces superflus autour de chaque champ
        site = champs[0].strip()
        capteur = champs[1].strip()
        val_str = champs[2].strip()
        
        # Programmation défensive : vérification de la présence des champs requis (site et capteur)
        if not site or not capteur:
            sys.stderr.write(f"Avertissement ligne {idx + 1} : le site ou le capteur est vide {champs}\n")
            continue # Donnée incomplète, passage à la ligne suivante
            
        # Conversion résiliente de la valeur de mesure (float)
        try:
            val = float(val_str)
        except ValueError:
            # Si la valeur n'est pas numérique ou vide, on la remplace par -999.0
            sys.stderr.write(f"Avertissement ligne {idx + 1} : valeur non_numerique '{val_str}' remplacee par -999.0\n")
            val = -999.0
            
        # Création du dictionnaire représentant la mesure et ajout à la liste
        e = {"site": site, "capteur": capteur, "valeur": val}
        enregs.append(e)
        nb += 1
        
    return enregs


def afficherGroupes(donnees):
    """
    Affiche les statistiques des groupes de mesures sur la console.
    """
    # Regroupement des mesures par la clé "site" (trié par ordre alphabétique)
    groupes = traitement.regrouper(donnees, "site")
    
    # Parcours de chaque groupe pour calculer et afficher ses statistiques
    for g in groupes:
        vals = [] # Liste temporaire pour stocker les mesures valides du groupe courant
        for m in g["membres"]:
            # On ignore les valeurs sentinelles -999.0 pour le calcul des indicateurs
            if m["valeur"] != -999.0:
                vals.append(m["valeur"])
                
        # S'il y a des mesures valides, on calcule et on affiche la moyenne
        if len(vals) > 0:
            ind = traitement.indicateurs(vals)
            # Affichage formaté : Nom_Site -> X mesures, moyenne Y.YY
            print(g["cle"], "->", len(g["membres"]), "mesures, moyenne", round(ind["moyenne"], 2))
        else:
            # Si aucune mesure valide n'est présente
            print(g["cle"], "-> aucune mesure valide")


def main():
    # 1. Analyse manuelle robuste des arguments en ligne de commande
    json_path = None
    args = sys.argv[1:] # On ignore le nom du script (sys.argv[0])
    
    # Recherche et extraction de l'option --json
    if "--json" in args:
        idx = args.index("--json")
        # On vérifie qu'il y a bien un argument après --json
        if idx + 1 < len(args):
            json_path = args[idx + 1] # Chemin du fichier JSON de sortie
            args.pop(idx + 1) # Suppression de la valeur du fichier de la liste des arguments
            args.pop(idx)     # Suppression du flag --json de la liste des arguments
        else:
            sys.stderr.write("Erreur: L'option --json necessite un fichier de sortie.\n")
            sys.exit(1) # Arrêt du script avec code d'erreur

    # Vérification qu'au moins le fichier CSV d'entrée est fourni
    if len(args) < 1:
        sys.stderr.write("usage: python datatool.py <fichier.csv> [seuil] [--json sortie.json]\n")
        sys.exit(1)

    # Récupération du chemin du fichier CSV à analyser
    chemin_csv = args[0]
    try:
        # Chargement et parsing du fichier CSV
        donnees = LireFichier(chemin_csv)
    except FileNotFoundError:
        # Gestion propre si le fichier spécifié n'existe pas
        sys.stderr.write(f"Erreur : Fichier CSV introuvable : '{chemin_csv}'\n")
        sys.exit(1)

    # 2. Gestion du seuil optionnel
    if len(args) > 1:
        try:
            s = float(args[1]) # Récupération et conversion du seuil
            valeurs = []
            # On isole toutes les valeurs de mesures qui ne sont pas invalides
            for e in donnees:
                if e["valeur"] != -999.0:
                    valeurs.append(e["valeur"])
            # Filtrage des valeurs supérieures ou égales au seuil
            retenues = traitement.filtrer_par_seuil(valeurs, s)
            # Affichage du nombre de valeurs qui dépassent le seuil
            print(f"{len(retenues)} valeurs retenues sur {len(valeurs)}")
        except ValueError:
            sys.stderr.write("Erreur: Le seuil doit etre un nombre valide.\n")
            sys.exit(1)

    # 3. Export JSON ou Affichage console selon les options passées
    if json_path:
        # Regroupement des données par site avant export
        groupes = traitement.regrouper(donnees, "site")
        try:
            # Écriture structurée dans le fichier JSON ciblé
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(groupes, f, ensure_ascii=False, indent=4)
            print(f"Exportation JSON reussie dans : {json_path}")
        except Exception as e:
            # Gestion d'erreur d'écriture (ex: permission refusée, dossier inexistant)
            sys.stderr.write(f"Erreur lors de l'exportation JSON : {e}\n")
            sys.exit(1)
    else:
        # Si aucun fichier JSON n'est spécifié, affichage des statistiques sur la console
        afficherGroupes(donnees)


if __name__ == "__main__":
    main()