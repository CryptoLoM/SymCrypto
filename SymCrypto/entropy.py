import math
from prettytable import PrettyTable
from collections import Counter, defaultdict

# Російський алфавіт + пробіл
ALPHABET = ' абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
ALPHABET = ALPHABET.replace('ё', 'е').replace('ъ', 'ь')

# Російський алфавіт + пробіл
S_ALPHABET = ALPHABET.replace('ё', 'е').replace('ъ', 'ь').replace(' ', '')

# === Очищення тексту ===
def clean_text(text):
    text = text.lower()
    text = text.replace('ё', 'е').replace('ъ', 'ь')
    return ''.join(c for c in text if c in ALPHABET)

def clean_space_and_text(text):
    text = text.lower()
    text = text.replace('ё', 'е').replace('ъ', 'ь').replace(' ', '')
    return ''.join(c for c in text if c in S_ALPHABET)

# === Частоти 1-грам і біграм ===
def get_frequencies(text):
    letter_freq = Counter(text)
    bigram_freq = Counter(text[i:i+2] for i in range(len(text)-1))
    return letter_freq, bigram_freq

# === Обчислення ентропії ===
def entropy(freq_dict, total):
    return -sum((cnt / total) * math.log2(cnt / total) for cnt in freq_dict.values())

# === Підрахунок H1, H2 ===
def compute_entropy(text):
    letter_freq, bigram_freq = get_frequencies(text)
    total_letters = sum(letter_freq.values())
    total_bigrams = sum(bigram_freq.values())

    H1 = entropy(letter_freq, total_letters)
    H2_total = entropy(bigram_freq, total_bigrams)
    H2 = H2_total / 2  # на 1 символ біграми


    return H1, H2, letter_freq, bigram_freq

def compute_entropy_without_space(text):
    letter_freq, bigram_freq = get_frequencies(text)
    total_letters = sum(letter_freq.values())
    total_bigrams = sum(bigram_freq.values())

    H1_s = entropy(letter_freq, total_letters)
    H2_S_total = entropy(bigram_freq, total_bigrams)
    H2_S = H2_S_total / 2

    return H1_s, H2_S,letter_freq, bigram_freq

# === Метод вгадування для умовної ентропії ===
def guess_entropy(text, n, alphabet):
    context_counter = defaultdict(Counter)

    for i in range(len(text) - n):
        context = text[i:i + n - 1]
        next_char = text[i + n - 1]
        if all(c in alphabet for c in context + next_char):
            context_counter[context][next_char] += 1

    total_guesses = 0
    correct_guesses = 0

    for context, next_chars in context_counter.items():
        most_common_char = next_chars.most_common(1)[0][0]
        correct_guesses += next_chars[most_common_char]
        total_guesses += sum(next_chars.values())

    guess_prob = correct_guesses / total_guesses if total_guesses > 0 else 0.00001
    conditional_entropy = -math.log2(guess_prob)

    return conditional_entropy

def save_bigram_table_to_txt(bigram_counter, filename="bigram_table.txt"):
    symbols = sorted(set(S_ALPHABET))

    table = PrettyTable()

    # Заголовок таблиці
    table.field_names = [" "] + symbols

    for row_char in symbols:
        row_data = [row_char]
        for col_char in symbols:
            bg = row_char + col_char
            count = bigram_counter.get(bg, 0)
            row_data.append(str(count))
        table.add_row(row_data)

    # Збереження у файл
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(table))

    print(f"\n Таблиця біграм збережена у файл: {filename}")


if __name__ == "__main__":
    with open("text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    filtered_text = clean_text(raw_text)
    H1, H2, letters, bigrams = compute_entropy(filtered_text)
    filtered_space_and_text = clean_space_and_text(raw_text)
    H1_S, H2_S, letterss, bigramss = compute_entropy(filtered_space_and_text)

    print(f"Ентропія (H1): {H1:.4f} біт")
    print(f"Ентропія (H2): {H2:.4f} біт")
    print(f"Ентропія (H1) без пробілів: {H1_S:.4f} біт")
    print(f"Ентропія без пробілів (H2): {H2_S:.4f} біт")

    print("\nТоп-10 символів:")
    for char, count in letters.most_common(10):
        print(f"{repr(char)}: {count}")

    save_bigram_table_to_txt(bigramss)  # або bigrams — якщо з пробілами


    # === Умовна ентропія H(n) для n = 10, 20 ===
    for n in [10, 20]:
        hn = guess_entropy(filtered_text, n, ALPHABET)
        print(f"H({n}) ≈ {hn:.4f} біт")
        hn_s = guess_entropy(filtered_space_and_text, n, ALPHABET)
        print(f"H({n} без пробілів) ≈ {hn_s:.4f} біт")

    # Максимальна ентропія H0 = log2(32)
    H0 = math.log2(32)
    redundancy_H1 = 1 - H1 / H0
    redundancy_H2 = 1 - H2 / H0
    print(f"\nH0 = {H0:.4f} біт")
    print(f"Надлишковість R (за H1): {redundancy_H1:.4f}")
    print(f"Надлишковість R (за H2): {redundancy_H2:.4f}")
