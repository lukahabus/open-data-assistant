# Uvod

Ovaj rad istražuje potencijal kombiniranja velikih jezičnih modela (LLM) s tehnologijama semantičkog weba kako bi se olakšao pristup i analiza otvorenih podataka, s posebnim fokusom na goleme resurse dostupne putem Portala otvorenih podataka EU. Ključni problem kojim se rad bavi jest inherentna poteškoća s kojom se suočavaju nestručni korisnici pri pokušaju otkrivanja i korištenja relevantnih skupova podataka iz velikih, strukturiranih repozitorija poput EU portala, koji se oslanja na SPARQL upitni jezik za dohvat podataka.

## Pozadina i motivacija

Portali otvorenih podataka, kao što je Portal otvorenih podataka EU, nude bogatstvo informacija koje pokrivaju različite domene poput okoliša, gospodarstva, zdravstva i prometa. Ovi podaci imaju značajan potencijal za istraživanje, inovacije i informirano donošenje odluka. Međutim, pristup tim podacima često zahtijeva tehničku stručnost, posebno poznavanje SPARQL-a i temeljnih RDF podatkovnih modela (ontologija poput DCAT, DCTERMS, FOAF). Ova prepreka ograničava učinkovito korištenje otvorenih podataka od strane šire publike, uključujući donositelje politika, novinare, istraživače iz netehničkih područja i opću javnost.

## Tehnološka osnova

Kako bi se premostio ovaj jaz, ovaj rad koristi nekoliko ključnih tehnologija:

1.  **Portal otvorenih podataka EU i SPARQL:** Ciljni izvor podataka je [Portal otvorenih podataka EU](https://data.europa.eu/hr), koji omogućuje pristup skupovima podataka različitih institucija i tijela EU. Dohvat podataka primarno se ostvaruje putem njegove [SPARQL pristupne točke (endpoint)](https://data.europa.eu/sparql), standardnog W3C upitnog jezika za RDF baze podataka. Razumijevanje SPARQL-a ključno je za izravnu interakciju sa strukturiranim podacima portala.

2.  **Veliki jezični modeli (LLM):** Najsuvremeniji LLM-ovi, poput OpenAI-jevog GPT-4o, posjeduju izvanredne sposobnosti razumijevanja i generiranja prirodnog jezika. Oni mogu prevoditi korisničke zahtjeve izražene prirodnim jezikom u formalne reprezentacije poput koda ili, u ovom slučaju, SPARQL upita. To čini osnovu za stvaranje intuitivnijeg sučelja za otkrivanje podataka.

3.  **Okvir Langchain:** Langchain je moćan okvir dizajniran za izgradnju aplikacija pokretanih LLM-ovima. Pruža alate i apstrakcije za upravljanje uputama (prompts), interakciju s LLM-ovima, povezivanje s izvorima podataka i orkestriranje složenih radnih tijekova (agenata). U ovom projektu, Langchain se koristi za strukturiranje interakcije između korisničkog upita na prirodnom jeziku, LLM-a (za generiranje SPARQL-a) i SPARQL pristupne točke (za izvršavanje upita).

4.  **RDF podatkovni model (DCAT, DCTERMS, FOAF):** Podaci unutar portala često se opisuju pomoću RDF rječnika kao što su Data Catalog Vocabulary (DCAT) za metapodatke skupova podataka, Dublin Core Terms (DCTERMS) za opisna svojstva (naslov, opis, izdavač, datumi) i Friend of a Friend (FOAF) za informacije o agentima (npr. izdavačima). Generiranje učinkovitih SPARQL upita zahtijeva određeno poznavanje ovih uobičajenih ontologija.

## Ciljevi

Glavni cilj ovog istraživanja je razviti i evaluirati sustav temeljen na LLM-u sposoban za:

*   Prevođenje pitanja postavljenih prirodnim jezikom o podatkovnim potrebama u izvršne SPARQL upite za Portal otvorenih podataka EU.
*   Izvršavanje tih upita i dohvaćanje relevantnih metapodataka skupova podataka.
*   Rukovanje potencijalnim pogreškama tijekom generiranja ili izvršavanja upita putem iterativnog poboljšanja.
*   Sažimanje nalaza u korisnički prihvatljivom formatu, fokusirajući se na otkrivanje skupova podataka za daljnje istraživanje.
*   Istraživanje sposobnosti sustava za obradu upita različite složenosti, uključujući one koji ukazuju na potencijalno povezivanje podataka.

*(Daljnji odjeljci detaljno će opisati metodologiju, implementaciju, evaluaciju i zaključke.)* 