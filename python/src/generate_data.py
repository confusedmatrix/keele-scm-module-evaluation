import pandas as pd
import numpy as np
import os
import re
import json
from hashlib import sha512
from vega import VegaLite
from wordcloud import WordCloud

DATA_DIR = "../data"
OUT_DIR = "static/data"

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
    file = '{0}/raw/modules/{1}/grades.csv'.format(DATA_DIR, module)
    with open(file, "r") as f:
        fline = f.readline()
        assessment_weights = [int(weight)/100 for weight in re.findall(r"\(([0-9]+?)%?\)", fline)]
        # print("assessment weights", assessment_weights)

    grades = pd.read_csv(file, skiprows=[0])
    grades = grades[['#Ass#', 'Mark', '#Cand Key']]
    grades.columns = ['ass', 'grade', 'user']
    # grades['user'] = grades['user'].str.replace(r'#|/[0-9]', '').apply(lambda u: sha512(u.encode('utf-8')).hexdigest())
    grades['user'] = grades['user'].str.replace(r'#|/[0-9]', '').astype('int')
    grades = grades.set_index('user')
    grades['grade'] = grades['grade'].apply(pd.to_numeric, errors="coerce").fillna(0)

    assessments = grades['ass'].unique()
    module_grades = pd.DataFrame([], index=grades.index.unique())

    for k, ass in enumerate(assessments):
        assessment_grades = grades[grades['ass'] == ass]['grade'].to_frame()
        assessment_grades.columns = [ass]
        assessment_grades['{0}_weighted'.format(ass)] = assessment_grades[ass] * assessment_weights[k]
        module_grades = module_grades.merge(assessment_grades, left_index=True, right_index=True, how="outer")

    module_grades = module_grades.fillna(0)
    module_grades['final_grade'] = module_grades.filter(regex="_weighted").sum(axis=1)
    
    return module_grades, assessment_weights

def get_year_and_semester(module):
    file = '{0}/raw/modules/{1}/grades.csv'.format(DATA_DIR, module)
    grades = pd.read_csv(file, skiprows=[0])
    
    return (grades.iloc[0]['Year'], grades.iloc[0]['Period'])

def build_grade_histogram(height, width, data, grade_field, title):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": title,
        "height": height,
        "width": width,
        "layer": [
            {
                "mark": "bar",
                "encoding": {
                    "x": {
                        "bin": { "step": 10 },
                        "field": grade_field,
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
                        "field": grade_field,
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
                "mark": "point",
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
            },
            {
                "mark": "text",
                "encoding": {
                    "x": {
                        "value": width / 3
                    },
                    "y": {
                        "value": height / 10
                    },
                    "text": {
                        "value": "Students who achieved a better grade in this module than their average grade over all modules",
                    },
                }
            },
            {
                "mark": "text",
                "encoding": {
                    "x": {
                        "value": width - (width / 3)
                    },
                    "y": {
                        "value": height - (height / 10)
                    },
                    "text": {
                        "value": "Students who achieved a worse grade in this module than their average grade over all modules",
                    },
                }
            }
        ]
    }, data)

def get_la_data(module):
    file = '{0}/raw/modules/{1}/la.csv'.format(DATA_DIR, module)
    la = pd.read_csv(file)
    la['STU_ID'] = la['STU_ID'].astype('int')
    la_mean_per_user = la.drop(['USER', 'WK'], axis=1).groupby(['STU_ID']).sum()
    # la_mean_per_user['ACC_MEAN_DUR_WK0'] =  la_mean_per_user['ACC_MEAN_DUR_WK0'].apply(lambda x: x/12)
    la_mean_per_user = la_mean_per_user.apply(lambda x: x/12)
    la_mean_per_week = la.drop(['STU_ID', 'USER'], axis=1).groupby(['WK']).mean().reset_index()
    
    return la_mean_per_user, la_mean_per_week

def build_la_line_chart(height, width, data, field):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": la_field_to_chart_title(field),
        "height": height,
        "width": width,
        "layer": [
            {
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": 'WK',
                        "type": "quantitative",
                        "axis": { "title": "Week", "tickCount": 12 },
                    },
                    "y": {
                        "field": field,
                        "type": "quantitative",
                        "axis": { "title": la_field_to_axis_title(field) }
                    }
                }
            },
            {
                "mark": "point",
                "encoding": {
                    "x": {
                        "field": "WK",
                        "type": "quantitative",
                    },
                    "y": {
                        "field": field,
                        "type": "quantitative",
                    }
                }
            }
        ]
    }, data)

def get_la_vs_grades(la, grades):
    merged = la.merge(grades, how="left", left_index=True, right_index=True)
    
    return merged

def build_la_grade_comparison_plot(height, width, data, field):
    return VegaLite({
        "$schema": "https://vega.github.io/schema/vega-lite/v2.0.json",
        "title": la_field_to_chart_title(field),
        "height": height,
        "width": width,
        "layer": [
            {
                "mark": "point",
                "encoding": {
                    "x": {
                        "field": "final_grade",
                        "type": "quantitative",
                        "axis": { "title": "Final Grade" },
                        "scale": { "domain": [0, 100]}
                    },
                    "y": {
                        "field": field,
                        "type": "quantitative",
                        "axis": { "title": la_field_to_axis_title(field) }
                    }
                }
            }
        ]
    }, data)

def la_field_to_chart_title(field):
    if field == 'ACC_TOT_WK0':
        return 'Number of clicks in the KLE'
    elif field == 'ACC_DUR_WK0':
        return 'Time spent in the KLE'
    elif field == 'ACC_MEAN_DUR_WK0':
        return 'Time per session spent in the KLE'
    elif field ==  'ACC_COUNT_WK0':
        return 'Number of days per week that KLE was accessed'
    elif field == 'ABS_WK0':
        return 'Number of absences from scheduled teaching events'
    elif field == 'LC_TOT':
        return 'Number of views of lecture captures'
    elif re.search(r'C_GRP.*', field) is not None:
        return "Number of clicks within the '{0}' folder on the KLE".format(re.sub(r'C_GRP_|_WK0', '', field))

    return 'Unknown field label'

def la_field_to_axis_title(field):
    if field == 'ACC_TOT_WK0':
        return 'Clicks'
    elif field == 'ACC_DUR_WK0':
        return 'Total duration (mins)'
    elif field == 'ACC_MEAN_DUR_WK0':
        return 'Mean duration (mins)'
    elif field ==  'ACC_COUNT_WK0':
        return 'Days per week'
    elif field == 'ABS_WK0':
        return 'Absences'
    elif field == 'LC_TOT':
        return 'Lecture capture views'
    elif re.search(r'C_GRP.*', field) is not None:
        return "Clicks in '{0}' folder".format(re.sub(r'C_GRP_|_WK0', '', field))

    return 'Unknown field label'

def get_student_multi_choice_feedback(module, answers):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fbq = pd.DataFrame(fb.filter(regex=r"^\d\.", axis=1))
    fbq = fbq.drop(fbq.columns[len(fbq.columns)-2:], axis=1)

    fb_answers = pd.DataFrame(fbq.apply(pd.value_counts))
    answers = pd.DataFrame(answers, columns=["answer"])
    answers = pd.DataFrame(answers).merge(fb_answers, left_on="answer", right_index=True, how="left").fillna(0)
    answers.columns = ["answer"] + ["q{0}".format(i+1) for i in range(len(fbq.columns))]
    
    return fbq.columns.tolist(), answers

def get_textual_student_feedback(module):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb = fb.filter(regex=r"additional comments", axis=1)
    
    text_fb = []
    for col in fb:
        text_fb.append(fb[col].dropna().drop_duplicates().tolist())
    
    return text_fb

def get_descriptive_student_feedback(module):
    fb = pd.read_csv("{0}/raw/modules/{1}/feedback.csv".format(DATA_DIR, module))
    fb = fb.drop(fb.columns[0:-2], axis=1)
    
    desc_fb = []
    for col in fb:
        desc_fb.append(fb[col].dropna())
    
    return fb.columns.tolist(), desc_fb

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

def build_word_cloud(text, height, width):
    return WordCloud(background_color="black", colormap="GnBu", height=height, width=width, font_path="../fonts/caveat.ttf").generate(text)

def get_staff_feedback(module):
    fb = pd.read_csv("{0}/raw/staff-feedback.csv".format(DATA_DIR))
    mfb = fb[fb["Module Code"] == module]
    if len(mfb) < 1:
        return None
    return mfb.drop(["Timestamp", "Email address", "Module Code", "Module Name"], axis=1).iloc[0].to_dict()

def generate_data():
    print("Running analysis...")

    modules = get_modules("{0}/raw/modules/".format(DATA_DIR))
    height = 400
    width = 800
    mc_options = [
        "Strongly Agree",
        "Agree",
        "Disagree",
        "Strongly Disagree",
        "N/A"
    ]

    # Generate output directories
    mkdir("{0}/".format(OUT_DIR))
    mkdir("{0}/images".format(OUT_DIR))

    # Get grades & average grades for all modules
    all_grades = [get_grades(module)[0]["final_grade"] for module in modules]
    average_grades = pd.DataFrame(pd.concat(all_grades, axis=1).mean(axis=1), columns=["average_grade"])

    full_output = {}
    for i, module in enumerate(modules):

        mkdir("{0}/images/{1}".format(OUT_DIR, module))
        
        output = {}
        output["module_code"] = module
        print(f"{i+1}/{len(modules)} Generating data for {module}")
        
        try:
            module_grades, ass_weights = get_grades(module)
            output["num_students"] = module_grades.shape[0]
            
            year, semester = get_year_and_semester(module)
            output["year"] = year
            output["semester"] = re.sub(r"SEM", "", semester)
            
            output["grade_histograms"] = {}
            output["grade_histograms"]["assessments"] = []
            for i in range(len(ass_weights)):
                chart = build_grade_histogram(height, width, module_grades, "#0{0}".format(i+1), 'Assessment {0} grade histogram'.format(i+1))
                output["grade_histograms"]["assessments"].append(chart.spec)

            chart = build_grade_histogram(height, width, module_grades, 'final_grade', 'Final grade histogram')
            output["grade_histograms"]['final'] = chart.spec
            
            output["grade_statistics"] = get_grade_stats(module_grades)
            
            compare_grades = module_grades.merge(average_grades, left_index=True, right_index=True, how="left")

            chart = build_grade_comparison_plot(height, width, compare_grades)
            output["grade_comparison_plot"] = chart.spec
        except(FileNotFoundError):
            print("No grade data found for {0}".format(module))

        try:
            lapu, lapw = get_la_data(module)
            output["la"] = {}
            output["la"]['num_students'] = len(lapu)
            output["la"]["charts"] = {}
            for field in lapw.drop(['WK'], axis=1).columns:
                chart = build_la_line_chart(height, width, lapw, field)
                output["la"]["charts"][la_field_to_axis_title(field)] = chart.spec

            output["la"]["vs_charts"] = {}
            la_vs_grades = get_la_vs_grades(lapu, module_grades)
            for field in lapw.drop(['WK'], axis=1).columns:
                chart = build_la_grade_comparison_plot(height, width, la_vs_grades, field)
                output["la"]["vs_charts"][la_field_to_axis_title(field)] = chart.spec
        except(FileNotFoundError):
            print("No LA data found for {0}".format(module))
        
        try:
            smcq, smca = get_student_multi_choice_feedback(module, mc_options)
            
            output["student_feedback"] = {}
            output["student_feedback"]["questions"] = []
            output["student_feedback"]["histograms"] = []
            for i in range(1, len(smcq)+1):
                chart = build_student_feedback_histogram(height, width, smca, smcq, i)
                output["student_feedback"]["questions"].append(smcq[i-1])
                output["student_feedback"]["histograms"].append(chart.spec)

            output['student_feedback']["text"] = get_textual_student_feedback(module)

            # output['student_feedback']['descriptive'] = []
            # dfbq, dfba = get_descriptive_student_feedback(module)
            # for i in range(len(dfbq)):
            #     no_wordcloud = False
            #     try:
            #         wordcloud = build_word_cloud(dfba[i].str.cat(sep=" "), height, width)
            #         wordcloud.to_file("{0}/images/{1}/{2}.png".format(OUT_DIR, module, dfbq[i][0]))
            #     except(ValueError):
            #         no_wordcloud = True

            #     output["student_feedback"]["questions"].append(dfbq[i])
            #     output['student_feedback']['descriptive'].append({
            #         "image": None if no_wordcloud else "data/images/{0}/{1}.png".format(module, dfbq[i][0]),
            #         "text": dfba[i].tolist()
            #     })
            
        except(FileNotFoundError):
            print("No student feedback data found for {0}".format(module))

        # try:
        #     staff_feedback = get_staff_feedback(module)
        #     if staff_feedback == None:
        #         print("No staff feedback data found for {0}".format(module))
        #     else:
        #         output["staff_feedback"] = get_staff_feedback(module)
        # except(FileNotFoundError):
        #     print("No staff feedback data found for {0}".format(module))

        full_output[module] = output

    save_file("{0}/modules.json".format(OUT_DIR), json.dumps(full_output))

if __name__ == "__main__":
    generate_data()