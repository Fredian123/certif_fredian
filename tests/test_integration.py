# -*- coding: utf-8 -*-
import unittest
import sys
import os
import io
import json
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datatool
import traitement


class TestIntegrationDataTool(unittest.TestCase):

    def setUp(self):
        # Création d'un fichier CSV temporaire de test
        self.csv_fd, self.csv_path = tempfile.mkstemp(suffix=".csv", text=True)
        with os.fdopen(self.csv_fd, "w", encoding="utf-8") as f:
            f.write("site;capteur;valeur\n")
            f.write("Nord;C1;12.5\n")
            f.write("Nord;C2;8.0\n")
            f.write("Sud;C1;15.0\n")
            f.write("Est;C3;non_numerique\n")  # Ligne avec valeur invalide (devrait donner -999)
            f.write("Ouest;;10.0\n")          # Ligne malformée (capteur vide -> ignorée)
            f.write("Sud;C2;\n")             # Ligne incomplète (valeur vide -> -999)
            f.write("\n")                      # Ligne vide -> ignorée

        # Fichier JSON temporaire pour tester l'export
        self.json_fd, self.json_path = tempfile.mkstemp(suffix=".json", text=True)
        os.close(self.json_fd)  # On ferme car json_path suffit pour l'écriture

    def tearDown(self):
        # Nettoyage des fichiers temporaires
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        if os.path.exists(self.json_path):
            os.remove(self.json_path)

    def test_lire_fichier_integration(self):
        """Vérifie le parsing global du CSV avec programmation défensive."""
        # Capturer stderr car LireFichier écrit des avertissements
        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            donnees = datatool.LireFichier(self.csv_path)
        
        # 6 lignes écrites (sans entête et ligne vide)
        # - Nord;C1;12.5 -> valide (1)
        # - Nord;C2;8.0 -> valide (2)
        # - Sud;C1;15.0 -> valide (3)
        # - Est;C3;non_numerique -> valeur invalide remplacée par -999 (4)
        # - Ouest;;10.0 -> capteur vide -> ignorée
        # - Sud;C2; -> valeur vide -> -999 (5)
        self.assertEqual(len(donnees), 5)
        
        # Vérification des détails des données lues
        self.assertEqual(donnees[0], {"site": "Nord", "capteur": "C1", "valeur": 12.5})
        self.assertEqual(donnees[3], {"site": "Est", "capteur": "C3", "valeur": -999.0})
        self.assertEqual(donnees[4], {"site": "Sud", "capteur": "C2", "valeur": -999.0})

        # Vérifier que les alertes sont écrites sur stderr
        warnings = stderr_capture.getvalue()
        self.assertIn("non_numerique", warnings)
        self.assertIn("site ou le capteur est vide", warnings)

    def test_cli_flux_nominal_console(self):
        """Test d'intégration du flux nominal via la console."""
        # Simuler les arguments CLI
        test_args = ["datatool.py", self.csv_path]
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with patch("sys.argv", test_args):
            with patch("sys.stdout", stdout_capture):
                with patch("sys.stderr", stderr_capture):
                    datatool.main()
        
        # Vérifier la sortie standard
        output = stdout_capture.getvalue()
        # Les groupes doivent être triés par clé croissante : Est, Nord, Sud
        self.assertIn("Est -> aucune mesure valide", output)
        self.assertIn("Nord -> 2 mesures, moyenne 10.25", output)
        self.assertIn("Sud -> 2 mesures, moyenne 15.0", output) # L'une des mesures de Sud est -999 (ignorée pour la moyenne)

    def test_cli_filtrage_et_json(self):
        """Test d'intégration du filtrage par seuil et de l'export JSON."""
        # Seuil de 10.0 et export JSON
        test_args = ["datatool.py", self.csv_path, "10.0", "--json", self.json_path]
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with patch("sys.argv", test_args):
            with patch("sys.stdout", stdout_capture):
                with patch("sys.stderr", stderr_capture):
                    datatool.main()
        
        # Le seuil de 10 doit retenir 12.5 (Nord) et 15.0 (Sud) - 2 valeurs sur 3 valides (les -999 sont ignorées)
        output = stdout_capture.getvalue()
        self.assertIn("2 valeurs retenues sur 3", output)
        self.assertIn("Exportation JSON reussie", output)

        # Lire le fichier JSON pour valider sa structure et son contenu
        with open(self.json_path, "r", encoding="utf-8") as f:
            groupes = json.load(f)
            
        # Doit contenir les 3 groupes dans l'ordre alphabétique : Est, Nord, Sud
        self.assertEqual(len(groupes), 3)
        self.assertEqual(groupes[0]["cle"], "Est")
        self.assertEqual(groupes[1]["cle"], "Nord")
        self.assertEqual(groupes[2]["cle"], "Sud")

    def test_cli_fichier_introuvable(self):
        """Test d'intégration pour un fichier introuvable."""
        test_args = ["datatool.py", "fichier_qui_n_existe_pas.csv"]
        
        stderr_capture = io.StringIO()
        
        with patch("sys.argv", test_args):
            with patch("sys.stderr", stderr_capture):
                with self.assertRaises(SystemExit) as cm:
                    datatool.main()
                    
        # Doit s'arrêter avec un code d'erreur 1
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Fichier CSV introuvable", stderr_capture.getvalue())


# Helper pour rediriger stderr
class redirect_stderr:
    def __init__(self, new_target):
        self.new_target = new_target
        self.old_target = sys.stderr

    def __enter__(self):
        sys.stderr = self.new_target
        return self.new_target

    def __exit__(self, exctype, excinst, exctb):
        sys.stderr = self.old_target


if __name__ == "__main__":
    unittest.main()
