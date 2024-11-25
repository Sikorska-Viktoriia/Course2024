import mysql.connector
import speech_recognition as sr
import hashlib
from mysql.connector import Error


db_config = {
    'user': 'sikorska',
    'password': 'tailcat12',
    'host': 'localhost',
    'database': 'client'
}


stored_encrypted_word = None

def connect_db():
   
    try:
        conn = mysql.connector.connect(**db_config)  
        if conn.is_connected():
            print("Підключено до бази даних MySQL")
        return conn
    except Error as e:
        print(f"Помилка підключення: {e}")
        return None

def create_table():

    conn = connect_db()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            encrypted_word VARCHAR(255) NOT NULL
        );
        """)
        print("Таблиця створена або вже існує.")
    except Error as e:
        print(f"Помилка при створенні таблиці: {e}")
    finally:
        cursor.close()
        conn.close()

def encrypt_word(word):
   
    return hashlib.sha256(word.encode()).hexdigest()

def register_user():
 
    global stored_encrypted_word  
    name = input("Введіть ваше ім'я: ")
    print("Скажіть ваше секретне слово для аутентифікації.")
    
   
    recognizer = sr.Recognizer()
    
   
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  
        print("Говоріть ваше слово...")
        try:
            audio = recognizer.listen(source, timeout=5)  
            print("Розпізнається слово...")
            
           
            word = recognizer.recognize_google(audio, language="uk-UA")
            print(f"Розпізнано слово: {word}")
            
          
            encrypted_word = encrypt_word(word)
            stored_encrypted_word = encrypted_word  
            print(f"Зашифроване слово для збереження: {encrypted_word}")
            
        
            print(f"Користувач {name} зареєстрований з зашифрованим словом: {encrypted_word}")
            
            
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user (name, encrypted_word) VALUES (%s, %s)", (name, encrypted_word))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Дані користувача {name} збережено в базі даних.")
            
        except sr.UnknownValueError:
            print("Не вдалося розпізнати слово. Спробуйте знову.")
        except sr.RequestError:
            print("Помилка при запиті до сервісу розпізнавання голосу.")
        except Exception as e:
            print(f"Сталася помилка: {e}")

def authenticate_user():
    """Процес аутентифікації користувача."""
    name = input("Введіть ваше ім'я для аутентифікації: ")
    print("Скажіть ваше секретне слово для аутентифікації.")
    
   
    recognizer = sr.Recognizer()
    
   
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source) 
        print("Говоріть ваше слово...")
        try:
            audio = recognizer.listen(source, timeout=5)  
            print("Розпізнається слово...")
            
            
            word = recognizer.recognize_google(audio, language="uk-UA")
            print(f"Розпізнано слово: {word}")
            
         
            encrypted_word = encrypt_word(word)
            print(f"Зашифроване слово для порівняння: {encrypted_word}")
            
            
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT encrypted_word FROM user WHERE name = %s", (name,))
                result = cursor.fetchone()
                
                if result:
                    stored_encrypted_word = result[0]
                    print(f"Знайдено зашифроване слово для {name}: {stored_encrypted_word}")
                    
                
                    if encrypted_word == stored_encrypted_word:
                        print(f"Аутентифікація успішна для {name}!")
                    else:
                        print(f"Аутентифікація не вдалася для {name}.")
                else:
                    print(f"Користувача з ім'ям {name} не знайдено в базі даних.")
                
                cursor.close()
                conn.close()
            
        except sr.UnknownValueError:
            print("Не вдалося розпізнати слово. Спробуйте знову.")
        except sr.RequestError:
            print("Помилка при запиті до сервісу розпізнавання голосу.")
        except Exception as e:
            print(f"Сталася помилка: {e}")

    
  
    recognizer = sr.Recognizer()
    
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  
        print("Говоріть ваше слово...")
        try:
            audio = recognizer.listen(source, timeout=5) 
            print("Розпізнається слово...")
            
          
            word = recognizer.recognize_google(audio, language="uk-UA")
            print(f"Розпізнано слово: {word}")
            
           
            encrypted_word = encrypt_word(word)
            print(f"Зашифроване слово для порівняння: {encrypted_word}")
            
           
            if encrypted_word == stored_encrypted_word:
                print(f"Аутентифікація успішна для {name}!")
            else:
                print(f"Аутентифікація не вдалася для {name}.")
            
        except sr.UnknownValueError:
            print("Не вдалося розпізнати слово. Спробуйте знову.")
        except sr.RequestError:
            print("Помилка при запиті до сервісу розпізнавання голосу.")
        except Exception as e:
            print(f"Сталася помилка: {e}")

def main():
    """Основна функція для вибору методу."""
    print("Оберіть метод:")
    print("1. Реєстрація")
    print("2. Аутентифікація")
    
    choice = input("Ваш вибір: ")
    
    if choice == "1":
        register_user()
    elif choice == "2":
        authenticate_user()
    else:
        print("Невірний вибір, спробуйте ще раз.")

if __name__ == "__main__":
    create_table()  
    main()
