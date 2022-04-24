# Implementační dokumentace k 2. úloze do IPP 2021/2022
Jméno a příjmení: Šimon Vacek\
Login: xvacek10

## Struktura
Implementace je rozdělena do několika souborů, které obsaují jednu třídu. V souboru
interpret.py se nachází metoda `main`, ve které probíhá interpretace. Jenotlivé
chybové kódy jsou uloženy zvlášť do souboru `errorCode.py`\
Přes jednotlivé instrukce se iteruje pomocí jejich atributu `order`, kvůli povolené
nesouvistlosti. To dále umožní provádět skoky na jednotlivé návěští změnou hodnoty
iterátoru.

### Interpret
Soubor `interpret.py` obsahuje třídu `Interpret`, ve které jsou třídní a statické
metody pro práci se zásobníkem volání, a kontrolu zdrojového XML souboru. Nedochází
tedy k její instanciaci.\
Před prováděním instrukcí se zavolá metoda `get_labels()`, která uloží návěští a jejich
pořádí a odebere je ze stromové struktury instukcí, protože tuto instrukci není třeba
dále provádět.

### Frame
Frame přdstavuje rámec paměťového modelu IPPcode22. Drží tedy dočasný rámec a zásobník
rámců, do kterého se na začátku interpretace vloží globální rámec. Každý rámec má
seznam proměnných, které jsou v něm definované a které je možné do něj dále přidávat.

### Variable
Třída variable se používá při vytávření, nebo změně atributů proměnné. Proměnná nemusí
při instanciaci inicializovaná, proto může obsahovat pouze název.\
Při vytváření instance se do objektu uloží celý název proměnné, tj. i s označením
rámce. Ten se později aktualizuje metodou `get_var_ids()`. Při aktualizaci hodnoty
proměnné se vytvoří instance Variable, která se vyhledá v seznamu proměnných v
rámci (`find_variable()`) a do ní se nové hodnoty nahrají.

### Instruction
Objekt typu Instruction představuje instrukci programu. Má atributy `opcode` pro název
instrukce a seznam s hodnotami operandů `args`.\
Třída poskytuje metody pro kontrolu instukcí, jejich parametrů a datových typů
operandů.

### InstructionLabel
Tato třída představuje návěští v programu. Drží zapouzdřený seznam všech návěští, které
byly v programu definovány a umožňuje s nimi dále pracovat.

## Analýza zdrojového XML souboru
Před prováděním zdrojového programu se celý soubor načte pomocí knihovny ElementTree.
Pro jednodušší interpretování instrukcí se instrukce ve struktuře se řadí podle jejich
atributu `order`. Během seřazení se provádí i kontrola, zda program má povinnou
hlavičku a obsahuje pouze podprvky instrukce a pouze povolené atributy. 

## Použité návrhové vzory
V programu se nachází jediný návrhový vzor a to **tovární metoda**. Je implementovaná
ve třídě Instruction jako `create_arith_ins()`. Ta provede kontroly parametrů
pro aritmetické instrukce (jako je ADD, SUB, apod.) a poté vytvaří instanci třídy
Instruction pro danou instrukci.\
Dále je použit vzor **jedináček** v metodě `create_global()` třídy Frame. Ta vytvoří
globální rámec, který vloží do spodu zásobníků rámců. Pokud už globální rámec byl
vytvořen, pak ho metoda vrátí. Dává smysl ho použít, právě zde, protože v zásobníku
rámců může být vždy jen jeden globální rámec.
