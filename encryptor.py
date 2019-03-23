import argparse
import json
import sys


def this_func():
    pass


def encode(args):
    if not (args.cipher == 'caesar' or args.cipher == 'vigenere' or args.cipher == 'vernam'):
        sys.exit("invalid encoder name")
    if args.input_file is None:
        input_text = input()
    else:
        with open(args.input_file, 'r') as read_file:
            input_text = read_file.read()

    if args.cipher == 'caesar':
        output_text = caesar_encode(args, input_text)
    elif args.cipher == 'vigenere':
        output_text = vigenere_encode(args, input_text)
    else:
        output_text = vernam_encode_decode(args, input_text)

    if args.output_file is None:
        print(output_text)
    else:
        with open(args.output_file, 'w') as write_file:
            write_file.write(output_text)


def decode(args):
    if not (args.cipher == 'caesar' or args.cipher == 'vigenere' or args.cipher == 'vernam'):
        sys.exit("invalid encoder name")
    if args.input_file is None:
        input_text = input()
    else:
        with open(args.input_file, 'r') as read_file:
            input_text = read_file.read()

    if args.cipher == 'caesar':
        output_text = caesar_decode(args, input_text)
    elif args.cipher == 'vigenere':
        output_text = vigenere_decode(args, input_text)
    else:
        output_text = vernam_encode_decode(args, input_text)

    if args.output_file is None:
        print(output_text)
    else:
        with open(args.output_file, 'w') as write_file:
            write_file.write(output_text)


def caesar_encode(args, input_text):
    if not args.key.isdigit():
        sys.exit("The key of сaesar's cipher is a number")
    caesar_shift = int(args.key)
    for i in range(len(input_text)):
        if 'a' <= input_text[i].lower() <= 'z':
            elem = chr((ord(input_text[i].lower()) - ord('a') + caesar_shift) % 26 + ord('a'))
            if input_text[i].isupper():
                elem = elem.upper()
            input_text = input_text[:i] + elem + input_text[i + 1:]
    return input_text


def vigenere_encode(args, input_text):
    if not args.key.isalpha():
        exit("The key of vigenere's cipher is a word")
    key_str = args.key.lower()
    key_index = 0
    for i in range(len(input_text)):
        if 'a' <= input_text[i].lower() <= 'z':
            key_elem = key_str[key_index % len(key_str)].lower()
            elem = chr((ord(key_elem) + ord(input_text[i].lower()) - 2 * ord('a')) % 26 + ord('a'))
            if input_text[i].isupper():
                elem = elem.upper()
            input_text = input_text[:i] + elem + input_text[i + 1:]
            key_index += 1
    return input_text


def vernam_encode_decode(args, input_text):
    if not args.key.isalpha():
            exit("The key of vigenere's cipher is a word")
    for i in range(len(input_text)):
        if 0 <= ord(input_text[i]) - ord('a') < 32 or 0 <= ord(input_text[i]) - ord('A') < 32:
            key_elem = args.key[i % len(args.key)].lower()
            elem = chr(((ord(input_text[i]) - ord('a')) ^ (ord(key_elem) - ord('a'))) + ord('a'))
            input_text = input_text[:i] + elem + input_text[i + 1:]
    return input_text


def caesar_decode(args, input_text):
    if not args.key.isdigit():
        sys.exit("The key of сaesar's cipher is a number")
    args.key = str(26 - int(args.key))
    return caesar_encode(args, input_text)


def vigenere_decode(args, input_text):
    if not args.key.isalpha():
        exit("The key of vigenere's cipher is a word")
    args.key = args.key.lower()
    for i in range(len(args.key)):
        args.key = args.key[:i] + chr((ord('a') + 26 - ord(args.key[i])) % 26 + ord('a')) + args.key[i + 1:]
    return vigenere_encode(args, input_text)


def train(args):
    if args.text_file is None:
        input_text = input()
    else:
        with open(args.text_file, 'r') as read_file:
            input_text = read_file.read()
    input_text = parc(input_text)
    count_symb = len(input_text)
    dict_symb = {chr(ord('a') + i): 0 for i in range(26)}
    for elem in input_text:
        dict_symb[elem] += 1
    if count_symb == 0:
        exit("The input file does not contain any characters")
    else:
        for key in dict_symb.keys():
            dict_symb[key] = dict_symb[key] / count_symb
    with open(args.model_file, "w") as write_file:
        json.dump(dict_symb, write_file)


def hack(args):
    if args.input_file is None:
        input_text = input()
    else:
        with open(args.input_file, 'r') as read_file:
            input_text = read_file.read()
    with open(args.model_file, 'r') as read_file:
        try:
            model_dict = json.load(read_file)
        except:
            sys.exit('model_file format is json')

    # find lenght key
    my_text = input_text
    input_text = parc(input_text)
    match_index_model = sum(map(lambda x: x ** 2, model_dict.values()))
    len_key = len(input_text)
    for len_st in range(1, len(input_text) + 1):
        is_corr_st = True
        for i in range(len_st):
            s = ''.join(input_text[j * len_st + i] for j in range((len(input_text) - i + len_st - 1) // len_st))
            dict_symb = {chr(ord('a') + i): 0 for i in range(26)}
            for elem in s:
                dict_symb[elem] += 1
            if len(s) <= 1:
                sys.exit("Key lenght is not defined")
            match_index_input = sum(map(lambda x: x * (x - 1) / (len(s) * (len(s) - 1)), dict_symb.values()))
            if abs(match_index_model - match_index_input) > 0.03 or abs(match_index_input - 1 / 26) < 0.015:
                is_corr_st = False
                break
        if is_corr_st:
            len_key = len_st
            break
    if len_key == 1:
        return caesar_hack(args, my_text)

    # find the shifts of the lines
    start_string = ''.join(input_text[j * len_key] for j in range((len(input_text) + len_key - 1) // len_key))
    line_shifts = [0] * len_key
    for i in range(1, len_key):
        s = ''.join(input_text[j * len_key + i] for j in range((len(input_text) - i + len_key - 1) // len_key))
        best_caesar_shift = 0
        max_match_index_str = 0
        for caesar_shift in range(26):
            args.key = str(caesar_shift)
            curr_match_index_str = get_str_match_index(start_string, caesar_decode(args, s))
            if curr_match_index_str > max_match_index_str:
                best_caesar_shift = caesar_shift
                max_match_index_str = curr_match_index_str
        line_shifts[i] = best_caesar_shift

    # find key
    best_key = ''
    min_dist = 100
    for start_shift in range(26):
        curr_key = ''
        start_elem = chr(ord('a') + start_shift)
        for i in range(len_key):
            curr_key = curr_key + chr((ord(start_elem) + line_shifts[i] - ord('a')) % 26 + ord('a'))
        args.key = curr_key
        curr_dist = get_dist_str(model_dict, vigenere_decode(args, input_text))
        if curr_dist < min_dist:
            min_dist = curr_dist
            best_key = curr_key
    args.key = best_key

    output_text = vigenere_decode(args, my_text)
    if args.output_file is None:
        print(output_text)
    else:
        with open(args.output_file, 'w') as write_file:
            write_file.write(output_text)


def caesar_hack(args, input_text):
    with open(args.model_file, 'r') as read_file:
        model_dict = json.load(read_file)
    my_text = input_text
    input_text = parc(input_text)
    min_caesar_shift = 0
    min_dist = 100
    for caesar_shift in range(26):
        args.key = str(caesar_shift)
        curr_dist = get_dist_str(model_dict, caesar_decode(args, input_text))
        if curr_dist < min_dist:
            min_dist = curr_dist
            min_caesar_shift = caesar_shift
    args.key = str(min_caesar_shift)

    output_text = caesar_decode(args, my_text)
    if args.output_file is None:
        print(output_text)
    else:
        with open(args.output_file, 'w') as write_file:
            write_file.write(output_text)


def get_str_match_index(s1, s2):
    dict_symb_s1 = {chr(ord('a') + i): 0 for i in range(26)}
    dict_symb_s2 = {chr(ord('a') + i): 0 for i in range(26)}
    for elem in s1:
        if 'a' <= elem <= 'z':
            dict_symb_s1[elem] += 1
    for elem in s2:
        if 'a' <= elem <= 'z':
            dict_symb_s2[elem] += 1
    return sum(map(lambda x: abs(dict_symb_s1[x] * dict_symb_s2[x]) / (len(s1) * len(s2)), list(dict_symb_s1.keys())))


def get_dist_str(dict_symb, s):
    dict_symb_s = {chr(ord('a') + i): 0 for i in range(26)}
    for elem in s.lower():
        if 'a' <= elem <= 'z':
            dict_symb_s[elem] += 1
    return sum(map(lambda x: abs(dict_symb[x] - dict_symb_s[x] / len(s)), list(dict_symb.keys())))


def parc(s):
    s1 = ''
    for elem in s.lower():
        if 'a' <= elem <= 'z':
            s1 = s1 + elem
    return s1


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_encode = subparsers.add_parser('encode')
    parser_encode.add_argument('--cipher', type=str, required=True)
    parser_encode.add_argument('--key',  type=str, required=True)
    parser_encode.add_argument('--input-file', type=str)
    parser_encode.add_argument('--output-file', type=str)
    parser_encode.set_defaults(this_func=encode)

    parser_encode = subparsers.add_parser('decode')
    parser_encode.add_argument('--cipher', type=str, required=True)
    parser_encode.add_argument('--key', type=str, required=True)
    parser_encode.add_argument('--input-file', type=str)
    parser_encode.add_argument('--output-file', type=str)
    parser_encode.set_defaults(this_func=decode)

    parser_encode = subparsers.add_parser('train')
    parser_encode.add_argument('--text-file', type=str)
    parser_encode.add_argument('--model-file', type=str, required=True)
    parser_encode.set_defaults(this_func=train)

    parser_encode = subparsers.add_parser('hack')
    parser_encode.add_argument('--input-file', type=str)
    parser_encode.add_argument('--output-file', type=str)
    parser_encode.add_argument('--model-file', type=str, required=True)
    parser_encode.set_defaults(this_func=hack)

    args = parser.parse_args()
    args.this_func(args)


if __name__ == "__main__":
    main()

