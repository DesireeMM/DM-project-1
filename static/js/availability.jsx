// for each availability record in a user's availabilities
//will need a parent component to hold these records
//fetch to a route that will return all of current user's availabilities to populate records

function AvailabilityRecordContainer() {
    const [records, setRecords] = React.useState([])

    React.useEffect(() => {
        fetch('/user-availability')
        .then((response) => response.json())
        .then((responseJson) => {
            setRecords(responseJson)
        })
        
    }, [])

    //this function goes in AddAvailabilityRecord component
    function addRecord(newAvailRecord) {
        const currentRecords = [...records];
        setRecords([...currentRecords, newAvailRecord]);
    }

    const availRecords = []

    for (const currentRecord of records) {
        availRecords.push(
            <AvailabilityRecord
                key = {currentRecord.avail_id}
                availID = {currentRecord.avail_id}
                weekday = {currentRecord.weekday}
                startTime = {currentRecord.start_time}
                endTime = {currentRecord.end_time}
                />
        )
    }

    return (
        <React.Fragment>
            <AddAvailabilityRecord addRecord={addRecord} />
            <h1>Availability Records</h1>
            <div className="col">{availRecords}</div>
        </React.Fragment>
    )
}

function AvailabilityRecord(props) {
    //form display toggle
    const [formDisplay, setFormDisplay] = React.useState(false)
    //record displays
    const [weekday, setWeekday] = React.useState(props.weekday);
    const [startTime, setStartTime] = React.useState(props.startTime);
    const [endTime, setEndTime] = React.useState(props.endTime);
    //input states
    const [weekdayInput, setWeekdayInput] = React.useState(props.weekday);
    const [startTimeInput, setStartTimeInput] = React.useState(props.startTime);
    const [endTimeInput, setEndTimeInput] = React.useState(props.endTime);
    // for deleting a record
    const [isDeleted, setIsDeleted] = React.useState(false)

    function updateAvailabilityRecord() {
        fetch('/update-availability', {
          method: 'POST',
          body: JSON.stringify({ "weekday": weekdayInput, "startTime": startTimeInput, "endTime": endTimeInput, "availID": props.availID }),
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then((response) => response.json())
        .then((responseJson) => {
        setWeekday(responseJson.weekday);
        setStartTime(responseJson.startTime);
        setEndTime(responseJson.endTime);
        })
      }

      function deleteAvailabilityRecord() {
        console.log("I am getting called!")

        fetch('/delete-availability', {
            method: 'POST',
            body: JSON.stringify({ "availID": props.availID }),
            headers: {
            'Content-Type': 'application/json',
            }
        })
        .then((response) => response.json())
        .then((responseJson) => {
            setIsDeleted(responseJson.success);
            alert(responseJson.status);
        })
    }


    if (formDisplay) {
    return (
        <div className="container">
        <div className="avail-record">
        <p>Day of the Week: {weekday}</p>
        <p>From: {startTime}</p>
        <p>To: {endTime} </p>
        </div>
        <div className="avail-update-form">
            <label htmlFor="weekday-select">Select a day of the week:</label>
                    <select name="weekday" id="weekday-select" value={weekdayInput} onChange={(event) => setWeekdayInput(event.target.value)}>
                        <option value="null">Weekday</option>
                        <option value="monday">Monday</option>
                        <option value="tuesday">Tuesday</option>
                        <option value="wednesday">Wednesday</option>
                        <option value="thursday">Thursday</option>
                        <option value="friday">Friday</option>
                        <option value="saturday">Saturday</option>
                        <option value="sunday">Sunday</option>
                    </select>
                    <br /><br />
                    <legend>
                        Select Start Time:
                        <input type="time" name="start-time" value={startTimeInput} onChange={(event) => setStartTimeInput(event.target.value)}/>
                    </legend>
                    <legend>
                        Select End Time:
                        <input type="time" name="end-time" value={endTimeInput} onChange={(event) => setEndTimeInput(event.target.value)}/>
                    </legend>
        </div>
        <button type="button" onClick={() =>
        setFormDisplay(false)}>
            Hide Form</button>
            <button type="button" onClick={updateAvailabilityRecord}>
            Make Changes</button>
        </div>
    )}
    else {
    return (
      <div className="avail-record">
        <p>Day of the Week: {weekday}</p>
        <p>From: {startTime}</p>
        <p>To: {endTime} </p>
        <button type="button" onClick={() =>
            setFormDisplay(true)}>
            Change this record</button>
        <button type="button" onClick={deleteAvailabilityRecord}>
        Delete this record</button>
      </div>
    );
    }
}

function AddAvailabilityRecord(props) {
    const [newWeekday, setNewWeekday] = React.useState("monday");
    const [newStartTime, setNewStartTime] = React.useState("");
    const [newEndTime, setNewEndTime] = React.useState("");
    


    function addNewRecord() {
        fetch('/add-availability', {
            method: 'POST',
            body: JSON.stringify({"weekday": newWeekday, "start_time": newStartTime, "end_time": newEndTime}),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then((response) => response.json())
        .then((responseJson) => {
            const newRecord = responseJson.newRecord;
            props.addRecord(newRecord);
        })
    }

    return (
        <React.Fragment>
            <h2>Add New Availability Record</h2>
            <label htmlFor="weekday-select">Select a day of the week:</label>
                    <select name="weekday" id="weekday-select" value={newWeekday} onChange={(event) => setNewWeekday(event.target.value)}>
                        <option value="monday">Monday</option>
                        <option value="tuesday">Tuesday</option>
                        <option value="wednesday">Wednesday</option>
                        <option value="thursday">Thursday</option>
                        <option value="friday">Friday</option>
                        <option value="saturday">Saturday</option>
                        <option value="sunday">Sunday</option>
                    </select>
                    <br /><br />
                    <legend>
                        Select Start Time:
                        <input type="time" name="start-time" value={newStartTime} onChange={(event) => setNewStartTime(event.target.value)} />
                    </legend>
                    <legend>
                        Select End Time:
                        <input type="time" name="end-time" value={newEndTime} onChange={(event) => setNewEndTime(event.target.value)} />
                    </legend>
            <button type="button" onClick={addNewRecord}>Add Record</button>
        </React.Fragment>
    )
}

    
ReactDOM.render(<AvailabilityRecordContainer />, document.getElementById('avail-div'));