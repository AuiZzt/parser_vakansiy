#!/usr/bin/env python3
"""
Управляющий скрипт для проекта "Агрегатор IT-вакансий Уфы"
Работает в интерактивном режиме.
"""

import os
import sys
import subprocess
import venv
import socket
import webbrowser
import signal
import time
import shutil
from pathlib import Path

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Константы
VENV_DIR = "venv"
REQUIREMENTS = "requirements.txt"
PARSER_SCRIPT = "main.py"
INDEX_HTML = "index.html"
PID_FILE = ".server.pid"

# Вспомогательные функции
def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color=RESET, bold=False):
    """Цветной вывод"""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def get_venv_paths():
    """Возвращает пути к python и pip внутри venv"""
    if sys.platform == "win32":
        python_exe = os.path.join(VENV_DIR, "Scripts", "python.exe")
        pip_exe = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        python_exe = os.path.join(VENV_DIR, "bin", "python")
        pip_exe = os.path.join(VENV_DIR, "bin", "pip")
    return python_exe, pip_exe

def venv_exists():
    return os.path.exists(VENV_DIR)

def is_venv_valid():
    """
    Проверяет, работает ли виртуальное окружение.
    Проверяет наличие python и pip, и возможность импортировать pip.
    """
    if not venv_exists():
        return False
    
    python_exe, pip_exe = get_venv_paths()
    
    # Проверяем, что python существует
    if not os.path.exists(python_exe):
        return False
    
    # Проверяем, что pip существует
    if not os.path.exists(pip_exe):
        return False
    
    # Проверяем, что pip работает (можно импортировать)
    try:
        result = subprocess.run(
            [python_exe, "-c", "import pip; print('ok')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == "ok" and result.returncode == 0
    except:
        return False

def ensure_valid_venv():
    """
    Гарантирует, что виртуальное окружение существует и работает.
    Если оно битое — удаляет и пересоздаёт заново.
    Возвращает (python_exe, pip_exe) или None, None при ошибке.
    """
    # Если venv есть, но битый — удаляем
    if venv_exists() and not is_venv_valid():
        print_colored("⚠️ Виртуальное окружение повреждено (возможно, создано на другом компьютере).", YELLOW)
        print_colored("🔄 Удаляю и создаю заново...", YELLOW)
        try:
            shutil.rmtree(VENV_DIR)
            print_colored("✅ Старое окружение удалено.", GREEN)
        except Exception as e:
            print_colored(f"❌ Не удалось удалить venv: {e}", RED)
            print_colored("💡 Удалите папку venv вручную и попробуйте снова.", YELLOW)
            return None, None
    
    # Если venv нет — создаём
    if not venv_exists():
        print_colored("📦 Создаём виртуальное окружение...", BLUE)
        try:
            venv.create(VENV_DIR, with_pip=True)
            print_colored("✅ Виртуальное окружение создано.", GREEN)
        except Exception as e:
            print_colored(f"❌ Не удалось создать venv: {e}", RED)
            return None, None
    
    # Получаем пути
    python_exe, pip_exe = get_venv_paths()
    
    # Дополнительная проверка: если pip всё ещё не найден — устанавливаем вручную
    if not os.path.exists(pip_exe):
        print_colored("⚠️ Pip не найден. Устанавливаю вручную...", YELLOW)
        try:
            # Скачиваем get-pip.py
            import urllib.request
            print("⏳ Скачиваю get-pip.py...")
            urllib.request.urlretrieve(
                "https://bootstrap.pypa.io/get-pip.py",
                "get-pip.py"
            )
            subprocess.run([python_exe, "get-pip.py"], check=True)
            os.remove("get-pip.py")
            
            # Обновляем пути
            if sys.platform == "win32":
                pip_exe = os.path.join(VENV_DIR, "Scripts", "pip.exe")
            else:
                pip_exe = os.path.join(VENV_DIR, "bin", "pip")
            
            print_colored("✅ Pip установлен.", GREEN)
        except Exception as e:
            print_colored(f"❌ Не удалось установить pip: {e}", RED)
            return None, None
    
    return python_exe, pip_exe

def is_server_running():
    """Проверяет, запущен ли сервер (по наличию PID-файла)"""
    return os.path.exists(PID_FILE)

def get_server_pid():
    if is_server_running():
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    return None

def find_free_port(start=8000, end=8010):
    """Поиск свободного порта в диапазоне"""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Нет свободных портов в диапазоне {start}-{end}")

def wait_for_key():
    """Ожидание нажатия Enter"""
    input("\nНажмите Enter, чтобы продолжить...")

# Основные действия
def action_install():
    """Установка / подготовка окружения"""
    clear_screen()
    print_colored("УСТАНОВКА ОКРУЖЕНИЯ", BLUE, bold=True)
    print("=" * 40)
    
    try:
        # Гарантируем рабочее виртуальное окружение
        python_exe, pip_exe = ensure_valid_venv()
        if python_exe is None or pip_exe is None:
            raise RuntimeError("Не удалось подготовить виртуальное окружение")
        
        print_colored(f"✅ Python: {python_exe}", GREEN)
        print_colored(f"✅ Pip: {pip_exe}", GREEN)

        print("\n📦 Устанавливаем зависимости из requirements.txt...")
        result = subprocess.run(
            [pip_exe, "install", "-r", REQUIREMENTS],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print_colored("\n✅ Окружение успешно подготовлено!", GREEN)
        else:
            print_colored("\n⚠️ Возможны проблемы при установке зависимостей.", YELLOW)
            
    except Exception as e:
        print_colored(f"\n❌ Ошибка: {e}", RED)
        print_colored("💡 Попробуйте удалить папку venv вручную и запустить снова.", YELLOW)
    
    wait_for_key()

def action_run():
    """Запуск парсера и сервера"""
    clear_screen()
    print_colored("ЗАПУСК", BLUE, bold=True)
    print("=" * 40)

    # Проверяем и чиним venv
    python_exe, _ = ensure_valid_venv()
    if python_exe is None:
        print_colored("❌ Виртуальное окружение не готово. Сначала выполните 'Установка'.", RED)
        wait_for_key()
        return

    # 1. Запуск парсера
    print("\n🚀 Запуск парсера...")
    try:
        subprocess.run([python_exe, PARSER_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Ошибка при выполнении парсера: {e}", RED)
        wait_for_key()
        return

    if not os.path.exists("vacancies.json"):
        print_colored("❌ Файл vacancies.json не создан. Парсер не сработал.", RED)
        wait_for_key()
        return
    
    print_colored("✅ Парсер завершил работу.", GREEN)

    # 2. Поиск порта
    try:
        port = find_free_port()
        print(f"🔌 Найден свободный порт: {port}")
    except RuntimeError as e:
        print_colored(f"❌ {e}", RED)
        wait_for_key()
        return

    # 3. Запуск сервера
    print(f"🌐 Запуск HTTP-сервера на порту {port}...")
    try:
        server_process = subprocess.Popen(
            [python_exe, "-m", "http.server", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        with open(PID_FILE, "w") as f:
            f.write(str(server_process.pid))
        print_colored(f"✅ Сервер запущен (PID: {server_process.pid})", GREEN)
    except Exception as e:
        print_colored(f"❌ Не удалось запустить сервер: {e}", RED)
        wait_for_key()
        return

    # 4. Открываем браузер
    url = f"http://localhost:{port}/{INDEX_HTML}"
    print(f"🌍 Открываем браузер: {url}")
    webbrowser.open(url)

    print_colored("\n✅ Сервер успешно запущен!", GREEN)
    print_colored("💡 Для остановки сервера выберите пункт 3 в меню.", YELLOW)
    wait_for_key()

def action_stop():
    """Остановка сервера"""
    clear_screen()
    print_colored("ОСТАНОВКА СЕРВЕРА", BLUE, bold=True)
    print("=" * 40)

    if not is_server_running():
        print_colored("⚠️ Сервер не запущен (PID-файл отсутствует).", YELLOW)
        wait_for_key()
        return

    pid = get_server_pid()
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print_colored(f"✅ Процесс {pid} остановлен.", GREEN)
    except ProcessLookupError:
        print_colored("⚠️ Процесс уже завершён.", YELLOW)
    except Exception as e:
        print_colored(f"❌ Ошибка при остановке: {e}", RED)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    wait_for_key()

def action_status():
    """Показать текущий статус"""
    clear_screen()
    print_colored("СТАТУС ПРОЕКТА", BLUE, bold=True)
    print("=" * 40)

    # Проверка venv
    if venv_exists():
        if is_venv_valid():
            print_colored("✅ Виртуальное окружение: работает", GREEN)
        else:
            print_colored("⚠️ Виртуальное окружение: повреждено (нужна переустановка)", YELLOW)
    else:
        print_colored("❌ Виртуальное окружение: не установлено", RED)
    
    # Проверка файла с вакансиями
    if os.path.exists("vacancies.json"):
        try:
            import json
            with open("vacancies.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            print_colored(f"✅ vacancies.json: есть ({len(data)} вакансий)", GREEN)
        except:
            print_colored("⚠️ vacancies.json: есть, но повреждён", YELLOW)
    else:
        print_colored("❌ vacancies.json: отсутствует", RED)

    # Проверка сервера
    if is_server_running():
        pid = get_server_pid()
        print_colored(f"✅ HTTP-сервер: ЗАПУЩЕН (PID: {pid})", GREEN)
    else:
        print_colored("❌ HTTP-сервер: ОСТАНОВЛЕН", RED)

    wait_for_key()

# Главное меню
def main_menu():
    while True:
        clear_screen()

        # Заголовок со статусом сервера
        print_colored("=" * 60, BLUE)
        print_colored("УПРАВЛЕНИЕ ПРОЕКТОМ АГРЕГАТОРА ВАКАНСИЙ", BLUE, bold=True)
        print_colored("=" * 60, BLUE)

        # Статус сервера в цвете
        if is_server_running():
            print_colored("🟢 Сервер: ЗАПУЩЕН", GREEN, bold=True)
        else:
            print_colored("🔴 Сервер: ОСТАНОВЛЕН", RED, bold=True)
        print()

        print("1. Установка / подготовка окружения")
        print("2. Запуск (парсер + сервер + браузер)")
        print("3. Остановка сервера")
        print("4. Показать статус")
        print("5. Выход")
        print()

        choice = input("Выберите действие (1-5): ").strip()

        if choice == "1":
            action_install()
        elif choice == "2":
            action_run()
        elif choice == "3":
            action_stop()
        elif choice == "4":
            action_status()
        elif choice == "5":
            clear_screen()
            print_colored("До свидания! 👋", BLUE, bold=True)
            break
        else:
            clear_screen()
            print_colored("❌ Неверный ввод, попробуйте снова.", RED)
            wait_for_key()

# Точка входа
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "install":
            action_install()
        elif cmd == "run":
            action_run()
        elif cmd == "stop":
            action_stop()
        elif cmd == "status":
            action_status()
        else:
            print("Неизвестная команда. Доступные: install, run, stop, status")
        sys.exit(0)
    else:
        main_menu()