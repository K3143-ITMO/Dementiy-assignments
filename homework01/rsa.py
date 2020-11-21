import random
import sys
import typing as tp


def is_prime(n: int) -> bool:
    """
    Tests to see if a number is prime.

    >>> is_prime(2)
    True
    >>> is_prime(11)
    True
    >>> is_prime(8)
    False
    """
    # Simple trial division (optimized by 6k+-1). Slow for large n, but easy to implement.
    if n <= 3:  # 1, 2, 3 are edge cases
        return n > 1
    elif (n % 2) == 0 or (
        n % 3
    ) == 0:  # rule out even numbers and numbers divisible by 3
        return False
    else:
        i = 5
        while i ** 2 <= n:  # testing is required only to sqrt(n)
            if n % i == 0 or n % (i + 2) == 0:  # 6k - 1 and 6k + 1
                return False
            i += 6
        return True


def gcd(a: int, b: int) -> int:
    """
    Euclid's algorithm for determining the greatest common divisor.

    >>> gcd(12, 15)
    3
    >>> gcd(3, 7)
    1
    """
    # Binary GCD (Stein's algorithm), recursive version.
    # Stein's algorithm is 60% more effecient over Euclidean GCD on average.
    # gcd(0, b) == b, gcd(a, 0) == a, gcd(0, 0) == 0
    if a == b:
        return a
    elif a == 0:
        return b
    elif b == 0:
        return a
    # a is even
    # because bitwise or with one digit is basically modulo division by two
    elif a & 1 == 0:
        # b is even
        if b & 1 == 0:
            return 2 * gcd(a >> 1, b >> 1)
        # b i odd
        else:
            return gcd(a >> 1, b)
    # a is odd
    elif a & 1 != 0:
        # b is even
        if b & 1 == 0:
            return gcd(a, b >> 1)
        # b is odd and a > b
        elif a > b and b & 1 != 0:
            return gcd((a - b) >> 1, b)
        # b is odd and u is smaller than v
        else:
            return gcd((b - a) >> 1, a)
    return 0  # mypy complains about not having that


def multiplicative_inverse(e: int, phi: int) -> int:
    """
    Euclid's extended algorithm for finding the multiplicative
    inverse of two numbers.

    >>> multiplicative_inverse(7, 40)
    23
    """
    # naive method, linear complexity
    # e * inverse is 1 (in mod phi)
    # This does not include negative numbers and non-coprime numbers, as that is not needed for RSA
    e = e % phi
    for i in range(1, phi):
        if (e * i) % phi == 1:
            return i

    return 0


def generate_keypair(
    p: int, q: int
) -> tp.Tuple[tp.Tuple[int, int], tp.Tuple[int, int]]:
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Both numbers must be prime.")
    elif p == q:
        raise ValueError("p and q cannot be equal")

    n = p * q

    phi = (p - 1) * (q - 1)

    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)

    # Use Euclid's Algorithm to verify that e and phi(n) are coprime
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    # Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, phi)

    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))


def encrypt(pk: tp.Tuple[int, int], plaintext: str) -> tp.List[int]:
    # Unpack the key into it's components
    key, n = pk
    # Convert each letter in the plaintext to numbers based on
    # the character using a^b mod m
    cipher = [(ord(char) ** key) % n for char in plaintext]
    # Return the array of bytes
    return cipher


def decrypt(pk: tp.Tuple[int, int], ciphertext: tp.List[int]) -> str:
    # Unpack the key into its components
    key, n = pk
    # Generate the plaintext based on the ciphertext and key using a^b mod m
    plain = [chr((char ** key) % n) for char in ciphertext]
    # Return the array of bytes as a string
    return "".join(plain)


if __name__ == "__main__":
    print("RSA Encrypter/ Decrypter")
    p = int(input("Enter a prime number (17, 19, 23, etc): "))
    q = int(input("Enter another prime number (Not one you entered above): "))
    print("Generating your public/private keypairs now . . .")
    public, private = generate_keypair(p, q)
    print("Your public key is ", public, " and your private key is ", private)
    message = input("Enter a message to encrypt with your private key: ")
    encrypted_msg = encrypt(private, message)
    print("Your encrypted message is: ")
    print("".join(map(lambda x: str(x), encrypted_msg)))
    print("Decrypting message with public key ", public, " . . .")
    print("Your message is:")
    print(decrypt(public, encrypted_msg))
