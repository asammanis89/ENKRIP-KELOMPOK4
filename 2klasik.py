import customtkinter
from tkinter import messagebox
from collections import OrderedDict
import time

# ==============================================================================
# BAGIAN 1: LOGIKA INTI PLAYFAIR CIPHER
# ==============================================================================

def generate_key_matrix(key_phrase):
    """Membuat matriks Playfair 5x5."""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key_clean = "".join(OrderedDict.fromkeys(filter(str.isalpha, key_phrase.upper().replace('J', 'I'))))
    matrix_string = key_clean + "".join([c for c in alphabet if c not in key_clean])
    return [list(matrix_string[i:i+5]) for i in range(0, 25, 5)]

def prepare_plaintext(plaintext):
    """Menyiapkan plaintext menjadi daftar pasangan huruf (digraphs) dengan logika yang benar."""
    # Mengolah teks: membuang spasi, memisahkan huruf kembar dengan 'X',
    # dan memastikan jumlah huruf genap untuk dipasangkan.
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
    """Fungsi utama untuk enkripsi/dekripsi Playfair."""
    matrix = generate_key_matrix(key_phrase)
    coords_map = {char: (r, c) for r, row in enumerate(matrix) for c, char in enumerate(row)}
    if mode == 'encrypt':
        digraphs = prepare_plaintext(text_input)
    else:
        clean_text = "".join(filter(str.isalpha, text_input.upper().replace('J', 'I')))
        digraphs = [clean_text[i:i+2] for i in range(0, len(clean_text), 2)]
    result_text = ""
    shift = 1 if mode == 'encrypt' else -1

    # Iterasi setiap pasangan huruf untuk dienkripsi/dekripsi berdasarkan 3 aturan utama.
    for char1, char2 in digraphs:
        if char1 not in coords_map or char2 not in coords_map:
            continue
            
        r1, c1 = coords_map[char1]
        r2, c2 = coords_map[char2]
        
        # Aturan 1: Jika huruf berada di baris yang sama (pola horizontal).
        if r1 == r2:
            # Geser setiap huruf ke kanan (atau ke kiri untuk dekripsi).
            result_text += matrix[r1][(c1 + shift) % 5] + matrix[r2][(c2 + shift) % 5]
        
        # Aturan 2: Jika huruf berada di kolom yang sama (pola vertikal).
        elif c1 == c2:
            # Geser setiap huruf ke bawah (atau ke atas untuk dekripsi).
            result_text += matrix[(r1 + shift) % 5][c1] + matrix[(r2 + shift) % 5][c2]
        
        # Aturan 3: Jika huruf membentuk persegi/kotak (pola diagonal).
        else:
            # Tukar huruf dengan sudut lain pada baris yang sama.
            result_text += matrix[r1][c2] + matrix[r2][c1]
            
    return result_text, matrix

# ==============================================================================
# BAGIAN 2: APLIKASI GUI DENGAN TAMPILAN BARU
# ==============================================================================

class ChainedCipherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Konfigurasi Jendela Utama ---
        self.title("Kriptografi Playfair & Caesar")
        self.geometry("800x800")
        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e1e")

        # --- Wadah Scroll Utama ---
        self.scroll_container = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Judul Aplikasi ---
        title_label = customtkinter.CTkLabel(self.scroll_container, text="Playfair & Caesar Chained Cipher", font=("Inter", 32, "bold"))
        title_label.pack(pady=(10, 20))

        # --- Kartu Input ---
        input_card = customtkinter.CTkFrame(self.scroll_container, corner_radius=15, fg_color="#2b2b2b")
        input_card.pack(fill="x", padx=10, pady=10)
        
        input_title = customtkinter.CTkLabel(input_card, text="Pengaturan Teks & Kunci", font=("Inter", 18, "bold"))
        input_title.pack(pady=(15, 10))

        self.text_entry = customtkinter.CTkEntry(input_card, placeholder_text="Masukkan Teks Anda", font=("Inter", 14), height=45, corner_radius=10)
        self.text_entry.pack(fill="x", padx=15, pady=5)
        self.playfair_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Masukkan Kunci Playfair (Frasa)", font=("Inter", 14), height=45, corner_radius=10)
        self.playfair_key_entry.pack(fill="x", padx=15, pady=5)
        self.caesar_key_entry = customtkinter.CTkEntry(input_card, placeholder_text="Masukkan Kunci Caesar (Angka)", font=("Inter", 14), height=45, corner_radius=10)
        self.caesar_key_entry.pack(fill="x", padx=15, pady=(5, 20))

        # --- Tombol Aksi ---
        button_frame = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=5)
        encrypt_button = customtkinter.CTkButton(button_frame, text="🔒 Enkripsi", command=lambda: self.process_chained_cipher('encrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#2c7a4d", hover_color="#1f5736", corner_radius=10)
        encrypt_button.pack(side="left", expand=True, padx=5)
        decrypt_button = customtkinter.CTkButton(button_frame, text="🔓 Dekripsi", command=lambda: self.process_chained_cipher('decrypt'), font=("Inter", 16, "bold"), height=50, fg_color="#b85b21", hover_color="#8a4418", corner_radius=10)
        decrypt_button.pack(side="right", expand=True, padx=5)

        # --- Kartu Hasil Akhir ---
        result_card = customtkinter.CTkFrame(self.scroll_container, corner_radius=15, fg_color="#2b2b2b")
        result_card.pack(fill="x", padx=10, pady=10)

        result_header_frame = customtkinter.CTkFrame(result_card, fg_color="transparent")
        result_header_frame.pack(fill="x", padx=15, pady=(15, 10))
        result_title = customtkinter.CTkLabel(result_header_frame, text="Hasil Akhir", font=("Inter", 18, "bold"))
        result_title.pack(side="left")
        
        self.copy_button = customtkinter.CTkButton(result_header_frame, text="📋 Salin", width=100, command=self.copy_to_clipboard, font=("Inter", 12))
        self.copy_button.pack(side="right")
        
        self.result_label = customtkinter.CTkLabel(result_card, text="", font=("Inter", 18, "bold"), wraplength=650, justify="left", fg_color="#1e1e1e", corner_radius=10, height=60)
        self.result_label.pack(fill="x", padx=15, pady=(0, 15))
        
        # --- Kartu Analisis (Awalnya Tersembunyi) ---
        self.analysis_frame = customtkinter.CTkFrame(self.scroll_container, corner_radius=15, fg_color="#2b2b2b")
        # jangan di .pack() dulu, akan ditampilkan saat ada hasil

        # Widget internal analisis (parent-nya self.analysis_frame)
        self.matrix_label = customtkinter.CTkLabel(self.analysis_frame, text="Matriks Kunci Playfair 5x5:", font=("Inter", 16, "bold"))
        self.matrix_display = customtkinter.CTkLabel(self.analysis_frame, text="", font=("Courier New", 18), justify="left")
        
        # PENAMBAHAN: Label untuk penjelasan inti Playfair
        self.playfair_explanation_label = customtkinter.CTkLabel(self.analysis_frame, text="", font=("Inter", 12, "italic"), wraplength=600, justify="left")
        
        self.intermediate_label = customtkinter.CTkLabel(self.analysis_frame, text="Hasil Antara:", font=("Inter", 16, "bold"))
        self.intermediate_result = customtkinter.CTkLabel(self.analysis_frame, text="", font=("Inter", 14), wraplength=600, justify="left")
        self.caesar_analysis_label = customtkinter.CTkLabel(self.analysis_frame, text="Perhitungan Caesar:", font=("Inter", 16, "bold"))
        self.caesar_analysis_frame = customtkinter.CTkScrollableFrame(self.analysis_frame, height=220, fg_color="#1e1e1e", corner_radius=10)

    def copy_to_clipboard(self):
        """Menyalin teks dari label hasil ke clipboard."""
        text_to_copy = self.result_label.cget("text")
        if text_to_copy:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            original_text = self.copy_button.cget("text")
            self.copy_button.configure(text="✔ Tersalin!")
            self.after(2000, lambda: self.copy_button.configure(text=original_text))

    def process_chained_cipher(self, mode):
        input_text = self.text_entry.get()
        playfair_key = self.playfair_key_entry.get().strip()
        caesar_key_str = self.caesar_key_entry.get().strip()
        if not all([input_text, playfair_key, caesar_key_str]):
            messagebox.showerror("Error", "Semua field harus diisi.")
            return
        if not caesar_key_str.isdigit():
            messagebox.showerror("Error", "Kunci Caesar harus berupa angka.")
            return

        self.clear_analysis()
        ALPHABET_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ALPHABET_LOWER = 'abcdefghijklmnopqrstuvwxyz'
        shift_key = int(caesar_key_str) % 26
        intermediate_text, final_result, matrix, intermediate_title = "", "", [], ""

        if mode == 'encrypt':
            intermediate_title = "Hasil Enkripsi Playfair:"
            intermediate_text, matrix = playfair_process(input_text, playfair_key, 'encrypt')
            text_for_caesar = intermediate_text
            for i, char in enumerate(text_for_caesar):
                if char in ALPHABET_UPPER:
                    pos = ALPHABET_UPPER.find(char)
                    new_pos = (pos + shift_key) % 26
                    new_char = ALPHABET_UPPER[new_pos]
                    if i < 5: self.add_analysis_step_caesar(char, pos, shift_key, new_pos, new_char, 'encrypt')
                    final_result += new_char
                else:
                    if i < 5: self.add_analysis_step_non_alpha(char)
                    final_result += char
        else:
            intermediate_title = "Hasil Dekripsi Caesar (Input Playfair):"
            text_for_caesar = input_text
            for i, char in enumerate(text_for_caesar):
                if char in ALPHABET_UPPER:
                    pos = ALPHABET_UPPER.find(char)
                    new_pos = (pos - shift_key) % 26
                    new_char = ALPHABET_UPPER[new_pos]
                    if i < 5: self.add_analysis_step_caesar(char, pos, shift_key, new_pos, new_char, 'decrypt')
                    intermediate_text += new_char
                elif char in ALPHABET_LOWER:
                    pos = ALPHABET_LOWER.find(char)
                    new_pos = (pos - shift_key) % 26
                    new_char = ALPHABET_LOWER[new_pos]
                    if i < 5: self.add_analysis_step_caesar(char, pos, shift_key, new_pos, new_char, 'decrypt')
                    intermediate_text += new_char
                else:
                    if i < 5: self.add_analysis_step_non_alpha(char)
                    intermediate_text += char
            final_result, matrix = playfair_process(intermediate_text, playfair_key, 'decrypt')

        self.display_analysis(matrix, intermediate_text, intermediate_title)
        self.result_label.configure(text=final_result)

    def display_analysis(self, matrix, intermediate_text, intermediate_title):
        self.analysis_frame.pack(fill="x", padx=10, pady=10) # Tampilkan kartu analisis
        
        self.matrix_label.pack(padx=15, pady=(15, 5), anchor="w")
        self.matrix_display.configure(text="\n".join(["   ".join(row) for row in matrix]))
        self.matrix_display.pack(padx=15, pady=(0, 10), anchor="w")

        # PENAMBAHAN: Atur teks penjelasan dan tampilkan
        explanation_text = (
            "Inti Aturan Playfair:\n"
            "∙ Sama Baris → Geser huruf ke kanan.\n"
            "∙ Sama Kolom → Geser huruf ke bawah.\n"
            "∙ Membentuk Persegi → Tukar dengan sudut di baris yang sama."
        )
        self.playfair_explanation_label.configure(text=explanation_text)
        self.playfair_explanation_label.pack(padx=15, pady=(5, 15), anchor="w")

        self.intermediate_label.configure(text=intermediate_title)
        self.intermediate_label.pack(padx=15, pady=(10, 5), anchor="w")
        self.intermediate_result.pack(padx=15, pady=(0, 10), anchor="w")
        self.intermediate_result.configure(text=intermediate_text)

        self.caesar_analysis_label.pack(padx=15, pady=(10, 5), anchor="w")
        self.caesar_analysis_frame.pack(fill="x", expand=True, padx=15, pady=(0, 15))

    def add_analysis_step_caesar(self, char, pos, shift, new_pos, new_char, mode):
        """Menambahkan langkah analisis Caesar dengan format yang lebih detail."""
        op = "+" if mode == 'encrypt' else "-"
        
        # Hitung hasil penjumlahan/pengurangan awal
        initial_result = pos + shift if mode == 'encrypt' else pos - shift
        
        # Format teks baru yang lebih deskriptif
        calculation_text = (
            f"Karakter '{char}' (posisi {pos})\n"
            f"  ↳ ({pos} {op} {shift}) mod 26 = {initial_result} mod 26\n"
            f"  ↳ Hasil akhir: '{new_char}' (posisi {new_pos})"
        )
        
        # Buat label baru untuk setiap langkah
        step_label = customtkinter.CTkLabel(
            self.caesar_analysis_frame, 
            text=calculation_text, 
            font=("Courier New", 14),
            justify="left"
        )
        step_label.pack(anchor="w", padx=10, pady=5) 
        
    def add_analysis_step_non_alpha(self, char):
        text = f"Karakter '{char}' bukan huruf, dilewati."
        customtkinter.CTkLabel(self.caesar_analysis_frame, text=text, font=("Inter", 13, "italic")).pack(anchor="w", padx=10)
        
    def clear_analysis(self):
        for widget in self.caesar_analysis_frame.winfo_children():
            widget.destroy()
        self.analysis_frame.pack_forget() # Sembunyikan kartu analisis

if __name__ == "__main__":
    app = ChainedCipherApp()
    app.mainloop()

