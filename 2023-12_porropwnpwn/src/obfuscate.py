import sys
import re
import string
import random

from pprint import pprint

# UAMFUSCATOR 3000
# Obuscador muy muy básico basado en jmpfuscator. IDA no tiene problemas en decompilar igualmente las funciones ofuscadas.
# Ni comento el código porque ni me acuerdo de lo que hace X-D



input_file = sys.argv[1]

def generate_random_function_name(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return "OBF_" + ''.join(random.choice(letters_and_digits) for _ in range(length))

    


def obfuscate_function(input_asm):

    out = ["# start obfuscate function\n"]
    out.append(input_asm[0])

    blocks = {}

    start = generate_random_function_name()
    last = start

    idx = 1
    while idx < len(input_asm):
        line = input_asm[idx]
        blocks[last] = [ line ]
        next = generate_random_function_name()
        if idx + 1 < len(input_asm):
            blocks[last].append("\tJMP " + next + "\n")
        last = next
        idx += 1


    out.append("\tJMP " + start + "\n")
    
    # iterate keys in blocks in random order
    keys = list(blocks.keys())
    random.shuffle(keys)

    for key in keys:
        out.append(key + ":\n")
        out.extend(blocks[key])


    out.append("# end obfuscate function\n")
    return out


def main():
    with open(input_file, 'r') as f:
        lines = f.readlines()

    output = []

    regex_start = re.compile(r"^[a-zA-Z][_a-zA-Z0-9]*:")
    regex_end = re.compile(r"\tret$")
    ident_string = re.compile(r"^\s*\.ident\s*\"(.*)\"$")

    idx = 0
    while True:
        # search for lines starting with regex [a-zA-Z]+:
        while idx < len(lines) and (not regex_start.match(lines[idx]) or ("flag1:" in lines[idx]) or "help:" in lines[idx]):
            # replace .ident string with random string
            if ident_string.match(lines[idx]):
                lines[idx] = "\t.ident \"UAMfuscator 3000\"\n"

            output.append(lines[idx])
            idx += 1

        if idx >= len(lines):
            break

        # found a function

        fn = []
        # search for lines ending with ret
        while idx < len(lines) and not regex_end.match(lines[idx]):
            fn.append(lines[idx])
            idx += 1

        if idx >= len(lines):
            break

        fn.append(lines[idx])
        idx += 1

        output.extend(obfuscate_function(fn))

    print("".join(output))



if __name__ == '__main__':
    main()


