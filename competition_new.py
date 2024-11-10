import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix import filechooser
import pandas as pd
import os

# Глобальные переменные для хранения данных
participants = []
current_pair_index = 0
scores = {}
grouppath = ""
groupname = ""

# Функция для загрузки CSV файла и обработки данных


def load_csv_file(instance):
    global participants, current_pair_index, scores, grouppath, groupname
    filechooser = FileChooserListView()
    select_button = Button(text="Выбрать файл", size_hint=(1, 0.1))
    label = Label(text="Выберите CSV файл", size_hint=(1, 0.1))
    chooser_layout = BoxLayout(orientation='vertical')
    chooser_layout.add_widget(filechooser)
    chooser_layout.add_widget(select_button)
    chooser_layout.add_widget(label)
    popup = Popup(title="Выберите CSV файл", content=chooser_layout, size_hint=(0.9, 0.9))
    def on_file_selected(button_instance):
        global grouppath
        selected_file = filechooser.selection
        if selected_file:
            selected_file_path = selected_file[0]
            label.text = f'Выбрано: {selected_file[0]}'
            popup.dismiss()
        else:
            label.text = 'Файл не выбран'
        
        df = pd.read_csv(selected_file_path, header=None)
        grouppath = selected_file_path
        grouppath = grouppath[:-4]
        parts1 = df[0].to_list()
        parts2 = df[1].to_list()
        for i in range(len(parts1)):
            participants.append([parts1[i], parts2[i]])
        

        # Проверка на пустой файл
        if not participants:
            raise ValueError("Файл пуст или не содержит данных.")

        # Инициализация словаря для хранения оценок
        scores.clear()
        scores.update({participant: {'Дистанция': 0, 'Входы': 0, 'Акробатика': 0, 'Техника': 0, 'Тактика': 0}
                       for pair in participants for participant in pair})
        current_pair_index = -1  # Устанавливаем индекс на -1, чтобы show_next_pair() увеличил его до 0
        show_next_pair()
        
    select_button.bind(on_press=on_file_selected)
    popup.open()


# Функция для отображения следующей пары участников
def show_next_pair():
    global current_pair_index, participants
    current_pair_index += 1

    if current_pair_index >= len(participants):
        export_results()
        return

    pair = participants[current_pair_index]
    participant1_label.text = f"Участник {pair[0]}"
    participant2_label.text = f"Участник {pair[1]}"
    reset_fields()

# Функция для обновления оценок в поле
def update_score(participant, field, increment):
    current_value = int(score_entries[participant][field].text)
    new_value = max(0, current_value + increment)  # Не позволяем числу быть отрицательным
    score_entries[participant][field].text = str(new_value)

# Функция для обнуления полей
def reset_fields():
    for participant in score_entries:
        for field in score_entries[participant]:
            score_entries[participant][field].text = '0'

# Функция для перехода к следующей паре и сохранения данных
def next_pair(instance):
    global current_pair_index, participants

    print(score_entries.keys())
    if current_pair_index < len(participants):
        i = 0
        for participant in score_entries.keys():
            for field in score_entries[participant]:
                number = participants[current_pair_index][i]
                scores[number][field] = int(score_entries[participant][field].text)
            i += 1
    show_next_pair()

# Функция для экспорта результатов в CSV файл
'''def export_results():
    global scores

    data = []
    for participant, fields in scores.items():
        total_score = sum(fields.values())
        row = [participant] + list(fields.values()) + [total_score]
        data.append(row)

    columns = ['Номер участника', 'Дистанция', 'Входы', 'Техника', 'Тактика', 'Акробатика', 'Итоговый балл']
    results_df = pd.DataFrame(data, columns=columns)

    def save_results(selected_path):
        if selected_path:
            results_df.to_csv(selected_path[0], index=False)
            popup.dismiss()
            Popup(title="Готово", content=Label(text="Результаты успешно сохранены!"), size_hint=(0.6, 0.3)).open()
            filechooser = FileChooserListView(select_string='Сохранить')
    filechooser.bind(on_submit=lambda f, s, *_: save_results(s))

    popup = Popup(title="Сохранить CSV файл", content=filechooser, size_hint=(0.9, 0.9))
    popup.open()'''


def export_results():
    global scores, grouppath

    data = []
    for participant, fields in scores.items():
        total_score = sum(fields.values())
        row = [participant] + list(fields.values()) + [total_score]
        data.append(row)
    

    columns = ['Номер участника', 'Дистанция', 'Входы', 'Техника', 'Тактика', 'Акробатика', 'Итоговый балл']
    results_df = pd.DataFrame(data, columns=columns)
    def save_results(instance):
        nonlocal filename
        path = grouppath + f"_{filename.text}.csv"
        results_df.to_csv(path, index=False)
        Popup(title="Готово", content=Label(text="Результаты успешно сохранены!"), size_hint=(0.6, 0.3)).open()

    saver = BoxLayout(orientation='vertical')
    filename = TextInput(hint_text="Введите номер судьи")
    save_button = Button(text="Сохранить", on_press=save_results)
    saver.add_widget(filename)
    saver.add_widget(save_button)

    popup = Popup(title="Выберите CSV файл", content=saver, size_hint=(0.9, 0.9))
    popup.open()

# Основная функция, создающая интерфейс
def build_interface():
    global participant1_label, participant2_label, score_entries

    layout = BoxLayout(orientation='vertical')
    header_layout = GridLayout(cols=3, size_hint_y=None, height=50)

    # Метки для отображения текущих участников
    participant1_label = Label(text="Участник 1", font_size=40)
    middle_label = Label(text="VS", font_size=40)
    participant2_label = Label(text="Участник 2", font_size=40)

    header_layout.add_widget(participant1_label)
    header_layout.add_widget(middle_label)
    header_layout.add_widget(participant2_label)

    layout.add_widget(header_layout)

    # Инициализация словаря для полей участников
    score_entries = {}
    fields = ['Входы', 'Тактика', 'Акробатика', 'Дистанция', 'Техника']


    score_entries["Участник 1"] = {}
    score_entries["Участник 2"] = {}

    for field in fields:
        grid = GridLayout(cols=6, size_hint_y=None, height=200, width=300)
        for i, participant in enumerate(["Участник 1", "Участник 2"]):
            if i == 0:

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

    


    # Кнопка для загрузки CSV файла
    load_button = Button(text="Загрузить CSV")
    load_button.bind(on_press=load_csv_file)
    layout.add_widget(load_button)
    
    # Кнопка "Далее" для перехода к следующей паре
    next_button = Button(text="Далее")
    next_button.bind(on_press=next_pair)
    layout.add_widget(next_button)

    return layout

# Определение приложения
class ParticipantScoringApp(App):
    def build(self):
        return build_interface()

# Запуск приложения
ParticipantScoringApp().run()















        