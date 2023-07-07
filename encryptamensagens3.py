import sys
import random
import string
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class RSAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA Cryptography App")
        self.setFixedSize(600, 400)

        # Estilo da janela
        self.setStyleSheet("background-color: white; color: black;")

        # Criação dos elementos da interface
        self.password_label = QLabel("Senha:", self)
        self.password_label.setStyleSheet("font-weight: bold;")
        self.password_input = QLineEdit(self)
        self.generate_password_button = QPushButton("Gerar Senha", self)
        self.generate_password_button.setStyleSheet("background-color: #0088FF; color: white;")
        self.message_label = QLabel("Mensagem:", self)
        self.message_label.setStyleSheet("font-weight: bold;")
        self.message_input = QTextEdit(self)
        self.encrypt_button = QPushButton("Criptografar", self)
        self.encrypt_button.setStyleSheet("background-color: #0088FF; color: white;")
        self.decrypt_button = QPushButton("Descriptografar", self)
        self.decrypt_button.setStyleSheet("background-color: #0088FF; color: white;")
        self.result_label = QLabel("Mensagem Criptografada/Descriptografada:", self)
        self.result_label.setStyleSheet("font-weight: bold;")
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)

        # Criação dos botões de seleção de bits
        self.bits_label = QLabel("Selecionar Bits:", self)
        self.bits_label.setStyleSheet("font-weight: bold;")
        self.bits_button_group = QButtonGroup(self)
        self.bits_512_button = QRadioButton("512 bits", self)
        self.bits_1024_button = QRadioButton("1024 bits", self)
        self.bits_2048_button = QRadioButton("2048 bits", self)
        self.bits_4096_button = QRadioButton("4096 bits", self)
        self.bits_512_button.setChecked(True)
        self.bits_button_group.addButton(self.bits_512_button)
        self.bits_button_group.addButton(self.bits_1024_button)
        self.bits_button_group.addButton(self.bits_2048_button)
        self.bits_button_group.addButton(self.bits_4096_button)

        # Configuração do layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.generate_password_button)
        layout.addWidget(self.message_label)
        layout.addWidget(self.message_input)
        layout.addWidget(self.bits_label)
        layout.addWidget(self.bits_512_button)
        layout.addWidget(self.bits_1024_button)
        layout.addWidget(self.bits_2048_button)
        layout.addWidget(self.bits_4096_button)
        layout.addWidget(self.encrypt_button)
        layout.addWidget(self.decrypt_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_output)
        self.setLayout(layout)

        # Conexão dos botões com as funções correspondentes
        self.generate_password_button.clicked.connect(self.generate_password)
        self.encrypt_button.clicked.connect(self.encrypt_message)
        self.decrypt_button.clicked.connect(self.decrypt_message)
        self.message_input.textChanged.connect(self.detect_bits)

        # Gerar chave RSA
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

    def generate_password(self):
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=64))
        self.password_input.setText(password)

    def encrypt_message(self):
        password = self.password_input.text()
        message = self.message_input.toPlainText().encode()

        # Obter o tamanho dos bits selecionado
        selected_bits = self.get_selected_bits()

        # Inserir os bits no cabeçalho da mensagem
        header = f"Bits: {selected_bits}\n".encode()
        message_with_header = header + message

        # Criptografar a mensagem
        encrypted_message = self.private_key.public_key().encrypt(
            message_with_header,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Exibir a mensagem criptografada no campo de saída
        self.result_output.setPlainText(encrypted_message.hex())

    def decrypt_message(self):
        password = self.password_input.text()
        encrypted_message = bytes.fromhex(self.result_output.toPlainText())

        # Descriptografar a mensagem
        decrypted_message = self.private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Remover o cabeçalho da mensagem para obter apenas o texto original
        header_length = decrypted_message.index(b'\n') + 1
        original_message = decrypted_message[header_length:]

        # Exibir a mensagem descriptografada no campo de saída
        self.result_output.setPlainText(original_message.decode())

    def get_selected_bits(self):
        if self.bits_512_button.isChecked():
            return 512
        elif self.bits_1024_button.isChecked():
            return 1024
        elif self.bits_2048_button.isChecked():
            return 2048
        elif self.bits_4096_button.isChecked():
            return 4096

    def detect_bits(self):
        encrypted_message = self.message_input.toPlainText()
        if encrypted_message.startswith("Bits:"):
            # Extrair o tamanho dos bits do cabeçalho da mensagem
            header_length = encrypted_message.index('\n') + 1
            bits_str = encrypted_message[6:header_length-1]

            # Selecionar o botão correspondente aos bits detectados
            if bits_str == '512':
                self.bits_512_button.setChecked(True)
            elif bits_str == '1024':
                self.bits_1024_button.setChecked(True)
            elif bits_str == '2048':
                self.bits_2048_button.setChecked(True)
            elif bits_str == '4096':
                self.bits_4096_button.setChecked(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Estilo da aplicação
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(245, 245, 245))
    palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(0, 136, 255))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    font = QFont()
    font.setPointSize(10)
    app.setFont(font)

    rsa_app = RSAApp()
    rsa_app.show()
    sys.exit(app.exec_())
