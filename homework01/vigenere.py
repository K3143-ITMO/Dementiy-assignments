import string


def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    # Viginere cipher is an extension of the Caesar cipher, which has shift calculated individually using a keyword
    # Alphabet position for a letter in the keyword is the shift(with a as 0)
    ascii_uppercase_letters_end = ord("Z")
    ascii_lowercase_letters_end = ord("z")
    ascii_uppercase_letters_start = ord("A")
    ascii_lowercase_letters_start = ord("a")
    alphabet_len = len(string.ascii_lowercase)  # length of latin alphabet
    # I need indices, so i have to use range since a simple "for i in smth" loop has no simple way of getting the element index
    for i in range(len(plaintext)):
        key_pos = i % (len(keyword))  # letter position in keyword, range [0; len(keyword))
        # determining shift
        # Wanted to use modulo division, but the rems are different for uppercase and lowercase
        # I'll stick with the method of checking case and subtracting ascii_letters_start consts
        # N.B: Assuming the keyword only contains letters
        shift = 0
        if keyword[key_pos] in string.ascii_uppercase:
            shift = ord(keyword[key_pos]) - ascii_uppercase_letters_start
        elif keyword[key_pos] in string.ascii_lowercase:
            shift = ord(keyword[key_pos]) - ascii_lowercase_letters_start
        else:
            continue  # SUGGESTION: add an exception for that
        # encrypting
        character = plaintext[i]
        if character in string.ascii_letters:
            if (character in string.ascii_lowercase) and (
                ord(character) + shift > ascii_lowercase_letters_end
            ):  # shifting of letters that loop back to the start of the alphabet
                ciphertext += chr(ord(character) - alphabet_len + shift)  # lowercase letters
            elif (character in string.ascii_uppercase) and (
                ord(character) + shift > ascii_uppercase_letters_end
            ):  # shifting of letters that loop back to the start of the alphabet
                ciphertext += chr(ord(character) - alphabet_len + shift)  # uppercase letters
            else:
                ciphertext += chr(ord(character) + shift)  # base case
        else:
            ciphertext += character  # digits, punctuation and special symbols
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    ascii_uppercase_letters_start = ord("A")
    ascii_lowercase_letters_start = ord("a")
    alphabet_len = len(string.ascii_lowercase)  # length of latin alphabet
    # I need indices, so i have to use range since a simple "for i in smth" loop has no simple way of getting the element index
    for i in range(len(ciphertext)):
        key_pos = i % (len(keyword))  # letter position in keyword, range [0; len(keyword))
        # determining shift
        # Wanted to use modulo division, but the rems are different for uppercase and lowercase
        # I'll stick with the method of checking case and subtracting ascii_letters_start consts
        # N.B: Assuming the keyword only contains letters
        shift = 0
        if keyword[key_pos] in string.ascii_uppercase:
            shift = ord(keyword[key_pos]) - ascii_uppercase_letters_start
        elif keyword[key_pos] in string.ascii_lowercase:
            shift = ord(keyword[key_pos]) - ascii_lowercase_letters_start
        else:
            continue  # SUGGESTION: add an exception for that
        # encrypting
        character = ciphertext[i]
        if character in string.ascii_letters:
            if (character in string.ascii_lowercase) and (
                ord(character) - shift < ascii_lowercase_letters_start
            ):  # shifting of letters that loop back to the start of the alphabet
                plaintext += chr(ord(character) + alphabet_len - shift)  # lowercase letters
            elif (character in string.ascii_uppercase) and (
                ord(character) - shift < ascii_uppercase_letters_start
            ):  # shifting of letters that loop back to the start of the alphabet
                plaintext += chr(ord(character) + alphabet_len - shift)  # uppercase letters
            else:
                plaintext += chr(ord(character) - shift)  # base case
        else:
            plaintext += character  # digits, punctuation and special symbols
    return plaintext
