# -*- coding: utf-8 -*-
"""Point d'entree de l'utilitaire datatool."""

import sys
import json
import traitement  # Assurez-vous que traitement.py est dans le même dossier


def LireFichier(chemin):
    """Lit un fichier CSV et retourne une liste de dictionnaires."""
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()
    lignes = contenu.split("\n")
    enregs = []
    nb = 0
    for l in lignes:
        if nb == 0:          # sauter l'en-tête
            nb += 1
            continue
        if l == "":
            continue
        champs = l.split(";")
        if len(champs) < 3 or champs[0] == "" or champs[1] == "":
            # Ligne malformée : on ignore silencieusement (ou on pourrait logger)
            continue
        try:
            val = float(champs[2])
        except Exception:
            val = -999.0   # valeur par défaut pour les données invalides
        e = {"site": champs[0], "capteur": champs[1], "valeur": val}
        enregs.append(e)
        nb += 1
    return enregs


def afficherGroupes(donnees):
    """Affiche les groupes par site avec le nombre de mesures et la moyenne."""
    groupes = traitement.regrouper(donnees, "site")
    for g in groupes:
        vals = [m["valeur"] for m in g["membres"] if m["valeur"] != -999]
        if vals:
            ind = traitement.indicateurs(vals)
            print(g["cle"], "->", len(g["membres"]), "mesures, moyenne", round(ind["moyenne"], 2))
        else:
            print(g["cle"], "-> aucune mesure valide")


def main():
    # Analyse des arguments
    args = sys.argv[1:]
    json_path = None

    if "--json" in args:
        idx = args.index("--json")
        if idx + 1 < len(args):
            json_path = args[idx + 1]
            args.pop(idx + 1)
            args.pop(idx)
        else:
            print("Erreur: L'option --json necessite un fichier de sortie.")
            return

    if len(args) == 0:
        print("Erreur: vous devez fournir le chemin du fichier CSV en argument.")
        return

    chemin_csv = args[0]

    try:
        donnees = LireFichier(chemin_csv)
    except FileNotFoundError:
        print(f"Erreur: le fichier '{chemin_csv}' est introuvable.")
        return

    # Gestion du seuil optionnel
    if len(args) > 1:
        try:
            s = float(args[1])
            valeurs = [e["valeur"] for e in donnees if e["valeur"] != -999]
            retenues = traitement.filtrer_par_seuil(valeurs, s)
            print(len(retenues), "valeurs retenues sur", len(valeurs))
        except ValueError:
            print("Erreur: le seuil doit être un nombre valide.")
            return

    # Export JSON ou affichage console
    if json_path:
        groupes = traitement.regrouper(donnees, "site")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(groupes, f, ensure_ascii=False, indent=4)
            print(f"Exportation JSON réussie dans : {json_path}")
        except Exception as e:
            print(f"Erreur lors de l'exportation JSON : {e}")
    else:
        afficherGroupes(donnees)


if __name__ == "__main__":
    main()