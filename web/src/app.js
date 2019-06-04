import "babel-polyfill";

import { h, app } from "hyperapp"
// import fetch from "isomorphic-fetch"
import vegaEmbed from 'vega-embed'

import modules from '../dist/data/modules.json'
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
    modules: {},
    // modules,
    currentModuleCode: null,
    // currentModuleCode: Object.keys(modules).sort()[0],
    printing: false
}
const actions = {
    init: () => async (state, actions) => {
        const resp = await fetch('data/modules.json')
        if (resp.status >= 400) throw new Error("Bad response from server")

        const modules = await resp.json()
        actions.loadModules(modules)
    },
    regenerateData: () => async (state, actions) => {
        actions.clearModules()
        const resp = await fetch('api/regenerate-data')
        if (resp.status >= 400) throw new Error("Bad response from server")

        const payload = await resp.json()
        actions.init()
    },
    clearModules: () => state => ({ modules: {}, currentModuleCode: null }),
    loadModules: modules => state => ({ modules, currentModuleCode: Object.keys(modules)[0] }),
    changeModule: module => state => ({ currentModuleCode: module }),
    printAll: () => (state, actions) => {
        setTimeout(() => window.print(), 1000)
        return ({ printing: true })
    },
    logState: () => state => console.log(state),
}

const AppView = (state, actions) => {
    if (Object.keys(state.modules).length < 1) {
        return <Loading />

    } else if (state.printing) {
        return <PrintView modules={modules} />
    }

    return (
        <div>
            <Header
                modules={state.modules}
                changeModule={actions.changeModule}
                printAll={actions.printAll}
                regenerateData={actions.regenerateData} />
            {state.currentModuleCode ? <Module module={state.modules[state.currentModuleCode]} /> : null}
        </div>
    )
}

const PrintView = ({ modules }) => (
    <div id="print-modules">
        {Object.values(modules).map(module => <Module module={module} />)}
    </div>
)

const Loading = () => (
    <div class="loading loading-lg"></div>
)

const Header = ({ modules, changeModule, printAll, regenerateData }) => (
    <div id="header" class="form-group">
        <label class="form-label form-inline">Select a module</label>
        <select class="form-select form-inline" onchange={e => changeModule(e.target.value)}>
            {Object.keys(modules).sort().map(module => (
                <option key={module} value={module}>{module}</option>
            ))}
        </select>
        <button class="btn" onclick={e => regenerateData()}>Regenerate all data</button>
        <button class="btn btn-primary print-btn form-inline" onclick={e => printAll()}>Print all modules</button>
    </div>
)

const Module = ({ module }) => (
    <div key={module.module_code} class="module">
        <h2>{module.module_code}</h2>
        {/* <h2>{module.module_code} ({module.year}, semester {module.semester})<br /><span class="h6 label">{module.num_students} students</span></h2> */}

        {/* <div oncreate={el => embedChart(el, "grade_histogram", module.grade_histogram)}></div>
        <ul class="module-stats">
            { Object.entries(transformStats(module.grade_statistics)).map(([ key, value ]) => (
                <li><span class="title">{key}</span><span class="value">{value}</span></li>
            )) }
        </ul>
        <div oncreate={el => embedChart(el, "grade_comparison_plot", module.grade_comparison_plot)}></div> */}
        {module.hasOwnProperty("student_feedback") ?
            <StudentFeedback feedback={module.student_feedback} /> :
            <p class="toast toast-error">No student feedback data available</p>}
        {/* { module.hasOwnProperty("staff_feedback") ? 
            <StaffFeeback feedback={module.staff_feedback} /> :
            <p class="toast toast-error">No staff feedback data available</p> } */}
    </div>
)

const StudentFeedback = ({ feedback }) => (
    <div>
        <h3>Student feedback</h3>
        {feedback.histograms.map((hist, k) => (
            <div class="question" data-qnumber={k + 1}>
                <h4>{formatQuestion(feedback.questions[k])}</h4>
                <div oncreate={el => embedChart(el, `student_feedback_histogram_${k + 1}`, feedback.histograms[k])}></div>
                {feedback.text[k].length < 1 ? null : (
                    <div>
                        <h4>Responses</h4>
                        {feedback.text[k].map(response => (
                            <blockquote innerHTML={escapeHtml(response)}></blockquote>
                        ))}
                    </div>
                )}
            </div>
        ))}

        {feedback.descriptive.map((desc, k) => {
            const key = feedback.histograms.length + k
            return (
                <div class="question" data-qnumber={key + 1}>
                    <h4>{formatQuestion(feedback.questions[key])}</h4>
                    <img src={feedback.descriptive[k].image} />
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
        })}
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

app(state, actions, AppView, document.getElementById("root")).init()