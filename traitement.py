# -*- coding: utf-8 -*-
"""Fonctions de traitement des donnees."""


def filtrer_par_seuil(valeurs, seuil):
    """Filtre une liste de valeurs numeriques selon un seuil (superieur ou egal)."""
    resultat = []
    for v in valeurs:
        if v >= seuil:
            resultat.append(v)
    return resultat


def regrouper(enregistrements, cle):
    """Regroupe une liste de dictionnaires selon la valeur d'une cle et trie par cle croissante."""
    groupes_dict = {}
    for e in enregistrements:
        k = e[cle]
        if k not in groupes_dict:
            groupes_dict[k] = []
        groupes_dict[k].append(e)
    
    groupes = []
    for k in sorted(groupes_dict.keys()):
        groupes.append({"cle": k, "membres": groupes_dict[k]})
    return groupes


def indicateurs(valeurs):
    """Calcule moyenne, minimum et maximum d'une liste non vide."""
    total = 0
    mini = valeurs[0]
    maxi = valeurs[0]
    for v in valeurs:
        total += v
        if v < mini:
            mini = v
        if v > maxi:
            maxi = v
    return {"moyenne": total / len(valeurs), "min": mini, "max": maxi}
