Implementační dokumentace k 1. úloze do IPP 2021/2022\
Jméno a příjmení: Šimon Vacek\
Login: xvacek10

##Struktura
Ještě před analýzou zdrojového souboru se zpracují argumenty skriptu funkcí `handleScriptArgs`,
v mém případě tedy jen argument `--help`.\
Hlavní částí analyzátoru je funkce `parse`, která volá jednotlivé funkce obstarávající lexikální,
typové a další kontroly. \
Pro jednotlivé chybové stavy jsem použil konstanty s prefixem `ERR_`.

##Implementace

###Zpracování vstupu
Zdrojový kód ippcode22 načítám řádek po řádku, který ořežu o komentáře, přebytečné bílé znaky
na krajích a rozdělím do pole podle libovolného počtu bílých znaků. Toto obstarává funcke
`getCode`.

###Kontroly instrukcí
K práci s instrukcemi jsem využil globální pole `instrArguments`, které má jako klíč název
instrukce. Každému klíči je přiřazeno hodnota z enumarátoru `ArgType`. Enumerátor nabývá hodnot,
které odpovídají počtu a typu parametrů. Tedy například instukce `ADD` má hodnotu `VarSymbSymb`,
protože očekává 3 argumenty a to typů &lt;var&gt;,&lt;symb1&gt; a &lt;symb2&gt;.\
\
Ve funkcích `isInstr`, `checkNOArgs` kontroluji instrukci a správný počet jejích parametrů.
Kontrolu správných typů parametrů hlídá `checkParseArgs`, která pomocí hodnoty z enumu
ArgType a vlastního počítadla kontroluje, zda je správný typ parametru na správném místě.
Na jednotlivé typy se volají funkce `isXYZOk`, ve kterých využívám regulární výrazy.

###Generování XML
Pro generování výstupního souboru jsem využil knihovnu XMLWriter, u které jsou použil
volání metod nad jejím objektem.