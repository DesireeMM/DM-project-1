const newMemberButton = document.querySelector('#add-more-members');

const addMemberInput = (evt) => { 
    evt.preventDefault();
    const memberList = document.querySelector('#members-div');
    let html = '<div class="form-floating"><input type="text" class="form-control focus-ring members" id="floatingEmail" name="email" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}" placeholder="Email Address" required><label for="floatingEmail">Email Address</label></div><br>';
    memberList.insertAdjacentHTML('beforeend', html);
}

newMemberButton.addEventListener('click', addMemberInput);
        
const submitButton = document.querySelector("#new-group-submit")

submitButton.addEventListener('click', (evt) => {
    console.log("something");
    
    const memberElementsToAdd = document.querySelectorAll(".members");
    
    const memberEmails = []
    for (const el of memberElementsToAdd) {
        memberEmails.push(el.value)
    }

    const formInputs = {
        "group_name": document.querySelector("#floatingGroupName").value,
        "group_members": memberEmails
    }
    console.log(formInputs)

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