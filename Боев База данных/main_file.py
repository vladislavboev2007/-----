import sqlite3
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView

import main_window

DB_PATH = r"Автосалон.db"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        # Заменяем QListView на QTableView
        self.tableView = QTableView(self.ui.gridLayoutWidget)
        self.ui.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.ui.listView_2.hide()  # Скрываем старый listView

        # Подключаем кнопки к функциям
        self.ui.pushButton_2.clicked.connect(self.find_ticket)
        self.ui.pushButton_6.clicked.connect(self.sort_descending)
        self.ui.pushButton.clicked.connect(self.sort_ascending)
        self.ui.pushButton_3.clicked.connect(self.add_ticket)
        self.ui.pushButton_4.clicked.connect(self.delete_ticket)

        # Загружаем данные при старте
        self.load_data()

    def load_data(self, query=None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            if query:
                cursor.execute(query)
            else:
                cursor.execute("""
                    SELECT a.Id_автомобиля, a.Модель, a.Стоимость, m.Наименование, m.Страна
                    FROM Автомобили a
                    JOIN Производители m ON a.Id_производителя = m.Id_производителя
                    ORDER BY a.Стоимость
                """)

            rows = cursor.fetchall()
            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")
        finally:
            conn.close()

    def display_data(self, rows):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Модель", "Стоимость", "Производитель", "Страна производителя"])

        for row in rows:
            items = [QtGui.QStandardItem(str(item)) for item in row]
            model.appendRow(items)

        self.tableView.setModel(model)
        # Настраиваем ширину столбцов
        self.tableView.setColumnWidth(0, 50)  # ID
        self.tableView.setColumnWidth(1, 150)  # Модель
        self.tableView.setColumnWidth(2, 150)  # Стоимость
        self.tableView.setColumnWidth(3, 120)  # Производитель
        self.tableView.setColumnWidth(4, 160)  # Страна производителя

    def find_ticket(self):
        search_text = self.ui.textEdit_2.toPlainText().strip()
        if not search_text:
            self.load_data()
            return

        query = f"""
            SELECT a.Id_автомобиля, a.Модель, a.Стоимость, m.Наименование, m.Страна
            FROM Автомобили a
            JOIN Производители m ON a.Id_производителя = m.Id_производителя
            WHERE a.Модель LIKE '%{search_text}%' OR m.Наименование LIKE '%{search_text}%'
            ORDER BY a.Стоимость
        """
        self.load_data(query)

    def sort_ascending(self):
        self.load_data("""
            SELECT a.Id_автомобиля, a.Модель, a.Стоимость, m.Наименование, m.Страна 
            FROM Автомобили a
            JOIN Производители m ON a.Id_производителя = m.Id_производителя
            ORDER BY a.Стоимость ASC
        """)

    def sort_descending(self):
        self.load_data("""
            SELECT a.Id_автомобиля, a.Модель, a.Стоимость, m.Наименование, m.Страна 
            FROM Автомобили a
            JOIN Производители m ON a.Id_производителя = m.Id_производителя
            ORDER BY a.Стоимость DESC
        """)

    def add_ticket(self):
        conn = None
        try:
            model = self.ui.textEdit_4.toPlainText().strip()
            price = float(self.ui.textEdit.toPlainText().strip())
            manufacturer = self.ui.textEdit_3.toPlainText().strip()

            if not all([model, manufacturer]):
                raise ValueError("Все поля должны быть заполнены")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Получаем ID вида транспорта
            cursor.execute("SELECT Id_производителя FROM Производители WHERE Наименование = ?", (manufacturer,))
            manufacture_id = cursor.fetchone()

            if not manufacture_id:
                raise ValueError("Указанный производитель не найден")

            # Добавляем новое направление
            cursor.execute("""
                INSERT INTO Автомобили (Модель, Стоимость, Id_производителя)
                VALUES (?, ?, ?)
            """, (model, price, manufacture_id[0]))

            conn.commit()
            QMessageBox.information(self, "Успех", "Автомобиль успешно добавлен")
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении билета: {str(e)}")
        finally:
            if conn:
                conn.close()

    def delete_ticket(self):
        selected = self.tableView.currentIndex()
        if not selected.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите билет для удаления")
            return

        conn = None
        try:
            model = self.tableView.model()
            ticket_id = model.data(model.index(selected.row(), 0))

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Автомобили WHERE Id_автомобиля = ?", (ticket_id,))
            conn.commit()

            QMessageBox.information(self, "Успех", "Автомобиль успешно удален")
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении автомобиля: {str(e)}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())