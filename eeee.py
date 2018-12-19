#!/usr/bin/env python3

import re
import argparse

def all_casings(input_string):
    if not input_string:
        yield ""
    else:
        first = input_string[:1]
        if first.lower() == first.upper():
            for sub_casing in all_casings(input_string[1:]):
                yield first + sub_casing
        else:
            for sub_casing in all_casings(input_string[1:]):
                yield first.lower() + sub_casing
                yield first.upper() + sub_casing



def find_unique_words(files, basestr):
    from math import ceil
    base = basestr * ceil(8/len(basestr))
    left_perms = []
    unique_words = {}

    for filename in files:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                result = re.search('"(.*)"', line)
                if result:
                    line = line.replace('"' + result.group(1) + '"', "")
                result = re.search('<(.*)>', line)
                if result:
                    line = line.replace('<' + result.group(1) + '>', "")
                words = line.split(' ')
                for word in words:
                    word = re.sub("\n|\r|\t", "", word)
                    if not word.startswith(('//')) \
                    and word not in unique_words \
                    and len(word)>=1:
                        if not left_perms:
                            base += basestr
                            left_perms = [x for x in all_casings(base)]
                        unique_words[word] = left_perms.pop()
                    else:
                        continue

    return unique_words

def translate_file(files, outfile, basestr):
    unique_words = find_unique_words(files, basestr)

    for src in files:
        with open(src, 'r') as inp:
            filename = basestr + '_' + src.split('/')[-1]
            try:
                open(filename, 'r')
            except FileNotFoundError:
                pass
            else:
                print('Files already exists')
                return
            with open(filename, 'w') as out:
                out.write(f'#include "defines_{outfile}.h"\n')
                for line in inp:
                    words = line.split(' ')
                    translated = []
                    for word in words:
                        word = re.sub("\n|\r|\t", "", word)
                        if word in unique_words:
                            translated.append(word.replace(word, unique_words[word]))
                        else:
                            translated.append(word)
                    newline = ' '.join(translated) + '\n'
                    for inpfile in files:
                        name = inpfile.split('/')[-1]
                        if name in newline:
                            newline = newline.replace(name, f'{basestr}_{name}')

                    out.write(newline)

def create_define_file(out, unique):
    filename = 'defines_' + out + '.h'
    with open(filename, 'w') as f:
        for k, v in unique.items():
            f.write('\t'*40 + f'#define {v} {k}\n')
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate cpp file into eeeee format")
    parser.add_argument('-i', dest='inp', type=str, nargs='+', required=True)
    parser.add_argument('-o', dest='out', type=str, nargs=None)
    parser.add_argument('-b', dest='base', type=str, default='e')
    args = parser.parse_args()
    if not args.out:
        args.out = args.base + '_' + str(args.inp[0].split('/')[-1])

    print(args.inp)

    if '.' not in args.out and ['.' not in inp for inp in args.inp]:
        print("File must have extension!")
        exit(0)

    translate_file(args.inp, args.out, args.base)
    unique_words = find_unique_words(args.inp, args.base)
    create_define_file(args.out, unique_words)