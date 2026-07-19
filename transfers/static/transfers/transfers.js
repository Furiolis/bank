const internalBtn = document.getElementById("btn_internal");
const externalBtn = document.getElementById("btn_external");
const internalContainer = document.getElementById("internal_form_container");
const externalContainer = document.getElementById("external_form_container");
function switchForm(showInternal) {
    if (showInternal) {
        internalContainer.classList.remove("hidden");
        externalContainer.classList.add("hidden");
    } else {
        internalContainer.classList.add("hidden");
        externalContainer.classList.remove("hidden");
    }
}
internalBtn.addEventListener("click", () => switchForm(true));
externalBtn.addEventListener("click", () => switchForm(false));