# Backend Python type GeneWeb

Ce backend FastAPI implémente une structure de base inspirée par la documentation GeneWeb (base, base.acc et index de chaînes et de noms), mais en JSON pour faciliter le prototypage côté Python.

Référence de la structure GeneWeb: https://geneweb.github.io/overview/database.html#gw-files

## Lancer le serveur

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## Importer une base

Endpoint: `POST /import`

Payload JSON:
```json
{
  "db_name": "demo",
  "persons": [
    {"first_names": ["Jean"], "surname": "Dupont", "sex": "M"},
    {"first_names": ["Marie"], "surname": "Durand", "sex": "F"}
  ],
  "families": [
    {"husband_id": 0, "wife_id": 1, "children_ids": [ ]}
  ]
}
```

Cela crée `data/demo.gwb/` avec:
- `base.json`: tableaux de personnes/familles/chaînes et métadonnées
- `base.acc.json`: offsets logiques par id
- `strings.inx.json`: index de chaînes hachées
- `names.inx.json`: index de noms (plein, sous-chaînes prénom/nom)

## Requêtes

- `GET /db/{db}/persons/{id}`: lire une personne encodée (les champs référencent ids de chaînes)
- `GET /db/{db}/families/{id}`: lire une famille
- `GET /db/{db}/search/name?q=...`: recherche par nom complet normalisé
- `GET /db/{db}/search/string?q=...`: recherche exacte sur chaîne normalisée
- `GET /db/{db}/stats`: compte des entrées

## Importer/parsers un fichier GW/GWPlus

Deux endpoints supplémentaires permettent de parser un fichier texte `.gw`/GWPlus et d’optionnellement créer la base JSON:

- `POST /parse_gw`: parse le contenu brut et renvoie `persons`, `families`, `notes`.
- `POST /import_gw`: parse puis écrit `data/{db_name}.gwb/` (même structure que ci-dessus).

Exemple minimal d’appel pour `POST /parse_gw`:
```json
{
  "gw_text": "encoding: utf-8\n gwplus\n\n fam Galichet Jean_Pierre 0 <1849 + Loche Marie_Elisabeth 0 <1849\n fevt\n #marr\n end fevt\n beg\n - h Jean_Charles 1813\n end\n pevt Galichet Jean_Charles\n #birt 1813\n end pevt\n"
}
```

Exemple d’appel pour `POST /import_gw`:
```json
{
  "db_name": "demo_gw",
  "gw_text": "encoding: utf-8\n gwplus\n ... (contenu du fichier .gw) ..."
}
```

Notes sur le parsing:
- Les noms utilisent des underscores pour coller les prénoms (`Thérèse_Eugénie` → `Thérèse Eugénie`). Les suffixes de désambiguïsation (`Louis.1`) sont ignorés.
- Les événements personnels (`pevt`) supportent `#birt`, `#deat` et les lieux via `#p`/`#bp`/`#dp`.
- Les familles (`fam`) + blocs `fevt` (mariage) et `beg`/`end` (enfants) sont reconnus; les enfants héritent des parents et leur sexe via `- h` (M) / `- f` (F).
- Les blocs `notes <Nom>` sont renvoyés dans `notes` (non persistés dans `base.json`).

## Notes

- Le format de stockage ici est JSON, pas le binaire OCaml utilisé par GeneWeb, mais la structure et les index répliquent l’esprit (accès par id, hachage, sous-chaînes).
- La normalisation des noms suit une approximation (accents enlevés, minuscules, ponctuation retirée) pour des recherches robustes.