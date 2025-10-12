import customtkinter
from tkinter import messagebox
from collections import OrderedDict
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ==============================================================================
# BAGIAN 1: LOGIKA INTI CIPHER
# ==============================================================================

# --- CIPHER KLASIK ---

def generate_key_matrix(key_phrase):
    """Membuat matriks Playfair 5x5."""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key_clean = "".join(OrderedDict.fromkeys(filter(str.isalpha, key_phrase.upper().replace('J', 'I'))))
    matrix_string = key_clean + "".join([c for c in alphabet if c not in key_clean])
    return [list(matrix_string[i:i+5]) for i in range(0, 25, 5)]

def prepare_plaintext(plaintext):
    """Menyiapkan plaintext untuk enkripsi Playfair."""
    separator = 'X'
    clean_text = list("".join(filter(str.isalpha, plaintext.upper().replace('J', 'I'))))
    if not clean_text:
        return []
    i = 0
    while i < len(clean_text) - 1:
        if clean_text[i] == clean_text[i+1]:
            clean_text.insert(i + 1, separator)
        i += 2
    if len(clean_text) % 2 != 0:
        clean_text.append(separator)
    final_text = "".join(clean_text)
    return [final_text[j:j+2] for j in range(0, len(final_text), 2)]

def playfair_process(text_input, key_phrase, mode):
    """Fungsi utama untuk enkripsi dan dekripsi Playfair."""
    matrix = generate_key_matrix(key_phrase)
    coords_map = {char: (r, c) for r, row in enumerate(matrix) for c, char in enumerate(row)}
    
    if mode == 'encrypt':
        digraphs = prepare_plaintext(text_input)
    else:
        clean_text = "".join(filter(str.isalpha, text_input.upper().replace('J', 'I')))
        digraphs = [clean_text[i:i+2] for i in range(0, len(clean_text), 2)]
        
    result_text = ""
    shift = 1 if mode == 'encrypt' else -1

    for char1, char2 in digraphs:
        if char1 not in coords_map or char2 not in coords_map:
            continue
        r1, c1 = coords_map[char1]
        r2, c2 = coords_map[char2]
        if r1 == r2:
            result_text += matrix[r1][(c1 + shift) % 5] + matrix[r2][(c2 + shift) % 5]
        elif c1 == c2:
            result_text += matrix[(r1 + shift) % 5][c1] + matrix[(r2 + shift) % 5][c2]
        else:
            result_text += matrix[r1][c2] + matrix[r2][c1]
    return result_text

def caesar_process(text_input, key, mode):
    """Fungsi untuk enkripsi dan dekripsi Caesar."""
    result = []
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    shift = key if mode == 'encrypt' else -key
    for char in text_input.upper():
        if char in alphabet:
            new_pos = (alphabet.find(char) + shift) % 26
            result.append(alphabet[new_pos])
        else:
            result.append(char)
    return "".join(result)

# --- CIPHER MODERN (AES) ---

def aes_process(text_input, key, mode):
    """Fungsi untuk enkripsi dan dekripsi AES-128 ECB."""
    try:
        # 1. Ubah kunci string menjadi kunci 16-byte menggunakan hash
        key_bytes = hashlib.sha256(key.encode()).digest()[:16]
        
        # 2. Buat objek cipher AES dengan mode ECB
        cipher = AES.new(key_bytes, AES.MODE_ECB)

        if mode == 'encrypt':
            # Ubah teks menjadi byte, tambahkan padding, lalu enkripsi
            data_bytes = text_input.encode('utf-8')
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_bytes = cipher.encrypt(padded_data)
            # Encode hasil biner ke Base64 agar bisa ditampilkan
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        else: # mode == 'decrypt'
            # Decode dari Base64 ke biner, dekripsi, lalu hapus padding
            data_bytes = base64.b64decode(text_input)
            decrypted_bytes = cipher.decrypt(data_bytes)
            unpadded_data = unpad(decrypted_bytes, AES.block_size)
            # Ubah kembali byte menjadi string
            return unpadded_data.decode('utf-8')
    except (ValueError, KeyError):
        # Error ini biasanya terjadi jika kunci salah atau ciphertext rusak
        return "DEKRIPSI GAGAL (Kunci salah atau data tidak valid)"


# ==============================================================================
# BAGIAN 2: APLIKASI GUI
# ==============================================================================

class ChainedCipherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kriptografi Klasik & Modern (AES)")
        self.geometry("800x700")
        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e1e")

        main_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(main_frame, text="Playfair, Caesar & AES Cipher", font=("Inter", 32, "bold"))
        title_label.pack(pady=(10, 20))

        input_card = customtkinter.CTkFrame(main_frame, corner_radius=15, fg_color="#2b2b2b")
        input_card.pack(fill="x", padx=10, pady=10)
        
        input_title = customtkinter.CTkLabel(input_card, text="Pengaturan Teks & Kunci", font=("Inter", 18, "bold"))
        input_title.pack(pady=(15, 10))

        self.text_entry = customtkinter.CTkEntry(input_card, placeholder_text="Masukkan Teks Anda", font=("Inter", 14), height=45, corner_radius=10)
        self.text_entry.pack(fill="x", padx=15, pady=5)
        self.playfair_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci Playfair (Frasa)", font=("Inter", 14), height=45, corner_radius=10)
        self.playfair_key_entry.pack(fill="x", padx=15, pady=5)
        self.caesar_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci Caesar (Angka)", font=("Inter", 14), height=45, corner_radius=10)
        self.caesar_key_entry.pack(fill="x", padx=15, pady=5)
        # TAMBAHAN: Input untuk kunci AES
        self.aes_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci AES (Teks/Angka)", font=("Inter", 14), height=45, corner_radius=10)
        self.aes_key_entry.pack(fill="x", padx=15, pady=(5, 20))

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        encrypt_button = customtkinter.CTkButton(button_frame, text="🔒 Enkripsi", command=lambda: self.run_process('encrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#2c7a4d", hover_color="#1f5736", corner_radius=10)
        encrypt_button.pack(side="left", expand=True, padx=5)
        decrypt_button = customtkinter.CTkButton(button_frame, text="🔓 Dekripsi", command=lambda: self.run_process('decrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#b85b21", hover_color="#8a4418", corner_radius=10)
        decrypt_button.pack(side="right", expand=True, padx=5)

        result_card = customtkinter.CTkFrame(main_frame, corner_radius=15, fg_color="#2b2b2b")
        result_card.pack(fill="x", padx=10, pady=10)

        result_header_frame = customtkinter.CTkFrame(result_card, fg_color="transparent")
        result_header_frame.pack(fill="x", padx=15, pady=(15, 10))
        result_title = customtkinter.CTkLabel(result_header_frame, text="Hasil Akhir", font=("Inter", 18, "bold"))
        result_title.pack(side="left")
        
        self.copy_button = customtkinter.CTkButton(result_header_frame, text="📋 Salin", width=100, command=self.copy_to_clipboard, font=("Inter", 12))
        self.copy_button.pack(side="right")
        
        self.result_label = customtkinter.CTkLabel(result_card, text="", font=("Courier New", 16), wraplength=650, justify="left", fg_color="#1e1e1e", corner_radius=10)
        self.result_label.pack(fill="x", padx=15, pady=(0, 15), ipady=10)

    def copy_to_clipboard(self):
        """Menyalin teks dari label hasil ke clipboard."""
        text_to_copy = self.result_label.cget("text")
        if text_to_copy and "DEKRIPSI GAGAL" not in text_to_copy:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            original_text = self.copy_button.cget("text")
            self.copy_button.configure(text="✔ Tersalin!")
            self.after(2000, lambda: self.copy_button.configure(text=original_text))

    def run_process(self, mode):
        input_text = self.text_entry.get()
        playfair_key = self.playfair_key_entry.get().strip()
        caesar_key_str = self.caesar_key_entry.get().strip()
        aes_key = self.aes_key_entry.get().strip()

        if not all([input_text, playfair_key, caesar_key_str, aes_key]):
            messagebox.showerror("Error", "Semua field harus diisi.")
            return
        
        try:
            caesar_key = int(caesar_key_str)
        except ValueError:
            messagebox.showerror("Error", "Kunci Caesar harus berupa angka.")
            return

        try:
            if mode == 'encrypt':
                # Alur Enkripsi: Teks -> Playfair -> Caesar -> AES
                playfair_result = playfair_process(input_text, playfair_key, 'encrypt')
                caesar_result = caesar_process(playfair_result, caesar_key, 'encrypt')
                final_result = aes_process(caesar_result, aes_key, 'encrypt')
            else: # mode == 'decrypt'
                # Alur Dekripsi DIBALIK: Teks -> AES -> Caesar -> Playfair
                aes_result = aes_process(input_text, aes_key, 'decrypt')
                if "DEKRIPSI GAGAL" in aes_result:
                    final_result = aes_result
                else:
                    caesar_result = caesar_process(aes_result, caesar_key, 'decrypt')
                    final_result = playfair_process(caesar_result, playfair_key, 'decrypt')
            
            self.result_label.configure(text=final_result)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan tak terduga: {e}")

if __name__ == "__main__":
    app = ChainedCipherApp()
    app.mainloop()
