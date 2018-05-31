import "babel-polyfill";

import { h, app } from "hyperapp"
import fetch from "isomorphic-fetch"
import vegaEmbed from 'vega-embed'

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
    currentModuleCode: null
}
const actions = {
    init: () => async (state, actions) => {
        const resp = await fetch('data/modules.json')
        if (resp.status >= 400) throw new Error("Bad response from server")
    
        const modules = await resp.json()
        actions.loadModules(modules)
    },
    loadModules: modules => state => ({ modules, currentModuleCode: Object.keys(modules)[0] }),
    changeModule: module => state => ({ currentModuleCode: module })
}

const AppView = (state, actions) => (
    <div>
        {Object.keys(state.modules).length < 1 ? 
            <Loading /> :
            <div>
                <ModuleSelector modules={state.modules} changeModule={actions.changeModule} />
                { state.currentModuleCode ? <Module module={state.modules[state.currentModuleCode]} /> : null }
            </div>
        }
    </div>
)

const Loading = () => (
    <div class="loading loading-lg"></div>
)

const ModuleSelector = ({ modules, changeModule }) => (
    <div id="module-selector">
        <select onchange={e => changeModule(e.target.value)}>
        { Object.keys(modules).map(module => (
            <option key={module} value={module}>{module}</option>
        )) }
        </select>
    </div>
)

const Module = ({ module }) => (
    <div key={module.module_code} id="module">
        <h2>{module.module_code} ({module.year}, semester {module.semester})<br /><span class="h6 label">{module.num_students} students</span></h2>
        
        <div oncreate={el => embedChart(el, "grade_histogram", module.grade_histogram)}></div>
        <ul class="module-stats">
            { Object.entries(transformStats(module.grade_statistics)).map(([ key, value ]) => (
                <li><span class="title">{key}</span><span class="value">{value}</span></li>
            )) }
        </ul>
        <div oncreate={el => embedChart(el, "grade_comparison_plot", module.grade_comparison_plot)}></div>
        { module.hasOwnProperty("student_feedback") ? 
            <StudentFeedback feedback={module.student_feedback} /> : 
            <p class="toast toast-error">No student feedback data available</p> }
        { module.hasOwnProperty("staff_feedback") ? 
            <StaffFeeback feedback={module.staff_feedback} /> :
            <p class="toast toast-error">No staff feedback data available</p> }
    </div>
)

const StudentFeedback = ({ feedback }) => (
    <div>
        <h3>Student feedback</h3>
        { feedback.histograms.map((hist, k) => (
            <div class="question" data-qnumber={k+1}>
                <h4>{formatQuestion(feedback.questions[k])}</h4>
                <div oncreate={el => embedChart(el, `student_feedback_histogram_${k+1}`, feedback.histograms[k])}></div>
                { feedback.text[k].length < 1 ? null : (
                    <div>
                        <h4>Responses</h4>
                        { feedback.text[k].map(response => (
                            <blockquote>{escapeHtml(response)}</blockquote>
                        )) }
                    </div>
                ) }
            </div>
        )) }

        { feedback.descriptive.map((desc, k) => {
            const key = feedback.histograms.length + k
            return (
                <div class="question" data-qnumber={key + 1}>
                    <h4>{formatQuestion(feedback.questions[key])}</h4>
                    <img src={feedback.descriptive[k].image} />
                    { feedback.descriptive[k].text.length < 1 ? null : (
                    <div>
                        <h4>Full responses</h4>
                        { feedback.descriptive[k].text.map(response => (
                            <blockquote>{escapeHtml(response)}</blockquote>
                        )) }
                    </div>
                ) }
                </div>
            )
        }) }
    </div>
)

const StaffFeeback = ({ feedback }) => (
    <div>
        <h3>Staff feedback</h3>
    </div>
)

app(state, actions, AppView, document.getElementById("root")).init()