from flask import Flask, render_template, jsonify
import subprocess
import sys

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Rute untuk halaman utama. Ini yang akan menampilkan file HTML Anda.
@app.route('/')
def halaman_utama():
    return render_template('index.html')

# Rute yang akan dipanggil oleh Tombol 1 di HTML
@app.route('/jalankan_aplikasi_aes')
def jalankan_aplikasi_aes():
    try:
        # Perintah ini membuka jendela aplikasi desktop Anda
        subprocess.Popen([sys.executable, 'aplikasi_kripto_aes.py'])
        # Mengirim pesan kembali ke browser bahwa perintah berhasil
        return jsonify(status='sukses', message='Aplikasi AES sedang dibuka...')
    except Exception as e:
        return jsonify(status='error', message=str(e))

# Rute untuk Tombol 2 (kosongan)
@app.route('/jalankan_fitur_2')
def jalankan_fitur_2():
    return jsonify(status='info', message='Fitur 2 belum diimplementasikan.')

# Rute untuk Tombol 3 (kosongan)
@app.route('/jalankan_fitur_3')
def jalankan_fitur_3():
    return jsonify(status='info', message='Fitur 3 belum diimplementasikan.')


# Bagian untuk menjalankan server saat file app.py dieksekusi
if __name__ == '__main__':
    app.run(debug=True)

