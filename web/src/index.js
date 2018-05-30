import vegaEmbed from 'vega-embed'
import fetch from 'isomorphic-fetch'

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
        let i = 0
        for (i in module.student_feedback.histograms) {
            const qDiv = document.createElement("div")
            qDiv.setAttribute("data-qnumber", parseInt(i)+1)
            qDiv.classList.add("question")
            parent.appendChild(qDiv)

            const q = document.createElement("h4")
            q.innerText = formatQuestion(module.student_feedback.questions[i])
            qDiv.appendChild(q)

            embedChart(qDiv, `student_feedback_histogram_${i+1}`, module.student_feedback.histograms[i])
            if (module.student_feedback.text[i].length > 0) {
                const qH4 = document.createElement("h4")
                qH4.innerText = "Responses"
                qDiv.appendChild(qH4)
                for (let j in module.student_feedback.text[i]) {
                    const bq = document.createElement("blockquote")
                    bq.innerText = module.student_feedback.text[i][j]
                    qDiv.appendChild(bq)
                }
            }
        }

        for (let j in module.student_feedback.descriptive) {
            const qDiv = document.createElement("div")
            qDiv.setAttribute("data-qnumber", parseInt(i) + parseInt(j) + 2)
            qDiv.classList.add("question")
            parent.appendChild(qDiv)

            const q = document.createElement("h4")
            q.innerText = formatQuestion(module.student_feedback.questions[parseInt(i) + parseInt(j) + 1])
            qDiv.appendChild(q)

            const img = document.createElement("img")
            img.src = module.student_feedback.descriptive[j].image
            qDiv.appendChild(img)
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