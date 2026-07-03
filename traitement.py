# -*- coding: utf-8 -*-
"""
Module traitement.py - Fonctions de traitement et d'analyse des données de mesures.
Ce module contient la logique métier pure de l'utilitaire datatool.

Conforme aux principes de programmation défensive et de haute qualité (BCC3 / BCC5).
"""

# =====================================================================
# 1. Gestion des exceptions personnalisées (BCC3.1 - Robustesse)
# =====================================================================

class DataToolError(Exception):
    """Exception de base pour toutes les erreurs de l'utilitaire datatool."""
    pass


class InvalidDataError(DataToolError):
    """Exception levée lorsque les données à traiter sont invalides ou malformées."""
    pass


# =====================================================================
# 2. Fonctions de traitement métier pures
# =====================================================================

def filtrer_par_seuil(valeurs, seuil):
    """
    Filtre une liste de valeurs numériques selon un seuil (supérieur ou égal).
    
    Programmation défensive : vérification des types et des valeurs d'entrée.
    
    :param valeurs: Liste ou itérable de nombres (float/int).
    :param seuil: Valeur numérique de seuil de filtrage.
    :return: Une nouvelle liste contenant les valeurs >= seuil.
    :raises InvalidDataError: Si les entrées sont de types incorrects.
    """
    if not isinstance(valeurs, (list, tuple, set)):
        raise InvalidDataError("Le paramètre 'valeurs' doit être un conteneur (liste, tuple, set).")
    
    try:
        seuil_val = float(seuil)
    except (ValueError, TypeError) as err:
        raise InvalidDataError(f"Le seuil '{seuil}' doit être une valeur numérique convertible en float : {err}")
    
    resultat = []
    for idx, v in enumerate(valeurs):
        try:
            val_num = float(v)
            if val_num >= seuil_val:
                resultat.append(val_num)
        except (ValueError, TypeError) as err:
            raise InvalidDataError(
                f"La valeur à l'index {idx} ('{v}') n'est pas numérique : {err}"
            )
            
    return resultat


def regrouper(enregistrements, cle):
    """
    Regroupe une liste de dictionnaires selon la valeur d'une clé.
    
    Les groupes retournés sont triés par clé croissante (ordre alphabétique).
    
    Complexité Algorithmique (BCC5.4) :
    - N : Nombre d'enregistrements.
    - K : Nombre de groupes (clés uniques). En général K << N.
    - Étape 1 (Regroupement) : On parcourt chaque enregistrement une seule fois.
      L'insertion dans le dictionnaire se fait en temps constant moyen O(1) grâce à la table de hachage.
      Cette étape est donc de complexité temporelle O(N) et spatiale O(N).
    - Étape 2 (Tri et formatage) : On récupère les K clés uniques et on les trie.
      Le tri en Python (Timsort) prend O(K log K) en temps.
    - Complexité globale : Temps O(N + K log K), Espace O(N).
    Cette implémentation élimine tout risque de doublons de mesures et de lenteur quadratique (O(N^2)).
    
    :param enregistrements: Liste de dictionnaires (ex: retour de LireFichier).
    :param cle: Clé de regroupement (ex: "site").
    :return: Liste de dictionnaires sous la forme [{"cle": k, "membres": [...]}, ...] triée par clé.
    :raises InvalidDataError: Si les enregistrements sont malformés ou si la clé est absente.
    """
    if not isinstance(enregistrements, (list, tuple)):
        raise InvalidDataError("Le paramètre 'enregistrements' doit être une liste ou un tuple.")
    
    groupes_dict = {}
    
    for idx, e in enumerate(enregistrements):
        if not isinstance(e, dict):
            raise InvalidDataError(f"L'enregistrement à l'index {idx} n'est pas un dictionnaire.")
        if cle not in e:
            raise InvalidDataError(f"Clé '{cle}' absente de l'enregistrement à l'index {idx} : {e}")
        
        k = e[cle]
        if k not in groupes_dict:
            groupes_dict[k] = []
        groupes_dict[k].append(e)
    
    groupes = []
    # Tri par clé croissante pour garantir un ordre prévisible et conforme
    for k in sorted(groupes_dict.keys()):
        groupes.append({"cle": k, "membres": groupes_dict[k]})
        
    return groupes


def indicateurs(valeurs):
    """
    Calcule des indicateurs statistiques (moyenne, minimum et maximum) d'une liste non vide.
    
    Programmation défensive : vérification que la liste n'est pas vide et validation des données.
    
    :param valeurs: Liste non vide de valeurs numériques.
    :return: Dictionnaire contenant {"moyenne": float, "min": float, "max": float}
    :raises InvalidDataError: Si la liste est vide ou si les données ne sont pas numériques.
    """
    if not valeurs:
        raise InvalidDataError("Impossible de calculer des indicateurs sur une liste de valeurs vide.")
    
    total = 0.0
    try:
        mini = float(valeurs[0])
        maxi = float(valeurs[0])
    except (ValueError, TypeError, IndexError) as err:
        raise InvalidDataError(f"La première valeur n'est pas numérique ou valide : {err}")
        
    for idx, v in enumerate(valeurs):
        try:
            val_num = float(v)
            total += val_num
            if val_num < mini:
                mini = val_num
            if val_num > maxi:
                maxi = val_num
        except (ValueError, TypeError) as err:
            raise InvalidDataError(
                f"La valeur à l'index {idx} ('{v}') n'est pas une valeur numérique valide : {err}"
            )
            
    return {
        "moyenne": total / len(valeurs), 
        "min": mini, 
        "max": maxi
    }
