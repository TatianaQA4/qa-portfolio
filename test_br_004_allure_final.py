"""
ПРОЕКТ BR_004: Ошибка 500 вместо валидации при пропуске поля.
Сайт: abcdveri.ru
Автор: Скрипай Татьяна
Группа: QA416
Версия с Allure-отчетом
"""

import os
import time
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from datetime import datetime


@allure.epic("Проект BR_004")
@allure.feature("Тестирование регистрации")
class TestBR004Allure:
    """Тестирование регистрации с Allure-отчетами"""

    SITE_URL = "https://abcdveri.ru"

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Настройка перед каждым тестом"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

        yield  # выполнение теста

        # Завершение
        if self.driver:
            self.driver.quit()

    def _take_screenshot(self, name):
        """Создание скриншота для Allure"""
        try:
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"Скриншот: {name}",
                attachment_type=allure.attachment_type.PNG
            )
            return True
        except:
            return False

    # ===================== ТЕСТЫ =====================

    @allure.story("Навигация")
    @allure.title("Переход к форме регистрации")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_navigation(self):
        """Тест навигации"""

        with allure.step("1. Открыть главную страницу"):
            self.driver.get(self.SITE_URL)
            time.sleep(2)
            assert "abcdveri" in self.driver.current_url
            self._take_screenshot("homepage")

        with allure.step("2. Найти меню 'Личный кабинет'"):
            menu = self.driver.find_element(
                By.XPATH, "//a[contains(text(), 'Личный кабинет')]"
            )
            menu.click()
            time.sleep(1)
            self._take_screenshot("menu_opened")

        with allure.step("3. Перейти к регистрации"):
            registration = self.driver.find_element(
                By.XPATH, "//a[contains(text(), 'Регистрация')]"
            )
            registration.click()
            time.sleep(3)
            self._take_screenshot("registration_page")

        with allure.step("4. Проверить загрузку формы"):
            assert "create-account" in self.driver.current_url
            allure.attach("Форма регистрации загружена", name="Результат")

    @allure.story("Регистрация")
    @allure.title("Успешная регистрация")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_registration(self):
        """Тест успешной регистрации"""

        with allure.step("1. Открыть форму регистрации"):
            self.driver.get(f"{self.SITE_URL}/create-account/")
            time.sleep(3)
            self._take_screenshot("form_loaded")

        with allure.step("2. Заполнить обязательные поля"):
            # Заполняем поля
            fields = {
                "input-firstname": f"Иван{int(time.time())}",
                "input-lastname": f"Тестов{int(time.time())}",
                "input-email": f"test{int(time.time())}@example.com",
                "input-telephone": f"+7999{int(time.time() % 1000000):06d}",
                "input-address-1": "Тестовый адрес",
                "input-city": "Москва",
                "input-password": "TestPassword123",
                "input-confirm": "TestPassword123"
            }

            for field_id, value in fields.items():
                element = self.driver.find_element(By.ID, field_id)
                element.clear()
                element.send_keys(value)

            # Выбор страны
            try:
                country = Select(self.driver.find_element(By.ID, "input-country"))
                country.select_by_visible_text("Российская Федерация")
                time.sleep(1)
            except:
                allure.attach("Не удалось выбрать страну", name="Предупреждение")

            # Выбор региона
            try:
                time.sleep(2)
                region = Select(self.driver.find_element(By.ID, "input-zone"))
                region.select_by_visible_text("Москва")
            except:
                allure.attach("Не удалось выбрать регион", name="Предупреждение")

            # Чекбокс согласия
            try:
                checkbox = self.driver.find_element(By.NAME, "agree")
                if not checkbox.is_selected():
                    checkbox.click()
            except:
                pass

            self._take_screenshot("form_filled")

        with allure.step("3. Отправить форму"):
            submit = self.driver.find_element(
                By.XPATH, "//input[@type='submit' and contains(@value, 'Продолжить')]"
            )
            submit.click()
            time.sleep(5)
            self._take_screenshot("after_submit")

        with allure.step("4. Проверить результат"):
            page_text = self.driver.page_source.lower()

            if "ваш аккаунт создан" in page_text or "успешно" in page_text:
                allure.attach("✅ РЕГИСТРАЦИЯ УСПЕШНА!", name="Результат")
                # НЕ вызывать pytest.fail() - регистрация прошла успешно
            elif "500" in page_text:
                #при заполнении всех полей не должно быть 500!
                allure.attach("❌ ОШИБКА 500 ПРИ ПОЛНОМ ЗАПОЛНЕНИИ (БАГ!)", name="Результат")
                pytest.fail("БАГ: Ошибка 500 при полном заполнении формы")
            else:
                allure.attach(f"⚠️ Неизвестный результат: {page_text[:200]}", name="Результат")

    @allure.story("Валидация")
    @allure.title("Проверка валидации при пропуске полей")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("field_to_skip", ["telephone", "zone"])
    def test_validation(self, field_to_skip):
        """Тест валидации формы"""

        with allure.step(f"1. Тестирование пропуска поля: {field_to_skip}"):
            self.driver.get(f"{self.SITE_URL}/create-account/")
            time.sleep(3)

            allure.attach(f"Пропускаемое поле: {field_to_skip}", name="Параметры")

        with allure.step("2. Заполнить все поля кроме одного"):
            fields_to_fill = {
                "input-firstname": "Иван",
                "input-lastname": "Тестов",
                "input-email": f"test{int(time.time())}@example.com",
                "input-address-1": "Адрес",
                "input-city": "Москва",
                "input-password": "Test123",
                "input-confirm": "Test123"
            }

            # Не заполняем указанное поле
            if field_to_skip != "telephone":
                fields_to_fill["input-telephone"] = "+79991234567"

            for field_id, value in fields_to_fill.items():
                element = self.driver.find_element(By.ID, field_id)
                element.clear()
                element.send_keys(value)

            # Выбор страны и региона (если не пропускаем регион)
            try:
                country = Select(self.driver.find_element(By.ID, "input-country"))
                country.select_by_visible_text("Российская Федерация")
                time.sleep(1)

                if field_to_skip != "zone":
                    time.sleep(2)
                    region = Select(self.driver.find_element(By.ID, "input-zone"))
                    region.select_by_visible_text("Москва")
            except:
                pass

            self._take_screenshot(f"form_without_{field_to_skip}")

        with allure.step("3. Отправить форму"):
            submit = self.driver.find_element(
                By.XPATH, "//input[@type='submit' and contains(@value, 'Продолжить')]"
            )
            submit.click()
            time.sleep(5)
            self._take_screenshot("result")

        with allure.step("4. Анализ результата"):
            page_text = self.driver.page_source.lower()
            current_url = self.driver.current_url

            result_info = f"""
URL: {current_url}
На странице 500: {'Да' if '500' in page_text else 'Нет'}
Остались на форме: {'Да' if 'create-account' in current_url else 'Нет'}
Текст ошибки: {'Есть' if 'ошибка' in page_text else 'Нет'}
"""

            allure.attach(result_info, name="Анализ результата")

            if "500" in page_text:
                allure.attach("❌ ОБНАРУЖЕН БАГ BUG-004!", name="Вывод")
                allure.attach(
                    f"Сервер возвращает ошибку 500 вместо валидации при пропуске поля: {field_to_skip}",
                    name="Баг-репорт"
                )
                pytest.fail(f"BUG-004: Ошибка 500 при пропуске {field_to_skip}")


# ===================== ЗАПУСК =====================

if __name__ == "__main__":
    print("🚀 Запуск тестов с Allure")
    pytest.main([
        __file__,
        "-v",
        "--alluredir=allure-results",
        "--clean-alluredir"
    ])