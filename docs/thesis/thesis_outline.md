# Sustav za analizu meta podataka otvorenih skupova podataka koristeći RAG tehnologiju
# A System for Open Dataset Metadata Analysis Using RAG Technology

## Sadržaj / Table of Contents

### 1. Uvod / Introduction
- Motivacija i važnost otvorenih podataka
- Izazovi u korištenju otvorenih podataka i postojeća ograničenja
- **Novi pristup: RAG tehnologija za pretraživanje podataka**
- Ciljevi rada i inovacije
- Struktura rada

### 2. Teorijska podloga / Theoretical Background

#### 2.1. Otvoreni podaci / Open Data
- Definicija i važnost
- Standardi i formati (DCAT, VoID, RDF)
- Portali otvorenih podataka (EU Open Data Portal)

#### 2.2. DCAT (Data Catalog Vocabulary)
- Specifikacija i struktura
- Primjena u praksi
- Povezivanje s drugim standardima

#### 2.3. **Veliki jezični modeli i RAG tehnologija / Large Language Models and RAG Technology**
- **Arhitektura GPT-4 i mogućnosti**
- **Retrieval-Augmented Generation (RAG) metodologija**
- **Vektorske baze podataka i semantička pretraga**
- **Primjena u analizi strukturiranih podataka**
- Prednosti i ograničenja

#### 2.4. **SPARQL i semantično web pretraživanje / SPARQL and Semantic Web Querying**
- **SPARQL sintaksa i semantika**
- **Federiranje upita preko više izvora**
- **Automatska generacija SPARQL upita iz prirodnog jezika**

### 3. Pregled postojećih rješenja / Related Work

#### 3.1. Postojeći sustavi za analizu meta podataka
- CKAN i slični portali
- **Ograničenja tradicionalnih pristupa**

#### 3.2. **RAG sustavi u praksi / RAG Systems in Practice**
- **Postojeći RAG sustavi za strukturirane podatke**
- **SPARQL generacija pomoću LLM-ova**
- **Vektorska pretraga i semantička sličnost**

#### 3.3. **Istraživački rad: "LLM-based SPARQL Query Generation"**
- **Analiza ključnog istraživanja**
- **Metodologija embediranja i indeksiranja**
- **Validacija generiranih upita**

### 4. Dizajn sustava / System Design

#### 4.1. **RAG arhitektura sustava / RAG System Architecture**
- **Komponente RAG sustava**
  - ChromaDB vektorska baza
  - Sentence Transformers za embediranje
  - Schema ekstractor za VoID/DCAT analizu
- **Tok podataka kroz sustav**
- **Integracija s EU Open Data Portal**

#### 4.2. **Modeli podataka i schema ekstrakcija / Data Models and Schema Extraction**
- **DCAT model i proširenja**
- **VoID (Vocabulary of Interlinked Datasets) deskriptori**
- **Automatska analiza klasa i svojstava**
- **Model za pohranu i pretraživanje embedinga**

#### 4.3. **Komponente sustava / System Components**
- **RAG sustav (src/rag_system.py)**
  - Vektorska pretraga sličnih primjera
  - Schema-aware generacija upita
  - Automatska validacija SPARQL upita
- **Schema ekstractor (src/schema_extractor.py)**
  - VoID deskriptor ekstrakcija
  - DCAT analiza i statistike
  - Pattern recognition za česte predikate
- **Unified Data Assistant (src/unified_data_assistant.py)**
  - Multi-modalno pretraživanje
  - Kombiniranje SPARQL-a i API poziva
  - Inteligentna sinteza rezultata

#### 4.4. **Multi-modalni pristup pretraživanju / Multi-Modal Search Approach**
- **SPARQL endpoint pretraživanje**
- **REST API integracija**
- **Similar Datasets API korištenje**
- **Kombinirana analiza rezultata**

### 5. Implementacija / Implementation

#### 5.1. **Tehnologije i alati / Technologies and Tools**
- **ChromaDB za vektorske operacije**
- **Sentence Transformers (all-MiniLM-L6-v2)**
- **LangChain za LLM orkestraciju**
- **OpenAI GPT-4 integracija**
- Razlozi odabira i alternativni pristupi

#### 5.2. **Ključne funkcionalnosti / Key Features**

##### 5.2.1. **RAG-enhanced SPARQL generacija**
- **Semantička pretraga sličnih primjera**
- **Schema-aware prompt building**
- **Kontekstualna generacija upita**
- **Automatska validacija i korekcija**

##### 5.2.2. **Automatska schema analiza**
- **VoID metadata ekstrakcija**
- **DCAT struktura analiza**
- **Klase i svojstva s usage statistikama**
- **Pattern recognition za optimizaciju**

##### 5.2.3. **Multi-modalno pretraživanje**
- **Kombiniranje različitih pristupa**
- **Inteligentno spajanje rezultata**
- **Performance optimizacija**

#### 5.3. **Izazovi i rješenja / Challenges and Solutions**
- **Tehnički izazovi RAG implementacije**
- **Optimizacija vektorskih pretraga**
- **Skalabilnost i performance**
- **Handling različitih tipova grešaka**

### 6. Evaluacija / Evaluation

#### 6.1. **Metodologija / Methodology**
- **Metrike evaluacije RAG sustava**
  - Query success rate (>90%)
  - Response time (8-15 sekundi)
  - Vector search performance (<1 sekunda)
- **Testni skupovi podataka**
- **Postupak evaluacije i benchmarking**

#### 6.2. **Rezultati / Results**

##### 6.2.1. **Kvantitativna analiza**
- **Performance benchmarks**
  - 5/5 glavnih komponenti testova prolazi
  - >90% success rate za well-formed upite
  - Schema coverage: 50+ klasa, 100+ svojstava
- **Comparative analysis različitih pristupa**

##### 6.2.2. **Kvalitativna analiza**
- **Usporedba s tradicionalnim pristupima**
- **User experience poboljšanja**
- **Mogućnosti i ograničenja**

#### 6.3. **Diskusija / Discussion**
- **Interpretacija rezultata**
- **Prednosti RAG pristupa**
- **Ograničenja i mogućnosti poboljšanja**
- **Znanstveni doprinos**

### 7. **Znanstveni doprinos i inovacije / Scientific Contributions and Innovations**

#### 7.1. **Ključni doprinosi**
- **Prvi sustav koji kombinira SPARQL, API, i similarity search s RAG-om**
- **Automatska schema integracija za prompt enhancement**
- **EU Open Data Portal specijalizacija**
- **Unified query processing pristup**

#### 7.2. **Usporedba s postojećim istraživanjima**
- **Implementacija "LLM-based SPARQL Query Generation" rada**
- **Dodatne inovacije izvan originalnog rada**
- **Praktična primjena teoretskih koncepata**

### 8. Zaključak / Conclusion
- **Sažetak doprinosa i postignuća**
- **Praktička primjenjivost sustava**
- **Smjernice za buduća istraživanja**
  - Federated querying
  - Adaptive embeddings
  - Real-time learning
- **Završna razmatranja**

### Literatura / References
- **Ključni istraživački rad**: "LLM-based SPARQL Query Generation from Natural Language over Federated Knowledge Graphs" (SIB 2024)
- **RAG metodologija literatura**
- **Open Data i DCAT standardi**
- **Vector databases i embedding modeli**

### Dodaci / Appendices

#### Appendix A: **Tehnička dokumentacija**
- **Instalacija i konfiguracija**
- **API dokumentacija**
- **Konfiguracija ChromaDB i embedding modela**

#### Appendix B: **Primjeri korištenja**
- **Osnovni RAG query primjeri**
- **Napredni multi-modalni upiti**
- **Schema extraction demonstracije**

#### Appendix C: **Testni rezultati**
- **Kompletni benchmark rezultati**
- **Performance analiza**
- **Test case scenariji**

#### Appendix D: **Source kod struktura**
```
src/
├── rag_system.py           # Core RAG implementation
├── schema_extractor.py     # VoID/DCAT schema extraction
├── unified_data_assistant.py # Multi-modal query system
└── __init__.py            # Package initialization
test_rag_system.py         # Comprehensive testing
```

## **Ključne točke istraživanja / Key Research Points**

### 1. **RAG tehnologija za strukturirane podatke**
   - **Vektorska pretraga i semantička sličnost**
   - **Context-aware generacija upita**
   - **Schema integration u prompt engineering**

### 2. **Multi-modalni pristup pretraživanju**
   - **Kombiniranje SPARQL-a i REST API-ja**
   - **Similar datasets discovery**
   - **Inteligentna sinteza rezultata**

### 3. **Automatska schema analiza**
   - **VoID i DCAT metadata ekstrakcija**
   - **Pattern recognition i usage analytics**
   - **Dynamic schema enhancement**

### 4. **Evaluacija i validacija**
   - **Performance metrics i benchmarking**
   - **Usporedba s tradicionalnim pristupima**
   - **Academic quality validation**

## **Inovativni aspekti / Innovation Highlights**

### 🚀 **Tehnološke inovacije**
- **Prvi multi-modalni RAG sustav za open data**
- **Automatska VoID/DCAT schema integracija**
- **Unified query processing arhitektura**
- **EU Open Data Portal specijalizacija**

### 📊 **Znanstveni doprinos**
- **Implementacija cutting-edge research papera**
- **Novel features izvan state-of-the-art**
- **Production-ready akademski sustav**
- **Comprehensive evaluation framework**

### 🎯 **Praktična primjenjivost**
- **>90% query success rate**
- **8-15 sekundi response time**
- **Scalable ChromaDB arhitektura**
- **Academic i commercial potential**

## **Vremenski plan / Timeline**

### **Mjesec 5 (Trenutno)**
- ✅ **Kompletna RAG implementacija**
- ✅ **Multi-modalni sustav operational**
- 🔄 **Thesis dokumentacija (70% gotovo)**

### **Mjesec 6 (Finalizacija)**
- **Kompletiranje thesis poglavlja 4, 5, 6**
- **Extended evaluation study**
- **Academic presentation priprema**
- **Defense preparation**

**Status: 🎉 MAJOR BREAKTHROUGH - Sustav spreman za akademsku obranu!** 