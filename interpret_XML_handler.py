import sys

instr_dic = {"MOVE" : ("var","symbol"),
             "CREATEFRAME" : (),
             "PUSHFRAME" : (),
             "POPFRAME" : (),
             "DEFVAR" : ("var",),
             "CALL" : ("label",),
             "RETURN" : (),
             "PUSHS" : ("symb",),
             "ADD" : ("var","symbol","symbol"),
             "ADDS" : (),
             "SUB" : ("var","symbol","symbol"),
             "SUBS" : (),
             "MUL" : ("var","symbol","symbol"),
             "MULS" : (),
             "IDIV" : ("var","symbol","symbol"),
             "IDIVS" : (),
             "DIV" : ("var","symbol","symbol"),
             "DIVS" : (),
             "LT" : ("var","symbol","symbol"),
             "LTS" : (),
             "GT" : ("var","symbol","symbol"),
             "GTS" : (),
             "EQ" : ("var","symbol","symbol"),
             "EQS" : (),
             "AND" : ("var","symbol","symbol"),
             "ANDS" : (),
             "OR" : ("var","symbol","symbol"),
             "ORS" : (),
             "NOT" : ("var","symbol"),
             "NOTS" : (),
             "INT2CHAR" : ("var","symbol"),
             "INT2CHARS" : (),
             "STRI2INT" : ("var","symbol","symbol"),
             "STRI2INTS" : (),
             "READ" : ("var","type"),
             "CONCAT" : ("var","symbol","symbol"),
             "STRLEN" : ("var","symbol",),
             "GETCHAR" : ("var","symbol","symbol"),
             "SETCHAR" : ("var","symbol","symbol"),
             "TYPE" : ("var","symbol"),
             "JUMP" : ("label",),
             "LABEL" : ("label",),
             "JUMPIFEQ" : ("label","symbol","symbol"),
             "JUMPIFEQS" : ("label",),
             "JUMPIFNEQ" : ("label","symbol","symbol"),
             "JUMPIFNEQS" : ("label",),
             "EXIT" : ("symbol",),
             "DPRINT" : ("symbol",),
             "BREAK" : (),
             "WRITE" : ("symbol",),
             "PUSHS" : ("symbol",),
             "POPS" : ("symbol",),
             "FLOAT2INT" : ("var","symbol"),
             "INT2FLOAT" : ("var","symbol"),
}

def check_XML(child):
    """kontrola spravnosti XML formatu

    Args:
        child (Element): XML element ET stromu
    """    
    if(child.tag == "instruction"):                                   #je tag instruction
        if "order" in child.attrib and "opcode" in child.attrib:    #ma dva atributy order a opcode
            try:
                order=int(child.attrib["order"])
                if(order<=0):
                    sys.exit(32)
            except ValueError:
                sys.exit(32)
            instruction_name=str(child.attrib["opcode"]).upper()
            if instruction_name in instr_dic:                 #je v opcode nejaka instrukcia a nie blbost
                if len(instr_dic[instruction_name]) == len(child):  #ma spravny pocet argumentov
                    i=1
                    correct_arg_names=[]
                    for arg in child:
                        correct_arg_names.append('arg{}'.format(i))
                        i=i+1
                    
                    i=1
                    for arg in child:                               #su atributy pomenovane arg1 ...
                        
                        if str(arg.tag) in correct_arg_names:
                            if 'type' in arg.attrib:                                #ma argument atribut typeu
                                arg_nb = int(str(arg.tag)[-1])
                                if instr_dic[instruction_name][arg_nb-1]=="symbol":      #uloz moznosti type
                                    type_posibility=["var","string","bool","int","nil","float"]
                                else:
                                    type_posibility=["var","label","type"]
                                if arg.attrib["type"] not in type_posibility:           #skontroluj type moznosti
                                    sys.exit(32)
                            else:
                                sys.exit(32)
                        else:
                            sys.exit(32)
                        i=i+1
                    child[:]=sorted(child,key = lambda arg: int(str(arg.tag)[-1]))      #zoradi argumenty podla ich ocislovania
                        
                else:
                    sys.exit(32)
            else:
                sys.exit(32)
        else:   
            sys.exit(32)
    else:
        sys.exit(32)