import sys
from sys import stdout
import xml.etree.ElementTree as ET
import re
import interpret_functions as intrFun
import interpret_memory as mem
import interpret_XML_handler as intrXML

args = intrFun.parse_arguments()
file = args.source

try:
    tree = ET.parse(file[0])
except Exception:
    sys.exit(31)

root = tree.getroot()
intrFun.sort_etree_by_order(root)
tree.write('output.xml')

memory = mem.memory_frames()

labels = {}
instruction_num = 0
for child in root:                                          #ulozim si kde sa v kode nachadzaju ake navestia
    intrFun.save_label(child, labels,child.attrib.get("opcode"),instruction_num)
    instruction_num=instruction_num + 1

current_position_in_tree = 0
while current_position_in_tree != instruction_num:
    instruction = str(root[current_position_in_tree].get("opcode")).lower()
    intrXML.check_XML(root[current_position_in_tree])

    if instruction in ["add", "sub", "mul", "div", "idiv", "adds", "subs", "muls", "idivs"]:
        if intrFun.is_stack_instruction(instruction):
            intrFun.perform_arithmetics_stack(memory, instruction)
        else:
            intrFun.perform_arithmetics(root, memory, instruction, current_position_in_tree)
    
    elif instruction in ['gt', 'lt', 'eq', 'gts', 'lts', 'eqs']:
        if intrFun.is_stack_instruction(instruction):
            intrFun.perform_comparsion_stack(memory, instruction)
        else:
            intrFun.perform_comparsion(root, memory, instruction, current_position_in_tree)
            
    elif instruction in ["ands", "ors", "and", "or"]:
        if intrFun.is_stack_instruction(instruction):
            intrFun.perform_logical_operations_stack(memory, instruction)
        else:
            intrFun.perform_logical_operations(root, memory, instruction, current_position_in_tree)
           
    elif instruction in ["nots", "not"]:
        if intrFun.is_stack_instruction(instruction):
            intrFun.perform_negation_stack(memory)
        else:
            intrFun.perform_negation(root, memory, current_position_in_tree)
            
    elif instruction in ["jumpifeq", "jumpifneq", "jumpifeqs", "jumpifneqs"]:
        label = root[current_position_in_tree][0].text
        if intrFun.is_stack_instruction(instruction):
            current_position_in_tree = intrFun.perform_jumps_stack(root, memory, instruction, current_position_in_tree, labels, label)
        else:
            current_position_in_tree = intrFun.perform_jumps(root, memory, instruction, current_position_in_tree, labels, label)
            
    elif instruction=="jump":
        label = root[current_position_in_tree][0].text
        current_position_in_tree = intrFun.jump(root, labels, label, current_position_in_tree)
            
    elif instruction=="move":
        var1_frame, var1_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
        
        if intrFun.symbol_is_set(root[current_position_in_tree][1], memory):
            symbol_value = intrFun.get_symbolValue(root[current_position_in_tree][1],memory)
            symbol_type = intrFun.get_symbolType(root[current_position_in_tree][1],memory)
            
            memory.save_to_var(var1_frame, var1_name, symbol_value,symbol_type)
        else:
            sys.exit(56)
                
    elif instruction=="defvar":
        
        var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
        memory.def_var(var_frame, var_name)
            
    elif instruction=="createframe":
        memory.create_TFframe()
        
    elif instruction=="pushframe":
        
        memory.append_TFtoStack()
        memory.destroy_TF()
    
    elif instruction=="popframe":
        memory.pop_LFtoTF()
        
    elif instruction in {"int2char", "int2chars"}:
        
       
        if intrFun.is_stack_instruction(instruction):
            stack_element = memory.stack_pop()
            element_value, element_type = memory.stack_element_info(stack_element)
            
            if element_type == "int":
                try:
                   result = chr(int(element_value)) 
                except Exception:
                    sys.exit(52)
                else:
                    memory.stack_push_element(result, "string")
            else:
                sys.exit(53)
                
        else:    
            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
            symbol = root[current_position_in_tree][1]
            
            if intrFun.check_symbol_type(symbol, memory, "int"):
                try:
                   result = chr(int(intrFun.get_symbolValue(symbol,memory))) 
                except Exception:
                    sys.exit(52)
                else:
                    memory.save_to_var(var_frame, var_name, result, "string")
            else:
                
                sys.exit(53)
            
    elif instruction in {"stri2int", "stri2ints"}:
        if intrFun.is_stack_instruction(instruction):
            stack_element2 = memory.stack_pop()
            stack_element1 = memory.stack_pop()
            
            element1_value, element1_type = memory.stack_element_info(stack_element1)
            element2_value, element2_type = memory.stack_element_info(stack_element2)
    
            if element1_type == "string" and element2_type == "int":
                position = int(element2_value)
                string = element1_value

                if string:
                    if (len(string) >= (position+1)) and (position > -1 ):
                        result = ord(string[position])
                        memory.stack_push_element(result, "int")
                    else:
                        sys.exit(58)
                else:
                    sys.exit(58)
            else:
                sys.exit(53)
                
        else:    
            symbol1 = root[current_position_in_tree][1]
            symbol2 = root[current_position_in_tree][2]
            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)

            if intrFun.check_symbol_type(symbol1, memory, "string") and intrFun.check_symbol_type(symbol2, memory, "int"):
                position = int(intrFun.get_symbolValue(symbol2, memory))
                string = intrFun.get_symbolValue(symbol1, memory)

                if string:
                    if (len(string) >= (position+1)) and (position > -1 ):
                        result = ord(string[position])
                        memory.save_to_var(var_frame, var_name, result,"int")
                    else:
                        sys.exit(58)
                else:
                    sys.exit(58)
            else:
                sys.exit(53)
            
    elif instruction=="concat":
        if intrFun.check_symbol_types(root[current_position_in_tree][1],root[current_position_in_tree][2],memory,"string"):
            string1 = intrFun.get_symbolValue(root[current_position_in_tree][1],memory)
            string2 = intrFun.get_symbolValue(root[current_position_in_tree][2],memory)
            
            if string1 == "None" :
                value = string2
            elif string2 == "None":
                value = string1
            else:
                value = str(string1) + str(string2)
            
            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
            memory.save_to_var(var_frame, var_name, value,"string")
        else:
            sys.exit(53)
        
    elif instruction=="strlen":
        symbol = root[current_position_in_tree][1]
        if intrFun.check_symbol_type(symbol,memory,"string"):
            string = intrFun.get_symbolValue(symbol,memory)
            if string == "None":
                string_lenght = 0
            else:
                string_lenght = len(intrFun.get_symbolValue(symbol,memory))
                
            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
            memory.save_to_var(var_frame, var_name, string_lenght,"int")
        else:
            sys.exit(53)
            
    elif instruction=="getchar":
        symbol1 = root[current_position_in_tree][1]
        symbol2 = root[current_position_in_tree][2]
        
        if intrFun.get_symbolType(symbol1,memory) == "string" and intrFun.get_symbolType(symbol2,memory) == "int":
            string = intrFun.get_symbolValue(root[current_position_in_tree][1],memory)
            position = int(intrFun.get_symbolValue(root[current_position_in_tree][2],memory))
            
            if position >= 0 and position<len(str(string)):
                value = string[position]
                var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
                memory.save_to_var(var_frame, var_name, value,"string")
            else:
                sys.exit(53)
        else:
            sys.exit(53)
                
    elif instruction=="setchar":
        if intrFun.check_symbol_type(root[current_position_in_tree][0],memory,"string") and intrFun.check_symbol_type(root[current_position_in_tree][1],memory,"int") and intrFun.check_symbol_type(root[current_position_in_tree][2],memory,"string"):
            string = str(intrFun.get_symbolValue(root[current_position_in_tree][0],memory))
            lenght = len(string)
            position = int(intrFun.get_symbolValue(root[current_position_in_tree][1],memory))
            character = str(intrFun.get_symbolValue(root[current_position_in_tree][2],memory))
            
            if (character != "None"):
                if (position >= 0 and position < lenght) and (position >= 0 and position < lenght):
                    result = string[0:position] + character[0] + string[position+1:] 

                    var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
                    memory.save_to_var(var_frame, var_name, result,"string")
                else:
                    sys.exit(58)
            else:
                sys.exit(58)        
        else:
            sys.exit(53)
                
    elif instruction=="type":
        symbol = root[current_position_in_tree][1]
        type = intrFun.get_symbolType(symbol, memory)
        
        var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
        memory.save_to_var(var_frame, var_name, type,"string")
        
    elif instruction == "dprint":
        print(intrFun.get_symbolValue(root[current_position_in_tree][0],memory), file=sys.stderr)
        
    elif instruction == "write":
        symbol = root[current_position_in_tree][0]
        sym_type = intrFun.get_symbolType(symbol,memory)
        sym_value = intrFun.get_symbolValue(symbol,memory) 
        if intrFun.symbol_is_set(symbol, memory):
            if (sym_type not in{"nil","None",''}) and sym_value not in{"None",''}:
                if sym_type == "float":
                    hexa_float = intrFun.float_to_hexa(sym_value)
                    print(hexa_float,end='')
                elif sym_type == "int":
                    print(intrFun.get_symbolValue(symbol,memory),end='')
                elif sym_type == "":
                    sys.exit(56)
                else:
                    print(intrFun.get_symbolValue(symbol,memory),end='')
            else:
                print("",end = '')
        else:
            sys.exit(58)
    
    elif instruction == "read":
        
        var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
        type = intrFun.get_symbolValue(root[current_position_in_tree][1],memory)
        
        try:
            new_varVal = input()
        except:
            memory.save_to_var(var_frame, var_name, "nil","nil")
        else:
            if type == "int":
                if re.match('^(-?\+?)[0-9]+$\s?',new_varVal):
                    memory.save_to_var(var_frame, var_name, new_varVal,"int")
                else:
                    memory.save_to_var(var_frame, var_name, "nil","nil")
            elif type == "string":
                memory.save_to_var(var_frame, var_name, new_varVal,"string")
            elif type == "float":
                memory.save_to_var(var_frame, var_name, new_varVal,"float")
            elif type == "bool":
                new_varVal = str(new_varVal).lower()
                if new_varVal == "true":
                    memory.save_to_var(var_frame, var_name, "true","bool")
                else:
                    memory.save_to_var(var_frame, var_name, "false","bool")
            else:
                memory.save_to_var(var_frame, var_name, "nil","nil")
                
        
    
    elif instruction== "pushs":
        symbol=root[current_position_in_tree][0]
        if intrFun.symbol_is_set(symbol,memory):
            intrFun.stack_push_symbol(memory, symbol)
        else:
            sys.exit(56)
    
    elif instruction== "pops":
        top_of_stack = memory.stack_pop()
        
        top_of_stack_type = top_of_stack.split("@",1)[0]
        top_of_stack_value = top_of_stack.split("@",1)[1]
        
        var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
        memory.save_to_var(var_frame, var_name, top_of_stack_value, top_of_stack_type)
        
    elif instruction== "exit":
        value = intrFun.get_symbolValue(root[current_position_in_tree][0],memory)
        
        if intrFun.chack_exit_value(value):
            sys.exit(int(value))
        else:
            sys.exit(57)        
    
    elif instruction== "call":
        label = root[current_position_in_tree][0].text
        
        if label in labels:
            memory.save_return_position(current_position_in_tree)
            current_position_in_tree = labels[label]         #posun current_position_in_tree na poziciu daneho navestia v kode naslede sa na konci cyklu posunie na nasledujucu instrukciu
        else:
            sys.exit(52)
    
    elif instruction == "return":
        current_position_in_tree = memory.return_to_position()
    
    elif instruction == "float2int":
        symbol = root[current_position_in_tree][1]
        
        if intrFun.check_symbol_type(symbol, memory, "float"):
            sym_value = intrFun.get_symbolValue(symbol, memory)
            hexa_float = intrFun.float_to_hexa(sym_value)
            
            try:
                int_value = int(float.fromhex(hexa_float))
            except:
                sys.exit(57)
                
            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
            memory.save_to_var(var_frame, var_name, int_value, "int")
            
        else:
            sys.exit(53)
            
    elif instruction == "int2float":
        symbol = root[current_position_in_tree][1]
        
        if intrFun.check_symbol_type(symbol, memory, "int"):
            sym_value = intrFun.get_symbolValue(symbol, memory)
            
            try:
                float_value = float(int(sym_value))
            except:
                sys.exit(57)
            
            hexa_float = intrFun.float_to_hexa(float_value)

            var_frame, var_name = intrFun.get_varInfo(root[current_position_in_tree][0].text)
            memory.save_to_var(var_frame, var_name, hexa_float, "float")
        else:
            sys.exit(53)
    
    current_position_in_tree=current_position_in_tree+1

sys.exit(0)

