const updateButtons = document.querySelectorAll('.update-avail');

for (const button of updateButtons) {
    button.addEventListener('click', () => {

        const newStart = prompt('Enter a new start time:')
        const newEnd = prompt('Enter a new end time:')
        const availID = button.id
        const formInputs = {
            "avail_id": availID,
            "new_start": newStart,
            "new_end": newEnd
        }

        fetch('/update-availability', {
            method: 'POST',
            body: JSON.stringify(formInputs),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(responseJson => {
            alert(responseJson.status);
            const availHTML = document.querySelector(`#avail_${availID}`);
            availHTML.innerText = `${newStart} to ${newEnd}`;
            window.location.replace(responseJson.redirect)
        })
    })
}

//wait until we learn regular expressions next week to figure out time entry validation