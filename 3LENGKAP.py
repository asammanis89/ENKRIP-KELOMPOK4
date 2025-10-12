import customtkinter
from tkinter import messagebox
from collections import OrderedDict
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ==============================================================================
# BAGIAN 1: LOGIKA INTI CIPHER (TETAP SAMA)
# ==============================================================================

def generate_key_matrix(key_phrase):
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key_clean = "".join(OrderedDict.fromkeys(filter(str.isalpha, key_phrase.upper().replace('J', 'I'))))
    matrix_string = key_clean + "".join([c for c in alphabet if c not in key_clean])
    return [list(matrix_string[i:i+5]) for i in range(0, 25, 5)]

def prepare_plaintext(plaintext):
    separator = 'X'
    clean_text = list("".join(filter(str.isalpha, plaintext.upper().replace('J', 'I'))))
    if not clean_text: return []
    i = 0
    while i < len(clean_text) - 1:
        if clean_text[i] == clean_text[i+1]: clean_text.insert(i + 1, separator)
        i += 2
    if len(clean_text) % 2 != 0: clean_text.append(separator)
    return "".join(clean_text)

def playfair_process(text_input, key_phrase, mode):
    matrix = generate_key_matrix(key_phrase)
    coords_map = {char: (r, c) for r, row in enumerate(matrix) for c, char in enumerate(row)}
    
    prepared_text = prepare_plaintext(text_input)
    if mode == 'encrypt':
        digraphs = [prepared_text[i:i+2] for i in range(0, len(prepared_text), 2)]
    else:
        clean_text = "".join(filter(str.isalpha, text_input.upper().replace('J', 'I')))
        digraphs = [clean_text[i:i+2] for i in range(0, len(clean_text), 2)]
        
    result_text = ""
    shift = 1 if mode == 'encrypt' else -1
    for char1, char2 in digraphs:
        if char1 not in coords_map or char2 not in coords_map: continue
        r1, c1 = coords_map[char1]
        r2, c2 = coords_map[char2]
        if r1 == r2: result_text += matrix[r1][(c1 + shift) % 5] + matrix[r2][(c2 + shift) % 5]
        elif c1 == c2: result_text += matrix[(r1 + shift) % 5][c1] + matrix[(r2 + shift) % 5][c2]
        else: result_text += matrix[r1][c2] + matrix[r2][c1]
    return result_text, matrix, prepared_text

def caesar_process(text_input, key, mode):
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

def aes_process(text_input, key, mode):
    try:
        key_bytes = hashlib.sha256(key.encode()).digest()[:16]
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        if mode == 'encrypt':
            data_bytes = text_input.encode('utf-8')
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_bytes = cipher.encrypt(padded_data)
            return base64.b64encode(encrypted_bytes).decode('utf-8'), key_bytes, padded_data
        else:
            data_bytes = base64.b64decode(text_input)
            decrypted_bytes = cipher.decrypt(data_bytes)
            unpadded_data = unpad(decrypted_bytes, AES.block_size)
            return unpadded_data.decode('utf-8'), key_bytes, data_bytes
    except (ValueError, KeyError):
        return "DEKRIPSI GAGAL", None, None

# ==============================================================================
# BAGIAN 2: APLIKASI GUI DENGAN ANALISIS LENGKAP
# ==============================================================================

class ChainedCipherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisis Kriptografi Super Detail")
        self.geometry("1000x950")
        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e1e")
        self.setup_ui()

    def setup_ui(self):
        self.scroll_container = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        customtkinter.CTkLabel(self.scroll_container, text="Analisis Detail Cipher Klasik & Modern", font=("Inter", 32, "bold")).pack(pady=(10, 20))

        input_card = customtkinter.CTkFrame(self.scroll_container, corner_radius=15, fg_color="#2b2b2b")
        input_card.pack(fill="x", padx=10, pady=10)
        customtkinter.CTkLabel(input_card, text="Pengaturan Teks & Kunci", font=("Inter", 18, "bold")).pack(pady=(15, 10))
        self.text_entry = customtkinter.CTkEntry(input_card, placeholder_text="Masukkan Teks Anda", font=("Inter", 14), height=45, corner_radius=10)
        self.text_entry.pack(fill="x", padx=15, pady=5)
        self.playfair_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci Playfair (Frasa)", font=("Inter", 14), height=45, corner_radius=10)
        self.playfair_key_entry.pack(fill="x", padx=15, pady=5)
        self.caesar_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci Caesar (Angka)", font=("Inter", 14), height=45, corner_radius=10)
        self.caesar_key_entry.pack(fill="x", padx=15, pady=5)
        self.aes_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Kunci AES (Teks/Angka)", font=("Inter", 14), height=45, corner_radius=10)
        self.aes_key_entry.pack(fill="x", padx=15, pady=(5, 20))

        button_frame = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        customtkinter.CTkButton(button_frame, text="🔒 Enkripsi", command=lambda: self.run_process('encrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#2c7a4d", hover_color="#1f5736", corner_radius=10).pack(side="left", expand=True, padx=5)
        customtkinter.CTkButton(button_frame, text="🔓 Dekripsi", command=lambda: self.run_process('decrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#b85b21", hover_color="#8a4418", corner_radius=10).pack(side="right", expand=True, padx=5)

        self.analysis_container = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")

    def clear_analysis(self):
        self.analysis_container.pack_forget()
        for widget in self.analysis_container.winfo_children():
            widget.destroy()

    def run_process(self, mode):
        # 1. VALIDASI INPUT
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

        self.clear_analysis()
        self.analysis_container.pack(fill="x", padx=10, pady=10)

        # 2. RUN & DISPLAY ANALYSIS
        try:
            if mode == 'encrypt':
                # --- Step 1: Playfair ---
                playfair_result, matrix, prepared_text = playfair_process(input_text, playfair_key, 'encrypt')
                self.display_playfair_card('encrypt', input_text, playfair_key, matrix, prepared_text, playfair_result)
                
                # --- Step 2: Caesar ---
                caesar_result = caesar_process(playfair_result, caesar_key, 'encrypt')
                self.display_caesar_card('encrypt', playfair_result, caesar_key, caesar_result)

                # --- Step 3: AES ---
                aes_result, aes_key_bytes, padded_data = aes_process(caesar_result, aes_key, 'encrypt')
                self.display_aes_card('encrypt', caesar_result, aes_key, aes_key_bytes, padded_data, aes_result)

            else: # Decrypt
                # --- Step 1: AES ---
                aes_result, aes_key_bytes, received_bytes = aes_process(input_text, aes_key, 'decrypt')
                if "GAGAL" in aes_result: 
                    messagebox.showerror("Error Dekripsi", aes_result); return
                self.display_aes_card('decrypt', input_text, aes_key, aes_key_bytes, received_bytes, aes_result)
                
                # --- Step 2: Caesar ---
                caesar_result = caesar_process(aes_result, caesar_key, 'decrypt')
                self.display_caesar_card('decrypt', aes_result, caesar_key, caesar_result)

                # --- Step 3: Playfair ---
                playfair_result, matrix, _ = playfair_process(caesar_result, playfair_key, 'decrypt')
                self.display_playfair_card('decrypt', caesar_result, playfair_key, matrix, None, playfair_result)

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat pemrosesan: {e}")

    def create_card(self, title):
        card = customtkinter.CTkFrame(self.analysis_container, corner_radius=15, fg_color="#2b2b2b")
        card.pack(fill="x", pady=(0, 10))
        customtkinter.CTkLabel(card, text=title, font=("Inter", 20, "bold")).pack(pady=(15, 10), padx=15, anchor="w")
        return card

    def add_info_section(self, parent, title, content, content_font=("Courier New", 13)):
        customtkinter.CTkLabel(parent, text=title, font=("Inter", 14, "bold"), text_color="#52a2f2").pack(fill="x", padx=15, pady=(10,2), anchor="w")
        customtkinter.CTkLabel(parent, text=content, font=content_font, justify="left", wraplength=850).pack(fill="x", padx=15, pady=(0,5), anchor="w")

    def add_detail_frame(self, parent):
        frame = customtkinter.CTkScrollableFrame(parent, corner_radius=10, fg_color="#1e1e1e", height=150)
        frame.pack(fill="x", padx=15, pady=5)
        return frame

    def add_arrow(self):
        customtkinter.CTkLabel(self.analysis_container, text="↓", font=("Inter", 24, "bold")).pack()

    def display_playfair_card(self, mode, input_text, key_phrase, matrix, prepared_text, output_text):
        title = f"1. {mode.title()} Playfair"
        card = self.create_card(title)
        
        self.add_info_section(card, "Input:", input_text)
        
        key_clean = "".join(OrderedDict.fromkeys(filter(str.isalpha, key_phrase.upper().replace('J', 'I'))))
        matrix_str = "\n".join([f"  {' '.join(row)}" for row in matrix])
        key_analysis_content = f"Frasa '{key_phrase.upper()}' dibersihkan menjadi '{key_clean}'.\nMatriks 5x5 yang dihasilkan adalah:\n{matrix_str}"
        self.add_info_section(card, "Analisis Kunci:", key_analysis_content)

        if mode == 'encrypt':
            text_analysis_content = f"Teks asli diolah: spasi dihapus, 'J' diganti 'I', dan 'X' disisipkan\nuntuk memisahkan huruf ganda atau jika jumlahnya ganjil.\nHasil Teks Siap: {prepared_text}"
            self.add_info_section(card, "Analisis Persiapan Teks:", text_analysis_content)

        self.add_info_section(card, "Analisis Proses per Pasangan Huruf (Digraph):", "Berikut adalah detail proses untuk 5 pasangan huruf pertama:")
        detail_frame = self.add_detail_frame(card)
        
        text_to_process = prepared_text if mode == 'encrypt' else input_text
        digraphs = [text_to_process[i:i+2] for i in range(0, len(text_to_process), 2)][:5]
        
        coords_map = {char: (r, c) for r, row in enumerate(matrix) for c, char in enumerate(row)}
        shift = 1 if mode == 'encrypt' else -1

        for i, digraph in enumerate(digraphs):
            char1, char2 = digraph[0], digraph[1]
            r1, c1 = coords_map[char1]
            r2, c2 = coords_map[char2]
            
            if r1 == r2: 
                rule = "Aturan Baris Sama"
                res_c1, res_c2 = (c1 + shift) % 5, (c2 + shift) % 5
                res_char1, res_char2 = matrix[r1][res_c1], matrix[r2][res_c2]
                explanation = f"'{char1}' (baris {r1}, kol {c1}) & '{char2}' (baris {r2}, kol {c2}) → Geser ke samping → '{res_char1}' & '{res_char2}'"
            elif c1 == c2: 
                rule = "Aturan Kolom Sama"
                res_r1, res_r2 = (r1 + shift) % 5, (r2 + shift) % 5
                res_char1, res_char2 = matrix[res_r1][c1], matrix[res_r2][c2]
                explanation = f"'{char1}' (baris {r1}, kol {c1}) & '{char2}' (baris {r2}, kol {c2}) → Geser ke bawah/atas → '{res_char1}' & '{res_char2}'"
            else: 
                rule = "Aturan Persegi"
                res_char1, res_char2 = matrix[r1][c2], matrix[r2][c1]
                explanation = f"'{char1}' (baris {r1}, kol {c1}) & '{char2}' (baris {r2}, kol {c2}) → Tukar kolom → '{res_char1}' & '{res_char2}'"

            step_text = f"{i+1}. Pasangan '{digraph}': {rule}\n   ↳ {explanation}"
            customtkinter.CTkLabel(detail_frame, text=step_text, font=("Courier New", 12), justify="left").pack(anchor="w", padx=10, pady=5)

        self.add_info_section(card, "Output Playfair:", output_text)
        self.add_arrow()

    def display_caesar_card(self, mode, input_text, key, output_text):
        title = f"2. {mode.title()} Caesar"
        card = self.create_card(title)
        
        self.add_info_section(card, "Input dari Tahap Sebelumnya:", input_text)
        
        self.add_info_section(card, "Analisis Proses per Karakter:", f"Setiap karakter digeser sebanyak {key} langkah ({'maju' if mode == 'encrypt' else 'mundur'}) dalam alfabet.")
        detail_frame = self.add_detail_frame(card)

        op = "+" if mode == 'encrypt' else "-"
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        for i, char_in in enumerate(input_text):
            if char_in not in alphabet: continue
            
            char_out = output_text[i]
            pos_in = alphabet.find(char_in)
            
            calc_result = (pos_in + key) if mode == 'encrypt' else (pos_in - key)
            pos_out = calc_result % 26
            
            step_text = f"• Karakter '{char_in}' (posisi alfabet ke-{pos_in})\n  ↳ ({pos_in} {op} {key}) = {calc_result}. Lalu ({calc_result} mod 26) = {pos_out}.\n  ↳ Hasil: '{char_out}' (posisi alfabet ke-{pos_out})"
            customtkinter.CTkLabel(detail_frame, text=step_text, font=("Courier New", 12), justify="left").pack(anchor="w", padx=10, pady=8)
            if i > 10: # Limit display for very long text
                customtkinter.CTkLabel(detail_frame, text="... dan seterusnya untuk karakter lain.", font=("Courier New", 12, "italic"), justify="left").pack(anchor="w", padx=10, pady=8)
                break

        self.add_info_section(card, "Output Caesar:", output_text)
        self.add_arrow()

    def display_aes_card(self, mode, input_text, key, key_bytes, data_bytes, output_text):
        title = f"3. {mode.title()} AES-128 (ECB)"
        card = self.create_card(title)
        
        self.add_info_section(card, "Input dari Tahap Sebelumnya:", input_text, ("Courier New", 12))
        
        key_hash_explanation = f"AES-128 memerlukan kunci biner tepat 16 byte (128 bit). Kunci teks '{key}'\ntidak valid. Maka, kunci di-hash (diproses secara matematis) menggunakan\nSHA-256 untuk menghasilkan deretan byte yang aman dan unik, lalu diambil\n16 byte pertama sebagai kunci final."
        self.add_info_section(card, "Analisis Kunci (Hashing):", key_hash_explanation, ("Inter", 12, "italic"))
        self.add_info_section(card, "Kunci Biner Final (16 byte, dalam format hexadecimal):", key_bytes.hex())

        if mode == 'encrypt':
            original_len = len(input_text.encode('utf-8'))
            padded_len = len(data_bytes)
            padding_len = padded_len - original_len
            padding_explanation = f"AES mengenkripsi data dalam blok-blok 16 byte. Teks input (panjang {original_len} byte)\nperlu ditambahkan 'padding' (byte tambahan) agar panjangnya menjadi kelipatan 16.\nDalam kasus ini, ditambahkan {padding_len} byte padding."
            self.add_info_section(card, "Analisis Proses (Padding):", padding_explanation, ("Inter", 12, "italic"))
            self.add_info_section(card, "Data Setelah di-Padding (hexadecimal):", data_bytes.hex())
            
            b64_explanation = "Hasil enkripsi AES adalah data biner mentah yang tidak bisa ditampilkan sebagai teks biasa.\nOleh karena itu, data biner tersebut di-encode menggunakan Base64 menjadi format teks\nyang aman untuk ditransfer dan ditampilkan."
            self.add_info_section(card, "Analisis Output (Base64 Encoding):", b64_explanation, ("Inter", 12, "italic"))
            self.add_info_section(card, "Output Final (Ciphertext dalam Base64):", output_text, ("Courier New", 12))
        else: # decrypt
            b64_explanation = f"Teks input dalam format Base64 di-decode terlebih dahulu menjadi data biner mentah\nyang siap untuk diproses oleh AES."
            self.add_info_section(card, "Analisis Proses (Base64 Decode):", b64_explanation, ("Inter", 12, "italic"))
            self.add_info_section(card, "Data Biner yang Diterima (hexadecimal):", data_bytes.hex())

            unpad_explanation = "Setelah data biner didekripsi, proses 'unpadding' dilakukan. Sistem memeriksa\nbyte terakhir dari data untuk mengetahui berapa banyak byte padding yang harus\ndibuang untuk mengembalikan data ke bentuk aslinya."
            self.add_info_section(card, "Analisis Output (Unpadding):", unpad_explanation, ("Inter", 12, "italic"))
            self.add_info_section(card, "Output Final (Plaintext):", output_text)
        
        children = self.analysis_container.winfo_children()
        if children and isinstance(children[-1], customtkinter.CTkLabel) and children[-1].cget("text") == "↓":
            children[-1].destroy()

if __name__ == "__main__":
    app = ChainedCipherApp()
    app.mainloop()

