# Image Sources Documentation

## Overview

✅ **RIJEŠENO**: Stvoren je akademski "Popis izvora slika" u LaTeX formatu (`image_sources.tex`) koji je uključen u glavni dokument.

Svi izvori slika su sada dokumentirani kao:
- **Akademski popis izvora slika** u samom dokumentu (nakon popisa literature)
- **Caption-ovi očišćeni** - uklonjeni "Izvor:" dijelovi radi čišćeg dizajna
- **Reference s brojem stranice** za lako pronalaženje svake slike

⚠️ **Status problema s jezikom u slikama:**
- LaTeX izvorni kod (.tex datoteke) je na hrvatskom jeziku
- PNG verzije možda nisu ažurirane, ali izvori su jasno označeni

## Image Categories and Sources

### 1. Author-Created Original Diagrams
These images were created by the author specifically for this thesis:

**LaTeX-Generated Diagrams:**
- `system_architecture.png` - System architecture showing main components (compiled from LaTeX)
- `rag_pipeline.png` - RAG pipeline flow diagram (compiled from LaTeX)
- `multimodal_search.png` - Multimodal search architecture (compiled from LaTeX)
- `ranking_combined_results2.png` - Results ranking visualization (compiled from LaTeX)

**Author-Created Screenshots:**
- `1.png` - Screenshot of system running complex query
- `2.png` - Screenshot of multimodal search functionality

**Conceptual Diagrams Based on Standards:**
- `dcat.png` - DCAT conceptual model based on W3C DCAT specification
- `chroma.png` - ChromaDB architecture based on ChromaDB documentation

**Screenshots from External Sources:**
- `Data_Europe.png` - Screenshot from EU Open Data Portal (data.europa.eu)

## ⚠️ Problematične slike s engleskim tekstom

### Status LaTeX dijagrama:
⚠️ **NAPOMENA**: LaTeX izvorni kod (.tex datoteke) je na hrvatskom jeziku, ali PNG verzije možda nisu ažurirane.

Potrebno je ponovno kompajlirati:
- `system_architecture.png` - LaTeX izvor je na hrvatskom (sistem_architecture.tex)
- `rag_pipeline.png` - LaTeX izvor je na hrvatskom (rag_pipeline.tex)  
- `multimodal_search.png` - LaTeX izvor je na hrvatskom (multimodal_search.tex)
- `ranking_combined_results2.png` - Možda treba kreirati .tex verziju na hrvatskom

### Slike koje možda nisu autorske:
- `chroma.png` - Možda preuzeta iz ChromaDB dokumentacije
- `dcat.png` - Možda preuzeta iz W3C specifikacije
- `Data_Europe.png` - Snimka zaslona (OK, označeno kao vanjski izvor)

### 2. Images from Previous Work (Izvjestaj.docx)
These images were extracted from the author's previous report document:

**Extracted Images (izvjestaj_image_*.png):**
All images with the `izvjestaj_image_` prefix were extracted from `izvjestaj.docx` using the `extract_images_from_docx.py` script. These represent:
- System implementation screenshots
- Process flow diagrams
- Performance analysis charts
- User interface mockups
- UML diagrams
- Technical architecture diagrams

### 3. Complete Image List by Chapter

#### Introduction/Background Chapter:
- `dcat.png` - Source: Author based on W3C DCAT specification

#### System Design/Implementation Chapter:
- `dcat.png` - Source: Author based on W3C DCAT specification
- `Data_Europe.png` - Source: Screenshot from EU Open Data Portal (data.europa.eu)
- `chroma.png` - Source: Author based on ChromaDB documentation
- `izvjestaj_image_4.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_11.png` - Source: Izvjestaj.docx (author's previous work)
- `multimodal_search.png` - Source: Author (LaTeX diagram)
- `izvjestaj_image_13.png` - Source: Izvjestaj.docx (author's previous work)
- `system_architecture.png` - Source: Author (LaTeX diagram)
- `rag_pipeline.png` - Source: Author (LaTeX diagram)
- `izvjestaj_image_53.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_84.png` - Source: Izvjestaj.docx (author's previous work)
- `1.png` - Source: Author (system screenshot)
- `2.png` - Source: Author (system screenshot)
- `ranking_combined_results2.png` - Source: Author (LaTeX diagram)
- `izvjestaj_image_68.png` - Source: Izvjestaj.docx (author's previous work)

#### Evaluation Chapter:
- `izvjestaj_image_58.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_62.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_66.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_70.png` - Source: Izvjestaj.docx (author's previous work)
- `izvjestaj_image_4.png` - Source: Izvjestaj.docx (author's previous work)

#### Discussion/Future Work Chapter:
- `izvjestaj_image_82.png` - Source: Izvjestaj.docx (author's previous work)

## Citation Format Used
All images now include source information in their captions using this format:
- **Author's original work**: "Izvor: Autor (LaTeX dijagram)" or "Izvor: Autor (snimka zaslona sustava)"
- **Based on external standards**: "Izvor: Autor na temelju [standard/documentation]"
- **Screenshots from external sources**: "Izvor: Snimka zaslona [source website]"
- **Previous author's work**: "Izvor: Izvjestaj.docx (postojeći rad autora)"

## Academic Compliance
- All images now have proper source attribution
- Original author work is clearly identified
- External sources are properly credited
- Screenshots from external websites include source URLs
- Standards-based diagrams reference the original specifications

## Preporuke za rješavanje problema jezika

### Opcija 1: Prijevod LaTeX dijagrama (PREPORUČENO)
- Editirati `.tex` datoteke u `docs/thesis/figures/` direktoriju
- Prevesti sve engleski tekst na hrvatski
- Ponovno kompajlirati dijagrame pomoću `compile_diagrams.py`

### Opcija 2: Označavanje kao preuzeto (ako nisu autorski)
- Ako su dijagrami preuzeti iz vanjske dokumentacije
- Dodati precizne izvore i reference
- Ažurirati citation format u captionovima

### Problematične LaTeX datoteke:
- `system_architecture.tex` - treba prevesti
- `rag_pipeline.tex` - treba prevesti
- `multimodal_search.tex` - treba prevesti

## File Generation Details
- LaTeX diagrams were compiled using the `compile_diagrams.py` script
- Previous work images were extracted using `extract_images_from_docx.py`
- All source files are maintained in the `docs/thesis/figures/` directory

Last updated: January 2025 