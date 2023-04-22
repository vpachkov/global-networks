import crc16
import crcmod
from random import randint


class HammingCode(object):
    '''
    initializes the class with a text input and the number of bits to use for Hamming encoding.
    '''
    def __init__(self, text, bits_count):
        self._text = text
        self._bits_count = bits_count
        self._encoding_dict_obj = None
        self._encoded = None
        self._checksum = None

    '''
    Creates a single-bit error in the encoded message.
    '''
    def encode_one_mistake(self):
        encoded = self.encode()
        for i in range(len(encoded)):
            idx = randint(0, len(encoded[i])-1)
            dd = list(encoded[i])
            dd[idx] = chr((ord('1') - ord(encoded[i][idx])) + ord('0'))
            encoded[i] = ''.join(dd)
        return encoded

    '''
    Creates two random errors in the encoded message.
    '''
    def encode_multiple_mistakes(self):
        encoded = self.encode()
        for i in range(len(encoded)):
            idx = randint(0, len(encoded[i])-1)
            if idx < 4:
                continue
            for j in range(2):
                idx = randint(0, len(encoded[i])-1)
                dd = list(encoded[i])
                dd[idx] = chr((ord('1') - ord(encoded[i][idx])) + ord('0'))
                encoded[i] = ''.join(dd)
        return encoded

    '''
    Encodes the message using Hamming code and returns it.
    '''
    def encode(self):
        if self._encoded:
            return self._encoded

        words = self._split()
        self._checksum = [crc16.crc16xmodem(bytes(i, 'utf-8')) for i in words]

        hamming_encoded = []
        for word in words:
            hamming_word = word
            for j in range(7):
                hamming_word = hamming_word[:2**j -
                                            1] + '0' + hamming_word[2**j-1:]
            for j in range(7):
                start = 2**j-1+1
                stop = 2*2**j-1
                line_sum = 0
                while start <= len(hamming_word):
                    arr = [int(i) for i in hamming_word[start:stop]]
                    line_sum += sum(arr)
                    start = stop+2**j
                    stop = start+2**j
                hamming_word = hamming_word[:2**j-1] + \
                    str(line_sum % 2) + hamming_word[2**j:]
            hamming_encoded.append(hamming_word)

        self._encoded = hamming_encoded
        return self._encoded

    '''
    Takes in a list of messages with potential errors and returns the corrected messages.
    '''
    def fix_mistakes(self, mistakes):
        mistakes_checker = []
        for i in range(len(mistakes)):
            mistakes_checker.append(mistakes[i])
            for j in range(7):
                start = 2**j-1+1
                stop = 2*2**j-1
                line_sum = 0
                while start <= (len(str(mistakes_checker[i]))):
                    arr = [int(k) for k in mistakes_checker[i][start:stop]]
                    line_sum += sum(arr)
                    start = stop+2**j
                    stop = start+2**j
                mistakes_checker[i] = mistakes_checker[i][:2**j-1] + \
                    str(line_sum % 2)+mistakes_checker[i][2**j:]

        numb_sent = []
        for i in range(len(mistakes_checker)):
            for j in range(len(mistakes_checker[i])):
                if (mistakes_checker[i][j] != mistakes[i][j]):
                    numb_sent.append(i)
                    break

        mistakes_checker = []
        mis = []
        for i in range(len(numb_sent)):
            mistakes_checker.append(mistakes[numb_sent[i]])
            mis.append([])
            for j in range(7):
                start = 2**j-1
                stop = 2*2**j-1
                line_sum = 0
                while start < (len(str(mistakes_checker[i]))):
                    arr = [int(k) for k in mistakes_checker[i][start:stop]]
                    line_sum += sum(arr)
                    start = stop+2**j
                    stop = start+2**j
                mis[i].append(line_sum % 2)

        mist_pos = []
        for i in range(len(mis)):
            pos = 0
            for j in reversed(range(7)):
                pos += mis[i][j]*2**j
            mist_pos.append(pos-1)

        words = mistakes.copy()
        for i in range(len(mist_pos)):
            try:
                words[numb_sent[i]] = words[numb_sent[i]][:mist_pos[i]] + \
                    str(abs(int(words[numb_sent[i]][mist_pos[i]])-1)
                        )+words[numb_sent[i]][mist_pos[i]+1:]
            except IndexError:
                continue

        return words

    '''
    Decodes the messages and compares with the original text.
    '''
    def compare(self, words):
        decoder = []
        for i in range(len(words)):
            decoder.append(words[i])
            for j in reversed(range(7)):
                decoder[i] = decoder[i][:2**j-1]+decoder[i][2**j:]

        def get_key(d, value):
            try:
                for k, v in d.items():
                    if v == value:
                        return k
            except TypeError:
                print(d[0])
                return d[0]

        full_bin = ''
        for i in range(len(decoder)):
            full_bin += decoder[i]
        final_text = ''
        for j in range(0, len(full_bin)-7, 8):
            try:
                final_text += get_key(self._encoding_dict(), full_bin[j:j+8])
            except TypeError:
                final_text += ''

        checksum = [crc16.crc16xmodem(bytes(i, 'utf-8')) for i in decoder]

        return self._checksum == checksum, self._text == final_text

    def _split(self):
        bin_text = ''
        words = []
        for char in self._text:
            bin_text += self._encoding_dict()[char]

        for i in range(0, len(bin_text), (self._bits_count-7)):
            word = bin_text[i:i+(self._bits_count-7)]
            while len(word) < (self._bits_count-7):
                word += '0'
            words.append(word)

        return words

    def _encoding_dict(self):
        if self._encoding_dict_obj:
            return self._encoding_dict_obj

        encoding_dict = {'': '00000000'}
        code = 1

        for i in range(len(self._text)):
            if self._text[i] not in encoding_dict:
                binary_code = str(bin(code)[2:])
                while len(binary_code) < 8:
                    binary_code = '0' + binary_code
                encoding_dict[self._text[i]] = binary_code
                code += 1

        self._encoding_dict_obj = encoding_dict
        return self._encoding_dict_obj


if __name__ == '__main__':
    text = '''
Архитектура ARM (от англ. Advanced RISC Machine — усовершенствованная RISC-машина; иногда — Acorn RISC Machine) — система команд и семейство описаний и готовых топологий 32-битных и 64-битных микропроцессорных/микроконтроллерных ядер, разрабатываемых компанией ARM Limited[1]. Среди лицензиатов готовых топологий ядер ARM — компании AMD, Apple, Analog Devices, Atmel, Xilinx, Cirrus Logic[en], Intel (до 27 июня 2006 года), Marvell, NXP, STMicroelectronics, Samsung, LG, MediaTek, Qualcomm, Sony, Texas Instruments, Nvidia, Freescale, Миландр, ЭЛВИС[2], HiSilicon, Байкал электроникс. Значимые семейства процессоров: ARM7, ARM9, ARM11 и Cortex[3][4]. Многие лицензиаты проектируют собственные топологии ядер на базе системы команд ARM: DEC StrongARM, Freescale i.MX, Intel XScale, NVIDIA Tegra, ST-Ericsson Nomadik[en], Krait и Kryo в Qualcomm Snapdragon, Texas Instruments OMAP, Samsung Hummingbird, LG H13, Apple A6 и HiSilicon K3. После достижения некоторых успехов с компьютером BBC Micro британская компания Acorn Computers задумалась над переходом от относительно слабых процессоров MOS Technology 6502 к более производительным решениям и выходом на рынок бизнес-компьютеров с той же платформой BBC Micro. Такие процессоры, как Motorola 68000 и 32016 от National Semiconductor, были для этого непригодны, а 6502 был недостаточно мощным, чтобы поддерживать графический пользовательский интерфейс[7].
Компании была нужна совершенно новая архитектура после того, как она протестировала все доступные ей процессоры и сочла их неэффективными. Acorn серьёзно настроился на разработку собственного процессора, и их инженеры начали изучать документацию проекта RISC, разработанного в Университете Калифорнии в Беркли. Они подумали, что раз уж группе студентов удалось создать вполне конкурентоспособный процессор, то их инженерам это будет несложно. Поездка в Western Design Center (Аризона) показала инженерам Стиву Ферберу и Софи Уилсон (на тот момент известной под именем Роджер[8]), что им не потребуются невероятные ресурсы для осуществления этого плана.
Уилсон приступила к разработке системы команд, создавая симулятор нового процессора на компьютере BBC Micro. Её успехи в этом убедили инженеров Acorn, что они на верном пути. Но все же перед тем, как идти дальше, им требовалось больше ресурсов, настало время для Уилсон идти к директору Acorn Герману Хаузеру и объяснить, в чём же дело. После того, как он дал добро, собралась небольшая команда для реализации модели Уилсон на аппаратном уровне.
    '''

    hc = HammingCode(text, 111)
    e1 = hc.fix_mistakes(hc.encode())
    e2 = hc.fix_mistakes(hc.encode_one_mistake())
    e3 = hc.fix_mistakes(hc.encode_multiple_mistakes())

    checksum_equal, text_equal = hc.compare(e1)
    print('checksum equal - ', checksum_equal)
    print('text eqaul - ', text_equal)
    print()

    checksum_equal, text_equal = hc.compare(e2)
    print('checksum equal - ', checksum_equal)
    print('text eqaul - ', text_equal)
    print()

    checksum_equal, text_equal = hc.compare(e3)
    print('checksum equal - ', checksum_equal)
    print('text eqaul - ', text_equal)
    print()
