import customtkinter
import base64
from tkinter import messagebox

# Import library kriptografi
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# --- KELAS UNTUK LOGIKA KRIPTOGRAFI (TIDAK BERUBAH) ---
class CryptoEngine:
    """Menangani logika enkripsi dan dekripsi AES-256."""
    def aes_encrypt(self, data: bytes, key: bytes) -> bytes:
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = iv + cipher.encrypt(pad(data, AES.block_size))
        return base64.b64encode(encrypted_data)

    def aes_decrypt(self, b64_encrypted_data: bytes, key: bytes) -> bytes:
        decoded_data = base64.b64decode(b64_encrypted_data)
        iv = decoded_data[:AES.block_size]
        encrypted_data = decoded_data[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_data), AES.block_size)

# --- KELAS ANTARMUKA PENGGUNA (GUI) ---
class App(customtkinter.CTk):
    """Kelas utama untuk membangun antarmuka aplikasi."""
    def __init__(self):
        super().__init__()
        
        # --- Konfigurasi Jendela Utama ---
        self.title("Enkripsi & Dekripsi Kelompok 4")
        self.geometry("600x600")
        customtkinter.set_appearance_mode("Light")
        self.configure(fg_color="#f3f4f6")

        self.crypto_engine = CryptoEngine()

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        title_label = customtkinter.CTkLabel(
            main_frame, 
            text="Enkripsi & Dekripsi Kelompok 4", 
            font=("Inter", 26, "bold"), 
            text_color="#1f2937"
        )
        title_label.pack(pady=(0, 25))
        
        self.aes_key_entry = customtkinter.CTkEntry(
            main_frame, 
            placeholder_text="tiga dua",
            font=("Inter", 14),
            height=40,
            border_width=2,
            border_color="#e5e7eb",
            fg_color="white",
            corner_radius=10
        )
        self.aes_key_entry.pack(fill="x", pady=10)

        self.input_text = customtkinter.CTkTextbox(
            main_frame, 
            height=150, 
            font=("Inter", 14),
            border_width=2,
            border_color="#e5e7eb",
            fg_color="white",
            corner_radius=10
        )
        self.input_text.pack(fill="both", expand=True, pady=10)
        self.input_text.insert("0.0", "Masukkan teks di sini...")

        # --- PERBAIKAN 1: Gunakan lambda untuk mengirim widget yang benar ---
        self.aes_key_entry.bind("<FocusIn>", lambda event: self.on_focus_in(self.aes_key_entry))
        self.aes_key_entry.bind("<FocusOut>", lambda event: self.on_focus_out(self.aes_key_entry))
        self.input_text.bind("<FocusIn>", lambda event: self.on_focus_in(self.input_text))
        self.input_text.bind("<FocusOut>", lambda event: self.on_focus_out(self.input_text))

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        self.encrypt_button = customtkinter.CTkButton(
            button_frame, 
            text="Enkripsi", 
            command=self.process_encrypt,
            font=("Inter", 14, "bold"),
            height=45,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            corner_radius=10
        )
        self.encrypt_button.pack(side="left", expand=True, padx=5)

        self.decrypt_button = customtkinter.CTkButton(
            button_frame, 
            text="Dekripsi", 
            command=self.process_decrypt,
            font=("Inter", 14, "bold"),
            height=45,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            corner_radius=10
        )
        self.decrypt_button.pack(side="right", expand=True, padx=5)
        
        self.output_text = customtkinter.CTkTextbox(
            main_frame, 
            height=150, 
            font=("Inter", 14), 
            state="disabled",
            border_width=0,
            fg_color="#e5e7eb",
            corner_radius=10
        )
        self.output_text.pack(fill="both", expand=True, pady=10)

    # --- PERBAIKAN 2: Ubah parameter fungsi dari 'event' menjadi 'widget' ---
    def on_focus_in(self, widget):
        """Ubah warna border menjadi biru saat widget mendapatkan fokus."""
        widget.configure(border_color="#4f46e5")

    def on_focus_out(self, widget):
        """Kembalikan warna border ke default saat widget kehilangan fokus."""
        widget.configure(border_color="#e5e7eb")

    def show_error(self, message):
        """Menampilkan pesan error."""
        messagebox.showerror("Error", message)
            
    def set_output_text(self, text):
        """Menampilkan teks pada kotak output."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def process_encrypt(self):
        """Memproses enkripsi teks."""
        plaintext = self.input_text.get("1.0", "end-1c").strip()
        if not plaintext or plaintext == "Masukkan teks di sini...":
            self.show_error("Input kosong. Silakan masukkan teks.")
            return

        key = self.aes_key_entry.get()
        if len(key) != 32:
            self.show_error("Kunci AES harus tepat 32 karakter.")
            return

        try:
            result = self.crypto_engine.aes_encrypt(plaintext.encode('utf-8'), key.encode('utf-8'))
            self.set_output_text(result.decode('utf-8'))
        except Exception as e:
            self.show_error(f"Terjadi kesalahan saat enkripsi: {e}")

    def process_decrypt(self):
        """Memproses dekripsi teks."""
        encrypted_text = self.input_text.get("1.0", "end-1c").strip()
        if not encrypted_text:
            self.show_error("Input kosong. Silakan masukkan teks terenkripsi.")
            return

        key = self.aes_key_entry.get()
        if len(key) != 32:
            self.show_error("Kunci AES harus tepat 32 karakter.")
            return
            
        try:
            result = self.crypto_engine.aes_decrypt(encrypted_text.encode('utf-8'), key.encode('utf-8'))
            self.set_output_text(result.decode('utf-8'))
        except Exception as e:
            self.show_error(f"Gagal mendekripsi.\nPastikan input dan kunci sudah benar.\n\nDetail: {e}")

# --- Titik masuk utama program ---
if __name__ == "__main__":
    app = App()
    app.mainloop()

