# Sustav preporuke proizvoda za internetsku trgovinu

Projekt predstavlja sustav preporuke proizvoda za internetsku trgovinu temeljen na sadržaju proizvoda. Sustav preporučuje sadržajno slične proizvode na temelju njihovih tekstualnih značajki te izrađuje personalizirane preporuke prema prethodnim aktivnostima korisnika.

Projekt je izrađen u okviru završnog rada na temu razvoja sustava preporuke proizvoda za internetsku trgovinu.

## Korištene tehnologije

- Python
- FastAPI
- pandas
- scikit-learn
- SQLAlchemy
- SQLite
- Jinja2
- pytest
- HTML
- CSS

## Skup podataka

U projektu se koristi H&M skup proizvoda dostupan putem platforme Hugging Face:

```text
Qdrant/hm_ecommerce_products
```

Za potrebe projekta iz skupa je nasumično odabrano 5.000 proizvoda. Za svaki proizvod koriste se sljedeća svojstva:

- identifikator proizvoda
- naziv proizvoda
- vrsta proizvoda
- grupa proizvoda
- boja
- odjel
- sekcija
- grupa odjevnog predmeta
- opis proizvoda
- poveznica na sliku proizvoda

Odabrana tekstualna svojstva spajaju se u zajednički tekstualni prikaz proizvoda koji se koristi prilikom izračuna sličnosti.

## Priprema podataka

Skripta `prepare_data.py` zadužena je za preuzimanje i pripremu proizvoda.

Prilikom pripreme podataka izvršavaju se sljedeći koraci:

1. dohvaćanje podataka s platforme Hugging Face
2. nasumični odabir 5.000 proizvoda
3. uklanjanje ponovljenih proizvoda
4. uklanjanje proizvoda bez identifikatora ili naziva
5. popunjavanje nedostajućih tekstualnih vrijednosti
6. spajanje odabranih značajki u stupac `combined_features`
7. pretvaranje teksta u mala slova
8. uklanjanje nepotrebnih razmaka
9. spremanje pripremljenih podataka u CSV datoteku

Pripremljeni podaci spremaju se u:

```text
data/products.csv
```

## Način rada sustava preporuke

Sustav koristi pristup preporučivanja temeljen na sadržaju proizvoda.

Tekstualne značajke proizvoda pretvaraju se u numeričke vektore pomoću metode TF-IDF. Nakon toga sličnost između proizvoda računa se pomoću kosinusne sličnosti.

Prilikom generiranja sličnih proizvoda sustav:

1. pronalazi TF-IDF vektor odabranog proizvoda
2. uspoređuje odabrani proizvod sa svim ostalim proizvodima
3. rangira proizvode prema vrijednosti kosinusne sličnosti
4. isključuje odabrani proizvod iz rezultata
5. uklanja ponavljanje istih modela proizvoda
6. vraća traženi broj najsličnijih proizvoda

TF-IDF vektorizator koristi pojedinačne riječi i parove riječi. Broj značajki ograničen je na 20.000 najvažnijih pojmova.

## Personalizirane preporuke

Sustav bilježi aktivnosti korisnika nad proizvodima. Podržane su tri vrste aktivnosti:

| Aktivnost | Težina |
|---|---:|
| Pregled proizvoda | 1 |
| Sviđanje proizvoda | 3 |
| Kupnja proizvoda | 5 |

Veća težina označava veći interes korisnika za određeni proizvod.

Korisnički profil izrađuje se kao ponderirani prosjek TF-IDF vektora proizvoda s kojima je korisnik ostvario interakciju.

Pojednostavljeni prikaz izračuna korisničkog profila:

```text
korisnički profil =
zbroj(težina aktivnosti × vektor proizvoda)
------------------------------------------------
zbroj težina aktivnosti
```

Personalizirane preporuke dobivaju se usporedbom korisničkog profila s TF-IDF vektorima svih proizvoda.

Prilikom generiranja personaliziranih preporuka sustav:

- uvažava vrstu i težinu aktivnosti
- zbraja težine ponovljenih aktivnosti
- isključuje proizvode s kojima je korisnik već ostvario interakciju
- uklanja ponavljanje jednakih naziva proizvoda
- vraća proizvode s najvećom sličnošću korisničkom profilu

## Hladni početak

Korisnik koji još nema zabilježenih aktivnosti nema dovoljno podataka za izradu personaliziranog profila.

U tom se slučaju korisniku prikazuje početni katalog različitih proizvoda. Nakon što korisnik pregleda, označi ili kupi proizvode, sustav može izraditi njegov profil i generirati personalizirane preporuke.

## Baza podataka

Za pohranu korisnika i njihovih aktivnosti koristi se SQLite baza podataka.

Baza sadrži dvije glavne tablice:

### Tablica `users`

| Stupac | Opis |
|---|---|
| `id` | Jedinstveni identifikator korisnika |
| `username` | Jedinstveno korisničko ime |

### Tablica `interactions`

| Stupac | Opis |
|---|---|
| `id` | Jedinstveni identifikator interakcije |
| `user_id` | Identifikator korisnika |
| `article_id` | Identifikator proizvoda |
| `interaction_type` | Vrsta aktivnosti |
| `created_at` | Vrijeme nastanka aktivnosti |

Proizvodi se ne spremaju u SQLite bazu jer se katalog proizvoda učitava iz pripremljene CSV datoteke.

## Struktura projekta

```text
product-recommender/
├── app/
│   ├── recommender/
│   │   ├── __init__.py
│   │   └── content_based.py
│   ├── static/
│   │   ├── placeholder.svg
│   │   └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── product_detail.html
│   │   ├── products.html
│   │   └── recommendations.html
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── data/
│   └── products.csv
├── tests/
│   ├── conftest.py
│   └── test_content_based.py
├── .gitignore
├── prepare_data.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Instalacija

Za pokretanje projekta potreban je Python 3.11 ili novija verzija.

### 1. Preuzimanje projekta

Pozicionirati se u korijensku mapu projekta:

```powershell
cd product-recommender
```

### 2. Izrada virtualnog okruženja

```powershell
python -m venv .venv
```

### 3. Aktivacija virtualnog okruženja na Windowsu

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalacija potrebnih biblioteka

```powershell
pip install -r requirements.txt
```

## Priprema skupa podataka

Ako datoteka `data/products.csv` nije dostupna, potrebno ju je izraditi pokretanjem skripte:

```powershell
python prepare_data.py
```

Skripta preuzima podatke, odabire 5.000 proizvoda, čisti ih i sprema pripremljeni skup u mapu `data`.

Za preuzimanje podataka potrebna je internetska veza.

## Pokretanje aplikacije

Aplikacija se pokreće iz korijenske mape projekta naredbom:

```powershell
uvicorn app.main:app --reload
```

Nakon pokretanja aplikacija je dostupna na adresi:

```text
http://127.0.0.1:8000
```

Automatski generirana Swagger API dokumentacija dostupna je na:

```text
http://127.0.0.1:8000/docs
```

Korisničko sučelje dostupno je na:

```text
http://127.0.0.1:8000/shop
```

## Stvaranje testnog korisnika

Prije korištenja personaliziranih preporuka potrebno je napraviti barem jednog korisnika.

U Swagger dokumentaciji potrebno je otvoriti endpoint:

```text
POST /users
```

Primjer tijela zahtjeva:

```json
{
  "username": "test_user"
}
```

## API endpointi

### Proizvodi

| Metoda | Endpoint | Opis |
|---|---|---|
| GET | `/products` | Dohvaćanje kataloga proizvoda |
| GET | `/products/{article_id}` | Dohvaćanje detalja proizvoda |
| GET | `/products/{article_id}/similar` | Dohvaćanje sadržajno sličnih proizvoda |

### Korisnici i aktivnosti

| Metoda | Endpoint | Opis |
|---|---|---|
| POST | `/users` | Stvaranje korisnika |
| GET | `/users` | Dohvaćanje svih korisnika |
| POST | `/interactions` | Bilježenje korisničke aktivnosti |
| GET | `/users/{user_id}/interactions` | Dohvaćanje aktivnosti korisnika |
| GET | `/users/{user_id}/recommendations` | Personalizirane preporuke |

### Korisničko sučelje

| Metoda | Endpoint | Opis |
|---|---|---|
| GET | `/shop` | Prikaz kataloga proizvoda |
| GET | `/shop/products/{article_id}` | Prikaz detalja proizvoda |
| POST | `/shop/interactions` | Bilježenje aktivnosti iz sučelja |
| GET | `/shop/recommendations/{user_id}` | Vizualni prikaz personaliziranih preporuka |

## Primjeri korištenja API-ja

### Dohvaćanje proizvoda

```http
GET /products?limit=20&offset=0
```

### Dohvaćanje detalja proizvoda

```http
GET /products/0300908010
```

### Dohvaćanje sličnih proizvoda

```http
GET /products/0300908010/similar?limit=5
```

### Bilježenje pregleda proizvoda

```http
POST /interactions
Content-Type: application/json
```

```json
{
  "user_id": 1,
  "article_id": "0300908010",
  "interaction_type": "view"
}
```

### Bilježenje sviđanja proizvoda

```json
{
  "user_id": 1,
  "article_id": "0517442001",
  "interaction_type": "like"
}
```

### Bilježenje kupnje proizvoda

```json
{
  "user_id": 1,
  "article_id": "0507181002",
  "interaction_type": "purchase"
}
```

### Dohvaćanje personaliziranih preporuka

```http
GET /users/1/recommendations?limit=10
```

## Testiranje

Automatski testovi pokreću se iz korijenske mape projekta naredbom:

```powershell
python -m pytest -v
```

Testovima su obuhvaćeni sljedeći slučajevi:

- uspješno učitavanje proizvoda
- očuvanje početnih nula u identifikatoru proizvoda
- vraćanje traženog broja preporuka
- isključivanje odabranog proizvoda
- uklanjanje ponovljenih modela proizvoda
- obrada nepostojećeg proizvoda
- validacija broja preporuka
- korisnik bez aktivnosti
- ignoriranje nepoznatih aktivnosti
- isključivanje proizvoda s kojima je korisnik već ostvario interakciju
- provjera utjecaja težine aktivnosti
- obrada nedostajuće CSV datoteke
- obrada skupa s nedostajućim obaveznim stupcima

Očekivani rezultat:

```text
13 passed
```

## Korisničko sučelje

Korisničko sučelje služi kao vizualna demonstracija rada sustava preporuke.

Omogućuje:

- pregled kataloga proizvoda
- paginaciju kataloga
- prikaz detalja proizvoda
- prikaz sadržajno sličnih proizvoda
- bilježenje pregleda proizvoda
- označavanje sviđanja
- simulaciju kupnje
- prikaz personaliziranih preporuka


