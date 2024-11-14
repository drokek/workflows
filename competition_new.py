import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

# Глобальные переменные для хранения оценок и данных участников
scores = []
score_entries = {}
total_scores = pd.DataFrame({'Номер участника': [], 'Входы': [],'Тактика': [],'Акробатика': [],'Дистанция': [],'Техника': [],'Итоговый балл': [],})

def update_score(participant, field, delta):
    """Функция для изменения значения оценки."""
    entry = score_entries[participant][field]
    current_value = int(entry.text)
#    new_value = max(0, current_value + delta)  # Ограничение для значений ≥ 0
    new_value = current_value + delta
    entry.text = str(new_value)

def save_current_pair():
    """Сохраняет текущую пару участников и их результаты."""
    global scores, total_scores

    participant1_number = participant1_label.text
    participant2_number = participant2_label.text

    for i, participant in enumerate(["Участник 1", "Участник 2"]):
        if i == 0:
            entry_data = [participant1_number]
        else:
            entry_data = [participant2_number]
        total_score = 0
        for field in score_entries[participant]:
            score = int(score_entries[participant][field].text)
            entry_data.append(score)
            total_score += score
        entry_data.append(total_score)
        scores.append(entry_data)
        total_scores = pd.concat([total_scores, pd.DataFrame([entry_data], columns=total_scores.columns)], ignore_index=True)

    reset_fields()

    '''if participant1_number and participant2_number:
        for participant in [participant1_number, participant2_number]:
            entry_data = [participant]
            total_score = 0
            print(score_entries.keys())
            for field in score_entries[participant]:
                score = int(score_entries[participant][field].text)
                entry_data.append(score)
                total_score += score
            entry_data.append(total_score)
            scores.append(entry_data)
        reset_fields()'''

def reset_fields():
    print(total_scores)
    """Сбрасывает поля ввода и обновляет метки участников."""
    global participant1_label, participant2_label, score_entries
    participant1_label.text = ""
    participant2_label.text = ""
    for participant in score_entries:
        for field in score_entries[participant]:
            score_entries[participant][field].text = '0'

def save_results_to_csv():
    """Сохраняет результаты в CSV файл и обнуляет данные."""
    global scores

    if scores:
        columns = ['Номер участника', 'Входы', 'Тактика', 'Акробатика', 'Дистанция', 'Техника', 'Итоговый балл']
        results_df = pd.DataFrame(scores, columns=columns)

        popup_content = BoxLayout(orientation='vertical')
        filename_input = TextInput(hint_text="Введите название файла", multiline=False)
        save_button = Button(text="Сохранить", on_press=lambda x: save_to_csv(filename_input.text, results_df))

        popup_content.add_widget(filename_input)
        popup_content.add_widget(save_button)

        popup = Popup(title="Сохранение файла", content=popup_content, size_hint=(0.6, 0.4))
        popup.open()

def save_to_csv(filename, results_df):
    """Сохраняет DataFrame в CSV файл."""
    if filename:
        results_df.to_csv(f"{filename}.csv", index=False)
        Popup(title="Готово", content=Label(text="Результаты успешно сохранены!"), size_hint=(0.6, 0.3)).open()
        reset_all_data()

def reset_all_data():
    """Сбрасывает все данные, возвращая приложение в начальное состояние."""
    global scores
    scores = []
    reset_fields()

def build_interface():
    """Создает интерфейс приложения."""
    global participant1_label, participant2_label, score_entries

    layout = BoxLayout(orientation='vertical')
    header_layout = GridLayout(cols=2, size_hint_y=None, height=50)

    # Поля для ввода номеров участников
    participant1_label = TextInput(hint_text="Участник 1", font_size=40, multiline=False)
    participant2_label = TextInput(hint_text="Участник 2", font_size=40, multiline=False)

    header_layout.add_widget(participant1_label)
    header_layout.add_widget(participant2_label)

    layout.add_widget(header_layout)

    # Поля для ввода оценок
    score_entries = {
        "Участник 1": {},
        "Участник 2": {}
    }
    fields = ['Входы', 'Тактика', 'Акробатика', 'Дистанция', 'Техника']

    for field in fields:
        grid = GridLayout(cols=4, size_hint_y=None, height=200)
        for participant in ["Участник 1", "Участник 2"]:
            if participant == "Участник 1":
                # Поле для ввода числового значения
                entry = TextInput(text='0', multiline=False, input_filter='int',size_hint_x=None , width=100, halign="center")
                score_entries[participant][field] = entry

                # Кнопки "+" и "-" для увеличения и уменьшения значения
                increment_layout = BoxLayout(orientation='horizontal')
                minus_button = Button(text="-", size_hint_x=None, width=215)
                minus_button.bind(on_press=lambda inst, p=participant, f=field: update_score(p, f, -1))
                plus_button = Button(text="+", size_hint_x=None, width=215)
                plus_button.bind(on_press=lambda inst, p=participant, f=field: update_score(p, f, 1))
                increment_layout.add_widget(plus_button)
                increment_layout.add_widget(entry)
                increment_layout.add_widget(minus_button)
                grid.add_widget(increment_layout)

            else:
                # Метка для названия поля
                field_label = Label(text=field, font_size=40)
                grid.add_widget(field_label)

                # Поле для ввода числового значения
                entry = TextInput(text='0', multiline=False, input_filter='int',size_hint_x=None , width=100, halign="center")
                score_entries[participant][field] = entry

                # Кнопки "+" и "-" для увеличения и уменьшения значения
                increment_layout = BoxLayout(orientation='horizontal')
                plus_button = Button(text="+", size_hint_x=None, width=215)
                plus_button.bind(on_press=lambda inst, p=participant, f=field: update_score(p, f, 1))
                minus_button = Button(text="-", size_hint_x=None, width=215)
                minus_button.bind(on_press=lambda inst, p=participant, f=field: update_score(p, f, -1))

                increment_layout.add_widget(minus_button)
                increment_layout.add_widget(entry)
                increment_layout.add_widget(plus_button)
                grid.add_widget(increment_layout)

        layout.add_widget(grid)

    # Кнопка "Далее"
    next_button = Button(text="Далее")
    next_button.bind(on_press=lambda x: save_current_pair())
    layout.add_widget(next_button)

    # Кнопка "Сохранить"
    save_button = Button(text="Сохранить")
    save_button.bind(on_press=lambda x: save_results_to_csv())
    layout.add_widget(save_button)

    return layout

class ParticipantScoringApp(App):
    def build(self):
        return build_interface()

# Запуск приложения
ParticipantScoringApp().run()







        
