[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
# P4-LUCAT_QA_API

Retrieve list of Subject, Predicate, Object triples in order to be used in a QA pipeline

## License
This work is licensed under the MIT license.

## Authors
P4-LUCAT_API has been developed by members of the Scientific Data Management Group at TIB, as an ongoing research effort.
The development is co-ordinated and supervised by Maria-Esther Vidal.
This API has been developed by Ahmad Sakor.

## Input Example
POST:
https://labs.tib.eu/sdm/p4lucat_qa_api/qa_cui_service
```
{
	"cuis":[
		"C0016967",
		"C0028978",
		"C0771375"
	]
}

```

## Output Example:

```
{
    "drugs": [
        {
            "Subject": "Galantamine",
            "Relation": "affects",
            "Object": "Tramadol"
        },
        {
            "Subject": "Galantamine",
            "Relation": "affects",
            "Object": "Azithromycin"
        },
        {
            "Subject": "Galantamine",
            "Relation": "affects",
            "Object": "Acetaminophen"
        },
        {
            "Subject": "Galantamine",
            "Relation": "affects",
            "Object": "Omeprazole"
         }
       ],
    "disorders": [
        {
            "Subject": "Omeprazole",
            "Relation": "Drug Disorder",
            "Object": "Peptic Ulcer Disease"
        }
    ],
    "phenotypes": [
        {
            "Subject": "Anemia",
            "Relation": "drugSideEffectInteraction",
            "Object": "Galantamine"
        },
        {
            "Subject": "Hemorrhage",
            "Relation": "drugSideEffectInteraction",
            "Object": "Galantamine"
        },
        {
            "Subject": "Diarrhea",
            "Relation": "drugSideEffectInteraction",
            "Object": "Galantamine"
         }
          ],
    "enzymes": [
        {
            "Subject": "Cytochrome P450 2D6",
            "Relation": "drugEnzymeInteraction",
            "Object": "Galantamine"
        },
        {
            "Subject": "Cytochrome P450 3A4",
            "Relation": "drugEnzymeInteraction",
            "Object": "Galantamine"
        },
        {
            "Subject": "Cholesterol side-chain cleavage enzyme%2C mitochondrial",
            "Relation": "drugEnzymeInteraction",
            "Object": "Omeprazole"
        }
    ]
}
