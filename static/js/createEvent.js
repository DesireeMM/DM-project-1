const memberSelector = document.querySelector('#group-select');

memberSelector.addEventListener( 'change', () => {
    const checkboxDiv = document.querySelector('#member-selection');

    const groupID = memberSelector.value

    const formInputs = {
        "group_id": groupID
    }

    fetch('/api/group-members', {
        method: 'POST',
        body: JSON.stringify(formInputs),
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(responseJson => {
        checkboxDiv.insertAdjacentHTML('afterbegin', "<h3>Who's going?</h3>")
        for (const member of responseJson) {
            const html = `<div className="form-check"><input className="form-check-input focus-ring" type="checkbox" value="${member.id}" id="member-check-${member.id}">${member.name}<label className="form-check-label" for="member-check-${member.id}</div>`
            checkboxDiv.insertAdjacentHTML('beforeend', html)
        }
    })
})