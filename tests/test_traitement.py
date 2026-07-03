# -*- coding: utf-8 -*-
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import traitement


class TestTraitement(unittest.TestCase):

    # =====================================================================
    # 1. Tests de filtrer_par_seuil
    # =====================================================================

    def test_filtrer_par_seuil(self):
        """Cas nominal : filtrage de valeurs numériques."""
        res = traitement.filtrer_par_seuil([1, 5, 10], 4)
        self.assertEqual(res, [5.0, 10.0])

    def test_filtrer_par_seuil_inclusif(self):
        """Cas limite : la valeur égale au seuil (4) doit être incluse."""
        res = traitement.filtrer_par_seuil([1, 4, 10], 4)
        self.assertEqual(res, [4.0, 10.0])

    def test_filtrer_par_seuil_types_invalides(self):
        """Cas d'erreur : valeurs de type incorrect."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.filtrer_par_seuil("pas_une_liste", 4)

    def test_filtrer_par_seuil_valeurs_non_numeriques(self):
        """Cas d'erreur : élément non convertible dans la liste."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.filtrer_par_seuil([1, "texte_invalide", 10], 4)

    def test_filtrer_par_seuil_seuil_invalide(self):
        """Cas d'erreur : seuil non convertible en float."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.filtrer_par_seuil([1, 5, 10], "seuil_texte")


    # =====================================================================
    # 2. Tests de indicateurs
    # =====================================================================

    def test_indicateurs(self):
        """Cas nominal : calcul sur des valeurs correctes."""
        ind = traitement.indicateurs([2, 4, 6])
        self.assertEqual(ind["moyenne"], 4.0)
        self.assertEqual(ind["min"], 2.0)
        self.assertEqual(ind["max"], 6.0)

    def test_indicateurs_liste_vide(self):
        """Cas d'erreur (limite) : liste vide."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.indicateurs([])

    def test_indicateurs_valeurs_non_numeriques(self):
        """Cas d'erreur : liste contenant des valeurs non numériques."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.indicateurs([2, "erreur", 6])


    # =====================================================================
    # 3. Tests de regrouper
    # =====================================================================

    def test_regrouper_sans_doublons(self):
        """Cas nominal : vérifie qu'il n'y a pas de doublons créés lors du regroupement."""
        donnees = [
            {"site": "Nord", "capteur": "C1", "valeur": 12.5},
            {"site": "Nord", "capteur": "C2", "valeur": 8.0},
        ]
        groupes = traitement.regrouper(donnees, "site")
        # Il ne doit y avoir qu'un seul groupe (Nord)
        self.assertEqual(len(groupes), 1)
        self.assertEqual(groupes[0]["cle"], "Nord")
        # Ce groupe doit contenir exactement les 2 mesures d'origine (sans doublon)
        self.assertEqual(len(groupes[0]["membres"]), 2)

    def test_regrouper_tri_croissant(self):
        """Cas nominal : vérifie que les groupes sont triés par ordre alphabétique de clé."""
        donnees = [
            {"site": "Sud", "capteur": "C1", "valeur": 15.2},
            {"site": "Nord", "capteur": "C1", "valeur": 12.5},
            {"site": "Ouest", "capteur": "C3", "valeur": 9.0},
        ]
        groupes = traitement.regrouper(donnees, "site")
        self.assertEqual(len(groupes), 3)
        self.assertEqual(groupes[0]["cle"], "Nord")
        self.assertEqual(groupes[1]["cle"], "Ouest")
        self.assertEqual(groupes[2]["cle"], "Sud")

    def test_regrouper_parametres_invalides(self):
        """Cas d'erreur : paramètres invalides."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.regrouper("pas_une_liste", "site")

    def test_regrouper_elements_non_dict(self):
        """Cas d'erreur : liste contenant des éléments qui ne sont pas des dicts."""
        with self.assertRaises(traitement.InvalidDataError):
            traitement.regrouper([{"site": "Nord"}, "non_dict"], "site")

    def test_regrouper_cle_absente(self):
        """Cas d'erreur : dictionnaire ne possédant pas la clé demandée."""
        donnees = [
            {"site": "Nord", "valeur": 10},
            {"nom": "Sud", "valeur": 15}  # clé "site" manquante
        ]
        with self.assertRaises(traitement.InvalidDataError):
            traitement.regrouper(donnees, "site")


if __name__ == "__main__":
    unittest.main()
