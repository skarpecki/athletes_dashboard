var cmjData;
var jumpIterator;
var jumpsMaxIdx;
var yMax = 0;
var xMin = 0;
var xMax = 0;



var getLabel = (labels, idFor) => {
    for (let i = 0; i < labels.length; i++) {
        if (labels[i].htmlFor == idFor) {
            return labels[i];
        }
    }
}

var fillmetricsTable = (table, json) => {
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
    document.querySelector(".navigate-jumps").style.display = "block";
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

var getYMaxValue = (value) => {
    let thousands = value / 1000;
    if(thousands < 1) {
        return 0;
    }
    return Math.ceil(thousands) * 1000;
}   

var getCMJPlotData = (json, xCol, yCol) => {
    let data = [];
    let xArr = json[xCol]
    let yArr = json[yCol]
    let tempYMax = yArr[0];
    xMin = xArr[0];
    xMax = xArr[xArr.length - 1];
    for (let i = 0; i < xArr.length; i++) {
        data.push({
            x: xArr[i],
            y: yArr[i]
        })
        tempYMax = Math.max(yArr[i], tempYMax);
    }
    if (tempYMax > yMax) {
        yMax = getYMaxValue(tempYMax);
    }
    return data;
}


var generateChartConfig = (data) => {
    return {
        type: 'scatter',
        data: data,
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: xMin,
                    max: xMax,
                },
                y: {
                    max: yMax,
                    min: 0,
                }
               
            },
            plugins: {
                title: {
                    display: true,
                    text: "Jump no. " + (jumpIterator + 1),
                    font: {
                        size: 30,
                    }
                },
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
    var plotDiv = document.querySelector(".plot")
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

    const labels = document.querySelectorAll("label");

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
        jumpIterator = 0;
        document.body.style.cursor='wait';
        
        const metricsTable = document.querySelector("#metricsTable");
        const forceCSV = forceFile.files[0];
        let formData = new FormData();
        formData.append("forceFile", forceCSV);
        const XHR = new XMLHttpRequest();
        XHR.addEventListener("load", event => {
            if (XHR.status != 200) {
                document.body.style.cursor='default';
                alert(event.target.responseText);
            }
            const data = JSON.parse(event.target.responseText);
            jumpsMaxIdx = data.length - 1;
            jumpIterator = 0;
            const stats = data[jumpIterator]["stats"];
            // fillmetricsTable(metricsTable, stats);
            cmjData = data;
            if(myScatter !== null) {
                myScatter.destroy();
                yMax = 0;
            }
            myScatter = new Chart(ctx, 
                generateChartConfig(generateChartForceData(cmjData[jumpIterator]["data"]))
                );
            showPlotElements();
            document.body.style.cursor='default';
            plotDiv.scrollIntoView();
        });
        XHR.addEventListener("error", event => {
            console.log("error");
            alert(event.target.responseText);
            document.body.style.cursor='default';
        });
        XHR.open("POST", "http://127.0.0.1:5000/analytics/cj/");
        XHR.send(formData);
    }

    let chartTypeBtns = document.querySelectorAll(".navigate-jumps-btn");
    function moveLeft() {
        jumpIterator = ( jumpIterator == 0 ) ? jumpsMaxIdx : jumpIterator - 1;
        let data = generateChartForceData(cmjData[jumpIterator]["data"]);
        config = generateChartConfig(data);
        myScatter.destroy();
        myScatter = new Chart(ctx, config);
        plotDiv.scrollIntoView();
    }

    function moveRight() {
        jumpIterator = ( jumpIterator == jumpsMaxIdx ) ? 0 : jumpIterator + 1; 
        let data = generateChartForceData(cmjData[jumpIterator]["data"]);
        config = generateChartConfig(data);
        myScatter.destroy();
        myScatter = new Chart(ctx, config);
        plotDiv.scrollIntoView();
    }

    
    document.addEventListener('keydown', (event) => {
        if(!event.repeat)
        {
            switch (event.key) {
                case "ArrowLeft":
                    moveLeft();
                    break;
                case "ArrowRight":
                    moveRight();
                    break;
            }
        }
    })


    for(let i = 0; i < chartTypeBtns.length; i++) {

        if(chartTypeBtns[i].value == "left") {
            chartTypeBtns[i].onclick = moveLeft;
        };

        if(chartTypeBtns[i].value == "right") {
            chartTypeBtns[i].onclick = moveRight;
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