const currentYear = new Date().getFullYear();

$("#timelineRange").ready(function() {
    // init
    $("#timelineRange").val(currentYear);
    $('#timelineRangeValue').html(currentYear);

    $("#timelineRange").bind("input", function() {
        $('#timelineRangeValue').html($(this).val());
    });

    $(function() {
        // const randYear = Math.floor(Math.random() * (currentYear + currentYear + 1)) - currentYear;
        const randYear = 1600;
        $( "#slider-range" ).slider({
            range: true,
            min: -5000,
            max: 2050,
            values: [ randYear, (randYear+100) ],
            slide: function( event, ui ) {
                $("#timelinestart").html(ui.values[0]);
                $("#timelineend").html(ui.values[1]);
            },
            change: function( event, ui ) {
                console.log("/timeline/filter/time?start=" + ui.values[0] + "-01&end=" + ui.values[1] + "-01");
                $.ajax({
                    url: "/timeline/filter/time?start=" + ui.values[0] + "-01&end=" + ui.values[1] + "-01",
                    type: 'GET',
                    dataType: 'json', // added data type
                    success: function(res) {
                        showResults(res.data.events);
                        displayResultsOnMap(res.data.events);
                    }
                });
            }
        });
        $("#timelinestart").html($( "#slider-range" ).slider( "values" )[0]);
        $("#timelineend").html($( "#slider-range" ).slider( "values" )[1]);
    })
    

});

$("#timelinestart").bind("dblclick", function() {
    const jumpYear = prompt("Enter the START year to seek to:", $( "#slider-range" ).slider( "values" )[0]);
    if (jumpYear && jumpYear.trim()) {
        $( "#slider-range" ).slider( "values", 0, jumpYear )
        $('#timelinestart').html(jumpYear);
    }
});

$("#timelineend").bind("dblclick", function() {
    const jumpYear = prompt("Enter the END year to seek to:", $( "#slider-range" ).slider( "values" )[1]);
    if (jumpYear && jumpYear.trim()) {
        $( "#slider-range" ).slider( "values", 1, jumpYear )
        $('#timelineend').html(jumpYear);
    }
});


var globLoc = {};
function showResults(events) {
    globLoc = {};
    mapPointLines = {};
    //  event time --subtable-- correspondinglocation
    evtTable = `<tr>
        <td>line</td>
        <td>event</td>
        <td>
            details :: [ TIME | LOCATION | Liner ]
        </td>
    </tr>`;
    for (const key in events) {
        evtTable += `
            <tr><td></td><td>${events[key].event}</td>
        `.trim();

        // lifespan
        if (events[key]["type"] === "lifespan") {
            detTable = `<table border="1" width="100%">`.trim();
            for (const spanMode in events[key]["time"]["lifespan"]) {
                detTable += `<tr>
                <td>${spanMode}</td>
                <td>${new Date(events[key]["time"]["lifespan"][spanMode]["ts"]).toUTCString()} (:: ${events[key]["time"]["lifespan"][spanMode]["humanly"]})</td>
                <td>${spanMode in events[key]["location"]["geo"]? events[key]["location"]["geo"][spanMode]["name"] : null}</td>
                <td><input type='checkbox' id="checkbox_${events[key]["id"]}_${spanMode}" onclick="updatemapline(this.id)" ${spanMode in events[key]["location"]["geo"]? "" : "disabled"} /></td>
                </tr>`.trim();

                // add to global location list
                if (spanMode in events[key]["location"]["geo"]) {
                    globLoc[`checkbox_${events[key]["id"]}_${spanMode}`] = [events[key]["location"]["geo"][spanMode]["lat"], events[key]["location"]["geo"][spanMode]["lon"]];
                }
            }
            detTable += "</table>";
        }

        evtTable += `<td>${detTable}</td></tr>`;
    }
    $("#event-list").html(evtTable);
}


var mapPointLines = {};
function updatemapline(id) {
    if($("#" + id).is(":checked") == true && id in globLoc) {
        mapPointLines[id] = globLoc[id];
    } else {
        delete mapPointLines[id];
    }
    displayLinesOnMap(mapPointLines);
}


