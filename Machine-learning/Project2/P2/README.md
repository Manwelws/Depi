# Machine Learning Engineer Nanodegree
## Supervised Learning
### Finding Donors for *CharityML*

The second project of the ML Engineer nanodegree. The goal is straightforward on paper:
figure out who earns more than \$50,000 a year from the 1994 U.S. Census data, because
those are the people most likely to donate to a charity. What's not straightforward is
everything in between — cleaning, encoding, choosing a metric that actually matches the
business problem, comparing models honestly, and tuning without fooling yourself.

## What's in here

| File | What it is |
| :--- | :--- |
| `finding_donors.ipynb` | The project itself. All eight questions answered, every cell executed. |
| `census.csv` | The dataset: 45,222 records, 13 features, 1 binary target. |
| `visuals.py` | Provided plotting helpers. Used as-is, untouched. |
| `project_description.md` | The original assignment brief. |
| `report.html` | HTML export of the finished notebook. |

## Setup

You'll need:

- [Python](https://www.python.org/downloads/) 3.11 or newer
- [NumPy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [scikit-learn](https://scikit-learn.org/)

The cleanest way to get all of that is [uv](https://docs.astral.sh/uv/) or
[Anaconda](https://docs.continuum.io/anaconda/), either of which will set you up in one
command. If you're using the repo's existing environment, it already has everything
except the notebook tooling:

```bash
uv pip install nbformat nbconvert
```

> **A note on the original requirements.** The assignment brief asks for Python 2.7 and
> scikit-learn 0.16, which are both long past end-of-life. This notebook was written and
> run on **Python 3.14.7** with **scikit-learn 1.9**, **pandas 3.0** and **NumPy 2.5**.
> The only real changes were mechanical — `sklearn.cross_validation` moved to
> `sklearn.model_selection`, and a couple of indexing calls that pandas 3 no longer
> accepts. None of the actual machine learning changed.

## Running it

From this directory:

```bash
jupyter notebook finding_donors.ipynb
```

Full execution takes roughly two and a half minutes, almost all of it in the grid search.
To re-run everything headlessly and regenerate the report:

```bash
python -m nbconvert --to notebook --execute --inplace finding_donors.ipynb
python -m nbconvert --to html finding_donors.ipynb
```

## What the project actually does

1. **Explore** — 45,222 people, of whom 11,208 (24.8%) earn over \$50K.
2. **Preprocess** — log-transform the badly skewed `capital-gain` and `capital-loss`,
   min-max scale the five numeric columns, one-hot encode the categorical ones. That
   takes 13 raw columns to 103.
3. **Benchmark** — score a naive "everyone is a donor" predictor (accuracy 0.248,
   F₀.₅ 0.292) so there's a floor to beat, then compare logistic regression, a random
   forest and AdaBoost at 1%, 10% and 100% of the training data.
4. **Tune** — grid search AdaBoost, the winner, over `n_estimators` and `learning_rate`.
5. **Interpret** — pull out the five features carrying most of the model's weight, then
   retrain on just those five and see what's lost.

## Results

| | Accuracy | F-score |
| :--- | :---: | :---: |
| Naive predictor | 0.2478 | 0.2917 |
| AdaBoost (default) | 0.8483 | 0.7029 |
| **AdaBoost (tuned)** | **0.8499** | **0.7133** |
| AdaBoost (tuned, top 5 features only) | 0.8472 | 0.7074 |

Scoring on F₀.₅ rather than accuracy is the point of the whole exercise. The classes are
badly imbalanced — three quarters of people earn under \$50K — so accuracy alone would
let a model that predicts "no" every single time score 0.75 while identifying not one
donor. F₀.₅ weights precision over recall, which is the right bias here: CharityML would
rather miss a donor than waste a mailing on someone who can't afford to give.

## The data

A modified version of the UCI Census Income dataset, donated by Ron Kohavi and Barry
Becker and published in *"Scaling Up the Accuracy of Naive-Bayes Classifiers: A
Decision-Tree Hybrid"* ([KDD 1996](https://www.aaai.org/Papers/KDD/1996/KDD96-033.pdf)).
The original is hosted at [UCI](https://archive.ics.uci.edu/ml/datasets/Census+Income).
The `fnlwgt` column has been removed, along with any rows containing missing or
malformed values.

**Features**

- `age` — Age
- `workclass` — Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked
- `education_level` — Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool
- `education-num` — Years of schooling completed
- `marital-status` — Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse
- `occupation` — Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces
- `relationship` — Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried
- `race` — White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black
- `sex` — Female, Male
- `capital-gain` — Monetary capital gains
- `capital-loss` — Monetary capital losses
- `hours-per-week` — Average hours worked per week
- `native-country` — Country of origin

**Target**

- `income` — `<=50K` or `>50K`