import zlib

class Encoder:
    TYPES = {
        1: "GET",
        2: "DATA",
        3: "INFO",
        4: "END",
        5: "ERR",
        6: "RET"
    }

    BYTES_SIZE = {
        "id": 2,
        "type": 2,
        "len": 4,
        "crc32": 4,
        "header": 16,
        "msg": 1024,
        "payload": 1012,
    }

    # checksum entre 0 e 2^32 - 1
    CRC_32 = lambda data: zlib.crc32(data) & 0xffffffff

    # Encode binário big endian
    BIN_ENC = lambda d, s: d.to_bytes(Encoder.BYTES_SIZE[s], 'big')

    # Decode binário big endian
    BIN_DEC = lambda d: int.from_bytes(d, 'big')

    @staticmethod
    def encode(id, header, data = ""):
        messages = {"END": "", "ERR": "Not found"}

        data = messages[header].encode("utf-8") if header in messages.keys() else data

        type = [h_id for h_id, h in Encoder.TYPES.items() if h == header][0]

        bytes = Encoder.BIN_ENC(type,"type") + Encoder.BIN_ENC(id, "id")
        bytes += Encoder.BIN_ENC(len(data), "len") + Encoder.BIN_ENC(Encoder.CRC_32(data), "crc32") + data

        return bytes

    @staticmethod
    def decode(data):
        len = Encoder.BIN_DEC(data[4:8])
        return {
            "id": Encoder.BIN_DEC(data[2:4]),
            "data": data[12:12+len],
            "type": Encoder.TYPES[Encoder.BIN_DEC(data[0:2])],
            "len": Encoder.BIN_DEC(data[4:8]),
            "crc32": Encoder.BIN_DEC(data[8:12])
        }