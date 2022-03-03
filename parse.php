<?php
require("./utils.php");

handleScriptArgs($argc, $argv);
parse();

/**
 * Zpracuje zadane parametry skriptu.
 * @param $argc
 * @param $argv
 * @return void
 */
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

/**
 * Radek kodu rozdeli po slovech do pole.
 * @param $line string Radek kodu
 * @return array|false|string[]
 */
function getCode($line) {
    // ziskam pouze aktivni kod
    $line = (str_contains($line, "#") ? strstr($line, "#", true) : $line);
    $line = trim($line);

    return preg_split("/[\s]+/", trim($line), 4, PREG_SPLIT_NO_EMPTY);
}

/**
 * Zkontroluje, jestli pocet parametru sedi na typ instrukce (staticky).
 * V pripade zmeny v instrukcich je treba funkci upravit.
 * @param $instruction string
 * @param $args string[]
 * @return bool zda pocet parametru odpovida dane instrukci
 */
function checkNOArgs($instruction, $args) {
    global $instrArguments;
    switch($instrArguments[$instruction]) {
        case ArgType::None:
            return sizeof($args) == 0;

        case ArgType::Var:
        case ArgType::Symb:
        case ArgType::Label:
            return sizeof($args) == 1;

        case ArgType::VarSymb:
        case ArgType::VarType:
            return sizeof($args) == 2;

        case ArgType::VarSymbSymb:
        case ArgType::LabelSymbSymb:
            return sizeof($args) == 3;
    }
    return false;
}

function checkSymb($arg) {
    if(str_starts_with($arg, "int@-1")) {
        return preg_match("/^int@-?[0-9]+$/", $arg);
    }
    elseif(str_starts_with($arg, "string@")) {
        if(preg_match("/^string@([^\s#\\/]|\\[0-9][0-9][0-9])*$/", $arg) == 0)
            return ERR_LEX_SYN;
        $arg = htmlspecialchars($arg, ENT_QUOTES);
        //TODO generovat
    }
    elseif(str_starts_with($arg, "bool@")) {
        return (strcmp("bool@true", $arg) || strcmp("bool@false", $arg));
    }
    else
        return strcmp("nil@nil", $arg);
}

function checkVar($arg) {
    if(preg_match("/^(GF@|TF@|LF@)/", $arg) == 0)
        return ERR_LEX_SYN;
    $id = preg_replace("/^(GF@|TF@|LF@)/", "", $arg);
    return checkLabel($id);
}

function checkType($arg) {
    return strcmp("int", $arg) || strcmp("string", $arg) || strcmp("bool", $arg);
}

function checkLabel($arg) {
    return preg_match("/^[_\-$&%*!?]?[a-zA-Z0-9]+$/", $arg);
}

function checkParseArgs($instruction, $args) {
    global $instrArguments;
    $argTypes = $instrArguments[$instruction];
    if($argTypes == ArgType::None)
        return true;
    $counter = 0;

    while(sizeof($args) != 0) {
        switch ($counter) {
            case 0:
                switch($argTypes) {
                    case ArgType::Symb:
                        if(checkSymb($args[0]) == 0)
                            return ERR_LEX_SYN;
                        break;

                    case ArgType::Label:
                    case ArgType::LabelSymbSymb:
                        if(checkLabel($args[0]) == 0)
                            return ERR_LEX_SYN;
                        break;

                    default:
                        if(checkVar($args[0]) == 0)
                            return ERR_LEX_SYN;
                        break;
                }
                break;

            case 1:
                if($argTypes == ArgType::VarType)
                    if(checkType($args[0]) == 0)
                        return ERR_LEX_SYN;
                else
                    if(checkSymb($args[0]) == 0)
                        return ERR_LEX_SYN;
                    break;

            case 2:
                if($argTypes != ArgType::VarSymbSymb || $argTypes != ArgType::LabelSymbSymb)
                    return ERR_LEX_SYN;
                else {
                    if(checkSymb($args[0]) == 0)
                        return ERR_LEX_SYN;
                }
                break;
        }
        $counter++;
        array_shift($args);
    }
    return ERR_OK;
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

        // kontrola instrukce
        $code[0] = strtolower($code[0]);
        if(!isInstr($code[0])) {
            fprintf(STDERR,"Neznámý operační kód: %s\n", $code[0]);
            exit(ERR_OPP_CODE);
        }

        // kontrola argumentu op kodu
        $instruction = array_shift($code);
        if(checkNOArgs($instruction, $code) == false) {
            fprintf(STDERR, "Špatný počet argumentů instrukce: %s\n", $instruction);
            exit(ERR_LEX_SYN);
        }
        if(checkParseArgs($instruction, $code) != ERR_OK) {
            fprintf(STDERR, "Špatný typ argumentů instrukce: %s\n", $instruction);
            exit(ERR_LEX_SYN);
        }

    }
}

?>