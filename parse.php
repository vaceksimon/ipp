<?php
require("./utils.php");

handleScriptArgs($argc, $argv);
parse();

function handleScriptArgs($argc, $argv) {
    if($argc <= 1)
        return;
    // parser dostal parametr
    for($i = 1; $i < $argc; $i++) {
        if(!strcmp("--help", $argv[$i])) {
            if($argc != 2) {
                fprintf(STDERR, "Parametr --help nelze kombinovat s jinými parametry.\n");
                exit(ERR_PARAM);
            }
            writeHelp();
            exit(ERR_OK);
        }
        else {
            fprintf(STDERR,"Neznámý parametr skriptu: %s.\n", $argv[$i]);
            exit(ERR_PARAM);
        }
    }
}

function getCode($line) {
    // ziskam pouze aktivni kod
    $line = (str_contains($line, "#") ? strstr($line, "#", true) : $line);
    $line = trim($line);

    return preg_split("/[\s]+/", trim($line), 4, PREG_SPLIT_NO_EMPTY);
}

function parse() {
    // zkontroluji hlavicku zdrojoveho souboru
    $line = fgets(STDIN);
    $line = (str_contains($line, "#") ? strstr($line, "#", true) : $line);
    $line = trim($line);

    if(!$line || (strcmp(strtolower(".ippcode22"), strtolower($line)) != 0)) {
        fprintf(STDERR, "Zdrojový kód neobsahuje povinnou hlavičku!\n");
        exit(ERR_HEADER);
    }
    // ctu radek po radku
    while(($line = fgets(STDIN)) != false) {
        // rozdelim radek na op kod a parametry
        $code = getCode($line);
        if(empty($code))
            continue;

        // kontrola operacniho kodu
        $instrIndex = checkInstr($code[0]);
        if($instrIndex == ERR_OPP_CODE) {
            fprintf(STDERR,"Neznámý operační kód: %s\n", $code[0]);
            exit(ERR_OPP_CODE);
        }

        // kontrola argumentu op kodu

        // TODO checkOppArgs($instrIndex);
    }
}

?>