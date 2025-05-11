import re
import sys

string = '''  - "0"
  - "1"
  - "2"
  - "3"
  - "4"
  - "5"
  - "6"
  - "7"
  - "8"
  - "9"
  - "a"
  - "b"
  - "c"
  - "d"
  - "e"
  - "f"
  - "g"
  - "h"
  - "i"
  - "j"
  - "k"
  - "l"
  - "m"
  - "n"
  - "o"
  - "p"
  - "q"
  - "r"
  - "s"
  - "t"
  - "u"
  - "v"
  - "w"
  - "x"
  - "y"
  - "z"
  - "A"
  - "B"
  - "C"
  - "D"
  - "E"
  - "F"
  - "G"
  - "H"
  - "I"
  - "J"
  - "K"
  - "L"
  - "M"
  - "N"
  - "O"
  - "P"
  - "Q"
  - "R"
  - "S"
  - "T"
  - "U"
  - "V"
  - "W"
  - "X"
  - "Y"
  - "Z"
  - "@"
  - "#"
  - "$"
  - "%"
  - "^"
  - "&"
  - "*"
  - "("
  - ")"
  - "-"
  - "_"
  - "="
  - "+"
  - "["
  - "]"
  - "{"
  - "}"
  - "<"
  - ">"
  - "?"
  - "/"
  - "!"
  - "."
  - ","
  - "'"'''
  
s = re.findall("\".\"", string)
chars = [c[1] for c in s]
ints = [i for i in range(87)]
char_dict = {c: i for c, i in zip(chars, ints)}
      
def map_char(char):
    return char_dict[char]

if __name__ == "__main__":
  if len(sys.argv) > 1:
    word = sys.argv[1]
    if len(word) > 1:
      for char in word:
        print(f'{char}: {map_char(char)}')
    else:
      print(map_char(word))
  else:
    print(char_dict)
