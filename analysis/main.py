#!/usr/bin/env python 

import pandas as pd
import numpy as np
import os
import re
import json
from hashlib import sha512
from vega import VegaLite
from wordcloud import WordCloud

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

def get_modules(root):
    modules = [item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item))]
    
    return modules

def get_grades(module):
    print(module)
    file = '{0}/raw/modules/{1}/grades.csv'.format(DATA_DIR, module)
    with open(file, "r") as f:
        fline = f.readline()
        assessment_weights = [int(weight)/100 for weight in re.findall(r"\(([0-9]+?)%?\)", fline)]
        print("assessment weights", assessment_weights)

    grades = pd.read_csv(file, skiprows=[0])
    grades = grades[['#Ass#', 'Mark', '#Cand Key']]
    grades.columns = ['ass', 'grade', 'user']
    grades['user'] = grades['user'].str.replace(r'#|/[0-9]', '').apply(lambda u: sha512(u.encode('utf-8')).hexdigest())
    grades = grades.set_index('user')
    grades['grade'] = grades['grade'].apply(pd.to_numeric, errors="coerce").fillna(0)

    assessments = grades['ass'].unique()
    module_grades = pd.DataFrame([], index=grades.index.unique())

    for k, ass in enumerate(assessments):
        assessment_grades = grades[grades['ass'] == ass]['grade'].to_frame()
        assessment_grades.columns = [ass]
        # print(assessment_grades[ass])
        assessment_grades['{0}_weighted'.format(ass)] = assessment_grades[ass] * assessment_weights[k]
        module_grades = module_grades.merge(assessment_grades, left_index=True, right_index=True, how="outer")

    module_grades = module_grades.fillna(0)
    module_grades['final_grade'] = module_grades.filter(regex="_weighted").sum(axis=1)
    
    print("done")
    return module_grades

def get_year_and_semester(module):
    file = '{0}/raw/modules/{1}/grades.csv'.format(DATA_DIR, module)
    grades = pd.read_csv(file, skiprows=[0])
    
    return (grades.iloc[0]['Year'], grades.iloc[0]['Period'])

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
                        "bin": { "step": 10 },
                        "field": "final_grade",
                        "type": "quantitative",
                        "axis": { "title": "Grade", "tickCount": 10 },
                        "scale": { "domain": [0, 100] }
                    },
                    "y": {
                        "aggregate": "count",
                        "type": "quantitative",
                        "axis": { "title": "Number of students" }
                    },
                    "color": {
                        "bin": { "step": 10 },
                        "field": "final_grade",
                        "type": "quantitative",
                        "legend": None
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
                        "axis": { "title": "Average Grade" },
                        "scale": { "domain": [0, 100] }
                    },
                    "y": {
                        "field": "final_grade", 
                        "typs": "quantitative",
                        "axis": { "title": "Module grade" },
                        "scale": { "domain": [0, 100] }
                    },
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

def get_student_multi_choice_feedback(module, questions, answers):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb_answers = pd.DataFrame(fb[questions])
    fb_answers = pd.DataFrame(fb_answers.apply(pd.value_counts))
    answers = pd.DataFrame(answers, columns=["answer"])
    answers = pd.DataFrame(answers).merge(fb_answers, left_on="answer", right_index=True, how="left").fillna(0)
    answers.columns = ["answer"] + ["q{0}".format(i+1) for i in range(len(questions))]
    
    return answers

def get_textual_student_feedback(module):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb = fb.filter(regex=r"additional comments", axis=1)
    
    text_fb = []
    for col in fb:
        text_fb.append(fb[col].dropna().tolist())
    
    return text_fb

def get_descriptive_student_feedback(module, questions):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb = fb.filter(questions, axis=1)
    
    desc_fb = []
    for col in fb:
        desc_fb.append(fb[col].dropna())
    
    return desc_fb

def build_student_feedback_histogram(height, width, data, questions, question):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        # "title": """",
        "height": height,
        "width": width,
        "mark": "bar",
        "encoding": {
            "x": {
                "field": "answer",
                "type": "nominal",
                "sort": None,
                "axis": { "title": "" }
            },
            "y": {
                "field": "q{0}".format(question),
                "type": "quantitative",
                "axis": { "title": "count" }
            },
            "color": {
                "field": "answer",
                "type": "nominal",
                "legend": None,
            }
        }
    }, data)

def build_word_cloud(text):
    return WordCloud(background_color="black", colormap="GnBu", height=height, width=width, font_path="analysis/fonts/caveat.ttf").generate(text)

def get_staff_feedback(module):
    fb = pd.read_csv("{0}/raw/staff-feedback.csv".format(DATA_DIR))
    mfb = fb[fb["Module Code"] == module]
    if len(mfb) < 1:
        return None
    return mfb.drop(["Timestamp", "Email address", "Module Code", "Module Name"], axis=1).iloc[0].to_dict()



# -------------------------------------------- #

modules = get_modules("{0}/raw/modules/".format(DATA_DIR))
height = 400
width = 800
mc_questions = [
    "1. Staff are good at explaining things",
    "2. The module was well organised.",
    "3. On this module, I have received sufficient advice and support with my studies.",
    "4. The module was interesting and engaging",
    "5. Practical / tutorial / workshop sessions were helpful.",
    "6. Useful support materials were made available on the KLE",
    "7. Overall, I am satisfied with the quality of this module. ",
]
mc_answers = [
    "Strongly Agree",
    "Agree",
    "Disagree",
    "Strongly Disagree",
    "N/A"
]
desc_questions = [
    "8. Was there anything in particular which you enjoyed in this module? ",
    "9. If you could improve one thing about this module, what would it be?"
]


# -------------------------------------------- #

print("Running analysis...")

# Generate output directories
mkdir("{0}/generated/".format(DATA_DIR))
mkdir("{0}/generated/images".format(DATA_DIR))

# Get grades & average grades for all modules
all_grades = [get_grades(module)["final_grade"] for module in modules]
average_grades = pd.DataFrame(pd.concat(all_grades, axis=1).mean(axis=1), columns=["average_grade"])

full_output = {}
for module in modules:

    mkdir("{0}/generated/images/{1}".format(DATA_DIR, module))
    
    output = {}
    output["module_code"] = module
    
    try:
        module_grades = get_grades(module)
        output["num_students"] = module_grades.shape[0]
        
        year, semester = get_year_and_semester(module)
        output["year"] = year
        output["semester"] = re.sub(r"SEM", "", semester)

        chart = build_grade_histogram(height, width, module_grades)
        output["grade_histogram"] = chart.spec
        
        output["grade_statistics"] = get_grade_stats(module_grades)
        
        compare_grades = module_grades.merge(average_grades, left_index=True, right_index=True, how="left")

        chart = build_grade_comparison_plot(height, width, compare_grades)
        output["grade_comparison_plot"] = chart.spec
    except(FileNotFoundError):
        print("No grade data found for {0}".format(module))
    
    try:
        smcfb = get_student_multi_choice_feedback(module, mc_questions, mc_answers)
        
        output["student_feedback"] = {}
        output["student_feedback"]["questions"] = []
        output["student_feedback"]["histograms"] = []
        for i in range(1, len(mc_questions)+1):
            chart = build_student_feedback_histogram(height, width, smcfb, mc_questions, i)
            output["student_feedback"]["questions"].append(mc_questions[i-1])
            output["student_feedback"]["histograms"].append(chart.spec)

        output['student_feedback']["text"] = get_textual_student_feedback(module)

        output['student_feedback']['descriptive'] = []
        dfb = get_descriptive_student_feedback(module, desc_questions)
        for i in range(len(desc_questions)):
            wordcloud = build_word_cloud(dfb[i].str.cat(sep=" "))
            wordcloud.to_file("{0}/generated/images/{1}/{2}.png".format(DATA_DIR, module, desc_questions[i][0]))

            output["student_feedback"]["questions"].append(desc_questions[i])
            output['student_feedback']['descriptive'].append({
                "image": "{0}/images/{1}/{2}.png".format(DATA_DIR, module, desc_questions[i][0]),
                "text": dfb[i].tolist()
            })
        
    except(FileNotFoundError):
        print("No student feedback data found for {0}".format(module))

    try:
        staff_feedback = get_staff_feedback(module)
        if staff_feedback == None:
            print("No staff feedback data found for {0}".format(module))
        else:
            output["staff_feedback"] = get_staff_feedback(module)
    except(FileNotFoundError):
        print("No staff feedback data found for {0}".format(module))

    full_output[module] = output

save_file("{0}/generated/modules.json".format(DATA_DIR), json.dumps(full_output))
