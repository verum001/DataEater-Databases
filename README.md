# DataEater Databases

Versioned manual collections for [DataEater](https://github.com/verum001/DataEater). Each database contains searchable source passages with document names and original PDF page references.

## Survival 0.1.0

[Download survival.dataeater](survival/versions/0.1.0/survival.dataeater?raw=true)

The collection contains:

- **FM 3-05.70 (FM 21-76), Survival**, Department of the Army, May 2002.
- **Nuclear War Survival Skills, Updated and Expanded 1987 Edition**, Cresson H. Kearny, Oregon Institute of Science and Medicine.
- **Air Force Handbook 10-644, Survival Evasion Resistance Escape (SERE) Operations**, Department of the Air Force, 27 March 2017.

Copy the database to the phone's DataEater folder, then choose it in the app. DataEater 1.5.0 source adds **All unlocked databases** to search several database files together. Text search works without an AI model; AI answers require a supported model.

This first edition is a searchable text extraction, not a revised survival handbook. It contains historical guidance. Images, diagrams and scale-dependent templates remain in the original PDFs. Consult the original source page for those materials. Complete cross-page procedure and complex-table review is pending; the database has no guarantee of answer accuracy.

See [source terms and notices](survival/SOURCE_NOTICES.md), [preparation and checks](survival/PREPARATION.md), and [build report](survival/versions/0.1.0/BUILD_REPORT.json). Free download does not remove the manuals' original restrictions or conditional reproduction terms.

## Versions and sources

Published database versions remain in `survival/versions/<version>/`. Checksums identify each artifact. The supplied original PDFs stay local in `survival/sources/` and are not published in this repository or its releases. The [source manifest](survival/sources/MANIFEST.json) records exact filenames, page counts and SHA-256 hashes.

To rebuild, place the matching PDFs in `survival/sources/`, install PyMuPDF, then run `python3 tools/build_survival.py`. Preparation is local and does not send documents to an online service. Version 0.1.0 was built with PyMuPDF 1.28.2; see the report for the actual installed version.

Original preparation code and repository documentation use Apache-2.0. Manual text and original PDFs retain their own terms; they are **not** relicensed as Apache-2.0.

## App download catalogue

`catalog.json` is the public catalogue used by DataEater's Download databases screen. It records published release metadata, versioned release download addresses, exact sizes and SHA-256 digests. The app reads it directly without GitHub API authentication or API quota usage.

After publishing a non-draft database release, update `catalog.json` from its final uploaded asset metadata. Keep older versions and notices available; do not include original PDFs or private files. Only uploaded `.dataeater` assets with a valid SHA-256 digest belong in the catalogue. Newest releases are selected by publication date.
