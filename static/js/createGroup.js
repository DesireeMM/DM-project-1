const newMemberButton = document.querySelector('#add-more-members');

const addMemberInput = (evt) => { 
    evt.preventDefault();
    const memberList = document.querySelector('#members');
    memberList.insertAdjacentHTML('beforeend', '<li>Member email: <input type="text" class="members" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"></li>');
}

newMemberButton.addEventListener('click', addMemberInput);
        
const submitButton = document.querySelector("#new-group-submit")

submitButton.addEventListener('click', (evt) => {
    
    const memberElementsToAdd = document.querySelectorAll(".members");
    
    const memberEmails = []
    for (const el of memberElementsToAdd) {
        memberEmails.push(el.value)
    }

    const formInputs = {
        "group_name": document.querySelector("#name-field").value,
        "group_members": memberEmails
    }

    fetch('/add-group', {
        method: 'POST',
        body: JSON.stringify(formInputs),
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(responseJson => {
        window.location.replace(responseJson.redirect);
        alert(responseJson.status);
    })
})