import vegaEmbed, { vega } from 'vega-embed'
import fetch from 'isomorphic-fetch'

const embedChart = (parent, id, json) => {
    const div = document.createElement('div')
    div.id = id
    parent.appendChild(div)
    vegaEmbed(`#${id}`, json, { actions: false })
}

const loadModule = (parent, module) => {
    parent.innerHTML = ""
    
    // Module heading
    const moduleH2 = document.createElement("h2")
    moduleH2.innerText = module.module_code
    parent.appendChild(moduleH2)

    // Histogram
    embedChart(parent, "grade_histogram", module.grade_histogram)

    // Grade boundary stats
    const ul = document.createElement("ul")
    ul.classList.add("module-stats")
    const stats = {
        "median": module.grade_statistics.median,
        ">=70": module.grade_statistics.gte70,
        ">=60": module.grade_statistics.gte60,
        "<=40": module.grade_statistics.lte40,
        "Zero": module.grade_statistics.zeros
    }
    for (const [key, val] of Object.entries(stats)) {
        const li = document.createElement("li")
        li.innerHTML = `<span class="title">${key}</span><span class="value">${val}</span>`
        ul.appendChild(li)
    }
    parent.appendChild(ul)

    // Module performance comparison
    embedChart(parent, "grade_comparison_plot", module.grade_comparison_plot)

    // Student feedback
    if (!module.hasOwnProperty("student_feedback")) {
        const p = document.createElement("p")
        p.innerText = "No student feedback data available"
        p.classList.add("toast")
        p.classList.add("toast-error")
        parent.appendChild(p)
    } else {
        const sfbH3 = document.createElement("h3")
        sfbH3.innerText = "Student feedback"
        parent.appendChild(sfbH3)
        for (let i in module.student_feedback.histograms) {
            embedChart(parent, `student_feedback_histogram_${i+1}`, module.student_feedback.histograms[i])
        }
    }
}

const root = document.getElementById("root")
fetch('data/modules.json')
    .then(response => {
        if (response.status >= 400) {
            throw new Error("Bad response from server")
        }

        return response.json()
    }).then(data => {

        const modules = Object.keys(data)

        // Module selector
        const moduleSelector = document.createElement("select")

        for (let code of modules) {
            const option = document.createElement("option") 
            option.value = code
            option.innerText = code
            moduleSelector.appendChild(option)
        }
        const selectorDiv = document.createElement("div")
        selectorDiv.id = "module-selector"
        selectorDiv.appendChild(moduleSelector)
        root.appendChild(selectorDiv)

        // Module div
        const moduleDiv = document.createElement("div")
        moduleDiv.id = "module"
        root.appendChild(moduleDiv)

        // Load initial module
        loadModule(moduleDiv, data[modules[0]])

        // Listen for changes to module selector and load new module
        moduleSelector.onchange = e => {
            loadModule(moduleDiv, data[e.target.value])
        }

    })