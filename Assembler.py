# Import text from .asm file
from sys import argv

###################
## JRD ASSEMBLER ##
###################

##Test##


print "JRD Nand2Tetris Assembler\n"

print "Enter the Source File (.asm) to be assembled:"

source_file = raw_input(">") # input source file name

print "This is the Source File: " + source_file # Print the Source Filename

out_filename = source_file[0:source_file.find(".")] + ".hack" # Extract and cat to create the Output Filename

txt = open(source_file, 'r') # Open source_file to read

initial_lines = txt.readlines() # Read the source file, by line, into initial_lines list


# Iterate and remove comments, line breaks and extra lines
code_lines = []

for line in initial_lines:
    if line[0] != "/" and line[0] != "\n" and line[0] != "\r":
        temp = "" # Initialize the temp string
        for e in line: # Iterate through each character in the line
            if e == "/" or e == "\r" or e == "\n": # Stop at comments or line breaks
                break
            if e != " ": # If not a white space..
                temp = temp + e # Then, concatenate the temp string w/current character
        code_lines.append(temp) # Add the final temp line to code_line


# Initialize Symbol Table and Other Dictionaries
# THIS FUNCTIONS INSTEAD OF "CONSTRUCTOR ROUTINE"

symbol_table = {"SP" : 0, "LCL" : 1, "ARG" : 2, "THIS" : 3, "THAT" : 4, "R0" : 0, "R1" : 1, "R2" : 2, "R3" : 3, "R4" : 4, "R5" : 5, "R6" : 6, "R7" : 7, "R8" : 8, "R9" : 9, "R10" : 10, "R11" : 11, "R12" : 12, "R13" : 13, "R14" : 14, "R15" : 15, "SCREEN" : 16384, "KBD" : 24576}

dest_dict = {"null" : "000", "0" : "000", "M" : "001", "D" : "010", "MD" : "011", "A" : "100", "AM" : "101", "AD" : "110", "AMD" : "111"}

comp_dict = {"0" : "0101010", "1" : "0111111", "-1" : "0111010", "D" : "0001100", "A" : "0110000", "!D" : "0001101", "!A" : "0110001", "-D" : "0001111", "-A" : "0110011", "D+1" : "0011111", "A+1" : "0110111", "D-1" : "0001110", "A-1" : "0110010", "D+A" : "0000010", "D-A" : "0010011", "A-D" : "0000111", "D&A" : "0000000", "D|A" : "0010101", "M" : "1110000", "!M" : "1110001", "-M" : "1110011", "M+1" : "1110111", "M-1" : "1110010", "D+M" : "1000010", "D-M" : "1010011", "M-D" : "1000111", "D&M" : "1000000", "D|M" : "1010101"}

jump_dict = {"null" : "000", "0" : "000", "JGT" : "001", "JEQ" : "010", "JGE" : "011", "JLT" : "100", "JNE" : "101", "JLE" : "110", "JMP" : "111"}


## HELPER FUNCTIONS

def dec2bin(n):
    if n==0: return ""
    else:
        return dec2bin(n/2) + str(n%2)

def bin15(n):
    if len(n) == 15:
        return n
    n = "0" + n
    return bin15(n)


## THE PARSER MODULE ###

def hasMoreCommands(line_number):
    if line_number + 1 >= len(code_lines):
        return False
    return True

def advance(line_number):
    return code_lines[line_number]

def commandType(current_line):
    if current_line[0] == "@": # Finds value/symbol
        return "A_COMMAND"
    if current_line.find("=") != -1 or current_line.find(";") != -1: # Finds comp or jump
        return "C_COMMAND"
    if current_line.find("(") != -1 and current_line.find(")") != -1: # Finds label
        return "L_COMMAND"

def symbol(current_line): # Only called if commandType is "A_COMMAND" or "L_COMMAND"
    if current_line.find("(") != -1 and current_line.find(")") != -1: # For L_COMMAND
        start = current_line.find("(")
        end = current_line.find(")")
        temp = current_line[start + 1: end]
        return temp
    if current_line.find("@") != -1: # For A-COMMAND
        temp = current_line[1:]
        return temp

def dest(current_line): # Only called if commandType is "C_COMMAND"
    if current_line.find("=") != -1:
        temp = current_line[0: current_line.find("=")]
        return dest_dict[temp]

def comp(current_line): # Only called if commandType is "C_COMMAND"
    if current_line.find("=") != -1:
        x = current_line.find("=")
        temp = current_line[x + 1:]
        return comp_dict[temp]
    if current_line.find(";") != -1:
        x = current_line.find(";")
        temp = current_line[0:x]
        return comp_dict[temp]

def jump(current_line): # Only called if commandType is "C_COMMAND"
    x = current_line.find(";")
    temp = current_line[x + 1: x + 4]
    return jump_dict[temp]


# THE SYMBOL TABLE MODULE

def addEntry(symbol, address):
    symbol_table[symbol] = address
    return

def contains(symbol):
    for e in symbol_table:
        if e == symbol:
            return True
    return False

def getAddress(symbol):
    return symbol_table[symbol]


# MAIN MODULE

def main():
    
    # FIRST PASS - RESOLVES L_COMMANDS (I.E. LOOP INSTRUCTIONS)
    line_number = 0 # Initial value
    rom_address = 0 # Initial value
    
    while hasMoreCommands(line_number):
        
        current_line = advance(line_number)
        
        if commandType(current_line) == "C_COMMAND" or commandType(current_line) == "A_COMMAND":
            rom_address = rom_address + 1

        if commandType(current_line) == "L_COMMAND":
            symbol_table[symbol(current_line)] = rom_address

        line_number = line_number + 1


    # SECOND PASS - RESOLVES A_COMMANDS (I.E. @VALUE INSTRUCTIONS)
    line_number = 0  # Initial value
    ram_address = 16 # Initial value

    while hasMoreCommands(line_number):
    
        current_line = advance (line_number)
    
        if commandType(current_line) == "A_COMMAND":
            if contains(symbol(current_line)) == False: # if value is not already in symbol_table
                if symbol(current_line).isdigit() == False: # if value is a variable
                    addEntry(symbol(current_line), ram_address)
                    ram_address = ram_address + 1

        line_number = line_number + 1


    # ASSEMBLE/GENERATE OBJECT CODE
    line_number = -1  # Initial value

    while hasMoreCommands(line_number):
        # Increment Line Number
        line_number = line_number + 1
        current_line = advance(line_number)
        
        # Conversion for C_COMMAND
        if commandType(current_line) == "C_COMMAND":
            if current_line.find("=") != -1 and current_line.find(";") == -1: # Found a comp instruction w/no jump
                binary = "111" + comp(current_line) + dest(current_line) + "000"
            if current_line.find(";") != -1 and current_line.find("=") == -1: # Found a jump instruction w/no dest
                binary = "111" + comp(current_line) + "000" + jump(current_line)
    
        # Conversion for A_COMMAND
        if commandType(current_line) == "A_COMMAND":
            n = symbol(current_line)
            if n.isdigit() == True: # if value is a constant
                binary = "0" + bin15(dec2bin(int(n)))
            else: # if value is a variable
                binary = "0" + bin15(dec2bin(getAddress(n)))

        # Add to results
        if commandType(current_line) != "L_COMMAND":
            results.append(binary)
            better_binary = binary[0:4] + " " + binary[4:8] + " " + binary[8:12] + " " + binary[12:]
            print current_line + "    "  + better_binary + "   /// " + commandType(current_line) + "\n"


## Run the Main Routine
results = []
main()

# Write the Output File
out_file = open(out_filename, 'w') # Open the Output File to write

print "\nFinal Symbol Table:\n"
print symbol_table
print "\n"

print "\nWriting the Destination File: " + out_filename + "\n" # Print the Output Filename

for line in results:
    out_file.write(line)
    out_file.write("\n")

out_file.close() # close the Output File



