from pathlib import Path

words = []

# Path to file relative to this script
file_path = Path(__file__).parent.parent / "candidatepasswords.txt"

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        words.append(line.strip())

print("[")

for word in words:
    print(f'    "{word}",')

print("]")