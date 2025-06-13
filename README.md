# aplikacja do zarzadzania domowym budzetem
# zalozenia aplikacji:
# wewnetrzny system z rejestracja i logowaniem
# dodawanie wydatkow i przychodow, zmiana stanu konta
# kategoryzacja wydatkow (jedzenie, transport itp)
# generowanie raportow miesiecznych
# eksport danych do pliku pdf(reportlab)/csv
# generowanie wykresow
# Aplikacja do zarzadzania domowym budzetem
## Założenia aplikacji:

### Wewnętrzny system z rejestracją i logowaniem
Skorzystam z gotowego rozwiązania w [Flask](https://pypi.org/project/Flask-Login/)

### Dodawanie wydatków i przychodów, zmiana stanu konta
Na kształt konta bankowego
- CRUD transakcji
- Dodatkowo: dodawanie dowodów zakupu (jako komentarz do transakcji)

### Kategoryzacja wydatków
  Możliwość przypisania transakcjom odpowiedniej kategorii, np. jedzenie, transport itp, co pozwoli na generowanie:
  - Podsumowania względem kategorii
  - PieCharty i inne wykresy
  - - [ ] [Pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.pie.html)
  - - [ ] [Flask](https://flask-appbuilder.readthedocs.io/en/latest/quickcharts.html)

### Eksport danych do pliku pdf / csv
- [ReportLab](https://www.reportlab.com/)
