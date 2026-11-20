"""ISO (setores de 2048) -> faixa de dados do CD em MODE1/2352 (sync, cabeçalho MSF, EDC e ECC), como a faixa 1 do Redump.
Prova: a ISO original vira a faixa 1 com CRC32 6D0FAABA (o arquivo que o patch em inglês v1.10 exige).
Uso: python iso_para_bin.py <entrada.iso> <saida.bin>"""
import sys
import zlib

import numpy as np

SYNC = bytes([0x00] + [0xFF] * 10 + [0x00])

# tabelas do ECC (ECMA-130) e do EDC (CRC32 com polinômio 0xD8018001, refletido)
F = np.zeros(256, np.uint8)
B = np.zeros(256, np.uint8)
for i in range(256):
    j = ((i << 1) ^ (0x11D if i & 0x80 else 0)) & 0xFF
    F[i] = j
    B[i ^ j] = i
EDC = np.zeros(256, np.uint32)
for i in range(256):
    e = i
    for _ in range(8):
        e = (e >> 1) ^ (0xD8018001 if e & 1 else 0)
    EDC[i] = e


def _indices(major_count, minor_count, major_mult, minor_inc):
    size = major_count * minor_count
    idx = np.zeros((major_count, minor_count), np.int64)
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        for minor in range(minor_count):
            idx[major, minor] = index
            index += minor_inc
            if index >= size:
                index -= size
    return idx


IDX_P = _indices(86, 24, 2, 86)        # paridade P: sobre 0x00C..0x81B, grava em 0x81C (172 bytes)
IDX_Q = _indices(52, 43, 86, 88)       # paridade Q: sobre 0x00C..0x8C7 (dados + P), grava em 0x8C8 (104 bytes)


def _ecc(src, idx):
    """src: (N, tamanho) uint8 a partir do cabeçalho (0x00C). Devolve (N, 2*majors)."""
    n, majors = src.shape[0], idx.shape[0]
    a = np.zeros((n, majors), np.uint8)
    b = np.zeros((n, majors), np.uint8)
    for minor in range(idx.shape[1]):
        t = src[:, idx[:, minor]]
        a ^= t
        b ^= t
        a = F[a]
    a = B[F[a] ^ b]
    return np.concatenate([a, a ^ b], axis=1)


def setores(dados, lba0=0):
    """dados: bytes múltiplos de 2048. Devolve bytes MODE1/2352."""
    n = len(dados) // 2048
    s = np.zeros((n, 2352), np.uint8)
    s[:, 0:12] = np.frombuffer(SYNC, np.uint8)
    lba = np.arange(lba0, lba0 + n) + 150
    bcd = lambda v: ((v // 10) << 4) | (v % 10)
    s[:, 12] = bcd(lba // 4500)
    s[:, 13] = bcd((lba // 75) % 60)
    s[:, 14] = bcd(lba % 75)
    s[:, 15] = 1
    s[:, 16:2064] = np.frombuffer(dados, np.uint8).reshape(n, 2048)
    crc = np.zeros(n, np.uint32)
    for k in range(2064):                           # EDC sobre sync + cabeçalho + dados
        crc = (crc >> 8) ^ EDC[(crc ^ s[:, k]) & 0xFF]
    s[:, 2064:2068] = crc.view(np.uint8).reshape(n, 4)    # little-endian (Windows/x86)
    s[:, 0x81C:0x8C8] = _ecc(s[:, 0x0C:0x81C], IDX_P)
    s[:, 0x8C8:0x930] = _ecc(s[:, 0x0C:0x8C8], IDX_Q)
    return s.tobytes()


def converter(entrada, saida, bloco=4096):
    crc = 0
    with open(entrada, 'rb') as fi, open(saida, 'wb') as fo:
        lba = 0
        while True:
            d = fi.read(2048 * bloco)
            if not d:
                break
            assert len(d) % 2048 == 0, 'ISO com tamanho que não é múltiplo de 2048'
            r = setores(d, lba)
            fo.write(r)
            crc = zlib.crc32(r, crc)
            lba += len(d) // 2048
    return '%08X' % crc


if __name__ == '__main__':
    assert sys.byteorder == 'little'
    print(converter(sys.argv[1], sys.argv[2]))
