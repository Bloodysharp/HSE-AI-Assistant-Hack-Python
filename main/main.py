import requests
import json
import pandas as pd


# Функция для отправки запроса в YandexGPT для анализа кода
def ask_gpt(user_text):
    if not user_text:
        return "Input text is empty."

    # Структура запроса
    prompt = {
        "modelUri": "gpt://b1gu0eskj5a33vgrltde/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": "1000"
        },
        "messages": [
            {"role": "system", "text": "You are a computer science teacher. You are given a student's decision. Find the errors and if there are any, give a hint where they may be."},
            {"role": "user", "text": user_text}
        ]
    }

    # Конвертируем в JSON
    json_prompt = json.dumps(prompt)

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2NvJxczfE7Xdk70FVtDIjmaYyj1UomQGZpZU"
    }

    try:
        response = requests.post(url, headers=headers, data=json_prompt)
        response.raise_for_status()

        # Парсим ответ
        api_response = response.json()

        if api_response["result"]["alternatives"]:
            gpt_response = api_response["result"]["alternatives"][0]["message"]["text"]
            return gpt_response
        else:
            return "No response received."

    except requests.exceptions.RequestException as e:
        return f"Failed to send request: {e}"
    except json.JSONDecodeError:
        return "Failed to parse response."


# Функция для проверки решений студентов с использованием тестов
def check_solution_with_tests(solution_code, tests_df, task_id):
    # Извлечение тестов, связанных с данным task_id
    relevant_tests = tests_df[tests_df['task_id'] == task_id]
    
    for _, test in relevant_tests.iterrows():
        input_data = test['input']
        expected_output = test['output']

        try:
            # Выполнение кода студента с тестовыми данными (используем exec, но с осторожностью)
            # Важно: Это небезопасно и рекомендуется использовать с ограничениями, например, через песочницу.
            exec_locals = {}
            exec(solution_code, {}, exec_locals)

            # Сравнение результата с ожидаемым выводом
            actual_output = exec_locals.get('result', None)
            if str(actual_output) != str(expected_output):
                return f"Error in test {test['number']}. Expected: {expected_output}, got: {actual_output}"

        except Exception as e:
            return f"Error during execution: {str(e)}"

    return "Solution passed all tests."


# Функция для обработки решений студентов и задач
def process_student_solutions(solutions_df, tasks_df, tests_df):
    results = []  # Список для хранения данных для submit_example

    for index, row in solutions_df.iterrows():
        solution_id = row['id']
        student_solution = row['student_solution']
        task_id = row['task_id']

        print(f"Processing solution ID: {solution_id}")

        # Получаем описание задачи и авторское решение
        task = tasks_df[tasks_df['id'] == task_id].iloc[0]
        task_description = task['description']
        author_solution = task['author_solution']

        # Проверяем студенческое решение через GPT
        gpt_response = ask_gpt(student_solution)

        # Проверка студенческого решения на открытых и закрытых тестах
        test_results = check_solution_with_tests(student_solution, tests_df, task_id)

        # Добавляем результат в таблицу solutions
        solutions_df.at[index, 'author_comment'] = gpt_response
        solutions_df.at[index, 'author_comment_embedding'] = test_results

        # Добавляем данные в список для submit_example
        results.append({
            'solution_id': solution_id,
            'author_comment': gpt_response,
            'author_comment_embedding': test_results
        })

    return solutions_df, pd.DataFrame(results)  # Возвращаем как обновленные данные, так и для submit_example


def main():
    # Чтение данных из файлов Excel
    solutions_file = "./data/raw/train/solutions.xlsx"
    tasks_file = "./data/raw/train/tasks.xlsx"
    tests_file = "./data/raw/train/tests.xlsx"

    solutions_df = pd.read_excel(solutions_file)
    tasks_df = pd.read_excel(tasks_file)
    tests_df = pd.read_excel(tests_file)

    # Обработка решений студентов
    updated_solutions_df, submit_df = process_student_solutions(solutions_df, tasks_df, tests_df)

    # Сохранение обновленного файла solutions
    solutions_output_file = "./data/raw/train/processed_solutions.xlsx"
    updated_solutions_df.to_excel(solutions_output_file, index=False)
    print(f"Processing completed. Results saved to {solutions_output_file}")

    # Сохранение файла submit_example с нужными столбцами
    submit_output_file = "submit_example.csv"
    submit_df.to_excel(submit_output_file, index=False)
    print(f"Submit example saved to {submit_output_file}")


if __name__ == "__main__":
    main()
