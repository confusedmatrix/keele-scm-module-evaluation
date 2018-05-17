#!/usr/bin/env python 

import pandas as pd
import numpy as np
import os
import json
from hashlib import sha512
from vega3 import VegaLite
from IPython.display import display

DATA_DIR = "data"

def mkdir(directory):
    """
    :param string directory: 
    :return: 
    """
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    
def save_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)

def get_grades(module):
    grades = pd.read_csv('{0}/raw/modules/{1}/grades.csv'.format(DATA_DIR, module), skiprows=[0])
    grades = grades[['#Ass#', 'Mark', '#Cand Key']]
    grades.columns = ['ass', 'grade', 'user']
    grades['user'] = grades['user'].str.replace(r'#|/[0-9]', '').apply(lambda u: sha512(u.encode('utf-8')).hexdigest())
    grades = grades.set_index('user')

    assessments = grades['ass'].unique()
    assessment_weights = [0.8, 0.2]
    module_grades = pd.DataFrame([], index=grades.index.unique())

    for k, ass in enumerate(assessments):
        assessment_grades = grades[grades['ass'] == ass]['grade'].to_frame()
        assessment_grades.columns = [ass]
        assessment_grades['{0}_weighted'.format(ass)] = assessment_grades[ass] * assessment_weights[k]
        module_grades = module_grades.merge(assessment_grades, left_index=True, right_index=True, how="outer")

    module_grades = module_grades.fillna(0)
    module_grades['final_grade'] = module_grades.filter(regex="_weighted").sum(axis=1)
    
    return module_grades

def build_grade_histogram(height, width, data):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": "Module attainment histogram",
        "height": height,
        "width": width,
        "layer": [
            {
                "mark": "bar",
                "encoding": {
                    "x": {
                        "bin": True,
                        "field": "final_grade",
                        "type": "quantitative",
                        "axis": {
                            "title": "Grade"
                        }
                    },
                    "y": {
                        "aggregate": "count",
                        "type": "quantitative",
                        "axis": {
                            "title": "Number of students"
                        }
                    }
                }
            },
            {
                "mark": "rule",
                "encoding": {
                    "x": {
                        "value": width/100 * 40
                    },
                    "size": {
                        "value": 2
                    },
                    "color": {
                        "value": "#ccc"
                    }
                }
            },
            {
                "mark": "rule",
                "encoding": {
                    "x": {
                        "value": width/100 * 60
                    },
                    "size": {
                        "value": 2
                    },
                    "color": {
                        "value": "#ccc"
                    }
                }
            }
        ]
    }, data)

def get_grade_stats(grades):
    stats = {}
    stats["median"] = round(grades['final_grade'].median(), 1)
    stats["gte70"] = int(grades[grades['final_grade'] >= 70]['final_grade'].count())
    stats["gte60"] = int(grades[grades['final_grade'] >= 60]['final_grade'].count() - stats["gte70"])
    stats["lte40"] = int(grades[grades['final_grade'] <= 40]['final_grade'].count())
    stats["zeros"] = int(grades[grades['final_grade'] == 0]['final_grade'].count())

    return stats

def build_grade_comparison_plot(height, width, data):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": "Module performance comparison",
        "height": height,
        "width": width,
        "layer": [
            {
                "mark": "circle",
                "encoding": {
                    "x": {
                        "field": "average_grade",
                        "type": "quantitative",
                        "axis": {
                            "title": "Average Grade"
                        }
                    },
                    "y": {
                        "field": "final_grade", 
                        "typs": "quantitative",
                        "axis": {
                            "title": "Module grade"
                        }
                    }
                }
            },
            {
                "mark": "rule",
                "encoding": {
                    "x": {
                        "value": 0
                    },
                    "y": {
                        "value": height
                    },
                    "size": {
                        "value": 1
                    },
                    "color": {
                        "value": "red"
                    }
                }
            }
        ]
    }, data)

def get_student_feedback(module, questions, answers):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb_answers = pd.DataFrame(fb[questions])
    fb_answers = pd.DataFrame(fb_answers.apply(pd.value_counts))
    answers = pd.DataFrame(answers, columns=["answer"])
    answers = pd.DataFrame(answers).merge(fb_answers, left_on="answer", right_index=True, how="left").fillna(0)
    answers.columns = ["answer"] + ["q{0}".format(i+1) for i in range(len(questions))]
    
    return answers

def build_student_feedback_histogram(height, width, data, question):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": questions[question-1],
        "height": height,
        "width": width,
        "mark": "bar",
        "encoding": {
            "x": {
                "field": "answer",
                "type": "nominal",
                "sort": None,
                "title": ""
            },
            "y": {
                "field": "q{0}".format(question),
                "type": "quantitative",
                "title": "count"
            }
        }
    }, data)


modules = ['MAT-10044']
height = 400
width = 800
questions = [
    "1. Staff are good at explaining things",
    "2. The module was well organised.",
    "3. On this module, I have received sufficient advice and support with my studies.",
    "4. The module was interesting and engaging",
    "5. Practical / tutorial / workshop sessions were helpful.",
    "6. Useful support materials were made available on the KLE",
    "7. Overall, I am satisfied with the quality of this module. ",
]
answers = [
    "Strongly Agree",
    "Agree",
    "Disagree",
    "Strongly Disagree",
    "N/A"
]

# Generate output directory
mkdir("{0}/generated/".format(DATA_DIR))

for module in modules:
    
    output = {}
    output["module_code"] = module
    
    module_grades = get_grades(module)
    chart = build_grade_histogram(height, width, module_grades)
    output["grade_histogram"] = chart.spec
    
    output["grade_statistics"] = get_grade_stats(module_grades)
    
    average_grades = pd.DataFrame((np.random.random_sample(module_grades.shape[0]) * 100).round(1), columns=['average_grade'], index=module_grades.index)
    compare_grades = module_grades.merge(average_grades, left_index=True, right_index=True)

    chart = build_grade_comparison_plot(height, width, compare_grades)
    output["grade_comparison_plot"] = chart.spec
    
    sfb = get_student_feedback(module, questions, answers)
    
    output["student_feedback"] = {}
    output["student_feedback"]['histograms'] = []
    for i in range(1, len(questions)+1):
        chart = build_student_feedback_histogram(height, width, sfb, i)
        output["student_feedback"]['histograms'].append(chart.spec)

    save_file("{0}/generated/{1}.json".format(DATA_DIR, module), json.dumps(output))
