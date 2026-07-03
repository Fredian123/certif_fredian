# -*- coding: utf-8 -*-
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import traitement


class TestTraitement(unittest.TestCase):

    def test_filtrer_par_seuil(self):
        res = traitement.filtrer_par_seuil([1, 5, 10], 4)
        self.assertEqual(res, [5, 10])

    def test_filtrer_par_seuil_inclusif(self):
        # Cas limite : la valeur égale au seuil (4) doit être incluse
        res = traitement.filtrer_par_seuil([1, 4, 10], 4)
        self.assertEqual(res, [4, 10])

    def test_indicateurs(self):
        ind = traitement.indicateurs([2, 4, 6])
        self.assertEqual(ind["moyenne"], 4)
        self.assertEqual(ind["min"], 2)
        self.assertEqual(ind["max"], 6)

    def test_regrouper_sans_doublons(self):
        # Vérifie qu'il n'y a pas de doublons créés lors du regroupement
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
        # Vérifie que les groupes sont retournés triés par clé croissante (ordre alphabétique)
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


if __name__ == "__main__":
    unittest.main()
