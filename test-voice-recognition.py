import os
import time
import random
import re
import markdown
import keyboard
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
from playsound import playsound

# Thiết lập API key cho Google Gemini
genai.configure(api_key="AIzaSyDIZSl-1nqZf59MqHeVl20P4TsAeLcxD6E")


def remove_code_blocks(text):
    # Loại bỏ code blocks được bao quanh bởi ```
    text = re.sub(r"`.*?`", "", text, flags=re.DOTALL)

    # Loại bỏ code blocks được bao quanh bởi ///
    text = re.sub(r"///.*?///", "", text, flags=re.DOTALL)

    return text


def clean_gemini_output(text):
    text = remove_code_blocks(text)
    html = markdown.markdown(text)
    text = re.sub(r"<[^>]+>", "", html)  # Loại bỏ HTML tags
    return text


def play_audio(text):
    try:
        # Tạo timestamp và số ngẫu nhiên
        timestamp = time.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(10000, 99999)  # Số ngẫu nhiên 5 chữ số

        # Kết hợp timestamp và số ngẫu nhiên để tạo tên file
        file_name = f"temp_audio_{timestamp}_{random_num}.mp3"
        temp_file_path = os.path.join(os.getcwd(), file_name)

        # Tương tự với file text
        file_name_text = f"{timestamp}_{random_num}.txt"
        temp_text_file_path = os.path.join(os.getcwd(), file_name_text)
        file_name_old_text = f"{timestamp}_{random_num}_old.txt"
        temp_text_old_file_path = os.path.join(os.getcwd(), file_name_old_text)

        tts = gTTS(text=text, lang="vi")
        tts.save(temp_file_path)

        with open(temp_text_file_path, "w", encoding="utf-8") as f:
            f.write(text)

        playsound(temp_file_path)
        print("Đã phát xong.")

        try:
            os.replace(temp_text_file_path, temp_text_old_file_path)
        except FileNotFoundError:
            pass

        for file in os.listdir():
            if file.startswith("temp_audio_") and file != file_name:
                try:
                    os.remove(file)
                    print(f"Đã xóa file cũ: {file}")
                except:
                    pass
            if file.startswith("temp_text_old_") and file != file_name_old_text:
                try:
                    os.remove(file)
                    print(f"Đã xóa file cũ: {file}")
                except:
                    pass

    except Exception as e:
        print(f"Lỗi khi phát  m thanh: {e}")


def main():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.9
    recognizer.energy_threshold = 400
    recognizer.phrase_threshold = 0.7
    recognizer.non_speaking_duration = 0.7
    while True:
        with sr.Microphone() as source:
            print("Nói điều gì đó...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="vi-VN")
            print(f"Bạn nói: {text}")

            if "kết thúc" in text.lower():
                print("Kết thúc chương trình.")
                break

            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(text)
            gemini_output = response.text
            cleaned_output = clean_gemini_output(gemini_output)

            print(f"Nội dung từ Gemini: {cleaned_output}")
            play_audio(cleaned_output)

            while keyboard.is_pressed("r"):
                play_audio(cleaned_output)
                time.sleep(0.2)  # Tránh đọc lại liên tục khi giữ phím

        except sr.UnknownValueError:
            print("Không thể nhận diện được âm thanh")
        except sr.RequestError as e:
            print(f"Không thể kết nối với dịch vụ Google: {e}")
        except Exception as e:
            print(f"Lỗi với Gemini API: {e}")


if __name__ == "__main__":
    main()
