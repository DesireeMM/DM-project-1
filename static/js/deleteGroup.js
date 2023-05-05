const deleteButton = document.querySelector('#delete-group');

deleteButton.addEventListener('click', () => {

    const deleteResponse = confirm("Are you sure you want to delete this group? This action is not reversible.")

    if (deleteResponse == true) {
        const groupID = document.querySelector('#group_id_num').value
        console.log(groupID)
        const formInputs = {
            "group_id": groupID,
        }

        fetch('/delete-group', {
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
    }
})
