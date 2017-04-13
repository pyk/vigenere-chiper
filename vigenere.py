# Menyimpan huruf dan mod 26-nya
huruf_ke_angka = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 
    'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,
    'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24,
    'z': 25
}
angka_ke_huruf = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 
    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

# Implementasi fungsi enkripsi Vigenere cipher dengan plain teks P
# dan kunci K
def enkripsi(P='', K=''):
    # Menghilangkan huruf spasi
    P = P.replace(' ', '').lower()

    # Memasangkan huruf kunci dan plain teksnya
    # Jika panjang P lebih besar dari panjang K maka K akan diulang
    # secara periodik.
    # Untuk setiap pasagan plain teks dan kuncinya, kita lakukan enkripsi
    # menggunakan rumus: Ek(P) = (P1+k1, P2+k2, .. , PN+km)
    cipher_teks = []
    if len(P) > len(K):
        ik = 0
        for huruf in P:
            # Kita ulang secara periodik
            kunci = ''
            if ik < len(K):
                kunci = K[ik]
            else:
                ik = 0
                kunci = K[ik]

            # Ci = Pi+Kj
            hasil_cipher = ((huruf_ke_angka[huruf] 
                            + huruf_ke_angka[kunci]) % 26)
            huruf_cipher = angka_ke_huruf[hasil_cipher]
            cipher_teks.append(huruf_cipher)
            ik += 1
    else:
        # Tidak perlu diulang secara periodik
        ik = 0
        for huruf in P:
            kunci = K[ik]
            # Pi+Kj
            hasil_cipher = ((huruf_ke_angka[huruf] 
                            + huruf_ke_angka[kunci]) % 26)
            huruf_cipher = angka_ke_huruf[hasil_cipher]
            cipher_teks.append(huruf_cipher)
            ik += 1

    cipher_teks = ''.join(cipher_teks).upper()
    return cipher_teks

# Implementasi fungsi dekripsi Vigenere cipher dengan cipher teks C
# dan kunci K
def dekripsi(C='', K=''):
    # Transformasi cipher teks ke huruf kecil
    C = C.lower()

    # Memasangkan huruf kunci dan cipher teksnya
    # Jika panjang C lebih besar dari panjang K maka K akan diulang
    # secara periodik.
    # Untuk setiap pasagan plain teks dan kuncinya, kita lakukan dekripsi
    # menggunakan rumus: Dk(C) = (C1+k1, C2+k2, .. , CN+km)
    plain_teks = []
    if len(C) > len(K):
        ik = 0
        for huruf in C:
            # Kita ulang secara periodik
            kunci = ''
            if ik < len(K):
                kunci = K[ik]
            else:
                ik = 0
                kunci = K[ik]

            # Pi = Ci-Kj
            hasil_plain = ((huruf_ke_angka[huruf] 
                            - huruf_ke_angka[kunci]) % 26)
            huruf_plain = angka_ke_huruf[hasil_plain]
            plain_teks.append(huruf_plain)
            ik += 1
    else:
        # Tidak perlu diulang secara periodik
        ik = 0
        for huruf in C:
            kunci = K[ik]
            # Ci-Kj
            hasil_plain = ((huruf_ke_angka[huruf] 
                            - huruf_ke_angka[kunci]) % 26)
            huruf_plain = angka_ke_huruf[hasil_plain]
            plain_teks.append(huruf_plain)
            ik += 1

    plain_teks = ''.join(plain_teks)
    return plain_teks

