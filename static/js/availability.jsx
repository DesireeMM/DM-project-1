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

    function deleteAvailabilityRecord(availID) {
        console.log("I am getting called!")

        fetch('/delete-availability', {
            method: 'POST',
            body: JSON.stringify({ "availID": availID }),
            headers: {
            'Content-Type': 'application/json',
            }
        })
        .then((response) => response.json())
        .then((responseJson) => {
            alert(responseJson.status);
            const deletedRecord = responseJson.target_avail;
            const updatedRecords = []
            //loop through records with for loop
            for (const record of records) {
                if (record["avail_id"] !== deletedRecord) {
                    updatedRecords.push(record)
                }
            }
            //add everything except the one you want to delete to a new list
            //then update the state with setRecords
            //pass this function in as prop to all child components
            setRecords(updatedRecords);
        })
    }

    //this function goes in AddAvailabilityRecord component as a prop
    function addRecord(newAvailRecord) {
        const currentRecords = [...records];
        setRecords([...currentRecords, newAvailRecord]);
    }

    const availRecords = []

    for (const currentRecord of records) {
        availRecords.push(
            <AvailabilityRecord
                key={currentRecord.avail_id}
                availID={currentRecord.avail_id}
                weekday={currentRecord.weekday}
                startTime={currentRecord.start_time}
                endTime={currentRecord.end_time}
                deleteAvailabilityRecord={deleteAvailabilityRecord}
                />
        )
    }

    return (
            <React.Fragment>
                <div className="dash-row-2">
                <div className="dash-avail-col-1">
                    <h2>Availability Records</h2>
                    {availRecords}
                </div>
                <div className="dash-avail-col-2">
                    <AddAvailabilityRecord addRecord={addRecord} />
                </div>
                </div>
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

    if (formDisplay) {
    return (
        <div className="container">
        <div className="avail-record">
        <p>Day of the Week: {weekday}</p>
        <p>From: {startTime}</p>
        <p>To: {endTime} </p>
        </div>
        <div className="avail-update-form">
            <label htmlFor="weekday-select">New Weekday? </label>
                    <select className="form-select" name="weekday" id="weekday-select" value={weekdayInput} onChange={(event) => setWeekdayInput(event.target.value)}>
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
                    Change Start Time: 
                    <input type="time" name="start-time" value={startTimeInput} onChange={(event) => setStartTimeInput(event.target.value)}/>
                    <br /><br />
                    Change End Time: 
                    <input type="time" name="end-time" value={endTimeInput} onChange={(event) => setEndTimeInput(event.target.value)}/>
                    <br /><br />
        </div>
        <button type="button" className="btn" onClick={() =>
        setFormDisplay(false)}>
            Hide Form</button>
            <button type="button" className="btn" onClick={updateAvailabilityRecord}>
            Make Changes</button>
        </div>
    )}
    else {
    return (
      <div className="avail-record">
        <p>Day of the Week: {weekday}</p>
        <p>From: {startTime}</p>
        <p>To: {endTime} </p>
        <button type="button" className="btn avail-btn" onClick={() =>
            setFormDisplay(true)}>
            Change record</button>
        <button type="button" className="btn avail-btn" onClick={() => props.deleteAvailabilityRecord(props.availID)}>
        Delete record</button>
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
                    <select className="form-select" name="weekday" id="weekday-select" value={newWeekday} onChange={(event) => setNewWeekday(event.target.value)}>
                        <option value="monday">Monday</option>
                        <option value="tuesday">Tuesday</option>
                        <option value="wednesday">Wednesday</option>
                        <option value="thursday">Thursday</option>
                        <option value="friday">Friday</option>
                        <option value="saturday">Saturday</option>
                        <option value="sunday">Sunday</option>
                    </select>
                    <br />
                    <p>Select Start Time: 
                    <input type="time" name="start-time" value={newStartTime} onChange={(event) => setNewStartTime(event.target.value)} />
                    </p><br />
                    Select End Time:
                    <input type="time" name="end-time" value={newEndTime} onChange={(event) => setNewEndTime(event.target.value)} />
                    <br /><br />
            <button type="button" className="btn avail-btn" onClick={addNewRecord}>Add Record</button>
        </React.Fragment>
    )
}

    
ReactDOM.render(<AvailabilityRecordContainer />, document.getElementById('avail-div'));