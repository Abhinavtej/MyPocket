import sys
import sqlite3
from PySide6.QtCore import Qt, QDate
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
import matplotlib.pyplot as plt
from PySide6 import QtCore
from PySide6.QtCore import QDate
from PySide6.QtGui import QPixmap, QColor, QBrush, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QVBoxLayout, QWidget, QDialog, QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem, \
    QAbstractItemView, QAbstractScrollArea, QComboBox, QDoubleSpinBox, QCalendarWidget, \
    QHeaderView, QHBoxLayout, QDateEdit


class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Page")
        self.setFixedSize(300, 400)

        # Connect to the database
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Create the users table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT PRIMARY KEY, password TEXT)")

        # Create widgets
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.title_label = QLabel("My Pocket")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.textChanged.connect(self.lowercase)
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # Mask the password
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        # Create a registration form
        self.registration_label = QLabel("Don't have an account?")
        self.registration_button = QPushButton("Register")
        self.registration_button.clicked.connect(self.register)

        # Create a forgot password form
        self.forgot_password_label = QLabel("Forgot your password?")
        self.forgot_password_button = QPushButton("Reset Password")
        self.forgot_password_button.clicked.connect(self.reset_password)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.registration_label)
        layout.addWidget(self.registration_button)
        layout.addWidget(self.forgot_password_label)
        layout.addWidget(self.forgot_password_button)

        # Create a central widget and set its layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Check if the user exists in the database
        self.cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = self.cursor.fetchone()

        if user is not None and user[2] == password:
            # If the user exists, show the Budget Planner page
            self.home = Home(email)
            self.home.show()
            self.close()

        else:
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Error")
            error_label = QLabel("Invalid username or password.")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

    def register(self):
        # Create a registration form dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Registration Form")

        # Create widgets
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        email_label = QLabel("Email:")
        email_input = QLineEdit()
        email_input.textChanged.connect(self.lowercase)
        password_label = QLabel("Password:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)  # Mask the password
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.Password)  # Mask the password
        register_button = QPushButton("Register")
        register_button.clicked.connect(
            lambda: self.register_user(dialog, name_input.text(), email_input.text(), password_input.text(),
                                       confirm_password_input.text()))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        layout.addWidget(confirm_password_label)
        layout.addWidget(confirm_password_input)
        layout.addWidget(register_button)

        # Set the dialog layout and show it
        dialog.setLayout(layout)
        dialog.exec()

    def register_user(self, dialog, name, email, password, confirm_password):
        # Check that the fields are not empty
        if not name.strip() or not email.strip() or not password.strip() or not confirm_password.strip():
            msg_box = QDialog(dialog)
            msg_box.setWindowTitle("Error")
            msg_label = QLabel("Fields are not empty.")
            layout = QVBoxLayout()
            layout.addWidget(msg_label)
            msg_box.setLayout(layout)
            msg_box.exec()
            return

        # Check that the passwords match
        if password != confirm_password:
            error_dialog = QDialog(dialog)
            error_dialog.setWindowTitle("Error")
            error_label = QLabel("Passwords do not match.")

            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        # Check if the user is already in the database
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = self.cursor.fetchone()
        if user is not None:
            error_dialog = QDialog(dialog)
            error_dialog.setWindowTitle("Error")
            error_label = QLabel("User already exists.")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        # Add the user to the database
        self.cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                            (name, email, password))
        self.connection.commit()

        # Close the dialog and show a message
        dialog.accept()
        message_dialog = QDialog(dialog)
        message_dialog.setWindowTitle("Success")
        message_label = QLabel("Registration successful.")
        layout = QVBoxLayout()
        layout.addWidget(message_label)
        message_dialog.setLayout(layout)
        message_dialog.exec()

    def reset_password(self):
        # Create a reset password form dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password Form")

        # Create widgets
        email_label = QLabel("Email:")
        email_input = QLineEdit()
        email_input.textChanged.connect(self.lowercase)
        reset_button = QPushButton("Reset Password")
        reset_button.clicked.connect(lambda: self.send_reset_email(dialog, email_input.text()))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        layout.addWidget(reset_button)

        # Set the dialog layout and show it
        dialog.setLayout(layout)
        dialog.exec()

    def send_reset_email(self, dialog, email):
        # Check if the user is in the database
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = self.cursor.fetchone()

        if user is None:
            # If the user doesn't exist, show an error message
            error_dialog = QDialog(dialog)
            error_dialog.setWindowTitle("Error")
            error_label = QLabel("This email address is not registered.")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        # Update the user's password in the database
        self.cursor.execute("UPDATE users SET password = ? WHERE email = ?", (user[0], email))
        self.connection.commit()

        # Set up the SMTP server credentials
        smtp_server = 'smtp-relay.sendinblue.com'
        smtp_port = 587  # or 465 for SSL/TLS encryption
        smtp_username = 'abhinavtej.9a@gmail.com'
        smtp_password = 'xsmtpsib-f708c5b860d3662c1247f7acbabb99f5d4d6b440642d851274b821e8907366e2-c1QskZnMC6NVdmg0'

        # Set up the email message
        sender = 'Admin@mypocket.app'
        recipient = email
        subject = 'New Password for My Pocket'
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = subject
        text = f'Your New Password is: {user[0]}'
        message.attach(MIMEText(text))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # enable encryption for plain text authentication
            server.login(smtp_username, smtp_password)
            server.sendmail(sender, recipient, message.as_string())

        # Close the dialog and show a message
        dialog.accept()
        message_dialog = QDialog(dialog)
        message_dialog.setWindowTitle("Success")
        message_label = QLabel("Your password has been reset. \nCheck your email for the New Password.")

        layout = QVBoxLayout()
        layout.addWidget(message_label)
        message_dialog.setLayout(layout)
        message_dialog.exec()

    def lowercase(self, text):
        try:
            email_input = self.sender()
            email_input.setText(text.lower())
        except NameError:
            pass

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class Home(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Home")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = self.cursor.fetchone()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel(f'Hello {user[0]}!')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Create a horizontal layout for buttons
        button_layout1 = QHBoxLayout()
        button_layout2 = QHBoxLayout()
        button_layout3 = QHBoxLayout()

        self.button1 = QPushButton("Budget Planner")
        self.button1.clicked.connect(self.open_budget_planner)
        self.button2 = QPushButton("Profile")
        self.button2.clicked.connect(self.open_profile)
        self.button3 = QPushButton("Income")
        self.button3.clicked.connect(self.open_income)
        self.button4 = QPushButton("Categories")
        self.button4.clicked.connect(self.open_category)
        self.button5 = QPushButton("Expenses")
        self.button5.clicked.connect(self.open_expenses)
        self.button6 = QPushButton("Reports")
        self.button6.clicked.connect(self.open_reports)
        button_layout1.addWidget(self.button1)
        button_layout1.addWidget(self.button2)
        button_layout2.addWidget(self.button3)
        button_layout2.addWidget(self.button4)
        button_layout3.addWidget(self.button5)
        button_layout3.addWidget(self.button6)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)

        # Create a horizontal layout for the logout button and add it to the main layout
        logout_layout = QHBoxLayout()
        logout_layout.addStretch(1)
        logout_layout.addWidget(self.logout_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(logout_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)
        main_layout.addLayout(button_layout3)
        main_layout.addSpacing(20)

        # Add the hyperlink text to the bottom of the window
        link_layout = QHBoxLayout()
        self.link_label1 = QLabel("<a href='#'>Contact Us</a>")
        self.link_label1.setMargin(0)
        self.link_label2 = QLabel("<a href='#'>About Us</a>")
        self.link_label2.setMargin(0)
        self.link_label1.setOpenExternalLinks(False)
        self.link_label2.setOpenExternalLinks(False)
        self.link_label1.setAlignment(QtCore.Qt.AlignCenter)
        self.link_label2.setAlignment(QtCore.Qt.AlignCenter)
        self.link_label1.linkActivated.connect(self.show_contact_form)
        self.link_label2.linkActivated.connect(self.show_about_us)
        # Connect signal to method
        link_layout.addWidget(self.link_label2)
        link_layout.addSpacing(-100)
        link_layout.addWidget(self.link_label1)
        main_layout.addLayout(link_layout)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def logout(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.login_window = LoginPage()
        self.login_window.show()

    def show_contact_form(self):
        # Create and show the ContactForm window
        self.contact_form = ContactForm()
        self.contact_form.show()

    def show_about_us(self):
        self.close()
        # Create and show the ContactForm window
        self.about_us = AboutUs(self.email)
        self.about_us.show()

    def open_budget_planner(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.budget_planner = BudgetPlanner(self.email)
        self.budget_planner.show()

    def open_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.category= Category(self.email)
        self.category.show()

    def open_reports(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.reports = Reports(self.email)
        self.reports.show()

    def open_profile(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.profile = Profile(self.email)
        self.profile.show()

    def open_income(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.income = Income(self.email)
        self.income.show()

    def open_expenses(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.expenses = Expenses(self.email)
        self.expenses.show()


class AboutUs(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("About Us")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('About Us')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_about_us)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create a QLabel for the paragraph text
        self.paragraph_label = QLabel()
        self.paragraph_label.setText(
            "J Abhinavtej Reddy - 2211CS020208\n"
            "K Nandini - 2211CS020230\n"
            "Gauri Mathur - 2211CS020183\n"
            "G Bharaghava - 2211CS020181\n"
            "J A Kruthin - 2211CS020209\n\n"
            "We the team of students from AIML Gamma, \n"
            "under the guidance of Dr. J Pradeep Kumar and \n"
            "Asst.Prof. D Chinni, have collaborated to develop\n"
            "an innovative budget planner app using Python."
        )
        self.paragraph_label.setStyleSheet("font-size: 11px;")
        self.paragraph_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.paragraph_label)
        main_layout.addSpacing(40)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def close_about_us(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()


class ContactForm(QWidget):
    def __init__(self):
        super().__init__()

        # Create widgets for form inputs
        name_label = QLabel('Name')
        self.name_input = QLineEdit()
        email_label = QLabel('Email')
        self.email_input = QLineEdit()
        self.email_input.textChanged.connect(self.lowercase)
        message_label = QLabel('Message')
        self.message_input = QTextEdit()
        submit_button = QPushButton('Submit')

        # Connect the submit button to the send_email slot
        submit_button.clicked.connect(self.send_email)

        # Create layout for form inputs
        form_layout = QVBoxLayout()
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(message_label)
        form_layout.addWidget(self.message_input)
        form_layout.addWidget(submit_button)

        # Create layout for entire form
        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)

        # Set main layout for window
        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle('Contact Us')
        self.setFixedSize(300, 400)

    def send_email(self):
        # Get the form input values
        name = self.name_input.text()
        email = self.email_input.text()
        message = self.message_input.toPlainText()

        # Validate the inputs
        if not name:
            QMessageBox.warning(self, 'Warning', 'Please enter your name.')
            return
        if not email:
            QMessageBox.warning(self, 'Warning', 'Please enter your email address.')
            return
        if not message:
            QMessageBox.warning(self, 'Warning', 'Please enter your message.')
            return

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = 'Admin@mypocket.com'  # Replace with your own recipient email address
        msg['Subject'] = 'New message from ' + name

        # Add the message body to the email
        body = message
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        smtp_server = smtplib.SMTP('smtp-relay.sendinblue.com', 587)  # Replace with your own SMTP server and port
        smtp_server.starttls()
        smtp_server.login('abhinavtej.9a@gmail.com', 'CzqpQmPNKG9fOrB7')
        text = msg.as_string()
        smtp_server.sendmail(email, 'abhinavtej.9a@gmail.com', text)  # Replace with your own recipient email address
        smtp_server.quit()

        # Show a message box to confirm the email was sent
        QMessageBox.information(self, 'Email Sent', 'Your message has been sent.')
        self.close()

    def lowercase(self, text):
        try:
            email_input = self.sender()
            email_input.setText(text.lower())
        except NameError:
            pass


class Profile(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Profile")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = self.cursor.fetchone()

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('User Profile')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_profile)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # User Info
        user_layout = QVBoxLayout()
        self.name_label = QLabel(f'Name : {user[0]}')
        self.email_label = QLabel(f'Email : {user[1]}')
        self.password_button = QPushButton("Change Password")

        self.name_label.setStyleSheet("font-size: 16px;")
        self.email_label.setStyleSheet("font-size: 16px;")
        self.name_label.setScaledContents(True)
        self.email_label.setScaledContents(True)
        user_layout.addWidget(self.name_label)
        user_layout.addWidget(self.email_label)
        user_layout.addWidget(self.password_button)
        self.password_button.clicked.connect(self.password)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(user_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Password")

        # Create widgets
        password_label = QLabel("New Password:")
        password_input = QLineEdit()
        confirm_label = QLabel("Confirm Password:")
        confirm_input = QLineEdit()
        change_button = QPushButton("Change")
        change_button.clicked.connect(
            lambda: self.change(dialog, password_input.text(), confirm_input.text()))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        layout.addWidget(confirm_label)
        layout.addWidget(confirm_input)
        layout.addWidget(change_button)

        # Set the dialog layout and show it
        dialog.setLayout(layout)
        dialog.exec()

    def change(self, dialog, password, confirm):
        if not password.strip() or not confirm.strip():
            msg_box = QDialog(dialog)
            msg_box.setWindowTitle("Error")
            msg_label = QLabel("Fields are not empty.")
            layout = QVBoxLayout()
            layout.addWidget(msg_label)
            msg_box.setLayout(layout)
            msg_box.exec()
            return

        # Check that the passwords match
        if password != confirm:
            error_dialog = QDialog(dialog)
            error_dialog.setWindowTitle("Error")
            error_label = QLabel("Passwords do not match.")

            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        self.cursor.execute("UPDATE users SET password = ? WHERE email = ?", (password, self.email))
        self.connection.commit()
        error_dialog = QDialog(dialog)
        error_dialog.setWindowTitle("Success")
        error_label = QLabel("Passwords changed successfully.")
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        error_dialog.setLayout(layout)
        error_dialog.exec()
        dialog.accept()

    def close_profile(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()


class Category(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Category")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create the expenses table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS category (category_id INTEGER PRIMARY KEY, email TEXT, category TEXT)")

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Category')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_category)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Your Categories:")
        self.category_combo = QComboBox()

        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()

        # Extract category names from the result
        category_names = [category[0] for category in categories]
        self.category_combo.addItems(category_names)

        self.add_button = QPushButton("Add New Category")
        self.add_button.clicked.connect(self.add_category)
        self.remove_button = QPushButton("Remove Category")
        self.remove_button.clicked.connect(self.remove_category)

        # Create a layout and add widgets to it
        category_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        category_layout.addWidget(self.category_label)
        category_layout.addWidget(self.category_combo)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(category_layout)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def add_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.add_category = AddCategory(self.email)
        self.add_category.show()

    def remove_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.add_category = RemoveCategory(self.email)
        self.add_category.show()

    def close_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class AddCategory(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Add Category")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Add Category')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_add_category)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        button_layout = QVBoxLayout()
        self.category_label = QLabel("Category:")
        button_layout.addWidget(self.category_label)
        self.category_input = QLineEdit()
        button_layout.addWidget(self.category_input)

        self.add_button = QPushButton("Add Category")
        self.add_button.clicked.connect(self.add_category)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()
        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def add_category(self):
        category = self.category_input.text()

        self.cursor.execute("SELECT category FROM category WHERE email = ?", (self.email,))
        existing_categories = self.cursor.fetchall()
        category_names = [category[0] for category in existing_categories]

        if category in category_names:
            QMessageBox.warning(self, 'Warning', 'Category already exist')
        else:
            self.cursor.execute("INSERT INTO category (email, category) VALUES (?, ?)", (self.email, category))
            self.connection.commit()
            QMessageBox.information(self, 'Success', 'Category added successfully')

        self.category_input.clear()

    def close_add_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.category = Category(self.email)
        self.category.show()

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


class RemoveCategory(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Remove Category")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Remove Category')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_remove_category)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()

        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()

        # Extract category names from the result
        category_names = [category[0] for category in categories]
        self.category_combo.addItems(category_names)

        button_layout = QVBoxLayout()
        self.category_label = QLabel("Category:")
        button_layout.addWidget(self.category_label)
        button_layout.addWidget(self.category_combo)
        self.remove_button = QPushButton("Remove Category")
        self.remove_button.clicked.connect(self.remove_category)
        button_layout.addWidget(self.remove_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()
        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def remove_category(self):
        # Retrieve input values
        category = self.category_combo.currentText()

        # Delete expenses with the specified category and date
        self.cursor.execute("DELETE FROM category WHERE category=? AND email=?",
                            (category, self.email))
        self.connection.commit()

        QMessageBox.information(self, 'Success', 'Category removed successfully')

        # Clear input fields
        self.category_combo.setCurrentIndex(0)

    def close_remove_category(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.category = Category(self.email)
        self.category.show()

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


class Income(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Income")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create the expenses table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS income (email TEXT PRIMARY KEY, month TEXT, income REAL)")

        self.cursor.execute("SELECT * FROM income WHERE email = ?", (email,))
        income_user = self.cursor.fetchone()

        if income_user is None:
            self.cursor.execute("INSERT INTO income (email, month, income) VALUES (?, ?, ?)", (self.email, None, None))

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Income')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_income)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Income Info
        income_layout = QVBoxLayout()
        if income_user is not None:
            self.income_label = QLabel(f"Income (₹): {income_user[2]}")
            self.month_label = QLabel(f"Month: {income_user[1]}")
        else:
            self.income_label = QLabel("Income (₹): N/A")
            self.month_label = QLabel("Month: N/A")
        self.other_label = QLabel(f'Other Income - *Coming Soon')
        self.change_button = QPushButton("Change Income")
        self.change_button.clicked.connect(self.income)

        self.income_label.setStyleSheet("font-size: 16px;")
        self.other_label.setStyleSheet("font-size: 16px;")
        self.month_label.setStyleSheet("font-size: 16px;")
        self.month_label.setScaledContents(True)
        self.income_label.setScaledContents(True)
        income_layout.addWidget(self.income_label)
        income_layout.addWidget(self.month_label)
        income_layout.addWidget(self.change_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(income_layout)
        main_layout.addSpacing(60)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def close_income(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()

    def income(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Income")

        # Create widgets
        income_label = QLabel("Income (₹):")
        income_input = QLineEdit()
        change_button = QPushButton("Change")
        change_button.clicked.connect(
            lambda: self.change_income(dialog, income_input.text()))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(income_label)
        layout.addWidget(income_input)
        layout.addWidget(change_button)

        # Set the dialog layout and show it
        dialog.setLayout(layout)
        dialog.exec()

    def change_income(self, dialog, income):
        month = datetime.now().strftime('%m-%Y')

        self.cursor.execute("SELECT * FROM income WHERE email = ?", (self.email,))
        income_user = self.cursor.fetchone()

        try:
            income = float(income)
        except ValueError:
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Warning")
            error_label = QLabel("Please enter Numerical.")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        if income > 200000:
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Warning")
            error_label = QLabel("Income should not exceed 2 Lakh Rupees.")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            error_dialog.setLayout(layout)
            error_dialog.exec()
            return

        if month == income_user[1]:
            if income > 0:
                self.cursor.execute("UPDATE income SET income=? WHERE email=?", (income, self.email))
                self.connection.commit()
            else:
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Warning")
                error_label = QLabel("Please enter Positive Numerical.")
                layout = QVBoxLayout()
                layout.addWidget(error_label)
                error_dialog.setLayout(layout)
                error_dialog.exec()
                return
            dialog.accept()
        else:
            if income > 0:
                self.cursor.execute("UPDATE income SET income=?, month=? WHERE email=?", (income, month, self.email))
                self.connection.commit()
            else:
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Warning")
                error_label = QLabel("Please enter Positive Numerical.")
                layout = QVBoxLayout()
                layout.addWidget(error_label)
                error_dialog.setLayout(layout)
                error_dialog.exec()
                return
            dialog.accept()


class Expenses(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Expenses")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create the expenses table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS expenses (expense_id INTEGER PRIMARY KEY, date TEXT, month TEXT, email TEXT, category TEXT, expense REAL)")

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Expenses')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_expenses)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create a horizontal layout for buttons
        button_layout1 = QHBoxLayout()
        self.button1 = QPushButton("Add Expense")
        self.button1.clicked.connect(self.open_add_expense)
        self.button2 = QPushButton("Update Expense")
        self.button2.clicked.connect(self.open_update_expense)
        button_layout1.addWidget(self.button1)
        button_layout1.addWidget(self.button2)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(70)
        main_layout.addLayout(button_layout1)
        main_layout.addSpacing(60)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def close_expenses(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()

    def open_add_expense(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.add_expense = AddExpense(self.email)
        self.add_expense.show()

    def open_update_expense(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.update_expense = UpdateExpense(self.email)
        self.update_expense.show()


class AddExpense(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Expenses")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Add Expense')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_add_expense)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()
        # Extract category names from the result
        category_names = [category[0] for category in categories]

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(category_names)
        self.amount_label = QLabel("Amount Spent:")
        self.amount_input = QLineEdit()
        self.add_button = QPushButton("Add Expense")
        self.add_button.clicked.connect(self.add_expense)

        # Create a layout and add widgets to it
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.category_label)
        button_layout.addWidget(self.category_combo)
        button_layout.addWidget(self.amount_label)
        button_layout.addWidget(self.amount_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def add_expense(self):
        # Retrieve input values
        category = self.category_combo.currentText()
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, 'Warning', 'Please enter Numerical.')
            return
        email = self.email
        date = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%m-%Y')

        # Check if expense with the same category and date already exists
        self.cursor.execute("SELECT expense FROM expenses WHERE category=? AND email=? AND date=? AND month=?",
                            (category, email, date, month))
        existing_expense = self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(expense) FROM expenses WHERE email=? AND month=? AND category=?",
                            (email, month, category))
        total_expense = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT budget FROM budget WHERE email=? AND month=? AND category=?",
                            (email, month, category))
        budget = self.cursor.fetchone()

        if budget is None:
            QMessageBox.warning(self, 'Warning', 'Please Add Budget to this Category.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return

        if (total_expense + amount) > budget[0]:
            QMessageBox.warning(self, 'Warning', 'Your Expense is Exceeding your Budget.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return

        if existing_expense:
            existing_amount = existing_expense[0]
            # Add the new amount to the existing expense
            if amount > 0:
                amount += existing_amount
                # Update the existing expense in the database with the new amount and time
                self.cursor.execute("UPDATE expenses SET expense=? WHERE category=? AND email=? AND date=? AND month=?",
                                    (amount, category, email, date, month))
                QMessageBox.information(self, 'Success', 'Expense added successfully')
            else:
                QMessageBox.warning(self, 'Warning', 'Please enter Positive Numerical.')

        else:
            # Insert a new expense into the database
            self.cursor.execute(
                "INSERT INTO expenses (date, month, email, category, expense) VALUES (?, ?, ?, ?, ?)",
                (date, month, email, category, amount))
            QMessageBox.information(self, 'Success', 'Expense added successfully')
        self.connection.commit()

        # Clear input fields
        self.category_combo.setCurrentIndex(0)
        self.amount_input.clear()

    def close_add_expense(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.expenses = Expenses(self.email)
        self.expenses.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class UpdateExpense(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Expenses")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Update Expense')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_update_expense)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()
        # Extract category names from the result
        category_names = [category[0] for category in categories]
        self.category_combo.addItems(category_names)
        self.amount_label = QLabel("Amount Spent:")
        self.amount_input = QLineEdit()
        self.add_button = QPushButton("Update Expense")
        self.add_button.clicked.connect(
            lambda: self.update_expense(self.email, self.category_combo.currentText())
        )

        # Create a layout and add widgets to it
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.category_label)
        button_layout.addWidget(self.category_combo)
        button_layout.addWidget(self.amount_label)
        button_layout.addWidget(self.amount_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def update_expense(self, email, category):
        try:
            new_amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, 'Warning', 'Please enter Numerical.')
            return
        # Retrieve today's date and current time
        date = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%m-%Y')

        # Check if expense with the same category and date already exists
        self.cursor.execute("SELECT expense FROM expenses WHERE category=? AND email=? AND date=? AND month=?",
                            (category, email, date, month))
        existing_expense = self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(expense) FROM expenses WHERE email=? AND month=? AND category=?",
                            (email, month, category))
        total_expense = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT expense FROM expenses WHERE email=? AND month=? AND category=? AND date=?",
                            (email, month, category, date))
        today_expense = self.cursor.fetchone()

        self.cursor.execute("SELECT budget FROM budget WHERE email=? AND month=? AND category=?",
                            (email, month, category))
        budget = self.cursor.fetchone()

        if existing_expense is None or today_expense is None or budget is None:
            QMessageBox.warning(self, 'Warning', 'Please add Expense/Budget to update.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return

        if new_amount > (budget[0] - (total_expense - today_expense[0])):
            QMessageBox.warning(self, 'Warning', 'Your Expense is Exceeding your Budget.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return
        else:
            # Update the existing expense for today's date and change the time
            if new_amount >= 0:
                self.cursor.execute("UPDATE expenses SET expense=? WHERE email=? AND category=? AND date=? AND month=?",
                                    (new_amount, email, category, date, month))
                self.connection.commit()
                QMessageBox.information(self, 'Success', 'Expense updated successfully')
            else:
                QMessageBox.warning(self, 'Warning', 'Please enter Positive Numerical.')

            # Clear input fields
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()

    def close_update_expense(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.expenses = Expenses(self.email)
        self.expenses.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class BudgetPlanner(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Budget Planner")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create the expenses table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS budget (budget_id INTEGER PRIMARY KEY, month TEXT, email TEXT, category TEXT, budget REAL)")

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Budget Planner')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_budget_planner)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        self.cursor.execute("SELECT SUM(budget), month FROM budget WHERE email = ?", (email,))
        budget_user = self.cursor.fetchone()

        budget_layout = QVBoxLayout()
        if budget_user is not None:
            self.budget_label = QLabel(f"Budget (₹): {budget_user[0]}")
            self.month_label = QLabel(f"Month: {budget_user[1]}")
        else:
            self.budget_label = QLabel("Income (₹): N/A")
            self.month_label = QLabel("Month: N/A")
        self.budget_label.setStyleSheet("font-size: 16px;")
        self.month_label.setStyleSheet("font-size: 16px;")
        self.month_label.setScaledContents(True)
        self.budget_label.setScaledContents(True)
        budget_layout.addWidget(self.budget_label)
        budget_layout.addWidget(self.month_label)

        # Create a horizontal layout for buttons
        button_layout1 = QHBoxLayout()

        self.button1 = QPushButton("Add Budget")
        self.button1.clicked.connect(self.open_add_budget)
        self.button2 = QPushButton("Update Budget")
        self.button2.clicked.connect(self.open_update_budget)
        button_layout1.addWidget(self.button1)
        button_layout1.addWidget(self.button2)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(budget_layout)
        main_layout.addLayout(button_layout1)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def close_budget_planner(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()

    def open_add_budget(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.add_budget = AddBudget(self.email)
        self.add_budget.show()

    def open_update_budget(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.update_budget = UpdateBudget(self.email)
        self.update_budget.show()


class AddBudget(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Budget Planner")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Add Budget')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_add_budget)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()
        # Extract category names from the result
        category_names = [category[0] for category in categories]
        self.category_combo.addItems(category_names)
        self.amount_label = QLabel("Budget Amount:")
        self.amount_input = QLineEdit()
        self.add_button = QPushButton("Add Budget")
        self.add_button.clicked.connect(self.add_budget)

        # Create a layout and add widgets to it
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.category_label)
        button_layout.addWidget(self.category_combo)
        button_layout.addWidget(self.amount_label)
        button_layout.addWidget(self.amount_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def add_budget(self):
        # Retrieve input values
        category = self.category_combo.currentText()
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, 'Warning', 'Please enter Numerical.')
            return
        email = self.email
        month = datetime.now().strftime('%m-%Y')

        # Check if expense with the same category and date already exists
        self.cursor.execute("SELECT budget FROM budget WHERE category=? AND email=? AND month=?",
                            (category, email, month))
        existing_budget = self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(budget) FROM budget WHERE email=? AND month=?",
                            (email, month))
        total_budget = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT income FROM income WHERE email=? AND month=?",
                            (email, month))
        income = self.cursor.fetchone()

        if (total_budget + amount) > income[0]:
            QMessageBox.warning(self, 'Warning', 'Your budget is Exceeding your Income.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return

        if existing_budget:
            existing_budget = existing_budget[0]
            # Add the new amount to the existing expense
            if amount > 0:
                amount += existing_budget
                # Update the existing expense in the database with the new amount and time
                self.cursor.execute("UPDATE budget SET budget=? WHERE category=? AND email=? AND month=?",
                                    (amount, category, email, month))
                QMessageBox.information(self, 'Success', 'Budget added successfully')
            else:
                QMessageBox.warning(self, 'Warning', 'Please enter Positive Numerical.')

        else:
            # Insert a new expense into the database
            self.cursor.execute(
                "INSERT INTO budget (month, email, category, budget) VALUES (?, ?, ?, ?)",
                (month, email, category, amount))
            QMessageBox.information(self, 'Success', 'Budget added successfully')

        self.connection.commit()

        # Clear input fields
        self.category_combo.setCurrentIndex(0)
        self.amount_input.clear()

    def close_add_budget(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.budget_planner = BudgetPlanner(self.email)
        self.budget_planner.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class UpdateBudget(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Budget Planner")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Update Budget')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_update_budget)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create widgets for category, amount, and buttons
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        # Retrieve categories from the table
        self.cursor.execute("SELECT category FROM category WHERE email = ?", (email,))
        categories = self.cursor.fetchall()
        # Extract category names from the result
        category_names = [category[0] for category in categories]
        self.category_combo.addItems(category_names)
        self.amount_label = QLabel("Budget Amount:")
        self.amount_input = QLineEdit()
        self.add_button = QPushButton("Update Budget")
        self.add_button.clicked.connect(
            lambda: self.update_budget(self.email, self.category_combo.currentText())
        )

        # Create a layout and add widgets to it
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.category_label)
        button_layout.addWidget(self.category_combo)
        button_layout.addWidget(self.amount_label)
        button_layout.addWidget(self.amount_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def update_budget(self, email, category):
        try:
            new_amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, 'Warning', 'Please enter Numerical.')
            return
        # Retrieve today's date and current time
        month = datetime.now().strftime('%m-%Y')

        # Check if expense with the same category and date already exists
        self.cursor.execute("SELECT budget FROM budget WHERE category=? AND email=? AND month=?",
                            (category, email, month))
        existing_budget = self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(budget) FROM budget WHERE email=? AND month=?",
                            (email, month))
        total_budget = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT budget FROM budget WHERE email=? AND month=? AND category=?",
                            (email, month, category))
        category_budget = self.cursor.fetchone()

        self.cursor.execute("SELECT income FROM income WHERE email=? AND month=?",
                            (email, month))
        income = self.cursor.fetchone()

        if existing_budget is None:
            QMessageBox.warning(self, 'Warning', 'Please add Expense to update.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return

        if new_amount > income[0] - (total_budget - category_budget[0]):
            QMessageBox.warning(self, 'Warning', 'Your budget is Exceeding your Income.')
            self.category_combo.setCurrentIndex(0)
            self.amount_input.clear()
            return
        else:
            # Update the existing expense for today's date and change the time
            if new_amount >= 0:
                self.cursor.execute("UPDATE budget SET budget=? WHERE email=? AND category=? AND month=?",
                                    (new_amount, email, category, month))
                QMessageBox.information(self, 'Success', 'Budget updated successfully')

                self.connection.commit()
            else:
                QMessageBox.warning(self, 'Warning', 'Please enter Positive Numerical.')

        # Clear input fields
        self.category_combo.setCurrentIndex(0)
        self.amount_input.clear()

    def close_update_budget(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.budget_planner = BudgetPlanner(self.email)
        self.budget_planner.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()

class Reports(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Reports")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Reports')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_reports)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create a horizontal layout for buttons
        button_layout1 = QHBoxLayout()
        self.button1 = QPushButton("Daily Report")
        self.button2 = QPushButton("Monthly Report")
        self.button1.clicked.connect(self.open_daily_reports)
        self.button2.clicked.connect(self.open_monthly_reports)
        button_layout1.addWidget(self.button1)
        button_layout1.addWidget(self.button2)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(40)
        main_layout.addLayout(button_layout1)
        main_layout.addSpacing(70)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def close_reports(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.home = Home(self.email)
        self.home.show()

    def open_daily_reports(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.daily_reports = DailyReports(self.email)
        self.daily_reports.show()

    def open_monthly_reports(self):
        # Close the current window
        self.close()
        # Open a new instance of the Add Budget window
        self.monthly_reports = MonthlyReports(self.email)
        self.monthly_reports.show()


class DailyReports(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Reports")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Daily Report')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_daily_reports)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create a date input box
        self.date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setMinimumDate(QDate(2000, 1, 1))
        self.date_input.setMaximumDate(QDate(2099, 12, 31))
        # Set the calendar popup to the QDateEdit
        self.date_input.setCalendarPopup(True)
        self.add_button = QPushButton("Download Report")
        self.add_button.clicked.connect(self.generate_daily_report)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.date_label)
        button_layout.addWidget(self.date_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def generate_daily_report(self):
        # Retrieve input values
        date = self.date_input.date().toString("yyyy-MM-dd")

        # Retrieve user details from the database
        self.cursor.execute("SELECT name FROM users WHERE email=?", (self.email,))
        user = self.cursor.fetchone()
        name = user[0]

        # Retrieve daily expenses for the user from the database
        self.cursor.execute("SELECT category, expense FROM expenses WHERE email=? AND date=?", (self.email, date))
        expenses = self.cursor.fetchall()

        # Prepare data for the graph
        categories = []
        amounts = []
        for expense in expenses:
            category = expense[0]
            amount = expense[1]
            categories.append(category)
            amounts.append(amount)

        # Create a bar graph
        plt.bar(categories, amounts, label='Expense')
        plt.xlabel("Categories")
        plt.ylabel("Amount (₹)")
        plt.title("Daily Expense Report for {} - {}".format(name, date))

        plt.legend()
        filename = f"daily_report-{date}.pdf"
        plt.savefig(filename)
        plt.close()

        QMessageBox.information(self, 'Success', 'Daily Report Downloaded.')

        self.date_input.setDate(QDate.currentDate())

    def close_daily_reports(self):
        # Close the current window
        self.close()
        # Open a new instance of the login window
        self.reports = Reports(self.email)
        self.reports.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


class MonthlyReports(QMainWindow):
    def __init__(self, email):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("Reports")
        self.setFixedSize(300, 400)

        # Connect to the users database and check if user exists
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.email = email

        # Create a vertical layout for the logo and title
        logo_layout = QVBoxLayout()

        # Add the logo to the layout
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(100, 100)
        logo_layout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignCenter)

        # Add a stretch to decrease the space between the logo and title
        logo_layout.addStretch()

        # Add the title to the layout
        self.title_label = QLabel('Monthly Report')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setScaledContents(True)
        logo_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Logout Button
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.close_monthly_reports)

        # Create a horizontal layout for the logout button and add it to the main layout
        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        # Create a date input box
        self.month_label = QLabel("Month:")
        self.month_input = QDateEdit()
        self.month_input.setDisplayFormat("MM/yyyy")
        self.month_input.setMinimumDate(QDate(2000, 1, 1))
        self.month_input.setMaximumDate(QDate(2099, 12, 31))
        # Set the calendar popup to the QDateEdit
        self.month_input.setCalendarPopup(True)
        self.add_button = QPushButton("Download Report")
        self.add_button.clicked.connect(self.generate_monthly_report)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.month_label)
        button_layout.addWidget(self.month_input)
        button_layout.addWidget(self.add_button)

        # Create a vertical layout for the logo, title and buttons
        main_layout = QVBoxLayout()

        # Add the logo, title and buttons layouts to the main layout
        main_layout.addLayout(back_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)

        # Set the main layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def generate_monthly_report(self):
        # Retrieve input values
        month = self.month_input.date().toString("MM-yyyy")

        # Retrieve user details from the database
        self.cursor.execute("SELECT name FROM users WHERE email=?", (self.email,))
        user_details = self.cursor.fetchone()
        name = user_details[0]

        self.cursor.execute("SELECT category FROM category WHERE email=?",
                            (self.email,))
        month_category = self.cursor.fetchall()

        # Prepare data for the graph
        categories = [category[0] for category in month_category]
        expenses = []
        budgets = []

        for category in categories:
            self.cursor.execute("SELECT budget FROM budget WHERE email=? AND month=? AND category=?",
                                (self.email, month, category))
            budget = self.cursor.fetchone()
            if budget is not None:  # Check for None value
                budgets.append(budget[0])
            else:
                budgets.append(0)  # Assign a default value for missing budget

            self.cursor.execute("SELECT SUM(expense) FROM expenses WHERE email=? AND month=? AND category=?",
                                (self.email, month, category))
            month_expense = self.cursor.fetchone()
            if month_expense[0] is not None:  # Check for None value
                expenses.append(month_expense[0])
            else:
                expenses.append(0)

        # Generate x-axis positions for each category
        x = np.arange(len(categories))

        # Set the width of each bar
        bar_width = 0.35

        # Plot the bars for expense
        plt.bar(x, budgets, width=bar_width, label='Budget')

        # Plot the bars for budget
        plt.bar(x + bar_width, expenses, width=bar_width, label='Expense')

        # Set the x-axis ticks and labels
        plt.xticks(x + bar_width / 2, categories)

        # Set labels and title
        plt.xlabel("Categories")
        plt.ylabel("Amount (₹)")
        plt.title("Monthly Expense Report for {} - {}".format(name, month))

        # Add a legend & Display the plot
        plt.legend()
        filename = f"monthly_report-{month}.pdf"
        plt.savefig(filename)
        plt.close()

        QMessageBox.information(self, 'Success', 'Monthly Report Downloaded.')

        self.month_input.setDate(QDate.currentDate())

    def close_monthly_reports(self):
        # Close the current window
        self.close()
        self.reports = Reports(self.email)
        self.reports.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Create and show the login page
    login = LoginPage()
    login.show()
    sys.exit(app.exec())
