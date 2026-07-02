# -*- coding: utf-8 -*-
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import traitement


class TestTraitement(unittest.TestCase):

    def test_filtre(self):
        res = traitement.filtre_seuil([1, 5, 10], 4)
        self.assertEqual(res, [5, 10])

    def test_indicateurs(self):
        ind = traitement.indicateurs([2, 4, 6])
        self.assertEqual(ind["moyenne"], 4)
        self.assertEqual(ind["min"], 2)
        self.assertEqual(ind["max"], 6)

    def test_regrouper(self):
        donnees = [
            {"site": "Nord", "valeur": 1},
            {"site": "Sud", "valeur": 2},
        ]
        groupes = traitement.regrouper(donnees, "site")
        self.assertEqual(len(groupes), 2)


if __name__ == "__main__":
    unittest.main()
