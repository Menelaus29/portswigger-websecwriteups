input_file = "candidatepasswords.txt"
output_file = "lab-broken-bruteforce-protection-ip-block/integratedpasswords.txt"
to_add = "peter"

with open(input_file, "r") as f:
    passwords = f.read().splitlines()

with open(output_file, "w") as f:
    for pwd in passwords:
        f.write(pwd + "\n")
        f.write(to_add + "\n")