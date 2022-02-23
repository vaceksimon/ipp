<?php
require("./utils.php");

handleArgs($argc, $argv);
parse();

function handleArgs($argc, $argv) {
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

    $arr = preg_split("/[\s]+/", trim($line), 4, PREG_SPLIT_NO_EMPTY);
    return $arr;
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
        $code = getCode($line);
    }
}

?>

