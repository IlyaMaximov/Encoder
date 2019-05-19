import argparse
import json
import sys

SIZE_ALPHABET = 26


def read_from_file(input_file):
    if input_file is None:
        return sys.stdin.read()
    with open(input_file, 'r') as read_file:
        return read_file.read()


def write_to_file(output_file, text):
    if output_file is None:
        print(text)
    else:
        with open(output_file, 'w') as write_file:
            return write_file.write(text)


def encode(args):
    input_text = read_from_file(args.input_file)
    if args.cipher == 'caesar':
        output_text = caesar_encode(args, input_text)
    elif args.cipher == 'vigenere':
        output_text = vigenere_encode(args, input_text)
    else:
        output_text = vernam_encode_decode(args, input_text)

    write_to_file(args.output_file, output_text)


def decode(args):
    input_text = read_from_file(args.input_file)

    if args.cipher == 'caesar':
        output_text = caesar_decode(args, input_text)
    elif args.cipher == 'vigenere':
        output_text = vigenere_decode(args, input_text)
    else:
        output_text = vernam_encode_decode(args, input_text)

    write_to_file(args.output_file, output_text)


def caesar_encode(args, input_text):
    if not args.key.isdigit():
        sys.exit("The key of сaesar's cipher is a number")
    caesar_shift = int(args.key)
    encode_text_list = []
    for symb in input_text:
        if 'a' <= symb.lower() <= 'z':
            elem = chr((ord(symb.lower()) - ord('a') + caesar_shift) % SIZE_ALPHABET + ord('a'))
            if symb.isupper():
                elem = elem.upper()
            encode_text_list.append(elem)
        else:
            encode_text_list.append(symb)
    return ''.join(encode_text_list)


def vigenere_encode(args, input_text):
    if not args.key.isalpha():
        exit("The key of vigenere's cipher is a word")
    key_str = args.key.lower()
    key_index = 0
    new_text = []
    for symb in input_text:
        if 'a' <= symb.lower() <= 'z':
            key_elem = key_str[key_index % len(key_str)].lower()
            elem = chr((ord(key_elem) + ord(symb.lower()) - 2 * ord('a')) % SIZE_ALPHABET + ord('a'))
            if symb.isupper():
                elem = elem.upper()
            new_text.append(elem)
            key_index += 1
        else:
            new_text.append(symb)
    input_text = ''.join(new_text)
    return input_text


def vernam_encode_decode(args, input_text):
    if not args.key.isalpha():
        exit("The key of vigenere's cipher is a word")
    size_block = 32
    ans_list = []
    for i in range(len(input_text)):
        if 0 <= ord(input_text[i]) - ord('a') < size_block or 0 <= ord(input_text[i]) - ord('A') < size_block:
            key_elem = args.key[i % len(args.key)].lower()
            elem = chr(((ord(input_text[i]) - ord('a')) ^ (ord(key_elem) - ord('a'))) + ord('a'))
            ans_list.append(elem)
    input_text = ''.join(ans_list)
    return input_text


def caesar_decode(args, input_text):
    if not args.key.isdigit():
        sys.exit("The key of сaesar's cipher is a number")
    args.key = str(SIZE_ALPHABET - int(args.key))
    return caesar_encode(args, input_text)


def vigenere_decode(args, input_text):
    if not args.key.isalpha():
        exit("The key of vigenere's cipher is a word")
    args.key = args.key.lower()
    key_list = []
    for symb in args.key:
        key_list.append(chr((ord('a') + SIZE_ALPHABET - ord(symb)) % SIZE_ALPHABET + ord('a')))
    args.key = ''.join(key_list)
    return vigenere_encode(args, input_text)


def train(args):
    input_text = read_from_file(args.text_file)
    input_text = parc(input_text)
    count_symb = len(input_text)
    dict_symb = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
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
    input_text = read_from_file(args.input_file)
    with open(args.model_file, 'r') as read_file:
        try:
            model_dict = json.load(read_file)
        except Exception:
            sys.exit('model_file format is json')

    my_text = input_text
    input_text = parc(input_text)
    len_key = hack_find_len_key(input_text, model_dict)
    if len_key == 1:
        return caesar_hack(args, my_text)
    line_shifts = hack_find_line_shifts(args, input_text, len_key)

    best_key = ''
    min_dist = float("inf")
    for start_shift in range(SIZE_ALPHABET):
        curr_key_list = []
        start_elem = chr(ord('a') + start_shift)
        for i in range(len_key):
            curr_key_list.append(chr((ord(start_elem) + line_shifts[i] - ord('a')) % SIZE_ALPHABET + ord('a')))
        curr_key = ''.join(curr_key_list)
        args.key = curr_key
        curr_dist = get_dist_str(model_dict, vigenere_decode(args, input_text))
        if curr_dist < min_dist:
            min_dist = curr_dist
            best_key = curr_key
    args.key = best_key

    output_text = vigenere_decode(args, my_text)
    write_to_file(args.output_file, output_text)


def hack_find_len_key(input_text, model_dict):
    match_index_model = sum(map(lambda x: x ** 2, model_dict.values()))
    len_key = len(input_text)
    for curr_len in range(1, len(input_text) + 1):
        is_corr_st = True
        for i in range(curr_len):
            key_s = input_text[i::curr_len]
            dict_symb = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
            for elem in key_s:
                dict_symb[elem] += 1
            if len(key_s) <= 1:
                sys.exit("Key lenght is not defined, hack is impossible")
            match_index_input = sum(map(lambda x: x * (x - 1) / (len(key_s) * (len(key_s) - 1)), dict_symb.values()))
            if abs(match_index_model - match_index_input) > 0.03 or abs(match_index_input - 1 / SIZE_ALPHABET) < 0.015:
                is_corr_st = False
                break
        if is_corr_st:
            len_key = curr_len
            break
    return len_key


def hack_find_line_shifts(args, input_text, len_key):
    start_string = ''.join(input_text[j * len_key] for j in range((len(input_text) + len_key - 1) // len_key))
    line_shifts = [0] * len_key
    for i in range(1, len_key):
        gen_str = ''.join(input_text[j * len_key + i] for j in range((len(input_text) - i + len_key - 1) // len_key))
        best_caesar_shift = 0
        max_match_index_str = 0
        for caesar_shift in range(SIZE_ALPHABET):
            args.key = str(caesar_shift)
            curr_match_index_str = get_str_match_index(start_string, caesar_decode(args, gen_str))
            if curr_match_index_str > max_match_index_str:
                best_caesar_shift = caesar_shift
                max_match_index_str = curr_match_index_str
        line_shifts[i] = best_caesar_shift
    return line_shifts


def caesar_hack(args, input_text):
    with open(args.model_file, 'r') as read_file:
        model_dict = json.load(read_file)
    my_text = input_text

    input_text = parc(input_text)
    min_caesar_shift = 0
    min_dist = float("inf")
    my_tmp_dict = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
    args.key = '0'
    for elem in caesar_decode(args, input_text).lower():
        if 'a' <= elem <= 'z':
            my_tmp_dict[elem] += 1
    for caesar_shift in range(SIZE_ALPHABET):
        curr_dist = sum(map(lambda x: abs(my_tmp_dict[x] - model_dict[x] / len(input_text)), list(my_tmp_dict.keys())))
        if curr_dist < min_dist:
            min_dist = curr_dist
            min_caesar_shift = caesar_shift
        histogram_shift(my_tmp_dict)
    args.key = str(SIZE_ALPHABET - min_caesar_shift)

    output_text = caesar_decode(args, my_text)
    write_to_file(args.output_file, output_text)


def get_str_match_index(input_str1, input_str2):
    dict_symb_s1 = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
    dict_symb_s2 = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
    for elem in input_str1:
        if 'a' <= elem <= 'z':
            dict_symb_s1[elem] += 1
    for elem in input_str2:
        if 'a' <= elem <= 'z':
            dict_symb_s2[elem] += 1
    return sum(map(lambda x: abs(dict_symb_s1[x] * dict_symb_s2[x]) / (len(input_str1) * len(input_str2)),
                   list(dict_symb_s1.keys())))


def histogram_shift(my_dict):
    koll_z = my_dict['z']
    for shift in range(SIZE_ALPHABET - 1):
        my_dict[chr(ord('a') + SIZE_ALPHABET - shift - 1)] = my_dict[chr(ord('a') + SIZE_ALPHABET - shift - 2)]
    my_dict['a'] = koll_z


def get_dist_str(dict_symb, str_input):
    dict_symb_s = {chr(ord('a') + i): 0 for i in range(SIZE_ALPHABET)}
    for elem in str_input.lower():
        if 'a' <= elem <= 'z':
            dict_symb_s[elem] += 1
    return sum(map(lambda x: abs(dict_symb[x] - dict_symb_s[x] / len(str_input)), list(dict_symb.keys())))


def parc(input_str):
    res_str = []
    for elem in input_str.lower():
        if 'a' <= elem <= 'z':
            res_str.append(elem)
    return ''.join(res_str)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_encode = subparsers.add_parser('encode')
    parser_encode.add_argument('--cipher', choices=['caesar', 'vigenere', 'vernam'], type=str, required=True)
    parser_encode.add_argument('--key', type=str, required=True)
    parser_encode.add_argument('--input-file', type=str)
    parser_encode.add_argument('--output-file', type=str)
    parser_encode.set_defaults(this_func=encode)

    parser_encode = subparsers.add_parser('decode')
    parser_encode.add_argument('--cipher', choices=['caesar', 'vigenere', 'vernam'], type=str, required=True)
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

    args = parser.parse_args('hack --input-file output.txt --model-file model.json'.split())
    args.this_func(args)


if __name__ == "__main__":
    main()
