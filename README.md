# open-data-assistant - Upute za korištenje

1. Potrebno je nabaviti OpenAI API key na sljedećoj poveznici: https://openai.com/index/openai-api/
    - Napomena: API key se plaća, može se uzeti za 5$ za potrebe ovog projekta
2. Stvorite datoteku .env unutar projekta te zalijepite API key u sljedećem formatu: OPENAI_API_KEY=sk-proj-…
3. Unutar projekta otvorite terminal i unesite iduću naredbu: opendata_env\Scripts\activate
4. pip install -r requirements.txt
5. python main.py --> locations_map.html
6. python chatbot.py


rezoniranje o podacima iz metapodataka, CKAN i DCAT
vraćanje informacija o potrebnim datasetovima

npr. "daj mi sve podatke o broju stanovnika u Zagrebu i Splitu"
 --> pretražuje se CKAN i DCAT, vraćaju se svi datasetovi s podacima o broju stanovnika u Zagrebu i Splitu
    --> korisniku se prikazuju svi datasetovi, korisnik odabire koji želi
        --> korisniku se prikazuju podaci iz odabranog dataseta
