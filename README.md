# GymBeam-Projects

Golemio Libraries Data Extractor

Tento projekt slúži na extrakciu dát o mestských knižniciach z API Golemio a ich uloženie do CSV súboru. Extrakcia sa automaticky spúšťa denne o 7:00 ráno pražského času pomocou GitHub Actions.

Nastavenie





Získanie API kľúča





Zaregistrujte sa na Golemio API Keys a získajte API kľúč.



Nastavenie GitHub Secrets





V nastaveniach repozitára na GitHub pridajte secret s názvom GOLEMIO_API_KEY a hodnotou vášho API kľúča.



Spustenie skriptu





Skript sa automaticky spúšťa pomocou GitHub Actions. Na manuálne spustenie nastavte environment variable GOLEMIO_API_KEY a spustite python extract_libraries.py.



Výstup





Extrahované dáta sú uložené v súbore libraries.csv v koreňovom adresári repozitára.

Požiadavky





Python 3.x



Knižnice: requests, pandas, pytz (nainštalujte pomocou pip install -r requirements.txt)

Licencia

Tento projekt je licencovaný pod MIT licenciou.