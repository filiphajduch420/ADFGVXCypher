"""
Filip Hajduch
ADFG(V)X cypher
"""

from PyQt6 import QtCore, QtGui, QtWidgets
import random
import math
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
numbers = "0123456789"
diacritics = ["Ě", "Š", "Č", "Ř", "Ž", "Ý", "Á", "Í", "É", "Ů", "Ú", "Ť", "Ď", "Ó", "Ň"]
without_diacritics = ["E", "S", "C", "R", "Z", "Y", "A", "I", "E", "U", "U", "T", "D", "O", "N"]


# nahrazení čísel
def replaceNumbers(text):
    number_table = {
        '0': 'QABQ',
        '1': 'QBAQ',
        '2': 'QABY',
        '3': 'YABQ',
        '4': 'YABY',
        '5': 'YBAY',
        '6': 'XABY',
        '7': 'XABX',
        '8': 'YABX',
        '9': 'XBAX'
    }
    replaced_text = ""

    for char in text:
        if char.isdigit():
            replaced_text += number_table[char]
        else:
            replaced_text += char

    return replaced_text


# nahrazení 4znaků za čísla pro dešifrování
def replaceNumbersDecrypt(text):
    number_table = {
        'QABQ': '0',
        'QBAQ': '1',
        'QABY': '2',
        'YABQ': '3',
        'YABY': '4',
        'YBAY': '5',
        'XABY': '6',
        'XABX': '7',
        'YABX': '8',
        'XBAX': '9'
    }
    replaced_text = ""

    i = 0
    while i < len(text):
        substring = text[i:i + 4]
        if substring in number_table:
            replaced_text += number_table[substring]
            i += 4
        else:
            replaced_text += text[i]
            i += 1

    return replaced_text


# filtrace otevřeného textu
def filtrationOpenText(text, adfgx=True, czechEncoding=True):
    text = text.upper().replace(" ", "XMEZERAX")
    result = ""
    if adfgx:
        text = replaceNumbers(text)
        if czechEncoding:
            text = text.replace("W", "V")
        else:
            text = text.replace("J", "I")

    for char in text:
        if char in diacritics:
            index = diacritics.index(char)
            result += without_diacritics[index]
        elif char in alphabet:
            result += char
        elif char in numbers:
            result += char

    return result


def filtrationKey(key):
    key = key.upper().replace(" ", "")
    result = ""

    char_count = {}  # Slovník pro sledování opakujících se písmen
    for char in key:
        if char in diacritics:
            index = diacritics.index(char)
            result += without_diacritics[index]
        elif char in alphabet or numbers:
            result += char

    resultNew = ""

    for char in result:
        if char.isalpha():
            if char in char_count:
                char_count[char] += 1
                if char_count[char] == 1:
                    resultNew += char  # Keep the first occurrence
            else:
                char_count[char] = 1
                resultNew += char
        else:
            resultNew += char

    return resultNew


def createMatrix(adfgx=True, czechEncoding=True):
    ADFGXalphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ADFGVXalphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    if adfgx:
        if czechEncoding:
            alphabet = ADFGXalphabet.replace("W", "V")
        else:
            alphabet = ADFGXalphabet.replace("J", "I")
    else:
        alphabet = ADFGVXalphabet

    # Vytvoření unikátního seznamu písmen pro matici (bez opakování písmen)
    unique_alphabet = ''.join(dict.fromkeys(alphabet))

    if adfgx:
        index = "ADFGX"
    else:
        index = "ADFGVX"

    # Vytvoření matice jako pandas DataFrame
    matrix = pd.DataFrame('', index=list(index), columns=list(index))

    # Plnění matice náhodnými písmeny
    available_letters = list(unique_alphabet)
    for i in index:
        for j in index:
            if available_letters:
                letter = random.choice(available_letters)
                matrix.at[i, j] = letter
                available_letters.remove(letter)

    return matrix


def replaceChars(text, matrix, adfgx=True, czechEncoding=True):
    if adfgx:
        if czechEncoding:
            text = filtrationOpenText(text, True, True)
        else:
            text = filtrationOpenText(text, True, False)

    else:
        text = filtrationOpenText(text, False)

    replaced_text = ""
    for char in text:
        for row in matrix.index:
            if char in matrix.loc[row].values:
                col = matrix.loc[row][matrix.loc[row] == char].index[0]
                replaced_text += row + col

    saveMatrixToFile(matrix, "matice.txt")

    return replaced_text


def saveMatrixToFile(matrix, filename):
    try:
        with open(filename, 'w') as file:
            for row_index, row in matrix.iterrows():
                row_values = [str(cell) for cell in row]
                row_str = ' '.join(row_values)
                file.write(row_str + '\n')
        print(f"Matrix saved to {filename}")
    except Exception as e:
        print(f"Error: {e}")


def openMatrixFromFile(filename, adfgx=True):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            matrix_data = [line.strip().split() for line in lines]
            num_rows = len(matrix_data)
            num_columns = len(matrix_data[0])
            index = "ADFGX" if adfgx else "ADFGVX"

            matrix = pd.DataFrame(matrix_data, index=list(index[:num_rows]), columns=list(index[:num_columns]))

        return matrix
    except Exception as e:
        print(f"Error: {e}")
        return None


def createKeyMatrix(key, text):
    key = filtrationKey(key)
    sorted_key = sorted(key)

    # Vytvoreni rozmeru matice
    num_columns = len(key)
    num_rows = math.ceil(len(text) / num_columns)

    # Vytvoreni prazdne matice
    matrix = pd.DataFrame('', index=range(num_rows), columns=list(key))

    # Naplneni matice textem
    for i in range(len(text)):
        row = (i // num_columns)
        col = i % num_columns
        matrix.iloc[row, col] = text[i]

    # Zmena poradi sloupcu podle sorted_key
    matrix = matrix[sorted_key]

    return matrix


# Vypisovani textu z matice  po sloupcich
def getTextFromMatrixColumns(matrix):
    result = ""
    for j in range(len(matrix.columns)):
        for i in range(len(matrix)):
            if matrix.iloc[i, j] == '':
                result += '_'
            else:
                result += matrix.iloc[i, j]
    return result


# Šifrování
def encryptADFGVX(text, key, matrix, keyMatrix, adfgx=True, czechEncoding=True):
    if adfgx:
        if czechEncoding:
            filtered_key = filtrationKey(key)
            replaced_text = replaceChars(text, matrix, True, True)
        else:
            filtered_key = filtrationKey(key)
            replaced_text = replaceChars(text, matrix, True, False)

    else:
        replaced_text = replaceChars(text, matrix, False, False)
        filtered_key = filtrationKey(key)

    encryptedText = getTextFromMatrixColumns(keyMatrix)

    return encryptedText


# Funkce  pro vypsání textu z matice
def extractTextFromMatrix(matrix):
    text = ""
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            if matrix.iloc[i, j] == ' ':
                text += ''
            else:
                text += matrix.iloc[i, j]
    return text


def decryptMatrixOne(key, encryptedText):
    key = filtrationKey(key)
    sorted_key = sorted(key)

    num_columns = len(key)
    num_rows = math.ceil(len(encryptedText) / num_columns)

    # Vytvoření prázdné matice. Řádky jsou očíslovány, Sloupce jsou tvořeny ze seřazeného klíče
    matrix = pd.DataFrame('', index=range(num_rows), columns=list(sorted_key))

    index = 0
    for j in range(num_columns):
        for k in range(num_rows):
            if index < len(encryptedText):
                if encryptedText[index] == '_':
                    matrix.iloc[k, j] = ' '
                else:
                    matrix.iloc[k, j] = encryptedText[index]
                index += 1

    return matrix


def decryptADFGVX(key, encryptedText, loadedMatrix, adfgx=True):
    key = filtrationKey(key)
    sorted_key = sorted(key)

    if loadedMatrix is None:
        return "Matrix could not be loaded."

    num_columns = len(key)
    num_rows = math.ceil(len(encryptedText) / num_columns)

    # Vytvoření prázdné matice. Řádky jsou očíslovány, Sloupce jsou tvořeny ze seřazeného klíče
    matrix = pd.DataFrame('', index=range(num_rows), columns=list(sorted_key))

    index = 0
    for j in range(num_columns):
        for k in range(num_rows):
            if index < len(encryptedText):
                if encryptedText[index] == '_':
                    matrix.iloc[k, j] = ' '
                else:
                    matrix.iloc[k, j] = encryptedText[index]
                index += 1

    # Nastavení sloupců matice do původního pořadí klíče a následné vypsání textu z matice
    reordered_matrix = reorderMatrix(matrix, key)
    text_from_matrix = extractTextFromMatrix(reordered_matrix)

    decrypted_text = ""
    # Rozdělení textu do dvojic
    char_pairs = [text_from_matrix[i:i + 2] for i in range(0, len(text_from_matrix), 2)]

    # Hledání písmena z nahodně vytvořené matice pomocí dvojice znaků.
    for char_pair in char_pairs:
        if char_pair != ' ':
            row = char_pair[0]
            col = char_pair[1]
            decrypted_char = loadedMatrix.loc[row, col]
            decrypted_text += decrypted_char
        else:
            decrypted_text += ' '

    decrypted_text = decrypted_text.replace("XMEZERAX", " ")

    # Nahrazení 4 znaků zpět na čísla u ADFGX šifry
    if adfgx:
        decrypted_text = replaceNumbersDecrypt(decrypted_text)

    return decrypted_text


# Předělání matice do původního znění klíče
# Funkce využita v dešifrování
def reorderMatrix(matrix, key):
    columns = list(matrix.columns)
    reorderColumns = [columns.index(char) for char in key]
    reorder_matrix = matrix.iloc[:, reorderColumns]

    return reorder_matrix


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(900, 750)
        self.widget = QtWidgets.QWidget(parent=Form)
        self.widget.setGeometry(QtCore.QRect(0, 0, 1000, 900))
        self.widget.setStyleSheet(
            "QWidget#widget{background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(144, 222, 194, 255), stop:1 rgba(223, 255, 139, 255));}")
        self.widget.setObjectName("widget")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.widget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 70, 900, 750))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setItalic(False)
        font.setStrikeOut(False)
        self.tabWidget.setFont(font)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_2 = QtWidgets.QLabel(parent=self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(0, 10, 900, 31))
        self.label_2.setStyleSheet("font: 500 30pt \"Arial\";")
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.text_sifrovani = QtWidgets.QTextEdit(parent=self.tab_2)
        self.text_sifrovani.setGeometry(QtCore.QRect(40, 30, 311, 81))
        self.text_sifrovani.setStyleSheet("QTextEdit{\n"
                                          "background-color:rgb(255, 255, 255);\n"
                                          "font: 18pt \"Raleway\"; background-color: white;\n"
                                          "color: black;\n"
                                          "border-radius: 15px;\n"
                                          "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                          "padding-left:5px;\n"
                                          "padding-top:5px;\n"
                                          "}\n"
                                          "\n"
                                          "QTextEdit:focus{\n"
                                          "border: 2px solid rgb(73, 134, 127);\n"
                                          "\n"
                                          "}\n"
                                          "")
        self.text_sifrovani.setObjectName("text_sifrovani")
        self.klic_sifrovani = QtWidgets.QTextEdit(parent=self.tab_2)
        self.klic_sifrovani.setGeometry(QtCore.QRect(550, 30, 311, 81))
        self.klic_sifrovani.setStyleSheet("QTextEdit{\n"
                                          "background-color:rgb(255, 255, 255);\n"
                                          "font: 18pt \"Raleway\"; background-color: white;\n"
                                          "color: black;\n"
                                          "border-radius: 15px;\n"
                                          "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                          "padding-left:5px;\n"
                                          "padding-top:5px;\n"
                                          "}\n"
                                          "\n"
                                          "QTextEdit:focus{\n"
                                          "border: 2px solid rgb(73, 134, 127);\n"
                                          "\n"
                                          "}\n"
                                          "")
        self.klic_sifrovani.setObjectName("klic_sifrovani")
        self.encrypt_sifrovani = QtWidgets.QPushButton(parent=self.tab_2)
        self.encrypt_sifrovani.setGeometry(QtCore.QRect(120, 140, 141, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.encrypt_sifrovani.sizePolicy().hasHeightForWidth())
        self.encrypt_sifrovani.setSizePolicy(sizePolicy)
        self.encrypt_sifrovani.setStyleSheet("QPushButton#encrypt_sifrovani{\n"
                                             "background-color:rgba(91, 209, 206,0.7);\n"
                                             "font: 600 25pt \"Raleway\";\n"
                                             "border-radius: 15px;\n"
                                             "}\n"
                                             "\n"
                                             "\n"
                                             "QPushButton#encrypt_sifrovani:hover{\n"
                                             "background-color:rgb(73, 134, 127);\n"
                                             "font: 700 26pt \"Raleway\";\n"
                                             "}\n"
                                             "\n"
                                             "QPushButton#encrypt_sifrovani:pressed{\n"
                                             "font: 600 24pt \"Raleway\";\n"
                                             "}\n"
                                             "\n"
                                             "\n"
                                             "")
        self.encrypt_sifrovani.setObjectName("encrypt_sifrovani")
        self.label_4 = QtWidgets.QLabel(parent=self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(30, 240, 311, 41))
        self.label_4.setStyleSheet("font: 500 30pt \"Raleway\";")
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.filtrText_sifrovani = QtWidgets.QTextEdit(parent=self.tab_2)
        self.filtrText_sifrovani.setGeometry(QtCore.QRect(40, 280, 311, 81))
        self.filtrText_sifrovani.setStyleSheet("QTextEdit{\n"
                                               "background-color:rgb(255, 255, 255);\n"
                                               "font: 18pt \"Raleway\"; background-color: white;\n"
                                               "color: black;\n"
                                               "border-radius: 15px;\n"
                                               "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                               "padding-left:5px;\n"
                                               "padding-top:5px;\n"
                                               "}\n"
                                               "\n"
                                               "QTextEdit:focus{\n"
                                               "border: 2px solid rgb(73, 134, 127);\n"
                                               "\n"
                                               "}\n"
                                               "")
        self.filtrText_sifrovani.setReadOnly(True)
        self.filtrText_sifrovani.setAcceptRichText(False)
        self.filtrText_sifrovani.setObjectName("filtrText_sifrovani")
        self.label_5 = QtWidgets.QLabel(parent=self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(40, 360, 311, 41))
        self.label_5.setStyleSheet("font: 500 30pt \"Raleway\";")
        self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.encryptedText_sifrovani = QtWidgets.QTextEdit(parent=self.tab_2)
        self.encryptedText_sifrovani.setGeometry(QtCore.QRect(40, 400, 311, 81))
        self.encryptedText_sifrovani.setStyleSheet("QTextEdit{\n"
                                                   "background-color:rgb(255, 255, 255);\n"
                                                   "font: 18pt \"Raleway\"; background-color: white;\n"
                                                   "color: black;\n"
                                                   "border-radius: 15px;\n"
                                                   "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                   "padding-left:5px;\n"
                                                   "padding-top:5px;\n"
                                                   "}\n"
                                                   "\n"
                                                   "QTextEdit:focus{\n"
                                                   "border: 2px solid rgb(73, 134, 127);\n"
                                                   "\n"
                                                   "}\n"
                                                   "")
        self.encryptedText_sifrovani.setReadOnly(True)
        self.encryptedText_sifrovani.setObjectName("encryptedText_sifrovani")
        self.generateMatrix_sifrovani = QtWidgets.QPushButton(parent=self.tab_2)
        self.generateMatrix_sifrovani.setGeometry(QtCore.QRect(550, 430, 141, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.generateMatrix_sifrovani.sizePolicy().hasHeightForWidth())
        self.generateMatrix_sifrovani.setSizePolicy(sizePolicy)
        self.generateMatrix_sifrovani.setStyleSheet("QPushButton#generateMatrix_sifrovani{\n"
                                                    "background-color:rgba(91, 209, 206,0.7);\n"
                                                    "font: 600 25pt \"Raleway\";\n"
                                                    "border-radius: 15px;\n"
                                                    "}\n"
                                                    "\n"
                                                    "QPushButton#generateMatrix_sifrovani:hover{\n"
                                                    "background-color:rgb(73, 134, 127);\n"
                                                    "font: 700 26pt \"Raleway\";\n"
                                                    "}\n"
                                                    "\n"
                                                    "QPushButton#generateMatrix_sifrovani:pressed{\n"
                                                    "font: 600 24pt \"Raleway\";\n"
                                                    "}\n"
                                                    "\n"
                                                    "\n"
                                                    "")
        self.generateMatrix_sifrovani.setObjectName("generateMatrix_sifrovani")
        self.uploadMatrix_sifrovani = QtWidgets.QPushButton(parent=self.tab_2)
        self.uploadMatrix_sifrovani.setGeometry(QtCore.QRect(720, 430, 141, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadMatrix_sifrovani.sizePolicy().hasHeightForWidth())
        self.uploadMatrix_sifrovani.setSizePolicy(sizePolicy)
        self.uploadMatrix_sifrovani.setStyleSheet("QPushButton#uploadMatrix_sifrovani{\n"
                                                  "background-color:rgba(91, 209, 206,0.7);\n"
                                                  "font: 600 25pt \"Raleway\";\n"
                                                  "border-radius: 15px;\n"
                                                  "}\n"
                                                  "\n"
                                                  "QPushButton#uploadMatrix_sifrovani:hover{\n"
                                                  "background-color:rgb(73, 134, 127);\n"
                                                  "font: 700 26pt \"Raleway\";\n"
                                                  "}\n"
                                                  "\n"
                                                  "QPushButton#uploadMatrix_sifrovani:pressed{\n"
                                                  "font: 600 24pt \"Raleway\";\n"
                                                  "}\n"
                                                  "\n"
                                                  "\n"
                                                  "")
        self.uploadMatrix_sifrovani.setObjectName("uploadMatrix_sifrovani")
        self.matrixKey_sifrovani = QtWidgets.QTableView(parent=self.tab_2)
        self.matrixKey_sifrovani.setGeometry(QtCore.QRect(40, 510, 311, 131))
        self.matrixKey_sifrovani.setStyleSheet("QTableView\n"
                                               "{\n"
                                               "background-color:rgb(255, 255, 255);\n"
                                               "font: 18pt \"Raleway\"; background-color: white;\n"
                                               "color: black;\n"
                                               "border-radius: 15px;\n"
                                               "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                               "padding-left:5px;\n"
                                               "padding-top:5px;\n"
                                               "padding-right:5px;\n"
                                               "padding-bottom:5px;\n"
                                               "}\n"
                                               "\n"
                                               "QTableView:focus{\n"
                                               "border: 2px solid rgb(73, 134, 127);\n"
                                               "\n"
                                               "}")
        self.matrixKey_sifrovani.setObjectName("matrixKey_sifrovani")
        self.matrixKey_sifrovani.horizontalHeader().setVisible(True)
        self.matrixKey_sifrovani.horizontalHeader().setHighlightSections(False)
        self.matrixKey_sifrovani.verticalHeader().setVisible(False)
        self.matrixKey_sifrovani.verticalHeader().setHighlightSections(False)
        self.matrixSortedKey_sifrovani = QtWidgets.QTableView(parent=self.tab_2)
        self.matrixSortedKey_sifrovani.setGeometry(QtCore.QRect(550, 510, 311, 131))
        self.matrixSortedKey_sifrovani.setStyleSheet("QTableView\n"
                                                     "{\n"
                                                     "background-color:rgb(255, 255, 255);\n"
                                                     "font: 18pt \"Raleway\"; background-color: white;\n"
                                                     "color: black;\n"
                                                     "border-radius: 15px;\n"
                                                     "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                     "padding-left:5px;\n"
                                                     "padding-top:5px;\n"
                                                     "padding-right:5px;\n"
                                                     "padding-bottom:5px;\n"
                                                     "}\n"
                                                     "\n"
                                                     "QTableView:focus{\n"
                                                     "border: 2px solid rgb(73, 134, 127);\n"
                                                     "\n"
                                                     "}")
        self.matrixSortedKey_sifrovani.setObjectName("matrixSortedKey_sifrovani")
        self.matrixSortedKey_sifrovani.horizontalHeader().setVisible(True)
        self.matrixSortedKey_sifrovani.horizontalHeader().setHighlightSections(False)
        self.matrixSortedKey_sifrovani.verticalHeader().setVisible(False)
        self.matrixSortedKey_sifrovani.verticalHeader().setHighlightSections(False)
        self.comboBox_sifrovani = QtWidgets.QComboBox(parent=self.tab_2)
        self.comboBox_sifrovani.setGeometry(QtCore.QRect(552, 140, 311, 41))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setKerning(True)
        self.comboBox_sifrovani.setFont(font)
        self.comboBox_sifrovani.setObjectName("comboBox_sifrovani")
        self.comboBox_sifrovani.addItem("0")
        self.comboBox_sifrovani.addItem("1")
        self.comboBox_sifrovani.addItem("2")
        self.saved_matrix = QtWidgets.QLabel(parent=self.tab_2)
        self.saved_matrix.setGeometry(QtCore.QRect(40, 190, 311, 41))
        self.saved_matrix.setStyleSheet("font: 400 15pt \"Raleway\";")
        self.saved_matrix.setText("")
        self.saved_matrix.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.saved_matrix.setObjectName("saved_matrix")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.text_desifrovani = QtWidgets.QTextEdit(parent=self.tab)
        self.text_desifrovani.setGeometry(QtCore.QRect(40, 30, 311, 81))
        self.text_desifrovani.setStyleSheet("QTextEdit{\n"
                                            "background-color:rgb(255, 255, 255);\n"
                                            "font: 18pt \"Raleway\"; background-color: white;\n"
                                            "color: black;\n"
                                            "border-radius: 15px;\n"
                                            "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                            "padding-left:5px;\n"
                                            "padding-top:5px;\n"
                                            "}\n"
                                            "\n"
                                            "QTextEdit:focus{\n"
                                            "border: 2px solid rgb(73, 134, 127);\n"
                                            "\n"
                                            "}\n"
                                            "")
        self.text_desifrovani.setObjectName("text_desifrovani")
        self.label_6 = QtWidgets.QLabel(parent=self.tab)
        self.label_6.setGeometry(QtCore.QRect(0, 10, 900, 31))
        self.label_6.setStyleSheet("font: 500 30pt \"Arial\";")
        self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.klic_desifrovani = QtWidgets.QTextEdit(parent=self.tab)
        self.klic_desifrovani.setGeometry(QtCore.QRect(550, 30, 311, 81))
        self.klic_desifrovani.setStyleSheet("QTextEdit{\n"
                                            "background-color:rgb(255, 255, 255);\n"
                                            "font: 18pt \"Raleway\"; background-color: white;\n"
                                            "color: black;\n"
                                            "border-radius: 15px;\n"
                                            "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                            "padding-left:5px;\n"
                                            "padding-top:5px;\n"
                                            "}\n"
                                            "\n"
                                            "QTextEdit:focus{\n"
                                            "border: 2px solid rgb(73, 134, 127);\n"
                                            "\n"
                                            "}\n"
                                            "")
        self.klic_desifrovani.setObjectName("klic_desifrovani")
        self.decrypt_desifrovani = QtWidgets.QPushButton(parent=self.tab)
        self.decrypt_desifrovani.setGeometry(QtCore.QRect(120, 190, 141, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.decrypt_desifrovani.sizePolicy().hasHeightForWidth())
        self.decrypt_desifrovani.setSizePolicy(sizePolicy)
        self.decrypt_desifrovani.setStyleSheet("QPushButton#decrypt_desifrovani{\n"
                                               "background-color:rgba(91, 209, 206,0.7);\n"
                                               "font: 600 25pt \"Raleway\";\n"
                                               "border-radius: 15px;\n"
                                               "}\n"
                                               "\n"
                                               "\n"
                                               "QPushButton#decrypt_desifrovani:hover{\n"
                                               "background-color:rgb(73, 134, 127);\n"
                                               "font: 700 26pt \"Raleway\";\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton#decrypt_desifrovani:pressed{\n"
                                               "font: 600 24pt \"Raleway\";\n"
                                               "}\n"
                                               "\n"
                                               "\n"
                                               "")
        self.decrypt_desifrovani.setObjectName("decrypt_desifrovani")
        self.comboBox_sifrovani_2 = QtWidgets.QComboBox(parent=self.tab)
        self.comboBox_sifrovani_2.setGeometry(QtCore.QRect(550, 140, 311, 41))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setKerning(True)
        self.comboBox_sifrovani_2.setFont(font)
        self.comboBox_sifrovani_2.setObjectName("comboBox_sifrovani_2")
        self.comboBox_sifrovani_2.addItem("")
        self.comboBox_sifrovani_2.addItem("")
        self.comboBox_sifrovani_2.addItem("")
        self.encryptedText_sifrovani_2 = QtWidgets.QTextEdit(parent=self.tab)
        self.encryptedText_sifrovani_2.setGeometry(QtCore.QRect(40, 330, 311, 81))
        self.encryptedText_sifrovani_2.setStyleSheet("QTextEdit{\n"
                                                     "background-color:rgb(255, 255, 255);\n"
                                                     "font: 18pt \"Raleway\"; background-color: white;\n"
                                                     "color: black;\n"
                                                     "border-radius: 15px;\n"
                                                     "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                     "padding-left:5px;\n"
                                                     "padding-top:5px;\n"
                                                     "}\n"
                                                     "\n"
                                                     "QTextEdit:focus{\n"
                                                     "border: 2px solid rgb(73, 134, 127);\n"
                                                     "\n"
                                                     "}\n"
                                                     "")
        self.encryptedText_sifrovani_2.setReadOnly(True)
        self.encryptedText_sifrovani_2.setObjectName("encryptedText_sifrovani_2")
        self.label_7 = QtWidgets.QLabel(parent=self.tab)
        self.label_7.setGeometry(QtCore.QRect(40, 290, 311, 41))
        self.label_7.setStyleSheet("font: 500 30pt \"Raleway\";")
        self.label_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.matrixRandom_sifrovani_2 = QtWidgets.QTableView(parent=self.tab)
        self.matrixRandom_sifrovani_2.setGeometry(QtCore.QRect(550, 200, 311, 211))
        self.matrixRandom_sifrovani_2.setStyleSheet("QTableView\n"
                                                    "{\n"
                                                    "background-color:rgb(255, 255, 255);\n"
                                                    "font: 18pt \"Raleway\"; background-color: white;\n"
                                                    "color: black;\n"
                                                    "border-radius: 15px;\n"
                                                    "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                    "padding-left:5px;\n"
                                                    "padding-top:5px;\n"
                                                    "padding-right:5px;\n"
                                                    "padding-bottom:5px;\n"
                                                    "}\n"
                                                    "\n"
                                                    "QTableView:focus{\n"
                                                    "border: 2px solid rgb(73, 134, 127);\n"
                                                    "\n"
                                                    "}")
        self.matrixRandom_sifrovani_2.setObjectName("matrixRandom_sifrovani_2")
        self.matrixRandom_sifrovani_2.horizontalHeader().setVisible(True)
        self.matrixRandom_sifrovani_2.horizontalHeader().setHighlightSections(False)
        self.matrixRandom_sifrovani_2.verticalHeader().setVisible(True)
        self.matrixRandom_sifrovani_2.verticalHeader().setHighlightSections(False)
        self.matrixSortedKey_sifrovani_2 = QtWidgets.QTableView(parent=self.tab)
        self.matrixSortedKey_sifrovani_2.setGeometry(QtCore.QRect(550, 500, 311, 131))
        self.matrixSortedKey_sifrovani_2.setStyleSheet("QTableView\n"
                                                       "{\n"
                                                       "background-color:rgb(255, 255, 255);\n"
                                                       "font: 18pt \"Raleway\"; background-color: white;\n"
                                                       "color: black;\n"
                                                       "border-radius: 15px;\n"
                                                       "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                       "padding-left:5px;\n"
                                                       "padding-top:5px;\n"
                                                       "padding-right:5px;\n"
                                                       "padding-bottom:5px;\n"
                                                       "}\n"
                                                       "\n"
                                                       "QTableView:focus{\n"
                                                       "border: 2px solid rgb(73, 134, 127);\n"
                                                       "\n"
                                                       "}")
        self.matrixSortedKey_sifrovani_2.setObjectName("matrixSortedKey_sifrovani_2")
        self.matrixSortedKey_sifrovani_2.horizontalHeader().setVisible(True)
        self.matrixSortedKey_sifrovani_2.horizontalHeader().setHighlightSections(False)
        self.matrixSortedKey_sifrovani_2.verticalHeader().setVisible(False)
        self.matrixSortedKey_sifrovani_2.verticalHeader().setHighlightSections(False)
        self.matrixKey_sifrovani_2 = QtWidgets.QTableView(parent=self.tab)
        self.matrixKey_sifrovani_2.setGeometry(QtCore.QRect(40, 500, 311, 131))
        self.matrixKey_sifrovani_2.setStyleSheet("QTableView\n"
                                                 "{\n"
                                                 "background-color:rgb(255, 255, 255);\n"
                                                 "font: 18pt \"Raleway\"; background-color: white;\n"
                                                 "color: black;\n"
                                                 "border-radius: 15px;\n"
                                                 "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                                 "padding-left:5px;\n"
                                                 "padding-top:5px;\n"
                                                 "padding-right:5px;\n"
                                                 "padding-bottom:5px;\n"
                                                 "}\n"
                                                 "\n"
                                                 "QTableView:focus{\n"
                                                 "border: 2px solid rgb(73, 134, 127);\n"
                                                 "\n"
                                                 "}")
        self.matrixKey_sifrovani_2.setObjectName("matrixKey_sifrovani_2")
        self.matrixKey_sifrovani_2.horizontalHeader().setVisible(True)
        self.matrixKey_sifrovani_2.horizontalHeader().setHighlightSections(False)
        self.matrixKey_sifrovani_2.verticalHeader().setVisible(False)
        self.matrixKey_sifrovani_2.verticalHeader().setHighlightSections(False)
        self.uploadMatrix_desifrovani = QtWidgets.QPushButton(parent=self.tab)
        self.uploadMatrix_desifrovani.setGeometry(QtCore.QRect(630, 430, 141, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadMatrix_desifrovani.sizePolicy().hasHeightForWidth())
        self.uploadMatrix_desifrovani.setSizePolicy(sizePolicy)
        self.uploadMatrix_desifrovani.setStyleSheet("QPushButton#uploadMatrix_desifrovani{\n"
                                                    "background-color:rgba(91, 209, 206,0.7);\n"
                                                    "font: 600 25pt \"Raleway\";\n"
                                                    "border-radius: 15px;\n"
                                                    "}\n"
                                                    "\n"
                                                    "\n"
                                                    "QPushButton#uploadMatrix_desifrovani:hover{\n"
                                                    "background-color:rgb(73, 134, 127);\n"
                                                    "font: 700 26pt \"Raleway\";\n"
                                                    "}\n"
                                                    "\n"
                                                    "QPushButton#uploadMatrix_desifrovani:pressed{\n"
                                                    "font: 600 24pt \"Raleway\";\n"
                                                    "}\n"
                                                    "\n"
                                                    "\n"
                                                    "")
        self.uploadMatrix_desifrovani.setObjectName("uploadMatrix_desifrovani")
        self.tabWidget.addTab(self.tab, "")
        self.label = QtWidgets.QLabel(parent=self.widget)
        self.label.setGeometry(QtCore.QRect(0, 0, 900, 46))
        self.label.setStyleSheet("font: 600 30pt \"Raleway\";")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(parent=self.widget)
        self.label_3.setGeometry(QtCore.QRect(0, 24, 900, 51))
        self.label_3.setStyleSheet("font: 400 18pt \"Raleway\";")
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.matrix = QtWidgets.QTableView(parent=self.tab_2)
        self.matrix.setGeometry(QtCore.QRect(550, 210, 311, 211))  # Adjust the geometry as needed
        self.matrix.setStyleSheet("QTableView\n"
                                  "{\n"
                                  "background-color:rgb(255, 255, 255);\n"
                                  "font: 18pt \"Raleway\"; background-color: white;\n"
                                  "color: black;\n"
                                  "border-radius: 15px;\n"
                                  "border: 2px solid rgba(91, 209, 206,0.7);\n"
                                  "padding-left:5px;\n"
                                  "padding-top:5px;\n"
                                  "padding-right:5px;\n"
                                  "padding-bottom:5px;\n"
                                  "}\n"
                                  "\n"
                                  "QTableView:focus{\n"
                                  "border: 2px solid rgb(73, 134, 127);\n"
                                  "\n"
                                  "}")
        self.matrix.horizontalHeader().setVisible(True)
        self.matrix.horizontalHeader().setHighlightSections(False)
        self.matrix.verticalHeader().setVisible(True)
        self.matrix.verticalHeader().setHighlightSections(False)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "Šifrování"))
        self.text_sifrovani.setPlaceholderText(_translate("Form", "Zadejte text k šifrování..."))
        self.klic_sifrovani.setPlaceholderText(_translate("Form", "Zadejte klíč k šifrování..."))
        self.encrypt_sifrovani.setText(_translate("Form", "Zašifrovat"))
        self.label_4.setText(_translate("Form", "Filtrovaný text"))
        self.label_5.setText(_translate("Form", "Zašifrovaný text"))
        self.generateMatrix_sifrovani.setText(_translate("Form", "Random"))
        self.uploadMatrix_sifrovani.setText(_translate("Form", "Nahrát"))
        self.comboBox_sifrovani.setItemText(0, _translate("Form", "ADFGX CZ"))
        self.comboBox_sifrovani.setItemText(1, _translate("Form", "ADFGX EN"))
        self.comboBox_sifrovani.setItemText(2, _translate("Form", "ADFGVX"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Šifrování"))
        self.text_desifrovani.setPlaceholderText(_translate("Form", "Zadejte text k dešifrování..."))
        self.label_6.setText(_translate("Form", "Dešifrování"))
        self.klic_desifrovani.setPlaceholderText(_translate("Form", "Zadejte klíč k dešifrování..."))
        self.decrypt_desifrovani.setText(_translate("Form", "Dešifrovat"))
        self.comboBox_sifrovani_2.setItemText(0, _translate("Form", "ADFGX CZ"))
        self.comboBox_sifrovani_2.setItemText(1, _translate("Form", "ADFGX EN"))
        self.comboBox_sifrovani_2.setItemText(2, _translate("Form", "ADFGVX"))
        self.label_7.setText(_translate("Form", "Dešifrovaný text"))
        self.uploadMatrix_desifrovani.setText(_translate("Form", "Nahrát"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Dešifrování"))
        self.label.setText(_translate("Form", "ADFG(V)X CYPHER"))
        self.label_3.setText(_translate("Form", "Filip Hajduch"))

        self.matrixRandom_sifrovani = None
        self.matrix2 = None

        self.encrypt_sifrovani.clicked.connect(self.encryptTextGUI)
        self.generateMatrix_sifrovani.clicked.connect(self.createRandomMatrix)
        self.uploadMatrix_sifrovani.clicked.connect(self.openMatrixFromFile)
        self.decrypt_desifrovani.clicked.connect(self.decryptTextGUI)
        self.uploadMatrix_desifrovani.clicked.connect(self.openMatrixFromFile)

    def createRandomMatrix(self):
        selected_index = self.comboBox_sifrovani.currentIndex()

        adfgx = czechEncoding = True

        if selected_index == 0:
            adfgx = czechEncoding = True
        elif selected_index == 1:
            adfgx = True
            czechEncoding = False
        elif selected_index == 2:
            adfgx = czechEncoding = False

        try:
            matrix = createMatrix(adfgx, czechEncoding)
            self.matrixRandom_sifrovani = matrix
            self.updateMatrixView(matrix, self.matrix)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", str(e))

    def encryptTextGUI(self):
        text = self.text_sifrovani.toPlainText()
        key = self.klic_sifrovani.toPlainText()

        if self.matrixRandom_sifrovani is not None:
            matrix = self.matrixRandom_sifrovani
        else:
            matrix = None

        adfgx = czechEncoding = True

        selected_index = self.comboBox_sifrovani.currentIndex()

        if selected_index == 0:
            adfgx = czechEncoding = True
        elif selected_index == 1:
            adfgx = True
            czechEncoding = False
        elif selected_index == 2:
            adfgx = czechEncoding = False

        try:
            if matrix is not None:
                # You can use 'matrix' here in your encryption process
                filteredKey = filtrationKey(key)
                newText = replaceChars(text, matrix, adfgx, czechEncoding)
                keyMatrix = createKeyMatrix(filteredKey, newText)
                self.updateMatrixView(keyMatrix, self.matrixSortedKey_sifrovani)
                encryptedText = encryptADFGVX(text, key, matrix, keyMatrix, adfgx, czechEncoding)
                sortedKeyMatrix = reorderMatrix(keyMatrix, filteredKey)
                self.updateMatrixView(sortedKeyMatrix, self.matrixKey_sifrovani)
                filteredText = filtrationOpenText(text, adfgx, czechEncoding)
                matrixSavedText = "matice uložena jako matice.txt"
                self.filtrText_sifrovani.setText(filteredText)
                self.encryptedText_sifrovani.setText(encryptedText)
                self.saved_matrix.setText(matrixSavedText)
            else:
                # Handle the case where the matrix is not available
                QtWidgets.QMessageBox.critical(None, "Error", "Matrix not available")

        except ValueError as e:
            QtWidgets.QMessageBox.critical(None, "Error", str(e))

    def decryptTextGUI(self):
        text = self.text_desifrovani.toPlainText()
        key = self.klic_desifrovani.toPlainText()

        selected_index = self.comboBox_sifrovani_2.currentIndex()
        adfgx = True

        if selected_index == 0:
            adfgx = True
        elif selected_index == 1:
            adfgx = True
        elif selected_index == 2:
            adfgx = False

        if self.matrix2 is not None:
            matrix = self.matrix2
        else:
            QtWidgets.QMessageBox.critical(None, "Error", "Matrix not available")
            return

        try:
            key = filtrationKey(key)
            decryptedText = decryptADFGVX(key, text, matrix, adfgx)
            self.encryptedText_sifrovani_2.setText(decryptedText)
            nonSortedMatrix = decryptMatrixOne(key, text)
            sortedMatrix = reorderMatrix(nonSortedMatrix, key)
            self.updateMatrixView(sortedMatrix, self.matrixSortedKey_sifrovani_2)

            self.updateMatrixView(nonSortedMatrix, self.matrixKey_sifrovani_2)

        except KeyError as e:
            QtWidgets.QMessageBox.critical(None, "Error", "Invalid key or text. Check your input.")
        except ValueError as e:
            QtWidgets.QMessageBox.critical(None, "Error", str(e))

    def updateMatrixView(self, matrix, table_view):
        model = QtGui.QStandardItemModel(len(matrix), len(matrix.columns))
        model.setHorizontalHeaderLabels(matrix.columns)  # Nastavení popisků sloupců u matice
        model.setVerticalHeaderLabels([str(label) for label in matrix.index])  # Nastavení popisků řádků

        for row_idx in range(len(matrix)):
            for col_idx in range(len(matrix.columns)):
                item = QtGui.QStandardItem(str(matrix.iloc[row_idx, col_idx]))

                # nastavení textu doprostřed
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.setItem(row_idx, col_idx, item)

                table_view.setModel(model)

                # Set text to fill the entire QTableView
                table_view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

                table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

                table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def openMatrixFromFile(self):
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        # Get the current tab index
        tab_index = self.tabWidget.currentIndex()
        selected_index = 0
        if tab_index == 0:
            selected_index = self.comboBox_sifrovani.currentIndex()
        elif tab_index == 1:
            selected_index = self.comboBox_sifrovani_2.currentIndex()

        adfgx = True
        if selected_index == 0:
            adfgx = True
        elif selected_index == 1:
            adfgx = True

        elif selected_index == 2:
            adfgx = False

        try:
            matrix = openMatrixFromFile(path, adfgx)
            if tab_index == 0:
                self.matrixRandom_sifrovani = matrix
                self.updateMatrixView(matrix, self.matrix)
            elif tab_index == 1:
                self.matrix2 = matrix
                self.updateMatrixView(matrix, self.matrixRandom_sifrovani_2)
        except TypeError as e:
            QtWidgets.QMessageBox.critical(None, "Error", "Nebyla zvolena matice")
        except ValueError as e:
            QtWidgets.QMessageBox.critical(None, "Error", str(e))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
