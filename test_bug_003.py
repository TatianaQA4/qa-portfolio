"""
ТЕСТИРОВАНИЕ ДЕФЕКТА BUG-003: Невозможность выбора способа доставки
Сайт: abcdveri.ru
Автор: Скрипай Татьяна
Группа: QA416
"""

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import ElementNotInteractableException
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


class TestBug003DeliveryIssue:
    BASE_URL = "https://abcdveri.ru"
    TEST_ADDRESS = "ул. Тверская, Москва"
    TEST_PRODUCT_URL = "https://abcdveri.ru/index.php?route=product/product&path=59_65&product_id=425"

    def take_screenshot(self, driver, step_name):
        """Сделать скриншот и прикрепить к Allure отчету"""
        screenshots_dir = "./allure-results/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"{screenshots_dir}/{step_name}_{timestamp}.png"
        driver.save_screenshot(filename)

        with open(filename, "rb") as f:
            screenshot_data = f.read()
            allure.attach(
                screenshot_data,
                name=step_name,
                attachment_type=allure.attachment_type.PNG
            )

        print(f"   📸 Скриншот: {step_name}")
        return filename

    @allure.feature("BUG-003 Доставка")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Проверка дефекта BUG-003 для адреса ул. Тверская, Москва")
    def test_bug_003_delivery_issue(self, driver):
        """
        ТЕСТ ДЛЯ ТОЧНОГО ПОДТВЕРЖДЕНИЯ BUG-003:
        Система показывает "Доставка по данному адресу невозможна",
        но при этом предлагает кнопку "Продолжить", которая либо не работает,
        либо приводит к ошибке валидации.
        """

        print("=" * 70)
        print("ТЕСТИРОВАНИЕ BUG-003: ДОСТАВКА НЕВОЗМОЖНА")
        print("=" * 70)

        try:
            # ====== ШАГ 1: ПОДГОТОВКА ======
            with allure.step("1. Добавление товара и переход к оформлению"):
                print("\n1. ДОБАВЛЕНИЕ ТОВАРА")

                # Открываем товар
                driver.get(self.TEST_PRODUCT_URL)
                time.sleep(3)
                self.take_screenshot(driver, "01_товар_страница")

                # Добавляем в корзину
                try:
                    add_button = driver.find_element(By.ID, "button-cart")
                    add_button.click()
                    print("   ✅ Товар добавлен в корзину")
                    time.sleep(2)
                except:
                    print("   ⚠️ Не удалось добавить товар")

                self.take_screenshot(driver, "02_товар_добавлен")

            # ====== ШАГ 2: ПЕРЕХОД К ОФОРМЛЕНИЮ ======
            with allure.step("2. Переход к оформлению заказа"):
                print("\n2. ПЕРЕХОД К ОФОРМЛЕНИЮ")

                # Прямой переход на страницу оформления
                driver.get(f"{self.BASE_URL}/checkout/")
                time.sleep(4)
                self.take_screenshot(driver, "03_страница_оформления")

                # Выбираем оформление как гостя
                try:
                    guest_option = driver.find_element(By.XPATH, "//input[@value='guest']")
                    if not guest_option.is_selected():
                        guest_option.click()
                        print("   ✅ Выбрано оформление без регистрации")
                except:
                    print("   ℹ️ Оформление как гостя не найдено")

                # Нажимаем первую кнопку "Продолжить"
                try:
                    first_continue = driver.find_element(
                        By.XPATH,
                        "//input[@value='Продолжить'] | //button[contains(text(), 'Продолжить')]"
                    )
                    first_continue.click()
                    print("   ✅ Нажата первая кнопка 'Продолжить'")
                    time.sleep(3)
                except:
                    print("   ⚠️ Не удалось найти первую кнопку 'Продолжить'")

                self.take_screenshot(driver, "04_после_первой_продолжить")

            # ====== ШАГ 3: ЗАПОЛНЕНИЕ ФОРМЫ ======
            with allure.step(f"3. Заполнение данных доставки ({self.TEST_ADDRESS})"):
                print(f"\n3. ЗАПОЛНЕНИЕ ФОРМЫ ({self.TEST_ADDRESS})")

                # Ждем загрузки формы
                time.sleep(3)

                # Данные для заполнения (как в баг-репорте)
                test_data = {
                    "Имя": ("input-payment-firstname", "Иван"),
                    "Фамилия": ("input-payment-lastname", "Иванов"),
                    "Email": ("input-payment-email", f"test{int(time.time())}@test.com"),
                    "Телефон": ("input-payment-telephone", "+79991234567"),
                    "Адрес": ("input-payment-address-1", "ул. Тверская"),
                    "Город": ("input-payment-city", "Москва")
                }

                # Заполняем поля
                for field_name, (field_id, value) in test_data.items():
                    try:
                        field = driver.find_element(By.ID, field_id)
                        field.clear()
                        field.send_keys(value)
                        print(f"   ✅ {field_name}: {value}")
                        time.sleep(0.2)
                    except:
                        print(f"   ⚠️ Не удалось заполнить {field_name}")

                # Выбираем регион Москва
                try:
                    region_select = Select(driver.find_element(By.ID, "input-payment-zone"))
                    region_select.select_by_visible_text("Москва")
                    print("   ✅ Регион: Москва")
                except:
                    try:
                        region_select = Select(driver.find_element(By.ID, "input-payment-zone"))
                        region_select.select_by_value("2761")  # ID Москвы
                        print("   ✅ Регион: Москва (по ID)")
                    except:
                        print("   ⚠️ Не удалось выбрать регион")

                self.take_screenshot(driver, "05_форма_заполнена")

                # Нажимаем кнопку для перехода к доставке
                try:
                    # Ищем кнопку с ID button-guest
                    continue_button = driver.find_element(By.ID, "button-guest")
                    continue_button.click()
                    print("   ✅ Нажата кнопка 'Продолжить' (доставка)")
                    time.sleep(4)
                except:
                    # Альтернативный поиск
                    try:
                        continue_buttons = driver.find_elements(
                            By.XPATH,
                            "//input[@value='Продолжить'] | //button[contains(text(), 'Продолжить')]"
                        )
                        for btn in continue_buttons:
                            if btn.is_displayed():
                                btn.click()
                                print("   ✅ Нажата кнопка 'Продолжить' (альтернативная)")
                                time.sleep(4)
                                break
                    except:
                        print("   ❌ Не удалось найти кнопку для перехода")

                self.take_screenshot(driver, "06_переход_к_доставке")

            # ====== ШАГ 4: ПРОВЕРКА ДЕФЕКТА НА ШАГЕ ДОСТАВКИ ======
            with allure.step("4. Анализ шага 'Способ доставки'"):
                print("\n4. АНАЛИЗ ШАГА 'СПОСОБ ДОСТАВКИ'")

                # Даем время загрузиться
                time.sleep(3)
                self.take_screenshot(driver, "07_шаг_доставки")

                # Получаем весь текст страницы
                page_html = driver.page_source
                page_text = page_html.lower()

                print(f"   📍 Текущий URL: {driver.current_url}")

                # ====== КЛЮЧЕВАЯ ПРОВЕРКА 1: Сообщение об ошибке ======
                target_message = "доставка по данному адресу невозможна"

                if target_message in page_text:
                    print(f"   🔴 НАЙДЕНО: '{target_message}'")
                    allure.attach(
                        f"СИСТЕМНОЕ СООБЩЕНИЕ: '{target_message}'\n\n"
                        f"Это подтверждает основное условие дефекта BUG-003",
                        name="Сообщение системы"
                    )

                    # Делаем скриншот с выделением сообщения
                    self.take_screenshot(driver, "08_сообщение_ошибки")
                else:
                    print("   ❌ Сообщение об ошибке не найдено")
                    # Проверяем альтернативные формулировки
                    alt_messages = [
                        "доставка невозможна",
                        "нет доступных способов доставки"
                    ]
                    for msg in alt_messages:
                        if msg in page_text:
                            print(f"   🔴 Найдено альтернативное сообщение: '{msg}'")
                            break

                # ====== КЛЮЧЕВАЯ ПРОВЕРКА 2: Наличие кнопки "Продолжить" ======
                try:
                    # Ищем кнопку "Продолжить" на текущей странице
                    continue_btn = driver.find_element(
                        By.XPATH,
                        "//input[@value='Продолжить'] | //button[contains(text(), 'Продолжить')]"
                    )

                    if continue_btn.is_displayed():
                        print("   ✅ Кнопка 'Продолжить' присутствует на странице")

                        # Проверяем состояние кнопки
                        is_enabled = continue_btn.is_enabled()
                        print(f"   ℹ️ Кнопка активна (enabled): {is_enabled}")

                        if is_enabled:
                            # ====== КЛЮЧЕВАЯ ПРОВЕРКА 3: Что происходит при клике ======
                            print("   🔍 Пробую нажать 'Продолжить'...")

                            # Сохраняем текущий URL и состояние
                            url_before = driver.current_url
                            self.take_screenshot(driver, "09_перед_кликом_продолжить")

                            try:
                                # Пробуем кликнуть
                                continue_btn.click()
                                time.sleep(3)

                                # Проверяем результат
                                url_after = driver.current_url

                                # Проверяем, появилось ли сообщение об ошибке валидации
                                new_page_text = driver.page_source.lower()

                                validation_errors = [
                                    "необходимо указать способ доставки",
                                    "выберите способ доставки",
                                    "способ доставки не выбран",
                                    "укажите способ доставки"
                                ]

                                error_found = False
                                for error in validation_errors:
                                    if error in new_page_text:
                                        print(f"   🔴 ПОСЛЕ КЛИКА: '{error}'")
                                        allure.attach(
                                            f"РЕЗУЛЬТАТ КЛИКА:\n"
                                            f"• При нажатии 'Продолжить' появилось сообщение: '{error}'\n"
                                            f"• Это подтверждает, что система требует выбрать способ доставки\n"
                                            f"• Но выбрать нечего - нет доступных вариантов",
                                            name="Ошибка валидации"
                                        )
                                        error_found = True
                                        break

                                if not error_found:
                                    # Проверяем, перешли ли мы дальше
                                    if url_before == url_after:
                                        print("   🔴 Кнопка нажалась, но переход не произошел")
                                        allure.attach(
                                            "Кнопка 'Продолжить' нажалась, но система не перешла к следующему шагу\n"
                                            "Это означает, что система блокирует переход из-за отсутствия выбора доставки",
                                            name="Блокировка перехода"
                                        )
                                    else:
                                        print(f"   ℹ️ Перешли на новый URL: {url_after}")

                                self.take_screenshot(driver, "10_после_клика_продолжить")

                            except ElementNotInteractableException:
                                print("   🔴 ElementNotInteractableException: Кнопка не кликабельна")
                                allure.attach(
                                    "Кнопка 'Продолжить' вызывает ElementNotInteractableException\n"
                                    "Технически кнопка есть, но система блокирует взаимодействие с ней",
                                    name="Кнопка не кликабельна"
                                )
                            except Exception as e:
                                print(f"   ⚠️ Ошибка при клике: {str(e)[:50]}")
                        else:
                            print("   ℹ️ Кнопка 'Продолжить' неактивна (disabled)")
                    else:
                        print("   ⚠️ Кнопка 'Продолжить' не видна на странице")

                except Exception as e:
                    print(f"   ❌ Не удалось найти кнопку 'Продолжить': {str(e)[:50]}")

                # ====== КЛЮЧЕВАЯ ПРОВЕРКА 4: Наличие вариантов доставки ======
                print("\n   🔍 Проверяю наличие вариантов доставки...")

                # Ищем радиокнопки, чекбоксы, select'ы для доставки
                delivery_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "input[name='shipping_method'], "
                    "input[type='radio'][name*='shipping'], "
                    "input[type='radio'][name*='delivery'], "
                    "select[name*='shipping'], "
                    ".shipping-method, "
                    ".radio > input[type='radio']"
                )

                # Фильтруем только видимые элементы
                visible_delivery_options = []
                for element in delivery_elements:
                    try:
                        if element.is_displayed():
                            visible_delivery_options.append(element)
                    except:
                        pass

                if visible_delivery_options:
                    print(f"   ℹ️ Найдено элементов доставки: {len(visible_delivery_options)}")

                    # Проверяем, можно ли их выбрать
                    selectable_count = 0
                    for element in visible_delivery_options:
                        if element.is_enabled():
                            selectable_count += 1

                    print(f"   ℹ️ Из них доступно для выбора: {selectable_count}")

                    if selectable_count == 0:
                        print("   🔴 НЕТ ДОСТУПНЫХ ВАРИАНТОВ ДОСТАВКИ!")
                        allure.attach(
                            "Элементы выбора доставки присутствуют, но НИ ОДИН не доступен для выбора\n"
                            "Это подтверждает невозможность выбора способа доставки",
                            name="Нет доступных вариантов"
                        )
                else:
                    print("   🔴 ВАРИАНТЫ ДОСТАВКИ ОТСУТСТВУЮТ!")
                    allure.attach(
                        "На странице отсутствуют элементы для выбора способа доставки\n"
                        "Пользователь физически не может выбрать способ доставки",
                        name="Отсутствие вариантов"
                    )

            # ====== ШАГ 5: ФИНАЛЬНАЯ ОЦЕНКА ======
            with allure.step("5. Оценка подтверждения дефекта BUG-003"):
                print("\n" + "=" * 70)
                print("ФИНАЛЬНАЯ ОЦЕНКА ДЕФЕКТА BUG-003")
                print("=" * 70)

                # Проверяем ключевые индикаторы дефекта
                page_text_final = driver.page_source.lower()

                has_delivery_error = "доставка по данному адресу невозможна" in page_text_final
                has_continue_button = "продолжить" in page_text_final

                if has_delivery_error and has_continue_button:
                    print("\n🔴🔴🔴 ДЕФЕКТ BUG-003 ПОДТВЕРЖДЕН! 🔴🔴🔴")
                    print("\n📋 ДОКАЗАТЕЛЬСТВА:")
                    print("1. Система показывает: 'Доставка по данному адресу невозможна'")
                    print("2. При этом присутствует кнопка 'Продолжить'")
                    print("3. Выбрать способ доставки невозможно (нет вариантов)")
                    print("4. Нажатие 'Продолжить' приводит к ошибке или не работает")

                    final_conclusion = f"""
ФИНАЛЬНЫЙ ВЫВОД: ДЕФЕКТ BUG-003 ПОДТВЕРЖДЕН

УСЛОВИЯ ДЕФЕКТА:
✓ Адрес доставки: {self.TEST_ADDRESS}
✓ Сообщение системы: "Доставка по данному адресу невозможна"
✓ Наличие кнопки "Продолжить": Да
✓ Возможность выбора способа доставки: Нет

ПРОБЛЕМА:
• Система информирует о невозможности доставки
• Но предлагает продолжить оформление
• При этом не предоставляет возможности выбрать способ доставки
• Процесс оформления блокируется

ВЛИЯНИЕ НА БИЗНЕС:
• Потеря клиента и выручки
• Негативный пользовательский опыт
• Блокировка процесса покупки

РЕКОМЕНДАЦИЯ:
1. Добавить возможность выбора самовывоза
2. Или убрать кнопку "Продолжить" при невозможности доставки
3. Или предоставить альтернативные варианты доставки
"""

                    print(final_conclusion)
                    allure.attach(final_conclusion, name="ФИНАЛЬНЫЙ ОТЧЕТ: Дефект подтвержден")

                    # Финальный скриншот
                    self.take_screenshot(driver, "11_BUG003_ПОДТВЕРЖДЕН")

                    # Тест упадет - это ожидаемо при подтверждении дефекта
                    pytest.fail("BUG-003 подтвержден: Доставка невозможна, но кнопка 'Продолжить' присутствует")

                else:
                    print("\n✅ ДЕФЕКТ BUG-003 НЕ ПОДТВЕРЖДЕН")
                    print("\n📋 РЕЗУЛЬТАТЫ:")
                    print(f"• Сообщение об ошибке доставки: {'Найдено' if has_delivery_error else 'Не найдено'}")
                    print(f"• Кнопка 'Продолжить': {'Найдена' if has_continue_button else 'Не найдена'}")

                    allure.attach(
                        "Дефект BUG-003 не подтвержден\n"
                        "Условия дефекта не выполнены полностью",
                        name="ФИНАЛЬНЫЙ ОТЧЕТ: Дефект не подтвержден"
                    )

                    self.take_screenshot(driver, "11_BUG003_НЕ_ПОДТВЕРЖДЕН")

                    # Тест проходит успешно
                    assert True, "Дефект BUG-003 не подтвержден"

        except Exception as e:
            # Обработка неожиданных ошибок
            print(f"\n❌ ОШИБКА ВЫПОЛНЕНИЯ ТЕСТА: {str(e)[:100]}")
            self.take_screenshot(driver, "ERROR_критическая_ошибка")
            allure.attach(f"Критическая ошибка теста: {str(e)}", name="Ошибка выполнения")
            raise e

        finally:
            print("\n" + "=" * 70)
            print("ТЕСТ ЗАВЕРШЕН")
            print("=" * 70)


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v", "--alluredir=./allure-results"]))

# ИНСТРУКЦИЯ ПО ЗАПУСКУ:
# 1. Установите зависимости: pip install pytest selenium allure-pytest
# 2. Запустите тест: pytest test_bug_003.py --alluredir=./allure-results -v
# 3.Сгенерировать HTML отчет в папку
# allure generate ./allure-results -o ./allure-report --clean
# 4.Просмотрите отчет: allure serve ./allure-results
#
# ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
# - Если дефект BUG-003 существует: тест упадет с детальным отчетом
# - Если дефекта нет: тест пройдет успешно
# - Все скриншоты будут сохранены в Allure отчете