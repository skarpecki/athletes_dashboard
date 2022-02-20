var cmjData;

var getLabel = (labels, idFor) => {
    for (let i = 0; i < labels.length; i++) {
        if (labels[i].htmlFor == idFor) {
            return labels[i];
        }
    }
}

var fillCMJTable = (table, json) => {
    for (let key in json) {
        let newRow = table.insertRow(-1);
        let keyCell = newRow.insertCell(0);
        let valueCell = newRow.insertCell(1);
        let boldValue = document.createElement("strong");
        let keyText = document.createTextNode(key);
        let valueText = document.createTextNode(json[key]);
        boldValue.appendChild(valueText);
        keyCell.appendChild(keyText);
        valueCell.appendChild(boldValue);
    }
}

var showPlotElements = () => {
    document.querySelector(".select-chart-type").style.display = "block";
    document.querySelector("#resetZoomBtn").style.display = "block";
    document.querySelector("#myChart").style.background = "white";
}

var generateChartForceData = (jsonCMJ) => {
    const combinedForceData = getCMJPlotData(jsonCMJ, "Time (s)", "Combined (N)");
    const leftForceData = getCMJPlotData(jsonCMJ, "Time (s)", "Left (N)");
    const rightForceData = getCMJPlotData(jsonCMJ, "Time (s)", "Right (N)");

    const data = {
        datasets: [{
            label: 'Force [N]',
            data: combinedForceData,
            backgroundColor: 'rgb(255, 99, 132)',
            showLine: true,
            borderColor: 'rgb(255, 99, 132)',
            pointRadius: 0
        },
        {
            label: 'Left [N]',
            data: leftForceData,
            backgroundColor: 'rgb(153, 255, 153)',
            showLine: true,
            borderColor: 'rgb(153, 255, 153)',
            pointRadius: 0
        },
        {
            label: 'Right [N]',
            data: rightForceData,
            backgroundColor: 'rgb(95.7, 95.3, 32.2)',
            showLine: true,
            borderColor: 'rgb(95.7, 95.3, 32.2)',
            pointRadius: 0
        }],
    };
    return data
}



var getCMJPlotData = (json, xCol, yCol) => {
    let data = [];
    for (let i = 0; i < json.length; i++) {
        data.push({
            x: json[i][xCol],
            y: json[i][yCol]
        })
    }
    return data;
}

var generateChartVelocityData = (jsonCMJ) => {
    const combinedForceData = getCMJPlotData(jsonCMJ, "Time (s)", "Velocity (m/s)");

    const data = {
        datasets: [{
            label: 'Velocity (m/s)',
            data: combinedForceData,
            backgroundColor: 'rgb(255, 99, 132)',
            showLine: true,
            borderColor: 'rgb(255, 99, 132)',
            pointRadius: 0
        }],
    };

    return data
}

var generateChartAccelerationData = (jsonCMJ) => {
    const combinedForceData = getCMJPlotData(jsonCMJ, "Time (s)", "Acceleration (m/s^2)");

    const data = {
        datasets: [{
            label: 'Acceleration (m/s^2)',
            data: combinedForceData,
            backgroundColor: 'rgb(255, 99, 132)',
            showLine: true,
            borderColor: 'rgb(255, 99, 132)',
            pointRadius: 0
        }],
    };

    return data
}

var generateChartConfig = (data) => {
    return {
        type: 'scatter',
        data: data,
        options: {
            title: {
                display: true,
                text: "CMJ(s)"
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom'
                }
            },
        },
        options: {
            plugins: {
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        drag: {
                            enabled: false,
                            backgroundColor: "darkgrey",
                        },
                        mode: 'xy',
                    },
                    pan: {
                        enabled: true,
                    }
                }
            }
        }
    };
}


var colorTypeButtons = (allButons, btnToGreyIdx) => {
    for(let i = 0; i < allButons.length; i++) {
        if (i === btnToGreyIdx) {
            allButons[i].style.backgroundColor = "#b8b3b3";
        } else {
            allButons[i].style.backgroundColor =  "";
        }
    }
}



window.onload = () => {
    var ctx = null;
    var myScatter = null;
    if(document.getElementById('myChart') !== null) {
        ctx = document.getElementById('myChart').getContext('2d');
    }

    let navItemElements = document.querySelectorAll(".nav-item");
    let navbar = document.querySelector(".navbar");
    for (let i = 0; i < navItemElements.length; i++) {
        navItemElements[i].onclick = () => {
            let ul = navItemElements[i].querySelector("ul");
            if (ul != null) {
                ul.style.display = ul.style.display == "none" ? "block" : "none";
            }
        }
    }

    navbar.onmouseleave = () => {
        document.querySelector(".navbar-nav-menu").style.display = "none";
    }

    const velocityFile = document.querySelector("#velocityFile")
    const labels = document.querySelectorAll("label");
    velocityFile.onchange = (event) => {
        const label = getLabel(labels, velocityFile.id);
        const span = label.querySelector("span");
        if (event.target.files.length == 0) {
            span.innerHTML = "Choose a velocity file..."
        } else {
            const file = event.target.files[0];
            span.innerHTML = file.name;
        }
    }

    const forceFile = document.querySelector("#forceFile")
    forceFile.onchange = (event) => {
        const label = getLabel(labels, forceFile.id);
        const span = label.querySelector("span");
        if (event.target.files.length == 0) {
            span.innerHTML = "Choose a force file..."
        } else {
            const file = event.target.files[0];
            span.innerHTML = file.name;

        }
    }

    document.querySelector("#uploadFiles").onclick = () => {
        document.body.style.cursor='wait';
        
        const cmjTable = document.querySelector("#cmjTable");
        const forceCSV = forceFile.files[0];
        const velCSV = velocityFile.files[0];
        let formData = new FormData();
        formData.append("forceFile", forceCSV);
        formData.append("velocityFile", velCSV);
        const XHR = new XMLHttpRequest();
        XHR.addEventListener("load", event => {
            if (XHR.status != 200) {
                alert(event.target.responseText);
                document.body.style.cursor='default';
            }
            const data = JSON.parse(event.target.responseText);
            const stats = data["stats"];
            cmjData = data["data"];
            fillCMJTable(cmjTable, stats);
            myScatter = new Chart(ctx, 
                generateChartConfig(generateChartForceData(cmjData))
                );
            showPlotElements();
            document.body.style.cursor='default';
        });
        XHR.addEventListener("error", event => {
            console.log("error");
            alert(event.target.responseText);
            document.body.style.cursor='default';
        });
        XHR.open("POST", "http://127.0.0.1:5000/analytics/cmj/");
        XHR.send(formData);
    }

    let chartTypeBtns = document.querySelectorAll(".select-chart-type-btn");

    for(let i = 0; i < chartTypeBtns.length; i++) {

        if(chartTypeBtns[i].value == "vel") {
            chartTypeBtns[i].onclick = () => {
                colorTypeButtons(chartTypeBtns, i);
                data = generateChartVelocityData(cmjData);
                config = generateChartConfig(data);
                myScatter.destroy();
                myScatter = new Chart(ctx, config);
            }
        };

        if(chartTypeBtns[i].value == "force") {
            chartTypeBtns[i].onclick = () => {
                colorTypeButtons(chartTypeBtns, i);
                data = generateChartForceData(cmjData);
                config = generateChartConfig(data);
                myScatter.destroy();
                myScatter = new Chart(ctx, config);
            }
        };

        if(chartTypeBtns[i].value == "acc") {
            chartTypeBtns[i].onclick = () => {
                colorTypeButtons(chartTypeBtns, i);
                data = generateChartAccelerationData(cmjData);
                config = generateChartConfig(data);
                myScatter.destroy();
                myScatter = new Chart(ctx, config);
            }
        };
            
    } 
    
    document.querySelector("#resetZoomBtn").onclick = () => {
        console.log("click");
        myScatter.resetZoom();
    }

    // navbar.onmouseover = () => {
    //     document.querySelector(".header").style.left = "16rem"
    // }
}