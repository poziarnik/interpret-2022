
from dis import Instruction
import sys
from sys import stdout
import argparse
import xml.etree.ElementTree as ET
import re

_operators = {'gt' : '>',
             'eq' : '==',
             'lt' : '<',
             'gts' : '>',
             'eqs' : '==',
             'lts' : '<',
             'ors' : 'or',
             'or' : 'or',
             'ands' : 'and',
             'and' : 'and',
             'nots' : 'not',
             'not' : 'not',
             'sub' : '-',
             'subs' : '-',
             'add' : '+',
             'adds' : '+',
             'mul' : '*',
             'muls' : '*',
             'div' : '/',
             'idiv' : '//',
             'idivs' : '//',
             'jumpifeq' : '==',
             'jumpifeqs' : '==',
             'jumpifneq' : '!=',
             'jumpifneqs' : '!='}

def parse_arguments():
    """parsuje argumenty prikazovej rieadky pomocou argparse

    Returns:
        N@parse_args:  pole zpracovanych argumentov
    """    
    parser = argparse.ArgumentParser(description='look for file')
    parser.add_argument('--source',help="input xml file to interpret", nargs=1)
    return parser.parse_args()

def sort_etree_by_order(root):
    """zoradi instrukcie v xml strukture podla atributu order 

    Args:
        root (Element): _description_ koren xml struktury 
    """    
    
    try:
        root[:]=sorted(root,key = lambda child: int(child.get('order')))
    except Exception:
        sys.exit(32)        #ak nenajde order
    
    if _check_if_duplicate_order(root):
        sys.exit(32)

def save_label(child, labels, name, position):
    """ulozi navestie a jeho poziciu v zozname navesti

    Args:
        child (Element):  instrukcia z xml struktury
        labels (dictionary):  zoznam navesti
        name (string):  meno ukladaneho navestia
        position (int):  pozicia ukladaneho navestia
    """    
    
    if(str(name).lower()) == "label":
        name=child[0].text                      
        if name not in labels:
            labels[name] = position
        else:
            sys.exit(52)

def get_varInfo(var):
    """_summary_ zisti ramec a meno premennej

    Args:
        var (string):  predpis premennej

    Returns:
        string: ramec 
        string: meno premennej
    """    
    list = var.split("@")
    return list[0], list[1]

def get_symbolValue(instruction,memory):
    """ vrati hodnotu premennej alebo konstanti

    Args:
        instruction (string): predpis symbolu
        memory (memory_frames): pametovy objekt

    Returns:
        _type_: _description_ hodnota symbolu
    """    
    if instruction.attrib.get("type") == "var":
        var_frame, var_name = get_varInfo(instruction.text)
        return __replace_string_exits(str(memory.get_varValue(var_frame, var_name)))
    else:
        return __replace_string_exits(str(instruction.text))

def get_symbolType(symb,memory):
    """ vrati typ premennej alebo konstanti

    Args:
        symb (string): predpis symbolu
        memory (memory_frames): pamatovy objekt

    Returns:
        string:  typ symbolu
    """    
    if symb.attrib.get("type") == "var":
        var_frame, var_name = get_varInfo(symb.text)
        value = memory.get_vartype(var_frame, var_name)
        
        if value == "string":
            return "string"
        elif value == "int":
            return "int"
        elif value == "bool":
            return "bool"
        elif value == "nil":
            return "nil"
        elif value == "float":
            return "float"
        elif value == "":
            return ""
    else:
        return symb.attrib.get("type")
    
def stack_push_symbol(memory, symbol):
    """vlozi symbol na zasobnik

    Args:
        memory (memory_frames):  pamatovy objekt
        symbol (string): predpis symbolu
    """    
    value = get_symbolValue(symbol, memory)
    type = get_symbolType(symbol, memory)
    
    memory.stack_push_element(value, type)

def check_div_by_zero(value):
    """_summary_ zkontroluje ci je hodnota nulova. Ak nie tak exit, ak ano vrati int value

    Args:
        value (string):  hodnota

    Returns:
        int:  nenulova hodnota
    """    
    intValue = int(value)
    if intValue != 0:
        return intValue
    else:
        sys.exit(57)

def perform_arithmetics_stack(memory, instruction):
    """zpracuje aritmeticke instrukcie na zasobniku

    Args:
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
    """    
    stack_element2 = memory.stack_pop()
    stack_element1 = memory.stack_pop()

    result, type = _stack_elements_operate(memory, stack_element1, stack_element2, _operators[instruction])
    
    memory.stack_push_element(result, type)
        

def perform_arithmetics(root, memory, instruction, instruction_position):
    """zpracuje aritmeticke instrukcie na pamatovych ramcoch

    Args:
        root (Element): koren xml struktury
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
        instruction_position (int): pozicia instrukcie
    """    
    result = _symbols_oprerate(root[instruction_position][1], root[instruction_position][2], memory, _operators[instruction])
    var_frame, var_name=get_varInfo(root[instruction_position][0].text)                                            
    
    if are_both_int(root[instruction_position][1], root[instruction_position][2], memory):
        memory.save_to_var(var_frame, var_name, result, "int")      
    else:
        memory.save_to_var(var_frame, var_name, result, "float")    

def perform_comparsion(root, memory, instruction, instruction_position):
    """spracuje porovnavacie instrukcie na pamatovych ramcoch

    Args:
        root (Element): koren xml struktury
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
        instruction_position (int): pozicia instrukcie
    """    
    symbol1=root[instruction_position][1]
    symbol2=root[instruction_position][2]
    
    if instruction == "eq":
        if __valid_type_comparsion(symbol1,symbol2,memory) or _are_same_type_as(symbol1,symbol2,memory,"nil"):
            if __symbols_compare(symbol1,symbol2,memory,_operators[instruction]):
                var_frame, var_name=get_varInfo(root[instruction_position][0].text)
                memory.save_to_var(var_frame, var_name,"true","bool")
            else:
                var_frame, var_name=get_varInfo(root[instruction_position][0].text)
                memory.save_to_var(var_frame, var_name,"false","bool")
        elif __one_is_nil_type(symbol1,symbol2,memory):
            var_frame, var_name=get_varInfo(root[instruction_position][0].text)
            memory.save_to_var(var_frame, var_name,"false","bool")
        else:
            sys.exit(53)
    else:
        if __valid_type_comparsion(symbol1,symbol2,memory):
            if __symbols_compare(symbol1,symbol2,memory,_operators[instruction]):
                var_frame, var_name=get_varInfo(root[instruction_position][0].text)
                memory.save_to_var(var_frame, var_name,"true","bool")
            else:
                var_frame, var_name=get_varInfo(root[instruction_position][0].text)
                memory.save_to_var(var_frame, var_name,"false","bool")
        else:
            sys.exit(53)
            
def perform_comparsion_stack(memory, instruction):
    """spracuje porovnavacie instrukcie na zasobniku

    Args:
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
    """    
    stack_element2 = memory.stack_pop()
    stack_element1 = memory.stack_pop()
    
    element1_value, element1_type = memory.stack_element_info(stack_element1)
    element2_value, element2_type = memory.stack_element_info(stack_element2)
    
    if nil_in_equation(instruction, element1_type, element2_type):
        if element1_type == "nil" and element2_type == "nil":
            result = "true"
        elif element1_type == "nil" or element2_type == "nil": 
            result = "false"
        type = "bool"
    else:
        result, type = _stack_elements_operate(memory, stack_element1, stack_element2, _operators[instruction])
        result = __repair_bool_value_to_lower(result)
    
    memory.stack_push_element(result, type)

def nil_in_equation(instruction, element1_type, element2_type):
    """zisti ci sa jedna o rovnost a ak ano zisti ci je jeden z typov nil

    Args:
        instruction (string): meno instrukcie 
        element1_type (string): typ prveho elemntu
        element2_type (string): typ druheho elementu 

    Returns:
        bool: odpoved
    """    
    if (instruction in {"eqs", "jumpifeqs", "jumpifneqs"}) and (element1_type == "nil" or element2_type == "nil"):
        return True
    else:
        return False
    
        
def perform_logical_operations(root, memory, instruction, instruction_position):
    """spracuje logicke instrukcie na pamatovych ramcoch

    Args:
        root (Element): koren xml struktury
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
        instruction_position (int): pozicia instrukcie
    """    
    symbol1=root[instruction_position][1]
    symbol2=root[instruction_position][2]

    result=_symols_ANDOR(symbol1, symbol2, memory, _operators[instruction])
    
    if result!=0:  
        var_frame, var_name=get_varInfo(root[instruction_position][0].text)
        memory.save_to_var(var_frame, var_name,result,"bool")

def perform_logical_operations_stack(memory, instruction):
    """spracuje logicke instrukcie na zasobniku

    Args:
        memory (memory_frames): pamatovy objekt
        instruction (_typestring): meno instrukcie
    """    
    stack_element2 = memory.stack_pop()
    stack_element1 = memory.stack_pop()

    result, type = _stack_elements_operate_bool(memory, stack_element1, stack_element2, _operators[instruction])

    memory.stack_push_element(result, type)

def perform_jumps(root, memory, instruction, instruction_position, labels, label):
    """vykonaj skoky

    Args:
        root (Element): koren XML struktury
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instrukcie
        instruction_position (int): pozicia instrukcie
        labels (dictionary): zoznam navesti
        label (string): navestie skoku

    Returns:
        int: pozicia na ktoru ma skakat
    """    
    symbol1=root[instruction_position][1]
    symbol2=root[instruction_position][2]
    
    if _label_exists(labels,label):
        if __valid_type_comparsion(symbol1,symbol2,memory) or _are_same_type_as(symbol1,symbol2,memory,"nil"):
            if __symbols_compare(symbol1,symbol2,memory,_operators[instruction]):   
                return jump(root, labels, label, instruction_position)
            else:
                return instruction_position
        elif __one_is_nil_type(symbol1,symbol2,memory):
            if instruction == "jumpifneq":
                return jump(root, labels, label, instruction_position)
            else:
                return instruction_position
        else:
            sys.exit(53)
    else:
        sys.exit(52)


def jump(root, labels, label, instruction_position):
    """najde a vrati poziciu na ktoru treba skocit

    Args:
        root (Element): _description_ koren XML struktury
        labels (dictionary): zonznam navesti
        label (string): navestie skoku 
        instruction_position (int): pozicia instrukcie

    Returns:
        int: pozicia na ktoru treba skocit
    """    
    label=root[instruction_position][0].text
    if _label_exists(labels,label):
        return int(labels[label])         
    else:
        sys.exit(52)

def is_stack_instruction(instruction):
    """ zisiti ci sa jenda o instrukci ktora pracuje so zasobnikom 

    Args:
        instruction (string): meno instrukcie 

    Returns:
        bool: odpoved
    """    
    if instruction.endswith('s'):
        return True
    else:
        return False
        
def perform_jumps_stack(root, memory, instruction, instruction_position, labels, label):
    """ vykonaj skoky s datami zo zasobnika

    Args:
        root (Element): koren XML strukturi
        memory (memory_frames): pamatovy objekt
        instruction (string): meno instruckie
        instruction_position (int): pozicia instrukcie
        labels (dictionary): zoznam navesti
        label (string): navestie skoku

    Returns:
        int: pozicia na ktoru ma skocit
    """    
    stack_element2 = memory.stack_pop()
    stack_element1 = memory.stack_pop()
    
    element1_value, element1_type = memory.stack_element_info(stack_element1)
    element2_value, element2_type = memory.stack_element_info(stack_element2)
    
    if nil_in_equation(instruction, element1_type, element2_type):
        if element1_type == "nil" and element2_type == "nil":
            if instruction == "jumpifneqs":
                result = False
            else:
                result = True
        elif element1_type == "nil" or element2_type == "nil": 
            if instruction == "jumpifneqs":
                result = True
            else:
                result = False
    else:
        result, type = _stack_elements_operate(memory, stack_element1, stack_element2, _operators[instruction])
    
    if result:                                                                                        
        return jump(root, labels, label, instruction_position)
    else:
        return instruction_position

def perform_negation(root, memory, instruction_position):
    """vykonaj negaciu na pamatovych ramcoch

    Args:
        root (Element): koren XML struktury
        memory (memory_frames): pamatovy objekt
        instruction_position (int): pozicia instrukcie
    """    
    var_frame, var_name=get_varInfo(root[instruction_position][0].text)
    symbol1=root[instruction_position][1]
    
    if get_symbolType(symbol1,memory) == "bool":
        result = not _repair_bool_value_to_upper(get_symbolValue(symbol1,memory))
        memory.save_to_var(var_frame, var_name,__repair_bool_value_to_lower(result),"bool")
    else:
        sys.exit(53)

def perform_negation_stack(memory):
    """vykonaj negaciu na zasobniku

    Args:
        memory (memory_frames): pamatovy objekt
    """    
    stack_element = memory.stack_pop()
    element_value, element_type = memory.stack_element_info(stack_element)
    
    if element_type == "bool":
        result = not str_to_int(element_value)
        result = __repair_bool_value_to_lower(result)
        type = "bool"
        memory.stack_push_element(result, type)
    else:
        sys.exit(53)
        
def __repair_bool_value_to_lower(value):
    """zmeni pythonovsku bool hodnotu na string vhodny pre ulozenie do pamatoveho objektu

    Args:
        value (bool): bool hodnota

    Returns:
        string: string hodnota
    """    
    if value == True:
        return "true"
    elif value == False:
        return "false"

def _repair_bool_value_to_upper(value):
    """zmeni string hodnotu ulozenu v pamatovom objekte na pythonovsku bool hodnotu

    Args:
        value (string): string hodnota true,false

    Returns:
        bool: bool hodnota
    """    
    if value == "true":
        return True
    else:
        return False
     
def __replace_string_exits(value):
    """zmeni exitove symboli typu /000 na charaktery odpovedajuce zadanej asci hodnote  

    Args:
        value (string): string

    Returns:
        string: string so zamenenimi exit hodnotamy
    """    
    value = str(value)
    
    for asci_number in re.findall("\\\[0-9][0-9][0-9]",value):
        asci_value = asci_number[1:] 
        value = value.replace(asci_number,chr(int(asci_value)))
        
    return value
        
def _are_same_type_as(symb1,symb2,memory,type):
    """zisti ci su dva symboli zadaneho typu

    Args:
        symb1 (string): prvy symbol
        symb2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt
        type (string): zistovany typ

    Returns:
        bool: odpoved
    """    
    symbol1_type = get_symbolType(symb1,memory)
    symbol2_type = get_symbolType(symb2,memory)
    
    if symbol1_type == type and symbol2_type == type:
        return True
    else:
        return False

def __valid_type_comparsion(symb1,symb2,memory):
    """zisti ci su symboli vhodneho typu pre porovnavacie instrukcie

    Args:
        symb1 (string): prvy symbol
        symb2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt 

    Returns:
        bool: odpoved
    """    
    if _are_same_type_as(symb1,symb2,memory,"bool") or _are_same_type_as(symb1,symb2,memory,"int") or _are_same_type_as(symb1,symb2,memory,"float") or _are_same_type_as(symb1,symb2,memory,"string"):
        return True
    else:
        return False

def __one_is_nil_type(symb1,symb2,memory):
    """zisti ci je jeden sybol typu nil

    Args:
        symb1 (string): prvy symbol
        symb2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt

    Returns:
        bool: odpoved
    """    
    symbol1_type = get_symbolType(symb1,memory)
    symbol2_type = get_symbolType(symb2,memory)
    
    if symbol1_type == "nil" or symbol2_type == "nil":
        return True
    else:
        return False
    
def check_symbol_types(symbol1,symbol2,memory,type):
    """zisti ci su dva symboli zadaneho typu

    Args:
        symb1 (string): prvy symbol
        symb2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt
        type (string): zistovany typ

    Returns:
        bool: odpoved
    """    
    if _check_saved_symbol_type(symbol1,type,memory) and _check_saved_symbol_type(symbol2,type,memory):
        if _check_true_symbol_type(memory, symbol1, type) and _check_true_symbol_type(memory, symbol2,type):
            return True
        else:
            return False
    else:
        return False

def check_symbol_type(symbol, memory, type):
    """zisti ci je symbol zadaneho typu

    Args:
        symbol (string): symbol
        memory (memory_frames): pamatovy objekt
        type (string): zistovany typ

    Returns:
        bool: odpoved
    """    
    if _check_saved_symbol_type(symbol,type,memory):
        if _check_true_symbol_type(memory, symbol, type):
            return True
        else:
            return False
    else:
        return False
    
def _check_saved_symbol_type(symbol,type,memory):
    """zisti ci ma symbol v pamatovom ramci zapisany zadany typ

    Args:
        symbol (string): symbol
        type (string): zistovany typ
        memory (memory_frames): pamatovy objekt

    Returns:
        bool: odpoved
    """    
    if str(get_symbolType(symbol,memory)) == str(type):
        return True
    else:
        return False
    
def _check_true_symbol_type(memory, symbol,type):
    """zisti ci je hodnota symbolu spravne zapisana podla zadaneho typu

    Args:
        memory (memory_frames): pamatovy objekt 
        symbol (string): symbol
        type (string): zistovany typ

    Returns:
        bool: odpoved
    """    
    value = get_symbolValue(symbol,memory)
    if str(type) == "int":
        try:
           int(value) 
        except ValueError:
            stdout.flush()
            return False
        else:
            return True
    elif str(type) == "string":
        try:
           str(symbol.text)
        except ValueError:
            return False
        else:
            return True
    elif str(type) == "float":
        value = float.fromhex(value)
        try:
           float(value) 
        except ValueError:
            return False
        else:
            return True
    
def __symbols_compare(symbol1,symbol2,memory, operator):
    """porovna zadane symboli podla zadaneho opratoru

    Args:
        symbol1 (string): prvy symbol
        symbol2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt 
        operator (string): pouzity operator

    Returns:
        bool: vysledok
    """    
    sym_val1 = get_symbolValue(symbol1,memory)
    sym_val2 = get_symbolValue(symbol2,memory)
    sym_type = get_symbolType(symbol1,memory)
    
    if sym_type == "int":
        #toto zkontroluj ci su naozaj int
        sym_val1 = int(sym_val1)
        sym_val2 = int(sym_val2)
    elif sym_type == "string":
        if (sym_val1 is None) or (sym_val2 is None):
            return False
        else:
            sym_val1 = str(sym_val1)
            sym_val2 = str(sym_val2)
    elif sym_type == "bool":
        sym_val1 = _repair_bool_value_to_upper(sym_val1)
        sym_val2 = _repair_bool_value_to_upper(sym_val2)
        
    return eval(f'sym_val1 {operator} sym_val2')

def _symbols_oprerate(symbol1,symbol2,memory, operator):
    """spracuje opraciu nad symbolmi podla zadanehio operatoru;,;;;,;;;,;;

    Args:
        symbol1 (string): prvy symbol
        symbol2 (string): druhy symbol
        memory (memory_frames): pamatovy objekt
        operator (string): vyuziti operator

    Returns:
        _type_: _description_
    """        
    if _symbols_are_operateble(symbol1, symbol2, memory):
        sym_val1 = _get_operateble_symbol_value(symbol1,memory)
        sym_val2 = _get_operateble_symbol_value(symbol2,memory)
        
        return _values_operate(sym_val1, sym_val2, operator)
    else:
        sys.exit(53)

def _values_operate(value1, value2, operator):
    """spracuje operaciu nad hodnotami podla zadaneho operatoru

    Args:
        value1 (string, int, float): prva hodnota
        value2 (string, int, float): druha hodnota
        operator (string): pouzity operator

    Returns:
       string, int, float: vysledok
    """    
    if operator in {"/","//"}:
        if value2 == 0:
            sys.exit(57)  
            
    return eval(f'value1 {operator} value2')

def _stack_elements_operate(memory, element1, element2, operator):
    """spracuje dva elemty stacku podla operatoru

    Args:
        memory (memory_frames): pamatovy objekt 
        element1 (string): prvy element
        element2 (string): druhy element
        operator (string): vyuzity operator

    Returns:
        _type_: vysledok
    """    
    element1_value, element1_type = memory.stack_element_info(element1)
    element2_value, element2_type = memory.stack_element_info(element2)
    
            
    if element1_type == "int" and element2_type == "int":
        result = _values_operate(int(element1_value), int(element2_value), operator)
        
        return result, "int"
    
    elif element1_type == "float" and element2_type == "float":
        result = _values_operate(float(element1_value), float(element2_value), operator)
        
        return result, "float"
    
    elif element1_type == "string" and element2_type == "string":
        result = _values_operate(str(element1_value), str(element2_value), operator)

        return result, "string"
    
    elif element1_type == "bool" and element2_type == "bool":
        result = _values_operate(str(element1_value), str(element2_value), operator)
        
        return result, "bool"
    
    elif element1_type == "nil" or element2_type == "nil":
        sys.exit(53)
    else:
        sys.exit(53)
 
def _stack_elements_operate_bool(memory, element1, element2, operator):
    """spracuje logicke operacie nad dvoma elementmy zasobniku podla zadaneho operatoru

    Args:
        memory (_type_): pamatovy objekt
        element1 (_type_): prvy element
        element2 (_type_): druhy element
        operator (_type_): vyuzity operator

    Returns:
        bool: vysledok
    """    
    element1_value, element1_type = memory.stack_element_info(element1)
    element2_value, element2_type = memory.stack_element_info(element2)
    
    if element1_type == "bool" and element2_type == "bool":   
        result = int_to_bool(_values_operate(str_to_int(element1_value), str_to_int(element2_value), operator))
        return result, "bool"
    
    else:
        sys.exit(53)

def str_to_int(element_value):
    if element_value == "true":
        return 1 
    elif element_value == "false":
        return 0
def int_to_bool(element_value):
    if element_value == 1:
        return "true" 
    elif element_value == 0:
        return "false"
    
def _get_operateble_symbol_value(symbol,memory):
    """ziskaj pythonovsku hodnotu ulozenu v symbole

    Args:
        symbol (_type_): symbol
        memory (_type_): pamatovy objekt

    Returns:
        int, float, string : obsah symbolu
    """    
    sym_type = get_symbolType(symbol, memory)
    sym_val = get_symbolValue(symbol,memory)
    
    if _check_true_symbol_type(memory, symbol ,sym_type):
        if sym_type == "int":
            return int(sym_val)
        elif sym_type == "float":
            return float.fromhex(sym_val)
        elif sym_type == "string":
            return str(sym_val)
    else:
        return False
    
def symbol_is_set(symbol, memory):
    """zisti ci je v symbole ulozena hodnota

    Args:
        symbol (_type_): symbol
        memory (_type_): pamatovy objekt

    Returns:
        bool: vysledok
    """    
    sym_type = get_symbolType(symbol, memory)
    if sym_type:
        return True
    else:
        return False
def _symbols_are_operateble(symbol1, symbol2, memory):
    """zysti ci maju symboli vhodne typy pre spracovavanie

    Args:
        symbol1 (_type_): prvy symbol
        symbol2 (_type_): druhy symbol
        memory (_type_): pamatovy objekt

    Returns:
        bool: vysledok 
    """    
    symbol1_type = get_symbolType(symbol1, memory)
    symbol2_type = get_symbolType(symbol2, memory)
    
    if (symbol1_type == "float" and symbol2_type == "float") or (symbol1_type == "int" and symbol2_type == "int"):
        if _check_true_symbol_type(memory, symbol1, symbol1_type) and _check_true_symbol_type(memory, symbol2, symbol2_type):
            return True
        else:
            return False
    else:
        return False
        
def _symols_ANDOR(symbol1,symbol2,memory, operator):
    """spracuje logicke operacie nad symbolmi pri com kontroluje ich typy

    Args:
        symbol1 (_type_): prvy symbol
        symbol2 (_type_): druhy symbol
        memory (_type_): pamatovy objekt
        operator (_type_): vyuziti operator

    Returns:
        bool: vysledok
    """    
    if _are_same_type_as(symbol1,symbol2,memory,"string"):
        sym_val1 = get_symbolValue(symbol1,memory)
        sym_val2 = get_symbolValue(symbol2,memory)
        
        return eval(f'sym_val1 {operator} sym_val2')
    elif _are_same_type_as(symbol1,symbol2,memory,"bool"):
        sym_val1 = get_symbolValue(symbol1,memory)
        sym_val2 = get_symbolValue(symbol2,memory)
        
        sym_val1 = _repair_bool_value_to_upper(sym_val1)
        sym_val2 = _repair_bool_value_to_upper(sym_val2)
        
        return __repair_bool_value_to_lower(eval(f'sym_val1 {operator} sym_val2'))
    else:
        sys.exit(53)
    

        
def are_both_int(symbol1, symbol2, memory):
    if get_symbolType(symbol1, memory) == "int" and get_symbolType(symbol2, memory) == "int":
        return True
    else:
        return False

def float_to_hexa(sym_value):
    """upravi zadany float v roznych typoch zapisu na hexadecimalny zapis

    Args:
        sym_value (float, string): hodnota 

    Returns:
        vysledok: string
    """    
    try:
        decimal_float = float(sym_value)
    except Exception:                               #ak je v hexa podobe treba upravit na true hexa
        decimal_float = float.fromhex(sym_value)
        sym_value = float.hex(float(decimal_float)) 
        return sym_value
    else:                                           #ak je v decimalnej podobe
        sym_value = float.hex(decimal_float)
        return sym_value
    
def chack_exit_value(value):
    """zkontroluje ci je hodnota vhodna pre exit programu

    Args:
        value (string): hodnota

    Returns:
        bool: odpoved
    """    
    try:
        value = int(value)
    except Exception:    
        return False
        
    if value >= 0 and value <= 49:
        return True
    else:
        return False

def _check_if_duplicate_order(root):
    """zisti ci sa v XML strome nachadza viacnasobna hodnota atributu order
    
    Args:
        root (_type_): koren XML struktury

    Returns:
        bool: odpoved
    """    
    listt=[]
    
    for child in root:
        listt.append(child.get('order'))
    if len(listt) == len(set(listt)):
        return False
    else:
        return True
        
def _label_exists(labels,label):
    """zisti ci je v zozname navesti ulozene zadane navestie

    Args:
        labels (dictionary): zoznam
        label (string): navesie

    Returns:
        _type_: _description_
    """    
    if label in labels:
        return True
    else:
        return False
