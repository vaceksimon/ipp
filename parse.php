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

function isSymbOk($arg) {
    // symbol muze byt i promenna
    if(isVarOk($arg))
        return true;

    if(str_starts_with($arg, "int@")) {
        return preg_match("/^int@-?[0-9]+$/", $arg) == 1;
    }
    elseif(str_starts_with($arg, "string@")) {
        return preg_match("/^string@([^\s#\\\]|\\\[0-9][0-9][0-9])*$/", $arg) == 1;
    }
    elseif(str_starts_with($arg, "bool@")) {
        return (strcmp("bool@true", $arg) == 0 || strcmp("bool@false", $arg) == 0);
    }
    else
        return strcmp("nil@nil", $arg) == 0;
}

function isVarOk($arg) {
    if(preg_match("/^(GF@|TF@|LF@)/", $arg) == 0)
        return false;
    $id = preg_replace("/^(GF@|TF@|LF@)/", "", $arg);
    return isLabelOk($id);
}

function isTypeOk($arg) {
    return strcmp("int", $arg) == 0 || strcmp("string", $arg) == 0 || strcmp("bool", $arg) == 0;
}

function isLabelOk($arg) {
    return preg_match("/^[_\-$&%*!?]?[a-zA-Z0-9]+$/", $arg) == 1;
}

/**
 * Zkontroluje datove zda parametry odpovidaji instukci.
 *
 * @param $instruction string Nazev instrukce
 * @param $args string[] Pole s parametry instrikce
 * @return
 */
function checkParseArgs(string $instruction, array $args) {
    global $instrArguments;
    $argTypes = $instrArguments[$instruction];

    // instukce nema parametry
    if($argTypes == ArgType::None) {
        return true;
    }
    // bude pocitat na jakem parametru se nachazim
    $counter = 0;

    // podle counteru se sdruzi instrukce, ktere maji stejny typ parametru na stejne pozici
    while(sizeof($args) != 0) {
        switch ($counter) {
            case 0:
                switch($argTypes) {
                    case ArgType::Symb:
                        if(!isSymbOk($args[0]))
                            return false;
                        break;

                    case ArgType::Label:
                    case ArgType::LabelSymbSymb:
                        if(!isLabelOk($args[0]))
                            return false;
                        break;

                    default:
                        if(!isVarOk($args[0]))
                            return false;
                        break;
                }
                break;

            case 1:
                if($argTypes == ArgType::VarType) {
                    if (!isTypeOk($args[0]))
                        return false;
                }
                else
                    if(!isSymbOk($args[0]))
                        return false;
                    break;

            case 2:
                if($argTypes != ArgType::VarSymbSymb || $argTypes != ArgType::LabelSymbSymb)
                    return false;
                else {
                    if(!isSymbOk($args[0]))
                        return false;
                }
                break;
        }
        // posunu se na dalsi parametr tim, ze odeberu z pole ten prvni
        $counter++;
        array_shift($args);
    }
    return true;
}

function parse() {
    // zkontroluji hlavicku zdrojoveho souboru
    if(!hasHeader()) {
        fprintf(STDERR, "Zdrojový kód neobsahuje povinnou hlavičku!\n");
        exit(ERR_HEADER);
    }

    while(($line = fgets(STDIN)) != false) {
//        echo $line;
        // rozdelim radek na op kod a parametry
        $code = getCode($line);
        if(empty($code)) {
            continue;
        }
//        var_dump($code);
//        foreach($code as $item)
//            printf("%s,", $item);
//        echo "\n";

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
        if(!checkParseArgs($instruction, $code)) {
            fprintf(STDERR, "Špatný typ argumentů instrukce: %s\n", $instruction);
            exit(ERR_LEX_SYN);
        }

    }
}

?>