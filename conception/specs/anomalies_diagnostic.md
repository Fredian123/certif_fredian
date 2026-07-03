# Diagnostic Détaillé des Anomalies (Bugs) de `datatool`

Ce document répertorie et explique les différentes anomalies identifiées dans le code d'origine de l'utilitaire `datatool`.

---

## 1. Anomalie : Suite de tests unitaires cassée
* **Fichier impacté :** [test_traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/tests/test_traitement.py#L14)
* **Code d'origine :**
  ```python
  def test_filtre(self):
      res = traitement.filtre_seuil([1, 5, 10], 4)
      self.assertEqual(res, [5, 10])
  ```
* **Explication technique :**
  Le test tente d'appeler une fonction nommée `filtre_seuil` sur le module `traitement`. Cependant, dans le module [traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/traitement.py#L5), la fonction réelle a été nommée `filtrer_par_seuil`.
* **Conséquences :**
  Les tests unitaires ne peuvent pas s'exécuter. Toute tentative de lancement avec `python -m unittest discover tests` génère une erreur bloquante `AttributeError`.

💡 **Explication simple (Analogie) :**
> C'est comme si le manuel d'utilisation d'une machine vous disait d'appuyer sur le bouton rouge **"DÉMARRER"**, mais que le fabricant a imprimé le mot **"MISE_EN_MARCHE"** sur le bouton physique de la machine. L'opérateur automatique cherche le mot "DÉMARRER", ne le trouve pas, et refuse de lancer la machine.

---

## 2. Anomalie : Filtrage de seuil exclusif
* **Fichier impacté :** [traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/traitement.py#L9)
* **Code d'origine :**
  ```python
  if v > seuil:
  ```
* **Explication technique :**
  La spécification utilisateur (dans `README.md`) indique que le filtrage doit conserver les valeurs **supérieures ou égales** au seuil. L'opérateur de comparaison utilisé est un supérieur strict (`>`).
* **Conséquences :**
  Les mesures ayant une valeur exactement égale au seuil (par exemple, une mesure de `12.5` avec un seuil demandé de `12.5`) sont rejetées à tort par l'utilitaire, faussant ainsi les statistiques finales.

💡 **Explication simple (Analogie) :**
> Imaginez un vigile à l'entrée d'un club de sport qui a pour consigne : *"Laissez entrer toutes les personnes qui mesurent 1m80 ou plus"*. Si quelqu'téléphone se présente et mesure exactement 1m80, le vigile lui refuse l'accès en disant *"Non, tu fais exactement 1m80, il faut faire strictement plus d'1m80 pour entrer !"*. Il exclut à tort les personnes situées pile sur la limite autorisée.

---

## 3. Anomalie Critique : Doublons et lenteur algorithmique dans le regroupement
* **Fichier impacté :** [traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/traitement.py#L14-L30)
* **Code d'origine :**
  ```python
  for e in enregistrements:
      k = e[cle]
      nouveau = True
      for g in groupes:
          if g["cle"] == k:
              nouveau = False
              g["membres"].append(e) # <-- Ajout redondant
      if nouveau:
          membres = []
          for e2 in enregistrements:
              if e2[cle] == k:
                  membres.append(e2) # <-- Ajoute déjà tous les membres
          groupes.append({"cle": k, "membres": membres})
  ```
* **Explication technique :**
  1. **Création d'un groupe (Premier passage) :** Lorsqu'un site (ex. `"Nord"`) est rencontré pour la première fois, `nouveau` vaut `True`. Le code lance une boucle `for` pour chercher **tous** les enregistrements associés au site `"Nord"` dans le fichier et les insère dans le groupe. Le groupe `"Nord"` est alors complet et contient ses 2 mesures réelles.
  2. **Rencontre des éléments suivants (Passages ultérieurs) :** Lors des itérations suivantes pour les autres mesures du site `"Nord"`, `nouveau` est évalué à `False`. Mais au lieu de passer à l'élément suivant, le code exécute `g["membres"].append(e)`. Il rajoute ainsi à nouveau ces éléments pourtant déjà présents.
* **Conséquences :**
  - **Résultats erronés (Doublons) :** Des doublons sont insérés dans la liste des membres. Par exemple, le site `"Nord"` se retrouve avec 3 mesures au lieu de 2, ce qui fausse le calcul de la moyenne (la valeur `8.0` est comptée deux fois, ramenant la moyenne à `9.5` au lieu de `10.25`).
  - **Complexité algorithmique catastrophique ($O(N^2)$) :** À cause des deux boucles imbriquées sur la liste complète des données, le temps d'exécution explose sur les fichiers volumineux.

💡 **Explication simple (Analogie du tri du courrier) :**
> Imaginez que vous devez trier 10 000 lettres par ville (Paris, Lyon, Marseille).
> * **Le bug des doublons :** Pour la première lettre de "Paris", vous allez chercher dans tout votre sac toutes les autres lettres de "Paris" et vous les mettez ensemble dans une boîte "Paris". Mais lorsque vous piochez la deuxième lettre de "Paris" dans votre sac, au lieu de vous souvenir que vous avez déjà fait le travail pour "Paris", vous rajoutez à nouveau cette même lettre dans la boîte. Vous vous retrouvez donc avec des lettres en double dans vos boîtes, ce qui fausse le décompte final.
> * **La lenteur extrême :** Pour chaque lettre que vous touchez, vous videz tout votre sac par terre pour fouiller à nouveau toutes les lettres. Si vous avez 10 000 lettres, vous allez vider et fouiller tout votre sac 10 000 fois. C'est extrêmement fatiguant et cela prend des heures !
> * **La solution (Optimisation) :** Vous préparez des boîtes vides étiquetées sur votre table. Vous prenez les lettres une par une, et vous posez chaque lettre directement dans sa boîte sans jamais fouiller à nouveau dans le sac. C'est instantané et chaque lettre n'est rangée qu'une seule fois.

---

## 4. Anomalie : Absence de tri des groupes
* **Fichier impacté :** [traitement.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/traitement.py#L14-L30)
* **Explication technique :**
  La spécification requiert que les groupes soient retournés triés par clé croissante (ordre alphabétique des noms de sites). Or, l'implémentation d'origine se contente de retourner les groupes dans leur ordre d'apparition dans le fichier CSV.
* **Conséquences :**
  L'affichage et les exports des résultats ne respectent pas l'ordre requis par le cahier des charges.

💡 **Explication simple (Analogie) :**
> C'est comme si vous rangiez des dossiers dans un classeur mais que vous les laissiez dans le désordre de leur création (Marseille, puis Bordeaux, puis Lille) au lieu de les classer par ordre alphabétique (Bordeaux, Lille, Marseille). Pour retrouver une information, c'est bien plus difficile.

---

## 5. Anomalie : Export JSON non implémenté
* **Fichier impacté :** [datatool.py](file:///c:/rattrapage_L3_Examenfinale/Depot_degrade_Etudiant_2/datatool/datatool.py#L47-L60)
* **Explication technique :**
  La commande d'exportation `python datatool.py mesures.csv --json sortie.json` mentionnée dans la documentation n'est pas implémentée. La fonction `main()` ne vérifie pas la présence du paramètre `--json` dans la ligne de commande.
* **Conséquences :**
  L'option `--json` est ignorée ou génère des erreurs lors de l'exécution, rendant impossible l'exportation des données.

💡 **Explication simple (Analogie) :**
> C'est comme si le catalogue d'un magasin promettait qu'un formulaire papier est aussi disponible en version PDF sur clé USB, mais qu'en magasin le vendeur vous répond qu'il n'a jamais reçu la clé USB et ne peut vous donner que la version papier. La promesse est dans le catalogue, mais pas dans le magasin.
