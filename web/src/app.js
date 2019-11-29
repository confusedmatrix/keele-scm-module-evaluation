import "babel-polyfill"

import { h, app } from "hyperapp"
// import fetch from "isomorphic-fetch"
import vegaEmbed from 'vega-embed'

// import modules from '../dist/data/modules.json'
import { Model } from "vega-lite/build/src/compile/model";
import { labelAlign } from "vega-lite/build/src/compile/layout/header";

const embedChart = (parent, id, json) => {
    const div = document.createElement('div')
    div.id = id
    parent.appendChild(div)
    vegaEmbed(`#${id}`, json, { actions: false, renderer: "svg" })
}

const escapeHtml = unsafe => {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

const formatQuestion = question => question.replace(/\d+\.\s+/, "")

const transformStats = stats => ({
    "median": stats.median,
    ">=70": stats.gte70,
    ">=60": stats.gte60,
    "<=40": stats.lte40,
    "Zero": stats.zeros
})

const state = {
    subject: "",
    modules: {},
    currentModuleCode: null,
    currentLAChart: null,
    currentLAVsGradesChart: null,
    printing: false,
    regenerating: false,
}
const actions = {
    init: () => async (state, actions) => {
        const cachebust = new Date().getTime()
        const resp = await fetch(`data/modules.json?${cachebust}`)
        if (resp.status >= 400) throw new Error("Bad response from server")

        const modules = await resp.json()
        actions.loadModules(modules)
    },
    // TODO regenerate data currently doesn't account for subject
    regenerateData: () => async (state, actions) => {
        actions.clearModules()
        actions.regenerating()
        const resp = await fetch('/api/regenerate-data')
        if (resp.status >= 400) throw new Error("Bad response from server")

        const payload = await resp.json()
        actions.init()
    },
    regenerating: () => state => ({ regenerating: true }),
    clearModules: () => state => ({ modules: {}, currentModuleCode: null }),
    loadModules: modules => state => {
        const subject_regex = state.subject === "CSC" ? /CSC|CSY/ : /MAT/
        const module_keys = state.subject === "" ? Object.keys(modules) : Object.keys(modules).filter(module => module.search(subject_regex) !== -1)
        const filtered_modules = module_keys.reduce((a, m) => {
            a[m] = modules[m]
            return a
        }, {})
        return ({
            modules: filtered_modules,
            currentModuleCode: Object.keys(filtered_modules).sort()[0],
            regenerating: false
        })
    },
    changeModule: module => state => ({ currentModuleCode: module, currentLAChart: null, currentLAVsGradesChart: null }),
    changeLAChart: field => state => ({ currentLAChart: field }),
    changeLAVsGradesChart: field => state => ({ currentLAVsGradesChart: field }),
    printAll: () => (state, actions) => {
        setTimeout(() => window.print(), 1000)
        return ({ printing: true })
    },
    setSubject: subject => state => ({ subject }),
    logState: () => state => console.log(state),
}

const AppView = (state, actions) => {
    if (state.printing) {
        return <PrintView modules={state.modules} />
    }

    return (
        <div>
            <Header
                subject={state.subject}
                modules={state.modules}
                regenerating={state.regenerating}
                changeModule={actions.changeModule}
                printAll={actions.printAll}
                regenerateData={actions.regenerateData} />
            {Object.keys(state.modules).length < 1 ? <Loading /> : null}
            {state.currentModuleCode ? <Module module={state.modules[state.currentModuleCode]}
                                               currentLAChart={state.currentLAChart}
                                               currentLAVsGradesChart={state.currentLAVsGradesChart}
                                               changeLAChart={actions.changeLAChart}
                                               changeLAVsGradesChart={actions.changeLAVsGradesChart} /> : null}
        </div>
    )
}

const PrintView = ({ modules }) => (
    <div id="print-modules">
        {Object.keys(modules).sort().map(k => <Module module={modules[k]} />)}
    </div>
)

const Loading = () => (
    <div class="loading loading-lg"></div>
)

const Header = ({ subject, modules, regenerating, changeModule, printAll, regenerateData }) => (
    <div id="header">
        <div class="container grid-lg">
            <div class="columns">
                <div class="column col-8 col-md-12">
                    <h1>{"Module evaluation" + (subject === "CSC" ? " (Comp Sci)" : (subject === "MAT" ? " (Maths)" : ""))}</h1>
                </div>
                <div class="column col-4 col-md-12 form-group">
                    <label class="form-label form-inline">Select a module</label>
                    <select class="form-select form-inline" onchange={e => changeModule(e.target.value)}>
                        {Object.keys(modules).length < 1 ? <option>No modules</option> : Object.keys(modules).sort().map(module => (
                            <option key={module} value={module}>{module}</option>
                        ))}
                    </select>
                    {/* <button class="btn" onclick={e => regenerateData()}>{regenerating ? "Regenerating..." : "Regenerate all data"}</button>
                    <button class="btn btn-primary print-btn form-inline" onclick={e => printAll()}>Print all modules</button> */}
                </div>
            </div>
        </div>
    </div>
)

const Module = ({ module, currentLAChart, currentLAVsGradesChart, changeLAChart, changeLAVsGradesChart }) => (
    <div key={module.module_code} class="module">
        {/* <h2>{module.module_code}</h2> */}
        <h2>{module.module_code} ({module.year}, semester {module.semester})<br /><span class="h6 label">{module.num_students} students</span></h2>

        <h3>Individual assessment performance</h3>
        {module.grade_histograms.assessments.map((hist, k) => (
            <div oncreate={el => embedChart(el, `assessment_histogram_${k + 1}`, hist)}></div>
        ))}

        <h3>Final attainment</h3>
        <div oncreate={el => embedChart(el, "grade_histogram", module.grade_histograms.final)}></div>
        <ul class="module-stats">
            {Object.entries(transformStats(module.grade_statistics)).map(([key, value]) => (
                <li><span class="title">{key}</span><span class="value">{value}</span></li>
            ))}
        </ul>
        <div oncreate={el => embedChart(el, "grade_comparison_plot", module.grade_comparison_plot)}></div>

        {module.hasOwnProperty("la") ?
            <LearningAnalytics la={module.la} 
                               currentLAChart={currentLAChart}
                               currentLAVsGradesChart={currentLAVsGradesChart}
                               changeLAChart={changeLAChart} 
                               changeLAVsGradesChart={changeLAVsGradesChart} /> :
            <p class="toast toast-error">No learning analytics data available</p>}

        {module.hasOwnProperty("student_feedback") ?
            <StudentFeedback feedback={module.student_feedback} /> :
            <p class="toast toast-error">No student feedback data available</p>}
        {/* { module.hasOwnProperty("staff_feedback") ? 
            <StaffFeeback feedback={module.staff_feedback} /> :
            <p class="toast toast-error">No staff feedback data available</p> } */}
    </div>
)

const LearningAnalytics = ({ la, currentLAChart, currentLAVsGradesChart, changeLAChart, changeLAVsGradesChart }) => (
    <div id="learning-analytics">
        <h3>Learning analytics <span class="h6 label">based on {la.num_students} students</span></h3>

        <div class="container">
            <div class="columns">
                <div class="column col-8 col-md-12">
                    <h4>Per-week learning analytics stats<br /><small>Averaged over all students</small></h4>
                </div>
                <div class="column col-4 col-md-12 form-group">
                    <select class="form-select form-inline" onchange={e => changeLAChart(e.target.value)}>
                        {Object.keys(la.charts).map(field => (
                            <option key={field} value={field}>{field}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
        <div oncreate={el => embedChart(el, `la_chart`, currentLAChart == null ? la.charts[Object.keys(la.charts)[0]] : la.charts[currentLAChart])}
             onupdate={el => embedChart(el, `la_chart`, currentLAChart == null ? la.charts[Object.keys(la.charts)[0]] : la.charts[currentLAChart])}></div>
        
        <div class="container">
            <div class="columns">
                <div class="column col-8 col-md-12">
                    <h4>Student learning analytics vs attainment<br /><small>Averaged over all weeks</small></h4>
                </div>
                <div class="column col-4 col-md-12 form-group">
                    <select class="form-select form-inline" onchange={e => changeLAVsGradesChart(e.target.value)}>
                        {Object.keys(la.vs_charts).map(field => (
                            <option key={field} value={field}>{field}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
        <div oncreate={el => embedChart(el, `la_vs_chart`, currentLAVsGradesChart == null ? la.vs_charts[Object.keys(la.charts)[0]] : la.vs_charts[currentLAVsGradesChart])}
             onupdate={el => embedChart(el, `la_vs_chart`, currentLAVsGradesChart == null ? la.vs_charts[Object.keys(la.charts)[0]] : la.vs_charts[currentLAVsGradesChart])}></div>
    </div>
)

const StudentFeedback = ({ feedback }) => (
    <div>
        <h3>Student feedback</h3>
        {feedback.histograms.map((hist, k) => (
            <div class="question" data-qnumber={k + 1}>
                <h4>{formatQuestion(feedback.questions[k])}</h4>
                <div oncreate={el => embedChart(el, `student_feedback_histogram_${k + 1}`, feedback.histograms[k])}></div>
                {!feedback.text[k] || feedback.text[k].length < 1 ? null : (
                    <div>
                        <h4>Responses</h4>
                        {feedback.text[k].map(response => (
                            <blockquote innerHTML={escapeHtml(response)}></blockquote>
                        ))}
                    </div>
                )}
            </div>
        ))}

        {/* Word clouds */}
        {/* {feedback.descriptive.map((desc, k) => {
            const key = feedback.histograms.length + k
            return (
                <div class="question" data-qnumber={key + 1}>
                    <h4>{formatQuestion(feedback.questions[key])}</h4>
                    {feedback.descriptive[k].image ? <img src={feedback.descriptive[k].image} /> : null}
                    {feedback.descriptive[k].text.length < 1 ? null : (
                        <div>
                            <h4>Full responses</h4>
                            {feedback.descriptive[k].text.map(response => (
                                <blockquote innerHTML={escapeHtml(response)}></blockquote>
                            ))}
                        </div>
                    )}
                </div>
            )
        })} */}
    </div>
)

const StaffFeeback = ({ feedback }) => (
    <div>
        <h3>Staff feedback</h3>
        <div class="staff-feedback">
            {Object.entries(feedback).map(([key, value]) => (
                <div>
                    <h4>{key}</h4>
                    <p innerHTML={escapeHtml(value)}></p>
                </div>
            ))}
        </div>
    </div>
)

const hash = new URL(document.location).hash
const subject = hash.replace("#", "")

const App = app(state, actions, AppView, document.getElementById("root"))
App.setSubject(subject)
App.init()