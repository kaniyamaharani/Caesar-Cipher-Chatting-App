def caesar_enc(text, key):
    result = ""
    for i in range(len(text)):
        # dividing each character in the message
        char = text[i]
        result += chr((ord(char) + key - 32) % 95 + 32)
    return result


def caesar_dec(text, key):
    key = 95 - key
    result = ""
    for i in range(len(text)):
        char = text[i]
        result += chr((ord(char) + key - 32) % 95 + 32)
    return result
