# Voorraad-zoeker voor FixJeFilament

Een snelle, mobiele zoektool waarmee winkelpersoneel in een paar tikken ziet hoeveel filament er nog op voorraad is.

Gebouwd door Colin Delsink tijdens mijn stage bij Fixxar Winterswijk (september 2026 – januari 2027).

## Het probleem

In de winkel staan vooraan één of twee rollen filament per soort en kleur; de rest ligt achter. Om te weten of er nog voorraad was, moest personeel de klantwebsite doorzoeken of door de winkel lopen. Dat was traag en inefficiënt.

## De oplossing

Een webpagina die als bladwijzer op het beginscherm van een telefoon of tablet staat. Typ een paar letters van een kleur, soort of merk en je ziet meteen de voorraad en de status.

## Wat de tool doet

- **Live zoeken** terwijl je typt (met debounce: pas zoeken als je even stopt met typen)
- **Zoeken op productnaam**, ook op een deel van een woord: `easy` vindt Easyfill, `pla rood` vindt rode PLA
- **Suggesties** om je zoekterm af te maken
- **Voorraadstatus in één oogopslag**: uitverkochte producten staan in het rood
- **Gemaakt voor de telefoon**, als bladwijzer op het beginscherm
- **Afgeschermd** met een geheime sleutel in de link

## Gebouwd met

- **Backend:** Python, Flask, Gunicorn
- **Data:** WooCommerce REST API (read-only key)
- **Frontend:** HTML, CSS, JavaScript (zonder framework)
- **Hosting en monitoring:** Render, UptimeRobot
- **Tools:** Git, Bash, VS Code

## Hoe het werkt

```
Telefoon ──► Flask (/api/search) ──► WooCommerce REST API
   ▲                │
   └── JSON ◄───────┘  (filtert op productnaam, stuurt alleen naam + voorraad + status)
```

1. De pagina stuurt de zoekterm naar `/api/search`.
2. Flask vraagt WooCommerce om producten die bij de zoekterm passen. Daarbij haalt hij alleen de drie velden op die nodig zijn.
3. Flask houdt alleen producten over waarvan de **naam** alle zoekwoorden bevat. WooCommerce zoekt namelijk ook in beschrijvingen.
4. De pagina toont het resultaat.

## Wat ik geleerd heb

- **Prestaties meten en verbeteren.** Een zoekopdracht duurde 2,3 seconden. Bij het meten bleek dat de API per zoekopdracht 1,2 MB aan productdata stuurde, terwijl ik maar drie velden gebruikte. Met de parameter `_fields` werd dat 4 KB en 1,3 seconden.
- **Secrets veilig houden.** API-keys staan in een `.env`-bestand (lokaal) en in environment variables (online), nooit in de code of in de git-geschiedenis. De toegangssleutel wordt vergeleken met `secrets.compare_digest`, zodat hij niet via de reactietijd te raden is.
- **Deployen en monitoren.** Elke `git push` deployt automatisch naar Render. Een aparte `/health`-route, zonder sleutel en zonder WooCommerce-call, laat UptimeRobot de server wakker houden zonder het geheim te kennen.
- **Debuggen.** Foutmeldingen lezen in Python (`NameError`, verkeerd inspringen) en in JavaScript (browserconsole), en begrijpen waarom inspringen in Python bepaalt welke code bij welke functie hoort.
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

## Ideeën voor later

- Barcodes scannen met de camera
- Alle producten in het geheugen bewaren, zodat zoeken direct gaat
- Tests met `pytest` voor het zoekfilter
