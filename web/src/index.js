import vegaEmbed, { vega } from 'vega-embed'
import module from '../../data/generated/MAT-10044.json'

const embedChart = (parent, id, json) => {
    const div = document.createElement('div')
    div.id = id
    parent.appendChild(div)
    vegaEmbed(`#${id}`, json, { actions: false })
}

const loadModule = (parent, module) => {
    parent.innerHTML = ""
    
    // Module heading
    const h2 = document.createElement("h2")
    h2.innerText = module.module_code
    parent.appendChild(h2)

    // Histogram
    embedChart(parent, "grade_histogram", module.grade_histogram)

    // Grade boundary stats
    const ul = document.createElement("ul")
    const stats = {
        "median": module.grade_statistics.median,
        ">=70": module.grade_statistics.gte70,
        ">=60": module.grade_statistics.gte60,
        "<=40": module.grade_statistics.lte40,
        "Zero": module.grade_statistics.zeros
    }
    for (const [key, val] of Object.entries(stats)) {
        const li = document.createElement("li")
        li.innerText = `${key}: ${val}`
        ul.appendChild(li)
    }
    parent.appendChild(ul)

    // Module performance comparison
    embedChart(parent, "grade_comparison_plot", module.grade_comparison_plot)

    // Student feedback
    for (let i in module.student_feedback.histograms) {
        embedChart(parent, `student_feedback_histogram_${i+1}`, module.student_feedback.histograms[i])
    }
}


// Module selector
const moduleSelector = document.createElement('select')
const modules = [
    'MAT-10044',
    'CSC-10032',
    
]
for (let i in modules) {
    const option = document.createElement('option') 
    option.value = modules[i]
    option.innerText = modules[i]
    moduleSelector.appendChild(option)
}
document.body.appendChild(moduleSelector)

// Module div
const moduleDiv = document.createElement('div')
moduleDiv.id = "module"
document.body.appendChild(moduleDiv)

// Load initial module
loadModule(moduleDiv, module)

// Listen for changes to module selector and load new module
moduleSelector.onchange = (e) => {
    loadModule(moduleDiv, module/*e.target.value*/)
}