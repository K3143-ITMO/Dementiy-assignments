import string
import typing as tp


def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    ascii_uppercase_letters_end = ord("Z")
    ascii_lowercase_letters_end = ord("z")
    alphabet_len = len(string.ascii_lowercase)  # length of latin alphabet
    for i in plaintext:
        if (
            i in string.ascii_letters
        ):  # ascii_letters is both predefined and locale-independent
            if (i in string.ascii_lowercase) and (
                ord(i) + shift > ascii_lowercase_letters_end
            ):  # shifting of letters that loop back to the start of the alphabet
                ciphertext += chr(ord(i) - alphabet_len + shift)  # lowercase letters
            elif (i in string.ascii_uppercase) and (
                ord(i) + shift > ascii_uppercase_letters_end
            ):  # shifting of letters that loop back to the start of the alphabet
                ciphertext += chr(ord(i) - alphabet_len + shift)  # uppercase letters
            else:
                ciphertext += chr(ord(i) + shift)  # base case
        else:
            ciphertext += i  # digits, punctuation and special symbols
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    # Decrypting Caesar cipher is basically encrypting the input again with negative shift.
    # Could have implemented a alphabet loop shift in reverse in encrypt_caesar() and called encrypt_caesar(ciphertext, -1*shift)
    # Will not test that, though.
    ascii_uppercase_letters_start = ord("A")
    ascii_lowercase_letters_start = ord("a")
    alphabet_len = len(string.ascii_lowercase)
    for i in ciphertext:
        if i in string.ascii_letters:
            if (i in string.ascii_lowercase) and (
                ord(i) - shift < ascii_lowercase_letters_start
            ):  # shifting of letters that loop back to the end of the alphabet
                plaintext += chr(ord(i) + alphabet_len - shift)  # lowercase letters
            elif (i in string.ascii_uppercase) and (
                ord(i) - shift < ascii_uppercase_letters_start
            ):  # shifting of letters that loop back to the end of the alphabet
                plaintext += chr(ord(i) + alphabet_len - shift)  # uppercase letters
            else:
                plaintext += chr(ord(i) - shift)  # base decryption
        else:
            plaintext += i  # digits, punctuation and special symbols are unshifted
    return plaintext


def caesar_breaker_brute_force(ciphertext: str, dictionary: tp.Set[str]) -> int:
    """
    Brute force breaking a Caesar cipher.
    """
    best_shift = 0
    alphabet_len = len(string.ascii_lowercase)  # length of alphabet
    for i in range(
        0, alphabet_len
    ):  # i hope nobody shifts more than that, as it is unreasonable
        try_plain = decrypt_caesar(ciphertext, i)  # decryption attempt
        if try_plain in dictionary:
            best_shift = i
    return best_shift
