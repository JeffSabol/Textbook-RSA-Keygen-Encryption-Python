# Author:      Jeff Sabol

from cmath import exp
import math
import random
import argparse

# to_int() reads the given file and converts its contents to an integer
# Input:   file_name; The path to an existing file
# Output:  int_val  ; An integer representative of the file's contents
def to_int(file_name):
    # Read file contents
    with open(file_name, "r") as f:
        file_contents = f.read().strip()

    # If the file contents are already numeric, cast to an int
    int_val = 0
    if file_contents.isnumeric():
        int_val = int(file_contents)

    # Otherwise, encode as an integer
    else:
        for i, char in enumerate(file_contents[::-1]):
            int_val += ord(char) << i * 8

    return int_val

# to_file() writes the given data to a file
# Input:   out_val  ; The data to output
# Input:   file_name; The path to an existing file
# Output:  None
def to_file(out_val, file_name, needs_conversion=False):
    # If conversion is needed, encode integer to string
    str_val = str(out_val)
    if needs_conversion:
        str_val = bytearray()
        while out_val:
            byte = out_val & 0xff
            out_val >>= 8
            str_val.append(byte)
        str_val.reverse()
        str_val = bytes(str_val).decode("utf-8")
    with open(file_name, "w") as f:
        f.write(str_val)
    return

# fermat_primality_test() tests if a number is prime or not,
#         for a specific number of iteration attempts
# Input:  num;      The integer to be tested for primality
#         max_iter; The number of testing attempts to be made
# Output: Boolean;  False if not prime, True if non-primality not seen
def fermat_primality_test(num, max_iter):
    for _ in range(max_iter):
        a = random.randint(1,num-1) # a is greater than 1, but at least one less than num var
        if(math.gcd(a,num) != 1):
            return False #num is composite AKA not prime
        #if (a**(num-1)) % num != 1: #maybe use pow() function to make more efficient
        if (pow(a,num-1,num)!= 1):
            return False
    return True

# generate_prime() generates a prime number
# Input:           num_bits; The size of the number to be generated (in bits)
# Output:          num;      A (likely) prime number of the requested bit size
def generate_prime(num_bits):
    
    num = random.getrandbits(num_bits)

    while(fermat_primality_test(num,1000)==False):
        num = random.getrandbits(num_bits)
    return num

# mod_mult_inverse() calculates the modular multiplicative inverse
# Input:  num;     An integer for which we want to find the mod
#                  multiplicate inverse for
#         modulus; An integer for which we want to find congruence
#                  with respect to
# Output: b;       An integer which is the inverse mod modulus
def mod_mult_inverse(num, modulus):
    t_prev, t_curr = 0, 1
    r_prev, r_curr = modulus, num
    while r_curr != 0:
        q = r_prev // r_curr
        t_prev, t_curr = t_curr, t_prev - q * t_curr
        r_prev, r_curr = r_curr, r_prev - q * r_curr
    b = t_prev
    if b < 0:
        b = b + modulus
    return b

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="modes", dest="mode")

    # Key generation mode command-line arguments
    keygen = subparsers.add_parser("keygen")
    keygen.add_argument("--e-file", required=True,
                        help="Name of the file containing the public " +
                        "exponent e (file must exist before key generation")
    keygen.add_argument("--key-size", type=int, required=True,
                        choices=[512, 1024, 2048],
                        help="The size of the RSA key in bits")
    keygen.add_argument("--n-file", required=True,
                                                help="File name to write the modulus n to")
    keygen.add_argument("--d-file", required=True,
                        help="File name to write the private exponent d to")

    # Encryption mode command-line arguments
    encrypt = subparsers.add_parser("encrypt")
    encrypt.add_argument("--input-file", required=True,
                         help="File containing the input for encrypting/" +
                         "decrypting/signing")
    encrypt.add_argument("--exponent-file", required=True,
                         help="Name of the file containing the exponent")
    encrypt.add_argument("--modulus-file", required=True,
                         help="Name of the file containing the modulus")
    encrypt.add_argument("--output-file", required=True,
                         help="Name of the file to write the output to")

    args = parser.parse_args()

    # Key generation mode
    if args.mode == "keygen":

        # ask RJ if I did this correct
        #!      did I use argparser correctly?     !

        # Read e from file
        e = to_int(args.e_file)

        # Generate p and q
        p = generate_prime(args.key_size/2)
        q = generate_prime(args.key_size/2)
        print("p:\t{}\nq:\t{}".format(p, q))

        # Calculate n
        n = p*q
        print("n:\t{}".format(n))

        # Calculate phi(n)
        phi_n = (p-1)*(q-1)
        print("phi_n:\t{}".format(phi_n))

        # Calculate the private exponent d
        d = 1/(e%phi_n)
        print("e:\t{}\nd:\t{}".format(e, d))

        # Write n and d to files
        to_file(n, args.n_file)
        to_file(d, args.d_file)

    # Encryption mode (for encryption/decryption/signing)
    elif args.mode == "encrypt":
        # Read files containing the input, exponent, and modulus
        input_val = to_int(args.input_file)
        exponent_val = to_int(args.exponent_file)
        modulus_val = to_int(args.modulus_file)

        # Calculate the ouptput value using the input, exponent, and modulus
        # This should be a generalized form that works for encryption,
        # decryption, and signing (the only difference should be the arguments
        # that you pass in on the command line)
        output_val = None # TODO

        # Write output value to file (Yes I know this code is ugly -RJ)
        with open(args.input_file, "r") as f:
            orig_input = f.read().strip()
        if orig_input.isnumeric():
            to_file(output_val, args.output_file, needs_conversion=True)
        else:
            to_file(output_val, args.output_file)
        with open(args.output_file, "r") as f:
            print("output:\t{}".format(f.read().strip()))

    else:
        print("Invalid mode. Use python hw1.py -h for help.")