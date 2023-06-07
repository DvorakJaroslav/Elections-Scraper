import requests
from bs4 import BeautifulSoup
import csv
import sys

def main():
    if len(sys.argv) != 3:
        print("Zadejte 2 povinné argumenty odkaz a jméno výstupního souboru.csv")
        quit()
    else:
        url_vstup = sys.argv[1]
        jmeno_csv_vstup = sys.argv[2]

        if "https://volby.cz/pls/ps2017nss/" in jmeno_csv_vstup and ".csv" in url_vstup:
            print("zadal jsi argumenty ve špatném pořadí")
            quit()
        else:
            if "https://volby.cz/pls/ps2017nss/" not in url_vstup:
                print("První argument obsahuje špatný odkaz")
                quit()
            if ".csv" not in jmeno_csv_vstup:
                print("Druhý argument musí obsahovat -  jméno souboru a .csv")
                quit()


    vysledek = []
    # url = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
    url = url_vstup
    base_url = "https://volby.cz/pls/ps2017nss/"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[2:]:  # ignorování 2 řádků s hlavičko
            cells = row.find_all("td")
            psc = cells[0].text.strip()
            nazev_obce = cells[1].text.strip()
            strany = {}
            strany["psc"] = psc
            strany["obec"] = nazev_obce
            link = row.a
            if link:   # ověřuje jestli proměná link obsahuje nějakou hodnotu
                url_a = link.get("href")
                target_url = base_url+ url_a
                response = requests.get(target_url)
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                tables = soup.find_all("table", class_="table")

                table = tables[0]
                # Procházení řádků tabulky
                rows = table.find_all("tr")
                for row in rows[1:]:  # Ignorování prvního řádku s hlavičkou
                    cells = row.find_all("td")
                    if len(cells) > 0:
                        volici_vsez = cells[3].text.strip()  # Získání textu z druhé buňky
                        if "\xa0" in volici_vsez: # pokud je číslo větší než 1000 musí se odstranit "\xa0"
                            volici_vsez = volici_vsez.replace("\xa0", "")
                        odevzdane_obal = cells[6].text.strip()
                        if "\xa0" in odevzdane_obal:
                            odevzdane_obal = odevzdane_obal.replace("\xa0", "")
                        platne_hlasy = cells[7].text.strip()
                        if "\xa0" in platne_hlasy:
                            platne_hlasy = platne_hlasy .replace("\xa0", "")
                        strany["Voliči v seznamu"] = int(volici_vsez)
                        strany["Odevzdane obálky"] = int(odevzdane_obal)
                        strany["Platné hlasy"] = int(platne_hlasy)

                table = tables[1]
                # Procházení řádků tabulky
                rows = table.find_all("tr")
                for row in rows[1:]:  # Ignorování prvního řádku s hlavičkou
                    cells = row.find_all("td")
                    if len(cells) > 0:
                        strana = cells[1].text.strip()  # Získání textu z druhé buňky
                        pocet_hlasu = cells[2].text.strip()
                        if "\xa0" in pocet_hlasu:
                            pocet_hlasu = pocet_hlasu.replace("\xa0", "")
                        strany[strana] = int(pocet_hlasu)  # Přidání strany a počtu hlasů do slovníku

                table = tables[2]
                # Procházení řádků tabulky
                rows = table.find_all("tr")
                for row in rows[1:]:  # Ignorování prvního řádku s hlavičkou
                    cells = row.find_all("td")
                    if len(cells) > 0:
                        strana = cells[1].text.strip()  # Získání textu z druhé buňky
                        pocet_hlasu = cells[2].text.strip()
                        if "\xa0" in pocet_hlasu:
                            pocet_hlasu = pocet_hlasu.replace("\xa0", "")
                        if strana != "-":
                            strany[strana] = int(pocet_hlasu)  # Přidání strany a počtu hlasů do slovníku
                vysledek.append(strany)



    soubor = jmeno_csv_vstup
    hlavicka = vysledek[0].keys()

    with open(soubor, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=hlavicka)
        writer.writeheader()
        writer.writerows(vysledek)

if __name__ == '__main__':
    main()