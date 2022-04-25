<?php
ini_set('display_errors', 'stderr');

/**
 * trieda do ktorej sa zapisuju informacie o instrukcii
 */
class Instruction {
    public $name;
    public $order;
    public $arg1;
    public $arg2;
    public $arg3;
    
    /**
     * inicializacia argumentou 
     */
    function __construct(){
        $this->arg1=NULL;
        $this->arg2=NULL;
        $this->arg3=NULL;
    }

    /**
     * zapise meno instrukcie
     */
    function set_name($new_name){
        $this->name=strtoupper($new_name);
    }

    /**
     * zapise cislo instrukcie
     */
    function set_order($new_order){
        $this->order=$new_order;
    }

    /**
     * nastavi nty argumnet ako premennu
     */
    function set_arg_to_var($argnb, $frame, $name){
        $this->{"arg".$argnb} = array (
            0 => "var",
            1 => $frame,
            2 => $name,
        );
    }

    /**
     * nastavi nty argumnet ako navestie
     */
    function set_arg_to_label($argnb,$name){
        $this->{"arg".$argnb} = array (
            0 => "label",
            1 => $name,
        );
    }

    /**
     * nastavi nty argumnet ako typ
     */
    function set_arg_to_type($argnb,$type){
        $this->{"arg".$argnb} = array (
            0 => "type",
            1 => $type,
        );
    }

    /**
     * nastavi nty argumnet ako kontsantu
     */
    function set_arg_to_constant($argnb, $type, $value){
        $this->{"arg".$argnb} = array (
            0 => $type,
            1 => $type,
            2 => $value,
        );
    }
}

/**
 * objekt zabezbecujuci zbieranie informacii o statistikach a vytvaranie statistickych suborov 
 */
class Stats{
    public array $stat_files;
    public array $label_array;
    public array $backward_jumps_array;
    public array $waiting_jumps_array;

    public int $labels;
    public int $jumps;

    public int $bad_jumps;
    public int $backward_jumps;
    public int $forward_jumps;
    public int $comments;
    public int $instructions;

    /**
     * inicializuje pocitadla a pole stat_files
     */
    function __construct(){
        $this->stat_files = array();
        $this->label_array = array();
        $this->waiting_jumps_array = array();

        $this->labels = 0;
        $this->jumps = 0;
        $this->forward_jumps = 0;
        $this->backward_jumps = 0;
        $this->bad_jumps = 0;
        $this->comments = 0;
        $this->instructions = 0;
    }

    /**
     * zvysi hodnotu labels pocitadla o jedna
     */
    protected function add_label(){
        $this->labels=$this->labels + 1;
    }

    /**
     * zvysi hodnotu jumps pocitadla o jedna
     */
    protected function add_jump(){
        $this->jumps=$this->jumps + 1;
    }

    function save_label_name($label_name){
        $this->label_array[$label_name] = "";
    }

    function save_waiting_jump($label_name){
        $this->waiting_jumps_array[$label_name] = "";
    }

    function save_backward_jump($label_name){
        $this->backward_jumps = $this->backward_jumps + 1;
    }

    function save_forward_jump($label_name){
        $this->forward_jumps = $this->forward_jumps + 1;
    }

    function save_bad_jump($label_name){
        $this->bad_jumps = $this->bad_jumps + 1;
    }

    function is_backward_forward_jump($label_name){
        if(array_key_exists($label_name, $this->label_array)){
            $this->save_backward_jump($label_name);
        }
        else{
            $this->save_waiting_jump($label_name); 
        }
    }

    function find_forward_bad_jumps(){
        foreach ($this->waiting_jumps_array as $label){
            if(array_key_exists($label, $this->label_array)){
                $this->save_forward_jump($label);
            }
            else{
                $this->save_bad_jump($label);
            }
        }
    }

    /**
     * ak sa jedna o instrukciu label alebo jednu z jump instrukci zapocita ju do pocitadla 
     */
    function if_jump_label_count($instuction_name, $label_name){
        $instuction_name=strtolower($instuction_name);
        
        if(strcmp($instuction_name,"label")==0){
            
            $this->add_label();
            $this->save_label_name($label_name);
        }
        elseif((strcmp($instuction_name,"jump") == 0) || (strcmp($instuction_name,"jumpifeq") == 0) || (strcmp($instuction_name,"jumpifneq") == 0)){  
            $this->add_jump();
            $this->is_backward_forward_jump($label_name);
        }
    }

    /**
     * zvysi hodnotu comments pocitadla o jedna
     */
    function add_comment(){
        $this->comments = $this->comments + 1;
    }

    function add_instruction(){
        $this->instructions = $this->instructions + 1;
    }

    /**
     * z argumentou prikazovaj riadky ziskava informacie pre statisticke subory
     * ktore uklada to stat_files
     */
    function parse_arguments($argv, $argc){
        $source_file='';
        if($argc>1){
            foreach ($argv as $arg){
                if(substr_compare($arg, "--stats=", 0, 8) == 0){
                    $source_array=str_split($arg, $split_point = 9);
                    if(empty($source_array[1])){
                        exit(10);
                    }
                    else{
                        $source_file=$source_array[1];
                        $this->stat_files[$source_file]=array();
                    }
                }
                elseif(strcmp($arg,"--loc") == 0 || strcmp($arg,"--comments") == 0 || strcmp($arg,"--labels") == 0 || strcmp($arg,"--jumps") == 0){
                    if(empty($source_file)){
                        exit(10);
                    }
                    elseif(in_array($arg,$this->stat_files[$source_file])){
                        exit(12);
                    }
                    else{
                        array_push($this->stat_files[$source_file],$arg);
                    }
                }
                elseif(!strcmp(substr($arg,-9),"parse.php") == 0){
                    exit(12);
                }
            }
        }
    }
    
    /**
     * vytvori statisticke subory podla informacii z pola stat_files
     */
    function create_file(){
        foreach($this->stat_files as $file => $contents){
            $one_stat_file = fopen($file,"w");
            foreach($contents as $content){
                if(strcmp($content,"--labels") == 0)
                    fwrite($one_stat_file,$this->labels."\n");
                elseif(strcmp($content,"--comments") == 0){
                    fwrite($one_stat_file,$this->comments."\n");
                }
                elseif(strcmp($content,"--jumps") == 0){
                    fwrite($one_stat_file,$this->jumps."\n");
                }
                elseif(strcmp($content,"--loc") == 0){
                    fwrite($one_stat_file,$this->instructions."\n");
                }
                elseif(strcmp($content,"--fwjumps") == 0){
                    fwrite($one_stat_file,$this->forward_jumps."\n");
                }
                elseif(strcmp($content,"--backjumps") == 0){
                    fwrite($one_stat_file,$this->backward_jumps."\n");
                }
                elseif(strcmp($content,"--badjumps") == 0){
                    fwrite($one_stat_file,$this->bad_jumps."\n");
                }
            }
        }
    }
}

/**
 * Z objektu $instruction vytvory reprezentaciu v xml subore napaja sa na korenovy element v subore $output_file 
 * a $root, na ktore navezuje jednotlive instrukcie
 */
function XML_save_instruction($output_file, $instruction){
    $output_file->startElement('instruction');

    $output_file->startAttribute('order');
    $output_file->text($instruction->order);
    $output_file->endAttribute();

    $output_file->startAttribute('opcode');
    $output_file->text($instruction->name);
    $output_file->endAttribute();

    for ($i=1;$i < 4; $i++) {                       //prechadza a plni vsetky argumenty z objektu do xml suboru
        if($instruction->{"arg".$i} != NULL){
            $output_file->startElement('arg'.$i);
            
            if ($instruction->{"arg".$i}[0] == "var"){      //rozdiel medzy argumentmy var a const
                $output_file->startAttribute('type');
                $output_file->text($instruction->{"arg".$i}[0]);
                $output_file->endAttribute();

                $var=$instruction->{"arg".$i}[1]."@".$instruction->{"arg".$i}[2];
                $output_file->text($var);
            }
            elseif ($instruction->{"arg".$i}[0] == "label" || $instruction->{"arg".$i}[0] == "type"){
                $output_file->startAttribute('type');
                $output_file->text($instruction->{"arg".$i}[0]);
                $output_file->endAttribute();

                $label=$instruction->{"arg".$i}[1];
                $output_file->text($label);
            }
            else{
                $output_file->startAttribute('type');
                $output_file->text($instruction->{"arg".$i}[0]);
                $output_file->endAttribute();

                $constant=$instruction->{"arg".$i}[2];
                $output_file->text($constant);
            }

            $output_file->endElement();
        }
    }
    $output_file->endElement();;
}

/**
 * Vytvori XML objekt
 */
function XML_create_file(){
    $output_file = new XMLWriter(); 
    $output_file->openUri('php://output');              //otvori zapis na stdout
    $output_file->startDocument('1.0', 'UTF-8');
    $output_file->setIndent(true);
    $output_file->startElement('program');
    $output_file->startAttribute('language');
    $output_file->text('IPPcode22');
    $output_file->endAttribute();
    return $output_file;
}

/**
 * ukonci XML zapisovanie
 */
function XML_end_file($output_file){
    $output_file->endElement();
    $output_file->endDocument();
    $output_file->flush();
}

/**
 * odstrani z riadku komentare
 */
function remove_coments(&$line, $stats){
    if(preg_match('/(#.*\s*)|(\/\/.*)/', $line)){
        $line = preg_replace('/(#.*\s*)|(\/\/.*)/',"",$line);
        $stats->add_comment();
    }
}

/**
 * kontroluje ci dane slovo splna vlastnosti premennej, ak ano vklada informacie o premennej do objektu $instruction
 */
function var_save($word,$instruction,$arg_position){
    $word_elem = preg_split("/@/", $word);
    if(count($word_elem)>2){
        exit(23);
    }

    if(preg_match('/^(GF|TF|LF)@([^0-9\/][^\\s]*)$/',$word)){//(LF|TF|GF)@[^$&%*!?][^_-])
        $instruction->set_arg_to_var($arg_position,$word_elem[0],$word_elem[1]);
        return true;
    }
    else{return false;}
}

/**
 * kontroluje ci dane slovo splna vlastnosti navestia, ak ano vklada informacie o navestii do objektu $instruction
 */
function label_save($word,$instruction,$arg_position){
    if(preg_match('/^[a-zA-Z_\\-\$\&\%\\*\?\!][a-zA-Z\_\\-\$\&\%\\*?!0-9]*$/',$word)){//(LF|TF|GF)@[^$&%*!?][^_-])
        $instruction->set_arg_to_label($arg_position,$word);
        return true;
    }
    else{return false;}
}

/**
 * kontroluje ci dane slovo splna vlastnosti typu, ak ano vklada informacie o type do objektu $instruction
 */
function type_check($word,$instruction,$arg_position){
    if(preg_match('/^((int)|(string)|(nil)|(bool))$/',$word)){//(LF|TF|GF)@[^$&%*!?][^_-])
        $instruction->set_arg_to_type($arg_position,$word);
        return true;
    }
    else{return false;}
}

/**
 * kontroluje ci dane slovo splna vlastnosti konstanty, ak ano vklada informacie o konstante do objektu $instruction
 */
function const_save($word,$instruction,$arg_position){
    $word_elem = preg_split("/@/", $word, 2);
    if(preg_match('/^(int|string|bool|nil)@/',$word)){//'/^(int|string|bool|nil)@[^\s]/'
        if(constData_check($word_elem[0], $word_elem[1])){
            $instruction->set_arg_to_constant($arg_position,$word_elem[0],$word_elem[1]);
            return true;
        }
        else{return false;}
    }
    else {return false;}
    
}

/**
 *  kontoluje semantiku datovych typov v konstante, ak je vsetko v poriadku vracia true inak false
 */
function constData_check($dataType, $value){
    if($dataType == "int"){
        if(preg_match("/^(-?\+?)[0-9]+$\s?/",$value)){return true;}
    }
    elseif($dataType == "bool"){
        if(preg_match("/^((true)|(false))$/",$value)){return true;}
    }
    elseif($dataType == "nil"){
        if(preg_match("/^nil$/",$value)){return true;}
    }
    elseif($dataType == "string"){
        if(preg_match("/^((\\\\\d{3})|([@ů§\-,;()=a-zA-Z0-9<>\/\\p{L}]))*$/u",$value)||$value==""){
            return true;
        }
        else{return false;}
    }
    else {return false;}
}

/**
 * zisti ci sa jedna o premennu alebo constantu, zkontroluje ich zapis a informacie o nich ulozi do objektu instuction
 */
function symbol_save($word, $instruction,$arg_position){
    if(const_save($word,$instruction,$arg_position)){
        return true;
    }
    elseif(var_save($word,$instruction,$arg_position)){
        return true;
    }
    else{return false;}
}

/**
 * halda hlavicku suboru a kontroluje ci sa pred nevzskituje nieco okrem prazdnych riadkov
 */
function header_chack($File,$stats){

    while(!feof($File)){                            
        $line=fgets($File);                                     //nacitavaj prve riadky
        remove_coments($line,$stats);
        if(preg_match("/^\s*\.IPPcode22\s*$/i",$line)){           //cakaj na hlavicku                         
            break;
        }
        elseif($line!="\n" and $line!="" and $line!="\t"){                      //ak nie su pred hlavikou len prazdne riadky tak vypinaj   
            exit(21);
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////main///////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
$stats=new Stats;
$stats->parse_arguments($argv, $argc);

$output_file = XML_create_file();
$file_to_parse=fopen('php://stdin', 'r' );

header_chack($file_to_parse,$stats);

$order=1;
while(!feof($file_to_parse)){
    $line=fgets($file_to_parse);  
    remove_coments($line, $stats);
    
    if(!preg_match("/^.IPPcode22/", $line) and $line!="\n" and $line!="\r" and $line!=NULL){    //ak nie je prazny riadok
        $stats->add_instruction();
    
        $instruction = new Instruction();
        $args = preg_split("/[\s' ']+/", $line,-1,PREG_SPLIT_NO_EMPTY);     //arg[0] je instruction name
        $instuctionName=$args[0];
        $nbargs=count($args);
        
        $instruction->set_name($instuctionName);
        $instruction->set_order($order);
        $order=$order+1;
        if( preg_match("/^((MOVE)|(INT2CHAR)|(STRLEN)|(TYPE)|(NOT))$/i", $instuctionName)){
            if($nbargs != 3){exit(23);}
            if(!var_save($args[1],$instruction,1)){exit(23);}
            if(!symbol_save($args[2],$instruction,2)){exit(23);}
        }
        else if(preg_match("/^((ADD)|(SUB)|(MUL)|(IDIV)|(LT)|(GT)|(EQ)|(AND)|(OR)|(STRI2INT)|(CONCAT)|(GETCHAR)|(SETCHAR))$/i", $instuctionName)){      //INSTRUCTION <var> <symb> <symb>
            if($nbargs != 4){exit(23);}
            if(!var_save($args[1],$instruction,1)){exit(23);}
            if(!symbol_save($args[2],$instruction,2)){exit(23);}
            if(!symbol_save($args[3],$instruction,3)){exit(23);}
        }
        else if(preg_match("/^((WRITE)|(DPRINT)|(EXIT)|(PUSHS))$/i", $instuctionName)){       //INSTRUCTION <symbol>
            if($nbargs != 2){exit(23);}
            if(!symbol_save($args[1],$instruction,1)){exit(23);}
        }
        else if(preg_match("/^((DEFVAR)|(POPS))$/i", $instuctionName)){                      //INSTRUCTION <var>       
            if($nbargs != 2){exit(23);}      
            if(!var_save($args[1],$instruction,1)){exit(23);}
        }
        else if(preg_match("/^(READ)$/i", $instuctionName)){                                 //INSTRUCTION <var> <type>
            if($nbargs != 3){exit(23);}
            if(!var_save($args[1],$instruction,1)){exit(23);}
            if(!type_check($args[2],$instruction,2)){exit(23);}
        }
        else if(preg_match("/^((LABEL)|(JUMP)|(CALL))$/i", $instuctionName)){                //INSTRUCTION <label>
            if($nbargs != 2){exit(23);}
            if(!label_save($args[1],$instruction,1)){exit(23);}
            $stats->if_jump_label_count($args[0],$args[1]);
        }
        else if(preg_match("/^((JUMPIFEQ)|(JUMPIFNEQ))$/i", $instuctionName)){               //INSTRUCTION <label> <symb> <symb>
            if($nbargs != 4){exit(23);}
            if(!label_save($args[1],$instruction,1)){exit(23);}
            if(!symbol_save($args[2],$instruction,2)){exit(23);}
            if(!symbol_save($args[3],$instruction,3)){exit(23);}
            $stats->if_jump_label_count($args[0],$args[1]);
        }
        else if(preg_match("/^((BREAK)|(RETURN)|(POPFRAME)|(PUSHFRAME)|(CREATEFRAME))$/i", $instuctionName)){
            if($nbargs!=1){exit(23);}
        }
        else{
            exit(22);
        }
        XML_save_instruction($output_file, $instruction);
    }
    else if($line != "\n" and $line != "" ){
        exit(22);
    }
}
$stats->find_forward_bad_jumps();
$stats->create_file();
XML_end_file($output_file);
fclose($file_to_parse);

?>