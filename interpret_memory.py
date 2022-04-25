
import sys
from sys import stdout
import xml.etree.ElementTree as ET
import re


class memory_frames:
        
    def __init__(self) -> None:       
        self.GF_frame = {}
        self.TF_frame = {}
        self.LF_stack = []
        self.stack = []
        self.TF_frame_on = False
        self.call_stack = []
        
    def create_TFframe(self):
        """vytvori docasny ramec
        """        
        self.TF_frame = {}
        self.TF_frame_on = True
        
    def destroy_TF(self):
        """vymaze docasny ramec
        """        
        self.TF_frame = {}
        self.TF_frame_on = False
    
    def append_TFtoStack(self):
        """ulozi docasny ramec na LF zasobnik
        """        
        if self.TF_frame_on == True:
            self.LF_stack.append(self.TF_frame)
        else:
            sys.exit(55)
        
    def save_to_var(self,frame,name,value,type):
        """premennej v zadanom ramci zmen typ a hdnotu

        Args:
            frame (string): ramec premennej
            name (string): meno premennej
            value (string): nova hodonota premennej
            type (string): novy typ premennej
        """        
        if frame == "GF":
            self.__add_to_GF(name,value,type)
        elif frame == "LF":
            self.__add_to_LF(name,value,type)
        elif frame == "TF":
            self.__add_to_TF(name,value,type)
    
    def def_var(self,frame,name):
        """vytvor novu premennu na zadanom ramci

        Args:
            frame (string): ramec novej premennej
            name (string): meno novej premennej
        """        
        if frame == "GF":
            self.__def_GF_var(name)
        elif frame == "LF":
            self.__def_LF_var(name)
        elif frame == "TF":
            self.__def_TF_var(name)
    
    def get_varValue(self, frame, name):
        """vrati hodnotu premennej na ramci

        Args:
            frame (string): ramec
            name (string): meno premennej

        Returns:
            string: hodnota
        """        
        if frame=="GF":
            return self.__get_GF_value(name)
        elif frame=="LF":
            return self.__get_LF_value(name)
        elif frame=="TF":
            return self.__get_TF_value(name)
    
    def get_vartype(self, frame, name):
        """vrati typ premennej na ramci

        Args:
            frame (string): ramec
            name (string): meno premennej

        Returns:
            string: typ premennej
        """                
        if frame=="GF":
            return self.__get_GF_type(name)
        elif frame=="LF":
            return self.__get_LF_type(name)
        elif frame=="TF":
            return self.__get_TF_type(name)
    
    def replace_string_exits(value):
        """zmeni escape sekvencie typu /nnn na charaktery ktore predstavuje asci hodnota nnn

        Args:
            value (string): retazec

        Returns:
            string: novy retazec
        """        
        value = str(value)

        for asci_number in re.findall("\\\[0-9][0-9][0-9]",value):
            asci_value = asci_number[1:] 
            value = value.replace(asci_number,chr(int(asci_value)))

        return value
    
    def pop_LFtoTF(self):
        """z LF zasobnika popne vrchnu hodnotu a vlozi ju do TF ramca
        """        
        if self.LF_stack:
            self.TF_frame_on = True 
            self.TF_frame = self.LF_stack.pop()
        else:
            sys.exit(55)
    
    def stack_push_element(self, value, type):
        """pushni element na zasobnik (rozsirenie)

        Args:
            value (string): hodnota
            type (string): typ
        """        
        self.stack.append(str(type)+"@"+str(value))
    
    def stack_element_info(self, element):
        """ziskaj hodnotu a typ elementu v minulosti popnuteho zo zasobnika 

        Args:
            element (string): element

        Returns:
            (string): hodnota
            (string): typ 
        """        
        value = element.split("@",1)[1]
        type = element.split("@",1)[0]
    
        return value, type
    
    def stack_pop(self):
        """vyberie vrchny element zasobniku

        Returns:
            string: element
        """        
        if not self.stack:
            sys.exit(56)
        else:
            return self.stack.pop()
    
    def save_return_position(self, position):
        """ulozi poziciu na zasobnik call_stack pre pripadny navrat

        Args:
            position (int): pozicia
        """        
        self.call_stack.append(position)
    
    def return_to_position(self):
        """navrat na vrchnu poziciu na zasobniku call_stack

        Returns:
            int: position
        """        
        if self.call_stack:
            return self.call_stack.pop()
        else:
            sys.exit(56)
            
    def __add_to_GF(self,name,value,type):
        """zmeni hodnotu a typ premennej ulozenej v GF ramci

        Args:
            name (string): meno premennej
            value (string): nova hodnota premennej
            type (string): novy typ premennej
        """        
        if name in self.GF_frame:
            self.GF_frame[name]=str(type)+"@"+str(value)
        else:
            sys.exit(54)
        
    def __add_to_LF(self,name,value,type):
        """zmeni hodnotu a typ premennej ulozenej v LF ramci

        Args:
            name (string): meno premennej
            value (string): nova hodnota premennej
            type (string): novy typ premennej
        """
        if self.LF_stack:
            if name in self.LF_stack[-1]:
                self.LF_stack[-1][name] = str(type)+"@"+str(value)
            else:
                sys.exit(54)
        else:
            sys.exit(55)
                
        
    def __add_to_TF(self,name,value,type):
        """zmeni hodnotu a typ premennej ulozenej v TF ramci

        Args:
            name (string): meno premennej
            value (string): nova hodnota premennej
            type (string): novy typ premennej
        """
        if self.TF_frame_on == True:
            if name in self.TF_frame:
                self.TF_frame[name] = str(type)+"@"+str(value)
            else:
                sys.exit(54)
        else:
            sys.exit(55)
    
    def __var_exists(self, frame, name):
        """zisti ci v danom ramci existuje premenna

        Args:
            frame (string): ramec
            name (string): premenna

        Returns:
            bool: odpoved
        """        
        
        if frame == "TF":
            if name in self.TF_frame:
                return True
            else:
                return False
        elif frame == "GF":
            if name in self.GF_frame:
                return True
            else:
                return False
        elif frame == "LF":
            if self.LF_stack:
                if name in self.LF_stack[-1]:
                    return True
                else:
                    return False    
        
    def __def_GF_var(self,name):
        """vytvori novu premennu na GF ramci

        Args:
            name (string): meno novej premnnej
        """        
        if not self.__var_exists("GF",name):
            self.GF_frame[name]=""+"@"+""
        else:
            sys.exit(52)
        
    def __def_LF_var(self,name):
        """vytvori novu premennu na LF ramci

        Args:
            name (string): meno novej premnnej
        """
        if self.LF_stack:
            if not self.__var_exists("LF",name):
                self.LF_stack[-1][name] = ""+"@"+""
            else:
                sys.exit(52)
        else:
            sys.exit(55)
        
    def __def_TF_var(self,name):
        """vytvori novu premennu na TF ramci

        Args:
            name (string): meno novej premnnej
        """
        if self.TF_frame_on == True:
            if not self.__var_exists("TF",name):    
                self.TF_frame[name] = ""+"@"+""
            else:
                sys.exit(52)
        else:
            sys.exit(55)
            
    def __get_GF_value(self,name):
        """vrati hodnotu premennej ulozenej na GF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: hodnota
        """        
        if name in self.GF_frame:
            return self.GF_frame[name].split("@",1)[1]
        else:
            sys.exit(54)
        
    def __get_LF_value(self,name):
        """vrati hodnotu premennej ulozenej na LF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: hodnota
        """
        if self.LF_stack:
            if name in self.LF_stack[-1]:
                return self.LF_stack[-1][name].split("@",1)[1]
            else:
                sys.exit(54)
        else:
                sys.exit(55)
    def __get_TF_value(self, name):
        """vrati hodnotu premennej ulozenej na TF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: hodnota
        """
        
        if self.TF_frame_on == True:
            if name in self.TF_frame:
                return self.TF_frame[name].split("@",1)[1]
            else:
                sys.exit(54)
        else:
            sys.exit(55)
    
    def __get_GF_type(self,name):
        """vrati typ premennej ulozenej na GF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: typ premennej
        """
        if name in self.GF_frame:
            return self.GF_frame[name].split("@",1)[0]
        else:
            sys.exit(54)
   
    def __get_LF_type(self,name):
        """vrati typ premennej ulozenej na LF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: typ premennej
        """
        if self.LF_stack:
            if name in self.LF_stack[-1]:
                return self.LF_stack[-1][name].split("@",1)[0]
            else:
                sys.exit(54)
        else:
                sys.exit(55)
            
        
    def __get_TF_type(self,name):
        """vrati typ premennej ulozenej na TF ramci

        Args:
            name (string): meno premennej

        Returns:
            string: typ premennej
        """
        if name in self.TF_frame:
            return self.TF_frame[name].split("@",1)[0]
        else:
            sys.exit(54)
