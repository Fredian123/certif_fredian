# -*- coding: utf-8 -*-
"""Point d'entree de l'utilitaire datatool."""

import sys
import json

import traitement


def LireFichier(chemin):
    f = open(chemin, "r")
    contenu = f.read()
    f.close()
    lignes = contenu.split("\n")
    enregs = []
    nb = 0
    for l in lignes:
        if nb == 0:
            nb = nb + 1
            continue
        if l == "":
            continue
        champs = l.split(";")
        try:
            val = float(champs[2])
        except Exception:
            val = -999
        e = {"site": champs[0], "capteur": champs[1], "valeur": val}
        enregs.append(e)
        nb = nb + 1
    return enregs


def afficherGroupes(donnees):
    groupes = traitement.regrouper(donnees, "site")
    for g in groupes:
        vals = []
        for m in g["membres"]:
            if m["valeur"] != -999:
                vals.append(m["valeur"])
        if len(vals) > 0:
            ind = traitement.indicateurs(vals)
            print(g["cle"], "->", len(g["membres"]), "mesures, moyenne", round(ind["moyenne"], 2))
        else:
            print(g["cle"], "-> aucune mesure valide")


def main():
    # 1. Analyse manuelle robuste des arguments
    json_path = None
    args = sys.argv[1:]
    
    if "--json" in args:
        idx = args.index("--json")
        if idx + 1 < len(args):
            json_path = args[idx + 1]
            args.pop(idx + 1)
            args.pop(idx)
        else:
            print("Erreur: L'option --json necessite un fichier de sortie.")
            return

    if len(args) < 1:
        print("usage: python datatool.py <fichier.csv> [seuil] [--json sortie.json]")
        return

    chemin_csv = args[0]
    try:
        donnees = LireFichier(chemin_csv)
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{chemin_csv}' est introuvable.")
        return

    # 2. Gestion du seuil optionnel
    if len(args) > 1:
        try:
            s = float(args[1])
            valeurs = []
            for e in donnees:
                if e["valeur"] != -999:
                    valeurs.append(e["valeur"])
            retenues = traitement.filtrer_par_seuil(valeurs, s)
            print(len(retenues), "valeurs retenues sur", len(valeurs))
        except ValueError:
            print("Erreur: Le seuil doit etre un nombre valide.")
            return

    # 3. Export JSON ou Affichage console
    if json_path:
        groupes = traitement.regrouper(donnees, "site")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(groupes, f, ensure_ascii=False, indent=4)
            print(f"Exportation JSON reussie dans : {json_path}")
        except Exception as e:
            print(f"Erreur lors de l'exportation JSON : {e}")
    else:
        afficherGroupes(donnees)


if __name__ == "__main__":
    main()
