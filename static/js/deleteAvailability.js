const deleteButtons = document.querySelectorAll('.delete-avail');

for (const button of deleteButtons) {
    button.addEventListener('click', () => {

        const availID = button.id
        const formInputs = {
            "avail_id": availID,
        }

        fetch('/delete-availability', {
            method: 'POST',
            body: JSON.stringify(formInputs),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(responseJson => {
            alert(responseJson.status);
            window.location.replace(responseJson.redirect);
        })
    })
}