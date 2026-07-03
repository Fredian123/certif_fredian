# Journal des Corrections & Améliorations (Bugfix Log / Changelog)

Ce document répertorie et justifie toutes les corrections d'anomalies, les optimisations et les améliorations de robustesse apportées à l'utilitaire `datatool` pour l'obtention du niveau "Au-delà des attentes" du bloc de compétences **BCC3** (Maintenance corrective).

---

## 1. Anomalie de Filtrage de Seuil Exclusif (C3.1)
* **Pourquoi (Cause) :** La fonction `filtrer_par_seuil` utilisait la condition `v > seuil`, excluant à tort les valeurs exactement égales au seuil de filtrage. Cela contredisait la spécification utilisateur.
* **Comment (Résolution) :** L'opérateur de comparaison a été remplacé par `>=` dans [traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/traitement.py).
* **Impact :** Les valeurs limites sont désormais incluses correctement dans le filtrage.

---

## 2. Dysfonctionnement de la Suite de Tests Unitaires (C3.1)
* **Pourquoi (Cause) :** Le test unitaire `test_filtre` appelait `traitement.filtre_seuil` qui n'existait pas dans le code de production (nommé à l'origine `filtrer_par_seuil`), provoquant un crash `AttributeError` immédiat lors du lancement de la commande `python -m unittest discover tests`.
* **Comment (Résolution) :** Renommage de l'appel vers `traitement.filtrer_par_seuil` dans la suite de tests unitaires et mise à jour du fichier de tests [test_traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/tests/test_traitement.py).
* **Impact :** Rétablissement de la validation automatique.

---

## 3. Lenteur et Doublons dans la Fonction de Regroupement (C3.1 / C5.4)
* **Pourquoi (Cause) :** 
  1. Le code d'origine utilisait deux boucles `for` imbriquées sur la liste complète des données, aboutissant à une complexité temporelle quadratique de $\mathcal{O}(N^2)$ inacceptable pour de grands volumes.
  2. Lors des itérations ultérieures, il rajoutait à tort les mesures déjà insérées en double dans le groupe existant, faussant ainsi les statistiques (ex. moyenne du site "Nord" à 9.5 au lieu de 10.25).
* **Comment (Résolution) :**
  1. Utilisation d'une table de hachage (dictionnaire Python) pour regrouper les éléments en temps linéaire de $\mathcal{O}(1)$ par élément, soit $\mathcal{O}(N)$ au total.
  2. Construction directe des listes de membres, évitant les ré-insertions en double.
* **Impact :** Éradication totale des doublons, statistiques justes et performances optimales.

---

## 4. Absence de Tri des Groupes par Clé (C3.1)
* **Pourquoi (Cause) :** Les résultats étaient renvoyés dans l'ordre de leur apparition dans le fichier CSV, violant la spécification demandant un tri par clé croissante (ordre alphabétique des sites).
* **Comment (Résolution) :** Tri explicite des clés du dictionnaire de regroupement via `sorted(groupes_dict.keys())` lors du formatage final dans `regrouper`.
* **Impact :** Rendu ordonné et déterministe.

---

## 5. Non-implémentation de l'Export JSON (C3.1)
* **Pourquoi (Cause) :** L'option `--json sortie.json` n'était pas supportée par l'analyseur d'arguments, rendant impossible la génération du fichier JSON attendu.
* **Comment (Résolution) :** Implémentation d'un parseur d'arguments robuste dans `main()` gérant le drapeau `--json` et sa cible, et sérialisation propre via le module natif `json` de Python.
* **Impact :** Possibilité d'exporter de manière structurée et automatisée les résultats.

---

## 6. Fuite de Ressources et Robustesse de Lecture (BCC3.1 - Programmation Défensive)
* **Pourquoi (Cause - Risque Majeur) :** 
  1. L'utilisation d'appels `f = open()` suivis de `f.read()` et `f.close()` risquait de laisser des descripteurs de fichiers ouverts en mémoire en cas d'exception levée pendant la lecture, provoquant une fuite de ressources système.
  2. Charger la totalité du fichier brut en mémoire via `f.read()` risquait de saturer la mémoire vive (RAM) en présence de très gros fichiers CSV.
  3. Le découpage brut par chaîne de caractères (`split(";")`) ne respectait pas le format standard CSV (RFC 4180) et provoquait des plantages `IndexError` si une ligne était incomplète.
* **Comment (Résolution) :**
  1. Remplacement par des blocs de gestion de ressources sécurisés `with open(...) as f` garantissant la libération des ressources.
  2. Lecture en flux ligne par ligne en utilisant le module standard `csv.reader` (idéal pour la complexité d'espace mémoire $\mathcal{O}(1)$).
  3. Validation stricte du nombre de colonnes par ligne et gestion fine des types, avec envoi d'avertissements sur `sys.stderr` pour les lignes corrompues sans interrompre le traitement global.
* **Impact :** Sécurité système maximale, consommation mémoire optimisée et résilience face aux fichiers malformés.
