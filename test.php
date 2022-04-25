
<?php
ini_set('display_errors', 'stderr');
/**
 * vypise help na standardni vystup
 */
function help_argument($arguments){
    if(array_key_exists("help", $arguments)){
        if(count($arguments) == 1){
            echo "\tIPP projekt 2022\n\tJuraj Hatala (xhatal01)\n\tTestovací rámec (test.php)\n\n\n";
            echo "\t--help - vypise napovedu, nekombinovat s inymi prepinacmi\n";
            echo "\t--directory= - zadaj adresar obsahujuci testujuce subory\n";  
            echo "\t--recursive - prehladaj aj vsetky podadresara zadaneho adresara s testami\n";
            echo "\t--int-script= - zadaj cestu k interpretu\n";
            echo "\t--parce-script - zadaj cestu k parseru\n";   
            echo "\t--int-only - spusti iba testovanie interpretu\n";
            echo "\t--parse-only - spusti iba testovanie parseru\n";
            echo "\t--noclean - ponechaj docasne subory\n\n";
            exit(0);
        }
        else{
            exit(10);
        }
    }
}

/**
 * zparsuje argumenty prikazovej riadky
 */
function read_command_line_arguments(&$arguments){
    $shortop  = "";
    $longop  = array("help",
                     "directory:",  
                     "int-script:",
                     "parse-script:",   
                     "int-only",
                     "parse-only",
                     "recursive",
                     "noclean",
                     "jexampath:",
                     );

    $arguments = getopt($shortop, $longop);
}

/**
 * zkontroluje ci je kombinacia argumentov validna
 */
function chack_arguments($arguments){
    if(array_key_exists("int-only",$arguments)){
        
        if(array_key_exists("parse-only",$arguments) || array_key_exists("parse-script",$arguments)){
            exit(10);
        }
    }
    else if(array_key_exists("parse-only",$arguments)){
        if(array_key_exists("int-only",$arguments) or array_key_exists("int-script",$arguments)){
            exit(10);
        }
    }
}

/**
 * zpracuje argumenty prikazovej riadky
 */
function handle_arguments(){
    $arguments = array();
    
    read_command_line_arguments($arguments);
    chack_arguments($arguments);
    help_argument($arguments);
    
    return $arguments;
}

/**
 * ulozi testovacie subory do pola $all_test_files
 */
function search_test_files($arguments, &$all_test_files){
    $current_dir=getcwd();
    $test_dir = realpath($arguments["directory"]);
    if(file_exists($test_dir)){
        if(array_key_exists("recursive", $arguments)){
            search_test_files_recursive($current_dir, $test_dir, $all_test_files);
        }
        else{
            search_test_files_nonrecursive($test_dir, $all_test_files);
        } 
    }
    else{
        exit(41);
    }
}

/**
 * rekurzivne prechadza adresar az kym neprecita vsetky subory, ak subory .src .in ... uklada do array all_test_files 
 */
function search_test_files_recursive($current_dir, $Dir,&$all_test_files){
    $files = scandir($Dir);
    foreach($files as $file_name){
        $path_to_file = $Dir.'/'.$file_name;

        if(!preg_match("/\./",$file_name)){                  //ak sa nenachadza v nazve . teda adresar tak ho rekurzivne otvor
            search_test_files_recursive($current_dir,$path_to_file,$all_test_files);
        }
        elseif(!preg_match("/^((\.)|(\.\.))$/",$file_name)){                                           //ak som narazil na file tak ho uloz
            save_test_file($all_test_files, $file_name, $path_to_file);
        }   
    }
}

/**
 * ulozi vsetky testovacie subory v zadanom adresari do pola $all_test_files
 */
function search_test_files_nonrecursive($Dir, &$all_test_files){
    $files=scandir($Dir);
    
    foreach($files as $file_name){
        $path_to_file = $Dir.'/'.$file_name;
    
        if(!preg_match("/^((\.)|(\.\.))$/",$file_name)){                                           //ak som narazil na file tak ho uloz
            save_test_file($all_test_files, $file_name, $path_to_file);
        }
    }   
}

/**
 * ulozi testovaci subor $file_name, do pola $all_test_files
 */
function save_test_file(&$all_test_files, $file_name, $path_to_file){
    if(preg_match("/\.src$/",$file_name))     {array_push($all_test_files["src"], $path_to_file);}    //$current_dir."/".
    elseif(preg_match("/\.in$/",$file_name))  {array_push($all_test_files["in"], $path_to_file);}
    elseif(preg_match("/\.out$/",$file_name)) {array_push($all_test_files["out"], $path_to_file);}
    elseif(preg_match("/\.rc$/",$file_name))  {array_push($all_test_files["rc"], $path_to_file);}
}

/**
 * zisti z argumentov ci ma vymazavat docasne subory a informaciu ulozi do $destroy_tmp_files
 */
function is_clean_run($arguments, &$destroy_tmp_files){
    if(array_key_exists("noclean", $arguments)){
        $destroy_tmp_files = false;
    }
    else{
        $destroy_tmp_files = true;
    }
}

/**
 * hlada parse.php ak nie je zadana cesta v argumente tak ho hlda v sucastnom adresary
 */
function search_scripts(&$parse_script,&$interpret_script, $arguments){
    search_parse_script($parse_script,$arguments);    
    serch_interpret_script($interpret_script, $arguments);
}

/**
 * vyhlada jexampath subory, bud v adresary vlozenom v argumentoch prikazovej riadky alebo z predvoleneho adresaru
 */
function search_jexampath($arguments, &$jexam_options, &$jexam_jar){
   
    if (array_key_exists("jexampath", $arguments)){
        $Dir = realpath($arguments["jexampath"]);

        $File_name_reg = "/^jexamxml.jar/";
        if(!search_file_in_Dir($Dir, $File_name_reg, $jexam_jar)){
            exit(41);
        }

        $File_name_reg = "/^options$/";
        if(!search_file_in_Dir($Dir, $File_name_reg, $jexam_options)){
            exit(41);
        }   
    }
    else{
        $jexam_jar = "/pub/courses/ipp/jexamxml/jexamxml.jar";
        $jexam_options = "/pub/courses/ipp/jexamxml/options";
    }

    if(!file_exists($jexam_jar) || !file_exists($jexam_options)){
        exit(41);
    }
}

/**
 * vyhlada script parsera, bud v adresary vlozenom v argumentoch prikazovej riadky, alebo v sucastnom adresary
 */
function search_parse_script(&$parse_script, $arguments){
    if(array_key_exists("parse-script", $arguments)){                                        //ak nie je zadany parameter hladaj parse.php v sucastnom adresari
        $parse_script = realpath($arguments["parse-script"]);
    }
    else{
        $parse_script = "./parse.php";
    }

    if(!file_exists($parse_script)){
        exit(41);
    }
}

/**
 * vyhlada script interpretu, bud v adresary vlozenom v argumentoch prikazovej riadky, alebo v sucastnom adresary
 */
function serch_interpret_script(&$interpret_script, $arguments){
    if(array_key_exists("int-script", $arguments)){                                        //ak nie je zadany parameter hladaj parse.php v sucastnom adresari
        $interpret_script = realpath($arguments["int-script"]);
    }
    else{
        $interpret_script = "./interpret.py";
    }

    if(!file_exists($interpret_script)){
        exit(41);
    }
}

/**
 * vyhldaj subor v sucastnom adreasary
 */
function search_file_in_current_Dir($File_name_reg, &$save_file){
    $my_dir = getcwd();
    
    $files = scandir($my_dir);
    
    foreach($files as $file){
        if(preg_match($File_name_reg,$file)){                  //ak sa nenachadza v nazve . teda adresar tak ho rekurzivne otvor
            $save_file = $my_dir.'/'.$file;
        }
    }
}

/**
 * vyhladaj subor v zadanom adresary
 */
function search_file_in_Dir($Dir, $File_name_reg, &$save_file){
    $files = scandir($Dir);
    
    foreach($files as $file){
        if(preg_match($File_name_reg,$file)){                  
            $save_file = $Dir.'/'.$file;
            return true;
        }
    }
    return false;
}

/**
 * K [name].src suboru najde v poli all_test_files [name].in, [name].rc, [name].out subory.Ak subory nenajde vytvory nove. 
 * Subori uklada do pola current_test kde sa budu nachadzat 4 subory potrebne pre jeden test
 */
function build_current_test($all_test_files,&$current_test,$srcFile){
    $current_test["src"]=$srcFile;

    $expected_rc_file=preg_replace("/\.src$/",'.rc',$srcFile);
    $expected_in_file=preg_replace("/\.src$/",'.in',$srcFile);
    $expected_out_file=preg_replace("/\.src$/",'.out',$srcFile);
    
    if(in_array($expected_rc_file, $all_test_files["rc"])){
        $current_test["rc"]=$expected_rc_file;
    }
    else{
        fopen($expected_rc_file,"w");
        file_put_contents($expected_rc_file,"0");
        $current_test["rc"]=$expected_rc_file;
    }

    if(in_array($expected_in_file,$all_test_files["in"])){
        $current_test["in"]=$expected_in_file;
    }
    else{
        fopen($expected_in_file,"w");
        $current_test["in"]=$expected_in_file;
    }

    if(in_array($expected_out_file,$all_test_files["out"])){
        $current_test["out"]=$expected_out_file;
    }
    else{
        fopen($expected_out_file,"w");
        $current_test["out"]=$expected_out_file;
    }
    
}

/**
 * precita output jexamexm, ak bol current_test uspesny vypise uspech na vystup, ak nie tak vypise neuspech pripadne vymaze vytvoreny logfile
 */
function check_jexaxml_output($destroy_tmp_files, $testedFile, $nbTest, $return_code,$current_dir,&$unsucessfulTests,&$sucessfulTests){
    if($return_code==0){
        test_success($destroy_tmp_files, $nbTest,$sucessfulTests,$current_dir,$testedFile);
        return true;
    }
    else{
        test_failed($destroy_tmp_files, $nbTest,$unsucessfulTests,$current_dir,$testedFile);
        return false;
    }
}

/**
 * vypise informaciu o neuspesnosti testu na stdout v html formate, a zvisi hodnotu pocitadla neuspesnych testov
 */
function test_failed($destroy_tmp_files, $nbTest, &$unsucessfulTests, $current_dir, $testedFile){
    echo "<tr style=\"background-color: #FF5C0A  ;\"><td>test$nbTest</td><td>$testedFile</td></tr>\n";    
    $unsucessfulTests++;
        if(file_exists($current_dir.'/test'.$nbTest.'.xml.log')){
            if ($destroy_tmp_files){
                unlink($current_dir.'/test'.$nbTest.'.xml.log');
            }
        }
}

/**
 * vypise informaciu o uspesnosti testu na stdout v html formate, a zvisi hodnotu pocitadla uspesnych testov
 */
function test_success($destroy_tmp_files, $nbTest, &$sucessfulTests, $current_dir, $testedFile){
    echo "<tr style=\"background-color: #73B0FF ;\"><td>test$nbTest</td><td>$testedFile</td></tr>\n";
    $sucessfulTests++;
    if(file_exists($current_dir.'/test'.$nbTest.'.xml.log')){
        if($destroy_tmp_files){
            unlink($current_dir.'/test'.$nbTest.'.xml.log');
        }
    }
}

/**
 * zisti ci je navratova hodnota znaci uspech
 */
function testing_for_error($file_with_return_code){
    if(file_exists($file_with_return_code)){
        $output = shell_exec('cat '.$file_with_return_code);
        if($output == 0){
            return false;
        }
        else{
            return true;
        }
    }
}

/**
 * spusti interpret na current test a nasmeruje jeho vystup ho do $my_output_file_name
 */
function save_interpret_output_to_file($interpret_script, $current_test, $my_output_file_name,&$return_code){
    exec('python3 '.$interpret_script.' < '.$current_test["in"].' > '.$my_output_file_name.' --source='.$current_test["src"],$trash,$return_code);
}

/**
 * porovna vystupi funkciou diff
 */
function compare_files($corect_output, $my_output){
    exec('diff --strip-trailing-cr '.$my_output.' '.$corect_output,$output,$return_value);
    if($return_value==0){
        return true;
    }
    else{
        return false;
    }
}

/**
 * porovna ci je moja navratova hodnota totozna so spravnou navratovou hodnotou
 */
function compare_return_values($my_return, $correct_return_file){
    $file = fopen($correct_return_file, "r");

    if($correct_return = fgets($file) !== false){
        if($correct_return == $my_return){
            return true;
        }
        else{
            return false;
        }
    }
    else{
        return false;
    }
    
    fclose($file);
}

/**
 * spusti interpret skript na test a zhodnoti vysledok
 */
function interpret_test($destroy_tmp_files, $test_number, $interpret_script, $current_test,&$successful_tests, &$unsuccessful_tests){
    $current_dir=getcwd();
    $my_output_file_name="interpret_output.out";
    $my_return="";
    $file = fopen($my_output_file_name,"w");

    save_interpret_output_to_file($interpret_script, $current_test,$my_output_file_name,$my_return);

    if(testing_for_error($current_test["rc"])){
        if(compare_return_values($my_return, $current_test["rc"])){
            test_success($destroy_tmp_files, $test_number,$successful_tests,$current_dir,$current_test["rc"]);
        }            
        else{
            test_failed($destroy_tmp_files, $test_number, $unsuccessful_tests,$current_dir,$current_test["rc"]);
        }
    }
    else{
        $corect_output = $current_test["out"];
        if(compare_files($corect_output, $my_output_file_name)){
            test_success($destroy_tmp_files, $test_number,$successful_tests,$current_dir,$current_test["rc"]);
        }
        else{
            test_failed($destroy_tmp_files, $test_number,$unsuccessful_tests,$current_dir,$current_test["rc"]);
        }                  
    }
    if ($destroy_tmp_files){
        unlink($my_output_file_name);
    }
    fclose($file);
}

/**
 * ulozi zadany xml subor do testovacie pola
 */
function save_XMLfile_in_test(&$current_test, $file_name){
    $current_test["src"] = $file_name;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////// "main" ///////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
$arguments = handle_arguments();

$all_test_files = array(
    "src" => array(),
    "in" => array(),
    "out" => array(),
    "rc" => array(),
);
search_test_files($arguments, $all_test_files);

$parse_script;
$interpret_script;
search_scripts($parse_script,$interpret_script, $arguments);

$jexam_jar;
$jexam_options;
search_jexampath($arguments, $jexam_options, $jexam_jar);

$destroy_tmp_files = true;
is_clean_run($arguments, $destroy_tmp_files);

$successful_tests = 0;
$unsuccessful_tests = 0;

echo "<html> <head><title>Tests</title></head> <body><table> <tr><th>TestReference<th>FileName</th></tr>";

for ($i=0; $i < count($all_test_files["src"]); $i++) {                                                       //porovnavam tolko suborov kolko som nasiel .src suborov
    $current_test = array();
    build_current_test($all_test_files, $current_test, $all_test_files["src"][$i]);
    if(array_key_exists("parse-only", $arguments)){
        unset($out);

        $parser_output_file_name = "tmp_parser.xml";
        $file = fopen($parser_output_file_name,"w");
        
        $cur_dir = getcwd();
        $parser_output_file_path = $cur_dir."/".$parser_output_file_name;
        
        exec('php '.$parse_script.' < '.$all_test_files["src"][$i].' > '.$parser_output_file_path, $out, $my_return);                                 //spusti parse.php na testovany src subor
    
        if($my_return == 0){                                                     
            $corect_output = $current_test["out"];
            $java_output = array();
            $return_code;

            exec("java -jar ".$jexam_jar." ".$parser_output_file_path." ".$corect_output." /dev/null ".$jexam_options , $java_output, $return_code);        //porovnaj docasny subor s ocakavanym vystupom .out
            check_jexaxml_output($destroy_tmp_files, $corect_output,$i, $return_code,$cur_dir,$unsuccessful_tests,$successful_tests);                                                   //interpretuj vysledok porovnania  a vymaz logfiles
            
            if ($destroy_tmp_files){                //vymaz docasny subor
                unlink($parser_output_file_path);
            }
        }
        else{
            $corect_return_file = fopen($current_test["rc"],"r");
            if(!feof($corect_return_file)){
                $corect_return = fgets($corect_return_file);
                if($my_return == $corect_return){
                    test_success($destroy_tmp_files, $i, $successful_tests, $cur_dir, $current_test["out"]);
                }
                else{test_failed($destroy_tmp_files, $i,$unsuccessful_tests,$cur_dir,$current_test["out"]);}
            }
            else{test_failed($destroy_tmp_files, $i, $unsuccessful_tests, $cur_dir, $current_test["out"]);}
            fclose($corect_return_file);
        }
        fclose($file);
    }
    else if(array_key_exists("int-only",$arguments)){
        interpret_test($destroy_tmp_files, $i, $interpret_script, $current_test,$successful_tests, $unsuccessful_tests);
    }
    else{
        
        unset($out);
        $parse_output_file_name = 'parser_output.src';
        $current_dir=getcwd();
        $file = fopen($parse_output_file_name,"w");
        exec('php '.$parse_script.' < '.$all_test_files["src"][$i].' > '.$parse_output_file_name, $out, $my_return); 
        $parse_output_file = $current_dir.'/'.$parse_output_file_name;
        
        if($my_return == 0){                                                     //ak parsovanie prebehlo do konca a docasny subor existuje...
            save_XMLfile_in_test($current_test, $parse_output_file);
            interpret_test($destroy_tmp_files, $i, $interpret_script, $current_test, $successful_tests, $unsuccessful_tests);
        }
        else{
            $corect_return = fopen($current_test["rc"],"r");
            if(!feof($corect_return)){
                if($my_return==fgets($corect_return)){
                    test_success($destroy_tmp_files, $i, $successful_tests, $current_dir, $current_test["out"]);
                }
                else{test_failed($destroy_tmp_files, $i, $successful_tests, $current_dir, $current_test["out"]);}
            }
            else{test_failed($destroy_tmp_files, $i, $successful_tests, $current_dir, $current_test["out"]);}
            fclose($corect_return);
        }
        if ($destroy_tmp_files){
            unlink($parse_output_file_name);
        }
        fclose($file);
    }

}
echo "</table>
        <h1>successful tests: $successful_tests </h1>
        <h1>unsuccessful tests: $unsuccessful_tests </h1>
        </body>
        </html> ";

?>