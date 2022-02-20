<?php
require("./utils.php");

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

function main($argc, $argv){
    handleArgs($argc, $argv);
}

main($argc, $argv);
?>

