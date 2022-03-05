<?php
require("/data/soubory/prace/vysoka/2-LS/IPP/ipp/utils.php");

ini_set('display_errors', 'stderr');
handleScriptArgs($argc, $argv);
parse();

/**
 * Zpracuje zadane parametry skriptu.
 * @param $argc int Pocet parametru skiptu.
 * @param $argv array Argumenty skriptu.
 * @return void
 */
function handleScriptArgs(int $argc, array $argv) {
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
 * Zkontroluje, jestli pocet parametru sedi na typ instrukce.
 * @param $instruction string Jmeno instrukce.
 * @param $args string[] Argumenty instrukce.
 * @return bool Zda pocet parametru odpovida dane instrukci.
 */
function checkNOArgs(string $instruction, array $args): bool
{
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

/**
 * Kontroluje typ neterminalu <symb>.
 * @param $arg string Argument dane instrukce.
 * @param $xmlWrt XMLWriter Objekt, s generovanym XML dokumentem.
 * @return bool Zda je argument typem neterminalu <symb>.
 */
function isSymbOk(string $arg, XMLWriter $xmlWrt): bool
{
    // symbol muze byt i promenna
    if(isVarOk($arg, $xmlWrt))
        return true;

    if(str_starts_with($arg, "int@")) {
        $xmlWrt->writeAttribute("type", "int");
        $xmlWrt->text(preg_replace("/^int@/", "", $arg));
        return preg_match("/^int@[+-]?[0-9]+$/", $arg) == 1;
    }
    elseif(str_starts_with($arg, "string@")) {
        $xmlWrt->writeAttribute("type", "string");
        $xmlWrt->text(preg_replace("/^string@/", "", $arg));
        return preg_match("/^string@([^\s#\\\]|\\\[0-9][0-9][0-9])*$/", $arg) == 1;
    }
    elseif(str_starts_with($arg, "bool@")) {
        $xmlWrt->writeAttribute("type", "bool");
        $xmlWrt->text(preg_replace("/^bool@/", "", $arg));
        return (strcmp("bool@true", $arg) == 0 || strcmp("bool@false", $arg) == 0);
    }
    else{
        $xmlWrt->writeAttribute("type", "nil");
        $xmlWrt->text("nil");
        return strcmp("nil@nil", $arg) == 0;
    }
}

/**
 * Kontroluje typ neterminalu <var>.
 * @param $arg string Argument dane instrukce.
 * @param $xmlWrt XMLWriter Objekt, s generovanym XML dokumentem.
 * @return bool Zda je argument typem neterminalu <var>.
 */
function isVarOk(string $arg, XMLWriter $xmlWrt): bool
{
    if(preg_match("/^(GF@|TF@|LF@)/", $arg) == 0)
        return false;

    $xmlWrt->writeAttribute("type", "var");
    $xmlWrt->text($arg);

    $id = preg_replace("/^(GF@|TF@|LF@)/", "", $arg);
    // cast za oznacenim ramce je odpovida syntaxi labelu
    return preg_match("/^[_\-$&%*!?a-zA-Z][_\-$&%*!?a-zA-Z0-9]*$/", $id) == 1;
}

/**
 * Kontroluje typ neterminalu <type>.
 * @param $arg string Argument dane instrukce.
 * @param $xmlWrt XMLWriter Objekt, s generovanym XML dokumentem.
 * @return bool Zda je argument typem neterminalu <type>.
 */
function isTypeOk(string $arg, XMLWriter $xmlWrt): bool
{
    $xmlWrt->writeAttribute("type", "type");
    $xmlWrt->text($arg);
    return strcmp("int", $arg) == 0 || strcmp("string", $arg) == 0 || strcmp("bool", $arg) == 0;
}

/**
 * Kontroluje typ neterminalu <label>.
 * @param $arg string Argument dane instrukce.
 * @param $xmlWrt XMLWriter Objekt, s generovanym XML dokumentem.
 * @return bool Zda je argument typem neterminalu <label>
 */
function isLabelOk(string $arg, XMLWriter $xmlWrt): bool
{
    $xmlWrt->writeAttribute("type", "label");
    $xmlWrt->text($arg);
    return preg_match("/^[_\-$&%*!?a-zA-Z][_\-$&%*!?a-zA-Z0-9]*$/", $arg) == 1;
}

/**
 * Zkontroluje zda typy parametru odpovidaji instukci.
 * @param $instruction string Nazev instrukce
 * @param $args string[] Pole s parametry instrikce
 * @param $xmlWrt XMLWriter Objekt, s generovanym XML dokumentem.
 * @return bool Zda sedi typy argumentu instrukce.
 */
function checkParseArgs(string $instruction, array $args, XMLWriter $xmlWrt): bool
{
    global $instrArguments;
    $argTypes = $instrArguments[$instruction];

    // instukce nema parametry
    if($argTypes == ArgType::None) {
        return true;
    }
    // bude pocitat na jakem parametru se nachazim
    $counter = 1;

    // podle counteru se sdruzi instrukce, ktere maji stejny typ parametru na stejne pozici
    while(sizeof($args) != 0) {
        $xmlWrt->startElement("arg{$counter}");
        switch ($counter) {
            case 1:
                switch($argTypes) {
                    case ArgType::Symb:
                        if(!isSymbOk($args[0], $xmlWrt))
                            return false;
                        break;

                    case ArgType::Label:
                    case ArgType::LabelSymbSymb:
                        if(!isLabelOk($args[0], $xmlWrt))
                            return false;
                        break;

                    default:
                        if(!isVarOk($args[0], $xmlWrt))
                            return false;
                        break;
                }
                break;

            case 2:
                if($argTypes == ArgType::VarType) {
                    if (!isTypeOk($args[0], $xmlWrt))
                        return false;
                }
                else
                    if(!isSymbOk($args[0], $xmlWrt))
                        return false;
                    break;

            case 3:
                if($argTypes != ArgType::VarSymbSymb && $argTypes != ArgType::LabelSymbSymb)
                    return false;
                else {
                    if(!isSymbOk($args[0], $xmlWrt))
                        return false;
                }
                break;
        }
        // posunu se na dalsi parametr tim, ze odeberu z pole ten prvni
        $counter++;
        array_shift($args);
        $xmlWrt->endElement();
    }
    return true;
}

/**
 * Provede lexikalni a syntaktickou analyzu jazyka IPPcode22 ze STDIN a prelozi jej do XML na STDOUT.
 * @return void
 */
function parse() {
    // zkontroluji hlavicku zdrojoveho souboru
    if(!hasHeader()) {
        fprintf(STDERR, "Zdrojový kód neobsahuje povinnou hlavičku!\n");
        exit(ERR_HEADER);
    }

    $xmlWrt = new XMLWriter();
    $xmlWrt->openMemory();
    $xmlWrt->startDocument("1.0", "UTF-8");
    $xmlWrt->startElement("program");
    $xmlWrt->writeAttribute("language", "IPPcode22");
    $xmlWrt->setIndent(true);
    $xmlWrt->setIndentString("    ");

    $order = 1;
    while(($line = fgets(STDIN)) != false) {
        // rozdelim radek na op kod a parametry
        $code = getCode($line);
        if(empty($code)) {
            continue;
        }

        // kontrola instrukce
        $code[0] = strtolower($code[0]);
        if(!isInstr($code[0])) {
            fprintf(STDERR,"Neznámý operační kód: %s\n", $code[0]);
            $xmlWrt->flush();
            exit(ERR_OPP_CODE);
        }

        $instruction = array_shift($code);
        $xmlWrt->startElement("instruction");
        $xmlWrt->writeAttribute("order", $order);
        $xmlWrt->writeAttribute("opcode", strtoupper($instruction));

        // kontrola poctu argumentu instrukce
        if(checkNOArgs($instruction, $code) == false) {
            fprintf(STDERR, "Špatný počet argumentů instrukce: %s\n", $instruction);
            $xmlWrt->flush();
            exit(ERR_LEX_SYN);
        }

        // kontrola typu argumentu instrukce
        if(!checkParseArgs($instruction, $code, $xmlWrt)) {
            fprintf(STDERR, "Špatný typ argumentů instrukce: %s\n", $instruction);
            $xmlWrt->flush();
            exit(ERR_LEX_SYN);
        }
        $xmlWrt->endElement();
        $order++;
    }

    $xmlWrt->endElement();
    $xmlWrt->endDocument();
    echo $xmlWrt->outputMemory();
}

?>