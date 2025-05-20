import math
from collections import Counter

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def clean_text(text):
    return ''.join(c for c in text if c in ALPHABET)

rus_letter_freq = {
    'о': 0.1097, 'е': 0.0849, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670, 'т': 0.0626,
    'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0440, 'к': 0.0349, 'м': 0.0321,
    'д': 0.0298, 'п': 0.0281, 'у': 0.0262, 'я': 0.0201, 'ы': 0.0190, 'ь': 0.0174,
    'г': 0.0165, 'з': 0.0159, 'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097,
    'ж': 0.0094, 'ш': 0.0077, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
    'ф': 0.0026, 'ъ': 0.0004}
# total = sum(rus_letter_freq.values())
# rus_letter_freq = {ch: freq/total for ch, freq in rus_letter_freq.items()}

def vigenere_encrypt(plain_text, key):
    cipher_text = []
    m = len(key)
    for i, ch in enumerate(plain_text):
        
        pi = ALPHABET.index(ch)
        ki = ALPHABET.index(key[i % m])
        
        ci = (pi + ki) % len(ALPHABET)
        cipher_text.append(ALPHABET[ci])
    return ''.join(cipher_text)


def vigenere_decrypt(cipher_text, key):
    plain_text = []
    m = len(key)
    for i, ch in enumerate(cipher_text):
        ci = ALPHABET.index(ch) 
        ki = ALPHABET.index(key[i % m])
        
        pi = (ci - ki) % len(ALPHABET)
        plain_text.append(ALPHABET[pi])
    return ''.join(plain_text)

def index_of_coincidence(text):
    N = len(text)
    freq = Counter(text)
    ic = 0
    for count in freq.values():
        ic += count * (count - 1)
    return ic / (N * (N - 1))

# Функція оцінки ймовірної довжини ключа на основі індексу 
def estimate_key_length(cipher_text, max_r=30):
    random_ic = 1 / len(ALPHABET)
    best_r = 1
    best_score = 0.0
    for r in range(2, max_r+1):
        ic_sum = 0.0
        for part in range(r):
            block = cipher_text[part::r]
            if len(block) > 1:
                ic_sum += index_of_coincidence(block)
        avg_ic = ic_sum / r
        if avg_ic > random_ic * 1.5 and avg_ic > best_score:
            best_score = avg_ic
            best_r = r
    return best_r
 


# Визначення ключа за частотою найчастішої літери 
def guess_key_by_frequency(cipher_text, key_length):
    key = []
    for j in range(key_length):
        block = cipher_text[j::key_length]
        if not block:
            key.append('?')
            continue
        freq = Counter(block)
        most_common_cipher = freq.most_common(1)[0][0]
        k = (ALPHABET.index(most_common_cipher) - ALPHABET.index('о')) % len(ALPHABET)
        key.append(ALPHABET[k])
    return ''.join(key)

# метод M(g) 
def guess_key_by_M(cipher_text, key_length):
    key = []
    N = len(ALPHABET)
    for j in range(key_length):
        block = cipher_text[j::key_length]
        if not block:
            key.append('?')
            continue
        freq = Counter(block)
        best_score = -1
        best_g = 0
        for g in range(N):
            score = 0.0
            for c, count in freq.items():
                plain_idx = (ALPHABET.index(c) - g) % N
                plain_char = ALPHABET[plain_idx]
                prob = rus_letter_freq.get(plain_char, 0)
                score += (count / len(block)) * prob
            if score > best_score:
                best_score = score
                best_g = g
        key.append(ALPHABET[best_g])
    return ''.join(key)
if __name__ == "__main__":
    with open("plaintext.txt", "r", encoding="utf-8") as f:
        plain_text = clean_text(f.read())
    print(f"Довжина відкритого тексту: {len(plain_text)}")

    sample_keys = {
        2: "аб",
        3: "абв",
        4: "абвг",
        5: "абвгд",
        'named': "дальшебоганет"
    }
    
    ic_plain = index_of_coincidence(plain_text)
    print(f"Відкритий текст: IC = {ic_plain:.4f}")
    print("Зашифровані тексти та їхні IC:\n")

    for r in [2, 3, 4, 5]:
        key = sample_keys[r]
        cipher_text = vigenere_encrypt(plain_text, key)
        ic_value = index_of_coincidence(cipher_text)
        print(f"[Ключ довжини {r} = '{key}']:\n{cipher_text[:200]}...\nIC = {ic_value:.4f}\n")

    
    key_named = sample_keys['named']
    cipher_named = vigenere_encrypt(plain_text, key_named)
    ic_named = index_of_coincidence(cipher_named)
    print(f"[Ключ = 'дальшебоганет']:\n{cipher_named[:200]}...\nIC = {ic_named:.4f}\n")

    

    
    with open("cipher.txt", "r", encoding="utf-8") as f:
        cipher_data = f.read()

    est_r = estimate_key_length(cipher_data, max_r=30)
    print(f"Оцінена довжина ключа: {est_r}")

    key_guess1 = guess_key_by_frequency(cipher_data, est_r)
    print(f"Первинна оцінка ключа (за частотами): {key_guess1}")

    key_guess2 = guess_key_by_M(cipher_data, est_r)
    print(f"Уточнений ключ (за методом M(g)): {key_guess2}")

    decrypted_text = vigenere_decrypt(cipher_data, key_guess2)
    print(f"Дешифрований текст:\n{decrypted_text[:200]}...")
    print(f"IC дешифрованого тексту: {index_of_coincidence(decrypted_text):.4f}")
