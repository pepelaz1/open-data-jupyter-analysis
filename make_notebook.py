"""Build a reproducible Jupyter example from the unchanged source CSV."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "gapminder2007.csv"
TARGET = ROOT / "gapminder_analysis.ipynb"

df = pd.read_csv(SOURCE)
assert len(df) >= 100
assert {"country", "continent", "lifeExp"}.issubset(df.columns)
assert not df[["country", "continent", "lifeExp"]].isna().any().any()
assert df["country"].is_unique

comparison = (
    df[df["continent"].isin(["Africa", "Europe"])]
    .groupby("continent")["lifeExp"]
    .agg(["count", "mean", "median", "min", "max"])
)
africa = comparison.loc["Africa"]
europe = comparison.loc["Europe"]
difference = europe["mean"] - africa["mean"]


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md("""# Продолжительность жизни по континентам, 2007 год

**Вопрос:** как различается средняя ожидаемая продолжительность жизни между Африкой и Европой в опубликованном наборе Gapminder за 2007 год?

**Источник:** [Plotly datasets / gapminder2007.csv](https://github.com/plotly/datasets/blob/master/gapminder2007.csv). Исходный файл скачан 18.11.2026 и сохранён в `data/gapminder2007.csv` без правок. Каждая строка — одна страна в 2007 году; `continent` — категория, `lifeExp` — ожидаемая продолжительность жизни в годах, `pop` — численность населения, `gdpPercap` — ВВП на душу населения. Очистка, если она понадобится, выполняется только кодом ниже.
"""),
    code("""from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

source = Path('data/gapminder2007.csv')
df = pd.read_csv(source)
assert len(df) >= 100, 'В исходном файле должно быть не менее 100 строк'
print(f'Строк: {len(df)}; колонок: {len(df.columns)}')
display(df.head())
"""),
    md("""## Проверка качества данных

Показываем число строк, пропуски по каждому полю и повторы стран. Исходный CSV не изменяем.
"""),
    code("""print('Пропуски по колонкам:')
display(df.isna().sum().rename('missing').to_frame())
print('Повторы стран:', int(df['country'].duplicated().sum()))
"""),
    md("""## Пять показателей

Считаем количество стран, частоты категорий, среднее, медиану, минимум и максимум для `lifeExp`. Среднее здесь простое по странам: каждая страна имеет одинаковый вес.
"""),
    code("""print('Количество стран:', len(df))
display(df['continent'].value_counts().rename('countries').to_frame())
display(df['lifeExp'].agg(['mean', 'median', 'min', 'max']).rename('lifeExp_years').to_frame())
"""),
    md("""## Сравнение двух групп

Берём только Африку и Европу. Считаем те же показатели отдельно для каждой группы и разницу средних.
"""),
    code("""selected = df[df['continent'].isin(['Africa', 'Europe'])].copy()
groups = selected.groupby('continent')['lifeExp'].agg(['count', 'mean', 'median', 'min', 'max'])
display(groups.round(2))
difference = groups.loc['Europe', 'mean'] - groups.loc['Africa', 'mean']
print(f'Разница средних: {difference:.2f} года')
"""),
    code("""ax = groups['mean'].reindex(['Africa', 'Europe']).plot.bar(
    color=['#466c9b', '#e08a3f'], figsize=(6, 4), rot=0
)
ax.set(title='Средняя ожидаемая продолжительность жизни, 2007',
       xlabel='Континент', ylabel='Лет')
ax.bar_label(ax.containers[0], fmt='%.1f')
plt.tight_layout()
plt.show()
"""),
    md(f"""## Вывод

В исходном наборе **{len(df)} страны**. Среди них **{int(africa['count'])} стран Африки** и **{int(europe['count'])} стран Европы**. Средняя ожидаемая продолжительность жизни составляет **{africa['mean']:.2f} года** в Африке и **{europe['mean']:.2f} года** в Европе; разница — **{difference:.2f} года**. Медианы: **{africa['median']:.2f}** и **{europe['median']:.2f} года** соответственно.

**Ограничение:** это данные только за 2007 год, поэтому результат не описывает сегодняшнюю ситуацию. Сравнение даёт одинаковый вес каждой стране, независимо от численности населения; оно не доказывает причину различий.
"""),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Created {TARGET}")
print(f"Africa={africa['mean']:.2f}, Europe={europe['mean']:.2f}, difference={difference:.2f}")
