# -*- coding: utf-8 -*-
"""Point d'entree de l'utilitaire datatool."""

import sys

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
    if len(sys.argv) < 2:
        print("usage: python datatool.py <fichier.csv> [seuil]")
        return
    donnees = LireFichier(sys.argv[1])
    if len(sys.argv) > 2:
        s = float(sys.argv[2])
        valeurs = []
        for e in donnees:
            if e["valeur"] != -999:
                valeurs.append(e["valeur"])
        retenues = traitement.filtrer_par_seuil(valeurs, s)
        print(len(retenues), "valeurs retenues sur", len(valeurs))
    afficherGroupes(donnees)


if __name__ == "__main__":
    main()
