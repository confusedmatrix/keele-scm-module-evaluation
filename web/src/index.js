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
    h2.innerText = module.code
    parent.appendChild(h2)

    // Histogram
    embedChart(parent, "hist", module.hist)

    // Grade boundary stats
    const ul = document.createElement("ul")
    const stats = {
        "median": module.stats.median,
        ">=70": module.stats.gte70,
        ">=60": module.stats.gte60,
        "<=40": module.stats.lte40,
        "Zero": module.stats.zeros
    }
    for (const [key, val] of Object.entries(stats)) {
        const li = document.createElement("li")
        li.innerText = `${key}: ${val}`
        ul.appendChild(li)
    }
    parent.appendChild(ul)

    // Module performance comparison
    embedChart(parent, "compare", module.compare)
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