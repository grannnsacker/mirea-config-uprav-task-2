import sys
import requests

DICTIONARY = dict()


def get_libra_name(text: str) -> str:
    '''Удаляем мусор из названия, т.е. версии и тд'''
    return text.split()[0].split(">")[0].split('=')[0].split('!')[0]


def get_dependencies(package_name):
    '''Метод парсинга зависимостей с сайта PYPI'''
    url = f"https://pypi.org/pypi/{package_name}/json"  # формируем ссылку, добавляя название пакета
    try:
        # пытаемся запарсить
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'info' in data:
            info = data['info']
            dependencies = info.get('requires_dist', list())
            # возвращаем данные
            return dependencies
        else:
            print(f"Информация о пакете '{package_name}' не найдена на PyPI.")
            return
    except requests.exceptions.HTTPError:
        print(f"Информация о пакете '{package_name}' не найдена на PyPI.")
        return


def get_dependency(package_name: str, cur_depth: int, max_depth: int) -> None:
    '''Рекурсивный обход и получание зависимостей'''
    if cur_depth == max_depth:
        # если текущий равен максимальной заданной, значит надо выходить
        return
    dependencies = get_dependencies(package_name.lower())
    if dependencies:
        for dependency in dependencies:
            parts = dependency.split(";")
            dep_name = get_libra_name(parts[0].strip())
            if package_name in DICTIONARY.keys():
                # уже есть в словаре, добавляем еще одну зависимость
                DICTIONARY[package_name].append(dep_name)
            else:
                # иначе создаем зависимость
                DICTIONARY[package_name] = [dep_name]
            get_dependency(dep_name, cur_depth + 1, max_depth)


def generate_dependency_graph(package_name: str, n: int) -> str or None:
    dependencies = get_dependencies(package_name.lower())
    get_dependency(package_name, 0, n)
    if dependencies:
        graphviz_dot = f'digraph G {{\n"{package_name}" [style=bold];\n'
        for i in DICTIONARY.keys():
            for j in DICTIONARY[i]:
                graphviz_dot += f'"{get_libra_name(i)}" -> "{get_libra_name(j)}";\n'
        graphviz_dot += '}'
        return graphviz_dot


def main():
    '''Основная функция программы'''
    if len(sys.argv) < 2:
        # значит не переданы все аргументы и надо вызвать ошибку
        print("Ошибка")
    else:
        # иначе все хорошо
        package_name = sys.argv[1]
        n = int(sys.argv[2])
        ans = generate_dependency_graph(package_name, n)
        if len(sys.argv) > 2 and sys.argv[-1] == '-f':
            with open(f'{package_name}.dot', 'w', encoding="utf-8") as f:
                f.write(ans)
        print(ans)


if __name__ == "__main__":
    main()
    # dot flask.dot -Tpng -o image.png