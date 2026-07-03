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
    # Validation du type du conteneur de valeurs
    if not isinstance(valeurs, (list, tuple, set)):
        raise InvalidDataError("Le paramètre 'valeurs' doit être un conteneur (liste, tuple, set).")
    
    # Tentative de conversion sécurisée du seuil en float
    try:
        seuil_val = float(seuil)
    except (ValueError, TypeError) as err:
        raise InvalidDataError(f"Le seuil '{seuil}' doit être une valeur numérique convertible en float : {err}")
    
    resultat = [] # Liste pour accumuler les valeurs filtrées
    # Parcours des valeurs pour appliquer le filtre de programmation défensive
    for idx, v in enumerate(valeurs):
        try:
            val_num = float(v) # Conversion en float de la valeur courante
            # Comparaison inclusive (supérieur ou égal)
            if val_num >= seuil_val:
                resultat.append(val_num)
        except (ValueError, TypeError) as err:
            # Si un élément n'est pas convertible en float
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
    # Validation du type du conteneur d'enregistrements
    if not isinstance(enregistrements, (list, tuple)):
        raise InvalidDataError("Le paramètre 'enregistrements' doit être une liste ou un tuple.")
    
    groupes_dict = {} # Table de hachage pour un regroupement en O(N)
    
    # Parcours linéaire pour alimenter la table de hachage
    for idx, e in enumerate(enregistrements):
        # Validation que l'élément est bien un dictionnaire
        if not isinstance(e, dict):
            raise InvalidDataError(f"L'enregistrement à l'index {idx} n'est pas un dictionnaire.")
        # Validation que la clé demandée existe dans l'enregistrement courant
        if cle not in e:
            raise InvalidDataError(f"Clé '{cle}' absente de l'enregistrement à l'index {idx} : {e}")
        
        k = e[cle] # Récupération de la valeur de la clé de regroupement
        # Si la clé n'existe pas encore dans notre dictionnaire de groupes, on l'initialise
        if k not in groupes_dict:
            groupes_dict[k] = []
        # Ajout de l'enregistrement courant à son groupe de manière linéaire et unique (pas de doublon)
        groupes_dict[k].append(e)
    
    groupes = [] # Liste finale formatée
    # Tri par clé croissante pour garantir un ordre prévisible et conforme, complexité O(K log K)
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
    # Validation du cas limite : conteneur de valeurs vide
    if not valeurs:
        raise InvalidDataError("Impossible de calculer des indicateurs sur une liste de valeurs vide.")
    
    total = 0.0 # Somme cumulée
    # Tentative d'initialisation du min et du max avec le premier élément
    try:
        mini = float(valeurs[0])
        maxi = float(valeurs[0])
    except (ValueError, TypeError, IndexError) as err:
        raise InvalidDataError(f"La première valeur n'est pas numérique ou valide : {err}")
        
    # Parcours des valeurs pour calculer simultanément les statistiques en un seul passage O(N)
    for idx, v in enumerate(valeurs):
        try:
            val_num = float(v) # Conversion en float de la valeur courante
            total += val_num   # Accumulation pour le calcul de la moyenne
            # Mise à jour du minimum
            if val_num < mini:
                mini = val_num
            # Mise à jour du maximum
            if val_num > maxi:
                maxi = val_num
        except (ValueError, TypeError) as err:
            # Si un élément n'est pas numérique ou vide
            raise InvalidDataError(
                f"La valeur à l'index {idx} ('{v}') n'est pas une valeur numérique valide : {err}"
            )
            
    # Retourne les statistiques sous forme de dictionnaire
    return {
        "moyenne": total / len(valeurs), 
        "min": mini, 
        "max": maxi
    }
