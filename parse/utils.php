<?php
const ERR_OK = 0;
const ERR_PARAM = 10;
const ERR_INPUT = 11;
const ERR_OUTPUT = 12;
const ERR_HEADER = 21;
const ERR_OPP_CODE = 22;
const ERR_LEX_SYN = 23;
const ERR_INTERNAL = 99;

/**
 * Hodnoty odpovidaji typu a poradi argumentu, kterych instrukce mohou nabyvat.
 */
enum ArgType {
    case None;
    case Var;
    case Symb;
    case Label;
    case VarType;
    case VarSymb;
    case VarSymbSymb;
    case LabelSymbSymb;
}

/**
 * Klici jsou platne instrukce, kterym je prirazena hodnota odpovidajici poctu a typu jejich argumentu.
 */
$instrArguments= array(
    "err" => false,
    "createframe" => ArgType::None, "pushframe" => ArgType::None, "popframe" => ArgType::None, "return" => ArgType::None,
    "break" => ArgType::None,

    "defvar" => ArgType::Var, "pops" => ArgType::Var,

    "pushs" => ArgType::Symb, "write" => ArgType::Symb, "exit" => ArgType::Symb, "dprint" => ArgType::Symb,

    "call" => ArgType::Label, "label" => ArgType::Label, "jump" => ArgType::Label,

    "read" => ArgType::VarType,

    "move" => ArgType::VarSymb, "not" => ArgType::VarSymb, "int2char" => ArgType::VarSymb, "strlen" => ArgType::VarSymb,
    "type" => ArgType::VarSymb,

    "stri2int" => ArgType::VarSymbSymb, "add" => ArgType::VarSymbSymb, "sub" => ArgType::VarSymbSymb,
    "mul" => ArgType::VarSymbSymb, "idiv" => ArgType::VarSymbSymb, "lt" => ArgType::VarSymbSymb, "gt" => ArgType::VarSymbSymb,
    "eq" => ArgType::VarSymbSymb, "and" => ArgType::VarSymbSymb, "or" => ArgType::VarSymbSymb,
    "concat" => ArgType::VarSymbSymb, "getchar" => ArgType::VarSymbSymb, "setchar" => ArgType::VarSymbSymb,

    "jumpifeq" => ArgType::LabelSymbSymb, "jumpifneq" => ArgType::LabelSymbSymb
);

/**
 * Odebere z radku komentare a vrati jen platny kod.
 * @param $line string Radek vstupu.
 * @return string Radek zbaveny komentaru.
 */
function removeComments($line) {
    $line = (str_contains($line, "#") ? strstr($line, "#", true) : $line);
    $line = trim($line);
    return $line;
}

/**
 * Zkontroluje, jestli ma vstupni kod povinnou hlavicku.
 * @return bool Zda kod obsahuje povinnou hlavicku.
 */
function hasHeader(): bool
{
    while(true) {
        $line = removeComments(fgets(STDIN));
        if(empty($line))
            continue;
        return strcmp(strtolower(".ippcode22"), strtolower($line)) == 0;
    }
}

/**
 * Radek kodu rozdeli po slovech do pole.
 * @param $line string Radek kodu
 * @return false|string[]
 */
function getCode(string $line): array|bool
{
    // ziskam pouze aktivni kod
    $line = removeComments($line);
    return preg_split("/[\s]+/", trim($line), 4, PREG_SPLIT_NO_EMPTY);
}

/**
 * Zkontroluje, zda je instrukce platna.
 * @param $instrString string Kontrolovana instrukce.
 * @return bool Zda je instrukce platna.
 */
function isInstr(string $instrString): bool
{
    global $instrArguments;
    return array_search($instrString, array_keys($instrArguments)) != false;
}

/**
 * Vypise napovedu pro spusteni skriptu.
 * @return void
 */
function writeHelp() {
    printf("Na??te ze standardn??ho vstupu zdrojov?? k??d v IPP-code22, zkontroluje lexik??ln?? a ");
    printf("syntaktickou spr??vnost k??du a vyp????e na standardn?? v??stup XML reprezentaci programu.\n\n");
    printf("Parametry: --help Vyp????e tuto n??pov??du.\n\n");
    printf("Vrac??: 10 - chyb??j??c?? parametr skriptu (je-li t??eba) nebo pou??it?? zak??zan?? kombinace parametr??;\n");
    printf("       11 - chyba p??i otev??r??n?? vstupn??ch soubor?? (nap??. neexistence, nedostate??n?? opr??vn??n??);\n");
    printf("       12 - chyba p??i otev??en?? v??stupn??ch soubor?? pro z??pis (nap??. nedostate??n?? opr??vn??n??, chyba p??i z??pisu);\n");
    printf("       21 - chybn?? nebo chyb??j??c?? hlavi??ka ve zdrojov??m k??du zapsan??m v IPPcode22;\n");
    printf("       22 - ezn??m?? nebo chybn?? opera??n?? k??d ve zdrojov??m k??du zapsan??m v IPPcode22;\n");
    printf("       23 - jin?? lexik??ln?? nebo syntaktick?? chyba zdrojov??ho k??du zapsan??ho v IPPcode22.\n");
    printf("       99 - intern?? chyba (neovlivn??n?? vstupn??mi soubory ??i parametry p????kazov?? ????dky; nap??. chyba alokace pam??ti).\n");
}

?>