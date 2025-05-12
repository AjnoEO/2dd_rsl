function neatQueryString(url) {
    return url.replace(/=(?=&|$)/gm, '')
}

function setInputLanguage(rsl, user_initiated=true) {
    const form = document.getElementById("search")
    const input = document.getElementById("input")
    const button_icons = document.getElementsByClassName("switch_language_icon")
    const url = new URL(location.href)
    var translationsField = document.getElementById("translations")
    if (rsl) {
        if (user_initiated) {url.searchParams.delete("translations")}
        translationsField.remove()
        input.classList.add("rsl")
        input.setAttribute("placeholder", "55ДЯ ИИ??З")
        for (let i = 0; i < button_icons.length; i++) {
            button_icons[i].classList.add("rsl")
            button_icons[i].innerText = "5"
        }
    } else {
        if (user_initiated) {url.searchParams.set("translations", "")}
        form.setAttribute("action", "/search?translations")
        if (translationsField == null) {translationsField = document.createElement("input")}
        translationsField.hidden = true
        translationsField.id = "translations"
        translationsField.name = "translations"
        translationsField.value = "true"
        form.appendChild(translationsField)
        input.classList.remove("rsl")
        input.setAttribute("placeholder", "Введите слово")
        for (let i = 0; i < button_icons.length; i++) {
            button_icons[i].classList.remove("rsl")
            button_icons[i].innerText = "Я"
        }
    }
    if (user_initiated) {
        input.value = ""
        history.pushState(null, '', neatQueryString(url.toString()))
    }
}

function switchInputLanguage() {
    const url = new URL(location.href)
    translations = (url.searchParams.get("translations") != null)
    setInputLanguage(translations)
}

document.addEventListener('DOMContentLoaded', function() {
    rsl = document.getElementById('rsl')
    console.log(rsl)
    if (rsl) {
        rsl.remove()
        setInputLanguage(true, user_initiated=false)
    }
}, false);