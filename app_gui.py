from tkinter import Tk, Button, filedialog, Text, Frame, Canvas, BOTH, LEFT, RIGHT, Scrollbar, Y, messagebox, StringVar, Toplevel
from tkinter.ttk import Combobox, Label
from PIL import ImageTk, Image
import os
import ocr_logic  
import pre_processing  
import pandas as pd
from tkinter import filedialog, messagebox
import subprocess

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng trích xuất thông tin hóa đơn ")
        self.root.geometry("1920x1080")  

        # Biến lưu đường dẫn
        self.file_path = None
        self.json_path = None
        self.img = None
        self.photo = None

        # Ngôn ngữ OCR
        self.selected_language = 'vi'  # Mặc định ngôn ngữ là tiếng Viet

        # Khung chính của ứng dụng
        self.main_frame = Frame(root, bg="#f7f7f7")
        self.main_frame.pack(fill=BOTH, expand=True)

        # Khung chọn file và nút trích xuất
        self.button_frame = Frame(self.main_frame, bg="#f7f7f7")
        self.button_frame.pack(side="top", pady=20)

        # Combobox chọn mẫu hóa đơn
        self.invoice_label = Label(self.button_frame, text="Chọn mẫu hóa đơn", font=("Times New Roman", 16))
        self.invoice_label.pack(side=LEFT, padx=10)

        self.json_combobox = Combobox(self.button_frame, state="readonly", font=("Times New Roman", 14))
        self.populate_json_combobox()  
        self.json_combobox.pack(side=LEFT, padx=10)
        self.json_combobox.bind("<<ComboboxSelected>>", self.on_json_selected)

        # Nút chọn file ảnh
        self.select_button = Button(self.button_frame, text="Chọn file ảnh", font=("Times New Roman", 16), bg="#2196F3", fg="white", relief="flat", width=20, height=2, command=self.choose_file)
        self.select_button.pack(side=LEFT, padx=10)

        # Nút trích xuất
        self.extract_button = Button(self.button_frame, text="Trích xuất", font=("Times New Roman", 16), bg="#00ff0d", fg="white", relief="flat", width=20, height=2, command=self.process_image)
        self.extract_button.pack(side=LEFT, padx=10)

        # Combobox chọn ngôn ngữ
        self.language_label = Label(self.button_frame, text="Chọn ngôn ngữ OCR", font=("Times New Roman", 16))
        self.language_label.pack(side=LEFT, padx=10)

        self.language_combobox = Combobox(self.button_frame, values=['en', 'vi', 'zh', 'ja', 'ko', 'fr'], state="readonly", font=("Times New Roman", 14))
        self.language_combobox.set(self.selected_language)  # Set ngôn ngữ mặc định là 'vi'
        self.language_combobox.pack(side=LEFT, padx=10)

        # Khung hiển thị ảnh 
        self.image_frame = Frame(self.main_frame, bg="#e0e0e0", width=1056, height=1408)  
        self.image_frame.pack(side=LEFT, fill="both", expand=True, padx=10, pady=10)

        self.canvas = Canvas(self.image_frame, bg="white")
        self.canvas.pack(fill=BOTH, expand=True, side=LEFT)

        # Thanh cuộn dọc
        scrollbar = Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Khung hiển thị kết quả OCR
        self.result_frame = Frame(self.main_frame, bg="#ffffff", width=576) 
        self.result_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        # Tạo một frame riêng để chứa các nút "Chỉnh sửa" và "Xuất File"
        self.button_frame_result = Frame(self.result_frame, bg="#ffffff")
        self.button_frame_result.pack(side="top", anchor="ne", padx=10, pady=10)

        # Nút "Chỉnh sửa"
        self.edit_button = Button(self.button_frame_result, 
        text="Chỉnh sửa", font=("Times New Roman", 14), bg="#FFCC00", fg="black", relief="flat", command=self.enable_editing)
        self.edit_button.pack(side="left", padx=5)

        # Nút "Xuất File"
        self.export_button = Button(self.button_frame_result, 
        text="Xuất File", font=("Times New Roman", 14), bg="#00A8E8", fg="white", relief="flat", command=self.show_export_dialog)
        self.export_button.pack(side="left", padx=5)

        # Widget Text hiển thị kết quả OCR
        self.result_text = Text(self.result_frame, wrap="word", font=("Times New Roman", 14), bg="#f7f7f7", state="disabled", bd=2, relief="sunken")
        self.result_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def enable_editing(self):
        self.result_text.config(state="normal")

    def show_export_dialog(self):
        # Tạo một cửa sổ con (Toplevel) để cho người dùng chọn định dạng xuất file
        dialog = Toplevel(self.root)
        dialog.title("Chọn định dạng xuất file")
        dialog.geometry("300x150")

        # Label hướng dẫn
        label = Label(dialog, text="Chọn định dạng xuất file:", font=("Times New Roman", 14))
        label.pack(pady=10)

        # ComboBox cho phép chọn định dạng xuất
        self.export_format_combobox = Combobox(dialog, values=["Text"], state="readonly", font=("Times New Roman", 14))
        self.export_format_combobox.set("Text")  # Đặt mặc định là Text
        self.export_format_combobox.pack(pady=10)

        # Nút "OK" để xác nhận lựa chọn
        ok_button = Button(dialog, text="OK", font=("Times New Roman", 14), bg="#2196F3", fg="white", relief="flat", command=lambda: self.export_file(dialog))
        ok_button.pack(pady=10)

    def export_file(self, dialog):
        # Đóng cửa sổ lựa chọn định dạng
        dialog.destroy()

        # Chọn đường dẫn lưu file
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        if not file_path:
            return
        try:
            content = self.result_text.get("1.0", "end-1c")  # Lấy nội dung từ Text widget
            
            # Ghi nội dung vào file văn bản
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("Xuất File", f"Đã xuất file thành công tại: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")

    def populate_json_combobox(self):
        try:
            json_directory = "./Mẫu hóa đơn"  # Đường dẫn đến thư mục chứa mẫu hóa đơn
            json_files = [file for file in os.listdir(json_directory) if file.endswith('.json')]
            if not json_files:
                json_files.append("No JSON files found")
            self.json_combobox['values'] = ["Tạo mới mẫu hóa đơn"] + json_files  # Thêm mục Tạo mới
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi tải JSON files: {e}")


    def on_json_selected(self, event):
        selected_file = self.json_combobox.get()
        if selected_file == "Tạo mới mẫu hóa đơn":
            try:
                subprocess.run(["labelme"], check=True)  # Chạy Labelme
            except FileNotFoundError:
                messagebox.showerror("Lỗi", "Labelme không được cài đặt hoặc không tìm thấy!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở Labelme: {e}")
        elif selected_file and selected_file != "No JSON files found":
            json_directory = "./Mẫu hóa đơn"  # Thư mục chứa các tệp hóa đơn
            self.json_path = os.path.join(json_directory, selected_file)  # Chuẩn hóa đường dẫn
            if os.path.exists(self.json_path):
                messagebox.showinfo("Thông báo", f"Đã chọn tệp JSON: {self.json_path}")
            else:
                messagebox.showerror("Lỗi", f"Tệp JSON không tồn tại: {self.json_path}")
                self.json_path = None
        else:
            self.json_path = None
            messagebox.showwarning("Cảnh báo", "Chưa chọn tệp JSON nào!")


    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.file_path:
            self.img = Image.open(self.file_path)
            self.original_img_width, self.original_img_height = self.img.size  # Lưu kích thước ảnh gốc
            self.load_image()

    def load_image(self):
        # Nếu ảnh đã được chọn
        if self.file_path:
            self.img = Image.open(self.file_path)

            # Lấy kích thước widget chứa ảnh
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()

            # Lấy kích thước ảnh gốc
            img_width, img_height = self.img.size

            # Tính tỷ lệ để ảnh vừa với widget
            scale = min(frame_width / img_width, frame_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # Resize ảnh
            resized_img = self.img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_img)

            
            self.canvas.delete("all")
            self.canvas.create_image((frame_width - new_width) // 2, (frame_height - new_height) // 2, image=self.photo, anchor="nw")
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def process_image(self):
        # Kiểm tra nếu file JSON chưa được chọn
        if not self.json_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn tệp JSON trước khi trích xuất!")
            return

        # Kiểm tra nếu file ảnh chưa được chọn
        if not self.file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file ảnh trước khi trích xuất!")
            return

        # Tiền xử lý ảnh: thay đổi kích thước và làm nét
        try:
            preprocessed_image = pre_processing.sharpen_image(self.file_path)
            preprocessed_image.save("processed_image.png")  
        except Exception as e:
            messagebox.showerror("Lỗi", f"Tiền xử lý ảnh thất bại: {e}")
            return

        # Gọi hàm xử lý OCR với ngôn ngữ đã chọn
        try:
            annotated_image, results = ocr_logic.process_ocr_from_json(
                "processed_image.png", self.json_path, [self.selected_language]
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Xử lý OCR thất bại: {e}")
            return

        # Lấy kích thước của ảnh trích xuất và widget chứa ảnh
        annotated_img_width, annotated_img_height = annotated_image.size
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        # Tính toán tỷ lệ để ảnh trích xuất vừa với widget
        scale = min(frame_width / annotated_img_width, frame_height / annotated_img_height)
        new_width = int(annotated_img_width * scale)
        new_height = int(annotated_img_height * scale)

        # Resize ảnh trích xuất
        resized_annotated_img = annotated_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_annotated_img)

        # Căn giữa ảnh trích xuất trong widget
        self.canvas.delete("all")
        self.canvas.create_image((frame_width - new_width) // 2, (frame_height - new_height) // 2, image=self.photo, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Hiển thị kết quả trong Text widget
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        for label, text in results.items():
            self.result_text.insert("end", f"{label}: {text}\n")
        self.result_text.config(state="disabled")
    
if __name__ == "__main__":
    root = Tk()
    app = OCRApp(root)
    root.mainloop()