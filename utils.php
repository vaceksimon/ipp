<?php
const ERR_OK = 0;
const ERR_PARAM = 10;
const ERR_INPUT = 11;
const ERR_OUTPUT = 12;
const ERR_HEADER = 21;
const ERR_OPP_CODE = 22;
const ERR_LEX_SYN = 23;
const ERR_INTERNAL = 99;

function writeHelp() {
    printf("Načte ze standardního vstupu zdrojový kód v IPP-code22, zkontroluje lexikální a ");
    printf("syntaktickou správnost kódu a vypíše na standardní výstup XML reprezentaci programu.\n\n");
    printf("Parametry: --help Vypíše tuto nápovědu.\n\n");
    printf("Vrací: 10 - chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů;\n");
    printf("       11 - chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění);\n");
    printf("       12 - chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu);\n");
    printf("       21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode22;\n");
    printf("       22 - eznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22;\n");
    printf("       23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
    printf("       99 - interní chyba (neovlivněná vstupními soubory či parametry příkazové řádky; např. chyba alokace paměti).\n");
}
?>