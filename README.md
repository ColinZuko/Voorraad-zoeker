# Voorraad-zoeker voor FixJeFilament

Een snelle, mobiele zoektool waarmee winkelpersoneel in een paar tikken ziet hoeveel filament er nog op voorraad is.

Gebouwd door Colin Delsink tijdens mijn stage bij Fixxar Winterswijk (september 2026 – januari 2027).

## Het probleem

In de winkel staan vooraan één of twee rollen filament per soort en kleur; de rest ligt achter. Om te weten of er nog voorraad was, moest personeel de klantwebsite doorzoeken of door de winkel lopen. Dat was traag en inefficiënt.

## De oplossing

Een webpagina die als bladwijzer op het beginscherm van een telefoon of tablet staat. Typ een paar letters van een kleur, soort of merk, of scan de barcode op de doos of het schapkaartje, en je ziet meteen de voorraad en de status. Wat er van achter gepakt of bijbesteld moet worden, verzamel je in een paklijst.

## Wat de tool doet

- **Live zoeken** terwijl je typt (met debounce: pas zoeken als je even stopt met typen)
- **Zoeken op productnaam**, ook op een deel van een woord: `easy` vindt Easyfill, `pla rood` vindt rode PLA
- **Suggesties** om je zoekterm af te maken
- **Barcodes scannen** met de camera: EAN op de dozen en Code 128 op de schapkaartjes, op Android en iPhone. Een barcode met de hand intypen werkt ook.
- **Voorraadstatus in één oogopslag**: uitverkochte producten staan in het rood
- **Paklijst**: tik op een product om het op de lijst te zetten. Producten die op zijn krijgen het label *bijbestellen*. Items verwijder je met ✕, de lijst leeg je met één knop of hij leegt zichzelf na 12 uur.
- **Gemaakt voor de telefoon**, als bladwijzer op het beginscherm
- **Afgeschermd** met een geheime sleutel in de link

## Gebouwd met

- **Backend:** Python, Flask, Gunicorn
- **Data:** WooCommerce REST API (read-only key)
- **Frontend:** HTML, CSS, JavaScript (zonder framework), `localStorage` voor de paklijst
- **Barcodes:** [barcode-detector](https://github.com/Sec-ant/barcode-detector) (de `BarcodeDetector`-standaard, met ZXing via WebAssembly, zodat het ook op iPhone werkt)
- **Tests:** pytest
- **Hosting en monitoring:** Render, UptimeRobot
- **Tools:** Git, Bash, VS Code

## Hoe het werkt

```
Telefoon ──► Flask (/api/search) ──► WooCommerce REST API
   ▲                │
   └── JSON ◄───────┘  (filtert op productnaam, stuurt alleen naam + voorraad + status)
```

1. De pagina stuurt de zoekterm, of de gescande barcode, naar `/api/search`.
2. Bestaat de zoekterm alleen uit cijfers, dan is het een barcode. Flask zoekt dan in WooCommerce op het EAN-veld (`global_unique_id`).
3. Anders vraagt Flask WooCommerce om producten die bij de zoekterm passen, en houdt hij alleen producten over waarvan de **naam** alle zoekwoorden bevat. WooCommerce zoekt namelijk ook in beschrijvingen.
4. In beide gevallen haalt Flask alleen de velden op die nodig zijn (`id`, naam, voorraad, status).
5. De pagina toont het resultaat. De paklijst bewaart de browser zelf, in `localStorage`.

## Wat ik geleerd heb

- **Prestaties meten en verbeteren.** Een zoekopdracht duurde 2,3 seconden. Bij het meten bleek dat de API per zoekopdracht 1,2 MB aan productdata stuurde, terwijl ik maar drie velden gebruikte. Met de parameter `_fields` werd dat 4 KB en 1,3 seconden.
- **Secrets veilig houden.** API-keys staan in een `.env`-bestand (lokaal) en in environment variables (online), nooit in de code of in de git-geschiedenis. De toegangssleutel wordt vergeleken met `secrets.compare_digest`, zodat hij niet via de reactietijd te raden is.
- **Deployen en monitoren.** Elke `git push` deployt automatisch naar Render. Een aparte `/health`-route, zonder sleutel en zonder WooCommerce-call, laat UptimeRobot de server wakker houden zonder het geheim te kennen.
- **Onderzoeken in plaats van gokken.** De scanner las de dozen wel, maar de schapkaartjes niet. Door een foto door dezelfde barcodelezer te halen bleek dat de kaartjes geen EAN-barcode zijn maar Code 128. De oplossing was daarna één woord code.
- **Debuggen.** Foutmeldingen lezen in Python (`NameError`, verkeerd inspringen) en in JavaScript (browserconsole). Ook stille fouten leren herkennen: een typfout als `textContext` geeft geen melding maar alleen lege plekken, en een `catch` die de fout niet logt, laat "Camera niet beschikbaar" zien terwijl het om een typfout gaat.
- **Testen.** Het zoekfilter staat in een eigen functie met pytest-tests. Daarbij leerde ik dat `all([])` `True` is, en dat gedrag gebruik ik nu bewust bij het zoeken op barcode.
- **Werken met Git en Bash.** Commits, `.gitignore`, `git diff` en pushen naar GitHub, allemaal vanaf de commandline.

## Lokaal draaien

1. Maak een virtual environment en activeer die:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate
   ```
2. Installeer de packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Maak een `.env`-bestand:

   ```
   WC_URL=https://jouw-webshop.nl
   WC_KEY=ck_...
   WC_SECRET=cs_...
   ACCESS_KEY=...
   ```

   - `WC_KEY` en `WC_SECRET`: een **read-only** WooCommerce REST API-key (WooCommerce → Instellingen → Geavanceerd → REST API)
   - `ACCESS_KEY`: maak er een met `python -c "import secrets; print(secrets.token_urlsafe(16))"`

4. Start de server:
   ```bash
   flask --app app run --debug
   ```
5. Open `http://127.0.0.1:5000/?key=JOUW_ACCESS_KEY`
6. Tests draaien:
   ```bash
   pytest
   ```

De camera werkt alleen via HTTPS of op `localhost`. Op een telefoon test je de scanner dus via de online versie.

## Ideeën voor later

- Alle producten in het geheugen bewaren, zodat zoeken direct gaat
- Aantallen in de paklijst (bijvoorbeeld "3× pakken")
- Een gedeelde paklijst voor alle telefoons (vraagt een database)
