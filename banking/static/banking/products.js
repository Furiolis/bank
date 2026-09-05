const blockedOptions = JSON.parse(document.getElementById("blocked-options").textContent);
const selectElement = document.getElementById("id_accounts");
const addsubmitBtn = document.getElementById("add_card_btn");
const delsubmitBtn = document.getElementById("del_acc_btn");
const delcardBtn = document.getElementById("del_card_btn");
function updateButtons() {
    const selectedValue = selectElement.value;
    if (!selectedValue) {
        addsubmitBtn.disabled = true;
        addsubmitBtn.textContent = gettext("Choose account");
        delsubmitBtn.disabled = true;
        delsubmitBtn.textContent = gettext("Choose account");
        delcardBtn.disabled = true;
        delcardBtn.textContent = gettext("Choose account");
        } 
    else if (blockedOptions[selectedValue] === "True") {
        addsubmitBtn.disabled = true;
        addsubmitBtn.textContent = gettext("Card already added");
        delsubmitBtn.disabled = false;
        delsubmitBtn.textContent = gettext("Delete account");
        delcardBtn.disabled = false;
        delcardBtn.textContent = gettext("Delete card");
        } 
    else {
        addsubmitBtn.disabled = false;
        addsubmitBtn.textContent = gettext("Add card");
        delsubmitBtn.disabled = false;
        delsubmitBtn.textContent = gettext("Delete account");
        delcardBtn.disabled = true;
        delcardBtn.textContent = gettext("No card");
        }            
}
selectElement.addEventListener('change', updateButtons);
updateButtons();