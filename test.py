import subprocess

def generate_requirements():
    try:
        # Запускаем команду pip freeze, чтобы получить список всех установленных пакетов
        result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
        requirements = result.stdout

        # Сохраняем список пакетов в файл requirements.txt
        with open('requirements.txt', 'w') as file:
            file.write(requirements)

        print("requirements.txt успешно создан")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    generate_requirements()
