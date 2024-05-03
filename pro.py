import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import simpledialog, messagebox, Text, ttk
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar module
from tkinter import IntVar

class Student:
    def __init__(self, name, roll_number):
        self.name = name
        self.roll_number = roll_number
        self.attendance = {}

    def mark_attendance(self, date, status):
        self.attendance[date] = status

    def view_attendance(self):
        return self.attendance

class AttendanceSystem:
    def __init__(self):
        self.students = {}
        self.connection = None
        self.cursor = None
        self.fetch_data()

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Reddy@12",
                database="attendance",
                auth_plugin='caching_sha2_password'
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error: {e}")

    def fetch_data(self):
        self.connect_to_database()
        try:
            self.cursor.execute("SELECT roll_number, name FROM students")
            students_data = self.cursor.fetchall()
            for roll_number, name in students_data:
                student = Student(name, roll_number)
                self.students[roll_number] = student

            self.cursor.execute("SELECT roll_number, date, status FROM attendance")
            attendance_data = self.cursor.fetchall()
            for roll_number, date, status in attendance_data:
                if roll_number in self.students:
                    self.students[roll_number].mark_attendance(date, status)

        except Error as e:
            print(f"Error fetching data: {e}")
        finally:
            self.close_connection()

    def add_student(self, student):
        self.connect_to_database()
        try:
            query = "INSERT INTO students (name, roll_number) VALUES (%s, %s)"
            values = (student.name, student.roll_number)
            self.cursor.execute(query, values)
            self.connection.commit()

            self.students[student.roll_number] = student
            messagebox.showinfo("Success", "Student added successfully.")
        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.close_connection()

    def mark_attendance(self, roll_number, date, status):
        self.connect_to_database()
        try:
            if roll_number in self.students:
                self.students[roll_number].mark_attendance(date, status)

                query = "INSERT INTO attendance (roll_number, date, status) VALUES (%s, %s, %s)"
                values = (roll_number, date, status)
                self.cursor.execute(query, values)
                self.connection.commit()

                messagebox.showinfo("Success", "Attendance marked successfully.")
            else:
                messagebox.showerror("Error", "Student not found.")
        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.close_connection()

    def view_student_attendance(self, roll_number, text_widget):
        self.connect_to_database()
        try:
            if roll_number in self.students:
                student = self.students[roll_number]
                attendance_data = student.view_attendance()

                if not attendance_data:
                    text_widget.insert(tk.END, "No attendance data available for the student.")
                else:
                    student_info = f"{student.name} - Roll Number: {student.roll_number}"
                    attendance_str = "\n".join([f"{date}: {status}" for date, status in attendance_data.items()])
                    text_widget.insert(tk.END, f"{student_info}\n\nAttendance:\n{attendance_str}\n")
            else:
                messagebox.showerror("Error", "Student not found.")
        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.close_connection()

    def calculate_attendance_percentage(self, roll_number):
        self.connect_to_database()
        try:
            if roll_number in self.students:
                student = self.students[roll_number]
                total_classes = len(student.attendance)
                present_classes = sum(1 for status in student.attendance.values() if status.lower() == 'present')

                if total_classes == 0:
                    messagebox.showinfo("Info", "No attendance data available for the student.")
                else:
                    attendance_percentage = (present_classes / total_classes) * 100
                    messagebox.showinfo("Attendance Percentage", f"Attendance Percentage for {student.name} (Roll Number: {student.roll_number}): {attendance_percentage:.2f}%")
            else:
                messagebox.showerror("Error", "Student not found.")
        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.close_connection()

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Connection to MySQL database closed")

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Attendance Management System")

        # Adding heading for Vikash Degree College, Bargarh
        self.heading_label = ttk.Label(self, text="Vikash Degree College, Bargarh", font=("Helvetica", 18, "bold"))
        self.heading_label.pack(pady=10)

        # Add logo image
        self.logo_image = tk.PhotoImage(file="logo.png")
        self.label_logo = tk.Label(self, image=self.logo_image)
        self.label_logo.pack(pady=10)

        self.attendance_system = AttendanceSystem()

        self.menu_label = ttk.Label(self, text="Vikash Diploma Attendance System", font=("Helvetica", 16))
        self.menu_label.pack(pady=10)

        self.menu_buttons = []
        button_texts = ["Add Student", "Mark Attendance", "View Student Attendance", "Calculate Attendance Percentage", "Exit"]
        for text in button_texts:
            button = ttk.Button(self, text=text, command=lambda t=text: self.handle_menu_click(t))
            button.pack(pady=5, padx=10)
            

    def handle_menu_click(self, choice):

        if choice == "Add Student":
            name, roll_number = self.take_student_data()
            student = Student(name, roll_number)
            self.attendance_system.add_student(student)
        elif choice == "Mark Attendance":
            self.mark_attendance()
        elif choice == "View Student Attendance":
            roll_number = simpledialog.askstring("Input", "Enter the student's roll number:")
            self.view_student_attendance(roll_number)
        elif choice == "Calculate Attendance Percentage":
            roll_number = simpledialog.askstring("Input", "Enter the student's roll number:")
            self.attendance_system.calculate_attendance_percentage(roll_number)
        elif choice == "Exit":
            self.destroy()


    def mark_attendance(self):
        mark_attendance_window = tk.Toplevel(self)
        mark_attendance_window.title("Mark Attendance")
        

        roll_number_label = ttk.Label(mark_attendance_window, text="Enter the student's roll number:")
        roll_number_label.pack(pady=5)

        roll_number_entry = ttk.Entry(mark_attendance_window)
        roll_number_entry.pack(pady=5)

        date_label = ttk.Label(mark_attendance_window, text="Select the date:")
        date_label.pack(pady=5)

        # Use DateEntry widget for date selection
        date_entry = DateEntry(mark_attendance_window, date_pattern="yyyy-mm-dd", width=12)
        date_entry.pack(pady=5)

        status_label = ttk.Label(mark_attendance_window, text="Select attendance status:")
        status_label.pack(pady=5)

        status_var = tk.StringVar()

        present_radio = ttk.Radiobutton(mark_attendance_window, text="Present", variable=status_var, value="Present")
        present_radio.pack(pady=5)

        absent_radio = ttk.Radiobutton(mark_attendance_window, text="Absent", variable=status_var, value="Absent")
        absent_radio.pack(pady=5)

        submit_button = ttk.Button(mark_attendance_window, text="Submit", command=lambda: self.submit_attendance(roll_number_entry.get(), date_entry.get(), status_var.get()))
        submit_button.pack(pady=10)

    def submit_attendance(self, roll_number, date, status):
        self.attendance_system.mark_attendance(roll_number, date, status)
        messagebox.showinfo("Success", "Attendance marked successfully.")

    def take_student_data(self):
        name = simpledialog.askstring("Input", "Enter the student's name:")
        roll_number = simpledialog.askstring("Input", "Enter the student's roll number:")
        return name, roll_number

    def view_student_attendance(self, roll_number):
        view_attendance_window = tk.Toplevel(self)
        view_attendance_window.title("View Student Attendance")

        text_widget = Text(view_attendance_window, wrap=tk.WORD)
        text_widget.pack(padx=10, pady=10)

        self.attendance_system.view_student_attendance(roll_number, text_widget)

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
