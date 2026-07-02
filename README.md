# datatool

Utilitaire de traitement de mesures (CSV `site;capteur;valeur`).

## Fonctionnalites

- `filtrer_par_seuil(valeurs, seuil)` : conserve les valeurs **superieures ou egales** au seuil.
- `regrouper(enregistrements, cle)` : regroupe les enregistrements ; les groupes sont retournes **tries par cle croissante**.
- `indicateurs(valeurs)` : moyenne, min, max.

## Utilisation

    python datatool.py mesures.csv 12.5

Export JSON des groupes :

    python datatool.py mesures.csv --json sortie.json

## Tests

    python -m unittest discover tests
